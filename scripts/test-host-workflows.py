#!/usr/bin/env python3
"""Opt-in Codex observations; receipts never retain model or tool transcripts."""
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time
import tomllib

ROOT = Path(__file__).resolve().parents[1]
METRICS = ("input_tokens", "cached_input_tokens", "output_tokens")
PARTS = (".codex-plugin", "skills", "hooks", "assets", "scripts", "references", "licenses")
SCENARIOS = ROOT / "tests/fixtures/host-workflows/scenarios.json"
EXCLUDED = {".git", ".scratch", ".sonar-evidence", ".scannerwork", "__pycache__", ".pytest_cache"}
MANIFESTS = ("plugin.json", ".agents/plugins/marketplace.json")


def host_events(jsonl):
    for line in jsonl.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            raise ValueError("Malformed host JSONL") from None
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise ValueError("Host event must be a typed object")
        yield event


def advance_lifecycle(state, kind):
    if kind in ("error", "turn.failed"):
        raise RuntimeError("Host reported a failed turn")
    if state == "completed":
        raise ValueError("Unexpected event after completed turn")
    if kind == "thread.started":
        if state != "initial":
            raise ValueError("Repeated thread start")
        return "thread"
    if state == "initial":
        raise ValueError("Host event precedes thread start")
    if kind == "turn.started":
        if state == "turn":
            raise ValueError("Repeated turn start")
        return "turn"
    if state == "thread":
        raise ValueError("Host event precedes turn start")
    return "completed" if kind == "turn.completed" else state


def observed_usage(event):
    observed = event.get("usage", {})
    if not isinstance(observed, dict):
        raise ValueError("Invalid usage object")
    usage = {}
    for name in METRICS:
        if name not in observed:
            continue
        value = observed[name]
        if type(value) is not int or value < 0:
            raise ValueError("Invalid observed usage metric")
        usage[name] = value
    return usage


def parse_events(jsonl):
    state = "initial"
    usage = {}
    count = 0
    for event in host_events(jsonl):
        count += 1
        state = advance_lifecycle(state, event["type"])
        if state == "completed":
            usage = observed_usage(event)
    if state != "completed":
        raise ValueError("Incomplete host event lifecycle")
    return {"status": "passed", "evidence_layer": "event-execution", "event_count": count,
            "usage": usage, "missing_usage": [name for name in METRICS if name not in usage]}


def windows_job():
    """Closing this owned job terminates its child processes, including orphaned tools."""
    import ctypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.restype = ctypes.c_void_p
    kernel.SetInformationJobObject.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    kernel.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    job = kernel.CreateJobObjectW(None, None)
    # Win32 EXTENDED_LIMIT_INFORMATION: LimitFlags follows two LARGE_INTEGER fields.
    limits = ctypes.create_string_buffer(144 if struct.calcsize("P") == 8 else 112)
    struct.pack_into("I", limits, 16, 0x2000)  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not job or not kernel.SetInformationJobObject(job, 9, limits, len(limits)):
        if job:
            kernel.CloseHandle(job)
        raise RuntimeError("Owned subprocess containment unavailable")
    return kernel, job


def record_diagnostics(stderr, diagnostics):
    if diagnostics is None:
        return
    for signature, label in (("app runtime provisioning service is unavailable", "runtime-provisioning-unavailable"),
                             ("no rollout found for thread id", "ephemeral-child-rollout-unavailable"),
                             ("blocked by policy", "shell-policy-rejected")):
        if signature in stderr:
            diagnostics.append(label)


def stop_owned_process(process, containment):
    if containment:
        containment[0].CloseHandle(containment[1])
    elif process:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=10)


