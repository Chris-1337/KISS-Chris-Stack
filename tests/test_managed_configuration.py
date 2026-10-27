import os
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
POLICY = ROOT / "assets" / "global-stack-policy.md"
BEGIN = "<!-- kiss-chris-stack:start -->"
END = "<!-- kiss-chris-stack:end -->"
LEGACY_BEGIN = "<!-- ouroboros-stack:start -->"
LEGACY_END = "<!-- ouroboros-stack:end -->"


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
    path.write_bytes(f"{before}{LEGACY_BEGIN}\nstale policy\n{LEGACY_END}{after}".encode())

    update()
    first = path.read_bytes()
    update()
    second = path.read_bytes()

    assert first == second
    text = first.decode()
    assert text.startswith(before)
    assert text.endswith(after)
    assert text.count(BEGIN) == text.count(END) == 1
    assert LEGACY_BEGIN not in text
    assert "Before every implementation, formulate a strong `/goal`" in text
    assert "meta.job_observer" in text
    assert "ui-ux-pro-max" in text
    assert "ouroboros_start_execute_seed" in text
    assert "three iterations per acceptance criterion" in text
    assert "auto_evolve" in text


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
    files = [ROOT / "README.md", ROOT / "SKILL.md"]
    for directory in ("agents", "assets", "docs", "references", "scripts"):
        files.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())

    for path in files:
        content = path.read_text(encoding="utf-8")
        assert not secret.search(content), f"Possible hard-coded secret in {path.relative_to(ROOT)}"
        assert not local_path.search(content), f"Non-portable user path in {path.relative_to(ROOT)}"


def test_product_onboarding_covers_required_topics_and_is_installed():
    document = (ROOT / "docs" / "PRODUKT-ONBOARDING.md").read_text(encoding="utf-8")
    required = (
        "Was ist es?",
        "Zuständigkeit",
        "Kurzanleitung",
        "Architekturdiagramm",
        "Nutzungsweise",
        "Verwendungszweck",
        "Release-Stand",
        "Wie zur Verfügung gestellt",
        "Schulungs- und Onboarding-Konzept",
        "Betriebsmodell",
        "Features",
        "Grenzen",
    )
    assert all(topic in document for topic in required)
    assert "```mermaid" in document
    assert "'docs'" in (ROOT / "scripts" / "install-stack.ps1").read_text(encoding="utf-8")
    assert '"$ROOT/docs"' in (ROOT / "scripts" / "install-stack.sh").read_text(encoding="utf-8")


def test_product_brand_and_skill_id_are_kiss_chris_stack():
    assert "# KISS-Chris-Stack" in (ROOT / "README.md").read_text(encoding="utf-8")
    assert "# KISS-Chris-Stack" in (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert 'display_name: "KISS-Chris-Stack"' in (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "# KISS-Chris-Stack" in (ROOT / "docs" / "PRODUKT-ONBOARDING.md").read_text(encoding="utf-8")
    assert "name: kiss-chris-stack" in (ROOT / "SKILL.md").read_text(encoding="utf-8")
    installers = "\n".join(
        (ROOT / "scripts" / name).read_text(encoding="utf-8")
        for name in ("install-stack.ps1", "install-stack.sh")
    )
    assert "--skill kiss-chris-stack" in installers
    assert "kiss-chris-stack" in installers and "ouroboros-stack" in installers


def test_installers_apply_and_verifiers_check_bounded_deep_path_settings():
    settings = (
        "clarification.max_interview_rounds",
        "execution.max_iterations_per_ac",
        "execution.auto_evolve",
        "evaluation.stage3_enabled",
        "runtime_controls.generation_no_progress_timeout_seconds",
        "runtime_controls.generation_safety_timeout_seconds",
        "seed.verify_command_gate",
    )
    for name in ("install-stack.ps1", "install-stack.sh"):
        installer = (ROOT / "scripts" / name).read_text(encoding="utf-8")
        assert all(setting in installer for setting in settings)
    verifier = (ROOT / "scripts" / "verify-deep-path-config.py").read_text(encoding="utf-8")
    assert '"execution.max_iterations_per_ac": 3' in verifier
    assert '"execution.auto_evolve": False' in verifier
    assert '"runtime_controls.generation_no_progress_timeout_seconds": 900.0' in verifier
    assert '"runtime_controls.generation_safety_timeout_seconds": 3600.0' in verifier
