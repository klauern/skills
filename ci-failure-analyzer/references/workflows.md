# CI Failure Analysis Workflows

This document provides detailed step-by-step workflows for analyzing and fixing different types of CI failures.

## Table of Contents

- [Standard Analysis Workflow](#standard-analysis-workflow)
- [Single Failure Workflow](#single-failure-workflow)
- [Multiple Failure Workflow](#multiple-failure-workflow)
- [Test Failure Workflow](#test-failure-workflow)
- [Dependency Failure Workflow](#dependency-failure-workflow)
- [Flaky Test Workflow](#flaky-test-workflow)
- [Model Strategy by Phase](#model-strategy-by-phase)
- [Troubleshooting](#troubleshooting)

---

## Standard Analysis Workflow

This is the default workflow for analyzing CI failures.

### Phase 1: Context Detection

**Goal**: Understand the current git and PR context

**Model**: Haiku 4.5 (fast I/O operations)

**Steps**:

1. **Verify Git Status**
   ```bash
   git status
   ```
   - Check for uncommitted changes
   - Ensure working directory is clean

2. **Get Current Branch**
   ```bash
   git branch --show-current
   ```
   - Needed for branch-based check queries

3. **Check PR Existence**
   ```bash
   gh pr view --json number,title,state 2>/dev/null
   ```
   - Determines if we use PR-based or branch-based queries
   - PR context provides better check information

**Output**: Branch name, PR number (if exists), clean/dirty status

---

### Phase 2: List Failing Checks

**Goal**: Identify all failing CI checks

**Model**: Haiku 4.5 (command execution and parsing)

**Steps**:

1. **If PR Exists**:
   ```bash
   gh pr checks
   ```
   - Shows check name, status, elapsed time
   - More reliable than branch-based queries

2. **If No PR (Branch-Based)**:
   ```bash
   gh run list --branch $(git branch --show-current) --limit 5 --json databaseId,conclusion,name,status
   ```
   - Lists recent workflow runs
   - Filter for `conclusion: "failure"`

3. **Parse Results**:
   - Extract failing check names
   - Get run IDs for log retrieval
   - Note check status (in_progress, completed, etc.)

**Output**: List of failing checks with run IDs

**Edge Cases**:
- No checks found: May be still queued or not triggered
- All checks passing: Nothing to analyze
- Checks in progress: Wait or analyze completed ones

---

### Phase 3: Retrieve Failure Logs

**Goal**: Download logs for failing checks

**Model**: Haiku 4.5 (file retrieval)

**Steps**:

1. **For Each Failing Check**:
   ```bash
   gh run view <run-id> --log-failed
   ```
   - Gets only failed job logs (not entire run)
   - Output can be large (thousands of lines)

2. **Log Storage**:
   - Keep logs in memory for parsing
   - Or write to temp files if very large

3. **Verification**:
   - Check if logs are available (may not be for very recent runs)
   - Handle truncated logs gracefully

**Output**: Raw log content for each failure

**Edge Cases**:
- Logs not available yet: "Logs are not available yet"
- Very large logs: May be truncated by gh CLI
- Multiple job failures: Need to retrieve each separately

---

### Phase 4: Analyze Root Causes

**Goal**: Parse logs and identify failure types

**Model**: Sonnet 4.5 (complex analysis and reasoning)

**Steps**:

1. **Extract Error Messages**:
   - Use regex patterns for common error formats
   - Identify stack traces
   - Find file paths and line numbers
   - See [log-parsing.md](log-parsing.md) for patterns

2. **Categorize Failures**:
   - Formatting: Prettier, Black, gofmt, etc.
   - Linting: ESLint, Ruff, Clippy, etc.
   - Type checking: TypeScript, mypy, etc.
   - Tests: Unit, integration, E2E failures
   - Build: Compilation, bundling errors
   - Dependencies: Lock file mismatches, conflicts
   - Infrastructure: Timeouts, rate limits
   - See [failure-patterns.md](failure-patterns.md) for complete taxonomy

3. **Determine Fixability**:
   - **Auto-fixable**: Formatting, linting with --fix, lock files
   - **Manual**: Type errors, test logic, breaking changes
   - **Investigation needed**: Infrastructure, flaky tests

4. **Identify Tool to Use**:
   - Detect which formatter/linter is needed
   - See [tool-detection.md](tool-detection.md) for detection logic

**Output**: Categorized failures with fix strategies

**Reasoning Tasks** (why Sonnet):
- Ambiguous error messages require interpretation
- Correlating multiple related failures
- Assessing whether issue is code vs. environment
- Determining confidence in proposed fix

---

### Phase 5: Apply Fix Strategy

**Goal**: Fix issues or guide user to fix them

**Model**: Mixed (Haiku for execution, Sonnet for decisions)

#### For Auto-Fixable Issues

**Model**: Haiku 4.5 (command execution)

1. **Show Intent**:
   ```
   I found formatting issues that can be auto-fixed.
   Running: npx prettier --write .
   ```

2. **Apply Fix**:
   - Run the formatter/linter command
   - Capture output

3. **Verify Fix**:
   ```bash
   git diff
   ```
   - Show what changed
   - Ensure no unexpected modifications

4. **Stage Changes** (if appropriate):
   ```bash
   git add -u
   ```

**Auto-Fix Examples**:
```bash
# Prettier
npx prettier --write .

# Black
black .

# ESLint
npx eslint --fix .

# Ruff
ruff check --fix .

# gofmt
gofmt -w .

# Lock file regeneration
npm ci
poetry lock --no-update
```

#### For Manual Issues

**Model**: Sonnet 4.5 (explanation and guidance)

1. **Explain the Issue**:
   - What failed and why
   - Show relevant error messages
   - Point to specific files and line numbers

2. **Suggest Fix Approach**:
   - Type errors: "Add type annotation for parameter 'x'"
   - Test failures: "The test expects 5 but got 3. Check the calculation in `calculateTotal`"
   - Breaking changes: "The API changed from `getData()` to `fetchData()`. Update all calls."

3. **Provide Context**:
   - Link to relevant documentation
   - Show code snippets that need changing
   - Explain trade-offs if multiple approaches exist

4. **Ask User**:
   - "Would you like me to make these changes?"
   - "Should I open the file for you to edit?"

**Manual Fix Examples**:
- Type errors requiring code changes
- Test logic failures
- API breaking changes
- Complex refactoring

---

### Phase 6: Optional Re-run

**Goal**: Re-trigger CI after fixes

**Model**: Haiku 4.5 (command execution)

**Steps**:

1. **Ask User**:
   ```
   Fixes have been applied. Would you like me to re-run the CI checks?
   ```

2. **If Yes**:
   ```bash
   gh run rerun <run-id>
   ```

3. **Monitor** (optional):
   ```bash
   gh run watch <run-id>
   ```
   - Real-time status updates
   - Can be slow, user may prefer to check later

**Note**: Only re-run if:
- Fixes were actually applied
- User confirms
- Not too many failures (avoid wasting CI resources)

---

## Single Failure Workflow

**Scenario**: One check is failing, others pass or not run yet

**Optimization**: Faster, more focused analysis

### Steps

1. **Context Detection** (Haiku)
   - Same as standard workflow

2. **Identify Single Failure** (Haiku)
   - Get run ID for the failing check

3. **Retrieve Logs** (Haiku)
   - `gh run view <run-id> --log-failed`

4. **Quick Categorization** (Haiku if pattern matches, otherwise Sonnet)
   - Match against known patterns in [failure-patterns.md](failure-patterns.md)
   - If clear match (e.g., "prettier" in output): Haiku can handle
   - If ambiguous: Escalate to Sonnet

5. **Apply Fix** (Haiku or Sonnet based on fix type)
   - Auto-fix: Haiku executes
   - Manual: Sonnet explains

6. **Verify and Optionally Re-run** (Haiku)

**Model Strategy**:
- Try Haiku first for pattern matching
- Escalate to Sonnet only if categorization is uncertain
- Most single formatting/linting failures can be handled entirely with Haiku

**Time Savings**: ~50% faster for simple cases

---

## Multiple Failure Workflow

**Scenario**: Multiple checks failing (different jobs or cascading failures)

**Challenge**: Prioritize fixes, avoid fixing symptoms of root cause

### Steps

1. **Context Detection** (Haiku)
   - Same as standard workflow

2. **List All Failures** (Haiku)
   - Get run IDs for all failing checks

3. **Retrieve All Logs** (Haiku, parallel if possible)
   - Fetch logs for all failures simultaneously
   - May be large volume of data

4. **Correlate Failures** (Sonnet - critical reasoning task)
   - Identify if failures are independent or related
   - Detect root cause vs. symptoms
   - Example: Build failure causes test job to fail → Fix build first
   - Prioritize by impact: Build > Tests > Linting > Formatting

5. **Create Fix Plan** (Sonnet)
   - Order fixes by dependency
   - Group related fixes
   - Example priority order:
     1. Dependency issues (affects everything)
     2. Build failures (blocks tests)
     3. Type errors (blocks compilation)
     4. Test failures (business logic)
     5. Linting (code style)
     6. Formatting (cosmetic)

6. **Apply Fixes Incrementally** (Mixed)
   - Fix highest priority first
   - Verify after each category
   - Re-assess if lower-priority failures resolved themselves

7. **Batch Re-run** (Haiku)
   - Re-run once after all fixes applied
   - Avoid multiple re-runs (wastes CI resources)

**Model Strategy**:
- Sonnet is critical for failure correlation
- Haiku handles the mechanical fixes
- Sonnet makes strategic decisions on fix order

**Key Insight**: Fixing root cause often resolves cascade of symptoms

---

## Test Failure Workflow

**Scenario**: Unit, integration, or E2E tests failing

**Challenge**: Tests can fail for many reasons, need to understand semantics

### Steps

1. **Context Detection** (Haiku)

2. **Retrieve Test Logs** (Haiku)

3. **Parse Test Output** (Sonnet - requires understanding test semantics)
   - **Extract**:
     - Failing test names
     - Assertion failures (expected vs. actual)
     - Stack traces
     - Setup/teardown errors
   - **Categorize**:
     - Assertion failures: Logic bug
     - Timeout: Performance or infinite loop
     - Setup error: Test infrastructure issue
     - TypeError: Missing mocks or test data

4. **Analyze Test Code** (Sonnet)
   - Read the failing test file
   - Understand what the test is checking
   - Identify what changed recently (git diff)

5. **Correlate with Recent Changes** (Sonnet)
   ```bash
   git diff main -- <test-related-files>
   ```
   - See what code changed that might affect test
   - Check if test itself was modified

6. **Determine Fix Approach** (Sonnet)
   - **Simple assertion update**: Test expectations out of sync
   - **Logic bug**: Code change broke behavior
   - **Test bug**: Test itself is wrong
   - **Infrastructure**: Test environment issue

7. **Provide Debugging Guidance** (Sonnet)
   - Point to specific test and line number
   - Show expected vs. actual values
   - Suggest what to investigate
   - Offer to run test locally (if applicable)

8. **Fix if Clear** (Sonnet for code changes)
   - Update test expectations if trivial
   - Fix obvious logic bugs
   - **Consult user for non-obvious changes**

**Model Strategy**:
- Sonnet handles entire workflow (tests require semantic understanding)
- Only use Haiku for log retrieval
- Test failures rarely have mechanical fixes

**User Involvement**: High - tests often require business logic understanding

---

## Dependency Failure Workflow

**Scenario**: Lock file out of sync, version conflicts, missing packages

**Optimization**: Often auto-fixable with lock file regeneration

### Steps

1. **Context Detection** (Haiku)

2. **Retrieve Logs** (Haiku)

3. **Categorize Dependency Issue** (Haiku if pattern clear, Sonnet if ambiguous)
   - **Lock file mismatch**: `package-lock.json` out of sync
   - **Version conflict**: Multiple packages need incompatible versions
   - **Missing package**: Import found in code but not in dependencies
   - **Audit failure**: Vulnerable dependency detected

4. **Attempt Auto-Fix** (Haiku)

   **Lock file mismatch**:
   ```bash
   # npm
   npm ci

   # yarn
   yarn install --frozen-lockfile

   # pnpm
   pnpm install --frozen-lockfile

   # poetry
   poetry lock --no-update

   # cargo
   cargo update
   ```

   **Missing package** (if obvious):
   ```bash
   npm install <package>
   poetry add <package>
   go get <package>
   ```

   **Audit failure** (minor):
   ```bash
   npm audit fix
   ```

5. **Verify Fix** (Haiku)
   ```bash
   git diff package-lock.json
   ```
   - Ensure reasonable changes
   - Check if major version changes occurred

6. **If Version Conflict** (Sonnet - requires reasoning)
   - Analyze which packages conflict
   - Check if resolution is possible
   - Suggest version constraints
   - May require user decision on which version to prioritize

7. **If Breaking Change** (Sonnet)
   - Identify what API changed
   - Find all usage locations
   - Suggest migration path
   - See [Breaking Change Detection](#breaking-change-detection)

**Model Strategy**:
- Haiku for simple lock file regeneration
- Sonnet for conflicts and breaking changes
- Most dependency issues can be Haiku-driven

**Auto-Fix Rate**: High (~70-80% of dependency issues)

---

## Flaky Test Workflow

**Scenario**: Test passes sometimes, fails other times

**Challenge**: Hard to reproduce, requires pattern analysis

### Steps

1. **Detect Flakiness** (Sonnet - requires historical analysis)
   - Check recent run history:
     ```bash
     gh run list --workflow <workflow-name> --limit 20
     ```
   - Look for same test passing/failing on same commit
   - Identify pattern: Always fails? Random? Time-based?

2. **Categorize Flakiness Type** (Sonnet)
   - **Timing issues**: Race conditions, timeouts
   - **External dependencies**: API calls, database state
   - **Test order dependencies**: Tests not isolated
   - **Environment variability**: CI-specific conditions
   - **Random data**: Non-deterministic test inputs

3. **Provide Investigation Guidance** (Sonnet)
   - Suggest debugging approaches
   - Recommend adding logging
   - Propose test isolation improvements
   - Suggest retry strategies (last resort)

4. **Quick Mitigations** (Haiku for execution, Sonnet for strategy)
   - Add `jest.retries(3)` or equivalent
   - Increase timeouts
   - Add wait/sleep statements (not ideal, but pragmatic)
   - Mock external dependencies

5. **Long-Term Fix Recommendations** (Sonnet)
   - Improve test isolation
   - Use deterministic random seeds
   - Mock time-dependent code
   - Reduce test order dependencies

**Model Strategy**:
- Sonnet drives entire workflow
- Flaky tests require deep reasoning about test behavior
- Historical pattern analysis is key

**Auto-Fix Rate**: Low (~10%) - mostly mitigations, not true fixes

**User Involvement**: High - flaky tests often indicate design issues

---

## Breaking Change Detection

**Sub-workflow**: Handling upstream dependency breaking changes

### Steps

1. **Identify Breaking Change** (Sonnet)
   - Dependency updated in recent commits or CI
   - Error messages reference external package APIs
   - Method/function signatures changed

2. **Check Changelog** (Sonnet with WebFetch if available)
   - Find package's GitHub releases or CHANGELOG
   - Look for migration guides
   - Identify specific API changes

3. **Find All Usage Locations** (Haiku)
   ```bash
   rg "oldMethodName" --type ts
   ```
   - Search codebase for affected calls
   - List files needing updates

4. **Assess Migration Scope** (Sonnet)
   - Simple rename? Auto-fixable
   - Parameter changes? Need careful review
   - Architectural changes? Major refactor needed

5. **Provide Migration Plan** (Sonnet)
   - Explain what changed and why
   - Show before/after examples
   - Suggest systematic approach
   - Estimate complexity

6. **Offer to Apply Simple Migrations** (Haiku for execution)
   - If just renames, can do automatically
   - If parameter reordering, can do with user approval
   - If complex, guide user through manual process

**Model Strategy**:
- Sonnet analyzes changelogs and assesses impact
- Haiku searches codebase and applies mechanical changes
- Sonnet provides strategic migration guidance

---

## Model Strategy by Phase

Summary of when to use Haiku vs. Sonnet across all workflows:

### Haiku 4.5 Phases

1. **Context Detection** - Git/PR status checks
2. **Log Retrieval** - Downloading failure logs
3. **Pattern Matching** - Checking against known error patterns
4. **Tool Execution** - Running formatters, linters, lock file updates
5. **Simple Categorization** - When error type is clear from output
6. **File Operations** - Reading/writing files, git operations
7. **Verification** - Checking results after fixes applied

**Cost**: ~$0.004 per workflow (typical)

### Sonnet 4.5 Phases

1. **Root Cause Analysis** - Understanding why failure occurred
2. **Failure Correlation** - Linking related failures
3. **Test Semantics** - Understanding what tests are checking
4. **Breaking Change Analysis** - Assessing dependency update impacts
5. **Fix Strategy** - Deciding approach for complex issues
6. **Code Reasoning** - Understanding business logic
7. **Natural Language Explanation** - Explaining to users
8. **Risk Assessment** - Evaluating safety of automated fixes
9. **Prioritization** - Determining fix order for multiple failures

**Cost**: ~$0.15 per workflow (typical)

### Decision Tree: Haiku or Sonnet?

```
Is this a known pattern with clear signature?
├─ Yes → Haiku
└─ No → Sonnet

Is this purely I/O or command execution?
├─ Yes → Haiku
└─ No → Is reasoning required?
    ├─ Yes → Sonnet
    └─ No → Haiku

Is this a test or logic-related failure?
└─ Yes → Sonnet (tests need semantic understanding)

Is this formatting or linting?
└─ Yes → Haiku (mechanical fix)

Multiple failures needing prioritization?
└─ Yes → Sonnet (strategic reasoning)
```

### Hybrid Approach

Many workflows use both:

1. **Haiku**: Fetch logs
2. **Sonnet**: Analyze and plan
3. **Haiku**: Execute fixes
4. **Sonnet**: Verify results and explain

**Optimal balance**: ~70% Haiku, ~30% Sonnet by token usage

---

## Troubleshooting

### "No failing checks found"

**Symptoms**: Workflow reports no failures but user says CI is failing

**Diagnosis**:
1. Check if on correct branch: `git branch --show-current`
2. Verify PR exists: `gh pr view`
3. Check if checks are still queued: `gh run list --limit 10`

**Solutions**:
- Switch to correct branch
- Wait for checks to start
- Create PR if working with branch-based checks

---

### "Cannot retrieve logs"

**Symptoms**: `gh run view --log-failed` returns empty or error

**Diagnosis**:
1. Check run status: May still be in progress
2. Verify permissions: `gh auth status`
3. Check run ID: May be incorrect

**Solutions**:
- Wait for run to complete
- Re-authenticate: `gh auth login`
- Use `gh run list` to get correct run ID

---

### "Auto-fix didn't resolve failure"

**Symptoms**: Applied formatter/linter but CI still fails

**Diagnosis**:
1. Check if all issues were auto-fixable
2. Verify formatter config matches CI
3. Ensure no additional manual fixes needed

**Solutions**:
- Review remaining errors in log
- Check for CI-specific configuration
- Apply manual fixes for non-auto-fixable issues

---

### "Too many failures to handle"

**Symptoms**: 10+ different checks failing

**Diagnosis**:
1. Likely root cause affecting many checks
2. May be environment or setup issue
3. Could be major breaking change

**Solutions**:
- Identify common root cause (Sonnet analysis)
- Fix highest priority failure first
- Consider if PR is too large (split into smaller changes)

---

### "Flaky test keeps failing"

**Symptoms**: Same test passes locally but fails in CI

**Diagnosis**:
1. Environment differences (CI vs. local)
2. Timing issues (CI may be slower/faster)
3. Test order dependencies
4. External dependencies

**Solutions**:
- Add logging to understand failure
- Increase timeouts
- Improve test isolation
- Mock external dependencies
- See [Flaky Test Workflow](#flaky-test-workflow)

---

## Examples

For complete real-world examples with full logs and step-by-step resolution, see [examples.md](examples.md).

Quick reference:
- **Example 1**: Simple Prettier formatting failure (Haiku-driven)
- **Example 2**: Multiple ESLint + TypeScript errors (Mixed)
- **Example 3**: Test failure with assertion mismatch (Sonnet-driven)
- **Example 4**: Dependency lock file mismatch (Haiku-driven)
- **Example 5**: Breaking change in upstream package (Sonnet-driven)
- **Example 6**: Flaky test detection and mitigation (Sonnet-driven)
