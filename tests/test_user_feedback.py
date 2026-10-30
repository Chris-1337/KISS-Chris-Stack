"""Contracts for recording feedback and applying it to later project goals."""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
FEEDBACK = "agent-traces/user-feedback/"


def read(name):
    return (ROOT / name).read_text(encoding="utf-8").lower()


def test_shared_policy_requires_persistence_review_and_role_handoff():
    policy = read("assets/global-stack-policy.md")
    assert FEEDBACK in policy, "Feedback needs a canonical project-local destination"
    assert re.search(r"(?:persist|record|save)[^\n]*feedback", policy)
    assert re.search(r"(?:negative|correction)[^\n]*feedback|feedback[^\n]*(?:negative|correction)", policy)
    assert re.search(r"before[^\n]*goal[^\n]*feedback|feedback[^\n]*before[^\n]*goal", policy)
    assert re.search(r"feedback[^\n]*(?:acceptance|check)|(?:acceptance|check)[^\n]*feedback", policy)
    assert re.search(r"(?:agent|role)[^\n]*feedback|feedback[^\n]*(?:agent|role)", policy)


def test_feedback_protocol_is_actionable_scoped_and_preserves_history():
    protocol = read(FEEDBACK + "README.md")
    for concept in ("date", "context", "scope", "behavior", "action", "verification"):
        assert concept in protocol, f"Feedback records need {concept}"
    assert re.search(r"(?:repeat|duplicate)[^\n]*(?:existing|same)|(?:existing|same)[^\n]*(?:repeat|duplicate)", protocol)
    assert "history" in protocol and re.search(r"(?:correct|supersed)", protocol)
    assert "secret" in protocol and re.search(r"(?:raw|transcript)", protocol)
    assert "project" in protocol and re.search(r"(?:permission|authorization)", protocol)
    assert re.search(r"(?:pending|unverified|not verified)", protocol)


def test_setup_bootstraps_feedback_without_rewriting_or_inventing_entries():
    setup = read("skills/setup/SKILL.md")
    bootstrap = setup.split("## documentation bootstrap", 1)[1].split("## initialization completion", 1)[0]
    assert FEEDBACK in bootstrap, "First-time and explicit setup need the feedback structure"
    assert re.search(r"(?:create|missing)[^\n]*user-feedback|user-feedback[^\n]*(?:create|missing)", bootstrap)
    assert "preserve" in bootstrap and re.search(r"(?:not invent|never invent|no fabricated|do not fabricate)", bootstrap)
    assert "must not duplicate" in bootstrap or "must not" in bootstrap and "rewrite" in bootstrap
    assert "do not reinitialize" in setup, "Feedback must not change initialized-project routing"


def test_feedback_is_discoverable_and_used_by_orchestrator():
    orchestrator = read("skills/kiss-chris-stack/SKILL.md")
    assert FEEDBACK in orchestrator
    assert re.search(r"feedback[^\n]*(?:goal|register)|(?:goal|register)[^\n]*feedback", orchestrator)
    assert re.search(r"feedback[^\n]*(?:agent|role)|(?:agent|role)[^\n]*feedback", orchestrator)
    for name in ("README.md", "docs/ARCHITEKTUR.md"):
        assert "user-feedback" in read(name), f"{name} must expose the feedback workflow"


def test_initial_feedback_records_real_requirement_and_skill_hashes_match():
    records = list((ROOT / FEEDBACK).glob("2026-10-30-*.md"))
    assert records, "Persist the actual request without inventing a past failure"
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in records)
    assert "2026-10-30" in text and "feedback" in text
    assert re.search(r"(?:request|requirement)", text)
    assert re.search(r"(?:repeat|recurr|prevent)", text)
    manifest = json.loads((ROOT / "assets/bundle-manifest.json").read_text(encoding="utf-8"))["sha256"]
    for name in ("skills/setup/SKILL.md", "skills/kiss-chris-stack/SKILL.md"):
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == manifest[name], name
