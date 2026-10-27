#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="${1:-$PWD}"
POLICY="$ROOT/assets/global-stack-policy.md"
PACKAGE='ouroboros-ai[mcp,tui]'

say() { printf '%s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { say "ERROR: $1 is required."; exit 2; }; }
run() { say "+ $*"; "$@"; }

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    say 'ERROR: On native Windows use scripts/install-stack.ps1 so Ouroboros MCP autostart can be registered safely.'
    exit 2
    ;;
esac

need curl
need git
need node
need npm
need npx

if ! command -v uv >/dev/null 2>&1; then
  tmp_uv="$(mktemp)"
  curl -fsSL https://astral.sh/uv/install.sh -o "$tmp_uv"
  sh "$tmp_uv"
  rm -f "$tmp_uv"
  export PATH="$HOME/.local/bin:$PATH"
fi
need uv

run uv tool install --force "$PACKAGE"
export PATH="$HOME/.local/bin:$PATH"
need ouroboros
command -v ooo >/dev/null 2>&1 || { say 'ERROR: Required `ooo` command was not installed with Ouroboros.' >&2; exit 1; }
ouroboros_python="$(uv tool dir)/ouroboros-ai/bin/python"
[[ -x "$ouroboros_python" ]] || { say 'ERROR: Ouroboros tool Python was not found.' >&2; exit 1; }
run "$ouroboros_python" "$ROOT/scripts/patch-dashboard-picker.py"

tmp_rtk="$(mktemp)"
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh -o "$tmp_rtk"
sh "$tmp_rtk"
rm -f "$tmp_rtk"
export PATH="$HOME/.local/bin:$PATH"
need rtk

run npx -y github:JuliusBrussee/caveman

if command -v codex >/dev/null 2>&1; then
  codex plugin marketplace add Q00/ouroboros >/dev/null 2>&1 || true
  codex plugin marketplace upgrade ouroboros >/dev/null 2>&1 || true
  codex plugin add ouroboros@ouroboros >/dev/null 2>&1 || true
  codex plugin marketplace add DietrichGebert/ponytail >/dev/null 2>&1 || true
  codex plugin marketplace upgrade ponytail >/dev/null 2>&1 || true
  codex plugin add ponytail@ponytail >/dev/null 2>&1 || true
  run rtk init -g --codex
fi

if command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add Q00/ouroboros --scope user >/dev/null 2>&1 || true
  claude plugin install ouroboros@ouroboros --scope user >/dev/null 2>&1 || true
  claude plugin marketplace add DietrichGebert/ponytail --scope user >/dev/null 2>&1 || true
  claude plugin install ponytail@ponytail --scope user >/dev/null 2>&1 || true
  run rtk init -g --agent claude --auto-patch
fi

say '+ run required first agent action: ooo setup'
if ! bash "$ROOT/scripts/run-agent-setup.sh" "$PROJECT"; then
  printf '%s\n' 'ERROR: Required first agent action `ooo setup` was not verified successful. No further stack initialization was started.' >&2
  exit 1
fi

for setting in \
  clarification.max_interview_rounds=3 \
  execution.max_iterations_per_ac=3 \
  execution.auto_evolve=false \
  execution.auto_evolve_max_generations=1 \
  execution.verify_command_timeout_seconds=600 \
  evaluation.stage1_enabled=true \
  evaluation.stage2_enabled=true \
  evaluation.stage3_enabled=false \
  runtime_controls.generation_idle_timeout_seconds=600 \
  runtime_controls.generation_no_progress_timeout_seconds=900 \
  runtime_controls.generation_safety_timeout_seconds=3600 \
  orchestrator.default_max_turns=6 \
  seed.verify_command_gate=block; do
  run ouroboros config set "${setting%%=*}" "${setting#*=}"
done
run ouroboros config validate

run npm install -g ui-ux-pro-max-cli@latest
need uipro
if command -v codex >/dev/null 2>&1; then
  (cd "$HOME" && run uipro init --ai codex)
fi
if command -v claude >/dev/null 2>&1; then
  (cd "$HOME" && run uipro init --ai claude)
fi

run npm install -g @colbymchenry/codegraph@latest
need codegraph

if ! command -v codex >/dev/null 2>&1 && ! command -v claude >/dev/null 2>&1; then
  for candidate in 'opencode:opencode' 'gemini:gemini' 'copilot:copilot' 'kiro-cli:kiro' 'pi:pi' 'hermes:hermes' 'goose:goose' 'omp:omp'; do
    command_name="${candidate%%:*}"
    if command -v "$command_name" >/dev/null 2>&1; then
      run npx -y skills@latest add DietrichGebert/ponytail --skill '*' -g -y --copy
      run npx -y skills@latest add "$ROOT" --skill kiss-chris-stack -g -y --copy
      break
    fi
  done
fi

run codegraph install --target=auto --location=global --yes

if [[ -d "$PROJECT/.codegraph" ]]; then
  run codegraph sync "$PROJECT"
else
  run codegraph init -i "$PROJECT"
fi

if [[ -f "$PROJECT/.ouroboros/mechanical.toml" ]]; then
  say "+ preserve mechanical gates: $PROJECT/.ouroboros/mechanical.toml"
else
  run ooo detect "$PROJECT"
fi

install_skill() {
  local legacy_destination="$1/ouroboros-stack"
  local destination="$1/kiss-chris-stack"
  if [[ -d "$legacy_destination" && ! -e "$destination" ]]; then
    mv "$legacy_destination" "$destination"
  fi
  mkdir -p "$destination"
  cp -R "$ROOT/SKILL.md" "$ROOT/README.md" "$ROOT/agents" "$ROOT/assets" "$ROOT/docs" "$ROOT/references" "$ROOT/scripts" "$destination/"
}

install_skill "$HOME/.agents/skills"
if command -v claude >/dev/null 2>&1; then
  install_skill "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
fi

upsert_block() {
  bash "$ROOT/scripts/upsert-managed-block.sh" "$1" "$POLICY"
}

if command -v codex >/dev/null 2>&1; then
  codex_home="${CODEX_HOME:-$HOME/.codex}"
  upsert_block "$codex_home/AGENTS.md"
  [[ -s "$codex_home/AGENTS.override.md" ]] && upsert_block "$codex_home/AGENTS.override.md"
fi
if command -v claude >/dev/null 2>&1; then
  upsert_block "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/CLAUDE.md"
fi

run "$ROOT/scripts/verify-stack.sh" "$PROJECT"
say 'Done. Restart the agent so plugins, hooks, MCP servers, and global instructions reload.'
