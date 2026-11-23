"""Host harness mechanics only; synthetic events never prove live model behavior."""
import importlib.util
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
RUNNER = ROOT / "scripts/test-host-workflows.py"
PUBLIC_SENTINEL = "test-only-secret-do-not-retain-729"
USAGE = {"input_tokens": 12, "cached_input_tokens": 3, "output_tokens": 5}


@pytest.fixture
def harness():
    assert RUNNER.is_file(), "Provide the opt-in actual host scenario runner"
    spec = importlib.util.spec_from_file_location("host_workflow_tests", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def events(*, usage=USAGE, text=PUBLIC_SENTINEL):
    completed = {"type": "turn.completed"}
    if usage is not None:
        completed["usage"] = usage
    return "\n".join(json.dumps(event) for event in [
        {"type": "thread.started", "thread_id": "synthetic-thread"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": text}},
        completed,
    ]) + "\n"


def test_event_receipt_retains_observed_usage_without_transcript(harness):
    receipt = harness.parse_events(events(usage={**USAGE, "unknown_field": PUBLIC_SENTINEL}))
    assert receipt["status"] == "passed"
    assert receipt["usage"] == USAGE
    assert receipt["missing_usage"] == []
    serialized = json.dumps(receipt)
    assert PUBLIC_SENTINEL not in serialized
    assert "agent_message" not in serialized


def test_missing_usage_is_explicit_and_never_fabricated_as_zero(harness):
    receipt = harness.parse_events(events(usage=None))
    assert receipt["usage"] == {}
    assert set(receipt["missing_usage"]) == set(USAGE)


def test_partial_usage_preserves_only_observed_metrics(harness):
    receipt = harness.parse_events(events(usage={"input_tokens": 0}))
    assert receipt["usage"] == {"input_tokens": 0}
    assert set(receipt["missing_usage"]) == {"cached_input_tokens", "output_tokens"}


@pytest.mark.parametrize("payload", [
    "", "{broken", "[]\n", '{"type":"thread.started"}\n',
    '{"type":"turn.completed","usage":{}}\n',
    events().replace('"turn.completed"', '"turn.failed"'),
    events() + '{"type":"error","message":"failed"}\n',
    events() + "{broken\n",
])
def test_malformed_incomplete_and_failed_events_cannot_pass(harness, payload):
    with pytest.raises((ValueError, RuntimeError)):
        harness.parse_events(payload)


@pytest.mark.parametrize("kinds", [
    ("thread.started", "turn.completed"),
    ("thread.started", "turn.started", "turn.started", "turn.completed"),
    ("turn.started", "thread.started", "turn.completed"),
    ("thread.started", "item.completed", "turn.started", "turn.completed"),
    ("thread.started", "thread.started", "turn.started", "turn.completed"),
    ("thread.started", "turn.started", "turn.completed", "turn.completed"),
], ids=["missing-turn-start", "repeated-turn-start", "reordered-starts",
        "item-before-turn", "repeated-thread-start", "repeated-completion"])
def test_invalid_lifecycle_order_cannot_prove_execution(harness, kinds):
    payload = "\n".join(json.dumps({"type": kind}) for kind in kinds)
    with pytest.raises((ValueError, RuntimeError)):
        harness.parse_events(payload)


@pytest.mark.parametrize("value", [-1, "12", True, None])
def test_invalid_observed_usage_cannot_be_reported_as_valid(harness, value):
    with pytest.raises((ValueError, RuntimeError)):
        harness.parse_events(events(usage={"input_tokens": value}))


def test_run_host_preserves_argv_cwd_and_returns_only_summary(harness, tmp_path):
    literal = "argument with spaces & ; $(literal)"
    code = (
        "import os, sys; "
        "assert sys.argv[1] == " + repr(literal) + "; "
        "assert os.getcwd() == " + repr(str(tmp_path)) + "; "
        "sys.stderr.write(" + repr(PUBLIC_SENTINEL) + "); "
        "sys.stdout.write(" + repr(events()) + ")"
    )
    receipt = harness.run_host([sys.executable, "-c", code, literal], cwd=tmp_path, timeout=7)
    assert receipt["status"] == "passed"
    assert PUBLIC_SENTINEL not in json.dumps(receipt)
    assert list(tmp_path.iterdir()) == [], "Do not persist raw child streams"


@pytest.mark.parametrize("explicit_environment", [False, True], ids=["inherited", "supplied"])
def test_child_clears_desktop_identity_without_changing_parent_or_normal_environment(
    harness, monkeypatch, tmp_path, explicit_environment,
):
    desktop = (
        "CODEX_APP_RUNTIME_CLI_PATH", "CODEX_APP_TOOLS_PIPE_PATH", "CODEX_INTERNAL_ORIGINATOR_OVERRIDE",
        "CODEX_SESSION_ID", "CODEX_THREAD_ID", "CODEX_TOOL_CALL_ID", "CODEX_TASK_WORKSPACE_VERIFYING_IDENTITY",
        "CODEX_SHELL", "CODEX_WINDOWS_REGISTERED_CORE", "CODEX_WINDOWS_SANDBOX_PACKAGE_FAMILY",
    )
    for name in desktop:
        monkeypatch.setenv(name, "1" if name == "CODEX_WINDOWS_REGISTERED_CORE" else "synthetic-desktop")
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "ordinary-auth-profile"))
    monkeypatch.setenv("KISS_ORDINARY_SETTING", "inherited")
    parent = dict(os.environ)
    supplied = {**parent, "KISS_ORDINARY_SETTING": "supplied"} if explicit_environment else None
    expected = dict(supplied if explicit_environment else parent)
    preserved = {name: expected[name] for name in ("PATH", "CODEX_HOME", "KISS_ORDINARY_SETTING")}
    code = (
        "import os; "
        "assert all(name not in os.environ for name in " + repr(desktop) + "), 'desktop identity leaked'; "
        "assert all(os.environ.get(name) == value for name, value in " + repr(preserved) + ".items()), 'normal setting changed'; "
        "print('isolated')"
    )
    try:
        assert harness.child([sys.executable, "-c", code], cwd=tmp_path, timeout=7, env=supplied).strip() == "isolated"
    except RuntimeError as error:
        pytest.fail(str(error), pytrace=False)
    finally:
        assert dict(os.environ) == parent, "Isolation must not mutate the caller environment"
        if supplied is not None:
            assert supplied == expected and all(name in supplied for name in desktop)


