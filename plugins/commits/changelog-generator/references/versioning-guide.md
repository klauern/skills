# Semantic Versioning Guide

Guide to determining version numbers from conventional commits following Semantic Versioning 2.0.0.

## Semantic Versioning Basics

### Version Format

```text
MAJOR.MINOR.PATCH

Examples:
1.0.0
2.3.1
0.1.0-alpha
```

### Version Components

**MAJOR** (X.0.0): Incompatible API changes (breaking changes)

**MINOR** (0.X.0): Backward-compatible new functionality

**PATCH** (0.0.X): Backward-compatible bug fixes

---

## Version Bump Rules

### Rule 1: Breaking Changes → MAJOR

**Trigger**: Any commit with `!` or `BREAKING CHANGE:` footer

**Bump**: Increment MAJOR, reset MINOR and PATCH to 0

**Examples**:

```text
Current: 1.2.3

Commits:
- feat(api)!: change response format

New version: 2.0.0
```

```text
Current: 0.5.2

Commits:
- fix(auth)!: remove deprecated login method

New version: 1.0.0 (or 0.6.0 if still in initial development)
```

---

### Rule 2: Features → MINOR

**Trigger**: `feat:` commits (without `!`)

**Bump**: Increment MINOR, reset PATCH to 0

**Examples**:

```text
Current: 1.2.3

Commits:
- feat(auth): add OAuth login
- feat(ui): add dark mode

New version: 1.3.0
```

---

### Rule 3: Fixes → PATCH

**Trigger**: Only `fix:`, `perf:`, or `docs:` commits

**Bump**: Increment PATCH

**Examples**:

```text
Current: 1.2.3

Commits:
- fix(auth): resolve token validation
- fix(ui): correct button alignment

New version: 1.2.4
```

---

## Decision Tree

```text
Check commits since last release
│
├─ Has breaking changes? (! or BREAKING CHANGE:)
│  └─ MAJOR bump (1.2.3 → 2.0.0)
│
├─ Has new features? (feat:)
│  └─ MINOR bump (1.2.3 → 1.3.0)
│
├─ Only fixes/perf/docs?
│  └─ PATCH bump (1.2.3 → 1.2.4)
│
└─ No user-facing changes?
   └─ No release (or PATCH if needed)
```

---

## Initial Development (0.x.x)

### Pre-1.0.0 Versioning

During initial development (before 1.0.0):

**Option A: Relaxed rules**
- Breaking changes → MINOR (0.1.0 → 0.2.0)
- Features → MINOR (0.1.0 → 0.2.0)
- Fixes → PATCH (0.1.0 → 0.1.1)

**Option B: Strict rules**
- Breaking changes → MINOR (0.1.0 → 0.2.0)
- Features → PATCH (0.1.0 → 0.1.1)
- Fixes → PATCH (0.1.0 → 0.1.1)

**Recommendation**: Use Option A (treat MINOR as unstable)

### Moving to 1.0.0

Release 1.0.0 when:
- API is stable
- Used in production
- Breaking changes will be avoided

---

## Pre-release Versions

### Format

```text
MAJOR.MINOR.PATCH-prerelease.number

Examples:
2.0.0-alpha.1
2.0.0-beta.1
2.0.0-rc.1
1.3.0-next.5
```

### Pre-release Identifiers

**alpha**: Early testing, unstable
**beta**: Feature complete, testing
**rc** (release candidate): Final testing
**next**: Upcoming version

### Pre-release Bumps

```text
Current: 1.2.3

# Start pre-release
2.0.0-alpha.1

# More alpha releases
2.0.0-alpha.2
2.0.0-alpha.3

# Move to beta
2.0.0-beta.1

# Move to RC
2.0.0-rc.1

# Final release
2.0.0
```

---

## Examples

### Example 1: Features and Fixes

**Current**: 1.2.3

**Commits**:
```text
feat(auth): add OAuth login
feat(ui): add dark mode
fix(api): resolve timeout
docs: update README
```

**Analysis**:
- Breaking changes? No
- Features? Yes (2 feat commits)
- Only fixes? No (has features)

**New version**: 1.3.0 (MINOR bump)

---

### Example 2: Only Fixes

**Current**: 1.2.3

**Commits**:
```text
fix(auth): resolve token validation
fix(ui): correct button alignment
perf(db): optimize queries
docs(api): update examples
```

**Analysis**:
- Breaking changes? No
- Features? No
- Only fixes/perf/docs? Yes

**New version**: 1.2.4 (PATCH bump)

---

### Example 3: Breaking Change

**Current**: 1.2.3

**Commits**:
```text
feat(api)!: change response format

BREAKING CHANGE: Response now uses nested structure

feat(auth): add OAuth support
fix(ui): resolve layout issue
```

**Analysis**:
- Breaking changes? Yes (api change)
- Features? Yes (but overridden by breaking)
- Fixes? Yes (but overridden by breaking)

**New version**: 2.0.0 (MAJOR bump)

---

### Example 4: Initial Development

**Current**: 0.3.2

**Commits**:
```text
feat(auth)!: change authentication flow
feat(api): add new endpoints
fix(ui): resolve crash
```

**Analysis**:
- Breaking changes? Yes
- In 0.x? Yes (initial development)

**New version**: 0.4.0 (MINOR bump, not MAJOR during 0.x)

