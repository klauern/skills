---
name: ticktick-capture
description: This skill should be used when the user asks to "add a task", "capture this", "remind me to", "I need to do", "add to TickTick", "create a ticket", "track this", or mentions capturing or tracking a task or action item in TickTick.
version: 1.0.0
author: klauern
---

# TickTick Capture Skill

## Overview

Converts natural language input into structured TickTick tasks using the MCP server tools. Handles single tasks, lists of tasks, and tasks with complex metadata (due dates, priorities, projects, tags).

**MCP tool prefix**: `mcp__plugin_ticktick_ticktick__`

## When to Activate

- "Add a task: ..."
- "Remind me to ..."
- "I need to ..."
- "Capture this to TickTick"
- "Create a ticket for ..."
- "Track this action item"
- User provides a list of things to do

## Task Field Reference

| Field | MCP param | Values |
|-------|-----------|--------|
| Title | `title` | Required, plain text |
| Project | `projectId` | UUID from `get_projects` |
| Due date | `dueDate` | ISO 8601: `2025-03-07T10:00:00+00:00` |
| Priority | `priority` | 0=low/none, 1=medium, 3=high, 5=urgent |
| Tags | `tags` | Array of strings |
| Notes | `content` | Markdown supported |

## Core Workflow

**Phase 1 — Parse Intent**
Extract from user input: title, project hint (name/keyword), due date expression, priority signal, tags, notes/description.

**Phase 2 — Resolve Project**
- If user specifies a project name → call `get_projects`, match by name → get `projectId`
- If ambiguous → show project list and ask user to choose
- If no project mentioned → omit `projectId` (uses TickTick inbox)

**Phase 3 — Create Task(s)**
- Single task → `create_task` with structured params
- Multiple tasks (user gave a list) → `batch_create_tasks`
- Always include `dueDate` if parsed; omit rather than guess

**Phase 4 — Confirm**
Show: task title, project name (or "Inbox"), due date, priority label, task ID.

## Sub-Agent Strategy

**Use Haiku for**: `get_projects`, `create_task`, `batch_create_tasks` — fast, deterministic API calls
**Use Sonnet for**: NL parsing, date inference from relative expressions, project disambiguation, batch structuring from prose lists

## Progressive Disclosure

- `@references/examples.md` — NL parsing examples, date/priority mappings, MCP call shapes

## Requirements

- `TICKTICK_CLIENT_ID`, `TICKTICK_CLIENT_SECRET`, `TICKTICK_ACCESS_TOKEN` must be set
- Run `/ticktick:setup` if not configured
- MCP server must be connected (verify with `/mcp`)
