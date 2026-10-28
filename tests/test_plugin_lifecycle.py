import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
EVENTS = ("SessionStart", "UserPromptSubmit", "SubagentStart")


def test_plugin_marketplace_resolves_to_the_bundled_plugin():
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "kiss-chris-stack"
    assert manifest == {"name": "kiss-chris-stack"}, "Root identity must not shadow the native Codex hook manifest"
    native = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert native["name"] == manifest["name"]
    assert (ROOT / native["skills"]).is_dir()
    assert (ROOT / native["hooks"]).is_file()
    extension = native["extensions"]["com.openai"]
    assert (ROOT / extension["onboardingSkill"]).is_file()
    catalog_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries = [item for item in catalog["plugins"] if item["name"] == manifest["name"]]
    assert len(entries) == 1
    source = entries[0]["source"]
    local = source["path"] if isinstance(source, dict) else source
    assert isinstance(local, str) and not local.startswith(("http:", "https:", "git@"))
    candidates = (ROOT / local, catalog_path.parent / local)
    assert any((p.resolve() / "plugin.json").is_file() for p in candidates), "Marketplace must reference this packaged plugin"


def test_plugin_contains_real_skills_and_uiux_resources():
    for name in ("kiss-chris-stack", "setup", "ponytail", "caveman", "ui-ux-pro-max"):
        path = ROOT / "skills" / name / "SKILL.md"
        assert path.is_file(), f"Bundled skill missing: {name}"
        assert len(path.read_text(encoding="utf-8").splitlines()) > 5
    uiux = ROOT / "skills" / "ui-ux-pro-max"
    assert any(p.is_file() for p in (uiux / "data").rglob("*.csv")), "Bundle UIUX search data"
    assert any(p.is_file() for p in (uiux / "scripts").rglob("*.py")), "Bundle UIUX search implementation"
    assert len(list((ROOT / "skills").glob("ponytail*/SKILL.md"))) > 1, "Bundle Ponytail companion skills"
    assert not (ROOT / "scripts" / "install-stack.ps1").exists()
    assert not (ROOT / "scripts" / "install-stack.sh").exists()


def _commands(config, event):
    return [hook["command"] for group in config["hooks"].get(event, []) for hook in group.get("hooks", []) if hook.get("type") == "command"]


def test_each_lifecycle_event_runs_stack_and_ponytail_hooks():
    native = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / native["hooks"]).read_text(encoding="utf-8"))
    for event in EVENTS:
        commands = _commands(config, event)
        assert any("stack.js" in command for command in commands), f"Missing stack hook for {event}"
        assert any("ponytail" in command.lower() and "stack.js" not in command for command in commands), f"Missing upstream Ponytail hook for {event}"
        for command in commands:
            assert "dangerously" not in command and "skip-trust" not in command


@pytest.fixture
def isolated_plugin(tmp_path):
    target = tmp_path / "plugin with spaces"
    target.mkdir()
    for directory in ("hooks", "assets", "skills", "scripts", "references"):
        source = ROOT / directory
        if source.exists():
            shutil.copytree(source, target / directory)
    project = tmp_path / "project with spaces"
    project.mkdir()
    profile = tmp_path / "isolated profile"
    profile.mkdir()
    env = os.environ.copy()
    env.update(HOME=str(profile), USERPROFILE=str(profile), CODEX_HOME=str(profile / ".codex"), CODEX_PLUGIN_ROOT=str(target))
    return target, project, profile, env


def _hook(fixture, payload):
    plugin, project, _, env = fixture
    assert (plugin / "hooks" / "stack.js").is_file(), "Lifecycle adapter missing"
    result = subprocess.run(
        [shutil.which("node") or "node", str(plugin / "hooks" / "stack.js")],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        text=True, capture_output=True, cwd=project, env=env, timeout=15,
    )
    return result


@pytest.mark.parametrize("event", EVENTS)
def test_hook_process_routes_root_and_subagent_context(isolated_plugin, event):
    _, project, profile, _ = isolated_plugin
    prompt = "Implementiere die Bestellung; Behalte diesen Originalauftrag."
    payload = {"hook_event_name": event, "cwd": str(project), "prompt": prompt, "agent_type": "test-author"}
    result = _hook(isolated_plugin, payload)
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == event
    context = output["additionalContext"]
    assert isinstance(context, str) and context.strip()
    if event == "SubagentStart":
        assert "test-author" in context
        assert "goal" in context.lower()
    else:
        assert "/setup" in context
        assert "ready" in context.lower() or "readiness" in context.lower()
        if event == "UserPromptSubmit":
            assert prompt in context, "Keep original request available after setup instructions"
            assert context.index("/setup") < context.index(prompt)
        again = _hook(isolated_plugin, payload)
        assert again.returncode == 0
        assert "/setup" in json.loads(again.stdout)["hookSpecificOutput"]["additionalContext"], "Recheck each root event, never cache approval"
    assert list(profile.iterdir()) == [], "Lifecycle hook must not install or mutate the host profile"
    assert list(project.iterdir()) == [], "Lifecycle hook injects workflow; setup owns project writes"


