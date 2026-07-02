# CI Failure Analysis Examples

Real-world failure scenarios with analysis and resolution.

## Example 1: Formatting (Auto-Fix)

### Scenario
Prettier formatting issues on push.

### CI Log
```
Run Check formatting
[warn] src/index.ts
[warn] src/utils/helper.ts
[warn] Code style issues found. Run Prettier to fix.
Error: Process completed with exit code 1.
```

### Analysis & Fix
**Model**: Haiku (pattern match → auto-fix)

1. Detect: Log contains "prettier" + "Code style issues"
2. Verify config: `ls .prettierrc*`
3. Apply: `npx prettier --write .`
4. Confirm: `npx prettier --check .`


---

## Example 2: Linting + Type Errors (Mixed)

### CI Log
```
/src/api.ts
  15:10  error  'response' is assigned but never used  @typescript-eslint/no-unused-vars
  23:5   error  Missing return type on function        @typescript-eslint/explicit-function-return-type
  28:12  error  Unsafe assignment of an `any` value    @typescript-eslint/no-unsafe-assignment

✖ 5 problems (4 errors, 1 warning)
  2 errors potentially fixable with --fix
```

### Analysis & Fix
**Model**: Haiku for auto-fix, Sonnet for manual review

1. Run `npx eslint --fix .` → fixes 2 issues
2. For remaining 3: present options to user
   - Line 15: Remove unused var or use it?
   - Line 23: Add return type annotation
   - Line 28: Type the result properly


---

## Example 3: Test Failure (Logic Bug)

### CI Log
```
FAIL src/calculator.test.ts
  ● Calculator › calculateTotal › returns sum of array

    expect(received).toBe(expected)
    Expected: 15
    Received: 12

      22 |   it('returns sum of array', () => {
      23 |     const numbers = [3, 4, 5];
    > 24 |     expect(calculateTotal(numbers)).toBe(15);
```

### Analysis
**Model**: Sonnet (semantic understanding required)

1. Math check: 3 + 4 + 5 = 12 ≠ 15
2. Check recent diff:
   ```diff
   -  return numbers.reduce((sum, n) => sum + n, 0);
   +  return numbers.reduce((sum, n) => sum + n);  // Missing initial value!
   ```
3. Root cause: Without initial value 0, reduce uses first element as start

### Fix
```typescript
return numbers.reduce((sum, n) => sum + n, 0);  // Restore initial value
```


---

## Example 4: Lock File Mismatch (Auto-Fix)

### CI Log
```
npm ci
npm ERR! `npm ci` can only install packages when your package.json and package-lock.json are in sync.
npm ERR! Invalid: lock file's lodash@4.17.20 does not satisfy lodash@^4.17.21
```

### Analysis & Fix
**Model**: Haiku

1. Run `npm install`
2. Verify: `git diff package-lock.json`
3. Confirm: `npm ci` succeeds


---

## Example 5: Breaking Change (Upstream Dependency)

### CI Log
```
src/api.ts:15:23 - error TS2339: Property 'data' does not exist on type 'AxiosResponse'
src/api.ts:28:5 - error TS2554: Expected 2 arguments, but got 3.
```

### Analysis
**Model**: Sonnet

1. Check dependency changes: `axios: 0.27.2 → 1.0.0`
2. Research breaking changes in axios 1.0.0
3. Present migration options to user:
   - A) Migrate to 1.0.0 API
   - B) Downgrade temporarily


---

## Example 6: Missing Secret / Permission

### CI Log
```
##[error]No value for required secret 'NPM_TOKEN'.
Error: Resource not accessible by integration
```

### Analysis & Fix
**Model**: Sonnet

1. Identify: Secret `NPM_TOKEN` undefined
2. Surface workflow reference: `${{ secrets.NPM_TOKEN }}`
3. Remediation: "Add `NPM_TOKEN` in Settings → Secrets → Actions"

**No code changes** - configuration fix only.

---

## Example 7: Matrix Partial Failure

### CI Log
```
✔ test (node-version: 16, os: ubuntu-latest)
✗ test (node-version: 18, os: ubuntu-latest)
✔ test (node-version: 20, os: ubuntu-latest)

src/index.ts:12 - error TS2304: Cannot find name 'crypto'.
```

### Analysis
**Model**: Mixed

1. Parse matrix: Only Node 18 fails
2. Root cause: Node 18 lacks global `crypto` type
3. Fix: `import { randomUUID } from 'crypto'`
4. Rerun: `gh run rerun <id> --job "test (node-version: 18)"`

---

**Key Insight**: Mechanical issues (formatting, locks) resolve quickly and automatically. Logic issues (tests, breaking changes) require analysis and user input.
