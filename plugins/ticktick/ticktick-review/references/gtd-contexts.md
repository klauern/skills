---
name: ticktick-review-gtd-contexts
description: GTD context mappings and review checklists for the TickTick review skill
version: 1.0.0
author: klauern
---

# TickTick Review: GTD Contexts and Review Checklists

## GTD Concept → TickTick MCP Tool Mapping

| GTD Context | MCP Tool | What it returns |
|-------------|----------|----------------|
| Inbox (unclarified) | `get_all_tasks` | All tasks, filter for no project/due date |
| Next Actions | `get_next_tasks` | Tasks ready to act on now |
| Engaged / Active | `get_engaged_tasks` | Tasks currently in progress |
| Today's commitments | `get_tasks_due_today` | Tasks due today |
| Overdue | `get_overdue_tasks` | Tasks past their due date |
| This week | `get_tasks_due_this_week` | Tasks due within 7 days |
| Someday / Maybe | `get_tasks_by_priority` (priority=0) | Low/no priority tasks |
| Waiting for | search_tasks with tag "waiting" | Tasks tagged as waiting |

## Daily Review Checklist

Run every morning or at start of work session:

- [ ] Check overdue tasks (`get_overdue_tasks`) — must address or reschedule each
- [ ] Review today's tasks (`get_tasks_due_today`) — confirm list is realistic
- [ ] Identify top 3 focus items for the day (pick from overdue + today, highest priority)
- [ ] Clear completed tasks (mark done anything finished since last review)
- [ ] Capture any new tasks that came in (use ticktick-capture skill)

**Target time**: 5–10 minutes

## Weekly Review Checklist

Run once per week (Friday afternoon or Monday morning):

- [ ] Process overdue backlog — complete, reschedule, or delete every overdue task
- [ ] Review this week's upcoming tasks (`get_tasks_due_this_week`)
- [ ] Check all projects (`get_projects`) — any stalled with no next action?
- [ ] Review someday/maybe list — any ready to activate?
- [ ] Plan next week — set due dates on upcoming commitments
- [ ] Capture loose ends from the week

**Target time**: 20–30 minutes

## Triage Decision Tree

```text
Is the task still relevant?
├── No → DELETE
└── Yes → Is it done?
    ├── Yes → COMPLETE
    └── No → Can I do it today/this week?
        ├── Yes → Keep or reschedule to specific date
        └── No → Reschedule to realistic future date
                  (or move to Someday if truly indefinite)
```

### Reschedule Heuristics

| Situation | Suggested action |
|-----------|-----------------|
| Task is 1–3 days overdue | Reschedule to today or tomorrow |
| Task is 4–7 days overdue | Reschedule to this week or next |
| Task is 2+ weeks overdue | Ask: is this still a real commitment? If not, delete |
| Recurring blocker | Consider adding "waiting" tag and owner note |

## Priority Matrix

Use to determine which tasks to surface first in reviews:

| | Urgent | Not Urgent |
|--|--------|------------|
| **Important** | Do Now (priority=5) | Schedule (priority=3) |
| **Not Important** | Delegate / Minimize (priority=1) | Delete / Defer (priority=0) |

## Focus Item Selection

When recommending the top 3 focus items for the day:

1. **First**: Any task with priority=5 (urgent/high) due today or overdue
2. **Second**: Tasks with external dependencies (waiting on you)
3. **Third**: Tasks that unblock other work or have cascading value

Avoid surfacing low-priority tasks as focus items even if they're overdue — acknowledge them but don't let them crowd out important work.
