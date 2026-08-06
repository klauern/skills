#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT

rg -q -F 'git ls-remote --exit-code --heads origin' "$SKILL_DIR/SKILL.md"
rg -q -F '[ "$current_oid" = "$reviewed_oid" ]' "$SKILL_DIR/SKILL.md"
rg -q -F -- '--force-with-lease="refs/heads/$branch:$reviewed_oid"' "$SKILL_DIR/SKILL.md"

git init --quiet --bare "$FIXTURE/origin.git"
git init --quiet "$FIXTURE/repo"
git -C "$FIXTURE/repo" config user.email fixture@example.com
git -C "$FIXTURE/repo" config user.name Fixture
git -C "$FIXTURE/repo" checkout --quiet -b main
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: base"
git -C "$FIXTURE/repo" remote add origin "$FIXTURE/origin.git"
git -C "$FIXTURE/repo" push --quiet -u origin main
git -C "$FIXTURE/repo" branch feature/race
git -C "$FIXTURE/repo" push --quiet origin feature/race

reviewed_oid=$(git -C "$FIXTURE/repo" ls-remote --exit-code --heads origin refs/heads/feature/race | awk '{print $1}')
git -C "$FIXTURE/repo" checkout --quiet feature/race
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: remote branch advances"
git -C "$FIXTURE/repo" push --quiet origin feature/race
current_oid=$(git -C "$FIXTURE/repo" ls-remote --exit-code --heads origin refs/heads/feature/race | awk '{print $1}')

if [ "$current_oid" = "$reviewed_oid" ]; then
  echo "fixture did not advance the remote ref" >&2
  exit 1
fi

# A second update after the client check must make the lease-protected delete fail.
leased_oid=$current_oid
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: remote branch advances after check"
git -C "$FIXTURE/repo" push --quiet origin feature/race
if git -C "$FIXTURE/repo" push \
  --force-with-lease="refs/heads/feature/race:$leased_oid" \
  origin --delete -- feature/race >/dev/null 2>&1; then
  echo "stale lease unexpectedly deleted the advanced remote ref" >&2
  exit 1
fi
git -C "$FIXTURE/repo" ls-remote --exit-code --heads origin refs/heads/feature/race >/dev/null

echo "remote-ref race fixture passed (deletion correctly remains unauthorized)"
