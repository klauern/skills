---
allowed-tools: Bash, AskUserQuestion
description: Analyze changes and split them into multiple atomic commits with proper conventional commit messages.
---

# /commits:commit-split

Split the working tree's mixed changes into multiple atomic conventional commits.

## Behavior

Invoke the **commit-splitter** skill:

1. Analyze the full diff and categorize changes (type, scope, logical purpose).
2. Present the skill's split plan (commit count, per-commit type/scope/files, order).
3. Confirm or adjust the plan with AskUserQuestion before touching the index.
4. Execute: stage per group (file-level `git add`, or hunk-level per the skill for mixed
   files) and commit each with a heredoc conventional message.
5. Show `git log --oneline -n <count>` to verify the result.
