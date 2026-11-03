"""Contracts for native /init and project instruction cleanup during setup."""

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]


def setup():
    return (ROOT / "skills/setup/SKILL.md").read_text(encoding="utf-8").lower()


def instruction_phase():
    text = setup()
    phase = text.split("### module research and synthesis", 1)[1].split("## initialization completion", 1)[0]
    assert "/init" in phase, "Run native /init after module documentation and before initialization completion"
    return phase


def test_native_init_is_an_end_of_setup_step_before_marker_and_staging():
    phase = instruction_phase()
    assert re.search(r"(?:after|once)[^\n]*(?:documentation|synthesis)", phase)
    assert re.search(r"(?:first-time|initialization)[^\n]*(?:explicit|/setup)", phase)
    assert re.search(r"(?:root|main agent)[^\n]*(?:review|optimiz|edit|refine)", phase)
    assert re.search(r"(?:before|block)[^\n]*(?:marker|configuration|staging|completion)", phase)
    assert "runtime-readiness section only" in setup(), "Ordinary readiness must not rerun instruction generation"


def test_init_uses_the_host_native_command_in_the_selected_project():
    phase = instruction_phase()
    assert re.search(r"(?:host|native)[^\n]*/init|/init[^\n]*(?:host|native)", phase)
    assert re.search(r"(?:selected|intended|project)[ -]*(?:project[ -]*)?(?:directory|root|path)", phase)
    assert re.search(r"(?:never|do not|not)[^\n]*(?:shell|codex init|exec)", phase), "A slash command is not an invented executable"


def test_missing_native_dispatch_cannot_be_reported_as_success():
    phase = instruction_phase()
    assert re.search(r"(?:unavailable|unsupported|cannot|missing)[^\n]*(?:host|dispatch|native|/init)|(?:host|dispatch|native)[^\n]*(?:unavailable|unsupported|cannot|missing)", phase)
    assert re.search(r"(?:pending|block|incomplete)[^\n]*(?:completion|marker|staging|setup)|(?:completion|marker|staging|setup)[^\n]*(?:pending|block|incomplete)", phase)
    assert re.search(r"(?:report|explain|tell)[^\n]*(?:pending|block|unavailable|manual|/init)", phase)
    assert re.search(r"(?:never|do not|not)[^\n]*(?:claim|pretend|success|completed|complete)", phase)


def test_existing_agents_is_reused_and_unique_guidance_and_instruction_scopes_survive():
    phase = instruction_phase()
    assert "agents.md" in phase and "agents.override.md" in phase
    assert re.search(r"(?:existing|already)[^\n]*(?:no-op|noop|refus|skip|reuse)", phase)
    assert re.search(r"(?:never|do not)[^\n]*(?:delet|remov)[^\n]*(?:force|/init|regenerat)", phase)
    assert re.search(r"(?:preserve|retain)[^\n]*(?:unique|valid|project-specific)[^\n]*(?:guidance|instructions|rules)", phase)
    for boundary in ("managed", "override", "nested", "global"):
        assert boundary in phase, f"Preserve {boundary} instruction boundaries"
    assert re.search(r"(?:shadow|precedence|takes priority|instead of|overrides)", phase), "A same-directory override can shadow AGENTS.md"


def test_root_refines_concise_evidence_backed_instructions_without_copying_docs():
    phase = instruction_phase()
    assert "english" in phase
    assert re.search(r"(?:concise|brief|short)[^\n]*(?:actionable|specific|instructions|guidance)", phase)
    assert "docs/" in phase and "agent-traces/" in phase
    assert re.search(r"(?:link|reference)[^\n]*(?:docs/|documentation|canonical)", phase)
    assert re.search(r"(?:duplicate|duplicated|repeated)[^\n]*(?:inherited|policy|rules)|(?:inherited|policy)[^\n]*(?:duplicate|duplicated|repeated)", phase)
    assert "boilerplate" in phase and "architecture" in phase
    assert re.search(r"(?:stale|unsupported)[^\n]*(?:evidence|verif|claim)|(?:evidence|verif)[^\n]*(?:stale|unsupported)", phase)
    assert re.search(r"(?:idempotent|rerun|repeated run|unchanged)", phase)


def test_agents_is_an_exact_git_candidate_with_mixed_file_protection():
    text = setup()
    workflow = text.split("## git hygiene and staging", 1)[1].split("\n## ", 1)[0]
    eligible = workflow.split("eligible exact files", 1)[1].split("\n4.", 1)[0]
    assert "`agents.md`" in eligible, "Include the actual project-root instruction file among eligible exact setup paths"
    mixed = workflow.split("**preserve mixed work:**", 1)[1].split("\n5.", 1)[0]
    assert "agents.md" in mixed, "Existing dirty or partially staged instruction files must retain their index entry"
    assert "skip" in mixed and "index" in mixed
    assert "--literal-pathspecs" in mixed
