"""Lifecycle instruction contracts, not a simulated incident or evidence engine."""

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]


def read(relative):
    path = ROOT / relative
    assert path.is_file(), f"Missing lifecycle guidance: {relative}"
    return path.read_text(encoding="utf-8").lower()


def require_topics(text, *alternatives):
    for terms in alternatives:
        assert any(term in text for term in terms), f"Missing contract topic: {terms}"


def section(text, heading_pattern):
    """Include child headings while excluding unrelated sibling sections."""
    headings = list(re.finditer(r"(?m)^(#{1,6}) (.+)$", text))
    for index, heading in enumerate(headings):
        if re.search(heading_pattern, heading[2]):
            end = next((other.start() for other in headings[index + 1:]
                        if len(other[1]) <= len(heading[1])), len(text))
            return text[heading.start():end]
    raise AssertionError(f"Missing guidance section: {heading_pattern}")


def test_security_applicability_carries_risks_and_checks_through_existing_lifecycle():
    policy = read("assets/global-stack-policy.md")
    security = section(policy, r"security|risk-based")
    require_topics(
        security, ("applicab", "proportionate"), ("secret",), ("user data", "personal data"),
        ("trust",), ("permission",), ("exposed", "interface"), ("dependenc", "supply chain"),
        ("migration",), ("irreversib", "data loss"), ("availability",),
        ("asset",), ("abuse", "threat"), ("mitigat",), ("verif", "check"),
        ("discover", "design"), ("implement",), ("deliver", "release"), ("maintenan",),
        ("goal",), ("existing role", "existing test", "existing stack"),
        ("inapplicab", "not applicable"), ("sonar",), ("provenance", "integrity"),
    )
    # Preserve the benign-doc versus sensitive-short-change routing distinction.
    require_topics(policy, ("trust boundaries",), ("data migration",), ("need the stack",))
    direct = next(line for line in policy.splitlines() if "**direct:**" in line)
    assert all(term in direct for term in ("low-risk", "no setup", "interview"))
    assert re.search(r"(?:no|never|do not)[^.\n]*(?:certif|guarantee)|(?:cannot|does not)[^.\n]*(?:certif|guarantee)", security)


@pytest.mark.parametrize("relative", ["skills/kiss-chris-stack/SKILL.md", "skills/evaluate/SKILL.md"])
def test_goal_and_independent_evaluation_apply_security_without_new_roles(relative):
    text = read(relative)
    security = section(text, r"security|risk-based")
    require_topics(security, ("global-stack-policy.md",), ("applicab",), ("mitigat",),
                   ("verif", "check"), ("existing",), ("inapplicab", "not applicable"))
    require_topics(text, ("disabled/skipped", "skipped, not passed"), ("sonarqube",), ("live",))


def test_operations_handoff_has_observable_recovery_and_honest_ownership_limits():
    operations = read("docs/OPERATIONS.md")
    handoff = section(operations, r"handoff|operational record")
    require_topics(handoff, ("owner",), ("contact",), ("unknown",), ("target",), ("configur",),
                   ("health",), ("failure", "abort"), ("observab", "log"), ("redact",),
                   ("backup",), ("restore",), ("limit",), ("recover",), ("maintenan",),
                   ("dependenc",), ("sla", "response-time"))
    require_topics(operations, ("sonarqube.md",), ("delivery.md",), ("security.md",),
                   ("evaluation-config.py",), ("check-release.py",), ("unverified", "does not prove"))


