---
allowed-tools: ["Bash", "mcp__plugin_ticktick_ticktick__list_undone_tasks_by_time_query", "mcp__plugin_ticktick_ticktick__filter_tasks", "mcp__plugin_ticktick_ticktick__complete_task", "mcp__plugin_ticktick_ticktick__update_task", "mcp__plugin_ticktick_ticktick__search_task"]
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
2. Dedup: before rendering "This Week", remove any tasks whose IDs already appear in the "Today" list (tasks due today will be returned by both fetches)
3. Present tasks grouped by section: Overdue → Today → This Week
4. Collect triage decisions for each task
5. Execute all actions in batch: `complete_task`, `update_task`, or delete via script
6. Print a summary of every action taken

## Implementation

Fetch simultaneously:
- `filter_tasks` with `endDate` set to start of today — overdue tasks
- `list_undone_tasks_by_time_query` with `query_command: "today"` — today's tasks
- `list_undone_tasks_by_time_query` with `query_command: "next7day"` — this week's tasks

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
- **[c]omplete** — mark done via `complete_task` (requires `project_id` and `task_id`)
- **[r]eschedule** — prompt for new date, then call `update_task`
- **[n]o date** — clear due/start dates via the `ticktick_api.py` script:
  ```bash
  SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
  uv run "$SCRIPT_DIR/ticktick_api.py" clear-dates --task-id <TASK_ID> --project-id <PROJECT_ID> --json
  ```
- **[d]elete** — permanently remove via the `ticktick_api.py` script:
  ```bash
  SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
  uv run "$SCRIPT_DIR/ticktick_api.py" delete-task --task-id <TASK_ID> --project-id <PROJECT_ID> --json
  ```
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

- Before rendering the "This Week" section, filter out any tasks whose IDs are already present in the "Today" list — `list_undone_tasks_by_time_query("next7day")` includes tasks due today, so deduplication by task ID is required to prevent the same task appearing twice
- Deletion is permanent — confirm before executing
- Rescheduling to a specific date: ask "Reschedule to? (e.g. Tuesday, Apr 10)"
- If all three fetches return empty, report "Inbox zero — nothing to triage."
- The `complete_task` tool requires both `project_id` and `task_id` — extract `projectId` from the task data
