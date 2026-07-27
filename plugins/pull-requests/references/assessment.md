# PR Assessment Reference

## Report Shape

Keep assessment output stable and sectioned:

- PR identity: number, title, state, URL, branch, base branch
- Workspace: reused/created/not created, path, and head commit
- Change summary: file count, additions/deletions, changed areas, recent commits
- Comment triage: open actionable items, resolved items, outdated items filtered
- Follow-up notes: what should happen next, without mutating PR state

## Worktree Selection

1. Inspect existing worktrees with `git worktree list --porcelain`.
2. Reuse a worktree when either:
   - the path matches the deterministic assessment path, or
   - the worktree HEAD matches the PR head commit.
3. If no reusable worktree exists, create a detached worktree for the PR head commit.
4. Prefer `.worktrees/` at the repository root; create it when needed and keep it ignored by git.
5. Avoid duplicate worktrees for the same PR.

Recommended deterministic path:

```text
.worktrees/pr-<number>-<slug>
```

where `<slug>` is derived from the PR head branch name or title with unsafe characters replaced by `-`.

## Comment Triage

Classify comments and threads conservatively:

- `blocking`: must-fix issues, regressions, correctness problems, or explicit change requests
- `actionable`: changes or clarifications the author should address
- `suggestion`: optional code or workflow improvements
- `nit`: small style, wording, or formatting feedback
- `informational`: context, praise, status updates, or comments that do not require action

Filter review threads first:

- include open threads
- de-prioritize resolved threads
- exclude outdated threads from the actionable list

For each item, preserve:

- source: conversation comment or review thread
- author
- path and line when available
- a short body excerpt

## Follow-up Notes

Keep the final note concise:

- mention how many actionable items remain
- mention whether a worktree was created or reused
- do not draft replies or mutate PR state here
