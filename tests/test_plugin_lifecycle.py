import hashlib
import importlib.util
import json
import os
import re
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


def test_installation_onboarding_asks_before_setup_and_requires_a_project_path():
    native = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    entry = (ROOT / native["extensions"]["com.openai"]["onboardingSkill"]).resolve()
    assert entry != (ROOT / "skills/setup/SKILL.md").resolve(), "Installing a plugin must open a consent dialog, not setup"
    text = entry.read_text(encoding="utf-8").lower()
    for term in ("ask", "project", "yes", "no", "path", "existing", "wait", "/setup", "hook"):
        assert term in text, f"Onboarding must cover {term}"
    assert "do not" in text and ("declin" in text or "cancel" in text)
    assert "cwd" in text, "Do not infer a target project from the installation working directory"
    assert "before" in text and "lifecycle" in text, "Installation dialogue must precede automatic project setup/readiness"


def _root_context(fixture, event="UserPromptSubmit"):
    result = _hook(fixture, {"hook_event_name": event, "cwd": str(fixture[1]), "prompt": "Keep this request unchanged"})
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


@pytest.mark.parametrize("event", ["SessionStart", "UserPromptSubmit"])
def test_configured_hook_requests_bundled_config_backfill_before_readiness(isolated_plugin, event):
    plugin, project, profile, _ = isolated_plugin
    path = project / "kiss-chris-stack.config.json"
    original = b'{"evaluation":{"live":{"enabled":false}}}'
    path.write_bytes(original)
    context = _root_context(isolated_plugin, event)
    prefix = "Configuration update command (argv): "
    assert prefix in context, "Supply a concrete argv array rather than shell-evaluated project paths"
    arguments, _ = json.JSONDecoder().raw_decode(context.split(prefix, 1)[1])
    assert arguments == ["python", str(plugin / "scripts/evaluation-config.py"), "--project", str(project), "--update"]
    assert context.lower().index("onboarding") < context.index("--update")
    assert context.index("--update") < context.lower().index("runtime readiness"), "Backfill current defaults before runtime readiness"
    assert path.read_bytes() == original, "Hook context must not mutate config before onboarding is resolved"
    assert list(project.iterdir()) == [path] and list(profile.iterdir()) == []
    delegated = _hook(isolated_plugin, {"hook_event_name": "SubagentStart", "cwd": str(project), "agent_type": "test-author"})
    assert delegated.returncode == 0, delegated.stderr
    assert "--update" not in json.loads(delegated.stdout)["hookSpecificOutput"]["additionalContext"]
    assert path.read_bytes() == original


@pytest.mark.parametrize("plan_mode", [False, True])
def test_root_hook_preserves_plan_mode_and_requires_goal_approval_when_enabled(isolated_plugin, plan_mode):
    _, project, profile, _ = isolated_plugin
    configuration = project / "kiss-chris-stack.config.json"
    content = json.dumps({"plan-mode": plan_mode, "evaluation": {"live": {"enabled": False}}}).encode("utf-8")
    configuration.write_bytes(content)
    context = _root_context(isolated_plugin).lower()
    assert "plan-mode" in context
    assert "true" in context and "false" in context
    assert "goal" in context and "approval" in context and "explicit" in context
    assert "before" in context and ("stop" in context or "wait" in context)
    assert "evaluation-config.py" in context, "Keep strict validation in the shared resolver"
    assert configuration.read_bytes() == content
    assert list(profile.iterdir()) == []


