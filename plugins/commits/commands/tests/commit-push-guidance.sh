#!/usr/bin/env bash
set -euo pipefail

COMMAND=$(cd "$(dirname "$0")/.." && pwd)/commit-push.md
FIXTURE=$(mktemp -d "${TMPDIR:-/tmp}/commit-push-guidance.XXXXXX")
trap 'rm -rf -- "$FIXTURE"' EXIT
mkdir -p "$FIXTURE/bin"

line_count=$(wc -l <"$COMMAND" | tr -d ' ')
if ((line_count > 30)); then
  echo "commit-push command exceeds 30-line thin-command limit: $line_count" >&2
  exit 1
fi
rg -q 'Invoke the \*\*conventional-commits\*\* skill' "$COMMAND"
rg -q '\$ARGUMENTS' "$COMMAND"
rg -q 'full tracked diff and every untracked file' "$COMMAND"

awk '
  /BEGIN COMMIT_PUSH_REMOTE/ { capture=1; next }
  /END COMMIT_PUSH_REMOTE/ { exit }
  capture
' "$COMMAND" >"$FIXTURE/push.block"
{
  printf '#!/usr/bin/env bash\nset -euo pipefail\n'
  cat "$FIXTURE/push.block"
} >"$FIXTURE/run.sh"

cat >"$FIXTURE/bin/git" <<'GIT'
#!/usr/bin/env bash
set -euo pipefail
printf 'git %s\n' "$*" >>"$CALL_LOG"

if [[ $1 == rev-parse ]]; then
  [[ ${HAS_UPSTREAM:-0} == 1 ]]
elif [[ $1 == push ]]; then
  exit "${PUSH_STATUS:-0}"
fi
GIT
chmod +x "$FIXTURE/bin/git" "$FIXTURE/run.sh"

run_case() {
  : >"$CALL_LOG"
  HAS_UPSTREAM=$1 PUSH_STATUS=${2:-0} PATH="$FIXTURE/bin:$PATH" \
    bash "$FIXTURE/run.sh"
}

export CALL_LOG="$FIXTURE/calls"

run_case 1
rg -q '^git push$' "$CALL_LOG"
if rg -q '^git push -u origin HEAD$' "$CALL_LOG"; then
  echo "tracked branch unexpectedly used upstream setup" >&2
  exit 1
fi
rg -q '^git status --short --branch$' "$CALL_LOG"

run_case 0
rg -q '^git push -u origin HEAD$' "$CALL_LOG"
rg -q '^git status --short --branch$' "$CALL_LOG"

assert_push_failure() {
  local has_upstream=$1 status
  : >"$CALL_LOG"
  if HAS_UPSTREAM=$has_upstream PUSH_STATUS=42 PATH="$FIXTURE/bin:$PATH" \
    bash "$FIXTURE/run.sh"; then
    echo "failed push unexpectedly succeeded" >&2
    exit 1
  else
    status=$?
  fi
  [[ $status -eq 42 ]]
  if rg -q '^git status ' "$CALL_LOG"; then
    echo "local status ran after failed push" >&2
    exit 1
  fi
}

assert_push_failure 1
assert_push_failure 0

echo "commit-push workflow and structure fixtures passed"
