---
name: version-manager
description: Local skill for managing versions in the klauern-skills repository. Use when bumping versions for this repository's plugins after modifying skills, commands, or metadata. Detects changes via git, infers version bump type from conventional commits, updates plugin.json and marketplace.json, generates changelog entries, and creates conventional commits. Triggered by /bump-version command or used directly via scripts.
---

# Version Manager (Local Skill)

**Repository-specific version management for klauern-skills.**

This local skill helps you maintain semantic versioning in this repository as you develop plugins. This skill helps you:

1. Detect what changed (skills, commands, metadata)
2. Infer the appropriate version bump (major/minor/patch)
3. Update version numbers in plugin.json and marketplace.json
4. Generate changelog entries
5. Create conventional commits for the release

## Quick Start

**Recommended: Use the /bump-version command for guided workflow:**

```bash
/bump-version <plugin-name>
```

**Or manual workflow using scripts directly:**

```bash
# 1. Detect changes in a plugin
python .claude/skills/version-manager/scripts/detect_changes.py plugins/<plugin-name>

# 2. Infer bump type from commits
python .claude/skills/version-manager/scripts/infer_bump_type.py

# 3. Bump version (with confirmation)
python .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> <major|minor|patch>

# 4. Update changelog
python .claude/skills/version-manager/scripts/update_changelog.py <new-version>

# 5. Commit changes
git add .
git commit -m "chore(release): bump <plugin-name> to <version>"
```

## Workflow Decision Tree

Use this decision tree to determine your path:

```
Start
  │
  ├─ Creating a release PR?
  │  └─ YES → Follow "Complete Release Workflow"
  │
  ├─ Just added/modified a skill?
  │  └─ YES → Follow "Quick Version Bump"
  │
  ├─ Made breaking changes?
  │  └─ YES → Follow "Manual Bump with Override"
  │
  └─ Want to review changes first?
     └─ YES → Follow "Change Detection Only"
```

## Complete Release Workflow

Use this when preparing a release PR with all changes properly versioned.

### Step 1: Detect Changes

Identify what changed in the plugin since the last version:

```bash
python .claude/skills/version-manager/scripts/detect_changes.py plugins/<plugin-name>
```

**Output (JSON)**:
```json
{
  "skills_changed": ["skill-name-1"],
  "commands_changed": ["command.md"],
  "metadata_changed": false,
  "other_files": [],
  "since_ref": "v2.0.0"
}
```

**Interpreting results:**
- `skills_changed`: Skills that were modified or added
- `commands_changed`: Commands that were modified or added
- `metadata_changed`: Whether plugin.json or marketplace.json changed
- `since_ref`: Git reference used for comparison (last version tag)

### Step 2: Infer Bump Type

Analyze conventional commits to suggest the version bump type:

```bash
python .claude/skills/version-manager/scripts/infer_bump_type.py
```

**Output (JSON)**:
```json
{
  "bump_type": "minor",
  "reason": "Found 2 new feature(s)",
  "commits_analyzed": 5,
  "breaking_changes": [],
  "features": [
    "feat(dev-utilities): add version-manager skill",
    "feat(commits): add validation"
  ],
  "fixes": [],
  "other": ["docs: update README"]
}
```

**Bump type rules:**
- **major**: Breaking changes found (commits with `!` or `BREAKING CHANGE:`)
- **minor**: New features found (`feat:` commits)
- **patch**: Bug fixes only (`fix:` commits) or no conventional commits

**Important**: This is a SUGGESTION. You can override if needed (see "Manual Bump" below).

### Step 3: Bump Versions

Update version numbers in plugin.json and marketplace.json:

```bash
# Dry run (preview changes)
python .claude/skills/version-manager/scripts/bump_version.py \
  plugins/<plugin-name> <major|minor|patch> --dry-run

# Actual bump
python .claude/skills/version-manager/scripts/bump_version.py \
  plugins/<plugin-name> <major|minor|patch>
```

**Output (JSON)**:
```json
{
  "plugin": {
    "old_version": "1.0.0",
    "new_version": "1.1.0",
    "file": "plugins/dev-utilities/.claude-plugin/plugin.json"
  },
  "marketplace": {
    "old_version": "2.0.0",
    "new_version": "2.1.0",
    "file": ".claude-plugin/marketplace.json"
  },
  "dry_run": false
}
```

**Note**: Both plugin and marketplace versions are updated. Marketplace version is kept >= the highest plugin version.

### Step 4: Update Changelog

