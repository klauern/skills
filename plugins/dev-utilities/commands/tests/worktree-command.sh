#!/usr/bin/env bash
set -euo pipefail

COMMAND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT

rg -q -F 'ROOT="$(git rev-parse --show-toplevel)"' "$COMMAND_DIR/worktree.md"
rg -q -F 'refs/remotes/origin/HEAD' "$COMMAND_DIR/worktree.md"
rg -q -F 'refs/heads/$BRANCH' "$COMMAND_DIR/worktree.md"
rg -q -F 'refs/remotes/origin/$BRANCH' "$COMMAND_DIR/worktree.md"
rg -q -F 'git ls-remote --exit-code --heads origin' "$COMMAND_DIR/worktree.md"
rg -q -F '+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH' "$COMMAND_DIR/worktree.md"

git init --quiet --bare "$FIXTURE/origin.git"
git clone --quiet "$FIXTURE/origin.git" "$FIXTURE/repo"
git -C "$FIXTURE/repo" config user.email fixture@example.com
git -C "$FIXTURE/repo" config user.name Fixture
git -C "$FIXTURE/repo" checkout --quiet -b main
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: base"
git -C "$FIXTURE/repo" push --quiet -u origin main
git -C "$FIXTURE/origin.git" symbolic-ref HEAD refs/heads/main
git -C "$FIXTURE/repo" remote set-head origin --auto >/dev/null
mkdir -p "$FIXTURE/repo/nested/deeper"

# Publish a remote branch without updating the primary clone's tracking refs.
git clone --quiet "$FIXTURE/origin.git" "$FIXTURE/publisher"
git -C "$FIXTURE/publisher" config user.email fixture@example.com
git -C "$FIXTURE/publisher" config user.name Fixture
git -C "$FIXTURE/publisher" checkout --quiet -b remote/unfetched origin/main
git -C "$FIXTURE/publisher" commit --quiet --allow-empty -m "test: unfetched remote tip"
git -C "$FIXTURE/publisher" push --quiet -u origin remote/unfetched
if git -C "$FIXTURE/repo" show-ref --verify --quiet refs/remotes/origin/remote/unfetched; then
  echo "unfetched fixture unexpectedly has a local tracking ref" >&2
  exit 1
fi

# Advance caller HEAD locally; a new worktree must still start from origin/HEAD.
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: caller-only commit"
caller_oid=$(git -C "$FIXTURE/repo" rev-parse HEAD)

# Advance origin/main independently, refresh only the remote-tracking ref, and prove
# the caller and remote-default tips diverged from their common base.
git -C "$FIXTURE/publisher" checkout --quiet main
git -C "$FIXTURE/publisher" commit --quiet --allow-empty -m "test: remote-default-only commit"
git -C "$FIXTURE/publisher" push --quiet origin main
git -C "$FIXTURE/repo" fetch --quiet --no-tags origin \
  "+refs/heads/main:refs/remotes/origin/main"
origin_oid=$(git -C "$FIXTURE/repo" rev-parse refs/remotes/origin/main)
[ "$(git -C "$FIXTURE/repo" rev-parse HEAD)" = "$caller_oid" ]
if git -C "$FIXTURE/repo" merge-base --is-ancestor "$caller_oid" "$origin_oid"; then
  echo "caller tip unexpectedly remains an ancestor of origin/main" >&2
  exit 1
fi
if git -C "$FIXTURE/repo" merge-base --is-ancestor "$origin_oid" "$caller_oid"; then
  echo "origin/main unexpectedly remains an ancestor of caller tip" >&2
  exit 1
fi

ROOT=$(git -C "$FIXTURE/repo/nested/deeper" rev-parse --show-toplevel)
REPO=$(basename "$ROOT")
DEFAULT_REMOTE=$(git -C "$FIXTURE/repo/nested/deeper" symbolic-ref --quiet --short refs/remotes/origin/HEAD)
BRANCH=feature/from-default
DIR="$(dirname "$ROOT")/${REPO}-${BRANCH//\//-}"
git -C "$FIXTURE/repo/nested/deeper" worktree add --quiet -b "$BRANCH" -- "$DIR" "$DEFAULT_REMOTE"

base_oid=$(git -C "$FIXTURE/repo" rev-parse "$DEFAULT_REMOTE")
branch_oid=$(git -C "$DIR" rev-parse HEAD)
[ "$branch_oid" = "$base_oid" ]
[ "$branch_oid" != "$caller_oid" ]
case "$DIR" in
  "$ROOT"/*) echo "worktree was created inside repository root" >&2; exit 1 ;;
esac

git -C "$ROOT" branch local/topic main
git -C "$ROOT" worktree add --quiet -- "$FIXTURE/local-topic" local/topic
git -C "$ROOT" branch remote/topic main
git -C "$ROOT" push --quiet origin remote/topic
git -C "$ROOT" branch -D remote/topic >/dev/null
git -C "$ROOT" fetch --quiet --no-tags origin \
  "+refs/heads/remote/topic:refs/remotes/origin/remote/topic"
git -C "$ROOT" worktree add --quiet --track -b remote/topic -- "$FIXTURE/remote-topic" origin/remote/topic

REMOTE_BRANCH=remote/unfetched
REMOTE_LINE=$(git -C "$ROOT" ls-remote --exit-code --heads origin "refs/heads/$REMOTE_BRANCH")
REMOTE_OID=$(printf '%s\n' "$REMOTE_LINE" | awk 'NR == 1 {print $1}')
git -C "$ROOT" fetch --quiet --no-tags origin \
  "+refs/heads/$REMOTE_BRANCH:refs/remotes/origin/$REMOTE_BRANCH"
FETCHED_OID=$(git -C "$ROOT" rev-parse "refs/remotes/origin/$REMOTE_BRANCH")
[ "$FETCHED_OID" = "$REMOTE_OID" ]
git -C "$ROOT" worktree add --quiet --track -b "$REMOTE_BRANCH" -- \
  "$FIXTURE/remote-unfetched" "origin/$REMOTE_BRANCH"
[ "$(git -C "$FIXTURE/remote-unfetched" rev-parse HEAD)" = "$REMOTE_OID" ]

echo "worktree fixtures passed"
