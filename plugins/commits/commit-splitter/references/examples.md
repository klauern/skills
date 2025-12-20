# Commit Splitting Examples

Real-world examples of splitting large changesets into atomic commits.

## Example 1: New Feature with Tests and Docs

### Initial State

```bash
$ git diff --staged --stat
 src/auth/login.ts          | 45 +++++++++++++++++++
 src/auth/types.ts          | 12 +++++
 tests/auth/login.test.ts   | 67 ++++++++++++++++++++++++++
 docs/authentication.md     | 23 +++++++++
 4 files changed, 147 insertions(+)
```

### Analysis

Changes span multiple concerns:
- Implementation (login.ts, types.ts)
- Tests (login.test.ts)
- Documentation (authentication.md)

### Suggested Splits

```text
Commit #1: feat(auth): add OAuth login support
Files:
  - src/auth/login.ts (new OAuth flow)
  - src/auth/types.ts (OAuth types)

Commit #2: test(auth): add OAuth login tests
Files:
  - tests/auth/login.test.ts (OAuth test suite)

Commit #3: docs(auth): document OAuth login
Files:
  - docs/authentication.md (OAuth setup guide)
```

### Execution

```bash
# Commit 1: Implementation
git reset
git add src/auth/login.ts src/auth/types.ts
git commit -m "$(cat <<'EOF'
feat(auth): add OAuth login support

Implement OAuth 2.0 authentication flow with support for
Google and GitHub providers. Includes token validation
and refresh logic.
EOF
)"

# Commit 2: Tests
git add tests/auth/login.test.ts
git commit -m "$(cat <<'EOF'
test(auth): add OAuth login tests

Add comprehensive test suite for OAuth flow including:
- Token exchange
- Provider validation
- Error handling
EOF
)"

# Commit 3: Documentation
git add docs/authentication.md
git commit -m "$(cat <<'EOF'
docs(auth): document OAuth login

Add setup guide for OAuth providers with configuration
examples and troubleshooting steps.
EOF
)"
```

## Example 2: Refactor + New Feature

### Initial State

```bash
$ git diff --staged --stat
 src/utils/validation.ts    | 34 ++++++++++++++++++
 src/auth/register.ts       | 28 ++++++---------
 src/auth/password.ts       | 56 +++++++++++++++++++++++++++
 tests/utils/validation.test.ts | 45 ++++++++++++++++++++++
 4 files changed, 147 insertions(+), 16 deletions(-)
```

### Analysis

- Refactor: Extract validation logic to utils (validation.ts, register.ts changes)
- New feature: Password strength checking (password.ts)
- Tests for new utils

**Dependency**: Password strength uses extracted validators

### Suggested Splits

```text
Commit #1: refactor(auth): extract common validation logic
Files:
  - src/utils/validation.ts (new validators)
  - src/auth/register.ts (use extracted validators)

Commit #2: feat(auth): add password strength validation
Files:
  - src/auth/password.ts (strength checker using validators)

Commit #3: test(utils): add validation tests
Files:
  - tests/utils/validation.test.ts (validator tests)
```

### Execution

```bash
# Commit 1: Refactor
git reset
git add src/utils/validation.ts src/auth/register.ts
git commit -m "$(cat <<'EOF'
refactor(auth): extract common validation logic

Extract email and username validators to shared utils
for reuse across auth modules.
EOF
)"

# Commit 2: New feature
git add src/auth/password.ts
git commit -m "$(cat <<'EOF'
feat(auth): add password strength validation

Implement password strength checker with configurable
rules for length, complexity, and common password detection.
EOF
)"

# Commit 3: Tests
git add tests/utils/validation.test.ts
git commit -m "$(cat <<'EOF'
test(utils): add validation tests

Add test suite for email, username, and password validators
including edge cases and error scenarios.
EOF
)"
```

## Example 3: Multi-Component Feature

### Initial State

