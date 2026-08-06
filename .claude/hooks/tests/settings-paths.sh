#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT
PROJECT_LINK="$FIXTURE/project with spaces"
ln -s "$REPO_ROOT" "$PROJECT_LINK"

jq -r '.hooks[][]?.hooks[]?.command // empty' "$REPO_ROOT/.claude/settings.json" |
while IFS= read -r command; do
  printf '{}\n' | CLAUDE_PROJECT_DIR="$PROJECT_LINK" bash -c "$command" >/dev/null
done

echo "settings hook path fixture passed"
