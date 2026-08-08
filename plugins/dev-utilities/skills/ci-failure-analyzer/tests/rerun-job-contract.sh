#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
docs=(
  "$SKILL_DIR/SKILL.md"
  "$SKILL_DIR/references/examples.md"
  "$SKILL_DIR/references/test-matrix.md"
  "$SKILL_DIR/references/workflows.md"
)

for doc in "${docs[@]}"; do
  compact="$(awk '{$1 = $1; printf "%s ", $0}' "$doc")"
  rg -q -F 'selected job and its dependencies' <<<"$compact"
  if rg -q -F 'dependent jobs' "$doc"; then
    echo "outdated downstream-dependent wording remains in $doc" >&2
    exit 1
  fi
done

echo "CI rerun job contract assertions passed"
