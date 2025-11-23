---
name: git-optimize
description: Comprehensive Git repository optimization including branch cleanup, garbage collection, and repository maintenance
version: 1.0.0
author: klauern
---

# Git Optimize

## Overview

The `git-optimize` skill provides comprehensive Git repository maintenance through a suite of cleanup and optimization operations:

1. **Branch Cleanup** - Remove merged, stray, and orphaned branches (git-trim + aliases)
2. **Repository Optimization** - Garbage collection, repacking, and pruning
3. **Remote Maintenance** - Prune deleted remote refs
4. **Combined Workflows** - One-command full optimization (`git trimall`)

This skill integrates:
- **git-trim**: Smart merge-aware branch detection
- **cleanup/sweep**: Alias-based merged branch removal
- **pruner/repacker**: Deep repository optimization
- **optimize**: Combined pruning and repacking

## When to Use This Skill

Use this skill when you need to:

- Clean up branches after PR merges
- Optimize repository size and performance
- Prepare repositories for archival or handoff
- Audit repository health
- Automate maintenance workflows
- Speed up operations in large repositories

## Quick Start

```bash
# Show all available optimization commands
User: Show me my git optimization aliases

# Clean up merged branches (fast)
User: Run git cleanup

# Deep repository optimization (slow)
User: Optimize my repository

# Full cleanup workflow
User: Run git trimall
```

## Commands Overview

### Branch Cleanup (Fast Operations)

**cleanup**
```bash
git cleanup
```
Removes branches already merged into master. Safe and fast.

**sweep**
```bash
git sweep
```
More aggressive cleanup of merged branches from master/develop. Excludes current branch and base branches.

**git-trim**
```bash
git trim --dry-run          # Preview
git trim                    # Execute with confirmation
```
Smart detection of merged (classic/rebase/squash), stray, and orphaned branches.

### Repository Optimization (Slow Operations)

**pruner**
```bash
git pruner
```
Prunes all unreachable objects. Takes time but reclaims space.

**repacker**
```bash
git repacker
```
Repack repository with optimal delta compression. Overnight operation for large repos.

**optimize**
```bash
git optimize
```
Runs `pruner + repacker + prune-packed`. Full optimization cycle.

### Combined Workflows

**trimall**
```bash
git trimall
```
Complete maintenance workflow:
1. Fetch and prune remotes
2. Run git-trim (all categories)
3. Run cleanup (merged branches)
4. Run sweep (aggressive)
5. Run optimize (full optimization)

One command for complete repository health!

## Detailed Command Reference

### git cleanup

**Purpose**: Remove local branches already merged into master

**Command**:
```bash
git branch --merged | grep -v '\\*\\|master' | xargs -n 1 git branch -d
```

**Behavior**:
- Lists branches merged into current HEAD
- Excludes current branch (`*`) and `master`
- Deletes using `-d` (safe deletion, fails if unmerged)

**When to use**: After merging PRs, quick cleanup of finished work

**Safety**: High (uses `-d`, not `-D`)

---

### git sweep

**Purpose**: Aggressive cleanup of branches merged into master or develop

**Command**:
```bash
git branch --merged $(git rev-parse master) | \
  egrep -v "(^\\*|^\\s*(master|develop)$)" | \
  xargs git branch -d
```

**Behavior**:
- Checks if merged into master specifically
- Excludes current branch, master, and develop
- Can pass `-f` to force deletion

**When to use**: Periodic maintenance, git-flow repos

**Safety**: High (uses `-d` unless `-f` passed)

---

### git-trim

**Purpose**: Smart branch detection across merge styles

**Installation**:
```bash
brew install foriequal0/git-trim/git-trim
# or
cargo install git-trim
```

**Commands**:
```bash
git trim --dry-run          # Preview
git trim                    # Interactive
git trim --no-update        # Skip fetch
```

**Detection**:
- **Merged**: Classic merge, rebase/ff, squash
- **Stray**: Upstream deleted, may have unmerged commits
- **Diverged**: Upstream exists but diverged
- **Local**: No upstream tracking
- **Remote**: Remote branches

**Configuration**:
```bash
# Git-flow support
git config trim.bases "develop,master"

# Exclude branches
git config trim.exclude "staging production"
```

**When to use**: When you need merge-style awareness, git-flow repos

