#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
prompt=$(echo "$input" | jq -r '.prompt // empty')

if echo "$prompt" | grep -qE '/commit-push|/commits:commit-push'; then
  cat <<'EOF'
VERSION BUMP REMINDER: Run /version-bump before committing plugin changes.
EOF
fi
exit 0
