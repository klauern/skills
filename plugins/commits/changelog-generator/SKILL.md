---
name: changelog-generator
description: Generates CHANGELOG.md files from conventional commits using semantic versioning principles. Groups changes by type (features, fixes, breaking changes) and formats them in Keep a Changelog style.
version: 1.0.0
author: klauern
---

# Changelog Generator

## Overview

This skill generates and maintains CHANGELOG.md files from conventional commits. It parses git history, groups changes by type, identifies breaking changes, and formats everything following the Keep a Changelog specification and semantic versioning principles.

## Quick Start

### Slash Commands

- **`/changelog`**: Generate or update CHANGELOG.md - see [`../commands/changelog.md`](../commands/changelog.md)
- **`/changelog-release`**: Create changelog for new release - see [`../commands/changelog-release.md`](../commands/changelog-release.md)

### Core Documentation

- **[Format Specification](references/format-spec.md)** - CHANGELOG.md structure and formatting
- **[Grouping Rules](references/grouping-rules.md)** - How commits are categorized
- **[Versioning Guide](references/versioning-guide.md)** - Semantic versioning and release types

## When to Use This Skill

Use this skill when:

- Preparing a new release and need to document changes
- User asks to "generate changelog", "update changelog", or "create release notes"
- Setting up changelog automation
- Reviewing changes between versions
- Creating release documentation

## Workflow Overview

### Generation Process

1. **Parse commits** → Read conventional commits from git history
2. **Group by type** → Categorize as features, fixes, breaking changes, etc.
3. **Determine version** → Calculate next version based on changes
4. **Format sections** → Create markdown sections for each type
5. **Update file** → Insert new version entry into CHANGELOG.md

### Commit Grouping

Commits are grouped by type:

- **Breaking Changes**: Breaking changes (highest priority)
- **Features**: `feat:` commits (new functionality)
- **Bug Fixes**: `fix:` commits (corrections)
- **Performance**: `perf:` commits (speed improvements)
- **Documentation**: `docs:` commits (if significant)
- **Other**: Grouped by type (refactor, build, ci, etc.)

**See [grouping-rules.md](references/grouping-rules.md) for detailed categorization.**

### Version Determination

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes present
- **MINOR**: New features added (no breaking changes)
- **PATCH**: Only bug fixes

**See [versioning-guide.md](references/versioning-guide.md) for version calculation.**

## Sub-Agent Strategy

### Use Haiku 4.5 for

- Parsing git log output
- Extracting commit types and scopes
- Simple grouping by type
- Markdown formatting

### Use Sonnet 4.5 for

- Determining semantic version bumps
- Identifying breaking changes from footers
- Generating release summaries
- Deciding what to include/exclude

## Output Format

### Changelog Entry

```markdown
## [2.1.0] - 2024-01-15

### Breaking Changes

- **api**: Response format changed from array to object ([abc1234])
  - Migration: Update client code to access `data.items` instead of `data`

### Features

- **auth**: Add OAuth login support ([def5678])
- **api**: Add rate limiting to endpoints ([ghi9012])
- **ui**: Add dark mode toggle ([jkl3456])

### Bug Fixes

- **auth**: Resolve null pointer in token validation ([mno7890])
- **api**: Fix error handling for malformed requests ([pqr4321])

### Performance

- **db**: Optimize query performance with indexing ([stu6543])

[abc1234]: https://github.com/user/repo/commit/abc1234
[def5678]: https://github.com/user/repo/commit/def5678
```

### Full CHANGELOG.md Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Features

- Upcoming features not yet released

## [2.1.0] - 2024-01-15

[Version sections as above...]

## [2.0.0] - 2024-01-01

[Previous version...]

[Unreleased]: https://github.com/user/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/repo/releases/tag/v2.0.0
```

## Generation Modes

### Mode 1: New Release

Generate entry for unreleased commits:

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%H|%s|%b"

# Determine version bump
# Generate changelog section
# Update CHANGELOG.md
```

### Mode 2: Update Unreleased

Add commits to Unreleased section:

```bash
# Get commits since last release
# Add to Unreleased section
# Don't create version yet
```

### Mode 3: Full Regeneration

Regenerate entire changelog from history:

```bash
# Get all tags
git tag --sort=-version:refname

# For each version, generate section
# Combine into CHANGELOG.md
```

### Mode 4: Version Range

Generate changelog for specific range:

```bash
# Get commits between tags
git log v1.0.0..v2.0.0 --pretty=format:"%H|%s|%b"

# Generate section for this range
```

## Changelog Sections

### Priority Order

