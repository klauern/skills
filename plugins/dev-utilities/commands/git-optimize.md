---
allowed-tools: Bash
description: Optimize Git repository with branch cleanup and garbage collection
argument-hint: "[cleanup|trim|optimize|trimall]"
---

# /dev-utilities:git-optimize

Clean up merged branches and optimize repository size.

## Usage

```bash
/dev-utilities:git-optimize            # assess and recommend
/dev-utilities:git-optimize cleanup    # quick merged-branch cleanup
/dev-utilities:git-optimize trimall    # full workflow (can take hours)
```

## Behavior

Invoke the **git-optimize** skill:

1. Assess state: `git branch -vv`, `du -sh .git`, `git trim --dry-run` if installed.
2. Verify the skill's aliases exist (`git config alias.cleanup`); offer to install them
   or use the raw-git equivalents from the skill's command table.
3. Run the appropriate level (quick cleanup / weekly trim / deep optimize), warning
   before slow operations and using the skill's non-interactive git-trim strategy —
   never `yes | git trim`.
4. Verify results (`git branch`, `du -sh .git`) and remind about `git reflog` recovery.