def test_incident_walkthroughs_preserve_evidence_and_authorization_boundaries():
    operations = read("docs/OPERATIONS.md")
    incident = section(operations, r"incident")
    require_topics(incident, ("triage",), ("preserv",), ("redact",), ("contain",), ("authoriz",),
                   ("recover",), ("verif",), ("communicat",), ("follow-up", "follow up"),
                   ("public",), ("permission", "authoriz"))
    stopped = section(operations, r"stopped.*service|service.*stop|unavailable.*service")
    require_topics(stopped, ("identity", "target"), ("read-only",), ("authoriz",),
                   ("volume", "data"), ("gate",), ("block",), ("health",), ("functional", "workflow"))
    release = section(operations, r"failed.*release|release.*fail|failed.*revert")
    require_topics(release, ("abort",), ("candidate",), ("preserv",), ("authoriz",),
                   ("rollback", "forward recovery"), ("verif",), ("data",), ("limit", "unverified", "cannot"))
    exposure = section(operations, r"credential.*expos|expos.*credential|suspected.*credential")
    require_topics(exposure, ("redact",), ("revok", "rotat"), ("authoriz",),
                   ("private",), ("preserv",), ("verif",), ("follow-up", "follow up"))


def test_private_reporting_does_not_imply_permission_to_change_credentials_or_publish():
    security = read("SECURITY.md")
    require_topics(security, ("private vulnerability reporting",), ("public issue",),
                   ("credential",), ("authoriz", "permission"), ("operations.md",),
                   ("redact", "unredacted"), ("does not invalidate", "does not revoke"),
                   ("normal trust",), ("response-time guarantee",))


@pytest.mark.parametrize("relative", [
    "assets/global-stack-policy.md", "skills/kiss-chris-stack/SKILL.md",
    "skills/evaluate/SKILL.md", "skills/wayfinder/SKILL.md",
])
def test_existing_roles_carry_source_bound_criterion_evidence(relative):
    text = read(relative)
    evidence = section(text, r"traceab|evidence.*mapping|criterion.*evidence")
    require_topics(evidence, ("criterion", "criteria"), ("assert",), ("source",),
                   ("fingerprint",), ("evidence",), ("release", "candidate"),
                   ("failed", "failure"), ("disabled/skipped",), ("inapplicab",),
                   ("unknown", "unverified"), ("stale",), ("lifecycle.md",))


def test_lifecycle_matrix_distinguishes_execution_assertions_and_current_source():
    lifecycle = read("docs/LIFECYCLE.md")
    evidence = section(lifecycle, r"traceab|evidence|acceptance")
    require_topics(evidence, ("criterion", "criteria"), ("command",), ("assert",),
                   ("result", "status"), ("fingerprint",), ("evidence",),
                   ("release", "candidate"), ("--expect-source",), ("check-release.py",),
                   ("test-host-workflows.py",), ("stale",), ("missing assertion", "no assertion"),
                   ("failed",), ("disabled/skipped",), ("inapplicab",), ("unknown", "unverified"))


def test_compatibility_and_overhead_guidance_keeps_missing_observations_unknown():
    lifecycle = read("docs/LIFECYCLE.md")
    compatibility = section(lifecycle, r"compatib|overhead")
    require_topics(compatibility, ("host",), ("runtime",), ("model",), ("supported",),
                   ("observed",), ("unverified",), ("windows",), ("linux",), ("ci",),
                   ("native",), ("cli",), ("failed",), ("hook",), ("elapsed",),
                   ("usage", "token"), ("missing",), ("unknown",), ("currency",),
                   ("baseline",), ("saving",), ("host-tests.md",))


def test_retirement_guidance_separates_plugin_removal_from_downstream_decommissioning():
    lifecycle = read("docs/LIFECYCLE.md")
    retirement = section(lifecycle, r"retire|decommission")
    require_topics(retirement, ("plugin",), ("downstream",), ("owner",), ("authoriz",),
                   ("consumer",), ("integration",), ("deprecat", "migration"), ("notice",),
                   ("retention",), ("access",), ("legal",), ("credential",), ("job",),
                   ("hook",), ("backup",), ("recovery",), ("independent",), ("verif",),
                   ("preserv",), ("project",), ("data",), ("history",), ("shared",),
                   ("cache",), ("mcp",), ("global",), ("destructive",))