```bash
$ git diff --staged --stat
 src/api/rate-limit.ts          | 42 ++++++++++++++++++++
 src/api/middleware.ts          | 18 +++++++++
 src/api/users.ts               | 5 +++
 src/api/posts.ts               | 5 +++
 src/cache/redis.ts             | 28 +++++++++++++
 tests/api/rate-limit.test.ts   | 67 ++++++++++++++++++++++++++++++
 6 files changed, 165 insertions(+)
```

### Analysis

Rate limiting feature spans multiple scopes:
- Core rate limiter (rate-limit.ts)
- Middleware integration (middleware.ts)
- Application to endpoints (users.ts, posts.ts)
- Cache backend (redis.ts)
- Tests

### Suggested Splits

```text
Commit #1: feat(cache): add Redis rate limit storage
Files:
  - src/cache/redis.ts (Redis counter implementation)

Commit #2: feat(api): add rate limiting middleware
Files:
  - src/api/rate-limit.ts (rate limiter logic)
  - src/api/middleware.ts (middleware integration)

Commit #3: feat(api): apply rate limits to endpoints
Files:
  - src/api/users.ts (rate limit users endpoint)
  - src/api/posts.ts (rate limit posts endpoint)

Commit #4: test(api): add rate limiting tests
Files:
  - tests/api/rate-limit.test.ts (comprehensive tests)
```

### Execution

```bash
# Commit 1: Cache backend
git reset
git add src/cache/redis.ts
git commit -m "$(cat <<'EOF'
feat(cache): add Redis rate limit storage

Implement Redis-backed counter for distributed rate limiting
with automatic expiration.
EOF
)"

# Commit 2: Core middleware
git add src/api/rate-limit.ts src/api/middleware.ts
git commit -m "$(cat <<'EOF'
feat(api): add rate limiting middleware

Add configurable rate limiting middleware with per-endpoint
limits and Redis-backed storage.
EOF
)"

# Commit 3: Apply to endpoints
git add src/api/users.ts src/api/posts.ts
git commit -m "$(cat <<'EOF'
feat(api): apply rate limits to endpoints

Add rate limiting to users and posts endpoints:
- 100 req/min for authenticated users
- 20 req/min for unauthenticated
EOF
)"

# Commit 4: Tests
git add tests/api/rate-limit.test.ts
git commit -m "$(cat <<'EOF'
test(api): add rate limiting tests

Add comprehensive rate limit tests including:
- Limit enforcement
- Redis integration
- Multiple concurrent requests
EOF
)"
```

## Example 4: Bug Fix with Prevention

### Initial State

```bash
$ git diff --staged --stat
 src/data/parser.ts              | 8 +++---
 tests/data/parser.test.ts       | 34 +++++++++++++++++++++
 tests/regression/parser-null.ts | 12 ++++++++
 3 files changed, 50 insertions(+), 4 deletions(-)
```

### Analysis

- Bug fix in parser
- Unit tests for the fix
- Regression test to prevent recurrence

### Suggested Splits

```text
Commit #1: fix(data): handle null values in parser
Files:
  - src/data/parser.ts (add null checks)

Commit #2: test(data): add parser edge case tests
Files:
  - tests/data/parser.test.ts (null handling tests)
  - tests/regression/parser-null.ts (regression test)
```

### Execution

```bash
# Commit 1: Fix
git reset
git add src/data/parser.ts
git commit -m "$(cat <<'EOF'
fix(data): handle null values in parser

Add null checks to prevent TypeError when parsing
incomplete data objects. Fixes #1234.
EOF
)"

# Commit 2: Tests
git add tests/data/parser.test.ts tests/regression/parser-null.ts
git commit -m "$(cat <<'EOF'
test(data): add parser edge case tests

Add tests for null value handling and regression test
to prevent future null pointer errors.
EOF
)"
```

## Example 5: Breaking Change with Migration

### Initial State

