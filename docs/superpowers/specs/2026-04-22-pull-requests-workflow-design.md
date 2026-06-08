# Pull Requests Workflow Design

## Summary

This document defines a single PR workflow family centered on a `PR assessment` entry point. The goal is to make PR handling more generic and more useful by combining PR inspection, automatic worktree setup, comment triage, and draft responses into one coherent capability set.

The workflow is intentionally split into independent capabilities so the work can be delivered in separate sessions without losing the overall shape.

## Goals

- Provide one generic entry point for PR work instead of only narrow PR creation or conflict-resolution helpers.
- Automatically open or reuse a dedicated worktree when a PR should be worked on independently.
- Read PR comments and review threads, then classify what is actionable.
- Draft suggested responses and next steps without mutating the PR by default.
- Keep the eventual action layer separate so reply/resolve/close behavior can be approved explicitly.
- Shrink the top-level skill docs so they route behavior instead of duplicating workflow detail.

## Non-Goals

- Do not automatically reply to, resolve, or close PR comments during assessment.
- Do not build a full general-purpose issue tracker.
- Do not replace `gh` with a custom GitHub API client unless a specific command requires it.
- Do not make the assessment workflow depend on a browser UI.

## Current Surface Area

The repository already has several PR-related commands and skills:

- `/pr` for creating a PR
- `/pr-update` for updating PR title/body
- `/pr-comment-review` for triaging PR comments
- `/merge-conflicts` for resolving merge conflicts
- `pr-creator` and `pr-conflict-resolver` skills for the detailed logic behind those workflows

The main gap is an orchestration layer that treats PR work as a broader workflow rather than a set of disconnected commands.

## Proposed Capability Model

### 1. `assessment`

The front door for PR work.

Responsibilities:

- Identify the PR from the current branch or an explicit PR number.
- Collect PR metadata, diff, commit history, branch state, and comments.
- Decide whether a dedicated worktree is needed.
- Produce a structured assessment report.

Outputs:

- What changed
- What comments matter
- Whether a worktree is present or should be created
- Which follow-up items are actionable
- Which actions should be drafted, not executed

### 2. `workspace`

The isolation layer.

Responsibilities:

- Open a dedicated worktree for a PR automatically when assessment runs.
- Reopen or reuse an existing worktree if one already exists.
- Keep review work separate from the main checkout.

Rules:

- Worktree creation is automatic.
- Reuse should be preferred over creating duplicates.
- The workspace layer should be invisible unless something fails or a path conflict needs user input.

### 3. `triage`

The comment analysis layer.

Responsibilities:

- Read PR conversation comments and inline review threads.
- Filter resolved and outdated noise.
- Classify comments as actionable, informational, or optional.
- Rank actionable items by severity and likely effort.

Recommended classifications:

- blocking
- actionable
- suggestion
- nit
- informational

### 4. `response-draft`

The synthesis layer.

Responsibilities:

- Produce draft replies for actionable comments.
- Produce a short follow-up plan for code changes or clarifications.
- Generate a polished list of things the user can review or revise.

Rules:

- Drafting is automatic.
- The output should be reviewable, concise, and factual.
- Drafts should separate “reply text” from “work required”.

### 5. `actions`

The mutation layer.

Responsibilities:

- Reply to comments.
- Resolve or close threads where appropriate.
- Mark comments as addressed in the PR workflow.

Rules:

- This layer is opt-in, not default.
- It should only run after explicit approval.
- It should preserve a clear audit trail of what it changed.

## Default Workflow

1. User runs `PR assessment`.
2. The system identifies the PR and ensures a dedicated worktree exists.
3. The system gathers PR metadata, diff, commits, branch state, and comments.
4. The system triages comments and review threads.
5. The system drafts suggested replies and a follow-up plan.
6. The system returns a structured report with actionable items.
7. The user reviews and polishes the draft output.
8. Only then does the user approve any reply/resolve/close actions.

## Command and Skill Direction

The long-term naming should favor a generic `pull-requests` top-level skill rather than a narrow `pr-creator` name.

Suggested hierarchy:

- `pull-requests` as the orchestrator
- focused subskills or references for creation, update, assessment, triage, and conflict resolution

This keeps the top-level skill lightweight and lets the detail live in smaller, more stable documents.

## Phased Delivery Plan

### Phase 1: Normalize the PR workflow boundary

- Introduce the generic `pull-requests` entry skill.
- Reduce the top-level docs in the existing PR skills.
- Move detailed workflow material into references where appropriate.
- Keep existing commands working while the naming changes settle.

### Phase 2: Build assessment and workspace orchestration

- Add the `PR assessment` capability.
- Make worktree creation automatic.
- Reuse existing worktrees when possible.
- Return a stable assessment report format.

### Phase 3: Add comment triage and draft synthesis

- Harvest all PR comments and review threads.
- Classify actionable feedback.
- Generate draft replies and next-step notes.
- Keep the output useful even when no code changes are made.

### Phase 4: Add approved actions

- Implement reply/resolve/close behavior for approved items.
- Preserve thread state and auditability.
- Keep mutation behavior separate from triage and drafting.

### Phase 5: Polish and consolidation

- Trim duplicated content from the current PR skills.
- Add examples for the common review flows.
- Tighten error handling and edge cases.

## Risks and Constraints

- PR comments can be noisy, stale, or informational only; the triage layer must be conservative.
- Inline review threads can be outdated even when still visible; outdated items should be de-prioritized or filtered.
- Automatic worktree creation should avoid clobbering an existing checkout or creating duplicate worktrees.
- The action layer must not silently mutate PR state.
- The workflow should remain compatible with `gh` CLI-first operations.

## Acceptance Criteria

- A single assessment command can inspect a PR end to end.
- Running assessment creates or reuses a dedicated worktree automatically.
- The workflow returns a ranked set of actionable comments and review items.
- Draft responses are generated automatically but not posted.
- Reply/resolve/close actions require explicit approval.
- The PR-related skill docs are materially shorter and less repetitive than the current versions.

## Implementation Sessions

This workbook is intended to be executed in separate sessions:

1. Rename and slim the top-level PR skill boundary.
2. Implement assessment plus automatic worktree handling.
3. Implement comment triage.
4. Implement draft response generation.
5. Implement approved action execution.
6. Clean up and consolidate documentation.

