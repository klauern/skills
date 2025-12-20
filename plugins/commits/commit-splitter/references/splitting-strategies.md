# Commit Splitting Strategies

This guide explains different strategies for identifying logical commit boundaries in large changesets.

## Core Principles

### Atomic Commits

Each commit should:
- Represent a single logical change
- Build and pass tests independently
- Have a clear, singular purpose
- Be reviewable in isolation

### Commit Dependencies

Maintain proper ordering:
- Foundation changes before features that use them
- Refactors before new code that depends on them
- Type definitions before implementations that use them

## Splitting Strategies

### 1. File-Based Splitting

**When to use**: Changes span multiple unrelated files

**Strategy**: Group by file purpose

```text
Example: API endpoint + tests + docs

Split into:
1. feat(api): add user endpoint
   - src/api/users.ts

2. test(api): add user endpoint tests
   - tests/api/users.test.ts

3. docs(api): document user endpoint
   - docs/api.md
```

### 2. Concern-Based Splitting

**When to use**: Mixed refactors, features, and fixes

**Strategy**: Separate by commit type

```text
Example: Refactor + new feature using refactored code

Split into:
1. refactor(auth): extract validation logic
   - src/auth/validator.ts (extracted)
   - src/auth/login.ts (uses validator)

2. feat(auth): add password strength validation
   - src/auth/validator.ts (new strength check)
   - tests/auth/validator.test.ts
```

**Order matters**: Refactor first, then feature

### 3. Scope-Based Splitting

**When to use**: Changes affect multiple components/modules

**Strategy**: Group by component scope

```text
Example: Same feature across components

Split into:
1. feat(auth): add login rate limiting
   - src/auth/limiter.ts
   - src/auth/middleware.ts

2. feat(api): add rate limiting to endpoints
   - src/api/users.ts
   - src/api/posts.ts

3. test: add rate limiting tests
   - tests/auth/limiter.test.ts
   - tests/api/rate-limit.test.ts
```

### 4. Dependency-Based Splitting

**When to use**: Changes have clear dependencies

**Strategy**: Order by dependency chain

```text
Example: Type changes + implementation + usage

Split into:
1. refactor(types): add user role types
   - src/types/user.ts

2. feat(auth): implement role-based access
   - src/auth/roles.ts (uses types)

3. feat(api): add role checks to endpoints
   - src/api/middleware.ts (uses roles)

4. test(auth): add role tests
   - tests/auth/roles.test.ts
```

### 5. Mixed Strategy

**When to use**: Complex changes need multiple strategies

**Strategy**: Combine file, concern, and scope splitting

```text
Example: Large feature with refactors

Split into:
1. refactor(core): extract common utils
   - src/utils/helpers.ts

2. feat(user): add profile editing
   - src/user/profile.ts
   - src/user/types.ts

3. feat(api): add profile update endpoint
   - src/api/profile.ts

4. test(user): add profile tests
   - tests/user/profile.test.ts

5. test(api): add profile API tests
   - tests/api/profile.test.ts

6. docs: document profile editing
   - docs/user-guide.md
```

## Anti-Patterns

### Over-Splitting

❌ **Too granular**:
```text
1. Add import statement
2. Add type definition
3. Add function signature
4. Add function body
5. Add export statement
```

✅ **Right granularity**:
```text
1. feat(utils): add validation helper
   - src/utils/validation.ts (complete implementation)
```

### Under-Splitting

❌ **Too coarse**:
```text
1. Implement feature
   - 50 files changed
   - Tests + docs + feature + refactor all together
```

✅ **Right granularity**:
```text
1. refactor: extract common code
2. feat: implement core feature
3. test: add feature tests
4. docs: document new feature
```

### Breaking Dependencies

❌ **Wrong order**:
```text
1. feat(api): use new validator (validator doesn't exist yet)
2. feat(auth): add validator
```

✅ **Right order**:
```text
1. feat(auth): add validator
2. feat(api): use new validator
```

## Decision Tree

Use this tree to decide how to split:

```text
Large staged changes
├── Multiple concerns? (feat + refactor + fix)
│   └── Split by concern (refactor first, then features)
├── Multiple components?
│   └── Split by scope (one commit per component)
├── Tests + implementation?
│   └── Split by type (implementation first, then tests)
├── Docs + code?
│   └── Split by type (code first, then docs)
└── Single concern, single component?
    └── Don't split (atomic already)
```

## Examples by Scenario

### Scenario 1: New Feature with Tests

```bash
# Staged files:
# - src/feature.ts
# - tests/feature.test.ts
# - docs/feature.md

Split into:
1. feat(core): add new feature
2. test(core): add feature tests
3. docs(core): document new feature
```

### Scenario 2: Refactor + New Code

```bash
# Staged files:
# - src/old-code.ts (refactored)
# - src/new-feature.ts (uses refactored code)

Split into:
1. refactor(core): extract helper functions
2. feat(core): add feature using helpers
```

### Scenario 3: Multi-Component Feature

```bash
# Staged files:
# - src/auth/roles.ts
# - src/api/middleware.ts
# - src/user/permissions.ts

Split into:
1. feat(auth): add role definitions
2. feat(api): add role middleware
3. feat(user): add permission checks
```

### Scenario 4: Bug Fix + Prevention

```bash
# Staged files:
# - src/buggy-code.ts (fix)
# - tests/regression.test.ts (prevent regression)

Split into:
1. fix(core): resolve null pointer error
2. test(core): add regression test
```

## Tools for Analysis

### Analyzing Diffs

```bash
# See overall changes
git diff --staged --stat

# See detailed changes by file
git diff --staged

# See changes by function (useful for splitting)
git diff --staged --function-context
```

### Staging Partial Changes

```bash
# Stage specific files
git add file1.ts file2.ts

# Stage specific hunks interactively
git add -p file.ts

# Stage specific lines
git add -e file.ts
```

## Summary

**Good splits have**:
- Clear, single purpose
- Logical grouping
- Proper dependencies
- Independent builds
- Focused reviews

**Choose strategy based on**:
- Number of files
- Types of changes
- Component boundaries
- Dependencies
- Review goals
