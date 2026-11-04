"""Configured Wayfinder storage and safe setup of its operations binding."""

import importlib.util
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "scripts/evaluation-config.py"
SETUP = ROOT / "scripts/setup-wayfinder.py"
LOCAL = {"provider": "local", "directory": ".scratch"}
BEGIN = "<!-- kiss-chris-stack:wayfinder-tracker:start -->"
END = "<!-- kiss-chris-stack:wayfinder-tracker:end -->"


def write_config(project, tracker):
    path = project / "kiss-chris-stack.config.json"
    path.write_text(json.dumps({"wayfinder-tracker": tracker}), encoding="utf-8")
    return path


def run_config(project, *arguments):
    return subprocess.run(
        [sys.executable, str(CONFIG), "--project", str(project), *arguments],
        capture_output=True, text=True, timeout=15,
    )


def run_setup(project, *arguments, configuration=None):
    return subprocess.run(
        [sys.executable, str(SETUP), "--project", str(project), *arguments],
        input=json.dumps(configuration) if configuration is not None else None,
        capture_output=True, text=True, timeout=15,
    )


def test_missing_tracker_defaults_to_local_without_creating_project_files(tmp_path):
    result = run_config(tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["wayfinder-tracker"] == LOCAL
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("tracker", [
    {"provider": "local", "directory": "planning/wayfinder"},
    {"provider": "github", "repository": "Acme/Stack"},
    {"provider": "gitlab", "project": "https://gitlab.example.test/group/nested/stack"},
])
def test_tracker_variants_are_preserved_without_injecting_local_fields(tmp_path, tracker):
    path = write_config(tmp_path, tracker)
    result = run_config(tmp_path, "--update")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["wayfinder-tracker"] == tracker
    assert json.loads(path.read_text(encoding="utf-8"))["wayfinder-tracker"] == tracker


def test_prepare_creates_only_selected_local_root_and_operations_document(tmp_path):
    write_config(tmp_path, {"provider": "local", "directory": "planning/wayfinder"})
    result = run_setup(tmp_path, "--prepare")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "planning/wayfinder").is_dir()
    operations = tmp_path / "docs/agents/issue-tracker.md"
    assert operations.is_file()
    content = operations.read_text(encoding="utf-8")
    assert "planning/wayfinder" in content and ".scratch" not in content
    assert "map.md" in content and "issues/" in content
    assert not list((tmp_path / "planning/wayfinder").iterdir()), "Preparation must not create maps or tickets"
    checked = run_setup(tmp_path, "--check")
    assert checked.returncode == 0, checked.stderr


def test_local_provider_only_backfills_its_missing_directory(tmp_path):
    write_config(tmp_path, {"provider": "local"})
    result = run_config(tmp_path, "--update")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["wayfinder-tracker"] == LOCAL


