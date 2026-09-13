---
name: pr-assessment
description: Assess a pull request end to end without mutating PR state. Gathers PR metadata, commits, files, comments, and review threads, classifies feedback, and creates or reuses a dedicated worktree. Use when the user asks to "assess a PR", "triage PR feedback", "inspect a pull request", or uses /pr-assess.
version: 1.0.0
author: klauern
---

# PR Assessment

Inspect a pull request end to end and produce a stable, sectioned assessment report without replying, resolving, or otherwise mutating PR state.

## Quick Start

```text
User: assess PR 9
# or
User: /pr-assess 9
```

## Workflow

1. Resolve the target PR from the number argument or the current branch.
2. Gather PR metadata, commits, files, comments, and review threads with `gh` (GraphQL, paginated).
3. Create or reuse a dedicated detached worktree under `.worktrees/` when needed.
4. Classify comments and review threads into blocking, actionable, suggestion, nit, and informational items.
5. Return the assessment report: PR identity, workspace, change summary, comment triage, and follow-up notes.

## Rules

- Do not reply to comments during assessment.
- Do not resolve or close review threads during assessment.
- Do not post PR edits during assessment.
- Reuse an existing worktree when it matches the PR head or the deterministic path.

## Implementation

The bundled script does the heavy lifting:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)/plugins/pull-requests}"
uv run "$PLUGIN_ROOT/scripts/pr_assess.py" [pr-number]
```

See [references/assessment.md](references/assessment.md) for the report shape, triage rules, and worktree selection.
