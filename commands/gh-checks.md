---
allowed-tools: Bash
description: Review and fix GitHub Action check failures
---
# /gh-checks

Review GitHub Action checks and failures on the current branch and fix issues when possible.

## Usage

```bash
/gh-checks
```

## Behavior

1. **Check Branch Status**
   - Run: `git branch --show-current` to confirm current branch
   - Run: `git status` to see if there are uncommitted changes

2. **List GitHub Action Checks**
   - Run: `gh pr checks` (if PR exists) or `gh run list --branch $(git branch --show-current) --limit 5`
   - Show check names and their status (passing, failing, pending)

3. **Identify Failures**
   - For each failing check:
     - Get the run ID: `gh run list --branch <branch> --json databaseId,conclusion,name`
     - View failure logs: `gh run view <run-id> --log-failed`
   - Parse logs to identify root causes

4. **Categorize Issues**
   Common fixable issues:
   - **Formatting**: Run project formatter (prettier, black, gofmt, etc.)
   - **Linting**: Run linter and fix auto-fixable issues (eslint --fix, ruff check --fix, etc.)
   - **Type errors**: May require code changes
   - **Test failures**: Requires investigation
   - **Dependency issues**: May need updates to lock files

5. **Suggest/Apply Fixes**
   - For simple fixes (formatting, linting):
     - Show what will be run
     - Ask user for approval before executing
     - Apply fixes and show diff
   - For complex issues:
     - Explain the problem
     - Suggest potential fixes
     - **Don't overdo it** - consult user before major changes

6. **Re-run Checks (Optional)**
   - After fixes are committed and pushed: `gh run rerun <run-id>`
   - Or wait for automatic re-run on push

## Example Commands

```bash
# List recent workflow runs
gh run list --branch main --limit 5

# View specific run
gh run view 12345

# View only failed logs
gh run view 12345 --log-failed

# Re-run a specific run
gh run rerun 12345

# Check PR status (if PR exists)
gh pr checks
```

## Notes

- **Don't overdo it**: Simple fixes are okay (formatting, linting), but consult user before major changes
- Some failures may require discussion or design decisions
- Always show what changes will be made before applying them
- Consider if the failure is a legitimate issue vs. flaky test