@pytest.mark.parametrize("tracker", [
    None, False, "local", [], {}, {"directory": "planning"},
    {"provider": "unknown"}, {"provider": 1},
    {"provider": "local", "directory": None},
    {"provider": "local", "directory": "plans", "repository": "Acme/Repo"},
    {"provider": "github"}, {"provider": "github", "repository": ""},
    {"provider": "github", "repository": "Acme/Repo", "directory": ".scratch"},
    {"provider": "github", "repository": "https://github.com/Acme/Repo"},
    {"provider": "github", "repository": "evil.test/Acme/Repo"},
    {"provider": "github", "repository": "Acme/Repo;echo-secret"},
    {"provider": "gitlab"}, {"provider": "gitlab", "project": "group/repo"},
    {"provider": "gitlab", "project": "http://gitlab.test/group/repo"},
    {"provider": "gitlab", "project": "https://user:password@gitlab.test/group/repo"},
    {"provider": "gitlab", "project": "https://gitlab.test/group/repo?token=secret"},
    {"provider": "gitlab", "project": "https://gitlab.test/group/repo#fragment"},
    {"provider": "gitlab", "project": "https://gitlab.test/group/../repo"},
    {"provider": "gitlab", "project": "https://gitlab.test/group/repo", "repository": "Acme/Repo"},
])
def test_invalid_tracker_variants_fail_closed_and_preserve_configuration(tmp_path, tracker):
    path = write_config(tmp_path, tracker)
    original = path.read_bytes()
    for arguments in ((), ("--update",)):
        result = run_config(tmp_path, *arguments)
        assert result.returncode != 0, tracker
        assert result.stderr.strip() and not result.stdout.strip()
        assert path.read_bytes() == original
        assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("directory", [
    "", ".", "./planning", "..", "../outside", "planning/../outside", "/planning",
    "C:/planning", "C:planning", "\\\\server\\share", ".git/wayfinder", ".codegraph/wayfinder",
])
def test_unsafe_local_directory_is_rejected_without_writes(tmp_path, directory):
    path = write_config(tmp_path, {"provider": "local", "directory": directory})
    original = path.read_bytes()
    result = run_setup(tmp_path, "--prepare")
    assert result.returncode != 0, directory
    assert result.stderr.strip() and not result.stdout.strip()
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("content", [
    '{"wayfinder-tracker":{"provider":"local","provider":"github"}}',
    '{"wayfinder-tracker":{"provider":"github","repository":"Acme/One","repository":"Acme/Two"}}',
    '{"wayfinder-tracker":{"provider":"local"},"wayfinder-tracker":{"provider":"github","repository":"Acme/Repo"}}',
])
def test_duplicate_tracker_fields_are_not_overwritten_by_backfill(tmp_path, content):
    path = tmp_path / "kiss-chris-stack.config.json"
    path.write_text(content, encoding="utf-8")
    result = run_config(tmp_path, "--update")
    assert result.returncode != 0
    assert "duplicate" in result.stderr.lower() and not result.stdout.strip()
    assert path.read_text(encoding="utf-8") == content


def test_check_is_read_only_and_fails_before_preparation(tmp_path):
    path = write_config(tmp_path, LOCAL)
    original = path.read_bytes()
    for arguments in ((), ("--check",)):
        result = run_setup(tmp_path, *arguments)
        assert result.returncode != 0
        assert result.stderr.strip() and not result.stdout.strip()
        assert list(tmp_path.iterdir()) == [path] and path.read_bytes() == original


def test_pending_config_prepares_before_marker_and_is_unchanged_by_recheck(tmp_path):
    pending = {"wayfinder-tracker": {"provider": "local", "directory": "planning"}, "wayfinder": False}
    prepared = run_setup(tmp_path, "--prepare", "--config-stdin", configuration=pending)
    assert prepared.returncode == 0, prepared.stderr
    assert not (tmp_path / "kiss-chris-stack.config.json").exists()
    operations = tmp_path / "docs/agents/issue-tracker.md"
    snapshot = (operations.read_bytes(), operations.stat().st_mtime_ns)
    for arguments in (("--config-stdin",), ("--prepare", "--config-stdin")):
        result = run_setup(tmp_path, *arguments, configuration=pending)
        assert result.returncode == 0, result.stderr
        report = json.loads(result.stdout)
        assert report["ready"] is True and report["changed"] == []
        assert report["configuration"]["wayfinder-tracker"] == pending["wayfinder-tracker"]
        assert (operations.read_bytes(), operations.stat().st_mtime_ns) == snapshot
    assert not (tmp_path / "kiss-chris-stack.config.json").exists()


@pytest.mark.parametrize("content", [
    "# My existing tracker\nPreserve these instructions.\n",
    BEGIN + "\nunterminated\n",
    END + "\nreversed\n" + BEGIN,
    BEGIN + "\none\n" + END + "\n" + BEGIN + "\ntwo\n" + END,
])
def test_conflicting_operations_document_blocks_before_creating_tracker_root(tmp_path, content):
    config = write_config(tmp_path, {"provider": "local", "directory": "new-root"})
    operations = tmp_path / "docs/agents/issue-tracker.md"
    operations.parent.mkdir(parents=True)
    original = content.encode()
    operations.write_bytes(original)
    config_original = config.read_bytes()
    result = run_setup(tmp_path, "--prepare")
    assert result.returncode != 0
    assert result.stderr.strip() and not result.stdout.strip()
    assert operations.read_bytes() == original and config.read_bytes() == config_original
    assert not (tmp_path / "new-root").exists(), "Validate the document conflict before any preparation writes"


