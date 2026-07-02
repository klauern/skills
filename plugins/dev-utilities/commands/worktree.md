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
  # Sibling directory named <repo>-<branch> keeps worktrees out of the repo itself
  REPO="$(basename "$(git rev-parse --show-toplevel)")"
  DIR="../${REPO}-${BRANCH//\//-}"
  # Existing branch: check it out; new branch: create from the default branch
  git worktree add "$DIR" "$BRANCH" 2>/dev/null || git worktree add -b "$BRANCH" "$DIR"
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
