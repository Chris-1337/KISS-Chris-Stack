#!/usr/bin/env bash
set -u

project="${1:?project path is required}"

if command -v codex >/dev/null 2>&1; then
  agent=(codex exec --skip-git-repo-check -C "$project" 'ooo setup')
elif command -v claude >/dev/null 2>&1; then
  agent=(claude --print --permission-mode acceptEdits 'ooo setup')
else
  printf '%s\n' 'ERROR: Cannot start agent for required first action `ooo setup`: neither Codex nor Claude Code is available.' >&2
  exit 1
fi

if "${agent[@]}"; then
  exit 0
else
  status=$?
  printf 'ERROR: Required first agent action `ooo setup` did not complete successfully (exit code: %s). No further stack initialization was started.\n' "$status" >&2
  exit 1
fi
