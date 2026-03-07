---
allowed-tools: ["Bash", "mcp__plugin_ticktick_ticktick__get_tasks_due_today", "mcp__plugin_ticktick_ticktick__get_overdue_tasks", "mcp__plugin_ticktick_ticktick__complete_task", "mcp__plugin_ticktick_ticktick__update_task"]
description: Show today's tasks and overdue items, with triage actions
---

# /ticktick:today

Display overdue tasks and tasks due today, then offer quick triage actions for each.

## Usage

```
/ticktick:today
```

## Behavior

1. Fetch overdue tasks and today's tasks in parallel
2. Display both groups in a structured format
3. Offer per-task actions: complete, reschedule to tomorrow, or skip
4. Execute requested actions via `complete_task` or `update_task`
5. Print a summary of actions taken

## Implementation

Fetch simultaneously:
- `get_overdue_tasks` — tasks past their due date
- `get_tasks_due_today` — tasks due today

Display format:

```
OVERDUE (N tasks)
- [HIGH] Finish quarterly report (Work) — 3 days overdue
- [MED]  Reply to Alice (Inbox) — 1 day overdue

TODAY (N tasks)
- [HIGH] Team standup prep (Work) — due 09:00
- [LOW]  Water plants (Home) — all-day
```

After displaying, prompt for actions on each task:
- **complete** — mark done via `complete_task`
- **reschedule** — move to tomorrow via `update_task` (set due date to next day)
- **no date** — clear due/start dates via the `ticktick_dates.py` script:
  ```bash
  SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
  uv run "$SCRIPT_DIR/ticktick_dates.py" clear-dates --task-id <TASK_ID> --project-id <PROJECT_ID> --json
  ```
- **skip** — leave unchanged

## Output

```
Actions taken:
  Completed:    2 tasks
  Rescheduled:  1 task
  Skipped:      1 task
```

## Notes

- Priority labels: HIGH (priority >= 3), MED (priority 1-2), LOW (priority 0)
- "Days overdue" is calculated from the task's original due date
- Rescheduling sets the due date to tomorrow at the same time (or all-day if no time was set)
- If there are no overdue or due tasks, report "All clear — no tasks due today."
