# Conventional Commits Examples

## Simple Feature

A straightforward feature addition without additional context needed.

```bash
git commit -m "feat(api): add user profile endpoint"
```

## Bug Fix with Body

A bug fix that needs explanation of what was wrong and how it was fixed.

```bash
git commit -m "$(cat <<'EOF'
fix(validation): correct email validation regex

The previous regex was rejecting valid email addresses
containing plus signs. Updated to follow RFC 5322 spec.

Fixes #456
EOF
)"
```

## Breaking Change

Changes that break backward compatibility must be clearly marked.

```bash
git commit -m "$(cat <<'EOF'
refactor(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: All v1 API endpoints have been removed.
Clients must migrate to v2 endpoints. See migration guide
at docs/v2-migration.md for details.
EOF
)"
```

## Documentation Update

```bash
git commit -m "docs: add dark mode setup instructions"
```

## Performance Improvement

```bash
git commit -m "$(cat <<'EOF'
perf(database): optimize user query with indexing

Added composite index on (user_id, created_at) which
reduced query time from 450ms to 12ms on average.
EOF
)"
```

## Refactoring

```bash
git commit -m "$(cat <<'EOF'
refactor(auth): extract JWT validation to separate module

Moved JWT validation logic from middleware to dedicated
auth/jwt module for better testability and reuse.
EOF
)"
```

## Multiple Commits from Unstaged Changes

Breaking down multiple changes into logical, atomic commits:

```bash
# First commit: Feature
git add src/components/ThemeToggle.tsx src/styles/darkMode.css
git commit -m "feat(ui): add dark mode toggle"

# Second commit: Fix
git add src/components/Button.tsx
git commit -m "fix(ui): correct button alignment in mobile view"

# Third commit: Documentation
git add README.md
git commit -m "docs: add dark mode setup instructions"

# Fourth commit: Tests
git add tests/components/ThemeToggle.test.tsx
git commit -m "test(ui): add dark mode toggle tests"
```

## Chore with Dependencies

```bash
git commit -m "$(cat <<'EOF'
chore(deps): upgrade React to v18.2.0

Updated React and React DOM to latest stable version.
All tests passing with new version.
EOF
)"
```

## Build System Change

```bash
git commit -m "build(webpack): add source map generation for production"
```

## CI/CD Configuration

```bash
git commit -m "ci: add automated deployment to staging environment"
```

## Style Changes

```bash
git commit -m "style(components): apply consistent formatting with Prettier"
```

## Test Addition

```bash
git commit -m "test(api): add integration tests for user endpoints"
```

## Multiple Related Changes with Scope

When working on a feature that touches multiple areas:

```bash
# Backend changes
git add src/api/auth/*.ts
git commit -m "feat(auth): implement OAuth2 token refresh"

# Frontend changes
git add src/components/Login.tsx src/hooks/useAuth.ts
git commit -m "feat(auth): add auto-refresh token UI handling"

# Documentation
git add docs/authentication.md
git commit -m "docs(auth): document OAuth2 refresh flow"
```

## Breaking Change with Migration Path

```bash
git commit -m "$(cat <<'EOF'
feat(config)!: change environment variable prefix from APP_ to MYAPP_

BREAKING CHANGE: All environment variables now use MYAPP_ prefix
instead of APP_. Update your .env files:
- APP_API_KEY → MYAPP_API_KEY
- APP_DATABASE_URL → MYAPP_DATABASE_URL

Migration script available at scripts/migrate-env.sh
EOF
)"
