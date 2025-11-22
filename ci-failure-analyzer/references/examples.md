# CI Failure Analysis Examples

Real-world failure scenarios with complete analysis and resolution steps.

## Table of Contents

1. [Example 1: Simple Prettier Formatting](#example-1-simple-prettier-formatting)
2. [Example 2: Multiple ESLint + TypeScript Errors](#example-2-multiple-eslint--typescript-errors)
3. [Example 3: Test Failure with Assertion Mismatch](#example-3-test-failure-with-assertion-mismatch)
4. [Example 4: Dependency Lock File Mismatch](#example-4-dependency-lock-file-mismatch)
5. [Example 5: Breaking Change in Upstream Package](#example-5-breaking-change-in-upstream-package)
6. [Example 6: Flaky Test Detection](#example-6-flaky-test-detection)
7. [Example 7: Missing Secret / Permission](#example-7-missing-secret--permission)
8. [Example 8: Matrix Partial Failure](#example-8-matrix-partial-failure)

---

## Example 1: Simple Prettier Formatting

### Scenario

User pushes code and CI fails with formatting issues.

### CI Log Output

```
Run Check formatting
  npx prettier --check .

Checking formatting...
[warn] src/index.ts
[warn] src/utils/helper.ts
[warn] src/components/Button.tsx
[warn] Code style issues found in the above file(s). Run Prettier to fix.

Error: Process completed with exit code 1.
```

### Analysis

**Model**: Haiku 4.5 (straightforward pattern match)

**Detection**:

1. Log contains "prettier"
2. Exit code 1
3. Files listed with `[warn]` prefix
4. Message: "Run Prettier to fix"

**Categorization**: Formatting failure (auto-fixable)

**Root Cause**: Code doesn't match Prettier formatting rules

### Resolution Steps

**Step 1: Verify Tool Configuration** (Haiku)

```bash
# Check if prettier config exists
ls .prettierrc* prettier.config.*
```

Found: `.prettierrc`

**Step 2: Apply Auto-Fix** (Haiku)

```bash
npx prettier --write .
```

Output:

```
src/index.ts 150ms
src/utils/helper.ts 45ms
src/components/Button.tsx 87ms
```

**Step 3: Verify Fix** (Haiku)

```bash
git diff --stat
```

Output:

```
 src/index.ts              | 12 ++++++------
 src/utils/helper.ts       |  3 +--
 src/components/Button.tsx |  8 ++++----
 3 files changed, 11 insertions(+), 12 deletions(-)
```

**Step 4: Confirm** (Haiku)

```bash
npx prettier --check .
```

Output:

```
All matched files use Prettier code style!
```

### User Communication

```
I found Prettier formatting issues in 3 files:
- src/index.ts
- src/utils/helper.ts
- src/components/Button.tsx

Running: npx prettier --write .

✓ Prettier formatting applied successfully

Changed files:
 src/index.ts              | 12 ++++++------
 src/utils/helper.ts       |  3 +--
 src/components/Button.tsx |  8 ++++----

Next step: Commit these changes with /commit
```

### Time

- Detection: < 1 second
- Fix application: 2-3 seconds
- Total: < 5 seconds

### Cost

- Haiku tokens: ~500 (detection + execution)
- Cost: ~$0.001

---

## Example 2: Multiple ESLint + TypeScript Errors

### Scenario

User adds new TypeScript code with linting and type errors.

### CI Log Output

```
Run Lint
  npx eslint .

/Users/runner/work/project/src/api.ts
  15:10  error  'response' is assigned a value but never used  @typescript-eslint/no-unused-vars
  23:5   error  Missing return type on function                @typescript-eslint/explicit-function-return-type
  28:12  error  Unsafe assignment of an `any` value            @typescript-eslint/no-unsafe-assignment

/Users/runner/work/project/src/utils.ts
  42:1   error  'foo' is defined but never used                no-unused-vars
  55:3   warning  Unexpected console statement                 no-console

✖ 5 problems (4 errors, 1 warning)
  2 errors and 0 warnings potentially fixable with the `--fix` option.

Error: Process completed with exit code 1.
```

### Analysis

**Model**: Mixed (Haiku for auto-fix, Sonnet for manual fixes)

**Detection** (Haiku):

1. Log contains "eslint"
2. Error format: `file:line:col  level  message  rule`
3. Message indicates some are fixable with `--fix`

**Categorization**:

- **Auto-fixable** (2): no-unused-vars (remove), potentially others
- **Manual** (3): Type annotations, unsafe assignments

**Root Cause**: Code quality issues, some mechanical, some requiring judgment

### Resolution Steps

**Step 1: Apply Auto-Fix** (Haiku)

```bash
npx eslint --fix .
```

Output:

```
/Users/runner/work/project/src/api.ts
  15:10  error  'response' is assigned a value but never used  @typescript-eslint/no-unused-vars
  23:5   error  Missing return type on function                @typescript-eslint/explicit-function-return-type
  28:12  error  Unsafe assignment of an `any` value            @typescript-eslint/no-unsafe-assignment

✖ 3 problems (3 errors, 0 warnings)
```

**Result**: Fixed 2 problems (removed unused vars and console.log)

**Step 2: Analyze Remaining Errors** (Sonnet)

Read the affected file:

```typescript
// src/api.ts:15
const response = await fetch("/api/data"); // ← unused variable

// src/api.ts:23
async function fetchData(id: string) {
  // ← missing return type
  const data = await fetch(`/api/${id}`);
  return data.json();
}

// src/api.ts:28
const result: any = getConfig(); // ← unsafe any assignment
const config = result.data;
```

**Analysis** (Sonnet):

1. **Line 15**: `response` assigned but never used
   - **Fix**: Either use it or remove it
   - **Question**: Is this intended for future use?

2. **Line 23**: Missing return type
   - **Fix**: Add `: Promise<any>` or better, specific type
   - **Determination**: Needs to inspect what `data.json()` returns

3. **Line 28**: Unsafe `any` assignment
   - **Fix**: Type `result` properly or use `unknown`
   - **Question**: What is the actual type of `getConfig()`?

**Step 3: Interactive Fixes** (Sonnet guides, user decides)

**For Line 15 (unused variable)**:

```
I found an unused variable on line 15:
  const response = await fetch('/api/data');

This is likely a bug. Options:
A) Remove it (it's not being used)
B) Use the response (e.g., check status)
C) Keep it for future use (will need ESLint exception)

What would you like to do?
```

User response: "A - remove it"

**For Line 23 (missing return type)**:

```
Function fetchData is missing a return type on line 23.

The function returns data.json() which is Promise<any>.

I can add the return type:
  async function fetchData(id: string): Promise<any>

Or if you know the actual shape of the data:
  async function fetchData(id: string): Promise<DataType>

Should I:
A) Add Promise<any> (quick fix)
B) Show me the code so I can specify the correct type
C) Skip for now
```

User response: "A - add Promise<any>"

**For Line 28 (unsafe any)**:

```
Line 28 has an unsafe any assignment:
  const result: any = getConfig();

To fix this, I can:
A) Change to: const result = getConfig() as ConfigType;
B) Change to: const result: unknown = getConfig();
C) Open the file for you to review

What would you prefer?
```

User response: "A - use ConfigType"

**Step 4: Apply Manual Fixes** (Haiku executes)

```typescript
// Fix 1: Remove unused variable (line 15)
// Line removed

// Fix 2: Add return type (line 23)
async function fetchData(id: string): Promise<any> {
  const data = await fetch(`/api/${id}`);
  return data.json();
}

// Fix 3: Type the result (line 28)
const result = getConfig() as ConfigType;
const config = result.data;
```

**Step 5: Verify All Fixed** (Haiku)

```bash
npx eslint .
```

Output:

```
✓ No problems found
```

### User Communication

```
I found 5 ESLint issues. Here's what I did:

Auto-fixed (2 issues):
  ✓ Removed unused variable 'foo' (utils.ts:42)
  ✓ Removed console.log statement (utils.ts:55)

Manual fixes applied with your guidance (3 issues):
  ✓ Removed unused 'response' variable (api.ts:15)
  ✓ Added Promise<any> return type to fetchData (api.ts:23)
  ✓ Added type assertion for getConfig result (api.ts:28)

All ESLint errors resolved!

Changed files:
 src/api.ts   | 5 ++---
 src/utils.ts | 2 --

Next step: Commit with /commit
```

### Time

- Auto-fix: 3-5 seconds
- Manual analysis: 10-15 seconds
- User interaction: Variable (depends on response time)
- Total: ~30 seconds (excluding user think time)

### Cost

- Haiku: ~1000 tokens
- Sonnet: ~3000 tokens
- Total: ~$0.015

---

## Example 3: Test Failure with Assertion Mismatch

### Scenario

User refactors calculation logic, tests fail.

### CI Log Output

```
Run Tests
  npm test

 PASS  src/utils.test.ts
 FAIL  src/calculator.test.ts
  ● Calculator › calculateTotal › returns sum of array

    expect(received).toBe(expected)

    Expected: 15
    Received: 12

      22 |   it('returns sum of array', () => {
      23 |     const numbers = [3, 4, 5];
    > 24 |     expect(calculateTotal(numbers)).toBe(15);
         |                                     ^
      25 |   });
      26 |
      27 |   it('handles empty array', () => {

      at Object.<anonymous> (src/calculator.test.ts:24:37)

Test Suites: 1 failed, 1 passed, 2 total
Tests:       1 failed, 7 passed, 8 total
```

### Analysis

**Model**: Sonnet 4.5 (requires semantic understanding)

**Detection** (Sonnet):

1. Jest test failure
2. Assertion mismatch: Expected 15, Received 12
3. Test: `calculateTotal` with input `[3, 4, 5]`
4. Location: `calculator.test.ts:24`

**Categorization**: Test failure (logic issue)

**Root Cause Analysis** (Sonnet):

The test expects `calculateTotal([3, 4, 5])` to return 15.
But it returns 12.

Math check: 3 + 4 + 5 = 12

Wait, that's correct! So either:

1. The function is correct and test expectation is wrong (15 should be 12)
2. The function has a bug

Let's check recent changes:

```bash
git diff main -- src/calculator.ts
```

Output:

```diff
-export function calculateTotal(numbers: number[]): number {
-  return numbers.reduce((sum, n) => sum + n, 0);
-}
+export function calculateTotal(numbers: number[]): number {
+  return numbers.reduce((sum, n) => sum + n);  // ← Bug: missing initial value!
+}
```

**Aha!** The initial value `0` was removed. Without it, `reduce` uses the first element as the initial value:

- Start: `sum = 3` (first element)
- Iteration 1: `sum = 3 + 4 = 7`
- Iteration 2: `sum = 7 + 5 = 12`

Should be:

- Start: `sum = 0`
- Iteration 1: `sum = 0 + 3 = 3`
- Iteration 2: `sum = 3 + 4 = 7`
- Iteration 3: `sum = 7 + 5 = 15`

### Resolution Steps

**Step 1: Explain the Issue** (Sonnet)

```
Test failure in calculator.test.ts:24

The test expects calculateTotal([3, 4, 5]) to return 15, but it returns 12.

Root cause:
The recent change removed the initial value (0) from the reduce function.

In src/calculator.ts:
  return numbers.reduce((sum, n) => sum + n);  // Wrong!

Without an initial value, reduce uses the first element (3) as the starting point:
  3 + 4 + 5 = 12  (skips first element in accumulation)

With initial value 0:
  0 + 3 + 4 + 5 = 15  (correct)

Fix:
  return numbers.reduce((sum, n) => sum + n, 0);
```

**Step 2: Offer to Fix** (Sonnet)

```
Would you like me to restore the initial value in the reduce function?

This will fix the bug and make the test pass.
```

User: "Yes, please fix it"

**Step 3: Apply Fix** (Haiku executes, Sonnet directs)

```typescript
// src/calculator.ts
export function calculateTotal(numbers: number[]): number {
  return numbers.reduce((sum, n) => sum + n, 0); // ✓ Fixed: added initial value
}
```

**Step 4: Verify** (Haiku)

```bash
npm test -- calculator.test.ts
```

Output:

```
 PASS  src/calculator.test.ts
  Calculator
    calculateTotal
      ✓ returns sum of array (3 ms)
      ✓ handles empty array (1 ms)

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
```

### User Communication

```
Test failure analysis for calculator.test.ts:

Issue:
  calculateTotal([3, 4, 5]) returned 12 instead of 15

Root Cause:
  The reduce function is missing its initial value (0).
  Without it, reduce starts with the first element (3), giving: 3 + 4 + 5 = 12
  With initial 0, it correctly computes: 0 + 3 + 4 + 5 = 15

Fix Applied:
  ✓ Restored initial value: .reduce((sum, n) => sum + n, 0)

Verification:
  ✓ All tests in calculator.test.ts now pass

Changed files:
  src/calculator.ts | 2 +-

This was a logic bug introduced in a recent refactor.
```

### Time

- Log analysis: 5 seconds
- Code inspection: 5 seconds
- Root cause reasoning: 10 seconds
- Fix application: 2 seconds
- Verification: 5 seconds
- Total: ~27 seconds

### Cost

- Sonnet: ~2500 tokens (analysis + explanation)
- Haiku: ~500 tokens (execution)
- Total: ~$0.012

---

## Example 4: Dependency Lock File Mismatch

### Scenario

User updates package.json but forgets to update package-lock.json.

### CI Log Output

```
Run Install dependencies
  npm ci

npm ERR! code EUSAGE
npm ERR!
npm ERR! `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm ERR!
npm ERR! Invalid: lock file's lodash@4.17.20 does not satisfy lodash@^4.17.21

Error: Process completed with exit code 1.
```

### Analysis

**Model**: Haiku 4.5 (clear pattern, mechanical fix)

**Detection**:

1. "npm ci" command
2. Error: "package.json and package-lock.json... not in sync"
3. Specific mismatch: lodash@4.17.20 vs lodash@^4.17.21

**Categorization**: Dependency lock file mismatch (auto-fixable)

**Root Cause**: package.json was updated but lock file wasn't regenerated

### Resolution Steps

**Step 1: Verify the Mismatch** (Haiku)

```bash
# Check package.json
grep lodash package.json
```

Output:

```json
"lodash": "^4.17.21"
```

```bash
# Check package-lock.json
grep '"lodash"' package-lock.json | head -1
```

Output:

```json
"lodash": {
  "version": "4.17.20",
```

Confirmed: Versions don't match.

**Step 2: Regenerate Lock File** (Haiku)

```bash
npm install
```

Output:

```
added 1 package, changed 1 package, and audited 487 packages in 3s

found 0 vulnerabilities
```

**Step 3: Verify Changes** (Haiku)

```bash
git diff package-lock.json | head -20
```

Output:

```diff
       "node_modules/lodash": {
-        "version": "4.17.20",
-        "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.20.tgz",
-        "integrity": "sha512-PlhdFcillOINfeV7Ni6oF1TAEayyZBoZ8bcshTHqOYJYlrqzRK5hagpagky5o4HfCzzd1TRkXPMFq6cKk9rGmA=="
+        "version": "4.17.21",
+        "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
+        "integrity": "sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg=="
       },
```

**Step 4: Confirm Fix** (Haiku)

```bash
npm ci
```

Output:

```
added 487 packages in 5s
```

Success! No errors.

### User Communication

```
I found a lock file mismatch:

Issue:
  package.json requires lodash@^4.17.21
  package-lock.json has lodash@4.17.20

This happens when package.json is updated without regenerating the lock file.

Fix:
  Running: npm install

✓ Lock file regenerated successfully

Changed:
  lodash: 4.17.20 → 4.17.21

Verification:
  ✓ npm ci now succeeds

Changed files:
  package-lock.json | 6 +++---

Next step: Commit the updated lock file with /commit
```

### Time

- Detection: < 1 second
- Fix: 3-5 seconds (npm install)
- Verification: 5 seconds (npm ci)
- Total: ~10 seconds

### Cost

- Haiku only: ~600 tokens
- Cost: ~$0.002

---

## Example 5: Breaking Change in Upstream Package

### Scenario

Dependency update introduces breaking API changes.

### CI Log Output

```
Run Build
  npm run build

> project@1.0.0 build
> tsc

src/api.ts:15:23 - error TS2339: Property 'data' does not exist on type 'AxiosResponse<any, any>'.

15   const result = response.data.items;
                         ~~~~

src/api.ts:28:5 - error TS2554: Expected 2 arguments, but got 3.

28   axios.get('/api/users', config, timeout);
       ~~~~~~~~~

src/utils/http.ts:42:10 - error TS2304: Cannot find name 'AxiosRequestConfig'.

42   const config: AxiosRequestConfig = {
              ~~~~~~~~~~~~~~~~~~

Found 3 errors in 2 files.

Error: Process completed with exit code 2.
```

### Analysis

**Model**: Sonnet 4.5 (requires understanding breaking changes)

**Detection** (Sonnet):

1. TypeScript compilation errors
2. All related to axios types
3. Property missing, signature changed, type renamed

**Investigation** (Sonnet):

Check recent dependency changes:

```bash
git diff main -- package.json
```

Output:

```diff
-    "axios": "^0.27.2",
+    "axios": "^1.0.0",
```

Axios was updated from 0.x to 1.0.0 (major version bump = breaking changes)

**Research Breaking Changes** (Sonnet with WebFetch if available):

Axios 1.0.0 breaking changes:

1. Response structure changed: `response.data` still exists, but types changed
2. `axios.get()` now takes only 2 arguments (url, config), timeout moved into config
3. `AxiosRequestConfig` renamed to `AxiosRequestConfig<D>`

### Resolution Steps

**Step 1: Explain Breaking Changes** (Sonnet)

```
CI build failed due to breaking changes in axios 1.0.0.

Recent change:
  axios: 0.27.2 → 1.0.0 (major version update)

Breaking changes affecting your code:

1. src/api.ts:28 - axios.get() signature changed
   Old: axios.get(url, config, timeout)
   New: axios.get(url, config) // timeout goes in config

2. src/utils/http.ts:42 - Type renamed
   Old: AxiosRequestConfig
   New: AxiosRequestConfig<any> // Now generic

3. src/api.ts:15 - Type inference issue
   The response.data type may need explicit typing

Migration needed in 2 files.
```

**Step 2: Offer Migration Options** (Sonnet)

```
Would you like me to:

A) Migrate to axios 1.0.0 (fix the breaking changes)
B) Downgrade to axios 0.27.2 (revert for now)
C) Show me what needs to change first

Option A requires updating 3 locations in 2 files.
```

User: "A - migrate to 1.0.0"

**Step 3: Apply Migration** (Sonnet guides, Haiku executes)

**Fix 1: Update axios.get() call**

```typescript
// src/api.ts:28
// Before:
axios.get("/api/users", config, timeout);

// After:
axios.get("/api/users", {
  ...config,
  timeout,
});
```

**Fix 2: Update type import**

```typescript
// src/utils/http.ts:42
// Before:
const config: AxiosRequestConfig = {
  headers: { "Content-Type": "application/json" },
};

// After:
const config: AxiosRequestConfig<any> = {
  headers: { "Content-Type": "application/json" },
};
```

**Fix 3: Add explicit typing**

```typescript
// src/api.ts:15
// Before:
const result = response.data.items;

// After:
const result = (response.data as { items: any[] }).items;
// Or better, if you have the type:
const result = (response.data as ApiResponse).items;
```

**Step 4: Verify Build** (Haiku)

```bash
npm run build
```

Output:

```
> tsc

✓ Successfully compiled TypeScript
```

### User Communication

```
Build failure caused by axios 1.0.0 breaking changes.

Breaking Changes Detected:
  1. axios.get() signature changed (2 args instead of 3)
  2. AxiosRequestConfig is now generic
  3. Response typing needs adjustment

Migration Applied:

src/api.ts:
  ✓ Updated axios.get() call (line 28)
     timeout parameter moved into config object

  ✓ Added type assertion for response.data (line 15)

src/utils/http.ts:
  ✓ Updated AxiosRequestConfig to AxiosRequestConfig<any> (line 42)

Verification:
  ✓ TypeScript compilation succeeds
  ✓ Build passes

Changed files:
  src/api.ts        | 5 +++--
  src/utils/http.ts | 2 +-

Note: Axios 1.0.0 is a major update with multiple breaking changes.
Consider reviewing the full changelog for any other affected code.
```

### Time

- Detection: 5 seconds
- Breaking change research: 10-15 seconds
- Migration planning: 10 seconds
- Fix application: 5 seconds
- Verification: 10 seconds
- Total: ~45 seconds

### Cost

- Sonnet: ~4000 tokens (analysis + migration)
- Haiku: ~800 tokens (execution)
- Total: ~$0.020

---

## Example 6: Flaky Test Detection

### Scenario

Same test passes/fails intermittently on same commit.

### CI Log Output

```
Run Tests
  npm test

 FAIL  src/api.test.ts
  ● API Tests › fetches user data

    Timeout - Async operation did not complete within 5000ms

      45 |   it('fetches user data', async () => {
      46 |     const data = await fetchUser(123);
    > 47 |     expect(data.name).toBe('John Doe');
         |                      ^
      48 |   });

Test Suites: 1 failed, 2 passed, 3 total
Tests:       1 failed, 15 passed, 16 total
```

### Analysis

**Model**: Sonnet 4.5 (requires pattern analysis)

**Detection** (Sonnet):

1. Test timeout (not assertion failure)
2. Async operation exceeded 5000ms

**Historical Analysis** (Sonnet):

```bash
# Check recent run history
gh run list --workflow "CI" --limit 20 --json conclusion,name,headSha
```

Output shows:

- Run #45 (commit abc123): FAIL - "fetches user data" timeout
- Run #44 (commit abc123): SUCCESS - all tests pass
- Run #43 (commit def456): SUCCESS
- Run #42 (commit def456): FAIL - "fetches user data" timeout
- Run #41 (commit ghi789): SUCCESS

**Pattern**: Test fails intermittently, even on same commit!

This is a **flaky test**.

### Root Cause Investigation (Sonnet)

Read the test:

```typescript
// src/api.test.ts:45
it("fetches user data", async () => {
  const data = await fetchUser(123); // ← Makes real HTTP request?
  expect(data.name).toBe("John Doe");
});
```

Check implementation:

```typescript
// src/api.ts
export async function fetchUser(id: number) {
  const response = await axios.get(`https://api.example.com/users/${id}`);
  return response.data;
}
```

**Flakiness Causes**:

1. **Real Network Request**: Test makes actual HTTP call to external API
2. **No Timeout Control**: External API response time varies
3. **No Mocking**: Dependent on external service availability
4. **No Retry Logic**: Single attempt only

### Resolution Steps

**Step 1: Explain Flakiness** (Sonnet)

```
Flaky test detected: "fetches user data"

Evidence:
  - Fails with timeout (~40% of runs)
  - Same commit passes sometimes, fails others
  - No code changes between passing/failing runs

Root Cause:
  The test makes real HTTP requests to https://api.example.com
  External API response time varies:
    - Sometimes responds quickly (< 1s) ✓ pass
    - Sometimes slow or unavailable (> 5s) ✗ fail

This creates unreliable CI.
```

**Step 2: Suggest Fixes** (Sonnet)

```
Recommended fixes (in order of preference):

1. Mock the HTTP call (best practice)
   - Fast, reliable, no external dependencies
   - Tests your code, not the external API

2. Increase timeout (temporary workaround)
   - Reduces failures but doesn't solve root cause
   - Still dependent on external service

3. Add retry logic (mitigation)
   - Reduces flakiness but test still slow
   - Masks the real problem

Which approach would you like?
```

User: "1 - mock the HTTP call"

**Step 3: Apply Mocking Fix** (Sonnet guides)

```typescript
// src/api.test.ts
import axios from "axios";
import { fetchUser } from "./api";

// Mock axios
jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe("API Tests", () => {
  it("fetches user data", async () => {
    // Setup mock response
    mockedAxios.get.mockResolvedValue({
      data: {
        id: 123,
        name: "John Doe",
      },
    });

    // Test
    const data = await fetchUser(123);
    expect(data.name).toBe("John Doe");

    // Verify
    expect(mockedAxios.get).toHaveBeenCalledWith(
      "https://api.example.com/users/123",
    );
  });
});
```

**Step 4: Verify Fix** (Haiku)

```bash
# Run test multiple times to verify consistency
for i in {1..5}; do npm test -- api.test.ts; done
```

Output:

```
Run 1: PASS (125ms)
Run 2: PASS (118ms)
Run 3: PASS (122ms)
Run 4: PASS (119ms)
Run 5: PASS (121ms)
```

All pass, all fast!

### User Communication

```
Flaky test detected: "fetches user data"

Analysis:
  - Test fails intermittently with timeout
  - Same commit sometimes passes, sometimes fails
  - Root cause: Real HTTP requests to external API

Pattern:
  Run #45 (commit abc123): FAIL ✗
  Run #44 (commit abc123): PASS ✓  ← Same commit!
  Run #43 (commit def456): PASS ✓
  Run #42 (commit def456): FAIL ✗  ← Same commit!

Solution Applied:
  ✓ Mocked axios HTTP calls
  ✓ Test now uses predictable mock data
  ✓ No external dependencies

Benefits:
  - Fast: 120ms (was 5000ms+ on timeout)
  - Reliable: Consistent results every run
  - Isolated: Tests your code, not external APIs

Verification:
  ✓ Ran test 5 times, all passed consistently

Changed files:
  src/api.test.ts | 12 ++++++++++--

Note: Consider mocking all external API calls in tests to prevent future flakiness.
```

### Time

- Flakiness detection: 15 seconds
- Historical analysis: 10 seconds
- Root cause investigation: 15 seconds
- Fix application: 10 seconds
- Verification: 30 seconds (5 runs)
- Total: ~80 seconds

### Cost

- Sonnet: ~3500 tokens (analysis + fix)
- Haiku: ~600 tokens (execution)
- Total: ~$0.017

---

## Summary Table

| Example                | Type                | Model  | Auto-Fix      | Time | Cost   |
| ---------------------- | ------------------- | ------ | ------------- | ---- | ------ |
| 1. Prettier            | Formatting          | Haiku  | Yes (100%)    | ~5s  | $0.001 |
| 2. ESLint + TypeScript | Linting + Types     | Mixed  | Partial (40%) | ~30s | $0.015 |
| 3. Test Failure        | Logic Bug           | Sonnet | No            | ~27s | $0.012 |
| 4. Lock File           | Dependency          | Haiku  | Yes (100%)    | ~10s | $0.002 |
| 5. Breaking Change     | Dependency          | Sonnet | No            | ~45s | $0.020 |
| 6. Flaky Test          | Test Infrastructure | Sonnet | No            | ~80s | $0.017 |
| **7. Missing Secret** ⭐ | **Secrets/Permissions** | **Sonnet** | **No** | **~20s** | **$0.010** |
| **8. Matrix Partial** ⭐ | **Matrix Failure** | **Mixed** | **Yes (targeted)** | **~35s** | **$0.018** |

**Key Insights**:

1. **Mechanical issues** (formatting, lock files) are fast and cheap (Haiku-driven)
2. **Logic issues** (tests, breaking changes) require analysis (Sonnet-driven)
3. **Infrastructure issues** (secrets, permissions, matrix) require non-code remediation
4. **Mixed scenarios** benefit from hybrid approach
5. **Auto-fix success** correlates with issue complexity
6. **User interaction** is valuable for non-obvious fixes

**Average Success Metrics**:

- Auto-fixable issues: < 10 seconds, < $0.002
- Manual issues with guidance: < 60 seconds, < $0.020
- Overall: ~60% of CI failures can be auto-fixed

---

## Example 7: Missing Secret / Permission

### Scenario

Deployment job pushes to npm but `NPM_TOKEN` secret is missing.

### CI Log Output

```
Run Publish package
  npm publish

Error: Process completed with exit code 1.
npm ERR! code E403
npm ERR! Unable to authenticate, need: Basic realm="GitHub Package Registry"

##[error]No value for required secret 'NPM_TOKEN'.
Error: Resource not accessible by integration
```

### Analysis

**Model**: Sonnet (needs configuration reasoning)

1. Logs explicitly mention missing secret `NPM_TOKEN`.
2. Exit code 403 indicates authentication failure.
3. Step name `Publish package` corresponds to workflow block:
   ```yaml
   - name: Publish package
     env:
       NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
     run: npm publish
   ```

### Resolution Steps

1. **Confirm Secret Usage** (Haiku)
   - Surface YAML snippet referencing `secrets.NPM_TOKEN`.
2. **Explain Root Cause** (Sonnet)
   - “The repository/org secret `NPM_TOKEN` is not defined or lacks required scope.”
3. **Provide Remediation Guidance** (Sonnet)
   - Add secret via `Settings → Secrets and variables → Actions → New repository secret`.
   - Ensure token has `publish` scope on npm (or GitHub Packages).
4. **Advise Rerun** (Haiku)
   - After secret is added, rerun the single job: `gh run rerun <run-id> --job publish`.

### Communication Snippet

```
Permission failure in job “Publish package”.

Root cause:
- Workflow expects secrets.NPM_TOKEN but it is undefined.
- npm publish exits 403 due to missing token.

Action items:
1. Create repository/org secret `NPM_TOKEN` with npm publish scope.
2. Rerun job via `gh run rerun <id> --job 'Publish package'`.

No code changes applied.
```

---

## Example 8: Matrix Partial Failure

### Scenario

Matrix job runs tests on Node 16, 18, and 20. Only Node 18 exits with TypeScript compile error.

### CI Log Output

```
Run Test (node-version: 18, os: ubuntu-latest)
  npm run test

> project@1.0.0 test
> tsc && jest

src/index.ts:12:5 - error TS2304: Cannot find name 'crypto'.

12     crypto.randomUUID();
       ~~~~~~

Error: Process completed with exit code 2.
```

Other matrix children:

```
✔ test (node-version: 16, os: ubuntu-latest)
✔ test (node-version: 20, os: ubuntu-latest)
```

### Analysis

**Model**: Mixed

1. Use `gh run view <run-id> --json jobs --jq '.jobs[] | {name, conclusion}'` to list matrix results.
2. Only Node 18 job failed; same commit passes on Node 20, so failure is runtime-specific.
3. TypeScript error referencing `crypto.randomUUID()` implies Node 18 lacks global types (needs `dom` lib or polyfill).

### Resolution Steps

1. **Report Matrix Summary** (Sonnet)
   - “Matrix summary: Node16 ✅, Node18 ❌ (TS2304), Node20 ✅.”
2. **Identify Fix Options** (Sonnet)
   - Option A: Add polyfill import for Node 18 (e.g., `import { randomUUID } from 'crypto'`).
   - Option B: Drop Node 18 support if no longer required.
3. **Offer Targeted Commands** (Haiku)
   - Reproduce locally: `nvm use 18 && npm run test`.
   - Once fixed, rerun only the failing job: `gh run rerun <run-id> --job "test (node-version: 18, os: ubuntu-latest)"`.

### Communication Snippet

```
Matrix result:
- Node16: pass
- Node18: fail (TS2304 crypto.randomUUID undefined)
- Node20: pass

Cause:
Node 18’s type definitions don’t expose global crypto. Import it explicitly or guard the call.

Suggested fix:
```

```typescript
import { randomUUID } from "crypto";

export function makeId() {
  return randomUUID();
}
```

```
Note: If you can't reproduce locally with Node 18, you can also rerun just the failing job in CI to inspect logs more carefully—sometimes the issue appears only in CI's environment.

After patching, rerun only the failing matrix child.
```
