#!/usr/bin/env bash
set -euo pipefail

COMMAND=$(cd "$(dirname "$0")/.." && pwd)/commit-push.md

rg -q 'zero exit status from `git push`' "$COMMAND"
rg -q 'failed push stops the workflow' "$COMMAND"
rg -q 'use `git status` only to inspect local cleanliness afterward' "$COMMAND"

echo "commit-push guidance assertions passed"
