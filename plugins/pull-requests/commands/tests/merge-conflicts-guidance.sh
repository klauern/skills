#!/usr/bin/env bash
set -euo pipefail

COMMAND=$(cd "$(dirname "$0")/.." && pwd)/merge-conflicts.md

rg -q '^## Complete the active operation$' "$COMMAND"
rg -q '^git commit -m ' "$COMMAND"
rg -q '^git rebase --continue$' "$COMMAND"
rg -q 'continue the existing rebase instead of creating a merge commit' "$COMMAND"

echo "merge-conflicts guidance assertions passed"
