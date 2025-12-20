# Commit Splitting Best Practices

Guidelines for creating effective atomic commits through intelligent splitting.

## Core Principles

### 1. Atomic Commits

**Definition**: Each commit represents exactly one logical change.

**Benefits**:
- Easier code review
- Simpler git bisect for bug hunting
- Cleaner git history
- Better changelog generation
- Safer reverts

**Test**: Can you describe the commit in one sentence without using "and"?

```text
✅ Good: "Add user authentication middleware"
❌ Bad: "Add authentication and fix validation bug and update docs"
```

### 2. Build Independence

**Rule**: Each commit should build and pass tests independently.

**Why**: Enables git bisect, makes reverts safe, allows cherry-picking.

**Test**: Can you checkout this commit and run the test suite successfully?

```bash
# Test a commit
git checkout <commit-hash>
npm test  # Should pass
npm run build  # Should succeed
```

### 3. Logical Ordering

**Rule**: Commits should be ordered by dependency.

**Pattern**:
1. Type definitions / Interfaces
2. Implementations / Refactors
3. Features using above
4. Tests
5. Documentation

**Why**: Each commit builds on previous commits without breaking.

## When to Split

### Split When...

#### Multiple Concerns
```text
Staged changes contain:
- Bug fix + new feature
- Refactor + feature
- Multiple unrelated features
```

#### Multiple Components
```text
Changes affect:
- Auth module + API module + UI components
- Different microservices
- Multiple independent features
```

#### Large Changesets
```text
Changes include:
- 10+ files modified
- 500+ lines changed
- Multiple directories affected
```

#### Mixed Types
```text
Changes mix:
- Implementation + tests
- Code + documentation
- Feature + configuration
```

### Don't Split When...

#### Interdependent Changes
```text
Changes are tightly coupled:
- Function + its test helper
- Component + its types (same file)
- Rename across multiple files (single refactor)
```

#### Already Atomic
```text
Change is single-purpose:
- One function addition
- One bug fix
- One configuration tweak
```

#### Breaking Build
```text
Splitting would break:
- Type references
- Function calls
- Imports/exports
```

## Splitting Strategies

### Strategy 1: By Concern

**Use for**: Mixed change types

```bash
# Before (mixed)
- feat: login logic
- fix: validation bug
- refactor: extract helper

# After (split by concern)
1. refactor(auth): extract validation helper
2. fix(auth): correct email validation
3. feat(auth): add OAuth login
```

**Order**: Refactor → Fix → Feature

### Strategy 2: By Scope

**Use for**: Multi-component changes

```bash
# Before (multiple scopes)
- auth module changes
- api module changes
- ui module changes

# After (split by scope)
1. feat(auth): add OAuth provider
2. feat(api): add OAuth endpoints
3. feat(ui): add OAuth login button
```

**Order**: Backend → API → Frontend

### Strategy 3: By Type

**Use for**: Implementation + tests + docs

```bash
# Before (mixed types)
- implementation
- tests
- documentation

# After (split by type)
1. feat(auth): implement OAuth
2. test(auth): add OAuth tests
3. docs(auth): document OAuth setup
```

**Order**: Implementation → Tests → Docs

### Strategy 4: By Dependency

**Use for**: Layered changes

```bash
# Before (dependencies)
- types (used by implementation)
- implementation (used by feature)
- feature (uses implementation)

# After (split by dependency)
1. feat(types): add OAuth types
2. feat(auth): add OAuth provider
3. feat(api): integrate OAuth provider
```

**Order**: Foundation → Implementation → Usage

## Anti-Patterns

### 1. Over-Splitting

**Problem**: Commits too granular to be useful

```bash
❌ Bad:
1. Add import statement
2. Add type definition
3. Add function
4. Add export

✅ Good:
1. feat(utils): add validation helper
   - Complete implementation with types
```

**Rule**: Each commit should be independently useful.

### 2. Under-Splitting

**Problem**: Commits too large to review

```bash
❌ Bad:
1. Implement entire feature
   - 50 files
   - Auth + API + UI + tests + docs

✅ Good:
1. feat(auth): add OAuth provider
2. feat(api): add OAuth endpoints
3. feat(ui): add OAuth UI
4. test: add OAuth tests
5. docs: document OAuth
```

**Rule**: Keep commits focused and reviewable (< 300 lines ideal).

### 3. Breaking Dependencies

**Problem**: Wrong commit order breaks builds

```bash
❌ Bad:
1. feat(api): use new validator (doesn't exist yet)
2. feat(auth): add validator

✅ Good:
1. feat(auth): add validator
2. feat(api): use new validator
```

**Rule**: Maintain build stability across all commits.

### 4. Arbitrary Splitting

**Problem**: Split without logical reason