@pytest.mark.parametrize("event", ["SessionStart", "UserPromptSubmit"])
def test_root_hook_uses_project_config_as_initialization_marker(isolated_plugin, event):
    _, project, profile, _ = isolated_plugin
    uninitialized = _root_context(isolated_plugin, event)
    assert "kiss-chris-stack.config.json" in uninitialized
    assert "/setup" in uninitialized
    assert re.search(r"(?:missing|absent|not (?:yet )?(?:initialized|configured))", uninitialized, re.I)

    # Existing documentation and a nested config cannot mark this project ready.
    for directory in ("docs", "agent-traces"):
        (project / directory).mkdir()
        (project / directory / "existing.md").write_text("Existing project knowledge", encoding="utf-8")
    (project / "docs/kiss-chris-stack.config.json").write_text("{}", encoding="utf-8")
    assert _root_context(isolated_plugin, event) == uninitialized

    configuration = project / "kiss-chris-stack.config.json"
    content = b'{"evaluation":{"live":{"enabled":false},"sonarqube":{"enabled":true}}}\n'
    configuration.write_bytes(content)
    initialized = _root_context(isolated_plugin, event)
    assert initialized != uninitialized, "Config presence must select readiness checks instead of first-time setup"
    assert "kiss-chris-stack.config.json" in initialized
    assert "readiness" in initialized.lower() and "mcp" in initialized.lower()
    assert re.search(r"(?:already (?:initialized|configured)|configured project|(?:project|setup|initialization) (?:is )?(?:initialized|complete))", initialized, re.I)
    assert re.search(r"(?:do not|without|skip|no) [^.\n]*(?:initializ|bootstrap)", initialized, re.I), "Existing config must not reinitialize the project"
    assert "Keep this request unchanged" in initialized
    assert _root_context(isolated_plugin, event) == initialized, "Initialization never substitutes for current readiness checks"
    assert configuration.read_bytes() == content
    assert list(profile.iterdir()) == [], "Routing must not mutate the profile"


@pytest.mark.parametrize("event", ["SessionStart", "UserPromptSubmit"])
def test_root_hook_keeps_installation_onboarding_ahead_of_automatic_setup(isolated_plugin, event):
    native = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    skill = Path(native["extensions"]["com.openai"]["onboardingSkill"]).parts[-2]
    context = _root_context(isolated_plugin, event).lower()
    assert skill != "setup"
    assert "onboarding" in context and "consent" in context and "path" in context
    assert re.search(r"(?:before|precedence|priority|first)", context)


@pytest.mark.parametrize("event", ["SessionStart", "UserPromptSubmit"])
def test_root_hook_defers_unsafe_config_block_until_stack_route_is_selected(isolated_plugin, event):
    _, project, profile, _ = isolated_plugin
    marker = project / "kiss-chris-stack.config.json"
    marker.mkdir()
    prompt = "Fix this tiny typo without widening the change."
    result = _hook(isolated_plugin, {"hook_event_name": event, "cwd": str(project), "prompt": prompt})
    assert result.returncode == 0, "Unsafe stack config must not suppress direct-task routing guidance: " + result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"].lower()
    assert prompt.lower() in context
    assert "direct" in context and "grill-with-docs" in context and "wayfinder" in context
    boundary = "only after selecting a stack route:"
    assert context.index("direct") < context.index(boundary)
    stack_context = context.split(boundary, 1)[1].split("\n\n", 1)[0]
    assert "kiss-chris-stack.config.json" in stack_context
    assert re.search(r"(?:unsafe|invalid|nonregular|non-regular|regular file)[^.\n]*(?:block|stop)|(?:block|stop)[^.\n]*(?:unsafe|invalid|nonregular|non-regular|regular file)", stack_context)
    assert "execute /setup initialization" not in stack_context, "An unsafe path is not an absent initialization marker"
    assert "already configured" not in stack_context
    assert marker.is_dir() and list(marker.iterdir()) == []
    assert list(profile.iterdir()) == []


@pytest.mark.parametrize("dangling", [False, True])
def test_root_hook_defers_symlink_config_block_without_following_or_initializing(isolated_plugin, dangling):
    _, project, profile, _ = isolated_plugin
    target = project / "config-target.json"
    original = b'{"wayfinder":false}\n'
    if not dangling:
        target.write_bytes(original)
    marker = project / "kiss-chris-stack.config.json"
    try:
        marker.symlink_to(target)
    except OSError as error:
        pytest.skip(f"Host does not permit creating a symlink fixture: {error}")
    result = _hook(isolated_plugin, {"hook_event_name": "UserPromptSubmit", "cwd": str(project), "prompt": "Correct one typo."})
    assert result.returncode == 0, "A symlinked stack config must not suppress direct-task routing guidance: " + result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"].lower()
    assert "correct one typo." in context and "direct" in context
    stack_context = context.split("only after selecting a stack route:", 1)[1].split("\n\n", 1)[0]
    assert "symlink" in stack_context or "symbolic link" in stack_context
    assert "block" in stack_context or "stop" in stack_context
    assert "execute /setup initialization" not in stack_context
    assert "already configured" not in stack_context
    assert marker.is_symlink() and marker.readlink() == target
    if dangling:
        assert not target.exists()
    else:
        assert target.read_bytes() == original
    assert list(profile.iterdir()) == []


