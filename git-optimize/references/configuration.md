# Configuration

## Overview

git-trim uses Git's native configuration system for settings. Configuration can be set at repository-level (`.git/config`) or globally (`~/.gitconfig`).

## Configuration Options

### trim.bases

**Purpose**: Define multiple base branches for git-flow workflows

**Default**: Auto-detected (main, master, develop)

**Example**:
```bash
# Repository-specific
git config trim.bases "develop,master"

# Global (all repos)
git config --global trim.bases "develop,main"
```

**Use case**: Git-flow repositories with both master and develop branches

**Effect**:
- git-trim checks if branches are merged into ANY of these bases
- Branch is safe to delete if merged into at least one base

### trim.exclude

**Purpose**: Permanently exclude branches from cleanup

**Default**: None (only current branch is automatically excluded)

**Example**:
```bash
# Exclude staging and production branches
git config trim.exclude "staging production qa-testing"

# Add more branches (space-delimited)
git config trim.exclude "staging production develop-legacy hotfix-*"
```

**Use case**: Long-lived branches that should never be deleted

**Effect**:
- Excluded branches are never shown in trim output
- Applies to both merged and stray classifications

**Patterns**:
- Exact match: `staging`
- No glob support (yet) - specify each branch explicitly

## Global vs. Repository Configuration

### Repository-Level (Recommended)

Set config for current repository only:

```bash
cd /path/to/repo
git config trim.bases "develop,master"
git config trim.exclude "staging"
```

**Pros**:
- Different repos can have different workflows
- Committed in repo's `.git/config`
- Doesn't affect other projects

### Global (All Repositories)

Set config for all repositories:

```bash
git config --global trim.bases "main"
git config --global trim.exclude "staging production"
```

**Pros**:
- Consistent behavior across all repos
- Set once, apply everywhere
- Good for personal conventions

**Cons**:
- May not match all repo workflows
- Can cause confusion in repos with different branching strategies

## Viewing Configuration

### Show current config

```bash
# Repository-specific
git config trim.bases
git config trim.exclude

# Global
git config --global trim.bases
git config --global trim.exclude

# All config (including defaults)
git config --list | grep trim
```

### Show effective config

git-trim shows which config is being used:

```bash
git-trim --dry-run
# Output includes:
# Base branches: origin/main, origin/develop
# Excluded branches: staging, production
```

## Removing Configuration

```bash
# Unset repository config
git config --unset trim.bases
git config --unset trim.exclude

# Unset global config
git config --global --unset trim.bases
git config --global --unset trim.exclude
```

## Common Configurations

### GitHub Flow (single base)

```bash
git config trim.bases "main"
```

### Git Flow (dual base)

```bash
git config trim.bases "develop,master"
git config trim.exclude "staging production"
```

### Trunk-Based Development

```bash
git config trim.bases "trunk"
git config trim.exclude "release-*"
```

### Enterprise Workflow

```bash
git config trim.bases "develop,master,main"
git config trim.exclude "staging qa production hotfix develop-v2"
```

## Configuration File Locations

### Repository-Level
```
/path/to/repo/.git/config
```

Example contents:
```ini
[trim]
    bases = develop,master
    exclude = staging production
```

### Global
```
~/.gitconfig
```

Example contents:
```ini
[trim]
    bases = main
    exclude = staging
```

### System-Wide (Rare)
```
/etc/gitconfig
```

## Advanced Patterns

### Temporary Override

Override config for a single command:

```bash
# Temporarily ignore exclusions (not supported directly by git-trim)
# Instead, modify config temporarily:
ORIGINAL=$(git config trim.exclude)
git config --unset trim.exclude
git-trim --dry-run
git config trim.exclude "$ORIGINAL"
```

### Per-Remote Configuration

git-trim doesn't directly support per-remote config, but you can:

```bash
# Different bases for different remotes (workaround)
git config trim.bases "origin/main,upstream/develop"
```

Note: git-trim will check against all specified bases regardless of remote.

## Configuration Validation

Check if config is valid:

```bash
# Verify bases exist
git config trim.bases | tr ',' '\n' | while read branch; do
  git show-ref --verify refs/remotes/origin/$branch >/dev/null 2>&1 \
    && echo "✓ $branch exists" \
    || echo "✗ $branch not found"
done

# Verify exclusions are real branches
git config trim.exclude | tr ' ' '\n' | while read branch; do
  git show-ref --verify refs/heads/$branch >/dev/null 2>&1 \
    && echo "✓ $branch exists" \
    || echo "⚠ $branch doesn't exist (yet)"
done
```

## Troubleshooting

### Config not taking effect

1. Check config is set:
   ```bash
   git config trim.bases
   ```

2. Verify you're in the right directory:
   ```bash
   pwd
   git rev-parse --show-toplevel
   ```

3. Check global vs. local precedence:
   ```bash
   git config --list --show-origin | grep trim
   ```

### Wrong branches being excluded

1. Check for typos:
   ```bash
   git config trim.exclude
   ```

2. Remember: space-delimited, not comma-delimited:
   ```bash
   # Correct
   git config trim.exclude "staging production"

   # Incorrect
   git config trim.exclude "staging,production"
   ```

### Bases not detected

1. Ensure branches exist on remote:
   ```bash
   git ls-remote --heads origin
   ```

2. Specify explicitly:
   ```bash
   git config trim.bases "$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)"
   ```

## References

- Git config documentation: `git help config`
- git-trim options: `git-trim --help`
