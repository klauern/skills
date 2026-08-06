#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT

rg -q -F '# trimall-workflow' "$SKILL_DIR/references/configuration.md"

git init --quiet --bare "$FIXTURE/origin.git"
git init --quiet "$FIXTURE/repo"
git -C "$FIXTURE/repo" config user.email fixture@example.com
git -C "$FIXTURE/repo" config user.name Fixture
git -C "$FIXTURE/repo" checkout --quiet -b main
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: base"

for branch in merged-delete staging develop release-keep; do
  git -C "$FIXTURE/repo" branch "$branch"
done
git -C "$FIXTURE/repo" checkout --quiet -b release/1
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: requested cleanup base"
git -C "$FIXTURE/repo" checkout --quiet main

git -C "$FIXTURE/repo" remote add origin "$FIXTURE/origin.git"
git -C "$FIXTURE/repo" push --quiet -u origin main
git -C "$FIXTURE/repo" remote set-head origin main
git -C "$FIXTURE/repo" config trim.bases develop
git -C "$FIXTURE/repo" config trim.exclude "staging release-*"
# This decoy would expand `release-*` during tokenization unless globbing is disabled.
touch "$FIXTURE/repo/release-decoy"

alias_cleanup=$(
  awk 'BEGIN{emit=0} /^\[alias\]/{emit=1} emit && /^```/{exit} emit{print}' \
    "$SKILL_DIR/references/configuration.md" |
    git config --file /dev/stdin --get alias.cleanup
)
alias_sweep=$(
  awk 'BEGIN{emit=0} /^\[alias\]/{emit=1} emit && /^```/{exit} emit{print}' \
    "$SKILL_DIR/references/configuration.md" |
    git config --file /dev/stdin --get alias.sweep
)
git -C "$FIXTURE/repo" config alias.cleanup "$alias_cleanup"
git -C "$FIXTURE/repo" config alias.sweep "$alias_sweep"

set +e
preview=$(printf 'n\n' | git -C "$FIXTURE/repo" cleanup)
preview_status=$?
set -e
[ "$preview_status" -ne 0 ] || {
  echo "cleanup cancellation must return a nonzero status" >&2
  exit 1
}
case "$preview" in
  *merged-delete*) ;;
  *) echo "eligible branch missing from preview" >&2; exit 1 ;;
esac
for protected in main staging develop release-keep; do
  case "$preview" in
    *"  $protected"*) echo "protected branch appeared in preview: $protected" >&2; exit 1 ;;
  esac
done

set +e
sweep_preview=$(printf 'n\n' | git -C "$FIXTURE/repo" sweep)
sweep_status=$?
set -e
[ "$sweep_status" -ne 0 ]
case "$sweep_preview" in
  *merged-delete*) ;;
  *) echo "configured-base sweep omitted eligible branch" >&2; exit 1 ;;
esac

set +e
requested_preview=$(printf 'n\n' | git -C "$FIXTURE/repo" cleanup release/1)
requested_status=$?
set -e
[ "$requested_status" -ne 0 ]
case "$requested_preview" in
  *"  release/1"*) echo "requested base appeared in preview: release/1" >&2; exit 1 ;;
esac

printf 'yes\n' | git -C "$FIXTURE/repo" cleanup >/dev/null
if git -C "$FIXTURE/repo" show-ref --verify --quiet refs/heads/merged-delete; then
  echo "eligible branch was not deleted" >&2
  exit 1
fi
for protected in main staging develop release-keep; do
  git -C "$FIXTURE/repo" show-ref --verify --quiet "refs/heads/$protected"
done
git -C "$FIXTURE/repo" show-ref --verify --quiet refs/heads/release/1

