---
name: gh-actions-upgrader
description: Automatically detect, analyze, and upgrade GitHub Actions in workflows. Identifies forked actions and recommends upstream equivalents, handles major version upgrades with breaking change detection.
version: 1.0.0
author: klauern
---

# GitHub Actions Upgrader

## Overview

This skill automates the process of upgrading GitHub Actions in your repository's workflows. It:

1. **Detects** all GitHub Actions workflow files in `.github/workflows/`
2. **Analyzes** each action reference to identify current versions and fork status
3. **Discovers** available upgrades and identifies forked actions that should migrate to upstream
4. **Plans** upgrade strategies, detecting breaking changes and parameter updates
5. **Executes** upgrades across all workflow files
6. **Creates** a comprehensive PR with upgrade details and migration notes

## When to Use This Skill

Use this skill when you need to:

- Upgrade GitHub Actions to their latest versions
- Detect and migrate from forked actions to upstream equivalents
- Identify and handle breaking changes in major version upgrades
- Maintain up-to-date CI/CD workflows
- Audit action versions across your repository

## Quick Start

```bash
User: Upgrade all GitHub Actions in this repository
# or
User: /gh-actions-upgrade
```

The skill will:

1. Find all workflow files
2. Extract action references
3. Check for available upgrades
4. Generate upgrade plans
5. Apply updates
6. Commit, push, and create a PR

## How It Works

### Phase 1: Detection

Scans `.github/workflows/` for YAML workflow files and extracts action references.

**Detected patterns**:
- Standard actions: `actions/checkout@v3`
- Third-party actions: `azure/login@v1`
- Potentially forked actions: `custom-org/checkout@v3`
- Local actions: `./.github/actions/my-action`
- Docker actions: `docker://alpine:3.8`

**Tools used**:
```bash
find .github/workflows -name "*.yml" -o -name "*.yaml"
```

**See**: [references/detection_patterns.md](references/detection_patterns.md) for detailed parsing rules

### Phase 2: Analysis

Parses each workflow file to extract:

- Action name and owner
- Current version (commit SHA, tag, or branch)
- Action parameters and configuration
- Job dependencies and matrix configurations
- **Fork detection**: Checks if action repository is a fork using GitHub CLI

**YAML parsing**:
- Uses yq or similar tools to parse workflow YAML
- Extracts `uses:` directives
- Identifies action parameters under `with:` blocks

**Fork detection using gh CLI**:
```bash
# Check if repository is a fork
gh api repos/{owner}/{repo} --jq '.fork'

# Get parent repository if it's a fork
gh api repos/{owner}/{repo} --jq '.parent.full_name'

# Compare fork with upstream
gh api repos/{owner}/{repo} --jq '.parent.full_name, .updated_at'
gh api repos/{parent_owner}/{parent_repo} --jq '.updated_at'
```

**See**: [references/analysis_guide.md](references/analysis_guide.md) for technical details

### Phase 3: Upgrade Discovery

Checks for newer versions using multiple strategies:

