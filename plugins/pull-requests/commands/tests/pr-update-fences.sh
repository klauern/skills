#!/usr/bin/env bash
set -euo pipefail

COMMAND_FILE="$(cd "$(dirname "$0")/.." && pwd)/pr-update.md"

awk '
  /Or if body is long/ { expected = 1; next }
  expected == 1 {
    if ($0 !~ /^[[:space:]]*```bash[[:space:]]*$/) exit 1
    found = 1
    expected = 0
  }
  END { if (!found) exit 1 }
' "$COMMAND_FILE"

awk '
  /^[[:space:]]*Display:/ { expected = 1; next }
  expected == 1 {
    if ($0 !~ /^[[:space:]]*```text[[:space:]]*$/) exit 1
    found = 1
    expected = 0
  }
  END { if (!found) exit 1 }
' "$COMMAND_FILE"

echo "pr-update fence fixtures passed"
