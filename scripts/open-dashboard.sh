#!/usr/bin/env bash
set -euo pipefail

url="${1:?usage: open-dashboard.sh LOOPBACK_URL [--dry-run] [--no-open]}"
shift
dry_run=0
no_open=0
for option in "$@"; do
  case "$option" in
    --dry-run) dry_run=1 ;;
    --no-open) no_open=1 ;;
    *) printf 'ERROR: unknown option: %s\n' "$option" >&2; exit 2 ;;
  esac
done
case "$url" in
  http://localhost:*|https://localhost:*|http://127.0.0.1:*|https://127.0.0.1:*|http://\[::1\]:*|https://\[::1\]:*) ;;
  *) printf 'ERROR: refusing non-loopback dashboard URL: %s\n' "$url" >&2; exit 2 ;;
esac

if (( dry_run )); then printf '%s\n' "$url"; exit 0; fi
api_url="$(printf '%s' "$url" | sed -E 's#^(https?://(\[[^]]+\](:[0-9]+)?|[^/?]+)).*#\1/api/runs#')"
dashboard_ready() {
  local response
  response="$(curl -fsS --max-time "$2" "$1" 2>/dev/null)" && grep -q '"runs"[[:space:]]*:' <<<"$response"
}
if ! dashboard_ready "$api_url" 3; then
  command -v uv >/dev/null 2>&1 || { printf 'ERROR: stale dashboard URL and uv is unavailable: %s\n' "$url" >&2; exit 4; }
  ouroboros_python="$(uv tool dir)/ouroboros-ai/bin/python"
  [[ -x "$ouroboros_python" ]] || { printf 'ERROR: Ouroboros tool Python was not found.\n' >&2; exit 4; }
  base_url="$($ouroboros_python -c 'from ouroboros.dashboard_web import dashboard_base_url; print(dashboard_base_url())' | tail -n 1)"
  [[ -n "$base_url" ]] || { printf 'ERROR: Ouroboros did not return a dashboard URL.\n' >&2; exit 4; }
  query=''
  [[ "$url" == *'?'* ]] && query="?${url#*\?}"
  url="${base_url%/}${query}"
  api_url="${base_url%/}/api/runs"
fi
response="$(curl -fsS --retry 3 --retry-all-errors --retry-delay 1 --retry-max-time 45 --max-time 15 "$api_url")"
grep -q '"runs"[[:space:]]*:' <<<"$response" || {
  printf 'ERROR: Ouroboros dashboard run picker is not ready at %s\n' "$api_url" >&2
  exit 4
}
if (( no_open )); then printf '%s\n' "$url"; exit 0; fi
if command -v xdg-open >/dev/null 2>&1; then xdg-open "$url" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then open "$url" >/dev/null 2>&1 &
else printf 'Dashboard: %s\n' "$url"; exit 3
fi
