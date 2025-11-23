# Merge Detection

## Overview

git-trim's key feature is detecting whether branches are truly merged into base branches, not just whether their upstream is deleted. This document explains how detection works for different merge styles.

## Branch States

### Merged Branch

A branch is considered **merged** when:
1. The upstream branch exists on the remote
2. All commits from the upstream are integrated into the base branch's upstream
3. No unique commits remain

**Safe to delete**: Yes

### Stray Branch

A branch is considered **stray** when:
1. The upstream branch no longer exists on the remote
2. The local branch may contain unmerged commits
3. Cannot verify merge status without upstream

**Safe to delete**: Requires caution and confirmation

### Orphan Branch

A branch is considered **orphan** when:
1. No upstream tracking branch is configured
2. Purely local development
3. No remote reference

**Safe to delete**: Only if you know it's not needed

## Merge Style Detection

### 1. Classic Merge (Merge Commit)

**Command**: `git merge --no-ff`

**Detection Method**: Ancestry check

```bash
# git-trim equivalent logic
git merge-base --is-ancestor <branch> <base>
```

**How it works**:
- Checks if branch tip is an ancestor of base
- Merge commits create clear parent relationships
- Most reliable detection method

**Example**:
```
main:    A---B---C---M
                    /
feature: D---E-----/
```

Branch `feature` is merged at commit M.

### 2. Rebase/Fast-Forward Merge

**Command**: `git merge --ff-only` or `git rebase && git merge`

**Detection Method**: Cherry comparison

```bash
# git-trim equivalent logic
git cherry <base> <branch>
```

**How it works**:
- Compares patch IDs of commits
- If all patches from branch exist in base (different commit SHAs)
- Branch is considered merged

**Example**:
```
main:    A---B---D'--E'
                /
feature: D---E   (original commits)
```

Commits D and E were rebased as D' and E'. Same patches, different SHAs.

### 3. Squash Merge

**Command**: `git merge --squash`

**Detection Method**: Patch content comparison

**How it works**:
- Generates a diff of all changes in the branch
- Searches base branch commits for identical patch content
- Uses heuristics to match squashed commits

**Example**:
```
main:    A---B---S
                /
feature: D---E   (squashed into S)
```

Commits D and E are squashed into commit S on main.

**Caveats**:
- Less reliable than other methods
- May fail if squash commit was edited
- Depends on commit message patterns

## Implementation Details

### Branch Classification Algorithm

```
for each local branch:
  1. Check if has upstream tracking branch
     NO -> classify as ORPHAN

  2. Check if upstream exists on remote
     NO -> classify as STRAY (may have unmerged changes)

  3. Check merge status using detection methods:
     a. Try ancestry check (merge commit)
     b. Try cherry comparison (rebase/ff)
     c. Try patch comparison (squash)

  4. If any method confirms merge:
     YES -> classify as MERGED
     NO -> classify as UNMERGED (keep)
```

### Parallel Execution

git-trim analyzes branches concurrently:
- Spawns multiple threads
- Each thread processes branch subset
- Significant speedup for repos with 50+ branches

### Base Branch Detection

Identifies base branches in order:

1. **User config**: `git config trim.bases` (e.g., "develop,master")
2. **Remote HEAD**: `git symbolic-ref refs/remotes/origin/HEAD`
3. **Common names**: Checks for `main`, `master`, `develop`
4. **Current branch**: Falls back to checking against current branch

## Edge Cases

### Force-Pushed Branches

If a branch was force-pushed after merge:
- May be flagged as STRAY (upstream gone)
- Manual review recommended
- Check `git reflog` to verify

### Amended Commits After Merge

If commits were amended post-merge:
- Patch IDs may not match
- Could fail squash detection
- May be flagged as unmerged

### Partial Merges

If only some commits from a branch were cherry-picked:
- Branch remains unmerged
- git-trim will not delete
- Manual cleanup required

### Submodule Branches

git-trim operates on the repository level:
- Does not automatically recurse into submodules
- Run git-trim separately in each submodule

## Verification

To manually verify a branch is merged:

```bash
# Check ancestry (merge commit)
git merge-base --is-ancestor feature/branch origin/main && echo "MERGED"

# Check cherry (rebase)
git cherry origin/main feature/branch
# Empty output = all commits merged

# Check log
git log origin/main..feature/branch
# Empty = no unique commits
```

## Configuration Impact

### Base Branches

Setting multiple bases:
```bash
git config trim.bases "develop,master,main"
```

git-trim checks if branch is merged into ANY base.

### Protected Branches

Exclude from trimming:
```bash
git config trim.exclude "staging production"
```

These branches are never analyzed for deletion.

## References

- Git ancestry: `git help merge-base`
- Cherry comparison: `git help cherry`
- Patch IDs: `git help patch-id`
