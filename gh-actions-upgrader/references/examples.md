# GitHub Actions Upgrade Examples

This document provides complete examples of using the GitHub Actions upgrader skill in various scenarios.

## Example 1: Simple Version Upgrades

### Scenario

Repository has several actions using outdated versions, all are standard GitHub actions with minor/patch updates available.

### Initial Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      - run: npm ci
      - run: npm test
```

### Command

```bash
User: /gh-actions-upgrade
```

### Skill Output

```text
Scanning workflows...
✓ Found 1 workflow file

Detecting actions...
✓ Found 3 action references

Analyzing actions...
✓ actions/checkout@v3 → v4 available (major upgrade)
✓ actions/setup-node@v3 → v4 available (major upgrade)
✓ actions/cache@v3 is up to date

Checking fork status...
✓ All actions are from official sources

Generated upgrade plan:
- 2 major version upgrades available
- 0 fork migrations needed
- 1 action already current
```

### Interactive Decisions

**Question 1**: "How should we handle major version upgrades?"

**User selection**: "Apply all"

### Updated Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      - run: npm ci
      - run: npm test
```

### Generated PR

**Title**: `chore(ci): upgrade GitHub Actions to latest versions`

**Description**:
```markdown
## Summary

Upgraded 2 actions to their latest major versions.

## Upgrades Applied

- **actions/checkout**: v3 → v4
  - Breaking: Node.js 16 → 20
  - [Changelog](https://github.com/actions/checkout/releases/tag/v4.0.0)

- **actions/setup-node**: v3 → v4
  - Breaking: Node.js 16 → 20
  - [Changelog](https://github.com/actions/setup-node/releases/tag/v4.0.0)

## Testing Recommendations

- [ ] Verify CI workflows run successfully
```

---

## Example 2: Fork Migration to Upstream

### Scenario

Repository uses a forked version of `actions/checkout` that is significantly behind upstream and has no custom commits.

### Initial Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: custom-org/checkout@v2
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: python deploy.py
```

### Command

```bash
User: Upgrade all GitHub Actions
```

### Fork Detection

```bash
# Skill internally runs:
gh api repos/custom-org/checkout --jq '{
  fork: .fork,
  parent: .parent.full_name
}'

# Response:
{
  "fork": true,
  "parent": "actions/checkout"
}

# Check divergence:
gh api repos/custom-org/checkout/compare/actions:v4...v2 --jq '{
  ahead: .ahead_by,
  behind: .behind_by
}'

# Response:
{
  "ahead": 0,
  "behind": 150
}
```

### Skill Output

```text
Scanning workflows...
✓ Found 1 workflow file

Detecting actions...
✓ Found 2 action references

Analyzing actions...
✓ custom-org/checkout@v2 is a fork of actions/checkout
  - Fork is 150 commits behind upstream
  - Fork has 0 custom commits
  - Upstream version: v4
  → Recommendation: Migrate to actions/checkout@v4

✓ actions/setup-python@v4 is up to date

Generated upgrade plan:
- 0 version upgrades needed
- 1 fork migration recommended
- 1 action already current
```

### Interactive Decisions

**Question 1**: "Should we migrate forked actions to their upstream equivalents?"

**Context**:
```text
custom-org/checkout is a fork of actions/checkout
- Fork version: v2
- Upstream version: v4
- Fork is 150 commits behind
- No custom commits detected
```

**User selection**: "Migrate all forks to upstream"

### Updated Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: python deploy.py
```

### Generated PR

**Title**: `chore(ci): migrate forked actions to upstream`

**Description**:
```markdown
## Summary

Migrated forked GitHub Actions to their upstream equivalents for better maintenance and support.

## Fork Migrations

### custom-org/checkout@v2 → actions/checkout@v4

**Reason**: Fork is 150 commits behind upstream with no custom changes

**Analysis**:
- Fork last updated: 2023-01-15
- Upstream version: v4.1.1 (2024-11-01)
- Commits behind: 150
- Custom commits: 0
- Risk: Low

**Benefits**:
- Latest features and security updates
- Official GitHub support and maintenance
- Automatic compatibility updates
- Community-tested reliability

**Breaking Changes** (v2 → v4):
- Node.js 16 → 20 requirement
- Default fetch-depth changed
- New sparse-checkout support

## Testing Recommendations

- [ ] Verify checkout behavior is as expected
- [ ] Confirm deployment script still works
```

---

## Example 3: Major Version Breaking Changes

### Scenario

Actions have major version upgrades with significant breaking changes that require configuration updates.

### Initial Workflow

```yaml
# .github/workflows/test.yml
name: Test

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [16, 18, 20]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

### Skill Output

```text
Analyzing breaking changes...

actions/checkout v3 → v4:
- Runner now requires Node.js 20 (was 16)
- Default fetch-depth changed from 1 to 0
- Removed: set-safe-directory parameter
- Added: sparse-checkout support

actions/setup-node v3 → v4:
- Runner now requires Node.js 20 (was 16)
- Improved cache implementation
- Better error messages
```

### Interactive Decisions

**Question 1**: "How should we handle major version upgrades?"

**User selection**: "Apply all"

**Question 2**: "When action parameters change, should we:"

**User selection**: "Keep existing behavior"

### Updated Workflow

```yaml
# .github/workflows/test.yml
name: Test

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [16, 18, 20]
    steps:
      - uses: actions/checkout@v4
        with:
          # Explicitly set to preserve v3 behavior
          fetch-depth: 1
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

### Generated PR

**Title**: `chore(ci): upgrade GitHub Actions with breaking changes`

