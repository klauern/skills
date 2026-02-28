#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -z "$command" ]] && exit 0

if echo "$command" | grep -qE 'grep[[:space:]]+-E([[:space:]]|$)'; then
  cat >&2 <<'EOF'
{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"grep -E blocked. Use 'grep -e' or 'rg' instead (macOS compatibility)."}
EOF
  exit 2
fi
exit 0