def test_prepare_reconciles_only_managed_binding_and_preserves_old_tickets(tmp_path):
    write_config(tmp_path, {"provider": "local", "directory": "old-plans"})
    initial = run_setup(tmp_path, "--prepare")
    assert initial.returncode == 0, initial.stderr
    operations = tmp_path / "docs/agents/issue-tracker.md"
    prefix, suffix = b"# User header\r\nKeep this.\r\n", b"\r\n# User footer\r\nKeep that.\r\n"
    operations.write_bytes(prefix + operations.read_bytes() + suffix)
    ticket = tmp_path / "old-plans/effort/issues/01-existing.md"
    ticket.parent.mkdir(parents=True)
    ticket.write_bytes(b"Status: blocked\nUser-owned ticket data.\n")
    original_ticket = ticket.read_bytes()
    config = write_config(tmp_path, {"provider": "local", "directory": "new-plans"})
    original_config = config.read_bytes()
    stale = run_setup(tmp_path, "--check")
    assert stale.returncode != 0, "A stale operations target must not appear integrated"
    prepared = run_setup(tmp_path, "--prepare")
    assert prepared.returncode == 0, prepared.stderr
    content = operations.read_bytes()
    assert content.startswith(prefix) and content.endswith(suffix)
    assert b"new-plans" in content and b"old-plans" not in content
    assert ticket.read_bytes() == original_ticket and config.read_bytes() == original_config
    snapshot = (content, operations.stat().st_mtime_ns)
    repeated = run_setup(tmp_path, "--prepare")
    assert repeated.returncode == 0, repeated.stderr
    assert json.loads(repeated.stdout)["changed"] == []
    assert (operations.read_bytes(), operations.stat().st_mtime_ns) == snapshot