@pytest.mark.parametrize("failure", ["exit", "timeout"])
def test_child_failure_is_visible_without_retaining_secret_streams(harness, tmp_path, failure):
    code = "import sys, time; print(" + repr(PUBLIC_SENTINEL) + ", flush=True); sys.stderr.write(" + repr(PUBLIC_SENTINEL) + "); "
    code += "time.sleep(30)" if failure == "timeout" else "sys.exit(23)"
    started = time.monotonic()
    with pytest.raises((ValueError, RuntimeError)) as error:
        harness.run_host([sys.executable, "-c", code], cwd=tmp_path, timeout=0.5)
    assert time.monotonic() - started < 10, "Timeout must bound the actual child"
    assert PUBLIC_SENTINEL not in str(error.value)
    assert str(error.value).strip()
    assert list(tmp_path.iterdir()) == []


def test_timeout_stops_owned_tool_descendant(harness, tmp_path):
    marker = tmp_path / "owned-processes.json"
    forbidden = tmp_path / "tool-continued-after-timeout.txt"
    grandchild = "import pathlib, sys, time; time.sleep(3); pathlib.Path(sys.argv[1]).write_text('continued')"
    parent = (
        "import json, os, pathlib, subprocess, sys, time; "
        "child = subprocess.Popen([sys.executable, '-c', " + repr(grandchild) + ", sys.argv[2]]); "
        "pathlib.Path(sys.argv[1]).write_text(json.dumps([os.getpid(), child.pid])); time.sleep(30)"
    )
    try:
        with pytest.raises(RuntimeError, match="timed out|timeout"):
            harness.run_host([sys.executable, "-c", parent, str(marker), str(forbidden)], cwd=tmp_path, timeout=1)
        assert marker.is_file(), "The test must actually start an owned descendant"
        deadline = time.monotonic() + 3.5
        while time.monotonic() < deadline and not forbidden.exists():
            time.sleep(0.05)
        assert not forbidden.exists(), "A timed-out host must not leave its tool running"
    finally:
        if marker.is_file():
            for pid in json.loads(marker.read_text(encoding="utf-8")):
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                except OSError as error:
                    if getattr(error, "winerror", None) != 87:
                        raise


