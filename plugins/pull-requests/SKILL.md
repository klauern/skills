---
name: pull-requests
description: Orchestrate pull request workflows including assessment, creation, updates, comment triage, and merge-conflict handling. Use when Codex needs to inspect a PR, create a pull request, update PR metadata, triage review feedback, or coordinate PR worktree setup.
---

# Pull Requests

Use this skill as the entry point for pull request work.

## Entry Points

- `pr-assess`: Inspect a PR end to end, classify comments, and create or reuse a dedicated worktree.
- `pr`: Create a PR from the current branch and template.
- `pr-update`: Refresh PR title/body from the actual diff.
- `pr-comment-review`: Triage review feedback into actionable items.
- `merge-conflicts`: Resolve merge conflicts during PR workflows.

## Operating Rules

- Prefer `pr-assess` before non-trivial PR follow-up work.
- Keep assessment read-only to PR state; do not reply, resolve, or close threads during assessment.
- Reuse an existing dedicated worktree when one already matches the PR; create a detached worktree only when needed.
- Treat comment triage as conservative: separate blocking, actionable, suggestion, nit, and informational feedback.

## Detail References

- [Assessment workflow](references/assessment.md) for report shape, triage rules, and worktree selection.
- `pr-creator` for PR creation specifics.
- `pr-conflict-resolver` for conflict analysis and resolution details.