@pytest.mark.parametrize("obstruction", ["tracker-file", "docs-file", "operations-directory"])
def test_path_obstructions_fail_without_partial_preparation(tmp_path, obstruction):
    write_config(tmp_path, {"provider": "local", "directory": "planning"})
    if obstruction == "tracker-file":
        (tmp_path / "planning").write_bytes(b"Existing user file")
    elif obstruction == "docs-file":
        (tmp_path / "docs").write_bytes(b"Existing user file")
    else:
        (tmp_path / "docs/agents/issue-tracker.md").mkdir(parents=True)
    before = {path.relative_to(tmp_path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    result = run_setup(tmp_path, "--prepare")
    assert result.returncode != 0
    assert result.stderr.strip() and not result.stdout.strip()
    after = {path.relative_to(tmp_path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    assert after == before
    if obstruction != "tracker-file":
        assert not (tmp_path / "planning").exists()


def make_directory_link(link, target):
    if os.name == "nt":
        powershell = shutil.which("powershell")
        if not powershell:
            pytest.skip("PowerShell is unavailable for the Windows junction fixture")
        result = subprocess.run(
            [powershell, "-NoProfile", "-NonInteractive", "-Command",
             "$ErrorActionPreference = 'Stop'; New-Item -ItemType Junction -Path $env:KISS_TEST_LINK -Target $env:KISS_TEST_TARGET | Out-Null"],
            env={**os.environ, "KISS_TEST_LINK": str(link), "KISS_TEST_TARGET": str(target)},
            text=True, capture_output=True, timeout=15,
        )
        if result.returncode:
            pytest.skip("Host cannot create a junction fixture: " + result.stderr)
    else:
        link.symlink_to(target, target_is_directory=True)


@pytest.mark.parametrize("linked_path", ["tracker", "tracker-ancestor", "docs"])
def test_prepare_rejects_symlink_or_junction_ancestors_before_any_writes(tmp_path, linked_path):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "user-data.md"
    sentinel.write_bytes(b"Existing external data")
    if linked_path == "docs":
        link = project / "docs"
        tracker = {"provider": "local", "directory": "planning"}
    else:
        link = project / "planning"
        tracker = {"provider": "local", "directory": "planning" if linked_path == "tracker" else "planning/nested"}
    make_directory_link(link, outside)
    try:
        config = write_config(project, tracker)
        original = config.read_bytes()
        result = run_setup(project, "--prepare")
        assert result.returncode != 0
        assert result.stderr.strip() and not result.stdout.strip()
        assert config.read_bytes() == original
        assert list(outside.iterdir()) == [sentinel] and sentinel.read_bytes() == b"Existing external data"
        if linked_path == "docs":
            assert not (project / "planning").exists()
        else:
            assert not (project / "docs").exists()
    finally:
        if os.name == "nt":
            link.rmdir()
        else:
            link.unlink()


@pytest.mark.parametrize("raw", ["{broken", '{"wayfinder-tracker":{"provider":"local","provider":"github"}}'])
def test_pending_config_uses_strict_parser_and_never_initializes_on_error(tmp_path, raw):
    result = subprocess.run(
        [sys.executable, str(SETUP), "--project", str(tmp_path), "--prepare", "--config-stdin"],
        input=raw, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0
    assert result.stderr.strip() and not result.stdout.strip()
    assert list(tmp_path.iterdir()) == []


@pytest.fixture
def setup_module(monkeypatch):
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    spec = importlib.util.spec_from_file_location("wayfinder_setup_under_test", SETUP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoke_setup_main(module, project, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [str(SETUP), "--project", str(project), "--prepare"])
    try:
        module.main()
        code = 0
    except SystemExit as error:
        code = error.code
    captured = capsys.readouterr()
    return code, captured


@pytest.mark.parametrize("tracker", [
    {"provider": "github", "repository": "Acme/Stack"},
    {"provider": "gitlab", "project": "https://gitlab.example.test/group/nested/stack"},
])
def test_missing_external_cli_never_creates_local_fallback_or_binding(setup_module, tmp_path, monkeypatch, capsys, tracker):
    path = write_config(tmp_path, tracker)
    original = path.read_bytes()
    monkeypatch.setattr(shutil, "which", lambda command: None)
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code != 0
    assert captured.err.strip() and not captured.out.strip()
    assert list(tmp_path.iterdir()) == [path] and path.read_bytes() == original


GITHUB_REPO = {
    "nameWithOwner": "Acme/Stack", "url": "https://github.com/Acme/Stack",
    "isArchived": False, "hasIssuesEnabled": True, "viewerPermission": "TRIAGE",
}
GITLAB_PROJECT = {
    "path_with_namespace": "group/nested/stack", "web_url": "https://gitlab.example.test/group/nested/stack",
    "archived": False, "issues_access_level": "enabled", "issues_enabled": True,
    "permissions": {"project_access": {"access_level": 40}, "group_access": None},
}


def stub_remote(monkeypatch, response, *, code=0):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda command: command if command in ("gh", "glab") else None)

    def run(arguments, **kwargs):
        assert isinstance(arguments, list), "Use argument arrays instead of a shell command"
        assert kwargs.get("shell") is not True
        calls.append((arguments, {"shell": kwargs.get("shell"), "timeout": kwargs.get("timeout")}))
        return subprocess.CompletedProcess(arguments, code, json.dumps(response), "Not authenticated" if code else "")

    monkeypatch.setattr(subprocess, "run", run)
    return calls


@pytest.mark.parametrize("tracker,response,expected", [
    ({"provider": "github", "repository": "Acme/Stack"}, GITHUB_REPO,
     ["gh", "repo", "view", "github.com/Acme/Stack"]),
    ({"provider": "gitlab", "project": "https://gitlab.example.test/group/nested/stack"}, GITLAB_PROJECT,
     ["glab", "api", "--hostname", "gitlab.example.test", "projects/group%2Fnested%2Fstack"]),
])
def test_external_prepare_only_reads_exact_configured_target_and_binds_operations(setup_module, tmp_path, monkeypatch, capsys, tracker, response, expected):
    path = write_config(tmp_path, tracker)
    original = path.read_bytes()
    calls = stub_remote(monkeypatch, response)
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code == 0, captured.err
    assert calls
    arguments = calls[0][0]
    if tracker["provider"] == "github":
        assert arguments[:4] == expected
        assert "--json" in arguments
        fields = arguments[arguments.index("--json") + 1].split(",")
        assert set(fields) >= {"nameWithOwner", "url", "isArchived", "hasIssuesEnabled", "viewerPermission"}
    else:
        assert arguments == expected
    assert len(calls) == 1, "Preparation must not create, modify or publish remote artifacts"
    report = json.loads(captured.out)
    assert report["ready"] is True
    assert report["configuration"]["wayfinder-tracker"] == tracker
    content = (tmp_path / "docs/agents/issue-tracker.md").read_text(encoding="utf-8")
    target = "github.com/Acme/Stack" if tracker["provider"] == "github" else tracker["project"]
    assert target in content and "--repo" in content
    assert "Infer the repo from" not in content
    assert not (tmp_path / ".scratch").exists() and path.read_bytes() == original


@pytest.mark.parametrize("provider,patch", [
    ("github", {"nameWithOwner": "Other/Repo"}),
    ("github", {"url": "https://evil.test/Acme/Stack"}),
    ("github", {"isArchived": True}),
    ("github", {"hasIssuesEnabled": False}),
    ("github", {"viewerPermission": "READ"}),
    ("gitlab", {"path_with_namespace": "other/project"}),
    ("gitlab", {"web_url": "https://evil.test/group/nested/stack"}),
    ("gitlab", {"archived": True}),
    ("gitlab", {"issues_access_level": "disabled"}),
    ("gitlab", {"permissions": {}}),
    ("gitlab", {"permissions": {"project_access": {"access_level": 20}, "group_access": None}}),
])
def test_unusable_remote_targets_fail_before_binding_and_without_local_fallback(setup_module, tmp_path, monkeypatch, capsys, provider, patch):
    tracker = {"provider": "github", "repository": "Acme/Stack"} if provider == "github" else {"provider": "gitlab", "project": GITLAB_PROJECT["web_url"]}
    path = write_config(tmp_path, tracker)
    original = path.read_bytes()
    response = {**(GITHUB_REPO if provider == "github" else GITLAB_PROJECT), **patch}
    calls = stub_remote(monkeypatch, response)
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code != 0, response
    assert calls and captured.err.strip() and not captured.out.strip()
    assert list(tmp_path.iterdir()) == [path] and path.read_bytes() == original


@pytest.mark.parametrize("provider", ["github", "gitlab"])
def test_remote_auth_or_access_failure_is_visible_without_writes(setup_module, tmp_path, monkeypatch, capsys, provider):
    tracker = {"provider": "github", "repository": "Acme/Stack"} if provider == "github" else {"provider": "gitlab", "project": GITLAB_PROJECT["web_url"]}
    path = write_config(tmp_path, tracker)
    calls = stub_remote(monkeypatch, {}, code=1)
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code != 0 and calls
    assert captured.err.strip() and not captured.out.strip()
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("response", [
    {**GITLAB_PROJECT, "issues_access_level": "private", "permissions": {"project_access": None, "group_access": {"access_level": 30}}},
    {key: value for key, value in GITLAB_PROJECT.items() if key != "issues_access_level"},
])
def test_gitlab_effective_group_access_and_legacy_issues_flag_are_supported(setup_module, tmp_path, monkeypatch, capsys, response):
    write_config(tmp_path, {"provider": "gitlab", "project": GITLAB_PROJECT["web_url"]})
    calls = stub_remote(monkeypatch, response)
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code == 0, captured.err
    assert len(calls) == 1 and json.loads(captured.out)["ready"] is True


def test_setup_and_wayfinder_require_the_configured_binding_and_usable_target():
    setup = (ROOT / "skills/setup/SKILL.md").read_text(encoding="utf-8").lower()
    wayfinder = (ROOT / "skills/wayfinder/SKILL.md").read_text(encoding="utf-8").lower()
    for content in (setup, wayfinder):
        assert "wayfinder-tracker" in content
        assert "setup-wayfinder.py" in content
        assert "docs/agents/issue-tracker.md" in content
        assert "--check" in content
    assert "--prepare" in setup and "--config-stdin" in setup
    assert "pending" in setup and ("exclusive" in setup or "never overwrite" in setup)
    assert "evaluation-config.py" in wayfinder
    assert "target" in wayfinder and ("mismatch" in wayfinder or "matching" in wayfinder)
    assert "block" in wayfinder and "fallback" in wayfinder


def test_setup_explicitly_asks_storage_choice_before_dependent_writes():
    setup = (ROOT / "skills/setup/SKILL.md").read_text(encoding="utf-8").lower()
    tracker_setup = (ROOT / "skills/setup-matt-pocock-skills/SKILL.md").read_text(encoding="utf-8").lower()
    for content in (setup, tracker_setup):
        assert "must ask" in content and "storage choice" in content
        assert "first-time initialization" in content and "explicit `/setup`" in content
        assert "current provider/location" in content
        assert "wait for" in content and "user answer" in content
        assert "before dependent" in content and "writes" in content
        assert "same setup dialogue" in content
        assert "ordinary per-task readiness" in content and "without another prompt" in content
    assert setup.index("## required storage choice") < setup.index("## runtime readiness")
    assert "defaults are not consent" in setup
    assert "explicit invocation of this tracker setup skill" in tracker_setup


@pytest.mark.parametrize("existing,pending", [
    ({"wayfinder-tracker": {"provider": "local", "directory": "existing-plans"}},
     {"wayfinder-tracker": {"provider": "local", "directory": "pending-plans"}}),
    ({"plan-mode": True}, {"plan-mode": False}),
])
def test_pending_settings_cannot_override_existing_marker(tmp_path, existing, pending):
    path = tmp_path / "kiss-chris-stack.config.json"
    original = json.dumps(existing).encode()
    path.write_bytes(original)
    result = run_setup(tmp_path, "--prepare", "--config-stdin", configuration=pending)
    assert result.returncode != 0
    assert result.stderr.strip() and not result.stdout.strip()
    assert path.read_bytes() == original and list(tmp_path.iterdir()) == [path]


def test_matching_existing_marker_and_pending_config_can_be_prepared(tmp_path):
    pending = {"wayfinder-tracker": {"provider": "local", "directory": "planning"}}
    marker = write_config(tmp_path, pending["wayfinder-tracker"])
    original = marker.read_bytes()
    result = run_setup(tmp_path, "--prepare", "--config-stdin", configuration=pending)
    assert result.returncode == 0, result.stderr
    assert marker.read_bytes() == original
    assert (tmp_path / "planning").is_dir()


def test_marker_appearing_during_remote_preflight_blocks_pending_binding(setup_module, tmp_path, monkeypatch, capsys):
    pending = {"wayfinder-tracker": {"provider": "github", "repository": "Acme/Stack"}}
    marker = tmp_path / "kiss-chris-stack.config.json"
    concurrent = b'{"wayfinder-tracker":{"provider":"local","directory":"other-plans"}}'
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(pending)))
    monkeypatch.setattr(shutil, "which", lambda command: command)

    def remote_read(arguments, **kwargs):
        marker.write_bytes(concurrent)
        return subprocess.CompletedProcess(arguments, 0, json.dumps(GITHUB_REPO), "")

    monkeypatch.setattr(subprocess, "run", remote_read)
    monkeypatch.setattr(sys, "argv", [str(SETUP), "--project", str(tmp_path), "--prepare", "--config-stdin"])
    with pytest.raises(SystemExit) as error:
        setup_module.main()
    assert error.value.code != 0
    captured = capsys.readouterr()
    assert captured.err.strip() and not captured.out.strip()
    assert marker.read_bytes() == concurrent and list(tmp_path.iterdir()) == [marker]


UNSAFE_GITLAB_AUTHORITIES = (
    "gitlab;echo_BAD", "gitlab`echo_BAD`", "gitlab$(echo_BAD)", "gitlab bad",
    "gitlab'bad", 'gitlab"bad', "gitlab\\bad", "gitlab%3Bbad",
    "gitlab.example.test:", "gitlab.example.test:bad", "gitlab.example.test:0", "gitlab.example.test:65536",
)


@pytest.mark.parametrize("authority", UNSAFE_GITLAB_AUTHORITIES)
def test_gitlab_authority_validation_rejects_unsafe_hosts_and_ports_without_updating(tmp_path, authority):
    path = write_config(tmp_path, {"provider": "gitlab", "project": f"https://{authority}/group/project"})
    original = path.read_bytes()
    result = run_config(tmp_path, "--update")
    assert result.returncode != 0, "Unsafe authority was accepted: " + authority
    assert result.stderr.strip() and not result.stdout.strip()
    assert path.read_bytes() == original and list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("authority", UNSAFE_GITLAB_AUTHORITIES)
def test_gitlab_authority_validation_precedes_remote_calls_and_binding_writes(setup_module, tmp_path, monkeypatch, capsys, authority):
    path = write_config(tmp_path, {"provider": "gitlab", "project": f"https://{authority}/group/project"})
    original = path.read_bytes()
    monkeypatch.setattr(shutil, "which", lambda command: command)

    def forbidden_remote_call(*arguments, **kwargs):
        pytest.fail("Unsafe configured authority reached remote preflight before validation")

    monkeypatch.setattr(subprocess, "run", forbidden_remote_call)
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code != 0
    assert captured.err.strip() and not captured.out.strip()
    assert path.read_bytes() == original and list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("authority", [
    "gitlab.example.test", "localhost", "127.0.0.1", "gitlab.example.test:8443", "127.0.0.1:443",
    "[::1]", "[2001:db8::1]:8443",
])
def test_gitlab_authority_validation_preserves_valid_dns_ip_and_ports(tmp_path, authority):
    tracker = {"provider": "gitlab", "project": f"https://{authority}/group/project"}
    path = write_config(tmp_path, tracker)
    original = path.read_bytes()
    result = run_config(tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["wayfinder-tracker"] == tracker
    assert path.read_bytes() == original


@pytest.mark.parametrize("permissions", [
    {"unrelated_access": {"access_level": 40}},
    {"project_access": {"access_level": 0}, "group_access": {"access_level": 0}, "unrelated_access": {"access_level": 40}},
    {"project_access": {"access_level": "40"}},
    {"project_access": {"access_level": 40.0}},
])
def test_gitlab_permission_proof_uses_only_documented_strict_integer_roles(setup_module, tmp_path, monkeypatch, capsys, permissions):
    path = write_config(tmp_path, {"provider": "gitlab", "project": GITLAB_PROJECT["web_url"]})
    original = path.read_bytes()
    calls = stub_remote(monkeypatch, {**GITLAB_PROJECT, "permissions": permissions})
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code != 0, "Unproven GitLab role was accepted: " + repr(permissions)
    assert calls and captured.err.strip() and not captured.out.strip()
    assert path.read_bytes() == original and list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("metadata_patch", [
    {"path_with_namespace": "team/project"},
    {"web_url": "https://gitlab.example.test/team/project"},
])
def test_gitlab_target_proof_preserves_exact_configured_project_path_case(setup_module, tmp_path, monkeypatch, capsys, metadata_patch):
    configured = "https://gitlab.example.test/Team/Project"
    path = write_config(tmp_path, {"provider": "gitlab", "project": configured})
    original = path.read_bytes()
    response = {**GITLAB_PROJECT, "path_with_namespace": "Team/Project", "web_url": configured, **metadata_patch}
    calls = stub_remote(monkeypatch, response)
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code != 0, "A differently cased project path was accepted as the configured target"
    assert calls and captured.err.strip() and not captured.out.strip()
    assert path.read_bytes() == original and list(tmp_path.iterdir()) == [path]


def test_gitlab_target_proof_normalizes_host_case_without_normalizing_project_path(setup_module, tmp_path, monkeypatch, capsys):
    configured = "https://gitlab.example.test/Team/Project"
    path = write_config(tmp_path, {"provider": "gitlab", "project": configured})
    original = path.read_bytes()
    response = {**GITLAB_PROJECT, "path_with_namespace": "Team/Project", "web_url": "https://GITLAB.EXAMPLE.TEST/Team/Project"}
    calls = stub_remote(monkeypatch, response)
    code, captured = invoke_setup_main(setup_module, tmp_path, monkeypatch, capsys)
    assert code == 0, captured.err
    assert calls and json.loads(captured.out)["ready"] is True
    assert path.read_bytes() == original
    content = (tmp_path / "docs/agents/issue-tracker.md").read_text(encoding="utf-8")
    assert configured in content


@pytest.mark.parametrize("pending_tracker,response", [
    ({"provider": "github", "repository": "Acme/Stack"}, GITHUB_REPO),
    ({"provider": "gitlab", "project": GITLAB_PROJECT["web_url"]}, GITLAB_PROJECT),
])
def test_existing_marker_authority_is_checked_before_pending_remote_preflight(setup_module, tmp_path, monkeypatch, capsys, pending_tracker, response):
    marker = write_config(tmp_path, {"provider": "local", "directory": "existing-plans"})
    original = marker.read_bytes()
    pending = {"wayfinder-tracker": pending_tracker}
    calls = stub_remote(monkeypatch, response)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(pending)))
    monkeypatch.setattr(sys, "argv", [str(SETUP), "--project", str(tmp_path), "--prepare", "--config-stdin"])
    with pytest.raises(SystemExit) as error:
        setup_module.main()
    assert error.value.code != 0
    captured = capsys.readouterr()
    assert captured.err.strip() and not captured.out.strip()
    assert not calls, "Conflicting pending settings must not contact a remote target before rejecting the existing marker mismatch"
    assert marker.read_bytes() == original and list(tmp_path.iterdir()) == [marker]


@pytest.mark.parametrize("directory", [
    "kiss-chris-stack.config.json", "kiss-chris-stack.config.json/plans",
    "AGENTS.md", "AGENTS.md/plans",
    "docs/agents/issue-tracker.md", "docs/agents/issue-tracker.md/plans",
])
def test_first_init_tracker_root_cannot_collide_with_setup_owned_file_outputs(tmp_path, directory):
    pending = {"wayfinder-tracker": {"provider": "local", "directory": directory}}
    result = run_setup(tmp_path, "--prepare", "--config-stdin", configuration=pending)
    assert result.returncode != 0, "Tracker directory collided with a later setup file output: " + directory
    assert result.stderr.strip() and not result.stdout.strip()
    assert list(tmp_path.iterdir()) == [], "Reject known file-output collisions before creating any directory, binding or marker"


@pytest.mark.parametrize("directory", ["docs/agents", "planning/AGENTS.md"])
def test_first_init_tracker_root_allows_ancestors_and_unrelated_markdown_directory_names(tmp_path, directory):
    pending = {"wayfinder-tracker": {"provider": "local", "directory": directory}}
    result = run_setup(tmp_path, "--prepare", "--config-stdin", configuration=pending)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / directory).is_dir()
    assert (tmp_path / "docs/agents/issue-tracker.md").is_file()
    assert not (tmp_path / "kiss-chris-stack.config.json").exists()
    checked = run_setup(tmp_path, "--config-stdin", configuration=pending)
    assert checked.returncode == 0, checked.stderr


def test_rendered_gitlab_ipv6_commands_quote_and_preserve_explicit_targets(setup_module):
    target, host = "https://[::1]:8443/group/project", "[::1]:8443"
    content = setup_module.render_operations({"provider": "gitlab", "project": target})
    commands = re.findall(r"`(glab [^`\n]+)`", content)
    issues = [command for command in commands if command.startswith("glab issue ")]
    apis = [command for command in commands if command.startswith("glab api ")]
    assert issues and apis
    for command, flag, expected in [(command, "--repo", target) for command in issues] + [(command, "--hostname", host) for command in apis]:
        arguments = shlex.split(command)
        assert arguments[arguments.index(flag) + 1] == expected
        assert re.search(re.escape(flag) + r"\s+(['\"])" + re.escape(expected) + r"\1", command), "Quote IPv6 brackets so shell glob expansion cannot alter the configured target"
