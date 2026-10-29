"""Exercise setup orchestration without installing tools or touching the real profile."""
import hashlib
import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def runtime():
    return load_module("runtime_operations", "scripts/setup-runtime.py")


@pytest.fixture
def layout(tmp_path, runtime, monkeypatch):
    plugin, project, profile, npm = [tmp_path / name for name in ("plugin", "project", "profile", "npm")]
    for directory in (plugin / "assets", project / ".codegraph", profile):
        directory.mkdir(parents=True)
    resource = plugin / "resource.txt"
    resource.write_bytes(b"bundled resource")
    (plugin / "assets/bundle-manifest.json").write_text(json.dumps({"sha256": {"resource.txt": hashlib.sha256(resource.read_bytes()).hexdigest()}}))
    package = npm / runtime.VERSIONS["codegraph"]["package"] / "package.json"
    package.parent.mkdir(parents=True)
    package.write_text(json.dumps({"version": runtime.VERSIONS["codegraph"]["version"]}))
    runtime.update_policy(profile / "AGENTS.md")
    runtime.update_policy(profile / "AGENTS.override.md")
    monkeypatch.setattr(runtime, "ROOT", plugin)
    calls = []

    def command(name, *args):
        calls.append((name, *args))
        if (name, *args) == ("npm", "root", "-g"):
            return str(npm)
        if name == "rtk":
            return "rtk " + runtime.VERSIONS["rtk"]["version"]
        if (name, *args) == ("codex", "mcp", "list", "--json"):
            return "[]"
        return "tool version"

    monkeypatch.setattr(runtime, "command", command)
    monkeypatch.setattr(runtime, "mcp_config", lambda: {"enabled": True, "transport": {"type": "stdio", "command": "codegraph", "args": ["serve", "--mcp"]}})
    monkeypatch.setattr(runtime.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout='{"results":[{"title":"real query result"}]}', stderr=""))
    return SimpleNamespace(plugin=plugin, project=project, profile=profile, package=package, calls=calls, command=command)


def test_check_requires_all_runtime_resources_but_never_claims_session_ready(runtime, layout):
    checks, errors = runtime.check(layout.project, layout.profile)
    assert errors == []
    assert all(check["ok"] for check in checks)
    assert {"existing AGENTS.override policy", "CodeGraph status", "UIUX real query"}.issubset({check["name"] for check in checks})
    assert not any("install" in call or "add" in call for call in layout.calls)


@pytest.mark.parametrize("fault,expected", [("package", "CodeGraph npm package"), ("resource", "bundled skills/resources"), ("query", "UIUX real query"), ("node", "Node"), ("index", "CodeGraph index")])
def test_check_accumulates_actionable_failures_without_repair(runtime, layout, monkeypatch, fault, expected):
    if fault == "package":
        layout.package.write_text('{"version":"wrong"}')
    elif fault == "resource":
        (layout.plugin / "resource.txt").write_text("tampered")
    elif fault == "query":
        monkeypatch.setattr(runtime.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr="query failed"))
    elif fault == "index":
        (layout.project / ".codegraph").rmdir()
    else:
        def command(name, *args):
            if name == "node":
                raise RuntimeError("node missing")
            return layout.command(name, *args)
        monkeypatch.setattr(runtime, "command", command)
    checks, errors = runtime.check(layout.project, layout.profile)
    assert next(item for item in checks if item["name"] == expected)["ok"] is False
    assert any(error.startswith(expected + ":") for error in errors)
    assert any(item["ok"] for item in checks), "Keep independent diagnostic evidence after a failure"


@pytest.mark.parametrize("indexed", [True, False])
def test_repair_adds_only_missing_mcp_and_updates_intended_index(runtime, layout, indexed):
    if not indexed:
        (layout.project / ".codegraph").rmdir()
    runtime.repair(layout.project, layout.profile)
    assert ("codex", "mcp", "add", "codegraph", "--", "codegraph", "serve", "--mcp") in layout.calls
    assert layout.calls[-1] == (("codegraph", "sync", str(layout.project)) if indexed else ("codegraph", "init", "-i", str(layout.project)))
    assert runtime.policy_current(layout.profile / "AGENTS.override.md")
    assert not any("install" in call for call in layout.calls)


