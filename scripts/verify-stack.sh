#!/usr/bin/env bash
set -euo pipefail

PROJECT="${1:-$PWD}"
failed=0
for command_name in uv ouroboros ooo codegraph rtk uipro; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'OK  %s\n' "$command_name"
  else
    printf 'ERR %s not found\n' "$command_name"
    failed=1
  fi
done

if command -v ouroboros >/dev/null 2>&1; then
  ouroboros mcp doctor || failed=1
  ouroboros_python="$(uv tool dir)/ouroboros-ai/bin/python"
  if [[ -x "$ouroboros_python" ]]; then
    "$ouroboros_python" "$(dirname "$0")/patch-dashboard-picker.py" --check || failed=1
    "$ouroboros_python" "$(dirname "$0")/verify-deep-path-config.py" || failed=1
    dashboard_url="$($ouroboros_python -c 'from ouroboros.dashboard_web import dashboard_base_url; print(dashboard_base_url())' | tail -n 1)"
    api_url="$(printf '%s' "$dashboard_url" | sed -E 's#^(https?://(\[[^]]+\](:[0-9]+)?|[^/?]+)).*#\1/api/runs#')"
    curl -fsS --max-time 5 "$api_url" | grep -q '"runs"[[:space:]]*:' || { printf 'ERR Ouroboros dashboard run picker unavailable\n'; failed=1; }
  else
    printf 'ERR Ouroboros tool Python missing\n'
    failed=1
  fi
else
  failed=1
fi
command -v codegraph >/dev/null 2>&1 && codegraph status "$PROJECT" || failed=1

if command -v codex >/dev/null 2>&1; then
  mcp="$(codex mcp list 2>&1 || true)"
  grep -q '^ouroboros[[:space:]]' <<<"$mcp" || { printf 'ERR Codex MCP missing: ouroboros\n'; failed=1; }
  grep -q '^codegraph[[:space:]]' <<<"$mcp" || { printf 'ERR Codex MCP missing: codegraph\n'; failed=1; }
  plugins="$(codex plugin list 2>&1 || true)"
  grep -q ouroboros <<<"$plugins" || { printf 'ERR Codex Ouroboros plugin missing\n'; failed=1; }
  grep -q ponytail <<<"$plugins" || { printf 'ERR Codex Ponytail plugin missing\n'; failed=1; }
  codex_home="${CODEX_HOME:-$HOME/.codex}"
  grep -q 'meta.job_observer' "$codex_home/AGENTS.md" 2>/dev/null && grep -q 'ui-ux-pro-max' "$codex_home/AGENTS.md" 2>/dev/null || { printf 'ERR Codex global stack policy missing\n'; failed=1; }
  [[ -f "$HOME/.agents/skills/ui-ux-pro-max/SKILL.md" ]] || { printf 'ERR UI-UX-Pro-Max skill missing for Codex\n'; failed=1; }
fi
if command -v claude >/dev/null 2>&1; then
  mcp="$(claude mcp list 2>&1 || true)"
  grep -q ouroboros <<<"$mcp" || { printf 'ERR Claude MCP missing: ouroboros\n'; failed=1; }
  grep -q codegraph <<<"$mcp" || { printf 'ERR Claude MCP missing: codegraph\n'; failed=1; }
  plugins="$(claude plugin list 2>&1 || true)"
  grep -q ouroboros <<<"$plugins" || { printf 'ERR Claude plugin missing: ouroboros\n'; failed=1; }
  grep -q ponytail <<<"$plugins" || { printf 'ERR Claude plugin missing: ponytail\n'; failed=1; }
  claude_home="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
  grep -q 'meta.job_observer' "$claude_home/CLAUDE.md" 2>/dev/null || { printf 'ERR Claude global stack policy missing\n'; failed=1; }
  [[ -f "$claude_home/skills/ui-ux-pro-max/SKILL.md" ]] || { printf 'ERR UI-UX-Pro-Max skill missing for Claude Code\n'; failed=1; }
fi

[[ -f "$HOME/.agents/skills/kiss-chris-stack/SKILL.md" ]] || { printf 'ERR KISS-Chris-Stack skill missing\n'; failed=1; }
[[ -f "$HOME/.agents/skills/kiss-chris-stack/scripts/open-dashboard.sh" ]] || { printf 'ERR Dashboard browser launcher missing\n'; failed=1; }
[[ -f "$PROJECT/.ouroboros/mechanical.toml" ]] || { printf 'ERR Ouroboros mechanical gates missing\n'; failed=1; }

(( failed == 0 )) || exit 1
printf 'Stack verification passed.\n'