Generate and prepend changelog entry:

```bash
python .claude/skills/version-manager/scripts/update_changelog.py <new-version>
```

**What it does:**
- Analyzes commits since last tag
- Groups by type (features, fixes, breaking changes, etc.)
- Prepends entry to CHANGELOG.md
- Uses emoji prefixes for readability

**Example output:**
```markdown
## [2.1.0] - 2024-01-15

### ✨ Features

- Add version-manager skill
- Add commit validation

### 📚 Documentation

- Update README
```

### Step 5: Create Commit

Create a conventional commit for the release:

```bash
git add .claude-plugin/marketplace.json \
        plugins/<plugin-name>/.claude-plugin/plugin.json \
        CHANGELOG.md

git commit -m "$(cat <<'EOF'
chore(release): bump <plugin-name> to <new-version>

- Updated <plugin-name> from <old-version> to <new-version>
- Updated marketplace from <old-version> to <new-version>
- Updated CHANGELOG.md
EOF
)"
```

**Commit message template:**
```
chore(release): bump <plugin-name> to <version>

- Updated <plugin-name> from X.Y.Z to A.B.C
- Updated marketplace from X.Y.Z to A.B.C
- Updated CHANGELOG.md
```

### Step 6: Tag (Optional)

If this is a release:

```bash
git tag v<new-version>
git push origin main --tags
```

## Quick Version Bump

**Scenario**: You just added a skill or modified a command and want to quickly bump versions.

```bash
# Detect changes
python .claude/skills/version-manager/scripts/detect_changes.py plugins/<plugin-name>

# Infer bump type
BUMP=$(python .claude/skills/version-manager/scripts/infer_bump_type.py | jq -r '.bump_type')

# Bump versions
python .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> $BUMP

# Get new version
NEW_VERSION=$(jq -r '.version' plugins/<plugin-name>/.claude-plugin/plugin.json)

# Update changelog
python .claude/skills/version-manager/scripts/update_changelog.py $NEW_VERSION

# Commit
git add .
git commit -m "chore(release): bump <plugin-name> to $NEW_VERSION"
```

## Manual Bump with Override

**Scenario**: The inferred bump type is wrong, or you want to force a specific bump.

```bash
# Detect changes
python .claude/skills/version-manager/scripts/detect_changes.py plugins/dev-utilities

# Infer bump type (just for reference)
python .claude/skills/version-manager/scripts/infer_bump_type.py
# Output suggests: "minor"

# Override with major (because you know it's breaking)
python .claude/skills/version-manager/scripts/bump_version.py plugins/dev-utilities major

# Continue with changelog and commit...
```

**When to override:**
- Adding a feature that you know breaks compatibility
- Semantic meaning requires different bump (e.g., docs-only should be patch)
- Fixing up incorrect previous version

## Change Detection Only

**Scenario**: You want to see what changed without bumping versions yet.

```bash
# See what changed
python .claude/skills/version-manager/scripts/detect_changes.py plugins/commits | jq

# See suggested bump
python .claude/skills/version-manager/scripts/infer_bump_type.py | jq

# Review output, then decide whether to proceed
```

## Hybrid Approach (Recommended)

The recommended workflow combines automation with human judgment:

```bash
# 1. Auto-detect
CHANGES=$(python .claude/skills/version-manager/scripts/detect_changes.py plugins/<plugin-name>)
INFERENCE=$(python .claude/skills/version-manager/scripts/infer_bump_type.py)

# 2. Review
echo "Changes detected:"
echo "$CHANGES" | jq
echo ""
echo "Suggested bump:"
echo "$INFERENCE" | jq

# 3. Decide (use AskUserQuestion if uncertain)
# - Accept suggestion
# - Override with different bump type
# - Cancel if changes need refinement

# 4. Execute
BUMP_TYPE="minor"  # or user's choice
python .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> $BUMP_TYPE

# 5. Finalize
NEW_VERSION=$(jq -r '.version' plugins/<plugin-name>/.claude-plugin/plugin.json)
python .claude/skills/version-manager/scripts/update_changelog.py $NEW_VERSION
git add .
git commit -m "chore(release): bump <plugin-name> to $NEW_VERSION"
```

## Understanding Semantic Versioning

For detailed semantic versioning rules specific to this marketplace, see [references/semver-guide.md](references/semver-guide.md).

**Quick reference:**

- **MAJOR (X.0.0)**: Breaking changes
  - Removed/renamed skills or commands
  - Changed behavior incompatibly
  - Removed dependencies

