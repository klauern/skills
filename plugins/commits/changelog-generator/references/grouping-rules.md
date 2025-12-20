# Commit Grouping Rules

Rules for categorizing conventional commits into changelog sections.

## Type to Category Mapping

### Breaking Changes

**Source**: Any commit with `!` or `BREAKING CHANGE:` footer

**Category**: `### Breaking Changes`

**Always include**: Yes

**Examples**:
```text
feat(api)!: change response format
fix!: remove deprecated parameter
refactor(auth)!: replace authentication system
```

**All go to**: Breaking Changes section

---

### Features

**Source**: `feat:` commits

**Category**: `### Features`

**Include**: All `feat:` commits

**Examples**:
```text
feat(auth): add OAuth login
feat(ui): add dark mode
feat: add search functionality
```

---

### Bug Fixes

**Source**: `fix:` commits

**Category**: `### Bug Fixes`

**Include**: All `fix:` commits

**Examples**:
```text
fix(auth): resolve token validation
fix(ui): correct button alignment
fix: handle null values
```

---

### Performance

**Source**: `perf:` commits

**Category**: `### Performance`

**Include**: All `perf:` commits

**Examples**:
```text
perf(db): optimize query performance
perf(api): reduce response time
perf: improve startup speed
```

---

### Security

**Source**: `fix:` commits with security scope or keywords

**Category**: `### Security`

**Include**: Security-related fixes

**Detection**:
- Scope: `security`, `sec`
- Keywords: "security", "vulnerability", "CVE", "XSS", "SQL injection"

**Examples**:
```text
fix(security): prevent XSS in user input
fix(auth): patch authentication bypass
fix: resolve SQL injection vulnerability
```

---

### Deprecated

**Source**: Commits with deprecation notices

**Category**: `### Deprecated`

**Include**: Features marked for future removal

**Detection**:
- Footer: `Deprecated:` or `DEPRECATED:`
- Description contains "deprecate"

**Examples**:
```text
feat(api): deprecate v1 endpoints

Deprecated: v1 API endpoints will be removed in v3.0.0
```

---

### Removed

**Source**: Commits removing features

**Category**: `### Removed`

**Include**: Features that were removed

**Detection**:
- Type: Any with `!` indicating removal
- Description: "remove", "delete"
- Typically part of breaking changes

**Examples**:
```text
feat(api)!: remove deprecated v1 endpoints
chore!: remove support for Node 12
```

---

### Documentation

**Source**: `docs:` commits

**Category**: `### Documentation`

**Include**: User-facing documentation

**Exclude**: Internal docs, code comments

**Examples**:
```text
docs(api): add authentication guide
docs: update installation instructions
docs(readme): add usage examples
```

**Include when**:
- User-facing guides
- API documentation
- README updates
- Migration guides

**Exclude when**:
- JSDoc/code comments
- Internal developer docs
- Comment-only changes

---

## Conditional Inclusion

### Refactors

**Source**: `refactor:` commits

**Default**: Exclude

**Include when**:
- User-visible behavior changes
- Performance improvements (should be `perf:` instead)
- API surface changes

**Examples**:

```text
# Exclude (internal)
refactor(auth): extract validation logic
refactor: reorganize file structure

# Include (user-visible)
refactor(api): simplify endpoint structure
  - Note: Endpoint paths unchanged, but response is more consistent
```

---

### Tests

**Source**: `test:` commits

**Default**: Exclude

**Include when**: Never (not user-facing)

---

### Build/CI

**Source**: `build:`, `ci:` commits

**Default**: Exclude

**Include when**: Affects users (e.g., supported platforms)

**Examples**:

```text
# Exclude (internal)
build: update webpack config
ci: add GitHub Actions workflow

# Include (affects users)
build: add support for Node 18
build: drop support for Node 12
```

---

### Chores

**Source**: `chore:` commits

**Default**: Exclude

**Include when**:
- Dependency updates with security fixes
- License changes
- Support policy changes

**Examples**:

```text
# Exclude (internal)
chore: update dependencies
chore: clean up code

# Include (affects users)
chore: update license to MIT
chore: drop support for IE 11
```

---

### Reverts

