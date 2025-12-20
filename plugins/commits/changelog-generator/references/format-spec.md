# Changelog Format Specification

Complete specification for CHANGELOG.md structure following Keep a Changelog format.

## Overview

The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) with conventional commits integration and semantic versioning.

### Core Principles

1. **Human-readable**: Written for users, not machines
2. **Chronological**: Newest releases first
3. **Versioned**: Each release gets a version number
4. **Categorized**: Changes grouped by type
5. **Linked**: Commits and diffs linked for reference

---

## File Structure

### Complete Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Features

- **ui**: Add dark mode toggle

## [2.1.0] - 2024-01-15

### Features

- **auth**: Add OAuth login support ([abc1234])
- **api**: Add rate limiting ([def5678])

### Bug Fixes

- **auth**: Fix token validation ([ghi9012])

## [2.0.0] - 2024-01-01

### Breaking Changes

- **api**: Change response format ([jkl3456])
  - Migration: Update client code to use `data.items`

### Features

- **api**: Add pagination support ([mno7890])

## [1.0.0] - 2023-12-01

### Features

- **core**: Initial release ([pqr1234])

[Unreleased]: https://github.com/user/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/repo/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0

[abc1234]: https://github.com/user/repo/commit/abc1234
[def5678]: https://github.com/user/repo/commit/def5678
[ghi9012]: https://github.com/user/repo/commit/ghi9012
[jkl3456]: https://github.com/user/repo/commit/jkl3456
[mno7890]: https://github.com/user/repo/commit/mno7890
[pqr1234]: https://github.com/user/repo/commit/pqr1234
```

---

## Header Section

### Title

```markdown
# Changelog
```

**Required**: Yes
**Format**: Level 1 heading

### Preamble

```markdown
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

**Required**: Recommended
**Purpose**: Explain format and versioning

---

## Version Sections

### Version Header

```markdown
## [2.1.0] - 2024-01-15
```

**Format**:
- Level 2 heading
- Version in brackets: `[X.Y.Z]`
- Space, dash, space
- Release date in ISO format: `YYYY-MM-DD`

### Unreleased Section

```markdown
## [Unreleased]
```

**Purpose**: Track upcoming changes not yet released
**Position**: First version section (after preamble)
**Date**: No date (not released yet)

### Version Linking

At bottom of file:

```markdown
[Unreleased]: https://github.com/user/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
```

**Format**: `[version]: compare-url`

---

## Change Categories

### Standard Categories

Listed in priority order:

1. **Breaking Changes** (or **BREAKING CHANGES**)
2. **Security**
3. **Deprecated**
4. **Removed**
5. **Features** (or **Added**)
6. **Changed**
7. **Bug Fixes** (or **Fixed**)
8. **Performance** (or **Performance Improvements**)
9. **Documentation**

### Category Headers

```markdown
### Breaking Changes
```

**Format**:
- Level 3 heading
- Title case or sentence case (be consistent)
- Use plural form

### Category Content

```markdown
### Features

- **auth**: Add OAuth login support ([abc1234])
- **api**: Add rate limiting to all endpoints ([def5678])
  - Default: 100 requests per minute
  - Configurable per endpoint
```

**Format**:
- Unordered list (bullet points with `-`)
- **Bold scope**: followed by colon
- Description: Concise, imperative mood
- Commit link: `([hash])` at end
- Additional context: Indented bullet points

---

## Entry Format

### Basic Entry

```markdown
- **scope**: Description ([commit-hash])
```

**Components**:
- `**scope**` - Bold scope/component name
- `: ` - Colon and space
- `Description` - Change description
- ` ` - Space
- `([hash])` - Commit reference in parentheses

### Entry with Context

```markdown
- **api**: Change response format to nested object ([abc1234])
  - Migration: Update client code to use `data.items` instead of `data`
  - Reason: Enables pagination and better extensibility
```

**When to add context**:
- Breaking changes (migration instructions)
- Complex features (usage examples)
- Security fixes (impact explanation)

### Entry without Scope

```markdown
- Add support for custom themes ([abc1234])
```

**Use when**:
- Change affects entire project
- No clear component scope
- Top-level feature

### Multiple Scopes

```markdown
- **auth, api**: Add token-based authentication ([abc1234])
```

**Use when**:
- Change affects multiple related scopes
- Keep list concise

---

## Breaking Changes Format

### Detailed Format

```markdown
### Breaking Changes

- **api**: Change response format from array to nested object ([abc1234])
  - **What changed**: Response is now `{ data: [...], meta: {...} }` instead of flat array
  - **Why**: Supports pagination and better extensibility
  - **Migration**: Update client code:
    ```javascript
    // Before
    const items = response;

    // After
    const items = response.data;
    ```
  - **Affects**: All API endpoints returning lists
```

**Include**:
- What changed
- Why it changed
- How to migrate (with examples)
- What's affected

### Concise Format

```markdown
### Breaking Changes

- **api**: Response format changed to nested object ([abc1234])
  - Migration: Use `response.data` instead of `response`
```

**Minimum**:
- Description of change
- Migration instructions

---

## Commit Links

### Short Hash Format (Recommended)

At end of entry:

```markdown
- **auth**: Add OAuth login ([abc1234])
```

At bottom of file:

```markdown
[abc1234]: https://github.com/user/repo/commit/abc1234567890
```

**Benefits**:
- Clean, readable entries
- Links still available
- Keep a Changelog standard

### Inline Format

```markdown
- **auth**: Add OAuth login (abc1234)
```

**No link definition needed**
**Use when**: Manual changelog or no repository

---

## Version Links

### Comparison Links

At bottom of file:

