---
description: Create and manage git worktrees for parallel development work
allowed-tools: Bash
argument-hint: "[branch-name] | list | remove <branch-name>"
---

# /dev-utilities:worktree

Create, list, or remove git worktrees so multiple branches can be worked on in parallel checkouts.

## Behavior

Parse `$ARGUMENTS`:

- **A branch name** → create a worktree for it:
  ```bash
  # Resolve from the repository root, even when invoked in a nested directory.
  ROOT="$(git rev-parse --show-toplevel)"
  REPO="$(basename "$ROOT")"
  DIR="$(dirname "$ROOT")/${REPO}-${BRANCH//\//-}"

  # Reject option-like/invalid input before classifying the branch.
  git check-ref-format --branch "$BRANCH" >/dev/null

  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    # Existing local branch. Git reports visibly if another worktree owns it.
    git worktree add -- "$DIR" "$BRANCH"
  elif REMOTE_LINE="$(git ls-remote --exit-code --heads origin "refs/heads/$BRANCH")"; then
    # Remote-only branch: fetch only its exact ref and verify the fetched OID.
    REMOTE_OID="$(printf '%s\n' "$REMOTE_LINE" | awk 'NR == 1 {print $1}')"
    git fetch --no-tags origin \
      "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"
    FETCHED_OID="$(git rev-parse "refs/remotes/origin/$BRANCH")"
    [ "$FETCHED_OID" = "$REMOTE_OID" ] || {
      echo "origin/$BRANCH changed while it was being fetched; retry." >&2
      exit 1
    }
    git worktree add --track -b "$BRANCH" -- "$DIR" "origin/$BRANCH"
  else
    REMOTE_STATUS=$?
    [ "$REMOTE_STATUS" -eq 2 ] || exit "$REMOTE_STATUS"
    # New branch: always start at the resolved remote default, never caller HEAD.
    DEFAULT_REMOTE="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD)" || {
      echo "origin/HEAD is not configured; run 'git remote set-head origin --auto' or choose an existing branch." >&2
      exit 1
    }
    git worktree add -b "$BRANCH" -- "$DIR" "$DEFAULT_REMOTE"
  fi
  ```
  Report the created path so the user can `cd` into it.
- **`list` (or no argument)** → `git worktree list` and summarize each entry (path, branch, dirty state via `git -C <path> status --short`).
- **`remove <branch-name>`** → find the worktree path from `git worktree list`, then:
  ```bash
  git worktree remove "$DIR"   # add --force only if the user confirms discarding changes
  git worktree prune
  ```

## Notes

- Never remove a worktree with uncommitted changes without explicit confirmation.
- A branch checked out in any worktree cannot be checked out elsewhere — mention the existing path instead of failing silently.
- Never guess a default branch or retry a failed worktree operation with different
  ancestry. Report the exact Git error and stop.
