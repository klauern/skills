# Action Analysis Guide

This document describes how to analyze detected actions to determine fork status, current versions, and upgrade opportunities.

## Analysis Phases

### Phase 1: Repository Information

For each action, gather repository metadata.

### Phase 2: Fork Detection

Determine if the action is a fork and identify upstream.

### Phase 3: Version Analysis

Parse current version and compare with available versions.

### Phase 4: Parameter Analysis

Extract action parameters and configuration.

## Using GitHub CLI for Analysis

### Check Repository Metadata

```bash
gh api repos/{owner}/{repo}
```

**Key fields**:
```json
{
  "full_name": "owner/repo",
  "fork": true,
  "parent": {
    "full_name": "upstream-owner/upstream-repo",
    "default_branch": "main"
  },
  "default_branch": "main",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "pushed_at": "2024-12-01T00:00:00Z",
  "archived": false,
  "visibility": "public"
}
```

### Extract Fork Information

```bash
# Check if repository is a fork
gh api repos/{owner}/{repo} --jq '.fork'

# Get parent repository
gh api repos/{owner}/{repo} --jq '.parent.full_name'

# Get fork and parent in one call
gh api repos/{owner}/{repo} --jq '{
  is_fork: .fork,
  parent: .parent.full_name,
  fork_updated: .updated_at,
  fork_pushed: .pushed_at
}'
```

### Compare Fork with Upstream

```bash
# Get both fork and parent info
FORK_REPO="custom-org/checkout"
PARENT=$(gh api repos/$FORK_REPO --jq '.parent.full_name')

# Compare last updates
echo "Fork: $FORK_REPO"
gh api repos/$FORK_REPO --jq '{updated: .updated_at, pushed: .pushed_at}'

echo "Parent: $PARENT"
gh api repos/$PARENT --jq '{updated: .updated_at, pushed: .pushed_at}'
```

### Check Divergence

```bash
# Compare commits between fork and upstream
gh api repos/$FORK_REPO/compare/$PARENT_DEFAULT_BRANCH...$FORK_DEFAULT_BRANCH \
  --jq '{ahead: .ahead_by, behind: .behind_by, status: .status}'
```

**Possible statuses**:
- `identical`: Fork is up to date
- `ahead`: Fork has commits not in upstream
- `behind`: Upstream has commits not in fork
- `diverged`: Both have unique commits

## Fork Detection Algorithm

```python
def analyze_fork_status(owner, repo):
    # Get repository metadata
    repo_info = gh_api(f'repos/{owner}/{repo}')

    if not repo_info['fork']:
        return {
            'is_fork': False,
            'recommendation': 'check_for_upgrades'
        }

    parent = repo_info['parent']['full_name']

    # Compare fork with parent
    comparison = gh_api(f'repos/{owner}/{repo}/compare/{parent}:main...main')

    ahead = comparison['ahead_by']
    behind = comparison['behind_by']

    # Determine recommendation
    if ahead == 0 and behind == 0:
        return {
            'is_fork': True,
            'parent': parent,
            'status': 'identical',
            'recommendation': 'migrate_to_upstream',
            'reason': 'Fork is identical to upstream, no custom changes'
        }
    elif ahead == 0 and behind > 0:
        return {
            'is_fork': True,
            'parent': parent,
            'status': 'behind',
            'behind_by': behind,
            'recommendation': 'migrate_to_upstream',
            'reason': f'Fork is {behind} commits behind upstream, no custom changes'
        }
    elif ahead > 0 and behind == 0:
        return {
            'is_fork': True,
            'parent': parent,
            'status': 'ahead',
            'ahead_by': ahead,
            'recommendation': 'keep_fork',
            'reason': f'Fork has {ahead} custom commits, may need them'
        }
    else:
        return {
            'is_fork': True,
            'parent': parent,
            'status': 'diverged',
            'ahead_by': ahead,
            'behind_by': behind,
            'recommendation': 'review_manually',
            'reason': f'Fork has {ahead} custom commits and is {behind} behind upstream'
        }
```

## Version Analysis

### Extract Current Version

From the action reference `owner/repo@ref`:

```python
def parse_version_ref(ref):
    if ref.startswith('v'):
        # Likely a semantic version tag
        return {
            'type': 'tag',
            'value': ref,
            'is_semver': is_semver(ref)
        }
    elif len(ref) in [7, 40] and is_hex(ref):
        # Likely a commit SHA
        return {
            'type': 'sha',
            'value': ref,
            'is_full_sha': len(ref) == 40
        }
    else:
        # Likely a branch
        return {
            'type': 'branch',
            'value': ref
        }
```

### Get Available Versions

