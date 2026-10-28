import os
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
POLICY = ROOT / "assets" / "global-stack-policy.md"
BEGIN = "<!-- kiss-chris-stack:start -->"
END = "<!-- kiss-chris-stack:end -->"


def _run(command: list[str]) -> None:
    subprocess.run(command, check=True, cwd=ROOT)


def _bash_path(path: Path) -> str:
    path = path.resolve()
    if os.name != "nt":
        return str(path)
    return f"/mnt/{path.drive[0].lower()}{path.as_posix()[2:]}"


def _assert_managed_update(path: Path, update) -> None:
    before = "# recipient settings\ncustom = keep\n\n"
    after = "\n\n# recipient footer\nfooter = keep\n"
    path.write_bytes(f"{before}{BEGIN}\nstale policy\n{END}{after}".encode())

    update()
    first = path.read_bytes()
    update()
    second = path.read_bytes()

    assert first == second
    text = first.decode()
    assert text.startswith(before)
    assert text.endswith(after)
    assert text.count(BEGIN) == text.count(END) == 1
    block = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    assert block == POLICY.read_text(encoding="utf-8").strip()


def test_policy_is_shared_and_retains_goal_tools_and_context():
    policy = POLICY.read_text(encoding="utf-8")
    assert all(tool in policy for tool in ("get_goal", "create_goal", "update_goal", "token_budget"))
    assert all(context in policy for context in ("docs/", "agent-traces/", "Ponytail", "ui-ux-pro-max"))
    assert "/goal" in policy and "/setup" in policy
    for name in ("AGENTS.md", "skills/kiss-chris-stack/SKILL.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "global-stack-policy.md" in text, f"{name} must route to the shared policy"
    assert len(policy.splitlines()) <= 85, "Keep the common policy concise"


def test_setup_skill_is_explicitly_and_implicitly_discoverable():
    skill = ROOT / "skills" / "setup"
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert re.search(r"(?m)^name:\s*setup\s*$", text)
    assert "docs/" in text and "agent-traces/" in text
    assert "allow_implicit_invocation: true" in (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "setup/SKILL.md" in (ROOT / "skills" / "kiss-chris-stack" / "SKILL.md").read_text(encoding="utf-8")


def test_powershell_managed_block_is_idempotent_and_preserves_foreign_content(tmp_path):
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell, "PowerShell is required to verify the PowerShell installer helper"
    target = tmp_path / "AGENTS.md"
    script = ROOT / "scripts" / "upsert-managed-block.ps1"
    _assert_managed_update(
        target,
        lambda: _run([powershell, "-NoProfile", "-File", str(script), "-Path", str(target), "-PolicyPath", str(POLICY)]),
    )


def test_shell_managed_block_is_idempotent_and_preserves_foreign_content(tmp_path):
    bash = shutil.which("bash")
    assert bash, "bash is required to verify the POSIX installer helper"
    target = tmp_path / "CLAUDE.md"
    script = ROOT / "scripts" / "upsert-managed-block.sh"
    _assert_managed_update(
        target,
        lambda: _run([bash, _bash_path(script), _bash_path(target), _bash_path(POLICY)]),
    )


def test_distributable_sources_contain_no_secrets_or_local_user_paths():
    secret = re.compile(
        r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*[\"'][^$<{\"']+"
    )
    local_path = re.compile(r"(?i)[A-Z]:\\Users\\[^$%<{\\]+|/home/[a-z0-9._-]+")
    files = [ROOT / "AGENTS.md", ROOT / "README.md"]
    for directory in ("agents", "assets", "docs", "references", "scripts", "skills"):
        files.extend(path for path in (ROOT / directory).rglob("*") if path.is_file() and path.suffix in (".md", ".py", ".js", ".ps1", ".sh", ".json", ".yaml", ".yml", ".toml", ".csv"))

    for path in files:
        content = path.read_text(encoding="utf-8")
        assert not secret.search(content), f"Possible hard-coded secret in {path.relative_to(ROOT)}"
        # Upstream UIUX datasets contain intentional bad-code examples; hashes verify these unchanged resources separately.
        if not path.is_relative_to(ROOT / "skills" / "ui-ux-pro-max" / "data"):
            assert not local_path.search(content), f"Non-portable user path in {path.relative_to(ROOT)}"


def test_product_onboarding_covers_required_topics_and_is_installed():
    document = (ROOT / "docs" / "PRODUKT-ONBOARDING.md").read_text(encoding="utf-8")
    required = (
        "What is it?",
        "Responsibilities",
        "Quick start",
        "Architecture diagram",
        "Usage",
        "Purpose",
        "Release status",
        "Distribution",
        "Training and onboarding",
        "Operating model",
        "Features",
        "Limits",
    )
    assert all(topic in document for topic in required)
    assert "```mermaid" in document


def test_language_policy_covers_future_documentation_and_prompt_language():
    policy = POLICY.read_text(encoding="utf-8")
    assert re.search(r"(?i)documentation[^\n]*English", policy)
    assert re.search(r"(?i)future[^\n]*documentation|documentation[^\n]*future", policy)
    assert "docs/" in policy and "agent-traces/" in policy
    assert re.search(r"(?i)reasoning[^\n]*English", policy)
    assert re.search(r"(?i)(communicat|respond|repl)[^\n]*language[^\n]*prompt", policy)


def test_first_party_documentation_has_no_remaining_german_prose():
    files = [ROOT / name for name in ("AGENTS.md", "README.md", "SKILL.md", "assets/global-stack-policy.md", "references/stack-policy.md")]
    for directory in ("docs", "agent-traces"):
        files.extend((ROOT / directory).rglob("*.md"))
    # A regression guard for the translated prose; preserve existing paths and upstream examples.
    german = re.compile(r"\b(?:und|fuer|prüft|prueft|enthält|enthaelt|Warum|Grenzen|Dokumentation|Nutzerauftrag|gemeinsame|vorhandene|bereits|keine)\b", re.I)
    for path in files:
        text = path.read_text(encoding="utf-8")
        prose = re.sub(r"`[^`]*`|\]\([^)]*\)", "", text)
        assert not german.search(prose), f"Untranslated prose in {path.relative_to(ROOT)}"


def test_product_brand_and_skill_id_are_kiss_chris_stack():
    assert "# KISS-Chris-Stack" in (ROOT / "README.md").read_text(encoding="utf-8")
    assert "# KISS-Chris-Stack" in (ROOT / "skills" / "kiss-chris-stack" / "SKILL.md").read_text(encoding="utf-8")
    assert 'display_name: "KISS-Chris-Stack"' in (ROOT / "skills" / "kiss-chris-stack" / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "# KISS-Chris-Stack" in (ROOT / "docs" / "PRODUKT-ONBOARDING.md").read_text(encoding="utf-8")
    assert "name: kiss-chris-stack" in (ROOT / "skills" / "kiss-chris-stack" / "SKILL.md").read_text(encoding="utf-8")



def test_distribution_uses_only_the_remaining_stack():
    forbidden = re.compile(r"ouroboros|(?:fast|deep)[ -]?(path|track)|ooo setup|meta\.job_observer", re.I)
    files = [ROOT / "AGENTS.md", ROOT / "README.md"]
    for directory in ("agents", "assets", "docs", "references", "scripts", "skills"):
        files.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and p.suffix in (".md", ".py", ".js", ".ps1", ".sh", ".json", ".yaml", ".yml", ".toml", ".csv"))
    for path in files:
        assert not forbidden.search(path.name), path
        assert not forbidden.search(path.read_text(encoding="utf-8")), path
