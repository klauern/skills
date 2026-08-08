---
allowed-tools: Bash
description: Commit and push with Conventional Commits
---

# /commits:commit-push

`$ARGUMENTS` optionally names a target branch directly or in a phrase such as `to main`.

## Workflow

1. Parse and validate any target branch from `$ARGUMENTS`.
2. Honor an explicit target; otherwise, create a descriptive feature branch when currently on `main` or `master`.
3. Invoke the **conventional-commits** skill for change analysis, atomic split decisions, staging, message composition, and commit creation. It must inspect the full tracked diff and every untracked file before staging or composing messages.
4. Create all requested commits before the single push step below.
5. Run this upstream-aware push and local-cleanliness check exactly in sequence:

```bash
# BEGIN COMMIT_PUSH_REMOTE
if git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' >/dev/null 2>&1; then
  git push
else
  git push -u origin HEAD
fi && git status --short --branch
# END COMMIT_PUSH_REMOTE
```

The successful push exit status proves remote acceptance; `git status` only inspects local cleanliness and tracking. Stop and report any push failure.
