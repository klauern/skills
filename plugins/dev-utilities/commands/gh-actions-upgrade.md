---
description: Automatically detect, analyze, and upgrade GitHub Actions in workflows
---

# GitHub Actions Upgrade

Automatically detect, analyze, and upgrade GitHub Actions in your repository's workflows.

## What This Does

This command will:

1. **Scan** all workflow files in `.github/workflows/` to find action references
2. **Analyze** each action to determine:
   - Current version
   - Whether it's a fork (using `gh api` to check repository status)
   - Available upgrades
   - Potential breaking changes
3. **Generate upgrade plans** for each action with:
   - Version migration path
   - Breaking change summaries
   - Fork-to-upstream migration recommendations
   - Parameter updates needed
4. **Apply upgrades** to all workflow files
5. **Create a PR** with comprehensive upgrade documentation

## Usage

```bash
/gh-actions-upgrade
```

## Workflow

### Phase 1: Discovery

The skill will automatically:

- Find all YAML files in `.github/workflows/`
- Extract action references (e.g., `actions/checkout@v3`)
- Skip local actions (`./.github/actions/*`) and Docker images

### Phase 2: Fork Detection

For each action, the skill uses GitHub CLI to check:

```bash
# Check if action repository is a fork
gh api repos/{owner}/{repo} --jq '.fork'

# If it's a fork, get the parent
gh api repos/{owner}/{repo} --jq '.parent.full_name'
```

### Phase 3: Version Analysis

The skill will:

- Query GitHub API for latest releases
- Compare current version with available versions
- Identify major version changes
- Search for breaking changes in release notes

### Phase 4: Interactive Planning

You'll be asked to make key decisions:

#### 1. Fork Migration Strategy

**Question**: "Should we migrate forked actions to their upstream equivalents?"

**Context**: The skill detected actions that are forks of upstream repositories.

**Options**:
- **Migrate all forks to upstream** (recommended): Use upstream versions for better community support
- **Keep forks**: Retain forks if they contain custom patches or organizational requirements
- **Selective migration**: Review each fork individually to decide

#### 2. Major Version Upgrade Policy

**Question**: "How should we handle major version upgrades with potential breaking changes?"

**Context**: Some actions have major version upgrades available.

**Options**:
- **Apply all**: Upgrade everything (may require workflow adjustments)
- **Skip breaking upgrades**: Only apply minor/patch upgrades
- **Review individually**: Examine each major upgrade case-by-case

#### 3. Parameter Update Approach

**Question**: "When action parameters change, should we:"

**Context**: Some upgraded actions have changed parameters or defaults.

**Options**:
- **Use new defaults**: Adopt latest behavior (recommended for most cases)
- **Keep existing behavior**: Preserve current functionality explicitly
- **Add TODO comments**: Mark for manual review

### Phase 5: Execution

The skill will:

1. Create a new branch: `chore/upgrade-github-actions-{timestamp}`
2. Update all workflow files with approved changes
3. Validate YAML syntax after changes
4. Commit changes with conventional commit format
5. Push to remote
6. Create a PR with detailed upgrade information

## Requirements

- `.github/workflows/` directory with workflow files
- GitHub CLI (`gh`) installed and authenticated
- Write access to the repository
- Internet connection for API access

## Example Output

```text
Found 3 workflow files with 8 action references

Analyzing actions...
✓ actions/checkout@v3 → v4 available (major upgrade)
✓ actions/setup-node@v3 → v4 available (major upgrade)
⚠ custom-org/checkout@v2 is a fork of actions/checkout
  → Upstream at v4, recommend migrating
✓ actions/cache@v3 is up to date

Generated upgrade plan:
- 2 major version upgrades
- 1 fork migration opportunity
- 1 action already current

[Interactive decisions...]

Applying upgrades...
✓ Updated .github/workflows/ci.yml
✓ Updated .github/workflows/release.yml
✓ Updated .github/workflows/test.yml

Committing changes...
✓ Created commit: chore(ci): upgrade GitHub Actions to latest versions

Pushing to remote...
✓ Pushed to origin/chore/upgrade-github-actions-20250119

Creating pull request...
✓ Created PR #123: https://github.com/user/repo/pull/123
```

