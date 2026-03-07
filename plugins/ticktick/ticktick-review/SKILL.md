---
name: ticktick-review
description: This skill should be used when the user asks to "review my tasks", "what's due today", "what's overdue", "daily planning", "weekly review", "what should I work on", "show me my inbox", "triage tasks", or wants to prioritize or get an overview of their TickTick workload.
version: 1.0.0
author: klauern
---

# TickTick Review Skill

## Overview

Surfaces overdue, today, and upcoming tasks from TickTick and guides the user through triage. Supports daily planning, weekly reviews, and GTD-style next-action selection.

**MCP tool prefix**: `mcp__plugin_ticktick_ticktick__`

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
| Daily | "today", "daily", "standup" | `get_tasks_due_today` + `get_overdue_tasks` |
| Weekly | "this week", "weekly review" | `get_tasks_due_this_week` + `get_overdue_tasks` |
| Inbox | "inbox", "triage", "all tasks" | `get_all_tasks` + `get_overdue_tasks` |
| Priority | "urgent", "high priority" | `get_tasks_by_priority` |
| GTD | "next actions", "engaged tasks" | `get_next_tasks` / `get_engaged_tasks` |

## Core Workflow

**Phase 1 — Determine Mode**
Read user intent to select review mode from the table above. Default to Daily if unclear.

**Phase 2 — Fetch Tasks (parallel)**
Always include `get_overdue_tasks`. Add mode-specific tool calls in parallel.

**Phase 3 — Summarize**
Present grouped sections:
```
OVERDUE (N)  — tasks past due date
TODAY (N)    — due today
UPCOMING (N) — later this week (weekly mode only)
```
Highlight top 3 focus items by priority + urgency.

**Phase 4 — Triage Loop**
For each surfaced task, offer actions:
- `[c]omplete` → call `complete_task`
- `[r]eschedule` → call `update_task` with new dueDate
- `[n]o date` → clear due/start dates via `ticktick_dates.py clear-dates` script (for tasks that shouldn't have a date)
- `[d]elete` → call `delete_task`
- `[s]kip` → leave unchanged

**Phase 5 — Execute & Summarize**
Batch execute all user choices. End with: "N completed, M rescheduled, P deleted."

## Sub-Agent Strategy

**Use Haiku for**: all parallel task fetches, `complete_task`, `update_task`, `delete_task` calls
**Use Sonnet for**: prioritization reasoning, selecting focus items, triage recommendations, rescheduling date suggestions

## Progressive Disclosure

- `@references/gtd-contexts.md` — GTD context mapping, review checklists, triage decision tree

## Requirements

- `TICKTICK_CLIENT_ID`, `TICKTICK_CLIENT_SECRET`, `TICKTICK_ACCESS_TOKEN` must be set
- Run `/ticktick:setup` if not configured
- MCP server must be connected (verify with `/mcp`)