def child(command, *, cwd, timeout, env=None, diagnostics=None):
    # Nested desktop IPC/thread identity is not a standalone CLI session identity.
    environment = dict(os.environ if env is None else env)
    for name in ("CODEX_APP_RUNTIME_CLI_PATH", "CODEX_APP_TOOLS_PIPE_PATH", "CODEX_INTERNAL_ORIGINATOR_OVERRIDE",
                 "CODEX_SESSION_ID", "CODEX_THREAD_ID", "CODEX_TOOL_CALL_ID", "CODEX_TASK_WORKSPACE_VERIFYING_IDENTITY", "CODEX_SHELL",
                 "CODEX_WINDOWS_REGISTERED_CORE", "CODEX_WINDOWS_SANDBOX_PACKAGE_FAMILY"):
        environment.pop(name, None)
    containment = windows_job() if os.name == "nt" else None
    process = None
    try:
        process = subprocess.Popen(command, cwd=cwd, env=environment, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                                   start_new_session=os.name != "nt")
        if containment and not containment[0].AssignProcessToJobObject(containment[1], int(process._handle)):
            raise RuntimeError("Owned subprocess containment unavailable")
        stdout, stderr = process.communicate(timeout=timeout)
        record_diagnostics(stderr, diagnostics)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Host subprocess timed out") from None
    except OSError:
        raise RuntimeError("Host subprocess could not start") from None
    finally:
        stop_owned_process(process, containment)
    if process.returncode:
        raise RuntimeError(f"Host subprocess exited with code {process.returncode}")
    return stdout


def run_host(command, *, cwd, timeout):
    start = time.monotonic()
    diagnostics = []
    result = parse_events(child(command, cwd=cwd, timeout=timeout, diagnostics=diagnostics))
    result["host_diagnostics"] = diagnostics
    result["elapsed_seconds"] = round(time.monotonic() - start, 3)
    return result


def assert_scenario(project, assertions):
    if not assertions:
        raise ValueError("Scenario requires filesystem assertions")
    project = project.resolve()
    for assertion in assertions:
        path = project / assertion["path"]
        if not path.resolve().is_relative_to(project) or path.is_symlink():
            raise ValueError("Assertion path escapes fixture")
        if assertion.get("absent"):
            if path.exists():
                raise AssertionError("Expected fixture path to remain absent")
        elif not path.is_file() or path.read_text(encoding="utf-8") != assertion["content"]:
            raise AssertionError("Fixture content assertion failed")


def require_unlinked(path, root, message):
    if path.is_symlink() or path.is_junction() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(message)


def excluded_resource(path):
    return path.name in EXCLUDED or path.name.startswith(".env") or path.suffix == ".pyc"


def candidate_directory(root, base):
    require_unlinked(base, root, "Candidate contains a linked resource")
    for directory, dirs, files in os.walk(base, followlinks=False):
        for entry in list(dirs) + files:
            path = Path(directory) / entry
            if excluded_resource(path):
                if entry in dirs:
                    dirs.remove(entry)
                continue
            require_unlinked(path, root, "Candidate contains a linked resource")
            if entry in files:
                yield path


def candidate_files(root):
    paths = []
    for name in PARTS:
        base = root / name
        if base.exists():
            paths.extend(candidate_directory(root, base))
    for name in MANIFESTS:
        path = root / name
        if path.exists():
            require_unlinked(path, root, "Candidate contains a linked resource")
            paths.append(path)
    return sorted(paths)


def fingerprint(root):
    hashes = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in candidate_files(root)}
    return hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()