alias_trimall=$(
  awk 'BEGIN{emit=0} /^\[alias\]/{emit=1} emit && /^```/{exit} emit{print}' \
    "$SKILL_DIR/references/configuration.md" |
    git config --file /dev/stdin --get alias.trimall
)
alias_pruner=$(
  awk 'BEGIN{emit=0} /^\[alias\]/{emit=1} emit && /^```/{exit} emit{print}' \
    "$SKILL_DIR/references/configuration.md" |
    git config --file /dev/stdin --get alias.pruner
)
alias_repacker=$(
  awk 'BEGIN{emit=0} /^\[alias\]/{emit=1} emit && /^```/{exit} emit{print}' \
    "$SKILL_DIR/references/configuration.md" |
    git config --file /dev/stdin --get alias.repacker
)
alias_optimize=$(
  awk 'BEGIN{emit=0} /^\[alias\]/{emit=1} emit && /^```/{exit} emit{print}' \
    "$SKILL_DIR/references/configuration.md" |
    git config --file /dev/stdin --get alias.optimize
)
git -C "$FIXTURE/repo" config alias.trimall "$alias_trimall"
git -C "$FIXTURE/repo" config alias.pruner "$alias_pruner"
git -C "$FIXTURE/repo" config alias.repacker "$alias_repacker"
git -C "$FIXTURE/repo" config alias.optimize "$alias_optimize"
phase_log="$FIXTURE/phases"
nested_phase_log="$FIXTURE/nested-phases"
origin_url=$(git -C "$FIXTURE/repo" remote get-url origin)
mkdir "$FIXTURE/bin"
real_git=$(command -v git)
cat >"$FIXTURE/bin/git" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

phase=${1:-}
# Top-level invocations pass "-C <repo>" first; the subcommand is arg 3 there.
if [ "$phase" = -C ]; then
  phase=${3:-}
fi
status=0
case "$phase" in
  pruner) status=${PRUNER_STATUS:-0} ;;
  prune) status=${PRUNE_STATUS:-0} ;;
  reflog) status=${REFLOG_STATUS:-0} ;;
  repacker) status=${REPACKER_STATUS:-0} ;;
  prune-packed) status=${PRUNE_PACKED_STATUS:-0} ;;
  *) exec "$REAL_GIT" "$@" ;;
esac

if [ -n "${NESTED_PHASE_LOG:-}" ]; then
  printf '%s\n' "$phase" >>"$NESTED_PHASE_LOG"
fi
[ "$status" -eq 0 ] || exit "$status"
exec "$REAL_GIT" "$@"
EOF
cat >"$FIXTURE/bin/git-trim" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo trim >>"$PHASE_LOG"
exit "${TRIM_STATUS:-0}"
EOF
chmod +x "$FIXTURE/bin/git" "$FIXTURE/bin/git-trim"

# Fetch failure stops before dry-run or any destructive phase.
git -C "$FIXTURE/repo" config remote.origin.url "$FIXTURE/missing-origin.git"
if PATH="$FIXTURE/bin:$PATH" REAL_GIT="$real_git" PHASE_LOG="$phase_log" \
  git -C "$FIXTURE/repo" trimall >"$FIXTURE/fetch.out" 2>"$FIXTURE/fetch.err"; then
  echo "trimall unexpectedly survived fetch failure" >&2
  exit 1
fi
[ ! -e "$phase_log" ]
rg -q -F 'Fetch failed; stopping.' "$FIXTURE/fetch.err"
git -C "$FIXTURE/repo" config remote.origin.url "$origin_url"

# Dry-run failure stops before cleanup, sweep, or optimize.
: >"$phase_log"
if PATH="$FIXTURE/bin:$PATH" REAL_GIT="$real_git" PHASE_LOG="$phase_log" TRIM_STATUS=1 \
  git -C "$FIXTURE/repo" trimall >"$FIXTURE/trim.out" 2>"$FIXTURE/trim.err"; then
  echo "trimall unexpectedly survived dry-run failure" >&2
  exit 1
fi
[ "$(cat "$phase_log")" = trim ]
rg -q -F 'git trim dry-run failed; stopping.' "$FIXTURE/trim.err"

# Cleanup cancellation/failure stops before sweep and optimize.
: >"$phase_log"
git -C "$FIXTURE/repo" config alias.cleanup \
  "!echo cleanup >>\"$phase_log\"; exit 1"
git -C "$FIXTURE/repo" config alias.sweep \
  "!echo sweep >>\"$phase_log\""
git -C "$FIXTURE/repo" config alias.optimize \
  "!echo optimize >>\"$phase_log\""
if printf 'yes\n' | PATH="$FIXTURE/bin:$PATH" REAL_GIT="$real_git" PHASE_LOG="$phase_log" \
  git -C "$FIXTURE/repo" trimall \
  >"$FIXTURE/cleanup.out" 2>"$FIXTURE/cleanup.err"; then
  echo "trimall unexpectedly survived cleanup cancellation" >&2
  exit 1