@pytest.mark.parametrize("event", ["SessionStart", "UserPromptSubmit"])
def test_root_hook_requires_strict_validation_without_replacing_malformed_config(isolated_plugin, event):
    _, project, _, _ = isolated_plugin
    marker = project / "kiss-chris-stack.config.json"
    malformed = b'{"evaluation": "broken"'
    marker.write_bytes(malformed)
    context = _root_context(isolated_plugin, event).lower()
    assert "evaluation-config.py" in context, "Use the strict shared resolver instead of trusting config presence"
    assert re.search(r"(?:invalid|malformed|unreadable)[^.\n]*(?:block|stop|error)", context)
    assert "before" in context and ("implementation" in context or "original request" in context)
    assert marker.read_bytes() == malformed


def test_delegated_hook_does_not_inspect_or_repair_project_marker(isolated_plugin):
    _, project, profile, _ = isolated_plugin
    marker = project / "kiss-chris-stack.config.json"
    marker.mkdir()
    result = _hook(isolated_plugin, {"hook_event_name": "SubagentStart", "cwd": str(project), "agent_type": "test-author"})
    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "test-author" in context and "Do not register another goal, run setup" in context
    assert marker.is_dir() and list(marker.iterdir()) == []
    assert list(profile.iterdir()) == []


def test_setup_marks_initialization_only_after_success_and_preserves_config():
    text = (ROOT / "skills/setup/SKILL.md").read_text(encoding="utf-8").lower()
    assert "kiss-chris-stack.config.json" in text
    assert "evaluation-config.py" in text, "Existing config needs the same strict resolver as evaluation"
    assert "marker" in text or "indicator" in text
    assert "create" in text and "only after" in text, "Never leave an initialized marker after failed setup or missing MCP"
    assert "mcp" in text and "documentation" in text
    assert re.search(r"(?:preserve|do not overwrite|never overwrite)[^.\n]*(?:config|settings|switch)", text)
    assert re.search(r"(?:invalid|malformed|unreadable)[^.\n]*(?:block|stop|error)", text), "A broken config must not be overwritten or treated as absent"
    policy = (ROOT / "assets/global-stack-policy.md").read_text(encoding="utf-8").lower()
    orchestrator = (ROOT / "skills/kiss-chris-stack/SKILL.md").read_text(encoding="utf-8").lower()
    for instructions in (policy, orchestrator):
        assert "kiss-chris-stack.config.json" in instructions
        assert "if either directory is missing" not in instructions
        assert "if documentation is missing or empty, bootstrap" not in instructions


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


def test_grilling_is_discoverable_attributed_and_integrity_checked():
    native = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    skill = ROOT / native["skills"] / "grilling" / "SKILL.md"
    assert skill.is_file(), "Grilling must be shipped as a discoverable bundled skill"
    content = skill.read_text(encoding="utf-8")
    assert re.search(r"(?m)^name:\s*grilling\s*$", content)
    assert re.search(r"(?m)^description:\s*\S", content)
    assert "mattpocock/skills" in content, "Identify the adapted upstream skill"
    license_path = ROOT / "licenses/grilling-LICENSE"
    license_text = license_path.read_text(encoding="utf-8")
    assert "MIT License" in license_text and "Matt Pocock" in license_text
    provenance = (ROOT / "docs/THIRD-PARTY.md").read_text(encoding="utf-8")
    assert "mattpocock/skills" in provenance and "grilling-LICENSE" in provenance
    hashes = json.loads((ROOT / "assets/bundle-manifest.json").read_text(encoding="utf-8"))["sha256"]
    for path in (skill, license_path):
        relative = path.relative_to(ROOT).as_posix()
        assert hashes.get(relative) == hashlib.sha256(path.read_bytes()).hexdigest(), relative


@pytest.mark.parametrize("relative", ["assets/global-stack-policy.md", "skills/kiss-chris-stack/SKILL.md"])
def test_root_policy_selects_pre_goal_workflow_from_request_and_context(relative):
    content = (ROOT / relative).read_text(encoding="utf-8").lower()
    assert "grill-with-docs" in content and "wayfinder" in content
    assert "grill-me" in content and "evaluation-config.py" in content
    assert "explicit" in content, "Keep the legacy interview explicitly available"
    assert "docs/" in content and "agent-traces/" in content
    assert "plan-mode" in content and "evaluation" in content
    assert "goal" in content and ("register" in content or "registration" in content)