**Safety**: High (interactive confirmation for stray)

**See**: [references/merge_detection.md](references/merge_detection.md)

---

### git pruner

**Purpose**: Remove all unreachable objects now

**Command**:
```bash
git prune --expire=now
git reflog expire --expire-unreachable=now --rewrite --all
```

**Behavior**:
- Prunes objects not reachable from any ref
- Expires reflog entries immediately
- Rewrites reflog history

**When to use**: Before repacking, after heavy rebasing/force pushes

**Safety**: Medium (removes unreachable objects permanently)

**Time**: Minutes to hours for large repos

---

### git repacker

**Purpose**: Optimal delta compression for repository

**Command**:
```bash
git repack -a -d --depth=250 --window=250
```

**Behavior**:
- Repacks all objects into single pack
- Deep delta chains (depth=250) for better compression
- Large scan window (window=250) for best delta candidates
- Removes old packs after success

**When to use**: Periodic optimization, before cloning/archiving

**Safety**: High (doesn't remove objects)

**Time**: Hours to overnight for large repos

**Benefits**:
- Significantly smaller `.git` directory
- Faster network operations (clone/fetch/push)
- Better compression for large files

**Based on**: Linus Torvalds' recommendations

---

### git optimize

**Purpose**: Complete optimization cycle

**Command**:
```bash
git pruner
git repacker
git prune-packed
```

**Workflow**:
1. Remove unreachable objects
2. Repack with optimal compression
3. Remove redundant packs

**When to use**: Monthly maintenance, after major refactoring

**Safety**: Medium (pruner removes objects)

**Time**: Hours to overnight

---

### git trimall

**Purpose**: Complete repository maintenance workflow

**Command** (as defined in your `.gitconfig`):
```bash
git trimall
```

**Steps**:
```
1. Fetching and pruning remotes...
   → git fetch --all --prune

2. Running git-trim...
   → git trim --no-confirm -d merged:*,stray,diverged:*,local,remote:*

3. Running cleanup...
   → git cleanup

4. Running sweep...
   → git sweep

5. Optimizing repository...
   → git optimize

Done!
```

**When to use**: Weekly/monthly full maintenance

**Safety**: Medium (combines multiple operations)

**Time**: 10 minutes to hours depending on repo size

**Output**: Shows progress through each step

---

## Configuration

### Git Config Location

Your aliases are defined in `~/.gitconfig`:

```ini
[alias]
    cleanup = "!git branch --merged | grep  -v '\\*\\|master' | xargs -n 1 git branch -d"

    sweep = "!f(){ git branch --merged $([[ $1 != \"-f\" ]] && git rev-parse master) | egrep -v \"(^\\*|^\\s*(master|develop)$)\" | xargs git branch -d; }; f"

    trimall = "!f() { \
        echo '1. Fetching and pruning remotes...'; \
        git fetch --all --prune; \
        echo '2. Running git-trim...'; \
        git trim --no-confirm -d merged:*,stray,diverged:*,local,remote:*; \
        echo '3. Running cleanup...'; \
        git cleanup; \
        echo '4. Running sweep...'; \
        git sweep; \
        echo '5. Optimizing repository...'; \
        git optimize; \
        echo 'Done!'; \
    }; f"

    pruner = "!git prune --expire=now; git reflog expire --expire-unreachable=now --rewrite --all"

    repacker = "!git repack -a -d --depth=250 --window=250"

    optimize = "!git pruner; git repacker; git prune-packed"
```

### git-trim Configuration

```bash
# Git-flow: multiple base branches
git config trim.bases "develop,master"

# Exclude long-lived branches
git config trim.exclude "staging production qa"

# Per-repository settings
cd /path/to/repo
git config trim.bases "main"
```

**See**: [references/configuration.md](references/configuration.md)

## Workflows

### Daily Workflow (After PR Merge)

```bash
git checkout main
git pull
git cleanup
```

Fast, safe cleanup of merged branches.

---

### Weekly Maintenance

```bash
git fetch --all --prune
git trim --dry-run      # Review
git trim                # Confirm
```

Branch cleanup with merge-style awareness.

---

### Monthly Deep Clean

```bash
git trimall
```

Full workflow: branches + optimization. Takes time but worth it.

---

### Pre-Archive Optimization

```bash
# Heavy optimization before handoff/archive
git optimize
```

Minimize repository size, maximize compression.

---

## Model Strategy

This skill uses different Claude models for optimal performance:

### Claude 4.5 Haiku

**Use for**:
- Git command execution
- Alias listing and explanation
- Configuration reading
- Simple branch inspection

### Claude 4.5 Sonnet

**Use for**:
- Analyzing branch relationships
- Recommending maintenance strategies
- Explaining optimization benefits
- Troubleshooting complex issues

## Installation Requirements

### git-trim (Optional but Recommended)

```bash
# macOS
brew install foriequal0/git-trim/git-trim

# All platforms (requires Rust)
cargo install git-trim

# Pre-built binaries
# Download from: https://github.com/foriequal0/git-trim/releases
```

**Verify**:
```bash
git-trim --version
```

**See**: [references/installation.md](references/installation.md)

### Aliases (Already Configured)

Your aliases are already in `~/.gitconfig`. To verify:

```bash
git config alias.cleanup
git config alias.trimall
git config alias.optimize
```

## Examples

### Example 1: Quick Branch Cleanup

**Scenario**: Just merged 3 PRs, want to clean up.

**See**: [references/example_workflows.md](references/example_workflows.md#example-1-quick-cleanup)

### Example 2: Weekly Maintenance

**Scenario**: Every Monday, clean branches + light optimization.

**See**: [references/example_workflows.md](references/example_workflows.md#example-2-weekly-routine)

### Example 3: Deep Optimization

**Scenario**: Repository is slow, .git folder is huge.

**See**: [references/example_workflows.md](references/example_workflows.md#example-3-deep-optimization)

### Example 4: Git-Flow Repository

**Scenario**: Project with develop + master branches.

**See**: [references/example_workflows.md](references/example_workflows.md#example-4-git-flow-maintenance)

## Safety & Best Practices

### Always Safe
- `git cleanup` (uses `-d`)
- `git sweep` (uses `-d`)
- `git trim --dry-run`
- `git repacker`

### Requires Caution
- `git pruner` (removes unreachable objects)
- `git sweep -f` (forces deletion)
- `git optimize` (includes pruner)
- `git trimall` (does everything)

### Best Practices

1. **Dry-run first**: Use `git trim --dry-run` before executing
2. **Backup branches**: Push important work before aggressive cleanup
3. **Understand commands**: Review what each alias does
4. **Schedule heavy ops**: Run `optimize` overnight or during downtime
5. **Test on clones**: Try on clones first if unsure
6. **Use reflog**: Remember `git reflog` for recovery

## Troubleshooting

### git-trim not found

```bash
# Install
brew install foriequal0/git-trim/git-trim

# Or use fallback aliases
git cleanup
git sweep
```

### Alias not working

```bash
# Check definition
git config alias.cleanup

# Re-source config
# (no action needed, git reads ~/.gitconfig automatically)
```

### Repository still large after optimize

```bash
# Check size
du -sh .git

# Aggressive cleanup
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**See**: [references/troubleshooting.md](references/troubleshooting.md)

## Performance Impact

| Command | Time | Space Saved | Risk |
|---------|------|-------------|------|
| cleanup | Seconds | Minimal | Very Low |
| sweep | Seconds | Minimal | Low |
| git-trim | Seconds-Minutes | Minimal | Low |
| pruner | Minutes-Hours | Medium | Medium |
| repacker | Hours-Overnight | High | Low |
| optimize | Hours-Overnight | High | Medium |
| trimall | 10min-Hours | High | Medium |

## Reference Documentation

- **[Installation Guide](references/installation.md)**: Setup instructions for git-trim
- **[Merge Detection](references/merge_detection.md)**: How git-trim detects merges
- **[Configuration](references/configuration.md)**: Alias and git-trim config
- **[Workflows](references/workflows.md)**: Common maintenance scenarios
- **[Automation](references/automation.md)**: Hooks and scripts
- **[Example Workflows](references/example_workflows.md)**: Step-by-step examples
- **[Troubleshooting](references/troubleshooting.md)**: Common issues and solutions

## Version History

- **1.0.0** (2025-01-22): Initial release
  - Integration with existing git aliases
  - git-trim support and documentation
  - Branch cleanup workflows
  - Repository optimization strategies
  - Model-optimized execution
