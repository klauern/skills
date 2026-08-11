---
name: dependency-upgrader
description: This skill should be used when the user asks to "check for outdated dependencies", "upgrade npm/poetry/go/cargo packages", "review breaking dependency updates", or "plan dependency migrations".
version: 1.0.0
author: klauern
allowed-tools: Bash Read Grep Glob Edit Write
---

# Dependency Upgrader

Automates upgrading package dependencies: detects outdated versions, identifies breaking changes, and prepares upgrade commits (PR creation stays with the pull-requests plugin).

## Quick Start

```
User: Check for outdated dependencies
User: Upgrade my npm packages
User: What packages need updating?
```

The skill will: detect ecosystem(s) → analyze outdated → categorize by semver → plan upgrades → execute with approval

## Workflow

1. **Detect**: Find manifest files (package.json, pyproject.toml, go.mod, Cargo.toml)
2. **Analyze**: Run ecosystem-specific outdated commands
3. **Categorize**: Group updates by patch/minor/major
4. **Plan**: Generate upgrade strategy with breaking change notes
5. **Execute**: Update manifest files (prompt for majors)
6. **Verify**: Run lock file update, optionally test

## Ecosystem Detection

| Ecosystem | Manifest | Check Outdated | Update |
|-----------|----------|----------------|--------|
| npm | package.json | `npx ncu` or `npm outdated` | `npx ncu -u` |
| poetry | pyproject.toml | `poetry show --outdated` | `poetry update` |
| go | go.mod | `go list -m -u all` | `go get -u ./...` |
| cargo | Cargo.toml | `cargo outdated` | `cargo update` |

Full per-ecosystem command references (flags, lock operations, constraint syntax) live
in [ecosystems.md](references/ecosystems.md) — the table above is the quick index.

## Decision Points

Prompt user for:

1. **Major versions**: "Apply major version upgrades?" (Apply all / Skip majors / Review each)
2. **Multiple ecosystems**: "Found npm and poetry. Upgrade both?" (All / Select)
3. **Breaking changes**: "Package X has breaking changes. Proceed?" (Yes / Skip / Show changelog)

## Breaking Change Detection

| Method | Source | Reliability |
|--------|--------|-------------|
| Semver major bump | Version comparison | High |
| CHANGELOG.md | Local file or GitHub | Medium |
| Release notes | `gh api repos/{owner}/{repo}/releases` | Medium |
| npm deprecation | `npm view <pkg> deprecated` | High |

**Strategy**: Flag major bumps → fetch changelog/releases for context → present to user

See [breaking-changes.md](references/breaking-changes.md) for detection methods.

## Git Operations

**Branch**: `chore/upgrade-{ecosystem}-deps-{date}` or `chore/upgrade-dependencies-{date}`

**Commit format**:
```
chore(deps): upgrade {ecosystem} dependencies

- package-a: 1.0.0 → 2.0.0 (major)
- package-b: 2.1.0 → 2.2.0 (minor)

Breaking changes:
- package-a: API change in foo() method
```

## Requirements

- `ncu` (npm-check-updates) for npm - optional but preferred
- `cargo-outdated` for Rust - optional
- `gh` CLI for changelog fetching

## Error Handling

| Issue | Solution |
|-------|----------|
| No manifest found | Report and exit gracefully |
| Tool not installed | Suggest installation, use fallback |
| Network error | Report, suggest retry |
| Lock file conflict | Guide through resolution |

## Configuration (Optional)

```yaml
# .dependency-upgrade-config.yml
excluded:
  - pinned-package@1.0.0
ecosystems:
  - npm
  - poetry
```

## References

- [ecosystems.md](references/ecosystems.md) - Detailed ecosystem commands
- [breaking-changes.md](references/breaking-changes.md) - Breaking change detection
- [examples.md](references/examples.md) - Real-world upgrade scenarios