def copy_candidate(source, destination):
    for path in candidate_files(source):
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def release_helpers():
    # Load the owning checkout's contract, never Python from the installed candidate.
    spec = importlib.util.spec_from_file_location("host_release_helpers", ROOT / "scripts/check-release.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def release_fingerprint(root):
    return release_helpers().source_identity(root)["fingerprint"]


def copy_release_candidate(source, destination):
    copy_candidate(source, destination)
    checker = release_helpers()
    for relative in checker.RELEASE_EXTRAS:
        path = checker.resource(source.resolve(), relative)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def snapshot(project):
    state = {}
    for directory, dirs, files in os.walk(project, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            if path.is_symlink() or path.is_junction() or not path.resolve().is_relative_to(project.resolve()):
                raise ValueError("Fixture contains a linked resource")
            if name in files:
                state[path.relative_to(project).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return state


def prompt_discovery(command, project, skills, timeout, env=None):
    raw = child(command + ["debug", "prompt-input", "Candidate skill discovery probe."],
                cwd=project, timeout=timeout, env=env)
    # The CLI renders skill-root aliases; verify their association rather than model self-report.
    rendered = json.dumps(json.loads(raw)).replace("\\\\", "/")
    path = skills.as_posix()
    match = re.search(r"`(r\d+)` = `" + re.escape(path) + r"`", rendered)
    discovered = bool(match and f"file: {match[1]}/kiss-chris-stack/SKILL.md" in rendered)
    if not discovered:
        raise RuntimeError("Host prompt did not discover candidate skill root")
    return {"status": "passed", "method": "codex debug prompt-input", "candidate_skill_discovered": True}


def configured_windows_sandbox():
    if os.name != "nt":
        return None
    config = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"
    if not config.is_file():
        return None
    configured = tomllib.loads(config.read_text(encoding="utf-8")).get("windows", {}).get("sandbox")
    return configured if configured in ("elevated", "unelevated") else None


def install_candidate(base, codex, timeout, receipt, original):
    stage = base / "candidate"
    stage.mkdir()
    # Local plugin installation copies ignored files too; never install from the working tree.
    copy_release_candidate(ROOT, stage)
    if release_fingerprint(stage) != original:
        raise RuntimeError("Staged candidate fingerprint mismatch")
    settings = ["-c", 'marketplaces.kiss-chris-stack.source_type="local"',
                "-c", "marketplaces.kiss-chris-stack.source=" + json.dumps(stage.as_posix())]
    profile = base / "profile"
    profile.mkdir()
    env = {**os.environ, "CODEX_HOME": str(profile)}
    receipt["stage"] = "isolated-candidate-install"
    install = json.loads(child([codex, *settings, "plugin", "add", "kiss-chris-stack@kiss-chris-stack", "--json"],
                               cwd=base, timeout=timeout, env=env))
    installed = Path(install["installedPath"])
    if release_fingerprint(installed) != original:
        raise RuntimeError("Installed candidate fingerprint mismatch")
    receipt["stage"] = "installed-candidate-discovery"
    receipt["installed_candidate_discovery"] = prompt_discovery(
        [codex, *settings], base, installed / "skills", timeout, env)
    receipt["installed_candidate_discovery"]["fingerprint_matches"] = True
    return installed


def prepare_project(base, scenario, installed, original, timeout):
    project = base / scenario["id"]
    project.mkdir()
    child(["git", "init", "--quiet", str(project)], cwd=base, timeout=timeout)
    candidate = project / ".agents"
    candidate.mkdir()
    copy_release_candidate(installed, candidate)
    if release_fingerprint(candidate) != original:
        raise RuntimeError("Project candidate fingerprint mismatch")
    for name, content in scenario["files"].items():
        (project / name).write_text(content, encoding="utf-8")
    return project


def observe_scenario(project, scenario, codex, model, timeout, windows_sandbox, receipt):
    observed = {"id": scenario["id"], "status": "running"}
    receipt["scenarios"].append(observed)
    receipt["stage"] = scenario["id"] + ":project-skill-discovery"
    observed["candidate_discovery"] = prompt_discovery([codex], project, project / ".agents/skills", timeout)
    before = snapshot(project)
    skill = project / ".agents/skills/kiss-chris-stack/SKILL.md"
    prompt = f"Load the candidate skill at {skill.as_posix()} and resolve its bundled references from that candidate root. {scenario['prompt']}"
    command = [codex, "exec", "--ignore-user-config", "--ephemeral", "--json", "--model", model,
               "--sandbox", "workspace-write", "-C", str(project), prompt]
    if windows_sandbox:
        command[2:2] = ["-c", "windows.sandbox=" + json.dumps(windows_sandbox)]
    observed["invocation"] = {"subcommand": "exec", "ephemeral": True, "sandbox": "workspace-write",
                              "ignore_user_config": True, "windows_sandbox": windows_sandbox or "not overridden"}
    receipt["stage"] = scenario["id"] + ":model-execution"
    try:
        observed["execution"] = run_host(command, cwd=project, timeout=timeout)
        receipt["stage"] = scenario["id"] + ":filesystem-assertions"
        assert_scenario(project, scenario["assertions"])
        after = snapshot(project)
        allowed = set() if scenario.get("preserve_state") else {a["path"] for a in scenario["assertions"]}
        if {p: h for p, h in before.items() if p not in allowed} != {p: h for p, h in after.items() if p not in allowed}:
            raise AssertionError("Scenario changed files outside its allowed correction")
        observed.update(status="passed", filesystem_assertions="passed", state_preservation="passed")
    except (RuntimeError, ValueError, AssertionError, OSError, KeyError) as error:
        observed.update(status="failed", failure=failure_detail(error), failed_stage=receipt["stage"])


def live(model, timeout, receipt):
    codex = shutil.which("codex")
    if not codex or not shutil.which("git"):
        raise RuntimeError("Codex and Git executables are required")
    receipt["cli_version"] = child([codex, "--version"], cwd=ROOT, timeout=timeout).strip()
    receipt["python_version"] = sys.version.split()[0]
    original = release_fingerprint(ROOT)
    receipt["candidate_fingerprint"] = fingerprint(ROOT)
    receipt["release_candidate_fingerprint"] = original
    receipt["scenario_fingerprint"] = hashlib.sha256(SCENARIOS.read_bytes()).hexdigest()
    windows_sandbox = configured_windows_sandbox()
    with tempfile.TemporaryDirectory(prefix="kiss-host-") as folder:
        base = Path(folder)
        installed = install_candidate(base, codex, timeout, receipt, original)
        receipt["scenarios"] = []
        for scenario in json.loads(SCENARIOS.read_text(encoding="utf-8")):
            project = prepare_project(base, scenario, installed, original, timeout)
            observe_scenario(project, scenario, codex, model, timeout, windows_sandbox, receipt)
    if release_fingerprint(ROOT) != original:
        raise RuntimeError("Candidate source changed during observation")
    receipt["status"] = "passed" if all(s["status"] == "passed" for s in receipt["scenarios"]) else "failed"
    receipt["stage"] = "complete"


def failure_detail(error):
    safe_messages = {"Codex and Git executables are required", "Host subprocess timed out",
                     "Host subprocess could not start", "Host reported a failed turn",
                     "Malformed host JSONL", "Incomplete host event lifecycle",
                     "Host prompt did not discover candidate skill root",
                     "Installed candidate fingerprint mismatch", "Project candidate fingerprint mismatch", "Staged candidate fingerprint mismatch",
                     "Owned subprocess containment unavailable",
                     "Candidate contains a linked resource",
                     "Fixture contains a linked resource",
                     "Fixture content assertion failed", "Expected fixture path to remain absent",
                     "Scenario requires filesystem assertions",
                     "Scenario changed files outside its allowed correction", "Candidate source changed during observation"}
    detail = str(error)
    return detail if detail in safe_messages or re.fullmatch(r"Host subprocess exited with code -?\d+", detail) else "Invalid host response or local fixture operation"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly invoke the authenticated local Codex model")
    parser.add_argument("--model", help="Required explicit model; no automatic fallback")
    parser.add_argument("--receipt", type=Path, help="Sanitized JSON summary destination")
    parser.add_argument("--timeout", type=float, default=180, help="Maximum seconds per child invocation")
    args = parser.parse_args()
    if not args.live or not args.model or not args.receipt:
        parser.error("--live, --model and --receipt are required")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be positive and finite")
    receipt = {"status": "blocked", "requested_model": args.model,
               "model_identity": "explicit CLI selection; server identity unavailable in exec events",
               "evidence_layer": "installed-skill-discovery plus authenticated-project-skill behavior",
               "automatic_plugin_hooks": "unverified; no hook trust changes",
               "delegation": "unverified; exec events do not prove agent model/effort separation",
               "catalogue": {"direct": "filesystem correction scenario", "interview": "pending decision preserves state",
                             "stack": "unverified: native goal and independent roles require host orchestration evidence",
                             "wayfinder": "unverified: parallel ticket orchestration requires separate host evidence"}}
    start = time.monotonic()
    try:
        live(args.model, args.timeout, receipt)
    except (RuntimeError, ValueError, AssertionError, OSError, KeyError) as error:
        # Child errors may contain credentials or model text; only our bounded failure categories persist.
        receipt["status"] = "failed"
        receipt["failure"] = failure_detail(error)
    receipt["elapsed_seconds"] = round(time.monotonic() - start, 3)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"Host observations: {receipt['status']}; sanitized receipt written")
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