**For standard actions** (actions/*, github/*):
- Query GitHub API for latest releases
- Compare semantic versions
- Identify major version changes

**For third-party actions**:
- Check action repository for latest tags
- Use web search for changelog information
- Detect breaking changes from release notes

**For forked actions**:
- Use `gh api` to check if repository is a fork
- Identify upstream parent repository
- Compare versions between fork and upstream
- Check if fork is behind upstream
- Generate migration recommendation if upstream is preferred

**API calls**:
```bash
# Check latest release
gh api repos/actions/checkout/releases/latest

# Check fork status and parent
gh api repos/{owner}/{repo} --jq '{fork: .fork, parent: .parent.full_name, updated: .updated_at}'

# Compare commits between fork and upstream
gh api repos/{owner}/{repo}/compare/{base}...{head}
```

**See**: [references/upgrade_detection.md](references/upgrade_detection.md) for discovery algorithms

### Phase 4: Planning

Generates detailed upgrade plans for each action:

**Plan includes**:
- Current version → Target version
- Breaking changes summary
- Parameter changes required
- Fork migration recommendation (if applicable)
- Risk assessment (low/medium/high)

**Example plan**:
```yaml
Action: actions/checkout
Current: v3
Target: v4
Type: Major version upgrade
Breaking Changes:
  - Node.js 16 → Node.js 20
  - Removed deprecated 'set-safe-directory' parameter
  - New 'sparse-checkout' feature available
Parameter Changes:
  - 'fetch-depth' default changed from 1 to 0
Migration Steps:
  - Update from actions/checkout@v3 to actions/checkout@v4
  - Review sparse-checkout usage
Risk: Low (well-documented upgrade)
```

**See**: [references/planning_strategy.md](references/planning_strategy.md) for plan generation logic

### Phase 5: Execution

Applies upgrades to workflow files:

**Update strategy**:
1. Create a new branch for upgrades
2. For each workflow file:
   - Parse YAML structure
   - Update action references
   - Update parameters if needed
   - Preserve comments and formatting
3. Validate YAML syntax
4. Run workflow linting if available

**Safety checks**:
- Preserve existing configurations
- Don't remove comments
- Validate YAML after changes
- Create backup before modifying

**See**: [references/execution_guide.md](references/execution_guide.md) for implementation details

### Phase 6: Git Operations

Creates a comprehensive PR with upgrade documentation:

**Branch naming**: `chore/upgrade-github-actions-{date}`

**Commit message format**:
```
chore(ci): upgrade GitHub Actions to latest versions

- actions/checkout: v3 → v4
- actions/setup-node: v3 → v4
- Migrate custom-org/checkout → actions/checkout (upstream)
```

**PR description includes**:
- Summary of all upgrades
- Breaking changes for each action
- Fork migration notes with upstream justification
- Testing recommendations
- Links to changelogs

**See**: [references/pr_template.md](references/pr_template.md) for PR generation

## Model Strategy

This skill uses different Claude models for optimal performance:

### Claude 4.5 Haiku

**Use for**:
- File discovery and parsing
- YAML structure extraction
- Simple version comparisons
- Pattern matching for action references

### Claude 4.5 Sonnet

**Use for**:
- Breaking change analysis
- Risk assessment
- PR description generation
- Complex upgrade decision-making
- Fork vs. upstream analysis and migration recommendations

## User Decision Points

The skill will request user input for critical decisions:

### 1. Fork Migration Strategy

**Question**: "Should we migrate forked actions to their upstream equivalents?"

**Options**:
- Migrate all forks to upstream (recommended for most cases)
- Keep forks (if there are custom patches or organizational requirements)
- Selective migration (review each fork individually)

### 2. Major Version Upgrade Policy

**Question**: "How should we handle major version upgrades with potential breaking changes?"

**Options**:
- Apply all (aggressive upgrade strategy)
- Skip breaking upgrades (conservative approach)
- Review each individually (manual control)

### 3. Parameter Update Approach

**Question**: "When action parameters change, should we:"

**Options**:
- Use new defaults (leverage latest features)
- Keep existing behavior (preserve current functionality)
- Add TODO comments for manual review

## Examples

### Example 1: Simple Version Upgrades

Repository with standard actions using outdated versions.

**See**: [references/examples.md](references/examples.md#example-1-simple-version-upgrades)

### Example 2: Fork Migration to Upstream

Workflows using forked actions that should migrate to upstream.

**See**: [references/examples.md](references/examples.md#example-2-fork-migration-to-upstream)

### Example 3: Major Version with Breaking Changes

Upgrading actions/checkout from v3 to v4 with parameter changes.

**See**: [references/examples.md](references/examples.md#example-3-major-version-breaking-changes)

### Example 4: Mixed Upgrades

Repository with various upgrade scenarios requiring different strategies.

**See**: [references/examples.md](references/examples.md#example-4-mixed-upgrades)

## Requirements

- Git repository with `.github/workflows/` directory
- GitHub CLI (`gh`) installed and authenticated
- Write access to repository
- Internet connection for version checking

**Installation**:
```bash
# Install gh CLI
brew install gh  # macOS

# Authenticate
gh auth login
```

## Configuration

### Custom Fork Mappings

If your organization uses custom forks, configure mappings:

```yaml
# .github/actions-upgrade-config.yml
# Optional: Force specific fork mappings (auto-detected by default)
fork_mappings:
  custom-org/checkout: actions/checkout
  custom-org/setup-node: actions/setup-node
```

### Excluded Actions

Skip specific actions from upgrades:

```yaml
# .github/actions-upgrade-config.yml
excluded_actions:
  - local/action  # Don't upgrade local actions
  - pinned/action@sha  # Keep pinned to specific SHA
```

## Error Handling

The skill gracefully handles:

- Missing workflow files (exits gracefully)
- Invalid YAML syntax (reports and skips)
- API rate limits (waits and retries)
- Network failures (provides manual fallback)
- Inaccessible action repositories (reports as warning)

**See**: [references/execution_guide.md](references/execution_guide.md#error-handling) for details

## Best Practices

1. **Review before merging**: Always review the PR before merging upgrades
2. **Test workflows**: Run upgraded workflows in a test branch first
3. **Read changelogs**: Review breaking changes for major upgrades
4. **Pin to tags, not branches**: Use `@v4` instead of `@main`
5. **Document custom changes**: If keeping forks, document why

## Limitations

- Requires GitHub CLI (doesn't support GitLab CI/CD)
- Cannot detect all breaking changes automatically
- May miss parameter deprecations not in changelogs
- Doesn't test workflows after upgrade (manual verification needed)
- Fork migration assumes upstream compatibility (may not account for custom patches)

## Reference Documentation

- **[Detection Patterns](references/detection_patterns.md)**: Action reference patterns and parsing rules
- **[Analysis Guide](references/analysis_guide.md)**: YAML parsing and extraction techniques
- **[Upgrade Detection](references/upgrade_detection.md)**: Version checking and discovery algorithms
- **[Planning Strategy](references/planning_strategy.md)**: Upgrade plan generation logic
- **[Execution Guide](references/execution_guide.md)**: File modification and validation
- **[PR Template](references/pr_template.md)**: Pull request structure and content
- **[Examples](references/examples.md)**: Complete workflow examples

## Troubleshooting

### No workflows found

- Check `.github/workflows/` exists
- Verify YAML files have `.yml` or `.yaml` extension

### API rate limits

- Authenticate with `gh auth login`
- Wait for rate limit reset
- Use personal access token with higher limits

### YAML parsing errors

- Validate workflow syntax: `yamllint .github/workflows/*.yml`
- Check for valid YAML structure

### Cannot determine latest version

- Verify internet connection
- Check action repository is public
- Try manual version lookup

## Version History

- **1.0.0** (2025-01-19): Initial release
  - Workflow detection and parsing
  - Action version analysis
  - Upgrade discovery with breaking change detection
  - zendesk/ fork migration support
  - Automated PR creation
  - Interactive decision points
