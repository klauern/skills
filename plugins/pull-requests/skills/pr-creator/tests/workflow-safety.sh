#!/usr/bin/env bash
set -euo pipefail

SKILL=$(cd "$(dirname "$0")/.." && pwd)/SKILL.md
UPDATE=$(cd "$(dirname "$0")/../../../commands" && pwd)/pr-update.md
FIXTURE=$(mktemp -d "${TMPDIR:-/tmp}/pr-creator-safety.XXXXXX")
trap 'rm -rf -- "$FIXTURE"' EXIT
mkdir -p "$FIXTURE/bin" "$FIXTURE/tmp"

extract_block() {
  awk -v start="$1" -v end="$2" '
    index($0, start) { capture=1; next }
    index($0, end) { exit }
    capture { sub(/^[[:space:]]{3}/, ""); print }
  ' "$3"
}
extract_block 'BEGIN PR_CREATOR_PREFLIGHT' 'END PR_CREATOR_PREFLIGHT' "$SKILL" >"$FIXTURE/preflight.sh"
extract_block 'BEGIN PR_CREATOR_CREATE' 'END PR_CREATOR_CREATE' "$SKILL" >"$FIXTURE/create.block"
extract_block 'BEGIN PR_UPDATE_APPLY' 'END PR_UPDATE_APPLY' "$UPDATE" >"$FIXTURE/update.sh"

cat >"$FIXTURE/bin/gh" <<'GH'
#!/usr/bin/env bash
set -euo pipefail
printf 'gh %s\n' "$*" >>"$CALL_LOG"
case "$1 $2" in
  'pr list')
    case ${GH_PR_MODE:-none} in
      existing) echo https://example.test/pr/1 ;;
      none) : ;;
      error) echo 'authentication failed' >&2; exit 1 ;;
    esac ;;
  'repo view')
    if [[ " $* " == *' defaultBranchRef '* ]]; then echo main; else echo "${GH_PERMISSION:-WRITE}"; fi ;;
  'pr create'|'pr edit')
    : >"$CAPTURE_ARGS"
    previous=
    for arg in "$@"; do
      printf '%s\n' "$arg" >>"$CAPTURE_ARGS"
      if [ "$previous" = --body-file ]; then
        printf '%s\n' "$arg" >"$CAPTURE_BODY_PATH"
        cp "$arg" "$CAPTURE_BODY"
      fi
      previous=$arg
    done ;;
esac
GH
cat >"$FIXTURE/bin/git" <<'GIT'
#!/usr/bin/env bash
set -euo pipefail
printf 'git %s\n' "$*" >>"$CALL_LOG"
case "$1" in
  branch) echo feature/safe ;;
  check-ref-format) : ;;
  fetch) cp "$REMOTE_BASE_FILE" "$LOCAL_BASE_FILE" ;;
  rev-parse) [ -s "$LOCAL_BASE_FILE" ] ;;
  push) : ;;
esac
GIT
chmod +x "$FIXTURE/bin/gh" "$FIXTURE/bin/git"

export PATH="$FIXTURE/bin:$PATH" CALL_LOG="$FIXTURE/calls" \
  REMOTE_BASE_FILE="$FIXTURE/remote-base" LOCAL_BASE_FILE="$FIXTURE/local-base"
echo current >"$REMOTE_BASE_FILE"

: >"$CALL_LOG"
GH_PR_MODE=existing bash "$FIXTURE/preflight.sh"
if rg -q '^git fetch ' "$CALL_LOG"; then
  echo "existing PR lookup unexpectedly fetched the base" >&2; exit 1
fi

: >"$CALL_LOG"
if GH_PR_MODE=error bash "$FIXTURE/preflight.sh" >/dev/null 2>&1; then
  echo "operational PR lookup failure unexpectedly continued" >&2; exit 1
fi
if rg -q '^git fetch ' "$CALL_LOG"; then
  echo "failed PR lookup unexpectedly fetched the base" >&2; exit 1
fi

rm -f "$LOCAL_BASE_FILE"
: >"$CALL_LOG"
GH_PR_MODE=none bash "$FIXTURE/preflight.sh"
cmp "$REMOTE_BASE_FILE" "$LOCAL_BASE_FILE"
fetch_line=$(rg -n '^git fetch ' "$CALL_LOG" | cut -d: -f1)
verify_line=$(rg -n '^git rev-parse ' "$CALL_LOG" | cut -d: -f1)
[ "$fetch_line" -lt "$verify_line" ]

echo stale >"$LOCAL_BASE_FILE"
echo refreshed >"$REMOTE_BASE_FILE"
: >"$CALL_LOG"
GH_PR_MODE=none bash "$FIXTURE/preflight.sh"
cmp "$REMOTE_BASE_FILE" "$LOCAL_BASE_FILE"

export CAPTURE_ARGS="$FIXTURE/args" CAPTURE_BODY="$FIXTURE/body" \
  CAPTURE_BODY_PATH="$FIXTURE/body-path" TMPDIR="$FIXTURE/tmp" GH_PR_MODE=none
literal_dollar='$'
BODY_TEXT=$(printf "summary\nBODY\nEOF\n\`literal\` and %s(literal)" "$literal_dollar")
export BASE=main PR_TITLE='feat: safe PR' PR_BODY="$BODY_TEXT" PR_DRAFT=false
{ printf 'REQUESTED_LABELS=()\nREQUESTED_ASSIGNEES=()\n'; cat "$FIXTURE/create.block"; } >"$FIXTURE/create.sh"
bash "$FIXTURE/create.sh"
if rg -q '^--draft$|^--label$|^--assignee$' "$CAPTURE_ARGS"; then
  echo "minimal create unexpectedly added optional metadata" >&2; exit 1
fi
[ "$(cat "$CAPTURE_BODY")" = "$BODY_TEXT" ]
[ ! -e "$(cat "$CAPTURE_BODY_PATH")" ]

export PR_DRAFT=true GH_PERMISSION=WRITE
{ printf 'REQUESTED_LABELS=("bug" "needs docs")\nREQUESTED_ASSIGNEES=("@me")\n'; cat "$FIXTURE/create.block"; } >"$FIXTURE/create-full.sh"
bash "$FIXTURE/create-full.sh"
rg -q '^--draft$' "$CAPTURE_ARGS"
[ "$(rg -c '^--label$' "$CAPTURE_ARGS")" -eq 2 ]
rg -q '^--assignee$' "$CAPTURE_ARGS"

export PR_NUMBER=42 UPDATED_TITLE='fix: safe update' UPDATED_BODY="$BODY_TEXT"
bash "$FIXTURE/update.sh"
[ "$(cat "$CAPTURE_BODY")" = "$BODY_TEXT" ]
[ ! -e "$(cat "$CAPTURE_BODY_PATH")" ]

echo "PR creator safety fixtures passed"
