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

1. **Check Branch & Workspace**
   - `git status` to detect dirty state and warn if unrelated changes exist
   - `git branch --show-current` to include branch name in the summary
   - If on `main`/`master`, caution before applying fixes directly

2. **Determine PR vs. Branch Context**
   - If a PR exists: `gh pr view --json number,title` then `gh pr checks`
   - Otherwise: `gh run list --branch $(git branch --show-current) --limit 5 --json databaseId,headBranch,status,conclusion`
   - Handle “no runs found” by explaining workflow triggers that must fire

3. **Collect Logs (Matrix-Aware)**
   - For each failing check:
     - Gather run/job metadata: `gh run view <run-id> --json jobs`
     - Download failed logs per job/matrix child: `gh run view <run-id> --job "<job-name>" --log-failed`
   - Note matrix parameters (e.g., `node-version: 18`) in the eventual report

4. **Categorize Failures**
   - Match logs against known signatures (formatting, linting, type, tests, dependency, secrets/permissions, cache/artifacts, infrastructure)
   - Distinguish primary root causes from downstream jobs blocked by `needs`
   - Record confidence (High/Med/Low) for each diagnosis

5. **Apply Guarded Fixes**
   - Auto-run without prompt:
     - Formatters (prettier, black, gofumpt, rustfmt)
     - Safe lint fixes (`eslint --fix`, `ruff check --fix`, etc.)
     - Lock-file sync commands (`npm install`, `poetry lock --no-update`, `cargo update`)
   - For interactive/unsafe work (type changes, tests, builds, secrets, workflow edits):
     - Present options and await user approval
     - Never modify secrets or workflow YAML unless explicitly asked
   - Always echo the exact command before execution and show `git diff --stat` afterward

6. **Summarize Findings**
   - Produce a structured summary including:
     - Branch/PR info and failing job names (with matrix axes)
     - Root cause + confidence per job
     - Commands executed vs. pending actions
     - Next steps (manual changes, reruns, secret updates)

7. **Offer Targeted Re-runs**
   - If fixes were applied, ask whether to rerun only the remediated job: `gh run rerun <run-id> --job "<job-name>"`
   - Otherwise, note that CI will rerun after the next push

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

- **Don't overdo it**: Simple fixes are okay (formatting, linting, lock files), but consult the user before modifying logic, tests, or workflows.
- **Surface context**: Always describe the failing job(s), category, and confidence before proposing fixes.
- **Show commands first**: Echo the exact formatter/linter command and scope, then show `git diff` output.
- **Highlight non-code issues**: When failures stem from secrets, permissions, caches, or infrastructure, focus on guidance rather than edits.

## Edge Cases & Tips

- **No PR yet**: Explain that `gh pr checks` has no data; rely on `gh run list` and remind the user that opening a PR yields richer status output.
- **Multiple recent runs**: Default to the latest concluded run but mention other failing runs for context.
- **Logs unavailable**: If `gh run view --log-failed` says logs are missing, wait or notify the user to rerun once logs are ready.
- **Matrix jobs**: Report failing axis values explicitly and avoid rerunning the full matrix unless asked.
- **Secrets/permissions**: Detect `Resource not accessible by integration` or missing secret names and direct the user to update GitHub secrets instead of guessing values. See [Secrets & Permissions Workflow](../ci-failure-analyzer/references/workflows.md#secrets--permissions-workflow) for detailed remediation.
- **Flaky tests**: When the same test both passes and fails on the same commit, label it as flaky and recommend mitigation steps (mocking, retries) instead of silent retries.