```bash
$ git diff --staged --stat
 src/api/v2/users.ts         | 78 +++++++++++++++++++++++++++++
 src/api/v1/users.ts         | 3 ++
 src/migration/api-v2.ts     | 45 +++++++++++++++++
 docs/migration-guide.md     | 67 +++++++++++++++++++++++++
 docs/api-v2.md              | 123 +++++++++++++++++++++++++++++++++++++++++++
 5 files changed, 316 insertions(+)
```

### Analysis

API v2 with breaking changes:
- New v2 implementation
- Deprecation notice in v1
- Migration script
- Documentation

### Suggested Splits

```text
Commit #1: feat(api)!: add v2 users endpoint

BREAKING CHANGE: New v2 API with different response format
Files:
  - src/api/v2/users.ts (new v2 implementation)

Commit #2: docs(api): add v2 API documentation
Files:
  - docs/api-v2.md (API reference)

Commit #3: chore(api): deprecate v1 users endpoint
Files:
  - src/api/v1/users.ts (deprecation warning)

Commit #4: feat(migration): add v1 to v2 migration script
Files:
  - src/migration/api-v2.ts (migration helper)
  - docs/migration-guide.md (migration guide)
```

### Execution

```bash
# Commit 1: Breaking change
git reset
git add src/api/v2/users.ts
git commit -m "$(cat <<'EOF'
feat(api)!: add v2 users endpoint

Implement new v2 users endpoint with improved response format
and better error handling.

BREAKING CHANGE: Response format changed from flat object to
nested structure with metadata. See migration guide.
EOF
)"

# Commit 2: API docs
git add docs/api-v2.md
git commit -m "$(cat <<'EOF'
docs(api): add v2 API documentation

Add complete API reference for v2 endpoints including
request/response formats and examples.
EOF
)"

# Commit 3: Deprecation
git add src/api/v1/users.ts
git commit -m "$(cat <<'EOF'
chore(api): deprecate v1 users endpoint

Add deprecation warning to v1 endpoint. Will be removed
in version 3.0.0.
EOF
)"

# Commit 4: Migration
git add src/migration/api-v2.ts docs/migration-guide.md
git commit -m "$(cat <<'EOF'
feat(migration): add v1 to v2 migration script

Add migration script and guide for upgrading from v1 to v2 API.
Includes automated data transformation and validation.
EOF
)"
```

## Example 6: Configuration + Implementation

### Initial State

```bash
$ git diff --staged --stat
 .eslintrc.json              | 5 +++++
 src/utils/validation.ts     | 23 +++++++++------------
 src/api/handlers.ts         | 34 +++++++++++++++---------------
 package.json                | 1 +
 4 files changed, 34 insertions(+), 29 deletions(-)
```

### Analysis

- Linting rule changes
- Code reformatted to comply
- New dependency

### Suggested Splits

```text
Commit #1: build: add stricter linting rules
Files:
  - .eslintrc.json (new rules)
  - package.json (eslint plugin)

Commit #2: style: apply new linting rules
Files:
  - src/utils/validation.ts (reformatted)
  - src/api/handlers.ts (reformatted)
```

### Execution

```bash
# Commit 1: Configuration
git reset
git add .eslintrc.json package.json
git commit -m "$(cat <<'EOF'
build: add stricter linting rules

Enable additional ESLint rules for better code quality:
- no-unused-vars
- prefer-const
- arrow-body-style
EOF
)"

# Commit 2: Apply rules
git add src/
git commit -m "$(cat <<'EOF'
style: apply new linting rules

Reformat code to comply with updated ESLint configuration.
No functional changes.
EOF
)"
```

## Summary

### Common Patterns

1. **Separate concerns**: Implementation → Tests → Docs
2. **Order dependencies**: Foundation → Features → Tests
3. **Group by scope**: Component A → Component B → Integration
4. **Isolate changes**: Refactor → New code → Configuration

### Key Takeaways

- Each commit should build successfully
- Keep related changes together
- Maintain logical dependencies
- Make review easier with focused commits
- Tell a story with commit sequence
