---
name: ticktick-enrich
description: This skill should be used when the user asks to "enrich a task", "flesh out this task", "make this task actionable", "add context to my tasks", or "fill in task details" — turning vague half-sentence TickTick tasks into prioritized, dated, labeled, linked items.
version: 1.0.0
author: klauern
---

# TickTick Enrich Skill

## Overview

Turns vague, half-sentence TickTick captures into actionable tasks. Gathers what
context it can on its own (opportunistic lookups), then interviews the user **one
question at a time** — grill-me style, with a recommended answer for each — to fill
in priority, timing, labels, links, and context. Writes the result back to both the
task **content** (markdown notes) and its **structured fields** (priority, tags,
dates).

Works on a single task, or loops over a whole project/filter (batch mode).

**MCP tool prefix**: `mcp__ticktick__`

## When to Activate

- "Enrich this task" / "flesh out this task" / "fill in the details"
- "Make this task actionable"
- "Add context to my tasks" / "enrich my Work list"
- A task is a one-liner with empty content, no tags, priority 0, or a placeholder
  due date and the user wants it specified

## Task Field Reference

| Field | MCP param | Values |
|-------|-----------|--------|
| Title | `title` | Concise; longer content → `content` |
| Notes/context | `content` | Markdown supported |
| Priority | `priority` | **0=none, 1=low, 3=medium, 5=high** (2 and 4 are invalid) |
| Tags | `tags` | Array; reuse the existing vocabulary (see references) |
| Due date | `dueDate` | ISO 8601 w/ offset: `2026-06-05T17:00:00-05:00` |
| Start date | `startDate` | ISO 8601 w/ offset |
| Time zone | `timeZone` | Preserve existing; default `America/Chicago` |

**Date sentinels**: clear a date by setting it to `1970-01-01T00:00:00.000+0000`.
On read, treat both `1970-01-01` **and** `2099-01-01` as "no real date / someday".

## Core Workflow

### Phase 1 — Select target

- **Single task** (default): user names the task, pastes an `id`, or asks for
  "the sparsest." Resolve a named task by listing the project's undone tasks and
  matching the title.
- **Batch mode**: an argument names a project (e.g. "Work") or a filter. Fetch
  undone tasks with `get_project_with_undone_tasks` (or `filter_tasks`), **rank by
  sparseness**, and enrich one at a time, confirming before moving to the next.

**Sparseness score** (higher = enrich first): empty `content` (+2), no `tags` (+1),
`priority == 0` (+1), placeholder/absent due date (+1), title ≤ 6 words (+1).

### Phase 2 — Auto-gather (opportunistic)

Fetch the task via `get_task_by_id`. Scan `title` + `content` for references and
resolve **only the ones already present** — never search blindly:

- **Jira keys** (`FSEC-1234`, `PCI-5628`, `SECURE-…`, etc.) → jira-core skill / CLI
- **GitHub** `org/repo` or PR URLs → `gh`
- **Confluence / Slack / Capacities / Google-Docs links** → confluence skill / fetch
- **People / teams** → cerebro

Degrade gracefully: if a lookup tool is not connected or fails, note it and move on.
Never block the interview on an external call.

### Phase 3 — Interview (grill-me style)

Ask **one question at a time**, each with your recommended answer, walking the
decision tree. **If a question is already answered by the task or by Phase-2
research, skip it** — prefer exploring over asking. Default sequence:

1. **Done when?** — what does "done" look like? (sharpens title + acceptance)
2. **Priority** — 0/1/3/5; recommend from signals (deadline, blocker, who's waiting)
3. **Timeframe** — a concrete date, or "someday"; replace any 2099 placeholder
4. **Labels** — propose from the existing tag vocabulary
5. **Links/context** — any ticket, doc, repo, or person to attach
6. **Next action** (optional, chunky items only) — the first physical step

See `references/question-bank.md` for the full tree, recommendation heuristics, the
tag vocabulary, detection regexes, and the content template.

### Phase 4 — Compose & write back

Build a **merged** `OpenTask` (full-object update, not a patch — preserve `id`,
`etag`, `kind`, `projectId`, and any field you are not changing). Then:

- Write a structured markdown block into `content` (see template in references:
  `## Context`, `## Links`, `## Done when`). Preserve any meaningful existing notes.
- Set `priority`.
- **Union** new tags with existing ones and dedup.
- Set `dueDate` / `startDate` (with offset), or the clear-date sentinel for "someday".
- Call `update_task` (single) — in batch mode, accumulate confirmed tasks and use
  `batch_update_tasks` once per set.

Use `add_comment` only if the user explicitly wants a dated note rather than body
enrichment (plain text, ≤1024 chars).

### Phase 5 — Confirm

Show a compact before/after of the changed fields and the task ID. In batch mode,
offer the next task; on "stop"/done, print a summary (N enriched, fields touched).

## Sub-Agent Strategy

- **Use Haiku for**: `get_task_by_id`, `list_tags`, `list_projects`, project/undone
  fetches, the final `update_task` / `batch_update_tasks` write.
- **Use Sonnet for**: sparseness ranking, reference detection, recommendation
  reasoning (priority/labels/dates), interview flow, composing the content block.

## Progressive Disclosure

- `@references/question-bank.md` — full question tree, recommendation heuristics,
  tag vocabulary, reference-detection regexes, content template.

## Requirements

- MCP server must be connected (verify with `/ticktick:setup`).
- Opportunistic lookups use whatever is available (jira-core, confluence, cerebro,
  `gh`); all are optional — the skill works offline with light parsing only.
