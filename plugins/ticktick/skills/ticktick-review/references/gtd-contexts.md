---
name: ticktick-review-gtd-contexts
description: GTD context mappings and review checklists for the TickTick review skill
version: 1.1.0
author: klauern
---

# TickTick Review: GTD Contexts and Review Checklists

## GTD Concept → TickTick MCP Tool Mapping

| GTD Context | MCP Tool | What it returns |
|-------------|----------|----------------|
| Inbox (unclarified) | `filter_tasks` (no date, no project filter) | All undone tasks — filter client-side for no project/due date |
| Next Actions | `filter_tasks` with `priority: [3, 5]` | High-priority tasks ready to act on |
| Today's commitments | `list_undone_tasks_by_time_query("today")` | Tasks due today |
| Overdue | `filter_tasks` with `endDate` < today | Tasks past their due date |
| This week | `list_undone_tasks_by_time_query("next7day")` | Tasks due within 7 days |
| Someday / Maybe | `filter_tasks` with `priority: [0]` | No-priority tasks |
| Waiting for | `search_task` with query "waiting" | Tasks containing "waiting" keyword |

## Daily Review Checklist

Run every morning or at start of work session:

- [ ] Check overdue tasks (`filter_tasks` with past `endDate`) — must address or reschedule each
- [ ] Review today's tasks (`list_undone_tasks_by_time_query("today")`) — confirm list is realistic
- [ ] Identify top 3 focus items for the day (pick from overdue + today, highest priority)
- [ ] Clear completed tasks (mark done anything finished since last review)
- [ ] Capture any new tasks that came in (use ticktick-capture skill)

**Target time**: 5-10 minutes

## Weekly Review Checklist

Run once per week (Friday afternoon or Monday morning):

- [ ] Process overdue backlog — complete, reschedule, or delete every overdue task
- [ ] Review this week's upcoming tasks (`list_undone_tasks_by_time_query("next7day")`)
- [ ] Check all projects (`list_projects`) — any stalled with no next action?
- [ ] Review someday/maybe list — any ready to activate?
- [ ] Plan next week — set due dates on upcoming commitments
- [ ] Capture loose ends from the week

**Target time**: 20-30 minutes

## Triage Decision Tree

```text
Is the task still relevant?
+-- No → DELETE (via ticktick_api.py delete-task script)
+-- Yes → Is it done?
    +-- Yes → COMPLETE
    +-- No → Can I do it today/this week?
        +-- Yes → Keep or reschedule to specific date
        +-- No → Reschedule to realistic future date
                  (or clear date if truly indefinite)
```

### Reschedule Heuristics

| Situation | Suggested action |
|-----------|-----------------|
| Task is 1-3 days overdue | Reschedule to today or tomorrow |
| Task is 4-7 days overdue | Reschedule to this week or next |
| Task is 2+ weeks overdue | Ask: is this still a real commitment? If not, delete |
| Recurring blocker | Consider adding "waiting" keyword and owner note |

## Priority Matrix

Use to determine which tasks to surface first in reviews:

| | Urgent | Not Urgent |
|--|--------|------------|
| **Important** | Do Now (priority=5) | Schedule (priority=3) |
| **Not Important** | Delegate / Minimize (priority=1) | Delete / Defer (priority=0) |

## Focus Item Selection

When recommending the top 3 focus items for the day:

1. **First**: Any task with priority=5 (high) due today or overdue
2. **Second**: Tasks with external dependencies (waiting on you)
3. **Third**: Tasks that unblock other work or have cascading value

Avoid surfacing low-priority tasks as focus items even if they're overdue — acknowledge them but don't let them crowd out important work.