**Source**: `revert:` commits

**Include**: Only if reverting released feature

**Format**: Explain what was reverted and why

**Examples**:

```text
# Include (reverting released feature)
revert: remove OAuth login

OAuth login has been temporarily removed due to security concerns.
Will be re-added in next release.

# Exclude (reverting unreleased)
revert: feat(ui): add dashboard
```

---

## Grouping Priority

When a commit matches multiple categories:

1. **Breaking Changes** (highest priority)
2. **Security**
3. **Deprecated**
4. **Removed**
5. **Features**
6. **Bug Fixes**
7. **Performance**
8. **Documentation**
9. **Other** (if included)

**Example**:

```text
feat(api)!: add new authentication

BREAKING CHANGE: Old auth method removed
```

**Goes to**: Breaking Changes (not Features)

---

## Scope Handling

### Preserving Scopes

Keep scopes in changelog entries:

```markdown
### Features

- **auth**: Add OAuth login
- **api**: Add rate limiting
- **ui**: Add dark mode
```

### Grouping by Scope

Optionally group within categories:

```markdown
### Features

#### Authentication

- Add OAuth login
- Add token refresh

#### API

- Add rate limiting
- Add pagination
```

### Multiple Scopes

```text
Commit: feat(auth,api): add token-based authentication

Changelog:
- **auth, api**: Add token-based authentication
```

---

## Special Cases

### Merge Commits

**Default**: Exclude

**Reason**: Content captured in individual commits

### Empty Scopes

```text
Commit: feat: add search

Changelog:
- Add search functionality
```

**No scope marker** if commit has no scope

### Long Descriptions

```text
Commit: feat(api): add comprehensive rate limiting with configurable limits per endpoint

Changelog:
- **api**: Add rate limiting with configurable limits
```

**Shorten if needed** to keep entries concise

---

## Configuration

### Custom Mappings

Projects can define custom type mappings:

```json
{
  "types": {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance",
    "custom": "Custom Changes"
  }
}
```

### Inclusion Rules

```json
{
  "include": ["feat", "fix", "perf"],
  "exclude": ["chore", "test", "ci"],
  "conditional": {
    "docs": "user-facing",
    "refactor": "if-user-impact"
  }
}
```

---

## Examples

### Example Commits → Changelog

**Commits**:
```text
1. feat(auth): add OAuth login
2. fix(auth): resolve token validation
3. perf(db): optimize queries
4. docs(api): add authentication guide
5. refactor(utils): extract helpers
6. test(auth): add login tests
7. chore: update dependencies
```

**Changelog**:
```markdown
### Features

- **auth**: Add OAuth login

### Bug Fixes

- **auth**: Resolve token validation

### Performance

- **db**: Optimize queries

### Documentation

- **api**: Add authentication guide
```

**Excluded**: refactor, test, chore (internal)

---

### Example with Breaking Changes

**Commits**:
```text
1. feat(api)!: change response format
2. feat(auth): add OAuth support
3. fix(api): handle null values
```

**Changelog**:
```markdown
### Breaking Changes

- **api**: Change response format
  - Migration: Use `response.data` instead of `response`

### Features

- **auth**: Add OAuth support

### Bug Fixes

- **api**: Handle null values
```

**Note**: `feat(api)!` goes to Breaking Changes, not Features

---

## Summary

### Always Include

- ✅ Breaking changes (any type with `!`)
- ✅ Features (`feat:`)
- ✅ Bug fixes (`fix:`)
- ✅ Performance (`perf:`)
- ✅ Security fixes

### Sometimes Include

- ⚠️ Documentation (`docs:`) - if user-facing
- ⚠️ Deprecated - if marking features for removal
- ⚠️ Removed - if removing features
- ⚠️ Build (`build:`) - if affects users

### Never Include

- ❌ Tests (`test:`)
- ❌ CI (`ci:`)
- ❌ Chores (`chore:`) - unless affects users
- ❌ Refactors (`refactor:`) - unless user-visible
- ❌ Merge commits

### Priority Order

1. Breaking Changes
2. Security
3. Deprecated
4. Removed
5. Features
6. Bug Fixes
7. Performance
8. Documentation
