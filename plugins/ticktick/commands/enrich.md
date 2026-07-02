---
allowed-tools: ["mcp__ticktick__search_task", "mcp__ticktick__get_task_by_id", "mcp__ticktick__update_task", "mcp__ticktick__list_projects", "mcp__ticktick__list_tags", "WebSearch", "WebFetch"]
description: Enrich a TickTick task — sharpen the title, flesh out the description, add subtasks, and confirm metadata (preview before write)
argument-hint: "[task id | search terms]"
---

# /ticktick:enrich

Turn a thin, one-line TickTick task into a well-formed, actionable one — sharper title,
fleshed-out description, subtask checklist, and only the metadata you supply.

## Usage

```bash
/ticktick:enrich 65f2c8a1b3d94e0012ab34cd    # by task ID (24-char hex)
/ticktick:enrich renew ssl                   # by search terms
/ticktick:enrich                             # asks which task to enrich
```

## Behavior

Invoke the **ticktick-enrich** skill:

1. Resolve the target task (ID → `get_task_by_id`; terms → `search_task`, asking on
   multiple matches). Capture `projectId` for the write.
2. Spot gaps, interview you to fill them (never fabricates facts), draft from your
   answers, and set only metadata you stated.
3. **Always previews a before → after diff and waits for approval** before calling
   `update_task` with the full merged task object.

The field reference, templates, and metadata policy live in the skill and its
enrichment-guide reference.
