#!/usr/bin/env bash
set -euo pipefail

HOOK="$(cd "$(dirname "$0")/.." && pwd)/validate-commit-format.sh"

run_hook() {
  local message=$1
  jq -n --arg command "git commit -m \"$message\"" \
    '{tool_input: {command: $command}}' | "$HOOK"
}

for type in feat fix docs style refactor perf test build ci chore revert; do
  if ! run_hook "$type: accepted fixture" >/dev/null 2>&1; then
    echo "expected accepted type to pass: $type" >&2
    exit 1
  fi
done

status=0
run_hook "invalid: rejected fixture" >/dev/null 2>&1 || status=$?
if [ "$status" -ne 2 ]; then
  echo "expected invalid type to exit 2, got $status" >&2
  exit 1
fi

echo "validate-commit-format fixtures passed"
