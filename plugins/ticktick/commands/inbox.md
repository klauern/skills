---
allowed-tools: ["Bash", "mcp__ticktick__list_undone_tasks_by_time_query", "mcp__ticktick__filter_tasks", "mcp__ticktick__complete_task", "mcp__ticktick__update_task"]
description: Full task triage — overdue, today, and this week
---

# /ticktick:inbox

Full inbox triage across overdue tasks, today's tasks, and the rest of the week.

## Behavior

Run the **ticktick-review** skill's triage flow over three sections:

1. Fetch in parallel: overdue (`filter_tasks`, `endDate` < today), today
   (`list_undone_tasks_by_time_query "today"`), this week (`"next7day"`).
2. Dedup by task ID before rendering This Week — the `next7day` query includes today's
   tasks.
3. Present grouped sections (Overdue → Today → This Week) with the skill's priority
   labels, collect a per-task decision — [c]omplete, [r]eschedule, [n]o date (clear via
   `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/ticktick_api.py" clear-dates`), [d]elete
   (same script, confirm first), [s]kip — then execute all actions in one pass.
4. Summarize counts per action. If all fetches are empty: "Inbox zero — nothing to triage."

Tool notes: `complete_task`/`update_task` need both `project_id` and `task_id` (take
`projectId` from the fetched task data).
