#!/usr/bin/env bash
set -euo pipefail

TEST_DIR=$(cd "$(dirname "$0")" && pwd)
LEDGER="$TEST_DIR/../2026-08-06-coderabbit-findings-ledger.md"
VALIDATOR="$TEST_DIR/validate-coderabbit-ledger.sh"
FIXTURE=$(mktemp -d "${TMPDIR:-/tmp}/ledger-validation.XXXXXX")
trap 'rm -rf -- "$FIXTURE"' EXIT

bash "$VALIDATOR" "$LEDGER"

awk '{ print; if ($0 ~ /^\| 17R5-01 \|/) print }' "$LEDGER" >"$FIXTURE/duplicate.md"
if bash "$VALIDATOR" "$FIXTURE/duplicate.md" >"$FIXTURE/out" 2>"$FIXTURE/err"; then
  echo "duplicated evidence row unexpectedly passed" >&2
  exit 1
fi
rg -q '17R5 rows: expected 1, got 2|duplicate ledger ID: 17R5-01' "$FIXTURE/err"

sed 's/^| 17R5-01 |\(.*\)\*\*fixed\/superseded\*\*/| 17R5-01 |\1**assigned**/' \
  "$LEDGER" >"$FIXTURE/disposition.md"
if bash "$VALIDATOR" "$FIXTURE/disposition.md" >/dev/null 2>&1; then
  echo "disposition mutation unexpectedly passed" >&2
  exit 1
fi

echo "CodeRabbit ledger mutation fixtures passed"
