---
allowed-tools: ["Bash", "mcp__plugin_ticktick_ticktick__list_undone_tasks_by_time_query", "mcp__plugin_ticktick_ticktick__filter_tasks", "mcp__plugin_ticktick_ticktick__complete_task", "mcp__plugin_ticktick_ticktick__update_task"]
description: Show today's tasks and overdue items, with triage actions
---

# /ticktick:today

Display overdue tasks and tasks due today, then offer quick triage actions for each.

## Usage

```bash
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
- `list_undone_tasks_by_time_query` with `query_command: "today"` — tasks due today
- `filter_tasks` with `endDate` set to the start of today (midnight) — overdue tasks (due before today and still undone)

Display format:

```text
OVERDUE (N tasks)
- [HIGH] Finish quarterly report (Work) — 3 days overdue
- [MED]  Reply to Alice (Inbox) — 1 day overdue

TODAY (N tasks)
- [HIGH] Team standup prep (Work) — due 09:00
- [LOW]  Water plants (Home) — all-day
```

After displaying, prompt for actions on each task:
- **[c]omplete** — mark done via `complete_task` (requires `project_id` and `task_id`)
- **[r]eschedule** — move to tomorrow via `update_task` (set due date to next day)
- **[n]o date** — clear due/start dates via the `ticktick_api.py` script:
  ```bash
  SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
  uv run "$SCRIPT_DIR/ticktick_api.py" clear-dates --task-id <TASK_ID> --project-id <PROJECT_ID> --json
  ```
- **[s]kip** — leave unchanged

> **Note**: Delete is not offered in the daily view — use `/ticktick:inbox` for full triage including deletion.

## Output

```text
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
- The `complete_task` and `update_task` tools require both `project_id` and `task_id` — extract `projectId` from the task data returned by the query tools
