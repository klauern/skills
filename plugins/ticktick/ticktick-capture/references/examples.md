---
name: ticktick-capture-examples
description: Natural-language capture examples and field reference for the TickTick capture skill
version: 1.0.0
author: klauern
---

# TickTick Capture: Examples and Field Reference

## Natural Language → Field Mapping

| Input | title | dueDate | priority | project hint |
|-------|-------|---------|----------|-------------|
| "Buy milk tomorrow" | Buy milk | tomorrow → next day | 0 | — |
| "Fix login bug - high priority, due Friday" | Fix login bug | next Friday | 3 | — |
| "Review PR by end of day" | Review PR | today 17:00 | 0 | — |
| "Call dentist next Monday at 2pm" | Call dentist | next Mon 14:00 | 0 | — |
| "Urgent: deploy hotfix" | Deploy hotfix | — | 5 | — |
| "Add dark mode to Work project, low priority" | Add dark mode | — | 0 | Work |
| "Finish report in 3 days" | Finish report | today + 3d | 0 | — |
| "Important: renew subscription by end of week" | Renew subscription | Friday EOD | 3 | — |
| "Write tests for auth module - medium priority" | Write tests for auth module | — | 1 | — |
| "Buy birthday gift for Sarah, due next Saturday" | Buy birthday gift for Sarah | next Sat | 0 | — |

## Date Expression → ISO 8601

| Expression | Resolution |
|-----------|------------|
| "today" | Current date, no time |
| "tomorrow" | Current date + 1 day |
| "tonight" / "this evening" | Current date 20:00 |
| "end of day" / "EOD" | Current date 17:00 |
| "next Monday" | Next occurrence of Monday |
| "this week" / "end of week" | Friday of current week |
| "next week" | Monday of next week |
| "in 3 days" | Current date + 3 days |
| "by Friday" | Upcoming Friday |
| "end of month" | Last day of current month |

Always output ISO 8601 with timezone offset: `2025-03-07T14:00:00+00:00`
Use UTC if user timezone is unknown. Omit time component for date-only due dates.

## Priority Keyword Mapping

| Signal words | priority value |
|-------------|---------------|
| "urgent", "ASAP", "critical", "immediately" | 5 |
| "high priority", "important", "must do" | 3 |
| "medium", "normal", "moderate" | 1 |
| "low priority", "someday", "when I can" | 0 |
| (no signal) | 0 |

## `create_task` MCP Call Shape

```json
{
  "title": "Fix login bug",
  "projectId": "abc123-uuid",
  "dueDate": "2025-03-07T17:00:00+00:00",
  "priority": 5,
  "tags": ["bug", "auth"],
  "content": "Users can't log in with SSO. Check the OAuth callback handler."
}
```

Minimal (title only):
```json
{
  "title": "Buy milk"
}
```

## `batch_create_tasks` MCP Call Shape

When user provides a list, structure as array:
```json
{
  "tasks": [
    { "title": "Review PR #42", "priority": 3 },
    { "title": "Update docs", "dueDate": "2025-03-10T00:00:00+00:00" },
    { "title": "Deploy to staging", "priority": 5, "tags": ["deploy"] }
  ]
}
```

## Project Resolution Pattern

1. Call `get_projects` → returns array of `{ id, name }` objects
2. Fuzzy match user's project hint against `name` fields
3. If single confident match → use that `id`
4. If multiple matches or no match → present list to user:
   ```text
   Which project?
   1. Work
   2. Personal
   3. Side Projects
   (or press Enter for Inbox)
   ```
