"""Contracts for the instruction-based setup Git workflow."""

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8").lower()


def git_workflow():
    setup = read("skills/setup/SKILL.md")
    heading = "## git hygiene and staging"
    assert heading in setup, "Setup needs one shared Git workflow for both setup skills"
    return setup.split(heading, 1)[1].split("\n## ", 1)[0]


def test_both_setup_entrypoints_use_shared_git_workflow():
    setup = read("skills/setup/SKILL.md")
    sonar = read("skills/setup-sonarqube/SKILL.md")
    assert "#git-hygiene-and-staging" in setup, "Wire preparation and final staging into normal setup"
    assert "../setup/skill.md#git-hygiene-and-staging" in sonar
    workflow = git_workflow()
    assert "initialization" in workflow and "explicit" in workflow
    assert re.search(r"(?:never|not|no|without)[^.\n]*readiness|readiness[^.\n]*(?:never|not|no|without)", workflow)


def test_setup_ignores_local_artifacts_without_discarding_existing_rules():
    workflow = git_workflow()
    for path in ("/.codegraph/", "/.env", "/.scannerwork/", "/.sonar-evidence/"):
        assert path in workflow, f"Protect setup-local artifact {path}"
    assert ".gitignore" in workflow and "preserve" in workflow
    assert re.search(r"(?:missing|duplicate|idempotent)", workflow)
    assert "git check-ignore" in workflow, "Prove actual exclusion, including conflicting negations"


def test_staging_uses_exact_nonsecret_setup_files_after_success():
    workflow = git_workflow()
    assert "--literal-pathspecs" in workflow and " add " in workflow
    assert "--" in workflow and "exact" in workflow
    for path in (".gitignore", "kiss-chris-stack.config.json", "docs/", "agent-traces/", "sonar-project.properties"):
        assert path in workflow, f"Cover generated setup metadata {path}"
    assert "nonsecret" in workflow or "non-secret" in workflow
    assert "success" in workflow
    assert re.search(r"(?:never|do not)[^.\n]*(?:git add \.|git add -a|broad|directories)", workflow)
    assert re.search(r"(?:never|do not)[^.\n]*force", workflow)


def test_preserves_unrelated_and_partially_staged_work():
    workflow = git_workflow()
    assert "before" in workflow and re.search(r"(?:snapshot|baseline|record)", workflow)
    assert "unrelated" in workflow and "index" in workflow
    assert re.search(r"(?:partial|mixed|pre-existing|preexisting)", workflow)
    assert re.search(r"(?:hunk|patch|skip|leave.*unstaged)", workflow), "Whole-file add must not stage unrelated edits in a setup file"
    assert "report" in workflow


def test_tracked_secrets_block_writes_and_git_failures_remain_visible():
    workflow = git_workflow()
    assert "git ls-files" in workflow and "tracked" in workflow
    assert re.search(r"before[^.\n]*(?:secret|credential)|(?:secret|credential)[^.\n]*before", workflow)
    assert re.search(r"(?:stop|block|conflict)", workflow)
    assert "untrack" in workflow and re.search(r"(?:never|do not)[^.\n]*untrack", workflow)
    assert "failure" in workflow or "failed" in workflow
    assert "report" in workflow and "secret" in workflow


def test_non_git_projects_and_readonly_checks_do_not_initialize_or_publish():
    workflow = git_workflow()
    assert re.search(r"(?:non-git|not.*repository|without.*git)", workflow)
    assert re.search(r"(?:never|do not)[^.\n]*git init", workflow)
    assert re.search(r"(?:skip|skipped)[^.\n]*stag|stag[^.\n]*(?:skip|skipped)", workflow)
    for operation in ("commit", "push"):
        assert re.search(rf"(?:never|do not)[^.\n]*{operation}", workflow)