**Description**:
```markdown
## Summary

Upgraded actions to latest versions and adjusted configurations to preserve existing behavior.

## Upgrades Applied

### actions/checkout: v3 → v4

**Breaking Changes**:
- Runner requires Node.js 20 (was 16)
- Default `fetch-depth` changed from 1 to 0 (full history)

**Configuration Changes**:
- Added explicit `fetch-depth: 1` to preserve v3 behavior
- This maintains shallow clone for faster checkouts

**Why preserve v3 behavior**: Our CI doesn't need full git history for tests.

### actions/setup-node: v3 → v4

**Breaking Changes**:
- Runner requires Node.js 20 (was 16)

**Configuration Changes**:
- None needed - cache behavior is compatible

## Testing Recommendations

- [ ] Verify tests run successfully on all Node.js versions (16, 18, 20)
- [ ] Confirm checkout is still fast (shallow clone working)
- [ ] Check npm cache is still effective
```

---

## Example 4: Mixed Upgrades

### Scenario

Repository has a mix of upgrade scenarios: version upgrades, fork migrations, and actions that should be kept as-is.

### Initial Workflows

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: custom-org/custom-action@v1  # Fork with custom patches
      - uses: actions/setup-go@v4
      - run: go build ./...

# .github/workflows/security.yml
name: Security
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: github/codeql-action/init@v2
      - uses: github/codeql-action/analyze@v2
```

### Fork Analysis

```bash
# Checking custom-org/custom-action
gh api repos/custom-org/custom-action --jq '{
  fork: .fork,
  parent: .parent.full_name
}'

# Response:
{
  "fork": true,
  "parent": "upstream-org/custom-action"
}

# Check commits
gh api repos/custom-org/custom-action/compare/upstream-org:main...main \
  --jq '{ahead: .ahead_by, behind: .behind_by}'

# Response:
{
  "ahead": 5,
  "behind": 2
}
```

### Skill Output

```text
Found 2 workflow files with 5 action references

Analysis:
✓ actions/checkout@v3 (used 2×)
  → v4 available (major upgrade)

⚠ custom-org/custom-action@v1 is a fork of upstream-org/custom-action
  → Fork has 5 custom commits
  → Fork is 2 commits behind upstream
  → Recommendation: Review manually

✓ actions/setup-go@v4 is up to date

✓ github/codeql-action/init@v2 → v3 available (major upgrade)
✓ github/codeql-action/analyze@v2 → v3 available (major upgrade)

Upgrade plan:
- 3 major version upgrades
- 1 fork needs manual review
- 1 action already current
```

### Interactive Decisions

**Question 1**: "Found custom-org/custom-action with custom commits. Should we:"

**Options**:
- Keep fork (has custom patches)
- Review manually
- Attempt migration (risky)

**User selection**: "Keep fork"

**Question 2**: "How should we handle major version upgrades?"

**User selection**: "Apply all"

### Updated Workflows

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: custom-org/custom-action@v1  # Kept: has custom patches
      - uses: actions/setup-go@v4
      - run: go build ./...

# .github/workflows/security.yml
name: Security
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
      - uses: github/codeql-action/analyze@v3
```

### Generated PR

**Title**: `chore(ci): upgrade GitHub Actions (selective)`

**Description**:
```markdown
## Summary

Upgraded standard GitHub Actions while preserving custom fork with patches.

## Upgrades Applied

- **actions/checkout**: v3 → v4 (2 workflows)
- **github/codeql-action/init**: v2 → v3
- **github/codeql-action/analyze**: v2 → v3

## Forks Kept

### custom-org/custom-action@v1

**Reason**: Fork contains 5 custom commits with organizational patches

**Analysis**:
- Fork has custom functionality not in upstream
- Fork is 2 commits behind upstream (non-critical updates)
- Risk of migration: High (would lose custom features)

**Recommendation**: Keep fork, monitor upstream for relevant updates

## Testing Recommendations

- [ ] Verify CI builds successfully
- [ ] Confirm security scans complete
- [ ] Test custom-action behavior unchanged
```

---

## Example 5: No Upgrades Needed

### Scenario

All actions are already at their latest versions.

### Current Workflow

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm test
```

### Skill Output

```text
Scanning workflows...
✓ Found 1 workflow file

Detecting actions...
✓ Found 2 action references

Analyzing actions...
✓ actions/checkout@v4 is up to date
✓ actions/setup-node@v4 is up to date

✅ All actions are at their latest versions!

No upgrades needed.
```

---

## Example 6: Branch References

### Scenario

Workflow uses branch references instead of tags (discouraged).

### Initial Workflow

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main
      - uses: actions/setup-node@main
```

### Skill Output

```text
⚠ Warning: Found actions using branch references

actions/checkout@main
  → Latest stable: v4.1.1
  → Recommendation: Pin to tag for stability

actions/setup-node@main
  → Latest stable: v4.0.2
  → Recommendation: Pin to tag for stability

Branch references can cause:
- Unexpected breaking changes
- Workflow instability
- Difficult debugging
```

### Interactive Decision

**Question**: "Convert branch references to stable tags?"

**User selection**: "Yes, use latest stable versions"

### Updated Workflow

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
```

### Generated PR

**Title**: `chore(ci): pin actions to stable versions`

**Description**:
```markdown
## Summary

Converted branch references to stable version tags for predictable workflows.

## Changes

- **actions/checkout**: main → v4.1.1
- **actions/setup-node**: main → v4.0.2

## Why This Change

Branch references (`@main`) can cause unexpected behavior:
- Code changes without warning
- Breaking changes without notice
- Difficult to debug issues

Stable tags (`@v4`) provide:
- Predictable behavior
- Controlled upgrades
- Clear change tracking

## Testing Recommendations

- [ ] Verify workflows behave identically
```
