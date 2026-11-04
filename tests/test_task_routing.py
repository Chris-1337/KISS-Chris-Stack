"""Routing/delegation instructions and the skills they actually ship."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
IMPORTED = ("grill-with-docs", "wayfinder", "domain-modeling", "research", "prototype", "handoff", "setup-matt-pocock-skills")
RESOURCES = (
    "domain-modeling/GLOSSARY-FORMAT.md", "domain-modeling/ADR-FORMAT.md",
    "prototype/LOGIC.md", "prototype/UI.md",
    "setup-matt-pocock-skills/issue-tracker-local.md",
    "setup-matt-pocock-skills/issue-tracker-github.md",
    "setup-matt-pocock-skills/issue-tracker-gitlab.md",
    "setup-matt-pocock-skills/domain.md",
    "setup-matt-pocock-skills/triage-labels.md",
)


def hook_context(event="UserPromptSubmit", role=None):
    payload = {"hook_event_name": event, "cwd": str(ROOT), "prompt": "Keep this request intact."}
    if role:
        payload["agent_type"] = role
    result = subprocess.run(
        ["node", str(ROOT / "hooks/stack.js")], input=json.dumps(payload),
        capture_output=True, text=True, cwd=ROOT, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"].lower()


@pytest.mark.parametrize("relative", ["assets/global-stack-policy.md", "skills/kiss-chris-stack/SKILL.md"])
def test_orchestrator_distinguishes_direct_clear_unclear_and_large_work(relative):
    content = (ROOT / relative).read_text(encoding="utf-8").lower()
    assert re.search(r"(?:tiny|small|minor|minimal)[^.\n]*(?:direct|without|no )", content)
    assert re.search(r"(?:clear|unambiguous)[^.\n]*goal", content)
    assert re.search(r"(?:unclear|ambiguous)[^.\n]*grill-with-docs", content)
    assert re.search(r"(?:large|big)[^.\n]*wayfinder", content)
    assert "parallel" in content and "ticket" in content
    assert "plan-mode" in content, "Stack routing retains independent configured goal approval"


def test_hook_routes_before_stack_readiness_and_keeps_original_request():
    context = hook_context()
    assert "grill-with-docs" in context and "wayfinder" in context
    assert "direct" in context and "runtime readiness" in context
    assert context.index("direct") < context.index("runtime readiness"), "Select the direct path before instructing every task to run setup"
    assert "keep this request intact." in context
    assert re.search(r"direct[^.\n]*(?:without|no|skip)[^.\n]*(?:setup|goal)", context)
    assert "onboarding" in context and context.index("onboarding") < context.index("direct")


def test_all_information_collection_uses_facts_only_luna_low_agents():
    content = (ROOT / "assets/global-stack-policy.md").read_text(encoding="utf-8").lower()
    assert "gpt-6-luna" in content and re.search(r"reasoning[^.\n]*low", content)
    assert "fork_turns" in content or re.search(r"fresh[^.\n]*context", content)
    assert re.search(r"(?:all|every|always)[^.\n]*(?:context|information|fact)[^.\n]*(?:collect|gather)|(?:all|every|always)[^.\n]*(?:collect|gather)[^.\n]*(?:context|information|fact)", content)
    assert "grill-me" in content and "goal" in content
    assert re.search(r"(?:no|never|do not|must not)[^.\n]*(?:design|speculat|implementation decisions)", content)
    assert re.search(r"(?:no|never|do not|must not)[^.\n]*(?:source|code|configuration)[^.\n]*(?:edit|chang)|(?:no|never|do not|must not)[^.\n]*(?:edit|chang)[^.\n]*(?:source|code|configuration)", content)
    assert re.search(r"(?:no|never|do not|must not)[^.\n]*(?:fallback|substitut)", content)
    assert "source" in content and ("reference" in content or "citation" in content)


@pytest.mark.parametrize("role", ["context-research", "direct-worker"])
def test_subagent_hook_supports_pre_goal_research_and_direct_work_without_recursive_setup(role):
    context = hook_context("SubagentStart", role)
    assert "direct" in context and "context" in context
    assert "facts" in context or "evidence" in context
    assert "do not register another goal, run setup" in context
    assert "recursive" in context


def test_wayfinder_ticket_execution_preserves_dependency_frontier_and_permissions():
    policy = (ROOT / "assets/global-stack-policy.md").read_text(encoding="utf-8").lower()
    wayfinder = ROOT / "skills/wayfinder/SKILL.md"
    assert wayfinder.is_file(), "Ship the workflow selected for large work"
    content = policy + "\n" + wayfinder.read_text(encoding="utf-8").lower()
    assert "unblocked" in content or "dependency-ready" in content
    assert "parallel" in content and ("concurrency" in content or "slots" in content)
    assert "claim" in content and "block" in content
    assert "failed" in content or "failure" in content
    assert "local" in content and "markdown" in content
    assert "external" in content and ("authorization" in content or "permission" in content)
    assert "goal" in content and ("textual" in content or "unregistered" in content), "Single-native-goal hosts must not invent registered ticket goals"


def test_imported_skill_dependency_closure_is_discoverable_and_integrity_checked():
    manifest = json.loads((ROOT / "assets/bundle-manifest.json").read_text(encoding="utf-8"))["sha256"]
    for name in (*IMPORTED, "grilling"):
        relative = f"skills/{name}/SKILL.md"
        path = ROOT / relative
        assert path.is_file(), f"Missing transitive skill: {name}"
        content = path.read_text(encoding="utf-8")
        assert re.search(rf"(?m)^name:\s*{re.escape(name)}\s*$", content)
        assert re.search(r"(?m)^description:\s*\S", content)
        assert manifest.get(relative) == hashlib.sha256(path.read_bytes()).hexdigest(), relative
    for resource in RESOURCES:
        relative = f"skills/{resource}"
        path = ROOT / relative
        assert path.is_file(), f"Missing transitive resource: {resource}"
        assert manifest.get(relative) == hashlib.sha256(path.read_bytes()).hexdigest(), relative


def test_imported_skills_preserve_upstream_license_and_pinned_provenance():
    provenance = (ROOT / "docs/THIRD-PARTY.md").read_text(encoding="utf-8")
    versions = json.dumps(json.loads((ROOT / "assets/versions.json").read_text(encoding="utf-8")))
    assert "https://github.com/mattpocock/skills" in versions
    assert "4ae2317ddb22b046e26455e4f9c9b3aaaf62212d" in versions
    for name in IMPORTED:
        assert name in provenance, f"Identify upstream and adaptation for {name}"
    licenses = list((ROOT / "licenses").glob("*LICENSE*"))
    assert any("Matt Pocock" in path.read_text(encoding="utf-8") and "MIT License" in path.read_text(encoding="utf-8") for path in licenses)


def test_repository_enables_new_routing_switches_by_default():
    config = json.loads((ROOT / "kiss-chris-stack.config.json").read_text(encoding="utf-8"))
    assert config.get("grill-with-docs") is True
    assert config.get("wayfinder") is True
