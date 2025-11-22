# CI Failure Patterns

Comprehensive taxonomy of CI failure types with detection patterns, root causes, and fix strategies.

## Table of Contents

1. [Formatting Failures](#formatting-failures)
2. [Linting Failures](#linting-failures)
3. [Type Checking Failures](#type-checking-failures)
4. [Test Failures](#test-failures)
5. [Build Failures](#build-failures)
6. [Dependency Failures](#dependency-failures)
7. [Security Failures](#security-failures)
8. [Secrets & Permissions Failures](#secrets--permissions-failures)
9. [Cache & Artifact Failures](#cache--artifact-failures)
10. [Matrix Partial Failures](#matrix-partial-failures)
11. [Infrastructure Failures](#infrastructure-failures)
12. [Pattern Matching Guide](#pattern-matching-guide)

---

## Formatting Failures

Auto-fixable issues related to code formatting and style.

### Prettier (JavaScript/TypeScript)

**Detection Patterns**:

```
- Log contains: "prettier" (case-insensitive)
- Exit code: 1
- Error format: "Code style issues found in the above file(s)"
- File references: Multiple files listed
```

**Common Error Messages**:

```
[warn] src/index.ts
[warn] src/utils.js
[warn] Code style issues found in the above file(s). Run Prettier to fix.
```

**Root Causes**:

- Incorrect indentation (tabs vs. spaces)
- Missing semicolons or extra semicolons
- Quote style mismatches (single vs. double)
- Line length violations
- Trailing commas

**Auto-Fix Command**:

```bash
npx prettier --write .
```

**Alternative Commands**:

```bash
# Specific files
npx prettier --write src/**/*.{js,ts,jsx,tsx}

# With custom config
npx prettier --write . --config .prettierrc

# Check only (no fix)
npx prettier --check .
```

**Verification**:

```bash
git diff
# Should show formatting changes
```

**Model**: Haiku 4.5 (pattern is clear, fix is mechanical)

**Auto-Fix Success Rate**: 99%

---

### Black (Python)

**Detection Patterns**:

```
- Log contains: "black" or "would reformat"
- Exit code: 1
- Error format: "X file(s) would be reformatted"
- File references: Listed before error message
```

**Common Error Messages**:

```
would reformat src/main.py
would reformat tests/test_utils.py
2 files would be reformatted, 3 files would be left unchanged.
```

**Root Causes**:

- Incorrect line length (default 88 characters)
- Inconsistent quote usage
- Whitespace issues
- Import formatting

**Auto-Fix Command**:

```bash
black .
```

**Alternative Commands**:

```bash
# Specific directory
black src/

# With custom line length
black --line-length 100 .

# Check only
black --check .
```

**Verification**:

```bash
git diff
```

**Model**: Haiku 4.5

**Auto-Fix Success Rate**: 99%

---

### gofmt (Go)

**Detection Patterns**:

```
- Log contains: "gofmt" or "not formatted"
- Exit code: 1
- Error format: Lists files with formatting issues
```

**Common Error Messages**:

```
main.go is not formatted
utils/helper.go is not formatted
```

**Root Causes**:

- Incorrect indentation (Go uses tabs)
- Missing newlines
- Whitespace around operators

**Auto-Fix Command**:

```bash
gofmt -w .
```

**Alternative Commands**:

```bash
# Specific files
gofmt -w $(find . -name '*.go')

# Check only
gofmt -l .

# Using gofumpt (stricter)
gofumpt -w .
```

**Model**: Haiku 4.5

**Auto-Fix Success Rate**: 99%

**Note**: User's CLAUDE.md specifies `gofumpt` preference over `gofmt`

---

### rustfmt (Rust)

**Detection Patterns**:

```
- Log contains: "rustfmt" or "cargo fmt"
- Exit code: 1
- Error indicates formatting issues
```

**Auto-Fix Command**:

```bash
cargo fmt
```

**Model**: Haiku 4.5

**Auto-Fix Success Rate**: 99%

---

## Linting Failures

Code quality issues that may or may not be auto-fixable.

### ESLint (JavaScript/TypeScript)

**Detection Patterns**:

```
- Log contains: "eslint"
- Exit code: 1
- Error format: "file.js:line:col  error  message  rule-name"
- Multiple errors listed with file paths
```

**Common Error Messages**:

```
/Users/user/project/src/index.ts
  15:10  error  'x' is assigned a value but never used  @typescript-eslint/no-unused-vars
  23:5   error  Missing return type on function         @typescript-eslint/explicit-function-return-type

✖ 2 problems (2 errors, 0 warnings)
```

**Root Causes**:

- Unused variables
- Missing semicolons
- Console.log statements
- Import order issues
- Spacing and formatting (if not using Prettier)
- Type annotations (TypeScript)

**Auto-Fix Command**:

```bash
npx eslint --fix .
```

**Alternative Commands**:

```bash
# Specific files
npx eslint --fix src/**/*.ts

# Check only
npx eslint .

# With specific config
npx eslint --fix --config .eslintrc.js .
```

**Auto-Fix Success Rate**: 60-80% (depends on rules)

**Manual Fixes Needed For**:

- Unused variables (need to determine if should be removed or used)
- Missing return types (need to determine correct type)
- Logic issues flagged by linter

**Model**:

- Haiku for running `--fix`
- Sonnet for manual fixes

**Verification**:

```bash
git diff
npx eslint . # Should show remaining issues if any
```

---

### Ruff (Python)

**Detection Patterns**:

```
- Log contains: "ruff"
- Exit code: 1
- Error format: "file.py:line:col: CODE message"
```

**Common Error Messages**:

```
src/main.py:15:10: F841 Local variable `x` is assigned to but never used
src/utils.py:23:5: E501 Line too long (92 > 88)
```

**Root Causes**:

- Unused imports
- Unused variables
- Line length violations
- Import order issues

**Auto-Fix Command**:

```bash
ruff check --fix .
```

**Alternative Commands**:

```bash
# Specific files
ruff check --fix src/

# Check only
ruff check .

# With specific rules
ruff check --select E,F --fix .
```

**Auto-Fix Success Rate**: 70-90%

**Model**: Haiku for `--fix`, Sonnet for remaining issues

---

### Clippy (Rust)

**Detection Patterns**:

```
- Log contains: "clippy" or "cargo clippy"
- Exit code: 1
- Warning/error format from cargo
```

**Common Error Messages**:

```
warning: unused variable: `x`
  --> src/main.rs:15:9
   |
15 |     let x = 5;
   |         ^ help: if this is intentional, prefix it with an underscore: `_x`
```

**Auto-Fix Command**:

```bash
# Clippy doesn't have auto-fix, but suggestions are clear
# Usually requires manual changes
```

**Auto-Fix Success Rate**: 20% (most require manual changes)

**Model**: Sonnet (requires understanding context)

---

### golangci-lint (Go)

**Detection Patterns**:

```
- Log contains: "golangci-lint"
- Exit code: 1
- Error format: "file.go:line:col: message (linter-name)"
```

**Auto-Fix Command**:

```bash
golangci-lint run --fix
```

**Auto-Fix Success Rate**: 40-60%

**Model**: Haiku for `--fix`, Sonnet for remaining issues

---

## Type Checking Failures

Type system errors requiring code changes.

### TypeScript (tsc)

**Detection Patterns**:

```
- Log contains: "tsc" or "TS[0-9]+"
- Exit code: 2
- Error format: "file.ts(line,col): error TS#### message"
```

**Common Error Messages**:

```
src/index.ts(15,10): error TS2322: Type 'string' is not assignable to type 'number'.
src/utils.ts(23,5): error TS7006: Parameter 'x' implicitly has an 'any' type.
src/api.ts(42,15): error TS2339: Property 'foo' does not exist on type 'Bar'.
```

**Root Causes**:

- Type mismatches
- Missing type annotations
- Wrong property access
- Null/undefined issues
- Generic type issues

**Auto-Fix Potential**:

- **Simple annotations**: Add `: type` → Can auto-fix
- **Type mismatches**: Need to understand intent → Manual
- **Missing properties**: May need interface updates → Manual

**Simple Auto-Fix Examples**:

```typescript
// Before
function foo(x) {
  return x + 1;
}

// After (auto-fixable if type is obvious from usage)
function foo(x: number): number {
  return x + 1;
}
```

**Auto-Fix Success Rate**: 20-30% (mostly simple annotations)

**Model**:

- Sonnet (type errors require understanding code intent)
- Only Haiku for trivial annotation additions

**Verification**:

```bash
npx tsc --noEmit
```

---

### mypy (Python)

**Detection Patterns**:

```
- Log contains: "mypy"
- Exit code: 1
- Error format: "file.py:line: error: message"
```

**Common Error Messages**:

```
src/main.py:15: error: Incompatible types in assignment (expression has type "str", variable has type "int")
src/utils.py:23: error: Missing return statement
```

**Auto-Fix Success Rate**: 15-25%

**Model**: Sonnet

---

## Test Failures

Failures in test suites - usually require logic fixes.

### Jest (JavaScript/TypeScript)

**Detection Patterns**:

```
- Log contains: "FAIL" and test file paths
- Exit code: 1
- Error format shows:
  - Test name
  - Expected vs. received
  - Stack trace
```

**Common Error Messages**:

```
FAIL src/utils.test.ts
  ● calculateTotal › returns correct sum

    expect(received).toBe(expected)

    Expected: 10
    Received: 8

      15 |   it('returns correct sum', () => {
      16 |     const result = calculateTotal([3, 5]);
    > 17 |     expect(result).toBe(10);
      18 |   });
```

**Root Causes**:

- Logic bugs in code under test
- Incorrect test expectations
- Missing mocks
- Async timing issues
- Setup/teardown problems

**Categorization**:

1. **Assertion Failures** (most common)
   - Expected value doesn't match received
   - Logic bug or wrong expectation

2. **Timeout Errors**
   - Test exceeds time limit
   - Async operation not completing
   - Infinite loop

3. **Setup Errors**
   - beforeEach/beforeAll failures
   - Missing dependencies
   - Environment issues

4. **TypeError/ReferenceError**
   - Undefined variables
   - Missing mocks
   - Wrong imports

**Auto-Fix Potential**: Very low (5-10%)

**Model**: Sonnet (requires semantic understanding)

**Analysis Approach**:

1. Identify failing test name
2. Extract expected vs. received values
3. Find test file and line number
4. Correlate with recent code changes
5. Determine if test or code is wrong

---

### pytest (Python)

**Detection Patterns**:

```
- Log contains: "FAILED" and test paths
- Exit code: 1
- Shows assertion failures with context
```

**Common Error Messages**:

```
FAILED tests/test_utils.py::test_calculate_total - AssertionError: assert 8 == 10
    def test_calculate_total():
        result = calculate_total([3, 5])
>       assert result == 10
E       assert 8 == 10
```

**Model**: Sonnet

**Auto-Fix Success Rate**: 5-10%

---

### Go Test

**Detection Patterns**:

```
- Log contains: "FAIL" and package paths
- Exit code: 1
- Shows test function names
```

**Common Error Messages**:

```
--- FAIL: TestCalculateTotal (0.00s)
    utils_test.go:15: got 8, want 10
FAIL
FAIL    github.com/user/project/utils   0.001s
```

**Model**: Sonnet

**Auto-Fix Success Rate**: 5-10%

---

## Build Failures

Compilation and bundling errors.

### Webpack/Vite Build

**Detection Patterns**:

```
- Log contains: "webpack" or "vite" or "build failed"
- Exit code: 1
- Shows module not found or syntax errors
```

**Common Error Messages**:

```
ERROR in ./src/index.ts
Module not found: Error: Can't resolve './utils' in '/project/src'

ERROR in ./src/App.tsx
Module parse failed: Unexpected token (15:10)
You may need an appropriate loader to handle this file type.
```

**Root Causes**:

- Missing imports
- Wrong file paths
- Missing loaders/plugins
- Syntax errors
- Circular dependencies

**Auto-Fix Potential**: 30-40%

**Model**:

- Haiku for missing import fixes
- Sonnet for complex bundling issues

---

### TypeScript Compilation

**Detection Patterns**:

```
- Similar to type checking but in build context
- May show in build output rather than tsc directly
```

**Model**: Sonnet

---

### Go Build

**Detection Patterns**:

```
- Log contains: "go build" or compilation errors
- Exit code: 2
- Shows syntax errors or undefined references
```

**Common Error Messages**:

```
./main.go:15:10: undefined: foo
./utils.go:23:5: syntax error: unexpected }, expecting expression
```

**Auto-Fix Potential**: 20-30%

**Model**: Sonnet for understanding context, Haiku for simple fixes

---

## Dependency Failures

Package management and dependency resolution issues.

### npm/yarn - Lock File Mismatch

**Detection Patterns**:

```
- Log contains: "package-lock.json" or "yarn.lock"
- Error messages about "out of sync" or "mismatch"
- CI install/ci command failing
```

**Common Error Messages**:

```
npm ERR! `npm ci` can only install packages when your package.json and package-lock.json are in sync.
npm ERR! Please update your lock file with `npm install` before continuing.

The package.json has been modified. Run "npm install" to update the lockfile.
```

**Root Causes**:

- package.json updated without regenerating lock file
- Lock file committed with wrong versions
- Different npm versions

**Auto-Fix Command**:

```bash
# npm
npm install
# Then commit the updated package-lock.json

# yarn
yarn install

# pnpm
pnpm install
```

**Auto-Fix Success Rate**: 95%

**Model**: Haiku (straightforward fix)

**Verification**:

```bash
git diff package-lock.json
# Should show updated versions/hashes
```

---

### Poetry Lock (Python)

**Detection Patterns**:

```
- Log contains: "poetry" and "lock file"
- Error about lock file out of sync
```

**Auto-Fix Command**:

```bash
poetry lock --no-update
```

**Auto-Fix Success Rate**: 90%

**Model**: Haiku

---

### Cargo (Rust)

**Detection Patterns**:

```
- Log contains: "Cargo.lock"
- Version mismatch errors
```

**Auto-Fix Command**:

```bash
cargo update
```

**Model**: Haiku

---

### Missing Dependency

**Detection Patterns**:

```
- Error: "Cannot find module 'foo'"
- Import errors
- ModuleNotFoundError
```

**Auto-Fix Command** (if dependency is obvious):

```bash
# npm
npm install <package>

# poetry
poetry add <package>

# go
go get <package>
```

**Auto-Fix Success Rate**: 60-70%

**Challenges**:

- Determining correct package name
- Choosing between dependencies vs. devDependencies
- Version selection

**Model**:

- Haiku if package name is obvious from import
- Sonnet if needs research

---

### Version Conflict

**Detection Patterns**:

```
- Error about incompatible versions
- Peer dependency warnings
- Resolution errors
```

**Common Error Messages**:

```
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^17.0.0" from react-dom@17.0.2
npm ERR! while installing react@18.0.0
```

**Auto-Fix Potential**: 30-40%

**Model**: Sonnet (requires understanding dependency graph)

---

## Security Failures

Vulnerability and security scan failures.

### npm audit

**Detection Patterns**:

```
- Log contains: "npm audit" or "vulnerabilities found"
- Lists vulnerable packages with severity
```

**Common Error Messages**:

```
found 3 vulnerabilities (1 moderate, 2 high)
  run `npm audit fix` to fix them, or `npm audit` for details
```

**Auto-Fix Command**:

```bash
npm audit fix
```

**Cautions**:

- May update to new major versions
- Can break compatibility
- Should review changes

**Auto-Fix Success Rate**: 50-70%

**Model**: Haiku for simple fixes, Sonnet for breaking changes

---

### Snyk/Dependabot

**Detection Patterns**:

```
- Security vulnerability alerts
- Links to CVE databases
```

**Auto-Fix Approach**:

- Update vulnerable dependency
- Verify no breaking changes
- Test after update

**Model**: Sonnet (needs impact assessment)

---

## Secrets & Permissions Failures

Missing secrets, insufficient token scopes, or organization policies blocking workflow actions.

### Detection Patterns

```
- "Resource not accessible by integration"
- "##[error]No value for required secret"
- "Error: The process '/usr/bin/git' failed with exit code 128"
- Exit code 78 (often indicates permission issues)
- API responses: "HttpError: 403 Forbidden"
```

### Common Root Causes

- Secret renamed or deleted (e.g., `secrets.NPM_TOKEN`)
- GITHUB_TOKEN missing required scopes (`contents: write`, `pull-requests: write`)
- Workflow trying to access org-level resources without approval
- Deploy keys revoked or expired

### Recommended Response

1. Identify the exact secret name or permission from logs.
2. Reference workflow YAML to show where the secret is used.
3. Suggest verifying via GitHub UI (`Settings → Secrets and variables → Actions`).
4. For token scope issues, recommend updating the `permissions` block.
5. Mark issue as **non-code** and avoid editing workflow files unless instructed.

**Model Strategy**:

- Sonnet for explaining configuration fixes and risks.
- Haiku can surface the relevant YAML snippet or secret references.

---

## Cache & Artifact Failures

Cache restore/save steps or artifact download/upload failures.

### Detection Patterns

```
- "Failed to restore cache"
- "Cache not found for input keys: ..."
- "tar: short read"
- "Error: Failed to download artifact"
- "Artifact has expired or was deleted"
```

### Root Causes

- Cache key changed or corrupted
- Artifact retention period expired
- Disk space limitations on runner
- Incompatible tar/compression versions

### Fix Strategy

1. Surface cache key and step name from logs.
2. Recommend bumping cache key suffix (e.g., `cache-node-modules-v2`).
3. Suggest deleting/re-uploading artifact if corruption suspected.
4. Encourage re-running the affected job only after cache adjustments.

**Model Strategy**:

- Haiku to extract cache keys and commands.
- Sonnet to explain impact and guide manual remediation.

---

## Matrix Partial Failures

Only a single matrix combination fails (e.g., Node 18 on ubuntu-latest).

### Detection Patterns

```
- Job names include matrix metadata: "test (node-version: 18, os: ubuntu-latest)"
- GitHub UI shows ✔️/❌ per combination
- Logs mention environment-specific errors (e.g., Windows path casing)
```

### Root Causes

- Runtime-specific bugs (Node version, Python version, OS differences)
- Missing dependencies on one platform
- Feature flags or conditional tests

### Fix Strategy

1. Enumerate all matrix combinations and mark failing ones.
2. Determine if failure is unique to runtime/OS or underlying code.
3. Provide targeted repro instructions (e.g., `nvm use 18 && npm test`).
4. Avoid rerunning entire matrix—rerun only the failing axis once fix is applied.

**Model Strategy**:

- Haiku to gather job metadata and logs.
- Sonnet to reason about axis-specific behaviors and prioritize fixes.

---

## Infrastructure Failures

CI environment and infrastructure issues.

### Timeout

**Detection Patterns**:

```
- Log contains: "timeout" or "exceeded maximum time"
- Job killed after time limit
- Exit code: 124 or 143
```

**Common Error Messages**:

```
Error: The operation was canceled.
Error: The job running on runner... has exceeded the maximum execution time of 360 minutes.
```

**Root Causes**:

- Slow tests
- Infinite loops
- Network issues
- Large build artifacts

**Auto-Fix Potential**: Low (5%)

**Solutions**:

- Increase timeout in workflow config
- Optimize slow operations
- Add timeouts to tests
- Cache dependencies

**Model**: Sonnet (requires diagnosis)

---

### Rate Limiting

**Detection Patterns**:

```
- Error: "rate limit exceeded"
- HTTP 429 errors
- API quota messages
```

**Common Error Messages**:

```
API rate limit exceeded for xxx.xxx.xxx.xxx
Error: You have exceeded a secondary rate limit

npm ERR! code E429
npm ERR! 429 Too Many Requests
```

**Auto-Fix Potential**: Very low

**Solutions**:

- Add delays between requests
- Use authentication tokens
- Cache responses
- Implement retry logic

**Model**: Sonnet

---

### Network Errors

**Detection Patterns**:

```
- Connection refused
- DNS errors
- Timeout connecting
```

**Auto-Fix Potential**: Very low (transient issues)

**Solutions**:

- Retry failed step
- Check if external service is down
- Verify network configuration

**Model**: Sonnet for diagnosis

---

### Disk Space

**Detection Patterns**:

```
- Error: "No space left on device"
- ENOSPC errors
```

**Auto-Fix Potential**: Low

**Solutions**:

- Clean up old artifacts
- Increase runner disk space
- Optimize build output

**Model**: Haiku for cleanup commands

---

## Pattern Matching Guide

### Priority Order for Pattern Matching

When analyzing logs, check patterns in this order:

1. **Explicit tool mentions** (highest confidence)
   - "prettier", "black", "eslint", "tsc"
   - Use Haiku - fast and accurate

2. **Error code patterns**
   - "TS####", "E####", "W####"
   - Use Haiku if code maps to known pattern

3. **File path + error format**
   - "file.ts:line:col: error message"
   - Use Haiku for extraction

4. **Exit codes**
   - 0: Success
   - 1: General error (most common)
   - 2: Compilation error
   - 124/143: Timeout
   - Use Haiku for categorization

5. **Stack traces**
   - Indicate runtime failures
   - Usually tests or build issues
   - Use Sonnet for analysis

6. **Context clues** (lowest confidence)
   - "expected" vs "received" → Test failure
   - "Cannot find module" → Import error
   - Use Sonnet if ambiguous

### Regex Patterns for Common Errors

```regex
# Prettier
prettier|Code style issues found

# Black
black|would reformat|file.*would be reformatted

# ESLint
eslint|\.js:\d+:\d+.*error

# TypeScript
TS\d{4}|\.ts\(\d+,\d+\):.*error

# Jest test failure
FAIL.*\.test\.(js|ts)x?|expect\(.*\)\.toBe\(

# npm audit
\d+ vulnerabilities?|npm audit

# Lock file mismatch
package-lock\.json.*out of sync|lock file.*mismatch

# Import errors
Cannot find module|ModuleNotFoundError|undefined: \w+

# Timeout
timeout|exceeded.*time limit|operation was canceled
```

### Confidence Levels

When matching patterns:

- **High confidence** (95%+): Exact tool name + known error format
  - Action: Haiku can auto-fix

- **Medium confidence** (70-90%): Error format matches but no explicit tool
  - Action: Haiku attempts, Sonnet verifies

- **Low confidence** (<70%): Ambiguous error message
  - Action: Escalate to Sonnet for analysis

---

## Summary Table

| Failure Type         | Auto-Fix Rate | Primary Model | Secondary Model |
| -------------------- | ------------- | ------------- | --------------- |
| Formatting           | 99%           | Haiku         | -               |
| Linting (with --fix) | 60-80%        | Haiku         | Sonnet          |
| Type Checking        | 20-30%        | Sonnet        | -               |
| Tests                | 5-10%         | Sonnet        | -               |
| Build                | 30-40%        | Sonnet        | Haiku           |
| Lock File            | 95%           | Haiku         | -               |
| Missing Deps         | 60-70%        | Haiku         | Sonnet          |
| Version Conflicts    | 30-40%        | Sonnet        | -               |
| Security             | 50-70%        | Haiku         | Sonnet          |
| Infrastructure       | 5%            | Sonnet        | -               |

**Overall Auto-Fix Rate**: ~60% of CI failures can be fixed autonomously

**Key Insight**: Mechanical issues (format, lint, locks) are highly auto-fixable. Logic issues (tests, types, builds) require human judgment.
