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
  <!-- worktree-create-workflow -->
  ```bash
  set -euo pipefail

  # Resolve from the repository root, even when invoked in a nested directory.
  ROOT="$(git rev-parse --show-toplevel)"
  REPO="$(basename "$ROOT")"
  DIR="$(dirname "$ROOT")/${REPO}-${BRANCH//\//-}"

  # Reject option-like/invalid input before classifying the branch.
  git check-ref-format --branch "$BRANCH" >/dev/null

  create_remote_worktree() {
    remote_line=$1
    if ! remote_oid="$(printf '%s\n' "$remote_line" | awk \
      -v expected="refs/heads/$BRANCH" '
        NF == 2 && $2 == expected && count == 0 { oid = $1; count++; next }
        { invalid = 1 }
        END {
          if (!invalid && count == 1 && oid ~ /^[0-9a-f]+$/) print oid
          else exit 1
        }
      ')"; then
      echo "Unexpected ls-remote response for origin/$BRANCH" >&2
      exit 1
    fi
    if ! git fetch --no-tags origin \
      "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"; then
      echo "Could not fetch origin/$BRANCH" >&2
      exit 1
    fi
    fetched_oid="$(git rev-parse --verify "refs/remotes/origin/$BRANCH^{commit}")"
    [ "$fetched_oid" = "$remote_oid" ] || {
      echo "origin/$BRANCH changed while it was being fetched; retry." >&2
      exit 1
    }
    git worktree add --track -b "$BRANCH" -- "$DIR" "origin/$BRANCH"
  }

  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    # Existing local branch. Git reports visibly if another worktree owns it.
    git worktree add -- "$DIR" "$BRANCH"
  elif git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
    # Cached remote branch: revalidate it against the server before use.
    if ! REMOTE_LINE="$(git ls-remote --exit-code --heads origin \
      "refs/heads/$BRANCH")"; then
      echo "Cached origin/$BRANCH no longer exists or cannot be verified." >&2
      exit 1
    fi
    create_remote_worktree "$REMOTE_LINE"
  elif REMOTE_LINE="$(git ls-remote --exit-code --heads origin "refs/heads/$BRANCH")"; then
    # Unfetched remote branch.
    create_remote_worktree "$REMOTE_LINE"
  else
    REMOTE_STATUS=$?
    [ "$REMOTE_STATUS" -eq 2 ] || exit "$REMOTE_STATUS"
    # New branch: resolve the server's current HEAD, not the local symbolic-ref cache.
    if ! DEFAULT_INFO="$(git ls-remote --symref origin HEAD)"; then
      echo "Could not resolve origin's default branch." >&2
      exit 1
    fi
    DEFAULT_REF="$(printf '%s\n' "$DEFAULT_INFO" | awk \
      '$1 == "ref:" && $3 == "HEAD" { print $2 }')"
    DEFAULT_OID="$(printf '%s\n' "$DEFAULT_INFO" | awk \
      '$1 != "ref:" && $2 == "HEAD" { print $1 }')"
    case "$DEFAULT_REF" in
      refs/heads/*) DEFAULT_BRANCH=${DEFAULT_REF#refs/heads/} ;;
      *) echo "origin HEAD is not a branch symbolic ref." >&2; exit 1 ;;
    esac
    [ -n "$DEFAULT_OID" ] || {
      echo "origin HEAD did not resolve to a commit." >&2
      exit 1
    }
    if ! git fetch --no-tags origin \
      "+$DEFAULT_REF:refs/remotes/origin/$DEFAULT_BRANCH"; then
      echo "Could not fetch origin/$DEFAULT_BRANCH" >&2
      exit 1
    fi
    FETCHED_DEFAULT_OID="$(git rev-parse --verify \
      "refs/remotes/origin/$DEFAULT_BRANCH^{commit}")"
    [ "$FETCHED_DEFAULT_OID" = "$DEFAULT_OID" ] || {
      echo "origin HEAD changed while it was being fetched; retry." >&2
      exit 1
    }
    git symbolic-ref refs/remotes/origin/HEAD \
      "refs/remotes/origin/$DEFAULT_BRANCH"
    git worktree add -b "$BRANCH" -- "$DIR" \
      "refs/remotes/origin/$DEFAULT_BRANCH"
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