@pytest.mark.parametrize("payload", ["{broken", {}, {"hook_event_name": "Unknown", "cwd": "."}, {"hook_event_name": "SessionStart"}])
def test_hook_rejects_invalid_events(isolated_plugin, payload):
    result = _hook(isolated_plugin, payload)
    assert result.returncode != 0
    assert result.stderr.strip(), "Invalid events need actionable diagnostics"
    assert not result.stdout.strip(), "Invalid events must not emit a successful workflow context"


def test_runtime_check_blocks_missing_runtime_without_mutation(isolated_plugin):
    plugin, project, profile, env = isolated_plugin
    env["PATH"] = ""
    result = subprocess.run(
        [sys.executable, str(plugin / "scripts" / "setup-runtime.py"), "--project", str(project)],
        env=env, cwd=project, text=True, capture_output=True, timeout=30,
    )
    assert result.returncode != 0, "Missing runtime must block readiness"
    report = json.loads(result.stdout)
    assert report["ready"] is False
    assert isinstance(report["checks"], list)
    assert report["errors"], "Readiness failure needs actionable errors"
    assert list(profile.iterdir()) == []
    assert list(project.iterdir()) == []


def test_bundled_resources_match_their_provenance_hashes():
    manifest = json.loads((ROOT / "assets" / "bundle-manifest.json").read_text(encoding="utf-8"))
    files = manifest["sha256"]
    assert files
    data = list((ROOT / "skills" / "ui-ux-pro-max" / "data").rglob("*.csv"))
    assert data and all(path.relative_to(ROOT).as_posix() in files for path in data)
    for relative, digest in files.items():
        path = (ROOT / relative).resolve()
        assert path.is_relative_to(ROOT.resolve()), "Bundle paths must stay within the plugin"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, relative


@pytest.fixture
def runtime_module(monkeypatch):
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    spec = importlib.util.spec_from_file_location("setup_runtime_under_test", ROOT / "scripts" / "setup-runtime.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("layout", ["reversed", "duplicated", "nested", "unterminated"])
@pytest.mark.parametrize("operation", ["check", "update"])
def test_runtime_policy_rejects_ambiguous_markers_without_writing(tmp_path, runtime_module, layout, operation):
    module = runtime_module
    block = f"{module.BEGIN}\n{module.POLICY}\n{module.END}"
    layouts = {
        "reversed": f"{module.END}\nforeign\n{module.BEGIN}\n{module.POLICY}",
        "duplicated": block + "\nforeign\n" + block,
        "nested": f"{module.BEGIN}\nforeign\n{module.BEGIN}\n{module.POLICY}\n{module.END}\n{module.END}",
        "unterminated": f"{module.BEGIN}\n{module.POLICY}\nforeign",
    }
    target = tmp_path / "AGENTS.md"
    target.write_text(layouts[layout], encoding="utf-8", newline="\n")
    before = target.read_bytes()
    if operation == "check":
        try:
            current = module.policy_current(target)
        except RuntimeError:
            current = False
        assert current is False, "Malformed marker order must never satisfy readiness"
    else:
        with pytest.raises(RuntimeError):
            module.update_policy(target)
    assert target.read_bytes() == before, "Reject ambiguity without rewriting foreign content"


def test_runtime_policy_update_preserves_foreign_bytes_and_is_idempotent(tmp_path, runtime_module):
    module = runtime_module
    target = tmp_path / "AGENTS.override.md"
    prefix, suffix = b"# foreign header\r\nkeep = true\r\n", b"\r\n# foreign footer\r\nkeep = true\r\n"
    target.write_bytes(prefix + f"{module.BEGIN}\r\nstale\r\n{module.END}".encode() + suffix)
    assert module.policy_current(target) is False
    module.update_policy(target)
    first = target.read_bytes()
    assert first.startswith(prefix) and first.endswith(suffix)
    assert module.policy_current(target) is True
    module.update_policy(target)
    assert target.read_bytes() == first
