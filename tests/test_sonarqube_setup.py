"""Read-only engine detection and the optional SonarQube workflow contract."""
import importlib.util
import json
import re
import subprocess
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

import pytest


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills/setup-sonarqube/SKILL.md"
HELPER = SKILL.parent / "scripts/check-container-runtime.py"


@pytest.fixture
def runtime(monkeypatch):
    assert HELPER.is_file(), "The optional setup needs an executable read-only prerequisite check"
    spec = importlib.util.spec_from_file_location("container_runtime_under_test", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configure(runtime, monkeypatch, engines):
    calls = []
    monkeypatch.setattr(runtime.shutil, "which", lambda name: name if name in engines else None)

    def run(argv, **kwargs):
        calls.append(argv)
        assert argv[1] == "info", "Prerequisite detection must never start containers or change a context"
        assert kwargs.get("timeout", 0) > 0, "A stopped engine must not hang normal setup"
        response = engines[argv[0]]
        if isinstance(response, Exception):
            raise response
        return SimpleNamespace(returncode=response[0], stdout=response[1], stderr="engine diagnostic")

    monkeypatch.setattr(runtime.subprocess, "run", run)
    return calls


@pytest.mark.parametrize("engine,payload", [
    ("docker", {"OSType": "linux"}),
    ("podman", {"host": {"os": "linux"}}),
])
def test_reachable_linux_engine_is_available(runtime, monkeypatch, engine, payload):
    calls = configure(runtime, monkeypatch, {engine: (0, json.dumps(payload))})
    report = runtime.check_runtime()
    assert report["available"] is True
    assert report["engine"] == engine
    assert len(calls) == 1


def test_missing_engine_is_optional(runtime, monkeypatch):
    calls = configure(runtime, monkeypatch, {})
    assert runtime.check_runtime()["available"] is False
    assert calls == []


@pytest.mark.parametrize("failure", [
    (1, ""),
    (0, "invalid JSON"),
    (0, json.dumps({"OSType": "windows"})),
    (0, "{}"),
    subprocess.TimeoutExpired("docker", 10),
    OSError("engine unavailable"),
])
def test_unusable_engine_falls_back_to_podman(runtime, monkeypatch, failure):
    calls = configure(runtime, monkeypatch, {
        "docker": failure,
        "podman": (0, json.dumps({"host": {"os": "linux"}})),
    })
    report = runtime.check_runtime()
    assert report["available"] is True
    assert report["engine"] == "podman"
    assert [call[0] for call in calls] == ["docker", "podman"]


def test_stopped_engines_do_not_raise(runtime, monkeypatch):
    configure(runtime, monkeypatch, {"docker": (1, ""), "podman": (1, "")})
    assert runtime.check_runtime()["available"] is False


def test_post_setup_offer_is_optional_and_links_to_packaged_skill():
    text = (ROOT / "skills/setup/SKILL.md").read_text(encoding="utf-8")
    assert "../setup-sonarqube/SKILL.md" in text
    assert "check-container-runtime.py" in text
    section = text[text.index("../setup-sonarqube/SKILL.md") - 300:].lower()
    assert "ask" in section and ("consent" in section or "confirm" in section)
    assert "later" in section and "install" in section
    assert "optional" in section


def test_skill_covers_credentials_stack_coverage_and_analysis_evidence():
    assert SKILL.is_file(), "Bundle /setup-sonarqube in the native skill directory"
    text = SKILL.read_text(encoding="utf-8").lower()
    for term in (".env", ".gitignore", "token", "password", "java", "typescript", "jacoco", "lcov"):
        assert term in text, f"Missing setup responsibility: {term}"
    for term in ("vulnerabilities", "bugs", "code smells", "80", "analysis", "quality gate"):
        assert term in text, f"Missing strict gate responsibility: {term}"
    assert "preserv" in text and "existing" in text
    assert "analysisid" in text or "analysis id" in text
    assert "report-task.txt" in text
    assert "timeout" in text


def test_shared_policy_requires_sonarqube_gate_before_completion():
    text = (ROOT / "assets/global-stack-policy.md").read_text(encoding="utf-8").lower()
    assert "sonarqube" in text, "Configured SonarQube must be part of the canonical goal policy"
    section = text[text.index("sonarqube") - 100:]
    assert "quality gate" in section
    assert "complete" in section
    assert "analysis" in section and ("fresh" in section or "current" in section)
    assert "all" in section


def test_reader_credentials_have_project_read_permissions_separate_from_scanning():
    text = SKILL.read_text(encoding="utf-8").lower()
    assert "sonar_reader_token" in text, "Persist a separately usable reader credential in protected .env"
    assert "user token" in text, "Project analysis tokens do not grant general read API access"
    assert "browse" in text and "see source code" in text
    assert "execute analysis" in text
    assert "project analysis token" in text
    assert "least" in text, "Reader credentials must not inherit administrative access"


def test_setup_proves_read_access_to_analysis_results_and_source():
    text = SKILL.read_text(encoding="utf-8").lower()
    for endpoint in ("/api/issues/search", "/api/measures/component", "/api/sources/lines", "/api/ce/task", "/api/qualitygates/project_status"):
        assert endpoint in text, f"Verify reader authorization against {endpoint}, including private projects"
    assert "403" in text and "401" in text
    assert "authentication/validate" in text
    assert "read" in text and "upload" in text


def test_reader_permission_audit_includes_effective_inherited_global_access():
    text = SKILL.read_text(encoding="utf-8").lower()
    assert "group" in text and "inherit" in text, "Default group membership can grant privileges absent from direct project grants"
    assert "effective" in text and "global" in text
    assert "provision" in text or "create project" in text
    assert "unrelated" in text, "A scoped reader must not gain project creation or analysis privileges over unrelated projects"
    assert "shared" in text and "authoriz" in text, "Fixing inherited permissions must preserve the existing-instance authorization boundary"


@pytest.fixture
def renewal_policy():
    sections = re.split(r"(?m)^## ", SKILL.read_text(encoding="utf-8").lower())
    candidates = [section for section in sections if re.search(r"\b(?:renew\w*|refresh\w*)\b", section) and "expir" in section]
    assert candidates, "Document managed expired-token renewal as an operational step"
    return candidates[0]


def test_renewal_distinguishes_expiry_and_preserves_managed_token_scope(renewal_policy):
    assert "before" in renewal_policy and "scanner" in renewal_policy and "reader" in renewal_policy
    assert all(reason in renewal_policy for reason in ("401", "403", "revok", "permission")), "Authentication/authorization failures need diagnosis rather than blind rotation"
    assert "owner" in renewal_policy and "protected" in renewal_policy and "credential" in renewal_policy
    assert "same" in renewal_policy and all(scope in renewal_policy for scope in ("type", "project", "least")), "Renewal must preserve the managed token's owner and least-privilege scope"


def test_renewal_persists_safely_retries_once_and_stays_quiet_on_success(renewal_policy):
    assert ".env" in renewal_policy and "atomic" in renewal_policy and "unrelated" in renewal_policy and "old" in renewal_policy
    assert "reload" in renewal_policy and "environment" in renewal_policy, "The retry must receive the replacement token rather than stale child-process credentials"
    assert re.search(r"\b(?:one|once|single)\b", renewal_policy) and "retry" in renewal_policy and "bounded" in renewal_policy
    assert ("quiet" in renewal_policy or "silent" in renewal_policy) and re.search(r"(?:no|without|not)[^.\n]*confirm", renewal_policy), "Successful authorized renewal must not interrupt the user"
    assert "fail" in renewal_policy and "visible" in renewal_policy and "block" in renewal_policy, "Failed renewal cannot satisfy the goal or bypass its gate"


@pytest.fixture
def analysis_reader():
    helper = SKILL.parent / "scripts/read-analysis.py"
    assert helper.is_file(), "Repeated gate/read checks need executable authorization evidence"
    spec = importlib.util.spec_from_file_location("sonar_analysis_reader_under_test", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


READ_ENDPOINTS = (
    "/api/issues/search", "/api/measures/component", "/api/sources/lines",
    "/api/ce/task", "/api/qualitygates/project_status",
)


def test_reader_requests_the_uploaded_analysis_and_actual_source(analysis_reader):
    calls = {}

    def request_json(path):
        url = urlsplit(path)
        calls[url.path] = parse_qs(url.query)
        return {"endpoint": url.path}

    evidence = analysis_reader.verify_read_access("repo:private", "analysis-new", "task-new", "repo:private:src/a.py", request_json)
    assert isinstance(evidence, dict) and evidence
    assert set(READ_ENDPOINTS).issubset(calls)
    assert calls["/api/issues/search"]["componentKeys"] == ["repo:private"]
    assert calls["/api/measures/component"]["component"] == ["repo:private"]
    assert calls["/api/sources/lines"]["key"] == ["repo:private:src/a.py"]
    assert calls["/api/ce/task"]["id"] == ["task-new"]
    assert calls["/api/qualitygates/project_status"]["analysisId"] == ["analysis-new"]
    assert "coverage" in calls["/api/measures/component"]["metricKeys"][0].split(",")


@pytest.mark.parametrize("endpoint", READ_ENDPOINTS)
@pytest.mark.parametrize("status", [401, 403])
def test_successful_auth_or_upload_cannot_hide_forbidden_reads(analysis_reader, endpoint, status):
    def request_json(path):
        if urlsplit(path).path == endpoint:
            raise HTTPError(path, status, "Denied", {}, None)
        return {"valid": True, "task": {"status": "SUCCESS", "analysisId": "analysis-new"}, "projectStatus": {"status": "OK"}}

    with pytest.raises(HTTPError) as error:
        analysis_reader.verify_read_access("repo:private", "analysis-new", "task-new", "repo:private:src/a.py", request_json)
    assert error.value.code == status
