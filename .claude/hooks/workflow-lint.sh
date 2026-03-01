#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
[[ -z "$file_path" ]] && exit 0

# Only check GitHub workflow files
echo "$file_path" | grep -q '\.github/workflows/.*\.yml$' || exit 0

# Try actionlint first
if command -v actionlint &>/dev/null; then
  lint_output=$(actionlint "$file_path" 2>&1) || true
  if [[ -n "$lint_output" ]]; then
    echo "Workflow Lint (actionlint):"
    echo "$lint_output"
  fi
  exit 0
fi

# Fall back to yq for basic YAML validation
if command -v yq &>/dev/null; then
  if ! yq eval '.' "$file_path" >/dev/null 2>&1; then
    echo "Workflow Lint: YAML syntax error detected in $file_path. Run yq or yamllint to see details."
  fi
  exit 0
fi

# Neither tool available
echo "Workflow Lint: Neither actionlint nor yq found. Please verify $file_path syntax manually."
exit 0
