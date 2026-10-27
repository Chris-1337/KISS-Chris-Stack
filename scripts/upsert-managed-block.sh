#!/usr/bin/env bash
set -euo pipefail

file="$1"
policy="$2"
begin='<!-- kiss-chris-stack:start -->'
end='<!-- kiss-chris-stack:end -->'
legacy_begin='<!-- ouroboros-stack:start -->'
legacy_end='<!-- ouroboros-stack:end -->'
mkdir -p "$(dirname "$file")"
touch "$file"

begin_count="$(awk -v marker="$begin" '{ line=$0; sub(/\r$/, "", line); if (line == marker) count++ } END { print count+0 }' "$file")"
end_count="$(awk -v marker="$end" '{ line=$0; sub(/\r$/, "", line); if (line == marker) count++ } END { print count+0 }' "$file")"
legacy_begin_count="$(awk -v marker="$legacy_begin" '{ line=$0; sub(/\r$/, "", line); if (line == marker) count++ } END { print count+0 }' "$file")"
legacy_end_count="$(awk -v marker="$legacy_end" '{ line=$0; sub(/\r$/, "", line); if (line == marker) count++ } END { print count+0 }' "$file")"
if [[ "$begin_count" != "$end_count" || "$legacy_begin_count" != "$legacy_end_count" ]]; then
  printf 'ERROR: Unmatched KISS-Chris-Stack marker in %s\n' "$file" >&2
  exit 1
fi
if (( begin_count > 0 && legacy_begin_count > 0 )); then
  printf 'ERROR: Both current and legacy KISS-Chris-Stack blocks exist in %s\n' "$file" >&2
  exit 1
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
awk -v begin="$begin" -v end="$end" -v legacy_begin="$legacy_begin" -v legacy_end="$legacy_end" -v policy="$policy" '
  {
    normalized=$0
    if (sub(/\r$/, "", normalized)) eol="\r"
  }
  normalized == begin || normalized == legacy_begin {
    seen=1
    print begin eol
    while ((getline line < policy) > 0) print line eol
    close(policy)
    skipping=1
    next
  }
  normalized == end || normalized == legacy_end { print end eol; skipping=0; next }
  !skipping { print }
  END {
    if (!seen && NR > 0) print eol
    if (!seen) {
      print begin eol
      while ((getline line < policy) > 0) print line eol
      close(policy)
      print end eol
    }
  }
' "$file" > "$tmp"
mv "$tmp" "$file"
trap - EXIT