## PR Structure

The generated PR will include:

### Title
```
chore(ci): upgrade GitHub Actions to latest versions
```

### Description

```markdown
## Summary

This PR upgrades GitHub Actions in our workflows to their latest versions and migrates forked actions to upstream equivalents.

## Upgrades Applied

### Version Upgrades

- **actions/checkout**: v3 → v4
  - Breaking: Node.js 16 → 20
  - New: sparse-checkout feature available
  - [Changelog](https://github.com/actions/checkout/releases/tag/v4.0.0)

- **actions/setup-node**: v3 → v4
  - Breaking: Node.js 16 → 20
  - Improved caching mechanism
  - [Changelog](https://github.com/actions/setup-node/releases/tag/v4.0.0)

### Fork Migrations

- **custom-org/checkout@v2** → **actions/checkout@v4**
  - Reason: Fork is 2 major versions behind upstream
  - Risk: Low - fork has no custom commits vs. upstream
  - Benefit: Better community support and maintenance

## Breaking Changes

### actions/checkout v3 → v4

- Runner requires Node.js 20 (previously Node.js 16)
- Default `fetch-depth` changed from `1` to `0` (full history)
- Removed deprecated `set-safe-directory` parameter

**Action required**: Verify workflows still function correctly with these changes.

### actions/setup-node v3 → v4

- Runner requires Node.js 20 (previously Node.js 16)
- Cache behavior improvements (no breaking changes expected)

## Testing Recommendations

- [ ] Run CI workflows on this branch to verify all actions work
- [ ] Check that checkout behavior is as expected
- [ ] Verify Node.js setup still caches dependencies correctly
- [ ] Review any custom scripts that depend on action outputs

## Related Documentation

- [GitHub Actions Release Notes](https://github.blog/changelog/label/actions/)
- [actions/checkout v4 Release](https://github.com/actions/checkout/releases/tag/v4.0.0)
- [actions/setup-node v4 Release](https://github.com/actions/setup-node/releases/tag/v4.0.0)
```

## Configuration

### Custom Fork Mappings

Override automatic fork detection:

```yaml
# .github/actions-upgrade-config.yml
fork_mappings:
  custom-org/special-action: upstream-org/special-action
```

### Excluded Actions

Skip specific actions:

```yaml
# .github/actions-upgrade-config.yml
excluded_actions:
  - local/custom-action
  - pinned/action  # Keep at current version
```

## Troubleshooting

### No workflow files found

**Issue**: Skill reports no workflows found.

**Solution**: Ensure `.github/workflows/` exists with `.yml` or `.yaml` files.

### API rate limiting

**Issue**: GitHub API rate limit exceeded.

**Solution**:
- Authenticate with `gh auth login`
- Wait for rate limit reset
- Use personal access token with higher limits

### Fork detection fails

**Issue**: Cannot determine if action is a fork.

**Solution**:
- Check internet connection
- Verify action repository is public
- Manually configure fork mapping in `.github/actions-upgrade-config.yml`

### YAML syntax errors after upgrade

**Issue**: Workflow files have syntax errors after modification.

**Solution**:
- Review changes in the PR
- Use `yamllint .github/workflows/*.yml` to identify issues
- May need to manually adjust complex workflow structures

## Best Practices

1. **Review the PR carefully** before merging
2. **Test workflows** on the upgrade branch
3. **Read changelogs** for major version upgrades
4. **Document decisions** about keeping forks vs. migrating
5. **Run workflows** in a test environment first if possible

## See Also

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [/commit-push](./commit-push.md) - Used internally for commits
- [/pr](./pr.md) - Used internally for PR creation
