---
name: ticktick-review
description: This skill should be used when the user asks to "review my tasks", "what's due today", "what's overdue", "daily planning", "weekly review", "what should I work on", "show me my inbox", "triage tasks", or wants to prioritize or get an overview of their TickTick workload.
version: 1.1.0
author: klauern
---

# TickTick Review Skill

## Overview

Surfaces overdue, today, and upcoming tasks from TickTick and guides the user through triage. Supports daily planning, weekly reviews, and GTD-style next-action selection.

**MCP tool prefix**: `mcp__ticktick__`

## When to Activate

- "What's due today?" / "Show today's tasks"
- "What's overdue?" / "I'm behind on tasks"
- "Daily standup / planning"
- "Weekly review"
- "What should I work on?"
- "Show my inbox" / "Triage my tasks"
- "Urgent tasks" / "High priority tasks"

## Review Modes

| Mode | Trigger keywords | Primary tools |
|------|-----------------|--------------|
| Daily | "today", "daily", "standup" | `list_undone_tasks_by_time_query("today")` + `filter_tasks` (overdue) |
| Weekly | "this week", "weekly review" | `list_undone_tasks_by_time_query("next7day")` + `filter_tasks` (overdue) |
| Inbox | "inbox", "triage", "all tasks" | `filter_tasks` (wide range) + overdue filter |
| Priority | "urgent", "high priority" | `filter_tasks` with `priority: [5]` or `priority: [3, 5]` |
| GTD | "next actions", "what should I do" | `filter_tasks` with `priority: [3, 5]` + `list_undone_tasks_by_time_query("today")` |

## Core Workflow

**Phase 1 — Determine Mode**
Read user intent to select review mode from the table above. Default to Daily if unclear.

**Phase 2 — Fetch Tasks (parallel)**

For overdue tasks, use `filter_tasks` with `endDate` set to the start of today (midnight). Any undone task with a due date before today is overdue.

Add mode-specific tool calls in parallel:
- Daily: `list_undone_tasks_by_time_query` with `query_command: "today"`
- Weekly: `list_undone_tasks_by_time_query` with `query_command: "next7day"`
- Priority: `filter_tasks` with `priority: [5]` or `priority: [3, 5]`

**Phase 3 — Summarize**
Present grouped sections:
```text
OVERDUE (N)  — tasks past due date
TODAY (N)    — due today
UPCOMING (N) — later this week (weekly mode only)
```
Highlight top 3 focus items by priority + urgency.

**Phase 4 — Triage Loop**
For each surfaced task, offer actions:
- `[c]omplete` → call `complete_task` (requires `project_id` and `task_id`)
- `[r]eschedule` → call `update_task` with new dueDate (requires `task_id` and `task` object)
- `[n]o date` → clear due/start dates via `ticktick_api.py clear-dates` script
- `[d]elete` → remove via `ticktick_api.py delete-task` script
- `[s]kip` → leave unchanged

**Phase 5 — Execute & Summarize**
Batch execute all user choices. End with: "N completed, M rescheduled, P deleted."

## Sub-Agent Strategy

**Use Haiku for**: all parallel task fetches, `complete_task`, `update_task` calls
**Use Sonnet for**: prioritization reasoning, selecting focus items, triage recommendations, rescheduling date suggestions

## Progressive Disclosure

- `@references/gtd-contexts.md` — GTD context mapping, review checklists, triage decision tree

## Requirements

- MCP server must be connected (verify with `/ticktick:setup`)
- `TICKTICK_ACCESS_TOKEN` only needed for script-based operations (clear-dates, delete-task)
