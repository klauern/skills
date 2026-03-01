#!/usr/bin/env bash
set -euo pipefail
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -z "$command" ]] && exit 0

# Only check gh pr create commands
echo "$command" | grep -q 'gh pr create' || exit 0

warnings=""

# Check if --body was used and extract its value
if echo "$command" | grep -q '\-\-body'; then
  body=$(echo "$command" | sed -n 's/.*--body[[:space:]]*["'"'"']\([^"'"'"']*\)["'"'"'].*/\1/p')
  if [[ -z "$body" ]]; then
    # Try heredoc-style body
    body=$(echo "$command" | sed -n 's/.*--body[[:space:]]*"\$([^)]*)/found/p')
    if [[ -z "$body" ]]; then
      warnings="${warnings}PR body appears to be empty.\n"
    fi
  elif [[ ${#body} -lt 50 ]]; then
    warnings="${warnings}PR body is short (${#body} chars). Consider adding more detail.\n"
  fi
else
  warnings="${warnings}No --body flag found. Consider adding a PR description.\n"
fi

# Check for JIRA reference in the full command
if ! echo "$command" | grep -qE 'FSEC-[0-9]+'; then
  warnings="${warnings}No JIRA ticket reference (FSEC-XXXX) found in PR. Consider linking a ticket.\n"
fi

if [[ -n "$warnings" ]]; then
  echo "PR Quality Check:"
  echo -e "$warnings"
fi
exit 0
