#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT

cat > "$temp/codex" <<'EOF'
#!/usr/bin/env bash
printf '%s|%s\n' "$*" "$MOCK_EXIT" >> "$MOCK_LOG"
exit "$MOCK_EXIT"
EOF
chmod +x "$temp/codex"

PATH="$temp:$PATH" MOCK_EXIT=0 MOCK_LOG="$temp/agent.log" bash "$root/scripts/run-agent-setup.sh" "$root"
grep -Eq 'exec --skip-git-repo-check -C .+ ooo setup\|0' "$temp/agent.log"

if PATH="$temp:$PATH" MOCK_EXIT=23 MOCK_LOG="$temp/agent.log" bash "$root/scripts/run-agent-setup.sh" "$root" 2>"$temp/stderr"; then
  printf '%s\n' 'POSIX gate accepted a failed agent setup.' >&2
  exit 1
fi
grep -q 'exit code: 23' "$temp/stderr"

rm "$temp/codex"
command() { return 1; }
export -f command
if PATH="$temp:/usr/bin:/bin" /usr/bin/env bash "$root/scripts/run-agent-setup.sh" "$root" 2>"$temp/stderr"; then
  printf '%s\n' 'POSIX gate accepted a missing agent.' >&2
  exit 1
fi
unset -f command
grep -q 'Cannot start agent.*neither Codex nor Claude Code is available' "$temp/stderr"

printf '%s\n' 'POSIX agent setup gate tests passed.'
