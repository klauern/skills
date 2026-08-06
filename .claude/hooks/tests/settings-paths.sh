#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT
PROJECT_LINK="$FIXTURE/project with spaces"
ln -s "$REPO_ROOT" "$PROJECT_LINK"

jq -r '.hooks[][]?.hooks[]?.command | select(type == "string" and length > 0)' \
  "$REPO_ROOT/.claude/settings.json" >"$FIXTURE/commands"
if [ ! -s "$FIXTURE/commands" ]; then
  echo "settings hook fixture found no commands" >&2
  exit 1
fi

while IFS= read -r command; do
  printf '{}\n' | CLAUDE_PROJECT_DIR="$PROJECT_LINK" bash -c "$command" >/dev/null
done <"$FIXTURE/commands"

echo "settings hook path fixture passed"