fi
[ "$(cat "$phase_log")" = "$(printf 'trim\ncleanup')" ]
rg -q -F 'Cleanup failed or was cancelled; stopping.' "$FIXTURE/cleanup.err"

# With every phase successful, the authoritative sequence reaches optimize in order.
: >"$phase_log"
git -C "$FIXTURE/repo" config alias.cleanup \
  "!echo cleanup >>\"$phase_log\""
printf 'yes\n' | PATH="$FIXTURE/bin:$PATH" PHASE_LOG="$phase_log" \
  REAL_GIT="$real_git" git -C "$FIXTURE/repo" trimall >/dev/null
[ "$(cat "$phase_log")" = "$(printf 'trim\ncleanup\nsweep\noptimize')" ]
git -C "$FIXTURE/repo" config alias.pruner "$alias_pruner"
git -C "$FIXTURE/repo" config alias.repacker "$alias_repacker"
git -C "$FIXTURE/repo" config alias.optimize "$alias_optimize"

# External git-* scripts shadow same-named aliases, so these nested-workflow
# helpers must be created only AFTER the alias-based trimall assertions above.
{
  printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail'
  # Route nested git calls through the shim: git prepends its exec-path to PATH
  # when running external git-* commands, which would otherwise bypass it.
  printf 'git() { "%s" "$@"; }\n' "$FIXTURE/bin/git"
  printf '%s\n' "${alias_pruner#!}"
} >"$FIXTURE/bin/git-pruner"
{
  printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail'
  # Route nested git calls through the shim: git prepends its exec-path to PATH
  # when running external git-* commands, which would otherwise bypass it.
  printf 'git() { "%s" "$@"; }\n' "$FIXTURE/bin/git"
  printf '%s\n' "${alias_repacker#!}"
} >"$FIXTURE/bin/git-repacker"
{
  printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail'
  # Route nested git calls through the shim: git prepends its exec-path to PATH
  # when running external git-* commands, which would otherwise bypass it.
  printf 'git() { "%s" "$@"; }\n' "$FIXTURE/bin/git"
  printf '%s\n' "${alias_optimize#!}"
} >"$FIXTURE/bin/git-optimize"
chmod +x "$FIXTURE/bin/git-pruner" "$FIXTURE/bin/git-repacker" \
  "$FIXTURE/bin/git-optimize"

# The pruner itself stops before reflog expiration when prune fails.
: >"$nested_phase_log"
if PATH="$FIXTURE/bin:$PATH" REAL_GIT="$real_git" \
  NESTED_PHASE_LOG="$nested_phase_log" PRUNE_STATUS=1 \
  git -C "$FIXTURE/repo" pruner >/dev/null 2>&1; then
  echo "pruner unexpectedly survived prune failure" >&2
  exit 1
fi
[ "$(cat "$nested_phase_log")" = "$(printf 'pruner\nprune')" ]

assert_nested_optimize_failure() {
  expected=$1
  status_name=$2
  : >"$nested_phase_log"
  if printf 'yes\n' | env PATH="$FIXTURE/bin:$PATH" REAL_GIT="$real_git" \
    PHASE_LOG="$phase_log" NESTED_PHASE_LOG="$nested_phase_log" \
    "$status_name=1" git -C "$FIXTURE/repo" trimall \
    >"$FIXTURE/$expected.out" 2>"$FIXTURE/$expected.err"; then
    echo "trimall unexpectedly survived nested $expected failure" >&2
    exit 1
  fi
  [ "$(tail -n 1 "$FIXTURE/$expected.err")" = "Optimize failed; stopping." ]
  if rg -q -F 'Done!' "$FIXTURE/$expected.out"; then
    echo "trimall printed Done after nested $expected failure" >&2
    exit 1
  fi
}

# A failed delegated pruner prevents repacker and prune-packed.
assert_nested_optimize_failure pruner PRUNER_STATUS
[ "$(cat "$nested_phase_log")" = pruner ]

# Later delegated phases also propagate nonzero and stop their successors.
assert_nested_optimize_failure repacker REPACKER_STATUS
[ "$(cat "$nested_phase_log")" = "$(printf 'pruner\nprune\nreflog\nrepacker')" ]
assert_nested_optimize_failure prune-packed PRUNE_PACKED_STATUS
[ "$(cat "$nested_phase_log")" = \
  "$(printf 'pruner\nprune\nreflog\nrepacker\nprune-packed')" ]

echo "cleanup and trimall fail-fast fixtures passed"
