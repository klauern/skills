---
allowed-tools: ["mcp__plugin_ticktick_ticktick__create_task", "mcp__plugin_ticktick_ticktick__get_projects", "mcp__plugin_ticktick_ticktick__batch_create_tasks"]
description: Capture a task or list of tasks to TickTick
---

# /ticktick:capture

Quickly create one or more tasks in TickTick, with optional project, due date, and priority.

## Usage

```
/ticktick:capture [task description]
```

## Arguments

- `[task description]` (optional): Natural-language task description. If omitted, interactive mode prompts for input.

## Behavior

### With a task description:
1. Parse the input for title, project hint, due date, and priority
2. If the project is ambiguous, call `get_projects` and ask the user to choose
3. Call `create_task` (or `batch_create_tasks` for multiple tasks)
4. Confirm with task title, project name, due date, and task ID

### Interactive mode (no argument):
1. Ask: "What task would you like to capture?"
2. Optionally prompt: "Any project, due date, or priority to set?"
3. Proceed with creation and confirmation

## Implementation

Parse the user-supplied description (or ask for one) and extract:
- **Title**: The core task text
- **Project**: Any project name hint (e.g., "in Work", "#personal")
- **Due date**: Natural language dates ("tomorrow", "Friday", "next Monday")
- **Priority**: Keywords like "high priority", "urgent", "low"

Call `get_projects` when:
- A project hint is present but does not unambiguously match a known project
- No project is specified and the user may want to choose

Use `batch_create_tasks` when the input contains multiple tasks (bullet list or comma-separated items).

## Output

```
Created task:
  Title:   Buy milk
  Project: Personal
  Due:     2026-03-07
  ID:      abc123xyz
```

## Examples

```
# Single task with natural-language date
/ticktick:capture Buy milk tomorrow

# Task with priority and due date
/ticktick:capture Fix the login bug - high priority, due Friday

# Interactive mode
/ticktick:capture

# Multiple tasks (batch)
/ticktick:capture
- Review PR #42
- Update README
- Send standup notes
```

## Notes

- Priority mapping: urgent/critical → 5, high → 3, medium → 1 (TickTick scale), low/none → 0
- Dates are interpreted relative to today (2026-03-06)
- If no project is chosen, the task lands in the default inbox
