"""Static CI contract; hosted runner execution is separate evidence."""
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_push_trigger_includes_feature_branches_without_a_pull_request():
    text = (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    triggers = text.split("permissions:", 1)[0]
    assert re.search(r"^  push:\s*$", triggers, re.MULTILINE), "Feature branch pushes must run ordinary CI"
    assert not re.search(r"^    (?:branches|branches-ignore|tags|tags-ignore|paths|paths-ignore):", triggers, re.MULTILINE)


def test_ci_bootstraps_windows_and_linux_for_full_unprivileged_suite():
    path = ROOT / ".github/workflows/tests.yml"
    assert path.is_file(), "Provide repeatable CI for the full existing suite"
    text = path.read_text(encoding="utf-8")
    for required in ("pull_request", "push", "ubuntu-latest", "windows-latest", "matrix", "setup-python@", "setup-node@", "setup-uv@"):
        assert required in text, f"CI must include {required}"
    assert re.search(r"runs-on:\s*\$\{\{\s*matrix\.", text)
    assert re.search(r"uv run --with pytest python -m pytest tests -q", text)
    assert "--offline" not in text, "A clean runner must bootstrap dependencies"
    assert "contents: read" in text
    for forbidden in ("secrets.", "pull_request_target", "write-all", "--live", "dangerously", "skip-trust"):
        assert forbidden not in text, f"Ordinary CI must not require {forbidden}"
