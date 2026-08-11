#!/usr/bin/env bash
set -euo pipefail

COMMAND_FILE="$(cd "$(dirname "$0")/.." && pwd)/pr-update.md"

rg -q -F 'mktemp "${TMPDIR:-/tmp}/pr-body.md.XXXXXX"' "$COMMAND_FILE"

awk '
  /Never pass a description inline/ { expected = 1; next }
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