```bash
❌ Bad:
1. First half of function
2. Second half of function

✅ Good:
1. Complete function implementation
```

**Rule**: Split by logic, not by lines.

### 5. Mixed Scopes in One Commit

**Problem**: Multiple components in single commit

```bash
❌ Bad:
1. feat: add feature
   - auth module changes
   - api module changes
   - ui module changes

✅ Good:
1. feat(auth): add OAuth
2. feat(api): add OAuth endpoints
3. feat(ui): add OAuth button
```

**Rule**: One scope (component/module) per commit when possible.

## Practical Guidelines

### File Organization

**Same commit**:
- Implementation + its types (same file)
- Component + its styles (tight coupling)
- Migration + rollback (paired changes)

**Separate commits**:
- Implementation + tests
- Code + documentation
- Different components
- Different concerns

### Commit Message Guidelines

**Be specific about scope**:
```bash
✅ feat(auth): add OAuth login
❌ feat: add stuff
```

**Describe the what, not how**:
```bash
✅ refactor(auth): extract validation logic
❌ refactor(auth): move code to new file
```

**Reference issues**:
```bash
✅ fix(api): handle null user (#1234)
❌ fix(api): fix bug
```

### Review Perspective

**Think about the reviewer**:
- Can they understand each commit independently?
- Is the commit message clear?
- Is the change focused?
- Could they review this in 5-10 minutes?

**Good commit sequence tells a story**:
```bash
1. refactor(db): extract query builder
   "Set up foundation"

2. feat(db): add query optimization
   "Build on foundation"

3. test(db): add optimization tests
   "Verify it works"

4. docs(db): document optimization
   "Explain to users"
```

## Testing Your Splits

### Checklist

Before finalizing splits, verify:

- [ ] Each commit builds successfully
- [ ] Each commit passes tests
- [ ] Commits are in dependency order
- [ ] Each commit has single, clear purpose
- [ ] Commit messages follow conventions
- [ ] No commit mixes multiple scopes
- [ ] No commit contains unrelated changes

### Validation Commands

```bash
# Test each commit individually
git rebase -i HEAD~n  # n = number of commits
# Mark each with "edit"

# For each commit:
npm run build && npm test

# If all pass, splits are good
git rebase --continue
```

### Quick Test

**Can you answer these for each commit?**

1. What is the single purpose?
2. Why is this change needed?
3. What scope/component does it affect?
4. Does it build and test independently?
5. Is it in the right order?

**If "no" to any**: Reconsider the split.

## Common Scenarios

### Scenario: Large Feature

**Approach**: Split by layers

```bash
1. Database schema changes
2. Data access layer
3. Business logic
4. API endpoints
5. Tests for each layer
6. Documentation
```

### Scenario: Bug Fix + Tests

**Approach**: Fix first, then tests

```bash
1. fix(module): correct issue
2. test(module): add regression test
```

**Why**: Fix should be clear without test noise.

### Scenario: Refactor + New Feature

**Approach**: Refactor first

```bash
1. refactor(module): extract helpers
2. feat(module): add feature using helpers
```

**Why**: Refactor establishes foundation.

### Scenario: Breaking Change

**Approach**: Isolate breaking change

```bash
1. feat(api)!: new v2 endpoint
   BREAKING CHANGE: response format changed

2. chore(api): deprecate v1 endpoint

3. feat(migration): add v1 to v2 migrator

4. docs(api): add migration guide
```

**Why**: Clear what breaks and how to migrate.

## Interactive Splitting Workflow

### Using git add -p

```bash
# Review each hunk
git add -p file.ts

# Options per hunk:
# y - stage this hunk
# n - don't stage
# s - split into smaller hunks
# e - manually edit hunk
```

### Using git add -e

```bash
# Manually edit staged content
git add -e file.ts

# Remove lines you don't want to stage
# Save and close to stage edited content
```

### Workflow

```bash
# 1. Review all changes
git diff --staged

# 2. Reset staging
git reset

# 3. Stage first logical group
git add file1.ts file2.ts
# or
git add -p file.ts

# 4. Commit first split
git commit -m "first logical change"

# 5. Repeat for remaining splits
```

## Summary

### Golden Rules

1. **One logical change per commit**
2. **Each commit builds independently**
3. **Order by dependency**
4. **Separate concerns (impl/test/docs)**
5. **Keep commits focused and reviewable**

### Benefits of Good Splits

- Easier code review
- Better git history
- Simpler debugging (bisect)
- Safer reverts
- Cleaner changelogs
- More professional codebase

### When Unsure

**Ask yourself**:
- Is this commit independently useful?
- Can I describe it without "and"?
- Would splitting make review easier?
- Does it break the build?

**If still unsure**: Err on the side of smaller, focused commits.
