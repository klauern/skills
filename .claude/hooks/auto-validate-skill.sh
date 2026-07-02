#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
[[ -z "$file_path" ]] && exit 0

# Check if the modified file is a SKILL.md
echo "$file_path" | grep -q 'SKILL\.md$' || exit 0

# PostToolUse plain stdout is transcript-only; use additionalContext so Claude sees it.
jq -n --arg ctx "SKILL.md modified ($file_path) — consider running the skill-validator agent to check compliance." \
  '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$ctx}}'
exit 0
