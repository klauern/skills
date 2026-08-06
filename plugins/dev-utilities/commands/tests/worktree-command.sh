#!/usr/bin/env bash
set -euo pipefail

COMMAND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT

marker='<!-- worktree-create-workflow -->'
[ "$(rg -c -F "$marker" "$COMMAND_DIR/worktree.md")" -eq 1 ]
workflow=$(
  awk -v marker="$marker" '
    index($0, marker) { marked = 1; next }
    marked && /^[[:space:]]*```bash$/ { capture = 1; next }
    capture && /^[[:space:]]*```$/ { exit }
    capture { sub(/^  /, ""); print }
  ' "$COMMAND_DIR/worktree.md"
)
[ -n "$workflow" ]

git init --quiet --bare "$FIXTURE/origin.git"
git clone --quiet "$FIXTURE/origin.git" "$FIXTURE/repo"
git -C "$FIXTURE/repo" config user.email fixture@example.com
git -C "$FIXTURE/repo" config user.name Fixture
git -C "$FIXTURE/repo" checkout --quiet -b main
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: initial default"
git -C "$FIXTURE/repo" push --quiet -u origin main
git -C "$FIXTURE/origin.git" symbolic-ref HEAD refs/heads/main
git -C "$FIXTURE/repo" remote set-head origin --auto >/dev/null
mkdir -p "$FIXTURE/repo/nested/deeper"

git clone --quiet "$FIXTURE/origin.git" "$FIXTURE/publisher"
git -C "$FIXTURE/publisher" config user.email fixture@example.com
git -C "$FIXTURE/publisher" config user.name Fixture

git -C "$FIXTURE/repo" branch local/topic
local_oid=$(git -C "$FIXTURE/repo" rev-parse local/topic)

git -C "$FIXTURE/publisher" checkout --quiet -b remote/cached origin/main
git -C "$FIXTURE/publisher" commit --quiet --allow-empty -m "test: cached remote"
git -C "$FIXTURE/publisher" push --quiet origin remote/cached
cached_oid=$(git -C "$FIXTURE/publisher" rev-parse HEAD)
git -C "$FIXTURE/repo" fetch --quiet --no-tags origin \
  "+refs/heads/remote/cached:refs/remotes/origin/remote/cached"

git -C "$FIXTURE/publisher" checkout --quiet -b remote/unfetched origin/main
git -C "$FIXTURE/publisher" commit --quiet --allow-empty -m "test: unfetched remote"
git -C "$FIXTURE/publisher" push --quiet origin remote/unfetched
unfetched_oid=$(git -C "$FIXTURE/publisher" rev-parse HEAD)
[ ! -e "$FIXTURE/repo/.git/refs/remotes/origin/remote/unfetched" ]
if git -C "$FIXTURE/repo" show-ref --verify --quiet \
  refs/remotes/origin/remote/unfetched; then
  echo "unfetched fixture unexpectedly has a tracking ref" >&2
  exit 1
fi

# Rename the server default while leaving the primary clone's cached origin/HEAD stale.
git -C "$FIXTURE/publisher" checkout --quiet -b trunk origin/main
git -C "$FIXTURE/publisher" commit --quiet --allow-empty -m "test: renamed default"
git -C "$FIXTURE/publisher" push --quiet origin trunk
trunk_oid=$(git -C "$FIXTURE/publisher" rev-parse HEAD)
git -C "$FIXTURE/origin.git" symbolic-ref HEAD refs/heads/trunk
[ "$(git -C "$FIXTURE/repo" symbolic-ref --short refs/remotes/origin/HEAD)" = \
  origin/main ]

# Diverge caller HEAD so a new branch cannot accidentally inherit caller ancestry.
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: caller-only commit"
caller_oid=$(git -C "$FIXTURE/repo" rev-parse HEAD)
[ "$caller_oid" != "$trunk_oid" ]

run_workflow() {
  branch=$1
  (cd "$FIXTURE/repo/nested/deeper" && BRANCH="$branch" bash -c "$workflow") \
    >"$FIXTURE/${branch//\//-}.out" 2>"$FIXTURE/${branch//\//-}.err"
}

run_workflow local/topic
[ "$(git -C "$FIXTURE/repo-local-topic" rev-parse HEAD)" = "$local_oid" ]

run_workflow remote/cached
[ "$(git -C "$FIXTURE/repo-remote-cached" rev-parse HEAD)" = "$cached_oid" ]
[ "$(git -C "$FIXTURE/repo-remote-cached" rev-parse --abbrev-ref '@{upstream}')" = \
  origin/remote/cached ]

run_workflow remote/unfetched
[ "$(git -C "$FIXTURE/repo-remote-unfetched" rev-parse HEAD)" = "$unfetched_oid" ]
[ "$(git -C "$FIXTURE/repo-remote-unfetched" rev-parse --abbrev-ref '@{upstream}')" = \
  origin/remote/unfetched ]

run_workflow feature/from-server-default
[ "$(git -C "$FIXTURE/repo-feature-from-server-default" rev-parse HEAD)" = \
  "$trunk_oid" ]
[ "$(git -C "$FIXTURE/repo" symbolic-ref --short refs/remotes/origin/HEAD)" = \
  origin/trunk ]
[ "$(git -C "$FIXTURE/repo-feature-from-server-default" rev-parse HEAD)" != \
  "$caller_oid" ]

echo "worktree workflow fixtures passed: local, cached, unfetched, and server-default"