def test_grilling_resolves_decisions_then_continues_without_closing_approval():
    content = (ROOT / "skills/grilling/SKILL.md").read_text(encoding="utf-8").lower()
    for concept in ("decision", "prerequisite", "round", "recommend", "fact", "wait", "answer"):
        assert concept in content, f"Preserve the upstream decision interview mechanism: {concept}"
    assert re.search(r"(?:continue|proceed|resume)[^.\n]*automatic|automatic[^.\n]*(?:continue|proceed|resume)", content)
    assert re.search(r"(?:no|without|do not|never)[^.\n]*(?:closing|final|shared.understanding)[^.\n]*(?:confirm|approv)|(?:no|without|do not|never)[^.\n]*(?:confirm|approv)[^.\n]*(?:closing|final|shared.understanding)", content)
    assert "plan-mode" in content and "approval" in content
    assert re.search(r"(?:clear|settled|resolved)[^.\n]*(?:question|ask)|(?:question|ask)[^.\n]*(?:clear|settled|resolved)", content), "Do not invent questions for an already settled request"
    assert "do not act on it until the user confirms" not in content


@pytest.mark.parametrize("event", ["SessionStart", "UserPromptSubmit"])
@pytest.mark.parametrize("plan_mode", [False, True])
@pytest.mark.parametrize("grill_me", [None, False, True])
def test_live_root_hook_routes_new_workflows_without_changing_goal_approval(isolated_plugin, event, plan_mode, grill_me):
    plugin, project, profile, _ = isolated_plugin
    path = project / "kiss-chris-stack.config.json"
    configuration = {"plan-mode": plan_mode}
    if grill_me is not None:
        configuration["grill-me"] = grill_me
    original = json.dumps(configuration).encode()
    path.write_bytes(original)
    context = _root_context(isolated_plugin, event).lower()
    assert json.dumps(str(plugin / "skills/kiss-chris-stack/SKILL.md")).lower() in context
    assert "grill-with-docs" in context and "wayfinder" in context
    assert "grill-me" in context and "evaluation-config.py" in context
    assert "default" in context and "true" in context and "false" in context
    assert "always run grilling" not in context
    assert "explicit" in context and "goal" in context
    assert "plan-mode" in context and "approval" in context
    assert path.read_bytes() == original and list(profile.iterdir()) == []


def test_delegated_role_does_not_restart_grilling(isolated_plugin):
    result = _hook(isolated_plugin, {"hook_event_name": "SubagentStart", "cwd": str(isolated_plugin[1]), "agent_type": "test-author"})
    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "skills/grilling" not in context.replace("\\", "/"), "The root owns goal preparation; delegated roles keep their assigned goal"
    assert "existing goal" in context


def test_unsupported_grilling_alias_is_rejected_without_changing_configuration(tmp_path):
    path = tmp_path / "kiss-chris-stack.config.json"
    path.write_text('{"grilling": false}', encoding="utf-8")
    result = subprocess.run([sys.executable, str(ROOT / "scripts/evaluation-config.py"), "--project", str(tmp_path)], text=True, capture_output=True, timeout=15)
    assert result.returncode != 0 and "supported keys" in result.stderr
    assert path.read_text(encoding="utf-8") == '{"grilling": false}'


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


@pytest.mark.parametrize("relative", [
    "skills/grilling/SKILL.md", "skills/evaluate/SKILL.md", "skills/setup/SKILL.md",
    "README.md", "docs/EVALUATION.md", "docs/ARCHITEKTUR.md", "docs/PRODUKT-ONBOARDING.md",
    "agents/openai.yaml", "skills/kiss-chris-stack/agents/openai.yaml",
])
def test_current_entrypoints_document_configurable_grilling(relative):
    content = (ROOT / relative).read_text(encoding="utf-8").lower()
    assert "grill-me" in content, f"Expose the supported switch consistently in {relative}"
    assert "true" in content or "default" in content


def test_grilling_skill_preserves_explicit_invocation_when_automatic_interviews_are_disabled():
    content = (ROOT / "skills/grilling/SKILL.md").read_text(encoding="utf-8").lower()
    assert "grill-me" in content
    assert "explicit" in content and ("invoke" in content or "invocation" in content or "request" in content)


def test_repository_default_keeps_grill_me_enabled():
    configuration = json.loads((ROOT / "kiss-chris-stack.config.json").read_text(encoding="utf-8"))
    assert configuration.get("grill-me") is True
