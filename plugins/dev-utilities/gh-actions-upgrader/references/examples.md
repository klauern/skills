# Examples

## Simple Version Upgrade

**Before**:
```yaml
- uses: actions/checkout@v3
- uses: actions/setup-node@v3
```

**After**:
```yaml
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
```

**PR Title**: `chore(ci): upgrade GitHub Actions to latest versions`

## Fork Migration

**Detection**:
```bash
gh api repos/custom-org/checkout --jq '{fork: .fork, parent: .parent.full_name}'
# {"fork": true, "parent": "actions/checkout"}
```

**Before**: `uses: custom-org/checkout@v2`
**After**: `uses: actions/checkout@v4`

**PR Title**: `chore(ci): migrate forked actions to upstream`

## Mixed Upgrades (Fork with Custom Commits)

When fork has custom commits (ahead > 0), keep it:
```yaml
- uses: actions/checkout@v4           # Upgraded
- uses: custom-org/custom-action@v1   # Kept (has custom patches)
- uses: github/codeql-action/init@v3  # Upgraded
```

**PR Title**: `chore(ci): upgrade GitHub Actions (selective)`
