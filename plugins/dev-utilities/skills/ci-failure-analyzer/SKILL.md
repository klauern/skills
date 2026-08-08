---
name: ci-failure-analyzer
description: This skill should be used when the user asks to "fix CI", "debug failing GitHub Actions checks", "analyze CI logs", or reports failing checks/tests in GitHub Actions.
version: 1.0.0
author: klauern
allowed-tools: Bash Read Grep Glob Edit Write
---

# CI Failure Analyzer

Automated analysis and resolution of GitHub Actions CI failures.

## Quick Start

**Command**: `/gh-checks` — Analyze and fix CI failures

**Documentation**:
- [Workflows](references/workflows.md) — Step-by-step analysis flows
- [Failure Patterns](references/failure-patterns.md) — Detection patterns, fix commands, and log-parsing techniques
- [Tool Detection](references/tool-detection.md) — Project tool/formatter detection
- [Examples](references/examples.md) — Real-world scenarios

## When to Use

**Invoke when**:
- User asks "why is CI failing?" or "fix CI"
- User mentions failing tests or checks
- After pushing code, user asks about status
- `/gh-checks` command is executed

**Don't use for**:
- Local test runs (not CI)
- CI configuration questions (not failures)
- Setting up new CI (not debugging)

## Workflow Overview

```
1. Context     → git status, branch, PR existence
2. List Fails  → gh pr checks / gh run list
3. Get Logs    → gh run view <id> --log-failed
4. Analyze     → Categorize, determine fixability
5. Fix         → Auto-fix or guide user
6. Verify      → git diff, optional rerun
```

### Matrix-Aware Log Collection

- Gather run/job metadata first: `gh run view <run-id> --json jobs --jq '.jobs[] | {name,databaseId,status,conclusion}'`
- Use `name` for display, but target a job or matrix child by its numeric ID:
  `gh run view <run-id> --job <job-database-id> --log-failed`
- Report failing matrix axes explicitly (e.g. `node-version: 18`) and avoid rerunning
  the full matrix — target the remediated matrix child; GitHub reruns the selected
  job and its dependencies, but not sibling matrix children:
  `gh run rerun <run-id> --job <job-database-id>`
- If logs are unavailable ("logs are missing"), wait for the run to finish or ask the
  user to rerun once logs are ready
- Distinguish primary root causes from downstream jobs blocked by `needs`

## Fix Strategy

### Auto-Fix (Haiku)
| Category | Command |
|----------|---------|
| Formatting | `npx prettier --write .`, `black .`, `gofumpt -w .` |
| Linting | `npx eslint --fix .`, `ruff check --fix .` |
| Lock files | `npm install`, `poetry lock` (Poetry 2.x) |

**Always**: Show intent before running, verify with `git diff --stat`

### Consult User (Sonnet)
- Type errors (code intent matters)
- Test failures (logic vs test expectation)
- Breaking changes (migration strategy)
- Anything affecting business logic

### Non-Code Issues
- **Secrets**: Direct to Settings → Secrets (never guess values)
- **Cache**: Bump key, rerun (no code changes)
- **Permissions**: Update workflow YAML `permissions:` block

## Autonomy Guardrails

| Action | Auto-run? | Notes |
|--------|-----------|-------|
| Formatters | ✅ Yes | Show diff afterward |
| Lint --fix | ✅ Yes | Surface remaining manual issues |
| Lock files | ✅ Yes | Warn if major versions changed |
| Type/test fixes | ⚠️ Ask first | Present options, wait for approval |
| Workflow edits | ❌ Never | Guidance only |

## Failure Categories

See the taxonomy table in [failure-patterns.md](references/failure-patterns.md) —
detection signatures, auto-fix likelihood, and fix commands per category.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No failing checks | Verify branch, wait for checks to start |
| Cannot retrieve logs | Wait for run to complete |
| Auto-fix didn't work | Check CI config vs local |
| Too many failures | Fix root cause first (build > tests > lint) |
