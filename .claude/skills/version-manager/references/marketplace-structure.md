# Marketplace Structure and Version Management

## Directory Structure

```
klauern-skills/
├── .claude-plugin/
│   └── marketplace.json          # Global marketplace config
├── plugins/
│   ├── commits/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       # Plugin config & version
│   │   ├── commands/
│   │   │   ├── commit.md
│   │   │   └── commit-push.md
│   │   └── conventional-commits/  # Skill directory
│   │       ├── SKILL.md          # Skill metadata (no version)
│   │       └── references/
│   ├── pull-requests/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── commands/
│   │   └── pr-creator/           # Skill directory
│   └── dev-utilities/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── commands/
│       └── version-manager/      # Skill directory
├── CHANGELOG.md                  # Global changelog
└── README.md
```

## Version Hierarchy

### 1. Marketplace Version

**Location**: `.claude-plugin/marketplace.json`

```json
{
  "name": "klauern-skills",
  "version": "2.0.0",
  "author": "klauern",
  "plugins": [
    "./plugins/commits",
    "./plugins/pull-requests",
    "./plugins/dev-utilities"
  ]
}
```

**Purpose**: Global version for the entire marketplace

**Versioning rules**:
- MAJOR: When any plugin has a major version bump
- MINOR: When any plugin has a minor version bump
- PATCH: When any plugin has a patch version bump
- Should always be >= highest plugin version

### 2. Plugin Version

**Location**: `plugins/<name>/.claude-plugin/plugin.json`

```json
{
  "name": "commits",
  "version": "1.2.3",
  "description": "Conventional commit message creation",
  "commands": ["commit", "commit-push"],
  "skills": ["conventional-commits"]
}
```

**Purpose**: Version for an individual plugin

**Versioning rules**:
- MAJOR: Breaking changes to commands or skills
- MINOR: New commands or skills added
- PATCH: Bug fixes, documentation, internal improvements

### 3. Skills (No Version)

**Location**: `plugins/<name>/<skill-name>/SKILL.md`

```yaml
---
name: conventional-commits
description: Guide for creating conventional commits
---
```

**Important**: Skills themselves do NOT have versions. They inherit the version of their parent plugin.

## Version Cascade Rules

When changes occur, versions cascade as follows:

```
Skill changed
  ↓
Plugin version bumps
  ↓
Marketplace version bumps (if needed)
```

### Rule 1: Skill Changes Bump Plugin

Any change to a skill requires bumping the plugin version:

- Modified `SKILL.md` → Plugin PATCH (or higher based on change)
- Added files to skill → Plugin PATCH
- Modified skill scripts → Plugin PATCH (or MINOR if new functionality)
- Modified skill references → Plugin PATCH

### Rule 2: Command Changes Bump Plugin

Any change to a command requires bumping the plugin version:

- Modified command → Plugin PATCH (or higher based on change)
- Added command → Plugin MINOR
- Removed command → Plugin MAJOR

### Rule 3: Plugin Changes Bump Marketplace

Any plugin version bump requires evaluating marketplace version:

- Plugin MAJOR bump → Marketplace MAJOR
- Plugin MINOR bump → Marketplace MINOR (if marketplace version allows)
- Plugin PATCH bump → Marketplace PATCH (if marketplace version allows)

### Rule 4: Marketplace Version >= Max Plugin Version

The marketplace version should always be at least as high as the highest plugin version:

```
Marketplace: 2.1.0
  commits: 1.5.2      ✅ OK (1.5.2 < 2.1.0)
  pull-requests: 2.0.0   ✅ OK (2.0.0 < 2.1.0)
  dev-utilities: 1.0.0   ✅ OK (1.0.0 < 2.1.0)
```

```
Marketplace: 2.0.0
  commits: 1.5.2      ✅ OK
  pull-requests: 2.1.0   ❌ BAD (2.1.0 > 2.0.0)
  dev-utilities: 1.0.0   ✅ OK

Fix: Bump marketplace to 2.1.0
```

## Change Detection Strategy

### Git-based Detection

Use git to detect what changed since the last version tag:

```bash
# Get last version tag
git describe --tags --abbrev=0 --match=v*

# Get changed files since tag
git diff --name-only v2.0.0 HEAD

# Analyze changes:
# - plugins/commits/conventional-commits/SKILL.md → commits plugin changed
# - plugins/pull-requests/commands/pr.md → pull-requests plugin changed
# - .claude-plugin/marketplace.json → marketplace metadata changed
```

### Change Categories

1. **Skill changes**: `plugins/<name>/<skill-name>/**`
2. **Command changes**: `plugins/<name>/commands/**`
3. **Plugin metadata**: `plugins/<name>/.claude-plugin/plugin.json`
4. **Marketplace metadata**: `.claude-plugin/marketplace.json`
5. **Other files**: README, CHANGELOG, etc. (usually PATCH)

## Workflow Examples

### Scenario 1: Add New Skill to Existing Plugin

```bash
# 1. Create skill: plugins/dev-utilities/version-manager/
# 2. Detect: Skill added to dev-utilities
# 3. Bump: dev-utilities 1.0.0 → 1.1.0 (MINOR - new skill)
# 4. Bump: marketplace 2.0.0 → 2.1.0 (MINOR)
# 5. Commit: "feat(dev-utilities): add version-manager skill"
# 6. Tag: v2.1.0
```

### Scenario 2: Fix Bug in Command

```bash
# 1. Fix: plugins/commits/commands/commit.md
# 2. Detect: Command changed in commits
# 3. Bump: commits 1.5.2 → 1.5.3 (PATCH - bug fix)
# 4. Bump: marketplace 2.1.0 → 2.1.1 (PATCH)
# 5. Commit: "fix(commits): correct heredoc formatting"
# 6. Tag: v2.1.1
```

### Scenario 3: Breaking Change to Skill

```bash
# 1. Change: Rename pr-creator skill
# 2. Detect: Breaking change in pull-requests
# 3. Bump: pull-requests 2.0.0 → 3.0.0 (MAJOR)
# 4. Bump: marketplace 2.1.1 → 3.0.0 (MAJOR)
# 5. Commit: "feat(pull-requests)!: rename pr-creator to pull-request-creator"
# 6. Tag: v3.0.0
```

## Automation Hooks

Consider adding git hooks for automation:

### Pre-commit Hook

```bash
# Check that all plugin versions are <= marketplace version
```

### Post-commit Hook

```bash
# Auto-detect changes and suggest version bump
```

### Pre-push Hook

```bash
# Verify CHANGELOG.md is updated for version changes
```

## References

- Semantic Versioning: https://semver.org/
- Conventional Commits: https://www.conventionalcommits.org/
- Plugin specification: See plugin.json schema
- Marketplace specification: See marketplace.json schema
