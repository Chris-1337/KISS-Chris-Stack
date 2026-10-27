#!/usr/bin/env python3
"""Apply the bounded Ouroboros dashboard progress-link hotfix."""

from __future__ import annotations

import argparse
import importlib.util
import os
import tempfile
from pathlib import Path


OLD = 'f"{PICKER_CANONICAL_LINK_ID_SQL} AS link_id, "'
NEW = '"aggregate_id AS link_id, "'


def reader_path() -> Path:
    spec = importlib.util.find_spec("ouroboros.dashboard_web.reader")
    if spec is None or spec.origin is None:
        raise SystemExit("ERROR: installed Ouroboros dashboard reader was not found")
    return Path(spec.origin)


def patch_reader(path: Path, *, check: bool = False) -> bool:
    source = path.read_text(encoding="utf-8")
    start = source.find("def _fetch_latest_progress_rows(")
    end = source.find("\ndef list_recent_executions(", start)
    if start < 0 or end < 0:
        raise SystemExit(f"ERROR: unsupported Ouroboros dashboard reader: {path}")
    function = source[start:end]
    if NEW in function and OLD not in function:
        return False
    if function.count(OLD) != 1:
        raise SystemExit(f"ERROR: unsupported Ouroboros dashboard progress query: {path}")
    updated = source[:start] + function.replace(OLD, NEW, 1) + source[end:]
    compile(updated, str(path), "exec")
    if check:
        raise SystemExit(f"ERROR: Ouroboros dashboard picker hotfix is missing: {path}")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(updated)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reader", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = args.reader or reader_path()
    changed = patch_reader(path, check=args.check)
    print(f"Dashboard picker hotfix {'applied' if changed else 'verified'}: {path}")


if __name__ == "__main__":
    main()
