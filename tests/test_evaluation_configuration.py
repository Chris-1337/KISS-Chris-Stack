"""Evaluation switches and the live-evidence workflow contract."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
HELPER = ROOT / "scripts/evaluation-config.py"
SKILL = ROOT / "skills/evaluate/SKILL.md"
DEFAULTS = {"evaluation": {"live": {"enabled": True}, "sonarqube": {"enabled": True}}}


@pytest.fixture
def config_module():
    spec = importlib.util.spec_from_file_location("evaluation_config_under_test", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolver_preserves_input_and_fills_independent_defaults(config_module):
    settings = {"evaluation": {"sonarqube": {"enabled": False}}}
    assert config_module.resolve_settings(settings, config_module.DEFAULTS) == {
        "evaluation": {"live": {"enabled": True}, "sonarqube": {"enabled": False}},
    }
    assert settings == {"evaluation": {"sonarqube": {"enabled": False}}}
    assert config_module.DEFAULTS == DEFAULTS


@pytest.mark.parametrize("settings", [
    [], {"unexpected": True}, {"evaluation": {"live": {"enabled": 0}}},
])
def test_resolver_rejects_unsupported_structure_or_value(config_module, settings):
    with pytest.raises(ValueError):
        config_module.resolve_settings(settings, config_module.DEFAULTS)


def test_json_objects_reject_duplicate_keys_at_every_depth(config_module):
    with pytest.raises(ValueError, match="Duplicate"):
        json.loads('{"evaluation": {}, "evaluation": {}}', object_pairs_hook=config_module.unique_object)


@pytest.mark.parametrize("content", [None, '{"evaluation":{"live":{"enabled":false}}}'])
def test_main_reads_actual_project_and_emits_normalized_config(config_module, tmp_path, monkeypatch, capsys, content):
    if content is not None:
        (tmp_path / "kiss-chris-stack.config.json").write_text(content, encoding="utf-8-sig")
    monkeypatch.setattr(sys, "argv", [str(HELPER), "--project", str(tmp_path)])
    config_module.main()
    captured = capsys.readouterr()
    assert not captured.err
    expected = {"evaluation": {"live": {"enabled": content is None}, "sonarqube": {"enabled": True}}}
    assert json.loads(captured.out) == expected


@pytest.mark.parametrize("failure", ["missing-project", "read-error", "invalid-json"])
def test_main_reports_blocking_errors_without_emitting_settings(config_module, tmp_path, monkeypatch, capsys, failure):
    project = tmp_path / "missing" if failure == "missing-project" else tmp_path
    path = tmp_path / "kiss-chris-stack.config.json"
    if failure == "read-error":
        path.mkdir()
    elif failure == "invalid-json":
        path.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", [str(HELPER), "--project", str(project)])
    with pytest.raises(SystemExit) as error:
        config_module.main()
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert not captured.out


def run_config(project, *arguments):
    assert HELPER.is_file(), "Evaluation needs a packaged executable config resolver"
    return subprocess.run(
        [sys.executable, str(HELPER), "--project", str(project), *arguments],
        text=True, capture_output=True, timeout=15,
    )


@pytest.mark.parametrize("configuration", [None, {}, {"evaluation": {}}, {"evaluation": {"live": {}}}])
def test_missing_settings_preserve_enabled_defaults(tmp_path, configuration):
    if configuration is not None:
        (tmp_path / "kiss-chris-stack.config.json").write_text(json.dumps(configuration), encoding="utf-8")
    result = run_config(tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == DEFAULTS
    if configuration is None:
        assert not (tmp_path / "kiss-chris-stack.config.json").exists(), "Reading defaults must not create configuration"


@pytest.mark.parametrize("live,sonarqube", [(False, True), (True, False), (False, False), (True, True)])
def test_switches_are_independent_real_booleans(tmp_path, live, sonarqube):
    configuration = {"evaluation": {"live": {"enabled": live}, "sonarqube": {"enabled": sonarqube}}}
    path = tmp_path / "kiss-chris-stack.config.json"
    path.write_text(json.dumps(configuration), encoding="utf-8-sig")
    original = path.read_bytes()
    result = run_config(tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == configuration
    assert path.read_bytes() == original, "Reading configuration must not rewrite project files"


@pytest.mark.parametrize("configuration", [
    [], None, False, {"unknown": True}, {"evaluation": []},
    {"evaluation": {"unknown": {"enabled": False}}},
    {"evaluation": {"live": False}},
    {"evaluation": {"sonarqube": None}},
    {"evaluation": {"live": {"enabled": "false"}}},
    {"evaluation": {"sonarqube": {"enabled": 0}}},
    {"evaluation": {"live": {"enabled": None}}},
    {"evaluation": {"live": {"enabeld": False}}},
])
def test_invalid_configuration_fails_closed(tmp_path, configuration):
    (tmp_path / "kiss-chris-stack.config.json").write_text(json.dumps(configuration), encoding="utf-8")
    result = run_config(tmp_path)
    assert result.returncode != 0
    assert result.stderr.strip(), "A blocked config must explain its error"
    assert not result.stdout.strip(), "Invalid config must not emit usable disabled gates"


@pytest.mark.parametrize("content", [
    "{broken", "", "{\"evaluation\": {\"live\": {\"enabled\": NaN}}}",
    '{"evaluation": {"live": {"enabled": true, "enabled": false}}}',
])
def test_malformed_json_fails_closed(tmp_path, content):
    (tmp_path / "kiss-chris-stack.config.json").write_text(content, encoding="utf-8")
    result = run_config(tmp_path)
    assert result.returncode != 0
    assert result.stderr.strip()
    assert not result.stdout.strip()


def test_missing_project_cannot_fall_back_to_enabled_defaults(tmp_path):
    result = run_config(tmp_path / "missing")
    assert result.returncode != 0
    assert result.stderr.strip()
    assert not result.stdout.strip()


def test_config_is_data_and_cannot_supply_shell_commands(tmp_path):
    marker = tmp_path / "executed"
    (tmp_path / "kiss-chris-stack.config.json").write_text(json.dumps({
        "evaluation": {"live": {"enabled": True, "command": f"echo unsafe > {marker}"}},
    }), encoding="utf-8")
    assert run_config(tmp_path).returncode != 0
    assert not marker.exists()


def test_canonical_policy_routes_goal_and_completion_through_evaluation_config():
    text = (ROOT / "assets/global-stack-policy.md").read_text(encoding="utf-8").lower()
    assert "kiss-chris-stack.config.json" in text
    assert "evaluation" in text and "before" in text and "goal" in text
    assert "live" in text and "sonarqube" in text and "complete" in text
    assert "evaluate/skill.md" in text, "Keep detailed workflow in a single bundled skill"


def test_live_workflow_demands_real_application_and_frontend_proof():
    assert SKILL.is_file(), "Bundle a reusable evaluation workflow"
    text = SKILL.read_text(encoding="utf-8").lower()
    for term in ("evaluation-config.py", "kiss-chris-stack.config.json", "docker compose", "direct", "frontend", "browser", "playwright", "chromium"):
        assert term in text, f"Missing live evaluation responsibility: {term}"
    assert "install" in text and ("automatic" in text or "without another" in text)
    assert "cli" in text and "headless" in text
    assert "assert" in text, "A startup/health response alone cannot demonstrate affected user behavior"
    assert "timeout" in text or "bounded" in text
    assert "fingerprint" in text and "evidence" in text
    assert "cleanup" in text and "volume" in text and "owned" in text


def test_disabled_and_inapplicable_checks_are_visible_and_sonar_stays_fresh():
    assert SKILL.is_file()
    text = SKILL.read_text(encoding="utf-8").lower()
    for term in ("disabled", "skip", "configured", "sonarqube", "analysis", "fresh", "block", "frontend"):
        assert term in text
    assert "no frontend" in text or "without a frontend" in text
    assert "not" in text and "pass" in text, "A disabled gate must not be reported as passed"