def test_repair_installs_missing_pins_but_does_not_overwrite_mcp_conflict(runtime, layout, monkeypatch):
    layout.package.unlink()
    installs = []
    monkeypatch.setattr(runtime, "install_rtk", lambda: installs.append("verified RTK install"))

    def command(name, *args):
        if name == "rtk":
            raise RuntimeError("missing RTK")
        if (name, *args) == ("codex", "mcp", "list", "--json"):
            return '[{"name":"codegraph"}]'
        return layout.command(name, *args)

    monkeypatch.setattr(runtime, "command", command)
    monkeypatch.setattr(runtime, "mcp_config", lambda: {"enabled": False})
    with pytest.raises(RuntimeError, match="conflicts"):
        runtime.repair(layout.project, layout.profile)
    assert installs == ["verified RTK install"]
    assert any(call[:3] == ("npm", "install", "-g") for call in layout.calls)
    assert not any("add" in call or "remove" in call for call in layout.calls)


def test_repair_reuses_matching_mcp_and_rejects_missing_project(runtime, layout, monkeypatch):
    def command(name, *args):
        if (name, *args) == ("codex", "mcp", "list", "--json"):
            return '[{"name":"codegraph"}]'
        return layout.command(name, *args)
    monkeypatch.setattr(runtime, "command", command)
    runtime.repair(layout.project, layout.profile)
    assert not any("add" in call for call in layout.calls)
    with pytest.raises(RuntimeError, match="directory does not exist"):
        runtime.repair(layout.project / "absent", layout.profile)


@pytest.mark.parametrize("payload", ['{"enabled":true}', "invalid"])
def test_mcp_config_parses_or_reports_invalid_json(runtime, monkeypatch, payload):
    monkeypatch.setattr(runtime, "command", lambda *args: payload)
    if payload == "invalid":
        with pytest.raises(RuntimeError, match="registration unavailable"):
            runtime.mcp_config()
    else:
        assert runtime.mcp_config() == {"enabled": True}


@pytest.mark.parametrize("failure", [False, True])
def test_command_runs_without_shell_and_preserves_diagnostics(runtime, monkeypatch, tmp_path, failure):
    executable = tmp_path / "tool.exe"
    monkeypatch.setattr(runtime.shutil, "which", lambda name: str(executable))
    calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(returncode=2 if failure else 0, stdout=" output \n", stderr="precise failure")
    monkeypatch.setattr(runtime.subprocess, "run", run)
    if failure:
        with pytest.raises(RuntimeError, match=r"failed \(2\): precise failure"):
            runtime.command("tool", "--version")
    else:
        assert runtime.command("tool", "--version") == "output"
    assert calls[0][0] == [str(executable), "--version"]
    assert calls[0][1]["timeout"] == 90
    assert not calls[0][1].get("shell", False)


def test_command_rejects_missing_cli_and_unresolved_windows_shim(runtime, monkeypatch, tmp_path):
    monkeypatch.setattr(runtime.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="not found"):
        runtime.command("node")
    if runtime.os.name != "nt":
        return
    monkeypatch.setattr(runtime.shutil, "which", lambda name: str(tmp_path / (name + ".cmd")))
    with pytest.raises(RuntimeError, match="native Node entrypoint"):
        runtime.command("codex")
    entry = tmp_path / "node_modules/@openai/codex/bin/codex.js"
    entry.parent.mkdir(parents=True)
    entry.write_text("// shim")
    captured = []
    monkeypatch.setattr(runtime.subprocess, "run", lambda argv, **k: captured.append(argv) or SimpleNamespace(returncode=0, stdout="ok", stderr=""))
    assert runtime.command("codex", "--version") == "ok"
    assert captured[0][1:] == [str(entry), "--version"]


