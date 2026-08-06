#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$(mktemp -d)"
BASE_RACE_PID=
cleanup() {
  if [ -n "$BASE_RACE_PID" ] && kill -0 "$BASE_RACE_PID" 2>/dev/null; then
    kill "$BASE_RACE_PID" 2>/dev/null || true
    wait "$BASE_RACE_PID" 2>/dev/null || true
  fi
  rm -r -- "$FIXTURE"
}
trap cleanup EXIT

after_merge_block=$(
  awk '
    /^\*\*After PR merge\*\*/ { section = 1; next }
    section && /^```bash$/ { capture = 1; next }
    capture && /^```$/ { exit }
    capture { print }
  ' "$SKILL_DIR/SKILL.md"
)
remote_deletion_block=$(
  awk '
    /^Example remote revalidation for one already-reviewed branch:/ { section = 1; next }
    section && /^```bash$/ { capture = 1; next }
    capture && /^```$/ { exit }
    capture { print }
  ' "$SKILL_DIR/SKILL.md"
)
[ -n "$after_merge_block" ]
[ -n "$remote_deletion_block" ]

git init --quiet --bare "$FIXTURE/origin.git"
git init --quiet "$FIXTURE/missing-default"
git -C "$FIXTURE/missing-default" remote add origin "$FIXTURE/origin.git"
if (cd "$FIXTURE/missing-default" && bash -eu -c "$after_merge_block") \
  >"$FIXTURE/missing-default.out" 2>"$FIXTURE/missing-default.err"; then
  echo "missing origin/HEAD unexpectedly passed the maintenance guard" >&2
  exit 1
fi
rg -q -F "origin/HEAD is unavailable" "$FIXTURE/missing-default.err"

git init --quiet "$FIXTURE/repo"
git -C "$FIXTURE/repo" config user.email fixture@example.com
git -C "$FIXTURE/repo" config user.name Fixture
git -C "$FIXTURE/repo" checkout --quiet -b main
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: base"
for branch in feature/success feature/base-race feature/unprotected feature/race; do
  git -C "$FIXTURE/repo" branch "$branch"
done
git -C "$FIXTURE/repo" remote add origin "$FIXTURE/origin.git"
git -C "$FIXTURE/repo" push --quiet -u origin main
git -C "$FIXTURE/origin.git" symbolic-ref HEAD refs/heads/main
git -C "$FIXTURE/repo" remote set-head origin --auto >/dev/null
git -C "$FIXTURE/repo" push --quiet origin \
  feature/success feature/base-race feature/unprotected feature/race

# Put every candidate behind the protected integration base.
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: integration base advances"
git -C "$FIXTURE/repo" push --quiet origin main

# The documented flow must reject a base outside the designated integration set.
if printf 'yes\n' | (
  cd "$FIXTURE/repo"
  env branch=feature/unprotected base_ref=origin/topic \
    BASE_IS_PROTECTED=yes bash -eu -c "$remote_deletion_block"
) >"$FIXTURE/unprotected.out" 2>"$FIXTURE/unprotected.err"; then
  echo "unprotected deletion base unexpectedly passed" >&2
  exit 1
fi
rg -q -F "Deletion base is not a designated protected integration branch" \
  "$FIXTURE/unprotected.err"
git -C "$FIXTURE/repo" ls-remote --exit-code --heads origin \
  refs/heads/feature/unprotected >/dev/null

# An unchanged protected base permits deletion through the exact candidate-OID lease.
printf 'yes\n' | (
  cd "$FIXTURE/repo"
  env branch=feature/success base_ref=origin/main \
    BASE_IS_PROTECTED=yes bash -eu -c "$remote_deletion_block"
) >"$FIXTURE/success.out" 2>"$FIXTURE/success.err"
if git -C "$FIXTURE/repo" ls-remote --exit-code --heads origin \
  refs/heads/feature/success >/dev/null; then
  echo "unchanged protected-base flow did not delete the reviewed candidate" >&2
  exit 1
fi

