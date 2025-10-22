# Conventional Commits Best Practices

## Commit Guidelines

### 1. Atomic Commits

Each commit should represent **one logical change**. Don't mix multiple unrelated changes in a single commit.

✅ **Good**: `feat(auth): add OAuth2 support`

❌ **Bad**: `feat(auth): add OAuth2 support and fix button styling and update README`

### 2. Clear and Consistent Scopes

Use consistent scope naming throughout the repository. Common patterns:

- Component-based: `feat(header)`, `fix(sidebar)`, `refactor(navigation)`
- Layer-based: `feat(api)`, `fix(database)`, `refactor(ui)`
- Feature-based: `feat(auth)`, `fix(payments)`, `refactor(search)`

### 3. Imperative Mood

Write commit descriptions as commands, not past tense.

✅ **Good**: `add user authentication`, `fix validation bug`, `remove deprecated code`

❌ **Bad**: `added user authentication`, `fixed validation bug`, `removed deprecated code`

### 4. Concise Descriptions

Keep the description line under **72 characters**. Put additional details in the body.

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

### 5. Meaningful Bodies

Use the commit body to explain **why**, not **what**. The diff shows what changed.

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

### 6. Document Breaking Changes

Always explicitly document breaking changes using either:

**Option 1 - Exclamation mark**:

```
feat(api)!: change authentication endpoint
```

**Option 2 - Footer**:

```
feat(api): change authentication endpoint

BREAKING CHANGE: /auth/login endpoint now requires
Content-Type: application/json header.
```

### 7. Prefer Multiple Small Commits

Break large changes into focused commits rather than one large mixed commit.

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

### 8. Review Before Committing

Always review your changes before committing:

```bash
git status          # Check what's staged
git diff --cached   # Review staged changes
git log -10 --oneline  # Check recent commit style
```

### 9. Consistent Type Usage

Use commit types consistently:

- `feat`: New features (adds functionality)
- `fix`: Bug fixes (fixes broken functionality)
- `docs`: Documentation only
- `style`: Formatting, whitespace (no code change)
- `refactor`: Code restructuring (no behavior change)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system or dependencies
- `ci`: CI/CD configuration
- `chore`: Maintenance tasks

### 10. Include Issue References

Link commits to issues in the footer when applicable:

```
fix(validation): correct email regex

Fixes #456
Closes #457
Related to #458
```

## Common Pitfalls to Avoid

### ❌ Vague Descriptions

Bad: `fix: update code`

Good: `fix(auth): prevent null pointer in token validation`

### ❌ Multiple Changes in One Commit

Bad: A commit that fixes a bug, adds a feature, and updates docs

Good: Three separate commits, each focused on one change

### ❌ Missing Scope When Beneficial

Bad: `feat: add validation` (in a large codebase)

Good: `feat(forms): add email validation`

### ❌ Not Following Repository Conventions

Always check recent commits to match the project's style:

```bash
git log -10 --oneline
```

### ❌ Forgetting to Mark Breaking Changes

Bad: Silently changing API behavior

Good: Using '!' or `BREAKING CHANGE:` footer

## Quick Reference

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Rules**:

- Description: imperative, lowercase, no period, ≤72 chars
- Body: explain "why", wrap at 72 chars
- Footer: `BREAKING CHANGE:`, issue refs, co-authors

**Common types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore

**Breaking changes**: Use '!' or `BREAKING CHANGE:` footer
