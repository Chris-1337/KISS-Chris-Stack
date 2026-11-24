"""Release readiness is local source evidence, never publication authorization."""
import importlib.util
import contextlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
CHECKER = ROOT / "scripts/check-release.py"
PUBLIC_SENTINEL = "fixture-secret-never-print-1947"


@pytest.fixture
def candidate(tmp_path):
    spec = importlib.util.spec_from_file_location("release_host_helpers", ROOT / "scripts/test-host-workflows.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    project = tmp_path / "candidate with spaces"
    project.mkdir()
    helpers.copy_candidate(ROOT, project)
    spec = importlib.util.spec_from_file_location("release_candidate_resources", CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    for relative in checker.RELEASE_EXTRAS:
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / relative).read_bytes())
    (project / ".env").write_text(PUBLIC_SENTINEL, encoding="utf-8")
    for args in (["init", "--quiet"], ["add", "plugin.json"],
                 ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--quiet", "-m", "Fixture"]):
        result = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, timeout=15)
        assert result.returncode == 0, result.stderr
    return project


def run_check(project, *args):
    assert CHECKER.is_file(), "Provide the local release-readiness CLI"
    spec = importlib.util.spec_from_file_location("release_readiness_checks", CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        code = checker.main(["--project", str(project), *args])
    direct = json.loads(captured.getvalue())
    result = subprocess.run([sys.executable, str(CHECKER), "--project", str(project), *args],
                            capture_output=True, text=True, timeout=30, cwd=ROOT)
    assert PUBLIC_SENTINEL not in result.stdout + result.stderr
    receipt = json.loads(result.stdout)
    assert code == result.returncode and direct == receipt, "Public main and actual command agree"
    assert receipt["published"] is False, "A readiness check never publishes"
    assert receipt["status"] == ("passed" if result.returncode == 0 else "failed")
    return result, receipt


def update_json(project, relative, change):
    path = project / relative
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def require_failure(project, *args):
    result, receipt = run_check(project, *args)
    assert result.returncode != 0
    assert receipt.get("errors"), "Retain actionable nonsecret diagnostics"
    return receipt


def test_valid_current_candidate_is_source_bound_and_read_only(candidate):
    files = {p.relative_to(candidate): p.read_bytes() for p in candidate.rglob("*") if p.is_file()}
    result, receipt = run_check(candidate)
    assert result.returncode == 0, result.stdout + result.stderr
    assert receipt["candidate"] == {"name": "kiss-chris-stack", "version": "0.2.0"}
    assert re.fullmatch(r"[0-9a-f]{40,64}", receipt["source"]["revision"])
    assert re.fullmatch(r"[0-9a-f]{64}", receipt["source"]["fingerprint"])
    repeated, again = run_check(candidate, "--expect-source", receipt["source"]["fingerprint"])
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr
    assert again["source"] == receipt["source"]
    assert files == {p.relative_to(candidate): p.read_bytes() for p in candidate.rglob("*") if p.is_file()}


@pytest.mark.parametrize("relative,field,value", [
    ("plugin.json", "name", "other-plugin"),
    ("plugin.json", "version", "99.0.0"),
    (".codex-plugin/plugin.json", "version", ""),
    (".agents/plugins/marketplace.json", "name", "other-marketplace"),
])
def test_mismatched_candidate_metadata_fails(candidate, relative, field, value):
    update_json(candidate, relative, lambda data: data.update({field: value}))
    require_failure(candidate)


def test_marketplace_entry_identity_and_optional_version_are_checked(candidate):
    relative = ".agents/plugins/marketplace.json"
    update_json(candidate, relative, lambda data: data["plugins"][0].update(version="99.0.0"))
    require_failure(candidate)
    update_json(candidate, relative, lambda data: data["plugins"][0].update(version="0.2.0", name="other-plugin"))
    require_failure(candidate)


def test_native_version_uses_semver_and_host_length_limit(candidate):
    cases = [
        ("1.2.3-alpha.1+build.001", True),
        ("1.2.3+001", True),
        ("1.2.3+" + "a" * 58, True),  # Exactly 64 characters.
        ("1.2.3+" + "a" * 59, False),
        ("1.2.3+.", False),
        ("1.2.3-01", False),
        ("01.2.3", False),
        ("1.2.3-alpha.", False),
        ("1.2.3+build.", False),
        ("1.2.3-", False),
        ("1.2.3+", False),
        ("\u0661.2.3", False),
    ]
    mismatches = []
    for version, valid in cases:
        update_json(candidate, ".codex-plugin/plugin.json", lambda data: data.update(version=version))
        result, receipt = run_check(candidate)
        if (result.returncode == 0) != valid:
            mismatches.append({"version": version, "expected_valid": valid, "receipt": receipt})
        if result.returncode:
            assert receipt.get("errors"), version
    assert not mismatches, mismatches


def test_malformed_manifest_fails_visibly_without_echoing_contents(candidate):
    (candidate / ".codex-plugin/plugin.json").write_text('{"broken":' + PUBLIC_SENTINEL, encoding="utf-8")
    require_failure(candidate)


@pytest.mark.parametrize("relative", ["hooks/hooks.json", "LICENSE", "licenses/grilling-LICENSE", "docs/THIRD-PARTY.md",
                                      "docs/DELIVERY.md", "docs/GITHUB-PUBLICATION.md", "assets/versions.json"])
def test_missing_referenced_or_provenance_resource_fails(candidate, relative):
    (candidate / relative).unlink()
    require_failure(candidate)


def test_modified_bundled_resource_fails_integrity_check(candidate):
    (candidate / "skills/grilling/SKILL.md").write_text("tampered", encoding="utf-8")
    require_failure(candidate)


@pytest.mark.parametrize("reference", ["native-hooks", "marketplace-source", "bundle-path"])
def test_manifest_paths_cannot_escape_candidate(candidate, reference, monkeypatch):
    outside = candidate.parent / "outside.json"
    outside.write_text(PUBLIC_SENTINEL, encoding="utf-8")
    if reference == "native-hooks":
        update_json(candidate, ".codex-plugin/plugin.json", lambda data: data.update(hooks="../outside.json"))
    elif reference == "marketplace-source":
        update_json(candidate, ".agents/plugins/marketplace.json",
                    lambda data: data["plugins"][0]["source"].update(path="../"))
    else:
        update_json(candidate, "assets/bundle-manifest.json", lambda data: data["sha256"].update({"../outside.json": "0" * 64}))
    original_open = Path.open

    def guarded_open(path, *args, **kwargs):
        assert path.resolve() != outside.resolve(), "Reject outside references before reading their bytes"
        return original_open(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", guarded_open)
        require_failure(candidate)
    assert outside.read_text(encoding="utf-8") == PUBLIC_SENTINEL


def test_source_expectation_rejects_wrong_or_changed_untracked_deliverable(candidate):
    result, receipt = run_check(candidate)
    assert result.returncode == 0, result.stdout + result.stderr
    original = receipt["source"]["fingerprint"]
    require_failure(candidate, "--expect-source", "0" * 64)
    (candidate / "scripts/untracked-deliverable.py").write_text("# New candidate content\n", encoding="utf-8")
    require_failure(candidate, "--expect-source", original)
    result, changed = run_check(candidate)
    assert result.returncode == 0, result.stdout + result.stderr
    assert changed["source"]["fingerprint"] != original
    assert changed["source"]["revision"] == receipt["source"]["revision"]


def test_candidate_python_is_data_and_never_imported(candidate):
    sentinel = candidate / "unexpected-code-execution"
    (candidate / "scripts/test-host-workflows.py").write_text(
        "from pathlib import Path\nPath(" + repr(str(sentinel)) + ").write_text('executed')\nraise RuntimeError('untrusted candidate')\n",
        encoding="utf-8")
    result, _ = run_check(candidate)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not sentinel.exists(), "Use owning checker helpers, never candidate Python imports"


@pytest.mark.parametrize("relative", ["LICENSE", "docs/THIRD-PARTY.md", "docs/DELIVERY.md", "docs/GITHUB-PUBLICATION.md"])
def test_release_source_identity_binds_license_and_provenance(candidate, relative):
    result, receipt = run_check(candidate)
    assert result.returncode == 0, result.stdout + result.stderr
    with (candidate / relative).open("a", encoding="utf-8") as stream:
        stream.write("\nCandidate provenance clarification.\n")
    require_failure(candidate, "--expect-source", receipt["source"]["fingerprint"])


def test_release_inventory_binds_operative_sdlc_guidance_and_preserves_existing_resources():
    spec = importlib.util.spec_from_file_location("release_candidate_inventory", CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    required = {
        "LICENSE", "docs/THIRD-PARTY.md", "docs/DELIVERY.md", "docs/GITHUB-PUBLICATION.md",
        "SECURITY.md", ".github/CODEOWNERS", ".github/main-ruleset.json", "README.md",
        "CONTRIBUTING.md", "AGENTS.md", "docs/OPERATIONS.md", "docs/LIFECYCLE.md", "docs/EVALUATION.md",
        "docs/WAYFINDER.md", "docs/ARCHITEKTUR.md", "docs/HOST-TESTS.md",
        "docs/SONARQUBE.md", "docs/REMOTE-CONTAINER.md", "docs/PRODUKT-ONBOARDING.md", "docs/LEARNING.md",
        "docs/adr/0001-dokumentation-und-agentenrollen.md", "docs/adr/0002-codex-marketplace-und-lifecycle.md",
        "docs/adr/0003-documentation-language.md", "docs/adr/0004-proportionate-routing-and-delegation.md",
        ".github/workflows/tests.yml", "sonar-project.properties",
    }
    assert required <= set(checker.RELEASE_EXTRAS), "Operative release guidance must be source-bound"


@pytest.mark.parametrize("change", ["modify", "omit"])
def test_operational_guidance_change_cannot_reuse_a_current_candidate_pass(candidate, change):
    path = candidate / "docs/OPERATIONS.md"
    path.write_bytes((ROOT / "docs/OPERATIONS.md").read_bytes())
    result, receipt = run_check(candidate)
    assert result.returncode == 0, result.stdout + result.stderr
    if change == "omit":
        path.unlink()
    else:
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\nChanged candidate recovery procedure.\n")
    require_failure(candidate, "--expect-source", receipt["source"]["fingerprint"])


def test_policy_carries_proportionate_delivery_acceptance_and_separate_authorization():
    text = (ROOT / "assets/global-stack-policy.md").read_text(encoding="utf-8").lower()
    # Scope checks to delivery guidance: unrelated setup/goal prose cannot satisfy it.
    sections = re.split(r"(?m)^## ", text)
    delivery = "\n".join(section for section in sections if section.strip() and re.search(r"delivery|release", section.splitlines()[0]))
    assert delivery, "The shared policy must own reusable delivery guidance"
    for alternatives in (("applicab",), ("target", "environment"), ("immutable",), ("source",),
                         ("configur",), ("compatib",), ("owner",), ("authoriz",), ("preflight",),
                         ("success",), ("abort",), ("rollback", "forward recovery"), ("preserv",),
                         ("post-release", "postrelease"), ("irreversib",)):
        assert any(term in delivery for term in alternatives), alternatives
    assert re.search(r"(?:does not|never|not)[^.\n]*(?:authoriz|permission)|(?:authoriz|permission)[^.\n]*(?:separate|explicit)", delivery)


@pytest.mark.parametrize("relative", ["skills/kiss-chris-stack/SKILL.md", "skills/evaluate/SKILL.md"])
def test_existing_roles_apply_delivery_guidance(relative):
    text = (ROOT / relative).read_text(encoding="utf-8").lower()
    assert "delivery" in text and "applicab" in text
    assert "authoriz" in text and ("rollback" in text or "recovery" in text)
    assert "post-release" in text or "postrelease" in text
    assert "global-stack-policy.md" in text


def test_repository_delivery_guide_distinguishes_local_reversal_and_published_recovery():
    path = ROOT / "docs/DELIVERY.md"
    assert path.is_file(), "Document the actual candidate and reversal procedure"
    text = path.read_text(encoding="utf-8").lower()
    for term in ("check-release.py", "--project", "--expect-source", "marketplace", "candidate", "revers", "preserv", "authoriz", "publish"):
        assert term in text, term
    assert "unverified" in text or "does not prove" in text
    publication = (ROOT / "docs/GITHUB-PUBLICATION.md").read_text(encoding="utf-8").lower()
    assert "delivery.md" in publication, "Reuse existing publication guidance"