- **MINOR (x.Y.0)**: New features
  - Added skills or commands
  - New features in existing skills
  - New optional dependencies

- **PATCH (x.y.Z)**: Bug fixes
  - Bug fixes
  - Documentation
  - Performance improvements
  - Refactoring

## Understanding Marketplace Structure

For detailed information about how versions cascade through the marketplace, see [references/marketplace-structure.md](references/marketplace-structure.md).

**Quick reference:**

```
Marketplace (global version)
  └─ Plugin (plugin version)
      ├─ Skill (inherits plugin version)
      └─ Command (inherits plugin version)
```

**Version cascade rule:**
- Skill/Command change → Plugin version bumps → Marketplace version bumps
- Marketplace version must always be >= highest plugin version

## Common Scenarios

### Adding a New Skill

```bash
# After creating plugins/dev-utilities/version-manager/
python .claude/skills/version-manager/scripts/detect_changes.py plugins/dev-utilities
# Shows: skills_changed: ["version-manager"]

python .claude/skills/version-manager/scripts/infer_bump_type.py
# Shows: bump_type: "minor" (if you used feat: commit)

python .claude/skills/version-manager/scripts/bump_version.py plugins/dev-utilities minor
# dev-utilities: 1.0.0 → 1.1.0
# marketplace: 2.0.0 → 2.1.0

python .claude/skills/version-manager/scripts/update_changelog.py 2.1.0
git add .
git commit -m "chore(release): bump dev-utilities to 1.1.0"
```

### Fixing a Bug in a Command

```bash
# After fixing plugins/commits/commands/commit.md
python .claude/skills/version-manager/scripts/detect_changes.py plugins/commits
# Shows: commands_changed: ["commit.md"]

python .claude/skills/version-manager/scripts/infer_bump_type.py
# Shows: bump_type: "patch" (if you used fix: commit)

python .claude/skills/version-manager/scripts/bump_version.py plugins/commits patch
# commits: 1.5.2 → 1.5.3
# marketplace: 2.1.0 → 2.1.1

python .claude/skills/version-manager/scripts/update_changelog.py 2.1.1
git add .
git commit -m "chore(release): bump commits to 1.5.3"
```

### Making a Breaking Change

```bash
# After renaming a skill
python .claude/skills/version-manager/scripts/infer_bump_type.py
# Shows: bump_type: "major" (if you used feat!: commit)

python .claude/skills/version-manager/scripts/bump_version.py plugins/pull-requests major
# pull-requests: 2.0.0 → 3.0.0
# marketplace: 2.1.1 → 3.0.0

python .claude/skills/version-manager/scripts/update_changelog.py 3.0.0
git add .
git commit -m "chore(release): bump pull-requests to 3.0.0"
```

## Script Reference

### detect_changes.py

**Purpose**: Detect what changed in a plugin

**Usage**: `python .claude/skills/version-manager/scripts/detect_changes.py <plugin-path>`

**Output**: JSON with skills_changed, commands_changed, metadata_changed, other_files, since_ref

**When to use**: Start of version bump workflow to understand scope of changes

### infer_bump_type.py

**Purpose**: Suggest version bump type from conventional commits

**Usage**: `python .claude/skills/version-manager/scripts/infer_bump_type.py [since-ref]`

**Output**: JSON with bump_type, reason, commit analysis

**When to use**: To get automated suggestion for bump type (can be overridden)

### bump_version.py

**Purpose**: Update version numbers in JSON files

**Usage**: `python .claude/skills/version-manager/scripts/bump_version.py <plugin-path> <major|minor|patch> [--dry-run]`

**Output**: JSON with old_version, new_version for plugin and marketplace

**When to use**: After deciding on bump type, to update version files

### update_changelog.py

**Purpose**: Generate and prepend changelog entry

**Usage**: `python .claude/skills/version-manager/scripts/update_changelog.py <version> [since-ref] [changelog-path]`

**Output**: Updated CHANGELOG.md

**When to use**: After bumping versions, before committing

## Best Practices

1. **Always review inferred bump type** - automation suggests, you decide
2. **Use dry-run first** - preview version changes before applying
3. **Commit atomically** - version bumps should be separate from feature work
4. **Update changelog** - always generate changelog entry for versions
5. **Tag releases** - create git tags for version releases
6. **Use conventional commits** - enables automatic bump type inference
7. **Test before bumping** - ensure changes work before versioning
8. **Document breaking changes** - be explicit in commit messages and changelog