def test_assertions_check_actual_files_and_preserve_unanswered_state(harness, tmp_path):
    marker = tmp_path / "decision.txt"
    marker.write_text("pending user answer\n", encoding="utf-8")
    assertions = [
        {"path": "decision.txt", "content": "pending user answer\n"},
        {"path": "unapproved.txt", "absent": True},
    ]
    harness.assert_scenario(tmp_path, assertions)
    assert marker.read_text(encoding="utf-8") == "pending user answer\n"
    marker.write_text("model claimed approval\n", encoding="utf-8")
    with pytest.raises((AssertionError, ValueError, RuntimeError)):
        harness.assert_scenario(tmp_path, assertions)
    marker.write_text("pending user answer\n", encoding="utf-8")
    (tmp_path / "unapproved.txt").write_text("unauthorized", encoding="utf-8")
    with pytest.raises((AssertionError, ValueError, RuntimeError)):
        harness.assert_scenario(tmp_path, assertions)


def test_edit_assertion_requires_expected_output_not_model_success(harness, tmp_path):
    assertions = [{"path": "result.txt", "content": "expected edit\n"}]
    with pytest.raises((AssertionError, ValueError, RuntimeError)):
        harness.assert_scenario(tmp_path, assertions)
    (tmp_path / "result.txt").write_text("expected edit\n", encoding="utf-8")
    harness.assert_scenario(tmp_path, assertions)


def test_missing_assertions_cannot_turn_execution_success_into_behavioral_proof(harness, tmp_path):
    execution = harness.parse_events(events())
    assert execution["status"] == "passed"
    assert execution["evidence_layer"] == "event-execution"
    with pytest.raises((ValueError, AssertionError, RuntimeError)):
        harness.assert_scenario(tmp_path, [])


@pytest.mark.parametrize("kind", ["file", "directory"])
def test_snapshot_rejects_outside_links_before_reading(harness, monkeypatch, tmp_path, kind):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_file = outside / "secret.txt"
    outside_file.write_text(PUBLIC_SENTINEL, encoding="utf-8")
    link = project / "linked-resource"
    try:
        link.symlink_to(outside_file if kind == "file" else outside, target_is_directory=kind == "directory")
    except OSError:
        if os.name != "nt" or kind != "directory":
            pytest.skip("This platform cannot create the requested fixture symlink")
        result = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(link), str(outside)],
                                capture_output=True, text=True, timeout=10)
        if result.returncode:
            pytest.skip("This Windows host cannot create a fixture directory junction")
    reads = []
    original_read = Path.read_bytes

    def observed_read(path):
        if path.resolve() == outside_file.resolve():
            reads.append(path)
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", observed_read)
    try:
        try:
            with pytest.raises((ValueError, RuntimeError)):
                harness.snapshot(project)
        finally:
            assert not reads, "Reject fixture links before reading any outside target"
    finally:
        if link.is_junction():
            link.rmdir()
        else:
            link.unlink()


