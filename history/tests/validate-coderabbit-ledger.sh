#!/usr/bin/env bash
set -euo pipefail

LEDGER=${1:-"$(cd "$(dirname "$0")/.." && pwd)/2026-08-06-coderabbit-findings-ledger.md"}

count_matches() {
  local pattern=$1 output status
  set +e
  output=$(rg -c "$pattern" "$LEDGER" 2>&1)
  status=$?
  set -e
  case $status in
    0) printf '%s\n' "$output" ;;
    1) printf '0\n' ;;
    *) printf 'ledger validator: rg failed: %s\n' "$output" >&2; return "$status" ;;
  esac
}

assert_count() {
  local expected=$1 pattern=$2 label=$3 actual
  actual=$(count_matches "$pattern")
  [ "$actual" = "$expected" ] || {
    printf '%s: expected %s, got %s\n' "$label" "$expected" "$actual" >&2
    return 1
  }
}

assert_count 37 '^\| 16-[0-9]{2} \|' 'PR 16 rows'
assert_count 28 '^\| 16-.*\*\*fixed/superseded\*\*' 'PR 16 fixed'
assert_count 5 '^\| 16-.*\*\*assigned\*\*' 'PR 16 assigned'
assert_count 4 '^\| 16-.*\*\*policy-rejected\*\*' 'PR 16 policy rejected'
assert_count 13 '^\| 17-[0-9]{2} \|' 'PR 17 rows'
assert_count 12 '^\| 17-.*\*\*fixed/superseded\*\*' 'PR 17 fixed'
assert_count 1 '^\| 17-.*\*\*policy-rejected\*\*' 'PR 17 policy rejected'
assert_count 7 '^\| 17R-[0-9]{2} \|' 'PR 17 remediation rows'
assert_count 7 '^\| 17R-[0-9]{2} \|.*\*\*fixed/superseded\*\*' 'PR 17 remediation fixed'
assert_count 5 '^\| 17R2-[0-9]{2} \|' 'PR 17 remediation 2 rows'
assert_count 5 '^\| 17R2-[0-9]{2} \|.*\*\*fixed/superseded\*\*' 'PR 17 remediation 2 fixed'
assert_count 6 '^\| L17-[0-9]{2} \|' 'Luna evidence rows'
for number in {01..06}; do
  assert_count 1 "^\\| L17-$number \\|" "Luna evidence required ID L17-$number"
done
assert_count 6 '^\| L17-[0-9]{2} \|.*\*\*fixed/superseded\*\*' 'Luna evidence fixed'
for group in 17R3 17R4 17R5; do
  assert_count 1 "^\\| $group-[0-9]{2} \\|" "$group rows"
  assert_count 1 "^\\| $group-[0-9]{2} \\|.*\\*\\*fixed/superseded\\*\\*" "$group fixed"
done
assert_count 14 '^\| 18R-[0-9]{2} \|' 'PR 18 review rows'
for number in {01..14}; do
  assert_count 1 "^\\| 18R-$number \\|" "PR 18 required ID 18R-$number"
done
assert_count 0 '^\| 18R-.*\*\*policy-rejected\*\*' 'PR 18 policy rejected'
assert_count 14 '^\| 18R-.*\*\*fixed/superseded\*\*' 'PR 18 fixed'
assert_count 0 '^\| 18R-.*\*\*assigned\*\*' 'PR 18 assigned'
assert_count 8 '^\| 18R2-[0-9]{2} \|' 'PR 18 second-review rows'
for number in {01..08}; do
  assert_count 1 "^\\| 18R2-$number \\|" "PR 18 second-review required ID 18R2-$number"
done
assert_count 8 '^\| 18R2-.*\*\*fixed/superseded\*\*' 'PR 18 second-review fixed'
assert_count 0 '^\| 18R2-.*\*\*assigned\*\*' 'PR 18 second-review assigned'
assert_count 0 '^\| 18R2-.*\*\*policy-rejected\*\*' 'PR 18 second-review policy rejected'
assert_count 8 '^\| 18R3-[0-9]{2} \|' 'PR 18 third-review rows'
for number in {01..08}; do
  assert_count 1 "^\\| 18R3-$number \\|" "PR 18 third-review required ID 18R3-$number"
done
assert_count 8 '^\| 18R3-.*\*\*fixed/superseded\*\*' 'PR 18 third-review fixed'
assert_count 0 '^\| 18R3-.*\*\*assigned\*\*' 'PR 18 third-review assigned'
assert_count 0 '^\| 18R3-.*\*\*policy-rejected\*\*' 'PR 18 third-review policy rejected'
assert_count 1 '^\| L18-[0-9]{2} \|' 'PR 18 Luna release rows'
assert_count 1 '^\| L18-[0-9]{2} \|.*\*\*assigned\*\*' 'PR 18 Luna release assigned'

awk -F '|' '
  /^\| (16-|17-|17R-|17R2-|17R3-|17R4-|17R5-|L17-|18R-|18R2-|18R3-|L18-)/ {
    id=$2; gsub(/^[[:space:]]+|[[:space:]]+$/, "", id)
    if (++seen[id] > 1) { print "duplicate ledger ID: " id > "/dev/stderr"; bad=1 }
  }
  END { exit bad }
' "$LEDGER"

echo "CodeRabbit ledger validation passed"
