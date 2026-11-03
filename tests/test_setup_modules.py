"""Contracts for setup's module research and root documentation synthesis."""

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]


def setup_documentation():
    setup = (ROOT / "skills/setup/SKILL.md").read_text(encoding="utf-8").lower()
    return setup.split("## documentation bootstrap", 1)[1].split("## initialization completion", 1)[0]


def test_module_research_follows_the_system_architecture_and_covers_real_modules():
    documentation = setup_documentation()
    assert re.search(r"(?:after|once)[^.\n]*(?:system architecture|system overview)", documentation), "Create or reuse the system overview before module dispatch"
    assert re.search(r"(?:each|every|per)[^.\n]*module", documentation), "Cover every actual module rather than a sample"
    assert re.search(r"(?:boundar|source roots|source paths)", documentation), "Identify actual module boundaries before assigning agents"


def test_module_research_pins_one_luna_low_agent_per_module_with_bounded_dispatch():
    documentation = setup_documentation()
    assert "gpt-6-luna" in documentation
    assert re.search(r"reasoning[^.\n]*\blow\b", documentation)
    assert re.search(r"(?:one|dedicated)[^.\n]*(?:agent|sub-agent)[^.\n]*(?:each|per)[^.\n]*module|(?:each|per)[^.\n]*module[^.\n]*(?:one|dedicated)[^.\n]*(?:agent|sub-agent)", documentation)
    assert re.search(r"(?:concurren|batch|available slots)", documentation), "Host limits must not silently omit modules"


def test_research_agents_only_collect_module_evidence_and_write_module_notes():
    documentation = setup_documentation()
    assert re.search(r"(?:only|restrict|limit|confine)[^.\n]*(?:assigned module|module['’]s|module-local)", documentation), "Researchers must stay within their assigned module"
    assert re.search(r"(?:source|code)[^.\n]*(?:link|reference)|(?:link|reference)[^.\n]*(?:source|code)", documentation)
    assert re.search(r"docs/[^\s`]*module[^\s`]*", documentation), "Keep research notes and final module documents under docs"
    assert "notes" in documentation
    assert re.search(r"(?:do not|must not|never|no)[^.\n]*(?:recursive|delegate|spawn)", documentation), "Module researchers must not start another workflow"
    assert re.search(r"(?:do not|must not|never|no)[^.\n]*(?:source edits|implementation|modify code|change code)", documentation), "Research is documentation work only"
    assert re.search(r"(?:unknown|uncertain|unresolved)", documentation)
    assert "fork_turns" in documentation or re.search(r"(?:fresh|isolated)[^.\n]*context", documentation), "Do not inherit unrelated parent context"
    assert re.search(r"(?:do not|must not|never|no)[^.\n]*(?:traverse|inspect|read)[^.\n]*(?:other modules|another module|target modules)", documentation), "Record imports without following other module sources"


def test_root_waits_for_all_research_then_synthesizes_linked_module_documentation():
    documentation = setup_documentation()
    assert re.search(r"(?:wait|after|once)[^.\n]*all[^.\n]*(?:research|agent|notes)", documentation), "Root synthesis must wait for every assigned researcher"
    assert re.search(r"(?:root|main agent)[^.\n]*(?:synthes|curat|organize)", documentation)
    assert re.search(r"module[^.\n]*architecture", documentation)
    assert re.search(r"(?:responsibil|purpose)", documentation)
    assert re.search(r"(?:interface|entry point)", documentation)
    assert re.search(r"(?:dependenc|interaction)", documentation)
    assert re.search(r"(?:link|index)[^.\n]*(?:system|overview)|(?:system|overview)[^.\n]*(?:link|index)", documentation)


def test_unavailable_model_or_failed_research_prevents_false_bootstrap_success():
    documentation = setup_documentation()
    assert re.search(r"(?:unavailable|unsupported|cannot)[^.\n]*(?:model|agent|reasoning)|(?:model|agent|reasoning)[^.\n]*(?:unavailable|unsupported|cannot)", documentation)
    assert re.search(r"(?:never|do not|no)[^.\n]*(?:fallback|substitut|different model)", documentation), "Do not silently replace the requested model or effort"
    assert re.search(r"(?:failed|failure|incomplete|interrupted)[^.\n]*(?:block|stop|complete)|(?:block|stop)[^.\n]*(?:failed|failure|incomplete|interrupted)", documentation)
    assert re.search(r"(?:resume|retry|remaining|missing)[^.\n]*(?:module|research|notes)", documentation), "Retain successful module work when resuming"


def test_module_work_preserves_existing_documents_and_empty_project_routing():
    setup = (ROOT / "skills/setup/SKILL.md").read_text(encoding="utf-8").lower()
    documentation = setup_documentation()
    assert "preserve existing" in documentation
    assert "reuse their layout" in documentation
    assert "must not duplicate or rewrite" in documentation
    assert re.search(r"empty project[^.\n]*(?:no|only|skip)", documentation)
    assert re.search(r"(?:skip|no|do not)[^.\n]*(?:module agents|research agents|module research)[^.\n]*empty|empty[^.\n]*(?:skip|no|do not)[^.\n]*(?:module agents|research agents|module research)", documentation), "Empty projects must not invent module researchers"
    assert "ordinary root task with a configuration" in setup
    assert "runtime-readiness section only" in setup
    assert "failed or interrupted setup does not stage partial output" in setup


def test_delegated_hook_allows_setup_research_without_creating_an_implementation_goal():
    setup = (ROOT / "skills/setup/SKILL.md").read_text(encoding="utf-8").lower()
    introduction = setup.split("## project selection", 1)[0]
    assert "research" in introduction, "Distinguish permitted setup researchers from implementation roles"
    result = subprocess.run(
        ["node", str(ROOT / "hooks/stack.js")],
        input=json.dumps({"hook_event_name": "SubagentStart", "cwd": str(ROOT), "agent_type": "setup-module-research"}),
        capture_output=True, text=True, cwd=ROOT, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"].lower()
    assert re.search(r"(?:setup|bootstrap)[^.\n]*research|research[^.\n]*(?:setup|bootstrap)", context)
    assert re.search(r"(?:without|no|need not|does not require)[^.\n]*(?:registered )?goal|goal[^.\n]*(?:not required|unregistered)", context), "Bootstrap researchers have no implementation goal yet"
    assert "do not register another goal, run setup" in context
