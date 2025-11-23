# Common Workflows

## Quick Reference

### Exploration (No Changes)

```bash
# Preview what would be deleted
git-trim --dry-run

# See detailed branch info
git branch -vv

# Check if branch is merged
git log origin/main..<branch> --oneline
```

### Safe Cleanup

```bash
# Interactive cleanup (confirms before deleting)
git-trim

# Delete merged only (skip stray)
git-trim  # Answer 'y' for merged, 'n' for stray
```

### Automation

```bash
# Post-merge hook (automatic)
# See: references/automation.md

# Sync alias (manual)
git config alias.sync '!git fetch --prune && git pull && git trim'
git sync
```

---

## Workflow Patterns

### Pattern 1: After PR Merge

**Scenario**: Just merged a PR on GitHub, want to clean local branch.

**Steps**:
1. Switch to main: `git checkout main`
2. Update from remote: `git pull`
3. Run cleanup: `git-trim`
4. Confirm deletion: `y`

**Shortcut**:
```bash
git checkout main && git pull && git-trim
```

**Expected Result**: Feature branch deleted locally.

---

### Pattern 2: Periodic Maintenance

**Scenario**: Weekly cleanup of accumulated stale branches.

**Steps**:
1. Fetch updates: `git fetch --prune`
2. Preview cleanup: `git-trim --dry-run`
3. Review output
4. Execute: `git-trim`
5. Confirm: `y`

**Frequency**: Weekly or bi-weekly

---

### Pattern 3: Before Major Refactoring

**Scenario**: Starting large refactor, want clean workspace.

**Steps**:
1. Commit all work: `git commit -am "WIP"`
2. Push branches: `git push --all`
3. Run cleanup: `git-trim --dry-run`
4. Review and execute: `git-trim`
5. Verify: `git branch`

**Goal**: Remove distractions, keep only active branches.

---

### Pattern 4: Repository Handoff

**Scenario**: Handing repository to another developer.

**Steps**:
1. Ensure all work is pushed: `git push --all`
2. Clean local branches: `git-trim`
3. Document remaining branches: `git branch > branches.txt`
4. Add to README: List of active branches

**Documentation**:
```markdown
## Active Branches
- `main` - Production
- `develop` - Next release
- `feature/new-api` - In progress (see #123)
```

---

### Pattern 5: Post-Release Cleanup

**Scenario**: Release merged, clean up release branches.

**Steps**:
1. Confirm release merged: `git log --oneline`
2. Run cleanup: `git-trim`
3. Verify release branch deleted
4. Tag release: `git tag v1.0.0`
5. Push tags: `git push --tags`

**Git-Flow Specific**:
```bash
# After release/1.0.0 merged to master
git checkout master
git pull
git-trim
# Confirm release/1.0.0 deletion
```

---

### Pattern 6: Investigating Stray Branches

**Scenario**: git-trim shows stray branches, need to decide safety.

**Decision Tree**:

```
Is upstream deleted?
  YES → Continue
  NO → Not stray, skip

Check commits: git log origin/main..<branch>
  Empty → SAFE (was merged, upstream deleted)
  Has commits → Continue

Check if commits exist elsewhere:
  git log --all --grep="<commit message>"
    Found → SAFE (squash merged)
    Not found → REVIEW

Manual review:
  git show <commit>
    Important? → KEEP + exclude
    Not needed? → DELETE
```

**Example**:
```bash
# Branch: feature/old-approach
git log origin/main..feature/old-approach
# Shows 2 commits

git show <commit-sha>
# Review changes

# Decision: Rejected approach, safe to delete
git branch -D feature/old-approach
```

---

### Pattern 7: Multi-Repo Bulk Cleanup

**Scenario**: Clean 20+ repositories at once.

**Steps**:
1. Create script: See `trim-all-repos.sh` in example_workflows.md
2. Dry-run first:
   ```bash
   find ~/projects -name .git -execdir git trim --dry-run \;
   ```
3. Review output
4. Execute:
   ```bash
   ./trim-all-repos.sh ~/projects
   ```

**Safety**: Always dry-run first across all repos.

---

### Pattern 8: CI/CD Integration

**Scenario**: Automate branch health checks in CI.

**Use Cases**:
- Warn on PRs with stale branches
- Weekly cleanup reports
- Block merges with orphaned branches

**Implementation**: See example_workflows.md Example 6.

---

## Workflow Decision Matrix

| Situation | Command | Confirmation Required | Risk Level |
|-----------|---------|----------------------|------------|
| First use | `git-trim --dry-run` | No (preview only) | None |
| Regular cleanup | `git-trim` | Yes (interactive) | Low |
| Merged branches only | `git-trim` → y (merged), n (stray) | Yes | Very Low |
| Include stray | `git-trim` → y (all) | Yes | Medium |
| Force delete | `git branch -D` | No | High |
| Exclude branch | `git config trim.exclude` | No | None |

---

## Integration with Git Workflows

### GitHub Flow

**Workflow**: `main` + feature branches

**Config**:
```bash
git config trim.bases "main"
```

**Usage**: Run git-trim after merging PRs.

### Git-Flow

**Workflow**: `master` + `develop` + feature/release/hotfix branches

**Config**:
```bash
git config trim.bases "develop,master"
git config trim.exclude "staging production"
```

**Usage**: Run git-trim after merging to develop or master.

### Trunk-Based

**Workflow**: `trunk` + short-lived branches

**Config**:
```bash
git config trim.bases "trunk"
```

**Usage**: Run git-trim daily or after each merge.

---

## Troubleshooting Workflows

### "Nothing to delete" but branches look stale

**Diagnosis**:
1. Check if branches track remote:
   ```bash
   git branch -vv
   ```
2. If no upstream (`[origin/...]`):
   - Branch is orphaned
   - Not tracked by git-trim
3. Manual cleanup:
   ```bash
   git branch -d <branch>
   ```

### "Stray" branch but it's merged

**Diagnosis**:
1. Check if actually merged:
   ```bash
   git log origin/main..<branch>
   ```
2. If empty, was squash merged:
   - git-trim couldn't detect (heuristics failed)
   - Safe to delete manually:
     ```bash
     git branch -D <branch>
     ```

### "Merged" branch but shouldn't be deleted

**Diagnosis**:
1. Check if branch should be excluded:
   ```bash
   git config trim.exclude "<branch>"
   ```
2. Or keep it:
   ```bash
   # Don't confirm deletion in git-trim prompt
   ```

---

## Best Practices

1. **Always dry-run first** when learning
2. **Fetch before cleanup** (default behavior)
3. **Review stray branches** before confirming
4. **Use automation** for regular repos
5. **Configure exclusions** for long-lived branches
6. **Document decisions** in commit messages or README

---

## Safety Tips

- git-trim never uses `--force` unnecessarily
- Current branch is always excluded
- Interactive confirmation for stray branches
- Use `git reflog` to recover if needed
- Test in a clone first if unsure

---

## Performance Tips

For large repositories (100+ branches):

- git-trim runs in parallel (automatic)
- Use `--no-update` to skip fetch
- Clean regularly to avoid buildup
- Consider automation (hooks/aliases)
