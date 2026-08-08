#!/usr/bin/env bash
set -euo pipefail

COMMAND=$(cd "$(dirname "$0")/.." && pwd)/merge-conflicts.md
SKILL=$(cd "$(dirname "$0")/../../skills/pr-conflict-resolver" && pwd)/SKILL.md
WORKFLOWS=$(cd "$(dirname "$0")/../../skills/pr-conflict-resolver/references" && pwd)/workflows.md

rg -q '^## Complete the active operation$' "$COMMAND"
rg -q '^git commit -m ' "$COMMAND"
rg -q -F '`git merge --abort` restores the pre-merge state' "$COMMAND"
if rg -q 'git rebase|rebase state|active rebase' "$COMMAND"; then
  echo "merge-only command unexpectedly promises rebase support" >&2
  exit 1
fi
rg -q -F 'active merges only' "$SKILL"
rg -q -F 'support conflicts from an active merge only' "$WORKFLOWS"

echo "merge-conflicts guidance assertions passed"
