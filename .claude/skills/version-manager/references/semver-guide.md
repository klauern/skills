# Semantic Versioning Guide for Plugin Marketplace

## Version Format

All versions follow semantic versioning: `MAJOR.MINOR.PATCH`

```
1.2.3
│ │ └─ Patch: Bug fixes, typos, minor improvements
│ └─── Minor: New features, backward-compatible changes
└───── Major: Breaking changes, incompatible API changes
```

## Determining Bump Type

### From Conventional Commits

Use conventional commit messages to determine the bump type automatically:

- **BREAKING CHANGE** or `!` suffix → **MAJOR** bump
  - `feat!: redesign skill loading mechanism`
  - `fix(api)!: remove deprecated function`
  - Commit body contains `BREAKING CHANGE:`

- **feat:** → **MINOR** bump
  - `feat(commits): add conventional commit validation`
  - `feat: new skill for managing versions`

- **fix:** → **PATCH** bump
  - `fix(pr-creator): correct template detection logic`
  - `fix: typo in skill description`

- **Other types** → **PATCH** bump (by default)
  - `docs: update README`
  - `chore: update dependencies`
  - `refactor: simplify version parsing`
  - `test: add integration tests`

### From Change Analysis

If conventional commits aren't used or you want manual control:

**MAJOR (X.0.0)**:
- Removed or renamed skills
- Removed or renamed commands
- Changed skill behavior in incompatible ways
- Changed command interfaces
- Removed dependencies that users rely on

**MINOR (x.Y.0)**:
- Added new skills
- Added new commands
- Added new features to existing skills
- Enhanced existing commands with new options
- Added new optional dependencies

**PATCH (x.y.Z)**:
- Bug fixes in skills or commands
- Documentation updates
- Performance improvements
- Code refactoring without behavior changes
- Fixed typos or formatting
- Internal improvements

## Plugin vs Marketplace Versions

### Plugin Versions

Each plugin has its own version in `plugins/<name>/.claude-plugin/plugin.json`:

```json
{
  "name": "commits",
  "version": "1.2.3",
  ...
}
```

**When to bump plugin version:**
- Changed any skill in the plugin
- Changed any command in the plugin
- Changed plugin metadata
- Changed plugin dependencies

### Marketplace Version

The marketplace has a global version in `.claude-plugin/marketplace.json`:

```json
{
  "version": "2.0.0",
  "plugins": [...]
}
```

**When to bump marketplace version:**
- Any plugin version changed
- Added or removed plugins
- Changed marketplace metadata
- Changed marketplace structure

**Rule**: Marketplace version should always be >= the highest plugin version.

## Examples

### Example 1: Adding a New Skill

```bash
# Changes:
# - Added plugins/dev-utilities/version-manager/

# Conventional commit:
git commit -m "feat(dev-utilities): add version-manager skill"

# Bumps:
# - dev-utilities plugin: 1.0.0 → 1.1.0 (MINOR)
# - marketplace: 2.0.0 → 2.1.0 (MINOR)
```

### Example 2: Fixing a Bug

```bash
# Changes:
# - Fixed bug in plugins/commits/commands/commit.md

# Conventional commit:
git commit -m "fix(commits): correct heredoc quoting in commit command"

# Bumps:
# - commits plugin: 1.2.3 → 1.2.4 (PATCH)
# - marketplace: 2.1.0 → 2.1.1 (PATCH)
```

### Example 3: Breaking Change

```bash
# Changes:
# - Renamed skill from pr-creator to pull-request-creator
# - Updated all references

# Conventional commit:
git commit -m "feat(pull-requests)!: rename pr-creator skill to pull-request-creator

BREAKING CHANGE: Skill name changed from pr-creator to pull-request-creator.
Users must update their slash commands."

# Bumps:
# - pull-requests plugin: 1.5.2 → 2.0.0 (MAJOR)
# - marketplace: 2.1.1 → 3.0.0 (MAJOR)
```

### Example 4: Multiple Changes

```bash
# Changes since last tag:
# - feat(commits): add commit validation
# - fix(pull-requests): template detection
# - docs: update README

# Inferred bump: MINOR (highest is feat)
# Bumps:
# - commits plugin: 1.2.4 → 1.3.0 (MINOR)
# - pull-requests plugin: 2.0.0 → 2.0.1 (PATCH for fix)
# - marketplace: 3.0.0 → 3.1.0 (MINOR, matches commits)
```

## Best Practices

1. **Always use conventional commits** for automatic version detection
2. **Bump versions atomically** - don't mix version bumps with feature work
3. **Update CHANGELOG.md** with each version
4. **Tag releases** with `v` prefix (e.g., `v2.1.0`)
5. **Test before bumping** - ensure changes work as expected
6. **Document breaking changes** clearly in commit messages and CHANGELOG
7. **Keep marketplace version in sync** with plugin versions
