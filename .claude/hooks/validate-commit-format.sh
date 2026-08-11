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
# Anchor to the heredoc that FOLLOWS -m so an unrelated earlier heredoc isn't picked up.
if echo "$command" | grep -qE -- '-[a-zA-Z]*m[[:space:]]+"\$\(cat <<'; then
  # The sed pattern intentionally matches literal `$(`.
  # shellcheck disable=SC2016
  msg=$(echo "$command" | sed -n '/-[a-zA-Z]*m[[:space:]]*"\$(cat <</{n;s/^[[:space:]]*//;p;}' | head -1)
elif echo "$command" | grep -q 'cat <<'; then
  msg=$(echo "$command" | sed -n "/cat <</{n;s/^[[:space:]]*//;p;}" | head -1)
else
  # Extract message from -m "message", --message "message", -am "message", etc.
  msg=$(echo "$command" | sed -En "s/.*(-[a-zA-Z]*m|--message)[[:space:]]*\"([^\"]*)\".*/\2/p")
  if [[ -z "$msg" ]]; then
    msg=$(echo "$command" | sed -En "s/.*(-[a-zA-Z]*m|--message)[[:space:]]*'([^']*)'.*/\2/p")
  fi
  if [[ -z "$msg" ]]; then
    msg=$(echo "$command" | sed -En "s/.*--message=\"([^\"]*)\".*/\1/p")
  fi
  if [[ -z "$msg" ]]; then
    msg=$(echo "$command" | sed -En "s/.*--message='([^']*)'.*/\1/p")
  fi
fi

# Message uses a variable or couldn't be parsed (e.g. -m "$MSG", escaped quotes):
# pass rather than hard-deny — we can't see the real message, and blocking legitimate
# commits is worse than missing a badly-formatted one.
if [[ -z "$msg" || "$msg" == \$* ]]; then
  exit 0
fi

# Validate conventional commit format (scope may list several comma-separated areas)
if ! echo "$msg" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_,./ -]+\))?(!)?: .+'; then
  cat >&2 <<'EOF'
{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"Commit message does not follow conventional commit format. Expected: <type>(<scope>): <description>\nTypes: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert"}
EOF
  exit 2
fi
exit 0
