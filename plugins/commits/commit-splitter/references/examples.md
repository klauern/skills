# Commit Split Examples

## Example 1: Feature with Tests and Docs

### Before (one large diff)

```
Changes:
  src/auth/login.ts      | +150 lines
  src/auth/types.ts      |  +30 lines
  tests/auth/login.test.ts | +200 lines
  docs/api/auth.md       |  +50 lines
```

### After (three atomic commits)

```bash
# Commit 1: Core feature
git add src/auth/login.ts src/auth/types.ts
git commit -m "$(cat <<'EOF'
feat(auth): add user login endpoint

Implements POST /api/auth/login with JWT token response.
Includes password hashing and rate limiting.
EOF
)"

# Commit 2: Tests
git add tests/auth/login.test.ts
git commit -m "$(cat <<'EOF'
test(auth): add login endpoint tests

Covers success, invalid credentials, and rate limit scenarios.
EOF
)"

# Commit 3: Documentation
git add docs/api/auth.md
git commit -m "$(cat <<'EOF'
docs(auth): document login API

Includes request/response examples and error codes.
EOF
)"
```

## Example 2: Multiple Bug Fixes

### Before

```
Changes:
  src/utils/date.ts      | 5 lines changed (fix timezone)
  src/utils/string.ts    | 3 lines changed (fix encoding)
  src/api/handler.ts     | 10 lines changed (fix null check)
```

### After

```bash
# Commit 1
git add src/utils/date.ts
git commit -m "fix(utils): correct timezone offset calculation"

# Commit 2
git add src/utils/string.ts
git commit -m "fix(utils): handle UTF-8 encoding in string helper"

# Commit 3
git add src/api/handler.ts
git commit -m "fix(api): add null check before accessing user property"
```

## Example 3: Refactor + Feature

### Before

```
Changes:
  src/database/client.ts    | Refactored connection pooling
  src/database/query.ts     | New query builder feature
  src/database/types.ts     | Types for both changes
```

### After

```bash
# Commit 1: Refactor first (foundation)
git add -p src/database/client.ts  # Select refactor hunks
git add -p src/database/types.ts   # Select related types
git commit -m "$(cat <<'EOF'
refactor(database): extract connection pool management

Moves pool logic to dedicated methods for better testability.
EOF
)"

# Commit 2: Feature (builds on refactor)
git add src/database/query.ts
git add src/database/client.ts  # Remaining changes
git add src/database/types.ts   # Remaining types
git commit -m "$(cat <<'EOF'
feat(database): add fluent query builder

Provides chainable API for constructing SQL queries.
EOF
)"
```

## Example 4: Config + Code Changes

### Before

```
Changes:
  tsconfig.json           | Added strict mode
  src/types/index.ts      | Type fixes for strict mode
  src/utils/helper.ts     | Type fixes for strict mode
  package.json            | Updated dev dependency
```

### After

```bash
# Commit 1: Dependencies
git add package.json
git commit -m "chore(deps): update typescript to 5.3"

# Commit 2: Config
git add tsconfig.json
git commit -m "chore(typescript): enable strict mode"

# Commit 3: Code fixes
git add src/types/index.ts src/utils/helper.ts
git commit -m "fix(types): resolve strict mode type errors"
```

## Example 5: Cross-Cutting Feature

### Before

```
Changes across multiple modules for "dark mode" feature:
  src/theme/colors.ts
  src/theme/context.tsx
  src/components/Header.tsx
  src/components/Sidebar.tsx
  src/hooks/useTheme.ts
  tests/theme/context.test.tsx
```

### After

```bash
# Commit 1: Core theme infrastructure
git add src/theme/colors.ts src/theme/context.tsx src/hooks/useTheme.ts
git commit -m "$(cat <<'EOF'
feat(theme): add dark mode support

Introduces ThemeContext and useTheme hook for theme switching.
Defines color palettes for light and dark modes.
EOF
)"

# Commit 2: Component updates
git add src/components/Header.tsx src/components/Sidebar.tsx
git commit -m "feat(components): integrate dark mode theming"

# Commit 3: Tests
git add tests/theme/context.test.tsx
git commit -m "test(theme): add ThemeContext tests"
```

## Split Decision Guide

| Situation | Recommended Split |
|-----------|------------------|
| Feature + tests | 2 commits: feat, then test |
| Feature + docs | 2 commits: feat, then docs |
| Multiple unrelated fixes | 1 commit per fix |
| Refactor enabling feature | 2 commits: refactor, then feat |
| Breaking change | Include in feature commit with `!` |
| Config + code using it | 2 commits: config, then code |
| Types + implementation | Usually 1 commit (types are part of feat) |
| Lint/format fixes | Separate commit: `style(scope): ...` |