```bash
# Get latest release
gh api repos/{owner}/{repo}/releases/latest --jq '{
  tag: .tag_name,
  name: .name,
  published: .published_at,
  prerelease: .prerelease
}'

# Get all releases
gh api repos/{owner}/{repo}/releases --jq '.[] | {
  tag: .tag_name,
  published: .published_at,
  prerelease: .prerelease
}'

# Get all tags (if no releases)
gh api repos/{owner}/{repo}/tags --jq '.[] | {
  name: .name,
  commit: .commit.sha
}'
```

### Compare Versions

```python
from packaging import version

def compare_versions(current, available):
    if current.startswith('v'):
        current = current[1:]
    if available.startswith('v'):
        available = available[1:]

    current_ver = version.parse(current)
    available_ver = version.parse(available)

    if available_ver > current_ver:
        # Determine upgrade type
        if current_ver.major < available_ver.major:
            return {
                'upgrade_available': True,
                'upgrade_type': 'major',
                'breaking_changes_likely': True
            }
        elif current_ver.minor < available_ver.minor:
            return {
                'upgrade_available': True,
                'upgrade_type': 'minor',
                'breaking_changes_likely': False
            }
        else:
            return {
                'upgrade_available': True,
                'upgrade_type': 'patch',
                'breaking_changes_likely': False
            }

    return {'upgrade_available': False}
```

## Parameter Analysis

Extract and analyze action parameters:

```yaml
# Example workflow step
- uses: actions/checkout@v3
  with:
    fetch-depth: 0
    submodules: recursive
    token: ${{ secrets.GITHUB_TOKEN }}
```

### Extract Parameters

```python
def extract_parameters(step):
    return {
        'parameters': step.get('with', {}),
        'environment': step.get('env', {}),
        'condition': step.get('if'),
        'continue_on_error': step.get('continue-on-error', False)
    }
```

### Check Parameter Compatibility

When upgrading, check if parameters are still valid:

```bash
# Get action definition
gh api repos/{owner}/{repo}/contents/action.yml \
  --jq '.content' | base64 -d | yq eval '.inputs'
```

## Analysis Output Format

```json
{
  "action": "actions/checkout@v3",
  "repository": {
    "owner": "actions",
    "repo": "checkout",
    "full_name": "actions/checkout",
    "is_fork": false,
    "archived": false,
    "visibility": "public"
  },
  "current_version": {
    "ref": "v3",
    "type": "tag",
    "is_semver": true,
    "major": 3,
    "minor": 0,
    "patch": 0
  },
  "latest_version": {
    "ref": "v4",
    "type": "tag",
    "is_semver": true,
    "major": 4,
    "minor": 1,
    "patch": 1,
    "published_at": "2024-01-15T00:00:00Z"
  },
  "upgrade_available": true,
  "upgrade_type": "major",
  "parameters": {
    "fetch-depth": "0",
    "submodules": "recursive"
  },
  "usage_count": 3,
  "workflows": [
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    ".github/workflows/test.yml"
  ]
}
```

## Fork Analysis Output Format

```json
{
  "action": "custom-org/checkout@v2",
  "repository": {
    "owner": "custom-org",
    "repo": "checkout",
    "full_name": "custom-org/checkout",
    "is_fork": true,
    "parent": "actions/checkout"
  },
  "fork_analysis": {
    "status": "behind",
    "ahead_by": 0,
    "behind_by": 150,
    "last_sync": "2023-01-01T00:00:00Z",
    "custom_commits": []
  },
  "current_version": {
    "ref": "v2",
    "type": "tag"
  },
  "upstream_version": {
    "ref": "v4",
    "type": "tag"
  },
  "recommendation": {
    "action": "migrate_to_upstream",
    "reason": "Fork is 150 commits behind upstream with no custom changes",
    "migration_target": "actions/checkout@v4",
    "risk": "low",
    "benefits": [
      "Latest features and security updates",
      "Better community support",
      "Automated updates from GitHub"
    ]
  }
}
```

## Error Handling

### Repository Not Found

```bash
gh api repos/{owner}/{repo} 2>&1
# Error: HTTP 404: Not Found
```

**Handling**: Report as warning, skip upgrade for this action.

### Rate Limiting

```bash
gh api rate_limit --jq '{
  limit: .rate.limit,
  remaining: .rate.remaining,
  reset: .rate.reset
}'
```

**Handling**: Wait until rate limit resets or ask user to authenticate.

### Private Repositories

If action repository is private and not accessible:

**Handling**: Skip fork detection, only check for version upgrades if possible.

## Next Steps

After analysis:
1. [Discover available upgrades](upgrade_detection.md)
2. [Generate upgrade plans](planning_strategy.md)
3. [Execute upgrades](execution_guide.md)
