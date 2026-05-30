---
name: ticktick-enrich
description: This skill should be used when the user asks to "enrich a task", "flesh out this task", "make this task actionable", "expand this task", "add subtasks", "break this down", "add detail to", "improve this task", or wants a thin one-line TickTick task turned into a well-formed task with a sharper title, description, subtasks, and metadata.
version: 1.0.0
author: klauern
---

# TickTick Enrich Skill

## Overview

Turns a thin TickTick task into a well-formed, actionable one — by **interviewing the user for the missing context, not by guessing.** It reads the task, spots what's missing (goal, steps, deadline, importance, links), asks focused questions, then structures the user's answers into a sharper title, a fleshed-out description, a subtask checklist, and only the metadata the user supplied. **Never fabricates facts (names, dates, URLs) the user didn't provide. Always previews changes and waits for approval before writing.**

**MCP tool prefix**: `mcp__ticktick__`

## When to Activate

- "Enrich this task" / "flesh out this task"
- "Make this task actionable" / "expand this"
- "Add subtasks" / "break this down into steps"
- "Add detail / context to this task"
- "Improve this task"
- After `/ticktick:capture`, when a quickly-captured task needs substance

## Task Field Reference

Fields live in the `task` object (camelCase):

| Field | `task` field | Notes |
|-------|--------------|-------|
| Title | `title` | Sharpen: action verb first, specific object, concise |
| Kind | `kind` | `TEXT`/`NOTE` → shows `content`; `CHECKLIST` → shows `desc` + `items` |
| Description | `desc` (checklist) / `content` (text) | Markdown. Holds Goal / Acceptance criteria / References |
| Subtasks | `items` | Native checklist `[{ "title": "...", "status": 0 }]`; checkable in-app (needs `kind: CHECKLIST`) |
| Priority | `priority` | 0=none, 1=low, 3=medium, 5=high |
| Due date | `dueDate` | ISO 8601: `2026-06-15T10:00:00+0000`; clear with `1970-01-01T00:00:00.000+0000` |
| Start date | `startDate` | ISO 8601 |
| Tags | `tags` | Array of strings; match existing via `list_tags` |
| Project | `projectId` | Carry over unchanged; an actual move is cleaner via `move_task` |

`update_task` signature: `update_task(task_id, task)` where `task` is the **full task object**. The call operates on the whole task — `get_task_by_id` (needs only `task_id`, scans all projects) → merge enrichment into the returned object → send it back complete so untouched fields aren't lost.

## Core Workflow

**Phase 1 — Resolve Task**
- Argument is a 24-char hex ID → `get_task_by_id`.
- Argument is free text → `search_task`; if multiple matches, list candidates and ask.
- No argument → ask what to enrich (offer a search).
- Always capture `projectId` from the result — required for the write.

**Phase 2 — Analyze & Spot Gaps**
Read title, `content`/`desc`, existing `items`, `priority`, dates, `tags`, `projectId`, `repeatFlag`. List what's *missing or vague* — unclear goal, no acceptance criteria, no steps, an ambiguous title (e.g. a bare name like "Gable"), no deadline, no stated importance. **These gaps drive the interview; do not fill them yourself.**

**Phase 3 — Interview for Context (don't fabricate)**
Ask the user focused, batched questions to close the gaps. **Never guess names, dates, URLs, or scope the user didn't state.** Typical questions:
- What's the goal / what does "done" look like?
- Is there a deadline, and how important is it?
- Any steps you already have in mind? (otherwise offer to *propose* a draft for them to edit)
- Any links, people, or background to capture?
- For a vague title: what is this actually about?

Skip anything the task already answers. If the user says "you draft it," propose options clearly marked as *yours* and let them correct — proposals are applied only on approval.

**Phase 4 — Draft from Their Answers**
Structure what the user gave you (and only that):
- **Title**: sharpen for clarity using their clarified intent — verb first, specific object. Keep their meaning.
- **Description** (markdown → `desc` for checklist tasks, `content` for text): Goal, Acceptance criteria, Notes, References — built only from supplied context. Template in `@references/enrichment-guide.md`.
- **Subtasks**: from the steps they described (or a proposed draft they approved). Normal task → native `items` (`kind: CHECKLIST`). **Recurring task** (`repeatFlag` set) → keep `kind: TEXT`, use a markdown `- [ ]` checklist in `content`, and never touch `repeatFlag`/`dueDate`/`reminders` (native `items` re-check awkwardly each cycle).
- **Metadata**: set only what the user specified — a deadline they gave → `dueDate`; importance they stated → `priority`; tags/project they named. See policy below.

**Phase 5 — Preview & Gate (mandatory)**
Show a before → after diff of every changed field; render new subtasks as a list. Anything the user didn't confirm goes under **"Open / suggested (not applied)"**. Ask for approval. Never write before an explicit yes.

**Phase 6 — Write**
On approval, take the full task from `get_task_by_id`, merge the enrichment into it, and call `update_task(task_id, task)` with the complete object so nothing is dropped. Subtasks → `kind: "CHECKLIST"`, description in `desc`, steps in `items` (`status: 0`); notes-only → leave `kind` and use `content`.

**Phase 7 — Confirm**
Summarize what changed and restate anything still open.

## Metadata Policy (User-Supplied Only)

- **Set metadata only from what the user states.** Never infer priority from keywords or invent a due date. If they don't mention it, leave it — or ask.
- Never overwrite an existing value without the user's explicit yes.
- Priority mapping (when the user expresses importance): urgent/critical → 5, high → 3, medium → 1, low/none → 0.
- **Dates**: only a deadline the user gives; `dueDate`/`startDate` in ISO 8601. Clear with `1970-01-01T00:00:00.000+0000`.
- **Tags**: settable via `tags`; reuse existing tags (`list_tags`) and confirm any new tag with the user.
- **Project**: a move is cleaner via `move_task` — suggest, don't move silently.

## Sub-Agent Strategy

**Use Haiku for**: `search_task`, `get_task_by_id`, `list_projects`, `list_tags`, the final `update_task` call — fast, deterministic.
**Use Sonnet for**: title rewriting, description synthesis, subtask decomposition, metadata inference, judging which references are worth attaching.

## Progressive Disclosure

- `@references/enrichment-guide.md` — description template, acceptance-criteria patterns, subtask heuristics, conservative metadata rules, research/link guidance, worked before/after example.

## Requirements

- MCP server must be connected (verify with `/ticktick:setup`).
- `WebSearch`/`WebFetch` only used when references add value; skip silently otherwise.
