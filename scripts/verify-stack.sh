#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v python3 >/dev/null 2>&1; then python_command=python3
elif command -v python >/dev/null 2>&1; then python_command=python
else printf 'Python 3.10+ is required for the bundled setup checker.\n' >&2; exit 1
fi
"$python_command" "$ROOT/scripts/setup-runtime.py" --project "${1:-$PWD}"
printf 'Runtime checks passed; actual session CodeGraph MCP visibility must still be verified.\n'
