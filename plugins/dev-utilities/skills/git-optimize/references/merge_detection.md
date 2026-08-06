# Merge Detection

Git-trim detects merged branches across different merge styles.

## Branch States

| State | Description | Safe to Delete |
|-------|-------------|----------------|
| Merged | Upstream exists, all commits integrated into base | Yes |
| Stray | Upstream deleted, may have unmerged commits | Confirm first |
| Orphan | No upstream tracking configured | Only if not needed |

## Merge Style Detection

### Classic Merge (Merge Commit)
```bash
# Detection: ancestry check
git merge-base --is-ancestor <branch> <base>
```

### Rebase/Fast-Forward
```bash
# Detection: cherry comparison (matches patch IDs)
git cherry <base> <branch>  # Empty = merged
```

### Squash Merge
- Compares patch content heuristically
- Less reliable (may fail if squash commit edited)

## Manual Verification

```bash
# ANCESTRY checks — valid for classic merges only; a squash- or rebase-merged
# branch still shows unique commits here:
git log origin/main..feature/branch --oneline   # Empty = merged (classic only)
git merge-base --is-ancestor feature/branch origin/main && echo "MERGED"

# For squash/rebase merges use patch comparison instead:
git cherry origin/main feature/branch  # Empty = all patches present upstream
```

## Base Branch Detection Order

1. User config: `git config trim.bases`
2. Remote HEAD: `git symbolic-ref refs/remotes/origin/HEAD`
3. Common names: main, master, develop
4. None found → stop and ask the user (never fall back to the current branch —
   comparing a branch with itself yields an empty range and false "merged" results)

## Edge Cases

| Scenario | Result | Action |
|----------|--------|--------|
| Force-pushed after merge | May show as STRAY | Check reflog |
| Amended commits post-merge | Patch IDs mismatch | May show unmerged |
| Partial cherry-pick | Unmerged | Manual cleanup |
| Submodules | Not recursive | Run trim separately |