1. **Breaking Changes** (if any)
2. **Security** (if any security fixes)
3. **Deprecated** (if any deprecations)
4. **Features** (new capabilities)
5. **Bug Fixes** (corrections)
6. **Performance** (optimizations)
7. **Documentation** (if user-facing)
8. **Other** (optional, grouped by type)

### Section Content

Each entry includes:

```markdown
- **scope**: Description ([commit-hash])
  - Additional context if breaking change or complex
```

Example:

```markdown
### Features

- **auth**: Add OAuth login support ([abc1234])
- **api**: Add rate limiting with configurable limits ([def5678])
  - Default: 100 requests per minute for authenticated users
```

## Inclusion Rules

### Always Include

- Features (`feat:`)
- Bug fixes (`fix:`)
- Breaking changes (any type with `!` or `BREAKING CHANGE:`)
- Security fixes (`fix:` with security-related scope)
- Performance improvements (`perf:`)

### Conditionally Include

- Documentation (`docs:`) - Only if user-facing
- Deprecations (`chore:` with deprecation notice)
- Reverts (`revert:`) - Only if reverting released feature

### Usually Exclude

- Refactors (`refactor:`) - Internal changes
- Tests (`test:`) - Not user-facing
- Build changes (`build:`) - Internal tooling
- CI changes (`ci:`) - Internal automation
- Chores (`chore:`) - Maintenance tasks

**See [grouping-rules.md](references/grouping-rules.md) for complete rules.**

## Configuration Options

### Project Configuration

Customize via `.changelogrc.json`:

```json
{
  "types": {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance",
    "docs": "Documentation"
  },
  "scopes": {
    "auth": "Authentication",
    "api": "API",
    "ui": "User Interface"
  },
  "includeCommitLinks": true,
  "breakingChangesTitle": "Breaking Changes",
  "hideTypes": ["chore", "build", "ci"]
}
```

### Version Bumping

```json
{
  "versionBump": {
    "breakingChanges": "major",
    "features": "minor",
    "fixes": "patch"
  }
}
```

## Automation

### Manual Generation

```bash
# Generate changelog for new release
/changelog

# Update with specific version
/changelog-release 2.1.0
```

### CI/CD Integration

```yaml
# .github/workflows/release.yml
- name: Generate Changelog
  run: |
    claude "/changelog-release $(cat VERSION)"
    git add CHANGELOG.md
    git commit -m "docs: update changelog for release"
```

### Pre-release Hook

```bash
# .git/hooks/pre-push
# Auto-update unreleased section
claude "/changelog" --unreleased
```

## Best Practices

**For entries**:
- Be concise but descriptive
- Focus on user impact, not implementation
- Link to commits for details
- Group related changes by scope

**For versions**:
- Follow semantic versioning strictly
- Mark breaking changes clearly
- Provide migration guidance for breaking changes
- Include release dates

**For maintenance**:
- Keep Unreleased section current
- Create release entry when tagging
- Don't edit historical entries
- Link to diffs between versions

**For detailed guidelines**, see [`references/format-spec.md`](references/format-spec.md)

## Examples

### Example 1: Minor Release (Features)

```markdown
## [1.2.0] - 2024-01-15

### Features

- **auth**: Add OAuth login with Google provider ([abc1234])
- **ui**: Add dark mode toggle to settings ([def5678])

### Bug Fixes

- **api**: Resolve timeout on large requests ([ghi9012])
```

Version: 1.2.0 (MINOR bump - features added)

### Example 2: Major Release (Breaking)

```markdown
## [2.0.0] - 2024-01-15

### Breaking Changes

- **api**: Change response format to nested structure ([abc1234])
  - **Migration**: Update client code to access `data.items` instead of `data` array
  - **Reason**: Allows pagination metadata and better extensibility

### Features

- **api**: Add pagination support with metadata ([def5678])
```

Version: 2.0.0 (MAJOR bump - breaking changes)

### Example 3: Patch Release (Fixes Only)

```markdown
## [1.1.1] - 2024-01-15

### Bug Fixes

- **auth**: Fix token expiration check ([abc1234])
- **ui**: Resolve button alignment on mobile ([def5678])
```

Version: 1.1.1 (PATCH bump - fixes only)

## Documentation Index

### Core Guides

- **[format-spec.md](references/format-spec.md)** - CHANGELOG.md format specification
- **[grouping-rules.md](references/grouping-rules.md)** - Commit categorization rules
- **[versioning-guide.md](references/versioning-guide.md)** - Semantic versioning guide

### Command Documentation

- **[changelog.md](../commands/changelog.md)** - Generate/update CHANGELOG.md
- **[changelog-release.md](../commands/changelog-release.md)** - Create release entry
