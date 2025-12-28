# Conventional Commits Best Practices

Actionable guidelines for creating high-quality conventional commits.

## Core Principles

### 1. Atomic Commits

Each commit = **one logical change**. Don't mix unrelated changes.

✅ **Good**: `feat(auth): add OAuth2 support`
❌ **Bad**: `feat(auth): add OAuth2 support and fix button styling and update README`

### 2. Imperative Mood

Write as commands, not past tense.

✅ **Good**: `add user authentication`, `fix validation bug`, `remove deprecated code`
❌ **Bad**: `added user authentication`, `fixed validation bug`, `removed deprecated code`

### 3. Concise Descriptions

≤72 characters. Put details in body.

✅ **Good**:
```
feat(auth): add OAuth2 support

Implemented OAuth2 authentication flow with support for
Google and GitHub providers. Includes token refresh logic.
```

❌ **Bad**:
```
feat(auth): add OAuth2 support with Google and GitHub providers and token refresh
```

### 4. Meaningful Bodies

Explain **why**, not **what** (diff shows what).

✅ **Good**:
```
refactor(database): switch to connection pooling

Previous implementation created new connections for each
query, causing performance issues under load. Connection
pooling reduces overhead and improves response times.
```

❌ **Bad**:
```
refactor(database): switch to connection pooling

Changed the database connection code to use a pool.
Updated all query functions to use the pool.
```

### 5. Multiple Small Commits

Better than one large mixed commit.

✅ **Good**:
```
1. feat(ui): add dark mode toggle component
2. feat(ui): implement dark mode styles
3. feat(ui): add dark mode preference persistence
4. docs: add dark mode usage guide
```

❌ **Bad**:
```
1. feat(ui): add complete dark mode feature with docs
```

## Scope Naming Conventions

Use **consistent scope names** throughout repository:

- **Component-based**: `feat(header)`, `fix(sidebar)`, `refactor(navigation)`
- **Layer-based**: `feat(api)`, `fix(database)`, `refactor(ui)`
- **Feature-based**: `feat(auth)`, `fix(payments)`, `refactor(search)`

**Check existing conventions**:
```bash
git log -10 --oneline  # Match project style
```

## Breaking Changes

Always explicitly document breaking changes.

**Option 1 - Exclamation**:
```
feat(api)!: change authentication endpoint
```

**Option 2 - Footer**:
```
feat(api): change authentication endpoint

BREAKING CHANGE: /auth/login endpoint now requires
Content-Type: application/json header.
```

## Pre-Commit Checklist

Before committing:

```bash
git status           # Check what's staged
git diff --cached    # Review staged changes
git log -10 --oneline  # Check recent commit style
```

## Type Selection Guide

- **`feat`**: New features (adds functionality)
- **`fix`**: Bug fixes (fixes broken functionality)
- **`docs`**: Documentation only
- **`style`**: Formatting, whitespace (no code change)
- **`refactor`**: Code restructuring (no behavior change)
- **`perf`**: Performance improvements
- **`test`**: Adding or updating tests
- **`build`**: Build system or dependencies
- **`ci`**: CI/CD configuration
- **`chore`**: Maintenance tasks

## Issue References

Link commits to issues in footer:

```
fix(validation): correct email regex

Fixes #456
Closes #457
Related to #458
```

## Common Pitfalls

### ❌ Vague Descriptions

Bad: `fix: update code`
Good: `fix(auth): prevent null pointer in token validation`

### ❌ Multiple Changes

Bad: One commit fixing bug + adding feature + updating docs
Good: Three separate focused commits

### ❌ Missing Useful Scope

Bad: `feat: add validation` (in large codebase)
Good: `feat(forms): add email validation`

### ❌ Ignoring Repository Conventions

Bad: Using inconsistent scope names
Good: Check `git log -10 --oneline` and match existing style

### ❌ Silent Breaking Changes

Bad: Changing API behavior without marking it
Good: Use '!' or `BREAKING CHANGE:` footer
