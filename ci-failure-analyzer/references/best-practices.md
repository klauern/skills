# CI Failure Analyzer Best Practices

Guidelines for autonomous fix application, safety protocols, and building user trust.

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [When to Auto-Fix vs. Ask](#when-to-auto-fix-vs-ask)
3. [Safety Checks](#safety-checks)
4. [User Communication](#user-communication)
5. [Progressive Fix Strategies](#progressive-fix-strategies)
6. [Handling Failures](#handling-failures)
7. [Trust and Transparency](#trust-and-transparency)
8. [Edge Cases](#edge-cases)

---

## Core Philosophy

### Don't Overdo It

The skill follows a **conservative, user-respecting approach**:

> **"Handle mechanical issues automatically, but respect user control over meaningful code changes."**

**Guiding Principles**:

1. **User Autonomy**: Users should feel in control, not like the tool is taking over
2. **Safety First**: Never apply risky changes without approval
3. **Transparency**: Always explain what will be done before doing it
4. **Reversibility**: Prefer changes that can be easily undone
5. **Predictability**: Behave consistently so users can trust the tool

### The Mechanical vs. Meaningful Boundary

**Mechanical** (auto-fixable):
- Code formatting (whitespace, indentation)
- Linting with --fix flags (import order, unused imports)
- Lock file regeneration
- Simple dependency installation

These don't change *what* the code does, only *how* it looks.

**Meaningful** (consult user):
- Type errors requiring code changes
- Test logic failures
- Breaking changes requiring API updates
- Architecture decisions
- Anything affecting business logic

These change *what* the code does or how it behaves.

---

## When to Auto-Fix vs. Ask

### Auto-Fix Without Asking

Apply these fixes automatically without user approval:

#### 1. Code Formatting

✅ **Always auto-fix**:
- Prettier, Black, gofmt, rustfmt
- Indentation, spacing, line length
- Quote style, trailing commas

**Why**: No semantic changes, universally expected

**Example**:
```
I found Prettier formatting issues. Running: npx prettier --write .
```

#### 2. Linting with --fix (Safe Rules)

✅ **Auto-fix if rules are safe**:
- Import order corrections
- Removing unused imports (not variables)
- Adding missing semicolons
- Spacing around operators

**Why**: These are mechanical style fixes

**Example**:
```
I found ESLint issues that can be auto-fixed. Running: npx eslint --fix .
```

❌ **Don't auto-fix**:
- Unused variables (might be intentionally there)
- Missing error handling (affects logic)
- Console.log removal (might be debugging)

#### 3. Lock File Regeneration

✅ **Auto-fix**:
- package-lock.json out of sync with package.json
- poetry.lock mismatch
- Cargo.lock updates

**Why**: These are deterministic based on package.json

**Caveat**: Always show the diff afterward

**Example**:
```
I found a lock file mismatch. Running: npm install
```

#### 4. Simple Dependency Installation

✅ **Auto-fix if obvious**:
- Missing import matches known package name
- Package name is unambiguous
- Adding to devDependencies (for test imports)

**Example**:
```
Missing package 'lodash'. Running: npm install lodash
```

❌ **Ask first if**:
- Package name is ambiguous (@types packages, multiple options)
- Adds to production dependencies
- Requires version selection

### Ask User Before Fixing

Always consult the user for these scenarios:

#### 1. Type Errors

**Why**: Requires understanding intent

**Example**:
```
I found a type error in src/utils.ts:15:
  Type 'string' is not assignable to type 'number'

This could mean:
- The function should accept strings, or
- The variable should be converted to a number

Would you like me to:
A) Change the type annotation to accept strings
B) Add a conversion to number
C) Show me the code so I can decide
```

#### 2. Test Failures

**Why**: Test failures indicate logic issues

**Example**:
```
Test failure in src/utils.test.ts:
  Expected: 10
  Received: 8

This suggests the calculateTotal function may have a bug, or the test expectation is wrong.

The function sums [3, 5] but returns 8 instead of 10.

Would you like me to:
- Open the function for you to review
- Show recent changes to this file
- Explain the test in more detail
```

#### 3. Breaking Changes

**Why**: Requires migration strategy decision

**Example**:
```
The package 'axios' was updated to v2.0.0 which has breaking changes.

Breaking changes:
- `axios.get()` now returns a different response format
- Configuration options have changed

I found 15 files using axios. Migrating requires:
1. Updating response handling in all API calls
2. Updating axios configuration

Would you like me to:
A) Create a detailed migration plan
B) Update the code (will show each change for approval)
C) Downgrade to v1.x temporarily
```

#### 4. Complex Build Failures

**Why**: May require architectural decisions

**Example**:
```
Build failing due to circular dependency:
  src/utils.ts → src/api.ts → src/utils.ts

This requires refactoring to break the cycle. Options:
1. Extract shared code to src/shared.ts
2. Merge the two files
3. Redesign the dependency relationship

Which approach would you prefer?
```

---

## Safety Checks

Before applying any fix, perform these safety checks:

### Pre-Fix Checklist

1. **Verify Clean Working Directory**
   ```bash
   git status
   ```
   - ❌ If uncommitted changes unrelated to CI fix, warn user
   - ✅ If clean, proceed

2. **Check Current Branch**
   - ❌ If on main/master, warn about applying changes directly
   - ✅ If on feature branch, proceed

3. **Verify Tool Availability**
   ```bash
   command -v prettier >/dev/null 2>&1
   ```
   - ❌ If tool not found, explain and suggest installation
   - ✅ If available, proceed

4. **Estimate Impact**
   - How many files will be affected?
   - Is this a single file or project-wide?
   - ✅ If localized (< 5 files), proceed
   - ⚠️ If widespread (> 10 files), inform user of scope

### During Fix

5. **Capture Output**
   - Save both stdout and stderr
   - Check exit code
   - ❌ If non-zero exit, report failure

6. **Verify Changes**
   ```bash
   git diff --stat
   ```
   - Show number of files changed
   - Show line count (+/-)
   - ⚠️ If unexpectedly large, pause and ask user

### Post-Fix Validation

7. **Show Diff**
   ```bash
   git diff
   ```
   - For small changes, show full diff
   - For large changes, show summary + offer full diff

8. **Verify Fix Solved Issue**
   - Re-run the tool if possible
   ```bash
   npx prettier --check .
   ```
   - ✅ If passes, confirm fix successful
   - ❌ If still failing, investigate further

9. **Test Build/Tests Locally** (if applicable)
   ```bash
   npm run build
   npm test
   ```
   - ⚠️ Only if fix might affect build/tests
   - ✅ If passes, high confidence in fix

---

## User Communication

### Before Fixing

**Template**:
```
I found [issue type] that [can be auto-fixed / requires manual changes].

[Brief explanation of the issue]

I will run: [exact command]

This will affect: [scope - files, impact]
```

**Example**:
```
I found Prettier formatting issues in 8 files.

The following files need reformatting:
- src/index.ts
- src/utils.ts
- ... (6 more)

I will run: npx prettier --write .

This is a safe operation that only changes code formatting.
```

### During Fixing

**Show Progress** for slow operations:
```
Running prettier... (this may take a moment)
```

**Stream Output** for transparency:
- Show key output lines
- Don't overwhelm with verbose output
- Capture full output for debugging

### After Fixing

**Report Results**:
```
✓ Prettier formatting applied

Changed files:
- src/index.ts (+2, -2)
- src/utils.ts (+1, -1)

8 files reformatted.

Next step: Review changes with `git diff` or run `/commit` to commit these fixes.
```

### For Manual Fixes

**Provide Guidance**:
```
I found type errors that require manual fixes:

src/utils.ts:15:10
  Type 'string' is not assignable to type 'number'

Recommendation:
Change line 15 from:
  let count: number = "5";
To:
  let count: number = 5;

Would you like me to make this change?
```

---

## Progressive Fix Strategies

### Start Simple, Escalate if Needed

**Level 1: Mechanical Fixes** (Haiku)
- Formatting
- Simple linting
- Lock files

If these don't resolve all issues → **Level 2**

**Level 2: Semantic Analysis** (Sonnet)
- Understand remaining errors
- Categorize by complexity
- Provide fix plan

If user approves manual fixes → **Level 3**

**Level 3: Guided Fixes** (Sonnet)
- Make changes with user approval
- Explain each change
- Verify after each fix

### Incremental Application

**Don't batch everything**:

❌ Bad:
```
Applying 10 different fixes...
[makes all changes at once]
```

✅ Good:
```
1. First, let's fix formatting (safe)
   [applies prettier]
   ✓ Done. Review with `git diff`

2. Next, I found ESLint issues with --fix available
   [applies eslint --fix]
   ✓ Done.

3. There are 3 type errors remaining that need manual review
   [shows each one individually]
```

**Benefits**:
- User can verify each step
- Easy to revert if something wrong
- Clear understanding of what changed

### Fail Fast

If a fix doesn't work:

❌ Don't keep trying random things:
```
Trying prettier... didn't work
Trying black... didn't work
Trying gofmt... didn't work
```

✅ Analyze and explain:
```
The formatting issue persists after running prettier.

This might mean:
- The CI uses a different prettier config
- The error is misidentified (might not be prettier)
- There's a syntax error preventing formatting

Let me check the actual error message more carefully...
```

---

## Handling Failures

### When Fix Doesn't Resolve Issue

**Don't panic, analyze**:

1. **Re-check Logs**
   - Was the issue correctly identified?
   - Are there additional errors not initially seen?

2. **Verify Tool Configuration**
   - Does CI use different config than local?
   - Check for .prettierrc, .eslintrc, tsconfig.json

3. **Consider Environment Differences**
   - Different tool versions?
   - Different Node/Python version?

4. **Explain to User**:
   ```
   The fix didn't resolve the CI failure. Here's what I found:

   - Applied prettier formatting
   - CI still reports formatting issues
   - Likely cause: CI uses .prettierrc with different config

   Next steps:
   1. Check .prettierrc settings
   2. Run prettier with same config as CI
   3. Verify with a commit and push to see CI results
   ```

### When Multiple Fixes Conflict

**Prioritize, don't overlap**:

Example: Both prettier and eslint handle formatting

✅ Good:
```
I see both prettier and eslint are configured.

Recommended order:
1. Run prettier first (handles formatting)
2. Run eslint --fix second (handles code quality)

This avoids conflicts where tools fight over formatting.
```

### When User Disagrees with Fix

**Respect user's decision**:

```
User: "Don't auto-format, I prefer my style"