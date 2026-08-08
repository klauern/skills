---
allowed-tools: ["Bash", "mcp__ticktick__list_undone_tasks_by_time_query", "mcp__ticktick__filter_tasks", "mcp__ticktick__complete_task", "mcp__ticktick__update_task"]
description: Show today's tasks and overdue items, with triage actions
---

# /ticktick:today

Display overdue tasks and tasks due today, then offer quick triage actions for each.

## Behavior

Run the **ticktick-review** skill's daily flow:

1. Fetch in parallel: today (`list_undone_tasks_by_time_query "today"`) and overdue
   (`filter_tasks` with `endDate` set to the start of today at midnight).
2. Display both groups with the skill's priority labels and days-overdue.
3. Offer per-task actions: [c]omplete, [r]eschedule to tomorrow (same time, or all-day),
   [n]o date (clear via `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/ticktick_api.py"
   clear-dates`), [s]kip.
4. Execute and summarize counts. If nothing is due: "All clear — no tasks due today."

Tool notes: `complete_task`/`update_task` need both `project_id` and `task_id` (take
`projectId` from the fetched task data).