---

### Example 5: Pre-release

**Current**: 1.2.3

**Commits** (for next major version):
```text
feat(api)!: change response format
```

**Pre-release flow**:
```text
1.2.3 → 2.0.0-alpha.1 → 2.0.0-alpha.2 → 2.0.0-beta.1 → 2.0.0-rc.1 → 2.0.0
```

---

## Special Cases

### No User-Facing Changes

**Commits**:
```text
chore: update dependencies
ci: add workflow
refactor: extract helpers
test: add unit tests
```

**Decision**: No release (or PATCH if needed for other reasons)

---

### Multiple Breaking Changes

**Commits**:
```text
feat(api)!: change authentication
feat(db)!: change schema
fix(ui)!: remove deprecated component
```

**Analysis**: Multiple breaking changes

**New version**: Still just one MAJOR bump (1.2.3 → 2.0.0)

---

### Mixed with Breaking

**Commits**:
```text
feat(api)!: breaking change
feat(ui): new feature
fix(auth): bug fix
```

**Analysis**: Breaking change present

**New version**: MAJOR bump (overrides feat and fix)

**Changelog**: Lists all under appropriate sections

---

## Version Strategies

### Conservative (Default)

- Wait for multiple changes
- Bundle fixes into releases
- Release on schedule (weekly, monthly)

**Example**:
```text
Week 1: 5 fixes → 1.2.4
Week 2: 3 features → 1.3.0
Week 3: 1 breaking → 2.0.0
```

### Aggressive

- Release every change
- Immediate fixes
- Continuous deployment

**Example**:
```text
fix: bug → 1.2.4
fix: another bug → 1.2.5
feat: feature → 1.3.0
```

### Scheduled

- Release on fixed schedule
- Bundle all changes
- Predictable cadence

**Example**:
```text
Monthly: All changes → calculate version
```

---

## Automation

### Calculating Next Version

```bash
# Get commits since last tag
commits=$(git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%s|%b")

# Check for breaking changes
if echo "$commits" | grep -qE '(^[^:]+!:|BREAKING CHANGE:)'; then
  # MAJOR bump
  next_version="2.0.0"
elif echo "$commits" | grep -q "^feat"; then
  # MINOR bump
  next_version="1.3.0"
else
  # PATCH bump
  next_version="1.2.4"
fi
```

### Semantic Release Tools

**semantic-release**: Automates versioning and changelog

**standard-version**: Manual versioning with automation

**conventional-changelog**: Just changelog generation

---

## Best Practices

### 1. Be Consistent

Choose a strategy and stick to it:
- Conservative, aggressive, or scheduled
- Pre-releases for majors or all
- Initial development handling

### 2. Communicate Breaking Changes

Always include migration guide:
```markdown
### Breaking Changes

- **api**: Change response format
  - Migration: Update client code to use `data.items`
  - See migration guide: docs/migration-v2.md
```

### 3. Don't Skip Versions

```text
❌ Don't: 1.2.3 → 1.5.0
✅ Do: 1.2.3 → 1.3.0 → 1.4.0 → 1.5.0
```

### 4. Tag Releases

```bash
git tag -a v1.3.0 -m "Release version 1.3.0"
git push --tags
```

### 5. Document Version Policy

In README or CONTRIBUTING:
```markdown
## Versioning

This project follows [Semantic Versioning](https://semver.org/).

- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

Pre-1.0.0: MINOR may include breaking changes
```

---

## Common Questions

### Q: What if I have both feat and fix?

**A**: MINOR bump (features take precedence over fixes)

### Q: What about refactors that change behavior?

**A**: If user-visible, should be `feat:` or `feat!:`, not `refactor:`

### Q: Can I have breaking changes in a PATCH?

**A**: No. Breaking changes always require MAJOR (or MINOR in 0.x)

### Q: What version for first release?

**A**: Start with 0.1.0 (initial development) or 1.0.0 (stable)

### Q: When should I use 1.0.0?

**A**: When API is stable and used in production

---

## Summary

### Quick Reference

| Commits | Current | Next | Bump |
|---------|---------|------|------|
| Breaking only | 1.2.3 | 2.0.0 | MAJOR |
| Breaking + feat | 1.2.3 | 2.0.0 | MAJOR |
| feat only | 1.2.3 | 1.3.0 | MINOR |
| feat + fix | 1.2.3 | 1.3.0 | MINOR |
| fix only | 1.2.3 | 1.2.4 | PATCH |
| perf only | 1.2.3 | 1.2.4 | PATCH |
| docs only | 1.2.3 | 1.2.4 | PATCH |
| Internal only | 1.2.3 | 1.2.3 | None |

### Decision Algorithm

1. Has `!` or `BREAKING CHANGE:`? → **MAJOR**
2. Has `feat:`? → **MINOR**
3. Has `fix:`, `perf:`, or `docs:`? → **PATCH**
4. Only internal (`test:`, `ci:`, `chore:`)? → **No release**

### Version Lifecycle

```text
0.1.0 → ... → 0.9.0 → 1.0.0 → 1.1.0 → 1.2.0 → 2.0.0-alpha.1 → 2.0.0
 ↑              ↑        ↑       ↑       ↑            ↑          ↑
Initial    Pre-1.0   Stable  Feature  More    Pre-release   Major
development         release           features              release
```