def test_cli_help_is_available_without_live_prerequisites():
    assert RUNNER.is_file(), "Provide the actual CLI entrypoint"
    result = subprocess.run([sys.executable, str(RUNNER), "--help"], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert "--live" in result.stdout and "--model" in result.stdout


def test_explicit_live_request_fails_when_host_is_missing(tmp_path):
    assert RUNNER.is_file(), "Provide the actual CLI entrypoint"
    receipt = tmp_path / "receipt.json"
    env = {**os.environ, "PATH": "", "HOST_TEST_PUBLIC_SENTINEL": PUBLIC_SENTINEL}
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--live", "--model", "unavailable-test-model", "--receipt", str(receipt)],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode != 0, "An explicitly requested live check cannot silently skip"
    assert (result.stdout + result.stderr).strip()
    assert PUBLIC_SENTINEL not in result.stdout + result.stderr
    assert receipt.is_file(), "Keep a sanitized prerequisite failure receipt"
    summary = json.loads(receipt.read_text(encoding="utf-8"))
    assert summary["status"] in {"failed", "blocked"}
    assert PUBLIC_SENTINEL not in json.dumps(summary)


@pytest.fixture
def synthetic_host_cli(tmp_path, harness, monkeypatch, capsys):
    """Real child processes with a fake CLI protocol; never real host/model proof."""
    candidate = tmp_path / "synthetic candidate"
    candidate.mkdir()
    harness.copy_candidate(ROOT, candidate)
    spec = importlib.util.spec_from_file_location("trusted_release_resources", ROOT / "scripts/check-release.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    for relative in checker.RELEASE_EXTRAS:
        path = candidate / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / relative).read_bytes())
    files = {
        "tests/fixtures/host-workflows/scenarios.json": (ROOT / "tests/fixtures/host-workflows/scenarios.json").read_text(encoding="utf-8"),
        ".env": PUBLIC_SENTINEL,
        ".env.synthetic": PUBLIC_SENTINEL,
        ".git/ignored-secret": PUBLIC_SENTINEL,
        ".sonar-evidence/ignored-secret": PUBLIC_SENTINEL,
        "skills/.env.synthetic": PUBLIC_SENTINEL,
        "skills/.sonar-evidence/ignored-secret": PUBLIC_SENTINEL,
    }
    for name, content in files.items():
        path = candidate / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    shutil.copyfile(RUNNER, candidate / "scripts/test-host-workflows.py")
    assert (candidate / "scripts/test-host-workflows.py").read_bytes() == RUNNER.read_bytes()
    bin_path = tmp_path / "synthetic bin"
    bin_path.mkdir()
    fake = bin_path / "fake_cli.py"
    fake.write_text('''import hashlib, json, os, shutil, sys
from pathlib import Path
args = sys.argv[1:]
mode = os.environ["SYNTHETIC_MODE"]
trace = Path(os.environ["SYNTHETIC_TRACE"])
sentinel = os.environ["SYNTHETIC_PUBLIC_SENTINEL"]
def record(kind, **values):
    with trace.open("a", encoding="utf-8") as output:
        output.write(json.dumps({"kind": kind, **values}) + "\\n")
if args[0] == "__git__":
    record("git-init")
elif args == ["--version"]:
    print("synthetic-codex 0.0-test")
elif "plugin" in args:
    setting = next(value for value in args if value.startswith("marketplaces.kiss-chris-stack.source="))
    source = Path(setting.split("=", 1)[1].strip('"'))
    inventory = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in source.rglob("*") if p.is_file()}
    record("install", files=inventory)
    if any(any(part.startswith(".env") or part in (".git", ".sonar-evidence") for part in Path(name).parts)
           for name in inventory):
        sys.exit(71)
    installed = Path(os.environ["CODEX_HOME"]) / "installed"
    shutil.copytree(source, installed)
    if mode == "source-mismatch":
        (installed / "skills/kiss-chris-stack/SKILL.md").write_text("different candidate")
    if mode == "missing-guide":
        (installed / "docs/LIFECYCLE.md").unlink(missing_ok=True)
    if mode == "changed-guide":
        (installed / "docs").mkdir(exist_ok=True)
        (installed / "docs/OPERATIONS.md").write_text("changed operative guide")
    print(json.dumps({"installedPath": str(installed)}))
elif "debug" in args:
    skills = (Path.cwd() / ".agents/skills") if (Path.cwd() / ".agents").exists() else Path(os.environ["CODEX_HOME"]) / "installed/skills"
    record("discovery", skills=str(skills))
    if mode == "missing-candidate":
        rendered = "No candidate skills found. " + sentinel
    else:
        if mode == "wrong-candidate-root":
            skills = skills.parent / "unrelated/skills"
        rendered = "`r0` = `" + skills.as_posix() + "` file: r0/kiss-chris-stack/SKILL.md " + sentinel
    print(json.dumps({"prompt": rendered}))
elif "exec" in args:
    model = args[args.index("--model") + 1]
    project = Path.cwd()
    candidate_skill = project / ".agents/skills/kiss-chris-stack/SKILL.md"
    scenario = next(item for item in json.loads(Path(os.environ["SYNTHETIC_SCENARIOS"]).read_text())
                    if item["id"] == project.name)
    record("exec", model=model, scenario=project.name,
           candidate_bound=str(candidate_skill) in args[-1] or candidate_skill.as_posix() in args[-1],
           fixture_prompt_preserved=scenario["prompt"] in args[-1],
           pasted_candidate=candidate_skill.read_text().strip() in args[-1])
    assert "--json" in args and "--ephemeral" in args
    assert "--ignore-user-config" in args
    assert args[args.index("--sandbox") + 1] == "workspace-write"
    assert Path(args[args.index("-C") + 1]) == project
    assert not any("dangerously" in value or "skip-trust" in value for value in args)
    if (project / "result.txt").exists() and mode != "claimed-edit-only":
        (project / "result.txt").write_text("expected edit\\n", encoding="utf-8")
    if (project / "decision.txt").exists() and mode == "unanswered-write":
        (project / "decision.txt").write_text("accepted\\n", encoding="utf-8")
    for event in [{"type":"thread.started","thread_id":"synthetic"}, {"type":"turn.started"},
                  {"type":"item.completed","item":{"type":"agent_message","text":sentinel}},
                  {"type":"turn.completed","usage":{"input_tokens":12,"cached_input_tokens":3,"output_tokens":5}}]:
        print(json.dumps(event))
else:
    sys.exit(72)
sys.stderr.write(sentinel)
''', encoding="utf-8")
    for name, extra in (("codex", ""), ("git", " __git__")):
        launcher = bin_path / (name + ".cmd" if os.name == "nt" else name)
        if os.name == "nt":
            launcher.write_text('@"' + sys.executable + '" "' + str(fake) + '"' + extra + ' %*\n', encoding="utf-8")
        else:
            launcher.write_text('#!/bin/sh\nexec "' + sys.executable + '" "' + str(fake) + '"' + extra + ' "$@"\n', encoding="utf-8")
            launcher.chmod(0o755)
    scratch = tmp_path / "owned temporary projects"
    scratch.mkdir()
    runtime_names = [path.relative_to(candidate).as_posix() for path in harness.candidate_files(candidate)]
    runtime_hashes = {name: hashlib.sha256((candidate / name).read_bytes()).hexdigest() for name in runtime_names}
    expected = hashlib.sha256(json.dumps(runtime_hashes, sort_keys=True).encode()).hexdigest()
    artifact_hashes = {**runtime_hashes, **{
        name: hashlib.sha256((candidate / name).read_bytes()).hexdigest() for name in checker.RELEASE_EXTRAS
    }}
    expected_release = checker.source_identity(candidate.resolve())["fingerprint"]

    def run(mode, *, imported_main=False):
        receipt = tmp_path / (mode + "-receipt.json")
        trace = tmp_path / (mode + "-mechanics-trace.jsonl")
        git = shutil.which("git")
        assert git, "The CLI mechanics fixture needs Git for disposable repository initialization"
        env = {**os.environ, "PATH": str(bin_path) + os.pathsep + str(Path(git).parent), "SYNTHETIC_MODE": mode,
               "SYNTHETIC_TRACE": str(trace), "SYNTHETIC_PUBLIC_SENTINEL": PUBLIC_SENTINEL,
               "SYNTHETIC_SCENARIOS": str(candidate / "tests/fixtures/host-workflows/scenarios.json"),
               "TMP": str(scratch), "TEMP": str(scratch), "TMPDIR": str(scratch)}
        arguments = [str(candidate / "scripts/test-host-workflows.py"), "--live", "--model", "synthetic-mechanics-model",
                     "--timeout", "8", "--receipt", str(receipt)]
        if imported_main:
            # Exercise the owning module for coverage as well as the standalone CLI process.
            with monkeypatch.context() as patch:
                patch.setattr(harness, "ROOT", candidate)
                patch.setattr(harness, "SCENARIOS", candidate / "tests/fixtures/host-workflows/scenarios.json")
                patch.setattr(sys, "argv", arguments)
                patch.setattr(os, "environ", env)
                patch.setattr(harness.tempfile, "tempdir", str(scratch))
                patch.chdir(tmp_path)
                returncode = harness.main()
            captured = capsys.readouterr()
            result = subprocess.CompletedProcess(arguments, returncode, captured.out, captured.err)
        else:
            result = subprocess.run([sys.executable, *arguments], cwd=tmp_path, env=env,
                                    capture_output=True, text=True, timeout=45)
        summary = json.loads(receipt.read_text(encoding="utf-8"))
        calls = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
        assert PUBLIC_SENTINEL not in result.stdout + result.stderr + json.dumps(summary) + json.dumps(calls)
        assert list(scratch.iterdir()) == [], "Remove owned staging/profile/projects after success or failure"
        assert (candidate / ".env").read_text(encoding="utf-8") == PUBLIC_SENTINEL
        return result, summary, calls

    return run, expected, artifact_hashes, expected_release


