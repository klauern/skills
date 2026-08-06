---
name: git-optimize
description: This skill should be used when the user asks to "clean up merged git branches", "run git trim/cleanup", "optimize repository size", or "perform git maintenance and garbage collection".
version: 1.0.0
author: klauern
allowed-tools: Bash Read
---

# Git Optimize

Repository maintenance through branch cleanup and optimization operations.

## Quick Start

**Command**: `/git-optimize` — Clean branches and optimize repository

**Documentation**:
- [Configuration](references/configuration.md) — Alias and git-trim setup
- [Merge Detection](references/merge_detection.md) — How git-trim detects merges
- [Installation](references/installation.md) — git-trim installation

## When to Use

**Invoke when**:
- User asks to clean up branches or merged PRs
- Repository performance is slow or .git is large
- Preparing repository for archival
- Running maintenance workflows

**Don't use for**:
- Branch creation or checkout
- Commit operations
- Remote management (use standard git)

## Step 1 — Check Prerequisites

The convenience commands below are **git aliases, not built-ins**. Before using any of
them, verify they exist and offer to install the missing ones (definitions in
[configuration.md](references/configuration.md)):

```bash
git config alias.cleanup || echo "alias missing"
```

If the user prefers not to install aliases, use the raw-git equivalents in the table.

## Commands

| Alias | Raw-git equivalent | Purpose | Time |
|-------|--------------------|---------|------|
| `git cleanup` | `git branch --merged \| grep -vE '^\*\|master\|main' \| xargs -r git branch -d` | Delete branches merged to HEAD | Seconds |
| `git sweep` | same, against `master`/`develop` | Aggressive merged-branch cleanup | Seconds |
| `git trim` | external tool ([git-trim](references/installation.md)) | Smart detection (merged/stray/squash) | Seconds |
| `git pruner` | `git reflog expire --expire=now --all && git gc --prune=now` | Remove unreachable objects | Minutes-Hours |
| `git repacker` | `git repack -a -d --depth=250 --window=250` | Optimal delta compression | Hours |
| `git optimize` | pruner + repacker + `git prune-packed` | Full optimization cycle | Hours |
| `git trimall` | fetch→trim→cleanup→sweep→optimize | Complete workflow | 10min-Hours |

## Workflows

**After PR merge** (daily):
```bash
BASE=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | cut -d/ -f2 || echo main)
git checkout "$BASE" && git pull && git cleanup
```

**Weekly maintenance**:
```bash
git fetch --all --prune && git trim --dry-run   # then delete per the strategy below
```

**Monthly deep clean**:
```bash
git trimall
```

## git-trim Execution Strategy (non-interactive)

git-trim's confirmation prompt uses terminal control sequences that break under pipes —
**never** use `yes | git trim` or `echo y | git trim`. Instead:

1. `git trim --dry-run` and parse the branch names under "Delete merged local branches:"
2. Delete each locally: `git branch -d <branch>`
3. Attempt remote deletion: `git push origin --delete <branch>`
4. Treat "remote ref does not exist" as success — the remote branch was already
   removed (e.g. by fetch --prune or the forge's delete-on-merge)
5. Verify with `git branch -vv`

Note: git-trim upstream (foriequal0/git-trim) has been unmaintained for years — it still
works, but prefer the raw-git equivalents when it misbehaves.

## Configuration

**Git-flow setup** (multiple base branches):
```bash
git config trim.bases "develop,master"
git config trim.exclude "staging production"
```

**Verify aliases**:
```bash
git config alias.cleanup
git config alias.trimall
```

See [configuration.md](references/configuration.md) for full alias definitions.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| git-trim not found | `brew install foriequal0/git-trim/git-trim` |
| Alias not working | Check `git config alias.<name>` |
| Repo still large | `git gc --prune=now --aggressive` |
| Stray branches flagged | `git log origin/main..<branch> --oneline` to check unmerged commits |

## Safety

**Always safe**: trim --dry-run, repacker (read-only / non-destructive)

**Review first — deletes branch refs**: cleanup, sweep, trimall (run a dry run or
review `git branch --merged` output before deleting)

**Use caution**: pruner (removes objects), optimize, sweep -f

**Best practices**:
1. Use `--dry-run` first
2. Push important work before aggressive cleanup
3. Schedule optimize/repacker overnight
4. Use `git reflog` for recovery

