#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT

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

preview=$(printf 'n\n' | git -C "$FIXTURE/repo" cleanup)
case "$preview" in
  *merged-delete*) ;;
  *) echo "eligible branch missing from preview" >&2; exit 1 ;;
esac
for protected in main staging develop release-keep; do
  case "$preview" in
    *"  $protected"*) echo "protected branch appeared in preview: $protected" >&2; exit 1 ;;
  esac
done

sweep_preview=$(printf 'n\n' | git -C "$FIXTURE/repo" sweep)
case "$sweep_preview" in
  *merged-delete*) ;;
  *) echo "configured-base sweep omitted eligible branch" >&2; exit 1 ;;
esac

requested_preview=$(printf 'n\n' | git -C "$FIXTURE/repo" cleanup release/1)
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

echo "cleanup alias fixture passed"
