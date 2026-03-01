#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -z "$command" ]] && exit 0

# Only check git commit commands
echo "$command" | grep -q 'git commit' || exit 0

# Check if -m flag is present (handles -m "msg", -m 'msg', -m "$(cat ...)")
has_m_flag=false
echo "$command" | grep -qE -- '-m[[:space:]]+' && has_m_flag=true
echo "$command" | grep -qE -- '-m"' && has_m_flag=true
echo "$command" | grep -qE -- "-m'" && has_m_flag=true

# Allow interactive commits and --amend without -m
if [[ "$has_m_flag" == "false" ]]; then
  exit 0
fi

# For heredoc-style commits: git commit -m "$(cat <<'EOF'\ntype: msg\nEOF\n)"
# Extract the first meaningful line after the heredoc opener
if echo "$command" | grep -q 'cat <<'; then
  msg=$(echo "$command" | sed -n "/cat <</{n;s/^[[:space:]]*//;p;}" | head -1)
else
  # Extract message from -m "message" or -m 'message'
  # Try double quotes first, then single quotes
  msg=$(echo "$command" | sed -n "s/.*-m[[:space:]]*\"\([^\"]*\)\".*/\1/p")
  if [[ -z "$msg" ]]; then
    msg=$(echo "$command" | sed -n "s/.*-m[[:space:]]*'\([^']*\)'.*/\1/p")
  fi
fi

# If we couldn't extract a message, pass through (don't block)
[[ -z "$msg" ]] && exit 0

# Validate conventional commit format
if ! echo "$msg" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\([a-zA-Z0-9_-]+\))?(!)?: .+'; then
  cat >&2 <<'EOF'
{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"Commit message does not follow conventional commit format. Expected: <type>(<scope>): <description>\nTypes: feat, fix, docs, style, refactor, perf, test, build, ci, chore"}
EOF
  exit 2
fi
exit 0