```markdown
[Unreleased]: https://github.com/user/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/repo/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

**Format**:
- Unreleased: `compare/latest-tag...HEAD`
- Versions: `compare/prev-tag...this-tag`
- First version: `releases/tag/v1.0.0`

### For Different Platforms

**GitHub**:
```markdown
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
```

**GitLab**:
```markdown
[2.1.0]: https://gitlab.com/user/repo/-/compare/v2.0.0...v2.1.0
```

**Bitbucket**:
```markdown
[2.1.0]: https://bitbucket.org/user/repo/branches/compare/v2.1.0%0Dv2.0.0
```

---

## Section Guidelines

### What to Include

**Always include**:
- User-facing features
- Bug fixes
- Breaking changes
- Security fixes
- Performance improvements
- Deprecations

**Sometimes include**:
- Documentation (if user-facing)
- Refactors (if significant user impact)
- Configuration changes (if user-facing)

**Usually exclude**:
- Internal refactors
- Test changes
- CI/CD changes
- Development tooling
- Dependency bumps (unless security)

### Description Guidelines

**Good descriptions**:
```markdown
- **auth**: Add OAuth login with Google and GitHub providers
- **api**: Fix null pointer error in user validation
- **ui**: Improve button contrast for accessibility
```

**Poor descriptions**:
```markdown
- Add feature (too vague)
- Fix bug (what bug?)
- Update code (what changed?)
```

**Rules**:
- Be specific about what changed
- Use imperative mood (add, fix, update)
- Focus on user impact
- Keep under 100 characters

---

## Date Format

### Release Date

```markdown
## [2.1.0] - 2024-01-15
```

**Format**: `YYYY-MM-DD` (ISO 8601)

**Use**:
- UTC date of release
- Date tag was created
- Date published to registry

### Date Consistency

**Correct**:
```markdown
## [2.1.0] - 2024-01-15
## [2.0.0] - 2024-01-01
## [1.9.0] - 2023-12-15
```

**Incorrect**:
```markdown
## [2.1.0] - 2024-01-15
## [2.0.0] - January 1, 2024
## [1.9.0] - 12/15/23
```

---

## Examples by Release Type

### Patch Release (Bug Fixes Only)

```markdown
## [1.0.1] - 2024-01-15

### Bug Fixes

- **auth**: Fix token expiration check ([abc1234])
- **ui**: Resolve button alignment on mobile ([def5678])
- **api**: Handle null values in request validation ([ghi9012])
```

### Minor Release (Features Added)

```markdown
## [1.1.0] - 2024-01-15

### Features

- **auth**: Add OAuth login support ([abc1234])
- **ui**: Add dark mode toggle ([def5678])

### Bug Fixes

- **api**: Fix timeout handling ([ghi9012])
```

### Major Release (Breaking Changes)

```markdown
## [2.0.0] - 2024-01-15

### Breaking Changes

- **api**: Change authentication from API keys to OAuth ([abc1234])
  - Migration: Replace API key headers with OAuth bearer tokens
  - See migration guide: docs/migration-v2.md

### Features

- **auth**: Add OAuth 2.0 support ([def5678])
- **api**: Add token refresh endpoints ([ghi9012])

### Deprecated

- **api**: API key authentication (will be removed in v3.0.0) ([jkl3456])
```

---

## Automation Markers

### Version Placeholder

During development:

```markdown
## [Unreleased]

### Features

- **ui**: Add search functionality
```

When releasing:

```markdown
## [2.1.0] - 2024-01-15

### Features

- **ui**: Add search functionality ([abc1234])
```

### Auto-generated Notice

```markdown
<!--
This changelog is auto-generated from conventional commits.
Do not edit manually - changes will be overwritten.
-->
```

---

## Full Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Features

- Upcoming features

## [X.Y.Z] - YYYY-MM-DD

### Breaking Changes

- **scope**: Description ([hash])
  - Migration instructions

### Security

- **scope**: Security fix description ([hash])

### Deprecated

- **scope**: Deprecated feature ([hash])

### Removed

- **scope**: Removed feature ([hash])

### Features

- **scope**: New feature description ([hash])

### Changed

- **scope**: Changed behavior ([hash])

### Bug Fixes

- **scope**: Bug fix description ([hash])

### Performance

- **scope**: Performance improvement ([hash])

### Documentation

- **scope**: Documentation update ([hash])

[Unreleased]: https://github.com/user/repo/compare/vX.Y.Z...HEAD
[X.Y.Z]: https://github.com/user/repo/compare/vX.Y.Z-1...vX.Y.Z

[hash]: https://github.com/user/repo/commit/hash
```

---

## Validation

### Valid Changelog

- ✅ Has title "# Changelog"
- ✅ Has preamble with Keep a Changelog reference
- ✅ Has [Unreleased] section first
- ✅ Versions in descending order (newest first)
- ✅ Dates in ISO format (YYYY-MM-DD)
- ✅ Categories in standard order
- ✅ Entries follow format
- ✅ Commit links defined
- ✅ Version compare links at bottom

### Common Issues

❌ **Versions out of order**
❌ **Inconsistent date formats**
❌ **Missing commit links**
❌ **Vague descriptions**
❌ **Mixed category naming**

---

## Summary

### Required Elements

1. Title: `# Changelog`
2. Version headers: `## [X.Y.Z] - YYYY-MM-DD`
3. Category headers: `### Category`
4. Entry format: `- **scope**: description ([hash])`

### Best Practices

- Keep entries concise and user-focused
- Use imperative mood in descriptions
- Group related changes by scope
- Provide migration guidance for breaking changes
- Link commits for reference
- Maintain chronological order (newest first)
- Follow Keep a Changelog format
