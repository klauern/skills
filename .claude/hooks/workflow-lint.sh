#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
[[ -z "$file_path" ]] && exit 0

# Only check GitHub workflow files (.yml or .yaml)
echo "$file_path" | grep -qE '\.github/workflows/.*\.ya?ml$' || exit 0

# PostToolUse plain stdout is transcript-only; wrap findings in additionalContext JSON
# so Claude actually sees them.
emit_context() {
  jq -n --arg ctx "$1" \
    '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$ctx}}'
}

# Try actionlint first
if command -v actionlint &>/dev/null; then
  lint_output=$(actionlint "$file_path" 2>&1) || true
  if [[ -n "$lint_output" ]]; then
    emit_context "Workflow lint (actionlint) found issues in $file_path:
$lint_output"
  fi
  exit 0
fi

# Fall back to yq for basic YAML validation
if command -v yq &>/dev/null; then
  if ! yq eval '.' "$file_path" >/dev/null 2>&1; then
    emit_context "Workflow lint: YAML syntax error detected in $file_path. Run yq or yamllint to see details."
  fi
  exit 0
fi

emit_context "Workflow lint: neither actionlint nor yq is installed; verify $file_path syntax manually."
exit 0
