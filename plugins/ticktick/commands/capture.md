---
allowed-tools: ["mcp__ticktick__create_task", "mcp__ticktick__list_projects", "mcp__ticktick__batch_add_tasks"]
description: Capture a task or list of tasks to TickTick
argument-hint: "[task description]"
---

# /ticktick:capture

Quickly create one or more tasks in TickTick, with optional project, due date, and priority.

## Usage

```bash
/ticktick:capture Buy milk tomorrow
/ticktick:capture Fix login bug - high priority, due Friday
/ticktick:capture            # interactive: prompts for the task
```

## Behavior

Invoke the **ticktick-capture** skill with the description (asking for one if omitted):

1. Parse title, project hint, due date, and priority per the skill's mapping tables.
2. Resolve the project via `list_projects` (ask if ambiguous; omit for Inbox).
3. Create via `create_task`, or `batch_add_tasks` when the user gave a list.
4. Confirm with task title, project name, due date, priority label, and task ID.
