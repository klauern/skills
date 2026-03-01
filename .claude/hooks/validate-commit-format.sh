#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -z "$command" ]] && exit 0

# Only check git commit commands (handles git -C repo commit, git -c key=val commit, etc.)
echo "$command" | grep -qE '(^|[[:space:]])git([[:space:]]+(-C|--git-dir|--work-tree|-c)([=[:space:]]+[^[:space:]]+))*[[:space:]]+commit([[:space:]]|$)' || exit 0

# Check if message flag is present (-m, --message, or combined flags like -am)
has_m_flag=false
echo "$command" | grep -qE -- '(^|[[:space:]])(-[a-zA-Z]*m|-m|--message)([=[:space:]]+|"|'"'"')' && has_m_flag=true

# Allow interactive commits and --amend without -m
if [[ "$has_m_flag" == "false" ]]; then
  exit 0
fi

# For heredoc-style commits: git commit -m "$(cat <<'EOF'\ntype: msg\nEOF\n)"
# Extract the first meaningful line after the heredoc opener
if echo "$command" | grep -q 'cat <<'; then
  msg=$(echo "$command" | sed -n "/cat <</{n;s/^[[:space:]]*//;p;}" | head -1)
else
  # Extract message from -m "message", --message "message", -am "message", etc.
  # Try double quotes first, then single quotes, then --message= form
  msg=$(echo "$command" | sed -n "s/.*\(-[a-zA-Z]*m\|--message\)[[:space:]]*\"\([^\"]*\)\".*/\2/p")
  if [[ -z "$msg" ]]; then
    msg=$(echo "$command" | sed -n "s/.*\(-[a-zA-Z]*m\|--message\)[[:space:]]*'\([^']*\)'.*/\2/p")
  fi
  if [[ -z "$msg" ]]; then
    msg=$(echo "$command" | sed -n "s/.*--message=\"\([^\"]*\)\".*/\1/p")
  fi
  if [[ -z "$msg" ]]; then
    msg=$(echo "$command" | sed -n "s/.*--message='\([^']*\)'.*/\1/p")
  fi
fi

# If -m flag was present but we couldn't extract a message, deny to prevent bypass
if [[ -z "$msg" ]]; then
  cat >&2 <<'EOF'
{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"Unable to parse commit message from -m/--message. Use a quoted message (e.g., -m \"type(scope): description\")."}
EOF
  exit 2
fi

# Validate conventional commit format
if ! echo "$msg" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\([a-zA-Z0-9_-]+\))?(!)?: .+'; then
  cat >&2 <<'EOF'
{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"Commit message does not follow conventional commit format. Expected: <type>(<scope>): <description>\nTypes: feat, fix, docs, style, refactor, perf, test, build, ci, chore"}
EOF
  exit 2
fi
exit 0
