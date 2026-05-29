---
allowed-tools: ["mcp__ticktick__get_task_by_id", "mcp__ticktick__get_project_with_undone_tasks", "mcp__ticktick__filter_tasks", "mcp__ticktick__update_task", "mcp__ticktick__batch_update_tasks", "mcp__ticktick__complete_task", "mcp__ticktick__list_tags", "mcp__ticktick__list_projects", "mcp__ticktick__add_comment", "AskUserQuestion"]
description: Interactively enrich a vague TickTick task (or a whole list) into an actionable item
---

# /ticktick:enrich

Turn a half-sentence TickTick capture into an actionable task: gather context, then
interview you one question at a time to fill in priority, timing, labels, links, and
notes — and write it all back.

## Usage

```bash
/ticktick:enrich [task title | task id | project name]
```

## Arguments

- `[task title | task id]` — enrich a single task (interactive, one question at a time)
- `[project name]` (e.g. `Work`) — batch mode: loop over the project's undone tasks,
  sparsest first, enriching one at a time with confirm-and-continue
- *(omitted)* — ask which task to enrich, or offer "the sparsest task in Work"

## Behavior

### Single task
1. Resolve the task (`get_task_by_id`, or match a title within its project)
2. Auto-gather: scan title/content for references (Jira keys, repos, URLs, people)
   and resolve only those already present — never search blindly
3. If a resolved reference IS the canonical tracker (open, owned Jira/GitHub item),
   offer **close-as-duplicate** (`complete_task`) before enriching
4. Interview, skipping anything already answered. Free-text for done-when/context;
   AskUserQuestion option prompts (recommended-first) for priority/timeframe/labels
5. Merge answers into a full task object and `update_task` — write a markdown
   content block AND set priority, tags, and dates
6. Show a before/after of changed fields + the task ID

### Batch mode (project name)
1. Fetch undone tasks via `get_project_with_undone_tasks`
2. Rank by sparseness (empty content, no tags, priority 0, placeholder date, short title)
3. Enrich the sparsest, confirm, then offer the next; "stop" exits with a summary

## Implementation

This command activates the `ticktick-enrich` skill, which carries the full workflow,
question tree, recommendation heuristics, tag vocabulary, detection regexes, and the
content template (`ticktick-enrich/references/question-bank.md`).

Build a **merged** task for `update_task` — preserve `id`, `etag`, `kind`,
`projectId`, and any unchanged fields; do not send a sparse patch.

## Output

```text
Enriched task:
  Title:    Confirm Azure prod access via Okta SSO
  Priority: 0 → 3 (medium)
  Tags:     (none) → azure, secure
  Due:      someday → 2026-06-05
  Notes:    + Done when / Context / Links block
  ID:       697b722a809a9107ca772506
```

## Examples

```bash
# Single task by title
/ticktick:enrich log in to azure zendesk prod through Okta

# Single task by id
/ticktick:enrich 697b722a809a9107ca772506

# Batch over the Work list, sparsest first
/ticktick:enrich Work

# Interactive — let it pick the sparsest
/ticktick:enrich
```

## Notes

- Priority scale: **0=none, 1=low, 3=medium, 5=high** — 2 and 4 are invalid.
- Dates are ISO 8601 with offset; the task's `timeZone` is preserved (default
  `America/Chicago`). "Someday" clears the date via the `1970-01-01` sentinel; an
  existing `2099-01-01` is treated as "someday" on read.
- Tags reuse the existing vocabulary (`aws`, `azure`, `zig`, `fsec`, `secure`,
  `compliance`, `docs`, `jira`, `ai-tooling`, `work-link`, …) rather than inventing
  new ones; new tags are unioned with the task's existing tags.
- Opportunistic lookups (jira-core, confluence, cerebro, `gh`) are all optional —
  the skill degrades gracefully to light parsing when a tool is unavailable.
```
