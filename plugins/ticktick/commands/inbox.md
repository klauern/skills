---
allowed-tools: ["Bash", "mcp__plugin_ticktick_ticktick__get_overdue_tasks", "mcp__plugin_ticktick_ticktick__get_tasks_due_today", "mcp__plugin_ticktick_ticktick__get_tasks_due_this_week", "mcp__plugin_ticktick_ticktick__complete_task", "mcp__plugin_ticktick_ticktick__update_task", "mcp__plugin_ticktick_ticktick__delete_task"]
description: Full task triage — overdue, today, and this week
---

# /ticktick:inbox

Full inbox triage across overdue tasks, today's tasks, and the rest of the week.

## Usage

```bash
/ticktick:inbox
```

## Behavior

1. Fetch overdue, today, and this-week tasks in parallel
2. Present tasks grouped by section: Overdue → Today → This Week
3. Collect triage decisions for each task
4. Execute all actions in batch: `complete_task`, `update_task`, or `delete_task`
5. Print a summary of every action taken

## Implementation

Fetch simultaneously:
- `get_overdue_tasks`
- `get_tasks_due_today`
- `get_tasks_due_this_week`

Display format:

```text
=== OVERDUE (N tasks) ===
- [HIGH] Finish spec doc (Work) — 4 days overdue
- [MED]  Book dentist (Personal) — 2 days overdue

=== TODAY (N tasks) ===
- [HIGH] Deploy hotfix (Work) — due 14:00
- [LOW]  Grocery run (Personal) — all-day

=== THIS WEEK (N tasks) ===
- [MED]  Draft blog post (Personal) — due Wed
- [LOW]  Clean desk (Home) — due Thu
```

For each task, the user chooses:
- **[c]omplete** — mark done via `complete_task`
- **[r]eschedule** — prompt for new date, then call `update_task`
- **[n]o date** — clear due/start dates via the `ticktick_dates.py` script:
  ```bash
  SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
  uv run "$SCRIPT_DIR/ticktick_dates.py" clear-dates --task-id <TASK_ID> --project-id <PROJECT_ID> --json
  ```
- **[d]elete** — permanently remove via `delete_task`
- **[s]kip** — leave unchanged

Collect all decisions first, then execute in a single pass to minimize round-trips.

## Output

```text
Triage complete:
  Completed:    3 tasks
  Rescheduled:  2 tasks
  Cleared date: 1 task
  Deleted:      1 task
  Skipped:      3 tasks
```

## Notes

- This-week tasks exclude today (avoid duplicating the Today section)
- Deletion is permanent — confirm before executing `delete_task`
- Rescheduling to a specific date: ask "Reschedule to? (e.g. Tuesday, Mar 10)"
- If all three fetches return empty, report "Inbox zero — nothing to triage."