@pytest.mark.parametrize("imported_main", [False, True], ids=["cli-process", "public-main"])
def test_synthetic_cli_mechanics_bind_candidate_discovery_execution_and_state(synthetic_host_cli, imported_main):
    run, expected, artifact_hashes, expected_release = synthetic_host_cli
    result, receipt, calls = run("success", imported_main=imported_main)
    assert result.returncode == 0, receipt
    assert receipt["status"] == "passed" and receipt["stage"] == "complete"
    assert receipt["candidate_fingerprint"] == expected
    assert receipt["release_candidate_fingerprint"] == expected_release
    assert receipt["cli_version"] == "synthetic-codex 0.0-test"
    assert receipt["requested_model"] == "synthetic-mechanics-model"
    assert receipt["installed_candidate_discovery"]["fingerprint_matches"] is True
    assert receipt["installed_candidate_discovery"]["candidate_skill_discovered"] is True
    assert {s["id"] for s in receipt["scenarios"]} == {"direct-edit", "unanswered-decision"}
    for scenario in receipt["scenarios"]:
        assert scenario["status"] == "passed"
        assert scenario["candidate_discovery"]["candidate_skill_discovered"] is True
        assert scenario["filesystem_assertions"] == scenario["state_preservation"] == "passed"
        assert scenario["execution"]["usage"] == USAGE
    installed_files = next(call["files"] for call in calls if call["kind"] == "install")
    assert all(installed_files[name] == digest for name, digest in artifact_hashes.items())
    assert {call["model"] for call in calls if call["kind"] == "exec"} == {"synthetic-mechanics-model"}
    assert all(call["candidate_bound"] for call in calls if call["kind"] == "exec"), "Bind the exact staged skill despite same-name user skills"
    assert all(call["fixture_prompt_preserved"] and not call["pasted_candidate"] for call in calls if call["kind"] == "exec")
    assert "unverified" in receipt["automatic_plugin_hooks"]
    assert "unverified" in receipt["delegation"]


