---
allowed-tools: Bash, Read, Edit, Grep
description: Review and fix GitHub Action check failures
---

# /dev-utilities:gh-checks

Review GitHub Action checks on the current branch and fix failures when possible.

## Usage

```bash
/gh-checks
```

## Behavior

Invoke the **ci-failure-analyzer** skill:

1. Establish context (branch, dirty state, PR vs. branch runs).
2. Collect failed logs matrix-aware (`gh run view --json jobs`, per-job `--log-failed`).
3. Categorize failures against the skill's pattern taxonomy with a confidence rating.
4. Apply fixes per the skill's autonomy guardrails — formatters/lint-fixes/lock syncs
   auto-run with diffs shown; anything touching logic, tests, secrets, or workflow YAML
   waits for approval.
5. Summarize root causes, commands run, and next steps; offer targeted job reruns.

Detection patterns, log-parsing recipes, and edge cases (no PR yet, flaky tests, missing
logs, secrets/permissions) live in the skill's references.