@pytest.mark.parametrize("system,archive_type", [("Windows", "zip"), ("Linux", "tar")])
@pytest.mark.parametrize("fault", [None, "checksum", "members"])
def test_rtk_download_verifies_hash_and_extracts_only_binary(runtime, monkeypatch, tmp_path, system, archive_type, fault):
    filename = "rtk.exe" if system == "Windows" else "rtk"
    binary = b"isolated fake binary"
    buffer = io.BytesIO()
    if archive_type == "zip":
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("dist/" + filename if fault != "members" else "wrong-file", binary)
            archive.writestr("../../unrelated", b"must not extract")
    else:
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            member = tarfile.TarInfo("dist/" + filename if fault != "members" else "wrong-file")
            member.size = len(binary)
            archive.addfile(member, io.BytesIO(binary))
    data = buffer.getvalue()
    digest = "0" * 64 if fault == "checksum" else hashlib.sha256(data).hexdigest()
    monkeypatch.setattr(runtime.platform, "system", lambda: system)
    monkeypatch.setattr(runtime.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(runtime.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("PATH", "original-path")
    monkeypatch.setitem(runtime.ENV, "PATH", "original-path")
    def urlopen(url, timeout):
        assert timeout in (30, 60)
        asset = "rtk-x86_64-pc-windows-msvc.zip" if system == "Windows" else "rtk-x86_64-unknown-linux-musl.tar.gz"
        return io.BytesIO((digest + "  " + asset + "\n").encode() if url.endswith("checksums.txt") else data)
    monkeypatch.setattr(runtime.urllib.request, "urlopen", urlopen)
    destination = tmp_path / ".local/bin" / filename
    if fault:
        with pytest.raises(RuntimeError, match="checksum|exactly one (regular )?binary"):
            runtime.install_rtk()
        assert not destination.exists()
    else:
        runtime.install_rtk()
        assert destination.read_bytes() == binary
        assert not destination.with_suffix(destination.suffix + ".new").exists()
        assert runtime.ENV["PATH"].startswith(str(destination.parent))
    assert not (tmp_path / "unrelated").exists()


def test_rtk_unsupported_platform_never_downloads(runtime, monkeypatch):
    monkeypatch.setattr(runtime.platform, "machine", lambda: "unsupported")
    with pytest.raises(RuntimeError, match="No pinned RTK"):
        runtime.install_rtk()


@pytest.mark.parametrize("system", ["Windows", "Linux"])
@pytest.mark.parametrize("limit_kind", ["download", "expanded"])
def test_rtk_resource_limits_preserve_existing_install(runtime, monkeypatch, tmp_path, system, limit_kind):
    binary = b"expanded-binary-exceeds-small-test-cap"
    filename = "rtk.exe" if system == "Windows" else "rtk"
    asset = "rtk-x86_64-pc-windows-msvc.zip" if system == "Windows" else "rtk-x86_64-unknown-linux-musl.tar.gz"
    buffer = io.BytesIO()
    if system == "Windows":
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr(filename, binary)
    else:
        with tarfile.open(fileobj=buffer, mode="w:gz") as bundle:
            member = tarfile.TarInfo(filename)
            member.size = len(binary)
            bundle.addfile(member, io.BytesIO(binary))
    data = buffer.getvalue()
    checksum = (hashlib.sha256(data).hexdigest() + "  " + asset).encode()
    monkeypatch.setattr(runtime.platform, "system", lambda: system)
    monkeypatch.setattr(runtime.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(runtime.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(runtime, "MAX_RTK_ARCHIVE_BYTES", len(data) - 1 if limit_kind == "download" else len(data) + 1, raising=False)
    monkeypatch.setattr(runtime, "MAX_RTK_BINARY_BYTES", len(binary) - 1 if limit_kind == "expanded" else len(binary) + 1, raising=False)
    monkeypatch.setattr(runtime.urllib.request, "urlopen", lambda url, **kw: io.BytesIO(checksum if url.endswith("checksums.txt") else data))
    destination = tmp_path / ".local/bin" / filename
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"previous verified binary")
    with pytest.raises(RuntimeError, match="limit|large|size|bound|exceed"):
        runtime.install_rtk()
    assert destination.read_bytes() == b"previous verified binary"
    assert not destination.with_suffix(destination.suffix + ".new").exists()


@pytest.mark.parametrize("system", ["Windows", "Linux"])
@pytest.mark.parametrize("kind", ["symlink", "duplicate"])
def test_rtk_rejects_nonregular_or_ambiguous_binary(runtime, monkeypatch, tmp_path, system, kind):
    filename = "rtk.exe" if system == "Windows" else "rtk"
    asset = "rtk-x86_64-pc-windows-msvc.zip" if system == "Windows" else "rtk-x86_64-unknown-linux-musl.tar.gz"
    buffer = io.BytesIO()
    if system == "Windows":
        with zipfile.ZipFile(buffer, "w") as archive:
            if kind == "symlink":
                member = zipfile.ZipInfo(filename)
                member.create_system = 3
                member.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(member, "untrusted-target")
            else:
                archive.writestr("first/" + filename, b"one")
                archive.writestr("second/" + filename, b"two")
    else:
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for prefix in ([""] if kind == "symlink" else ["first/", "second/"]):
                member = tarfile.TarInfo(prefix + filename)
                if kind == "symlink":
                    member.type = tarfile.SYMTYPE
                    member.linkname = "untrusted-target"
                    archive.addfile(member)
                else:
                    member.size = 3
                    archive.addfile(member, io.BytesIO(b"one"))
    data = buffer.getvalue()
    checksum = (hashlib.sha256(data).hexdigest() + "  " + asset).encode()
    monkeypatch.setattr(runtime.platform, "system", lambda: system)
    monkeypatch.setattr(runtime.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(runtime.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(runtime.urllib.request, "urlopen", lambda url, **kw: io.BytesIO(checksum if url.endswith("checksums.txt") else data))
    with pytest.raises(RuntimeError, match="binary|regular|member"):
        runtime.install_rtk()
    assert not (tmp_path / ".local/bin" / filename).exists()


@pytest.mark.parametrize("system", ["Windows", "Linux"])
@pytest.mark.parametrize("limit_kind", ["total_expansion", "member_count"])
def test_rtk_limits_include_irrelevant_archive_members(runtime, monkeypatch, tmp_path, system, limit_kind):
    filename = "rtk.exe" if system == "Windows" else "rtk"
    asset = "rtk-x86_64-pc-windows-msvc.zip" if system == "Windows" else "rtk-x86_64-unknown-linux-musl.tar.gz"
    entries = [("irrelevant.txt", b"X" * 128), (filename, b"binary")]
    buffer = io.BytesIO()
    if system == "Windows":
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in entries:
                archive.writestr(name, content)
    else:
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for name, content in entries:
                member = tarfile.TarInfo(name)
                member.size = len(content)
                archive.addfile(member, io.BytesIO(content))
    data = buffer.getvalue()
    checksum = (hashlib.sha256(data).hexdigest() + "  " + asset).encode()
    monkeypatch.setattr(runtime.platform, "system", lambda: system)
    monkeypatch.setattr(runtime.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(runtime.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(runtime, "MAX_RTK_EXPANDED_BYTES", 64 if limit_kind == "total_expansion" else 200000, raising=False)
    monkeypatch.setattr(runtime, "MAX_RTK_MEMBERS", 1 if limit_kind == "member_count" else 10, raising=False)
    monkeypatch.setattr(runtime.urllib.request, "urlopen", lambda url, **kw: io.BytesIO(checksum if url.endswith("checksums.txt") else data))
    destination = tmp_path / ".local/bin" / filename
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"keep original")
    with pytest.raises(RuntimeError, match="limit|large|size|bound|exceed|members"):
        runtime.install_rtk()
    assert destination.read_bytes() == b"keep original"


def test_rtk_tar_metadata_counts_toward_expansion_limit_before_install(runtime, monkeypatch, tmp_path):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz", format=tarfile.PAX_FORMAT) as archive:
        member = tarfile.TarInfo("rtk")
        member.size = 2
        member.pax_headers = {"comment": "X" * 100000}
        archive.addfile(member, io.BytesIO(b"OK"))
    data = buffer.getvalue()
    assert len(data) < 1024, "The fixture isolates metadata expansion rather than download size"
    asset = "rtk-x86_64-unknown-linux-musl.tar.gz"
    checksum = (hashlib.sha256(data).hexdigest() + "  " + asset).encode()
    monkeypatch.setattr(runtime.platform, "system", lambda: "Linux")
    monkeypatch.setattr(runtime.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(runtime.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(runtime, "MAX_RTK_EXPANDED_BYTES", 1024)
    monkeypatch.setattr(runtime.urllib.request, "urlopen", lambda url, **kw: io.BytesIO(checksum if url.endswith("checksums.txt") else data))
    destination = tmp_path / ".local/bin/rtk"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"previous verified binary")
    with pytest.raises(RuntimeError, match="limit|large|size|bound|exceed"):
        runtime.install_rtk()
    assert destination.read_bytes() == b"previous verified binary"
    assert not destination.with_suffix(".new").exists()


@pytest.mark.parametrize("repair_failure", [False, True])
def test_main_keeps_session_verification_pending_and_reports_repair_failure(runtime, monkeypatch, tmp_path, capsys, repair_failure):
    monkeypatch.setattr(sys, "argv", ["setup-runtime.py", "--project", str(tmp_path), "--repair"])
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "profile"))
    def repair(project, profile):
        assert project == tmp_path.resolve()
        assert profile == (tmp_path / "profile").resolve()
        if repair_failure:
            raise RuntimeError("precise repair failure")
    monkeypatch.setattr(runtime, "repair", repair)
    monkeypatch.setattr(runtime, "check", lambda *args: ([{"name": "isolated check", "ok": True}], []))
    assert runtime.main() == (1 if repair_failure else 0)
    report = json.loads(capsys.readouterr().out)
    assert report["ready"] is False and report["session_verification_required"] is True
    assert report["runtime_ready"] is not repair_failure
    assert report["errors"] == (["precise repair failure"] if repair_failure else [])


def test_reader_main_uses_reader_bearer_and_bounded_requests(monkeypatch, capsys):
    reader = load_module("reader_cli_test", "skills/setup-sonarqube/scripts/read-analysis.py")
    monkeypatch.setattr(sys, "argv", ["read-analysis.py", "--project", "private", "--analysis-id", "analysis", "--task-id", "task", "--source-key", "private:src.py"])
    monkeypatch.setenv("SONAR_HOST_URL", "http://127.0.0.1:19000/")
    monkeypatch.setenv("SONAR_READER_TOKEN", "isolated-reader-value")
    calls = []
    def urlopen(request, timeout):
        calls.append(request.full_url)
        assert request.get_header("Authorization") == "Bearer isolated-reader-value"
        assert timeout == 30
        return io.BytesIO(b'{"evidence":true}')
    monkeypatch.setattr(reader, "urlopen", urlopen)
    reader.main()
    assert len(calls) == 5
    assert all(url.startswith("http://127.0.0.1:19000/api/") for url in calls)
    assert set(json.loads(capsys.readouterr().out)) == {"issues", "measures", "source", "task", "gate"}


def test_reader_cli_requires_analysis_arguments_before_requests(monkeypatch):
    reader = load_module("reader_required_args_test", "skills/setup-sonarqube/scripts/read-analysis.py")
    monkeypatch.setattr(sys, "argv", ["read-analysis.py"])
    with pytest.raises(SystemExit) as error:
        reader.main()
    assert error.value.code == 2


@pytest.mark.parametrize("event", ["SessionStart", "UserPromptSubmit", "SubagentStart"])
@pytest.mark.parametrize("with_details", [True, False])
def test_actual_packaged_hook_resolves_skills_from_its_own_location(tmp_path, event, with_details):
    project, profile = tmp_path / "unrelated project", tmp_path / "clean profile"
    project.mkdir()
    profile.mkdir()
    env = dict(os.environ, HOME=str(profile), USERPROFILE=str(profile), CODEX_HOME=str(profile / ".codex"), CODEX_PLUGIN_ROOT=str(tmp_path / "wrong root"))
    payload = {"hook_event_name": event, "cwd": str(project)}
    if with_details:
        payload.update(prompt="Keep this original request intact", agent_type="contract evaluator")
    result = subprocess.run([shutil.which("node") or "node", str(ROOT / "hooks/stack.js")], input="\ufeff" + json.dumps(payload), capture_output=True, text=True, encoding="utf-8", env=env, cwd=project, timeout=15)
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == event
    context = output["additionalContext"]
    if event == "SubagentStart":
        assert ("contract evaluator" if with_details else "assigned role") in context
        assert "Do not register another goal, run setup, or spawn recursive role groups" in context
    else:
        for skill in ("setup", "kiss-chris-stack"):
            actual_path = ROOT / "skills" / skill / "SKILL.md"
            assert actual_path.is_file()
            assert json.dumps(str(actual_path)) in context
        assert (payload["prompt"] if with_details else "Continue the original user request already in this session.") in context
    assert list(project.iterdir()) == list(profile.iterdir()) == []


@pytest.mark.parametrize("payload", ["invalid JSON", "{}", '{"hook_event_name":"Unknown"}', '{"hook_event_name":"SessionStart","cwd":""}'])
def test_actual_packaged_hook_rejects_invalid_input_without_context(tmp_path, payload):
    result = subprocess.run([shutil.which("node") or "node", str(ROOT / "hooks/stack.js")], input=payload, capture_output=True, text=True, encoding="utf-8", cwd=tmp_path, timeout=15)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "hook failed" in result.stderr
