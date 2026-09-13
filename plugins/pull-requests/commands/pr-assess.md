---
allowed-tools: Bash, Read, Glob, Grep
description: Assess a pull request, triage comments, and create or reuse a dedicated worktree
argument-hint: "[pr-number]"
---

# /pr-assess

Assess a pull request end to end without mutating PR state.

## Usage

```bash
/pr-assess [pr-number]
```

If no PR number is provided, the command uses the PR associated with the current branch.

## Behavior

Invoke the **pr-assessment** skill:

1. Resolve the target PR from the provided number or current branch.
2. Gather PR metadata, commits, files, comments, and review threads with `gh` (GraphQL, paginated).
3. Create or reuse a dedicated detached worktree under `.worktrees/` when needed.
4. Classify comments and review threads into blocking, actionable, suggestion, nit, and informational items.
5. Return a stable assessment report with changed areas, actionable feedback, and follow-up notes.

## Rules

- Do not reply to comments during assessment.
- Do not resolve or close review threads during assessment.
- Do not post PR edits during assessment.
- Reuse an existing worktree when it already matches the PR head or deterministic path.

## Implementation

Use the bundled script:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)/plugins/pull-requests}"
uv run "$PLUGIN_ROOT/scripts/pr_assess.py" "$@"
```
