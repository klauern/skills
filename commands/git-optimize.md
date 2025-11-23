---
allowed-tools: Bash
description: Optimize Git repository with branch cleanup and garbage collection
---

## Instructions

This command helps you optimize your Git repository using your configured aliases and git-trim.

1. **Check what optimization is needed**:
   - Run `git branch -vv` to see branch tracking status
   - Run `du -sh .git` to check repository size
   - Run `git trim --dry-run` if git-trim is installed

2. **Determine the appropriate optimization level**:
   - **Quick cleanup** (after PR merge): Use `git cleanup`
   - **Weekly maintenance**: Use `git trim` or `git sweep`
   - **Deep optimization** (monthly/quarterly): Use `git optimize`
   - **Full workflow**: Use `git trimall`

3. **Execute the chosen command**:
   - For quick operations: Run immediately
   - For heavy operations (optimize, trimall): Warn user about time commitment
   - Always show what will happen before executing

4. **Verify results**:
   - Run `git branch` to show remaining branches
   - Run `du -sh .git` to show size reduction (for optimize/trimall)
   - Confirm operation completed successfully

## Available Commands

### Fast Operations (Seconds)

**git cleanup**
- Removes branches merged into current HEAD
- Excludes current branch and master
- Safe deletion (uses -d flag)

**git sweep**
- Removes branches merged into master
- Excludes master, develop, and current branch
- Can use `git sweep -f` to force

**git-trim** (if installed)
- Smart merge detection (classic/rebase/squash)
- Interactive confirmation
- Use `git trim --dry-run` to preview

### Slow Operations (Minutes to Hours)

**git pruner**
- Removes unreachable objects
- Expires reflog immediately
- Reclaims space from deleted branches

**git repacker**
- Optimal delta compression
- Based on Linus Torvalds' recommendations
- Significantly reduces .git size

**git optimize**
- Combines pruner + repacker + prune-packed
- Full optimization cycle
- Best for monthly maintenance

**git trimall**
- Complete workflow:
  1. Fetch and prune remotes
  2. Run git-trim (all categories)
  3. Run cleanup
  4. Run sweep
  5. Run optimize
- One command for complete health

## Important Notes

- **git-trim** is optional but recommended. If not installed:
  ```bash
  brew install foriequal0/git-trim/git-trim
  ```
  Fallback to `git cleanup` and `git sweep` if unavailable.

- **Heavy operations** (`optimize`, `trimall`) can take hours on large repos.
  Always warn the user and suggest running during low-activity periods.

- **Safety**: Always use `--dry-run` or explain what will happen before destructive operations.

- **Recovery**: Remind users that deleted branches can be recovered via `git reflog` if needed.

## Example Interactions

**Quick cleanup**:
```
User: Clean up my merged branches
Assistant: I'll run git cleanup to remove branches merged into the current HEAD.
$ git cleanup
Deleted branch feature/old-feature (was abc1234).
Deleted branch bugfix/old-bug (was def5678).
```

**Weekly maintenance**:
```
User: Do my weekly git maintenance
Assistant: I'll run git trim to check for merged and stray branches.
$ git trim --dry-run
[Shows preview]
Proceed with deletion? [y/N] y
```

**Deep optimization**:
```
User: Optimize my repository
Assistant: I'll run git optimize to deeply optimize the repository.
Warning: This may take hours on large repos. Continue? [y/N] y
$ git optimize
[Shows progress]
```

**Full workflow**:
```
User: Run the complete git maintenance
Assistant: I'll run git trimall for complete repository health.
This includes:
1. Fetching and pruning remotes
2. Branch cleanup (git-trim + cleanup + sweep)
3. Repository optimization (pruner + repacker)

This may take 10 minutes to hours depending on repo size. Continue? [y/N] y
$ git trimall
```

## Configuration Check

Before running, optionally check:
```bash
# Verify aliases exist
git config alias.cleanup
git config alias.trimall
git config alias.optimize

# Check git-trim config
git config trim.bases
git config trim.exclude
```

## Error Handling

- If git-trim is not installed and user requests it, provide installation instructions
- If in a non-git directory, inform user and exit
- If no branches to clean, report success (nothing to do)
- If operations fail, show error and suggest recovery steps