# Prepare an unrelated replacement for origin/main in a separate clone. Updating from
# that clone keeps the review client's origin/main stale until the documented re-fetch.
git clone --quiet "$FIXTURE/origin.git" "$FIXTURE/publisher"
git -C "$FIXTURE/publisher" config user.email fixture@example.com
git -C "$FIXTURE/publisher" config user.name Fixture
git -C "$FIXTURE/publisher" checkout --quiet --orphan rewritten-main
git -C "$FIXTURE/publisher" commit --quiet --allow-empty -m "test: rewritten base"
rewritten_base_oid=$(git -C "$FIXTURE/publisher" rev-parse HEAD)
reviewed_base_oid=$(git -C "$FIXTURE/repo" rev-parse refs/remotes/origin/main)
[ "$rewritten_base_oid" != "$reviewed_base_oid" ]

# Pause the exact documented flow at confirmation, rewrite the base, then answer yes.
# It must refresh origin/main, lose ancestry, and refuse deletion.
mkfifo "$FIXTURE/base-race.answer"
exec 3<>"$FIXTURE/base-race.answer"
(
  cd "$FIXTURE/repo"
  env branch=feature/base-race base_ref=origin/main \
    BASE_IS_PROTECTED=yes bash -eu -c "$remote_deletion_block"
) <&3 >"$FIXTURE/base-race.out" 2>"$FIXTURE/base-race.err" &
BASE_RACE_PID=$!

prompt_seen=
for _ in {1..100}; do
  if rg -q -F 'Delete origin/feature/base-race' "$FIXTURE/base-race.out" 2>/dev/null; then
    prompt_seen=yes
    break
  fi
  if ! kill -0 "$BASE_RACE_PID" 2>/dev/null; then
    break
  fi
  sleep 0.05
done
[ "$prompt_seen" = yes ] || {
  echo "documented deletion flow never reached confirmation" >&2
  exit 1
}

git -C "$FIXTURE/publisher" push --quiet --force origin \
  "$rewritten_base_oid:refs/heads/main"
printf 'yes\n' >&3
exec 3>&-
set +e
wait "$BASE_RACE_PID"
base_race_status=$?
set -e
BASE_RACE_PID=

[ "$base_race_status" -ne 0 ] || {
  echo "rewritten base unexpectedly allowed candidate deletion" >&2
  exit 1
}
[ "$(git -C "$FIXTURE/repo" rev-parse refs/remotes/origin/main)" = \
  "$rewritten_base_oid" ] || {
  echo "immediate pre-delete base refresh did not run" >&2
  exit 1
}
rg -q -F "Remote branch is no longer merged into refreshed" \
  "$FIXTURE/base-race.err"
git -C "$FIXTURE/repo" ls-remote --exit-code --heads origin \
  refs/heads/feature/base-race >/dev/null

# Preserve the candidate-side race proof: an exact-OID lease must reject a later update.
reviewed_oid=$(git -C "$FIXTURE/repo" ls-remote --exit-code --heads \
  origin refs/heads/feature/race | awk '{print $1}')
git -C "$FIXTURE/repo" checkout --quiet feature/race
git -C "$FIXTURE/repo" commit --quiet --allow-empty -m "test: remote branch advances"
git -C "$FIXTURE/repo" push --quiet origin feature/race
current_oid=$(git -C "$FIXTURE/repo" ls-remote --exit-code --heads \
  origin refs/heads/feature/race | awk '{print $1}')
[ "$current_oid" != "$reviewed_oid" ] || {
  echo "fixture did not advance the remote ref" >&2
  exit 1
}

leased_oid=$current_oid
git -C "$FIXTURE/repo" commit --quiet --allow-empty \
  -m "test: remote branch advances after check"
git -C "$FIXTURE/repo" push --quiet origin feature/race
if git -C "$FIXTURE/repo" push \
  --force-with-lease="refs/heads/feature/race:$leased_oid" \
  origin --delete -- feature/race >/dev/null 2>&1; then
  echo "stale lease unexpectedly deleted the advanced remote ref" >&2
  exit 1
fi
git -C "$FIXTURE/repo" ls-remote --exit-code --heads origin \
  refs/heads/feature/race >/dev/null

echo "remote deletion fixtures passed: base guards, base race, and candidate lease"