@pytest.mark.parametrize("mode,stage", [
    ("missing-candidate", "installed-candidate-discovery"),
    ("wrong-candidate-root", "installed-candidate-discovery"),
    ("source-mismatch", "isolated-candidate-install"),
    ("missing-guide", "isolated-candidate-install"),
    ("changed-guide", "isolated-candidate-install"),
    ("claimed-edit-only", "direct-edit:filesystem-assertions"),
    ("unanswered-write", "unanswered-decision:filesystem-assertions"),
])
def test_synthetic_cli_mechanics_reject_false_success(synthetic_host_cli, mode, stage):
    run, expected, _, _ = synthetic_host_cli
    result, receipt, calls = run(mode)
    assert result.returncode != 0
    assert receipt["status"] == "failed"
    assert receipt["candidate_fingerprint"] == expected
    if mode in {"missing-candidate", "wrong-candidate-root", "source-mismatch", "missing-guide", "changed-guide"}:
        assert receipt["stage"] == stage
        assert receipt["failure"]
        assert not any(call["kind"] == "exec" for call in calls)
    else:
        failed = next(s for s in receipt["scenarios"] if s["id"] == stage.split(":")[0])
        assert failed["status"] == "failed"
        assert failed["failed_stage"] == stage
        assert failed["failure"]
        assert any(call["kind"] == "exec" for call in calls), "Claims must reach independent filesystem assertions"
