---
allowed-tools: ["mcp__ticktick__search_task", "mcp__ticktick__get_task_by_id", "mcp__ticktick__update_task", "mcp__ticktick__list_projects", "mcp__ticktick__list_tags", "WebSearch", "WebFetch"]
description: Enrich a TickTick task — sharpen the title, flesh out the description, add subtasks, and infer metadata (preview before write)
---

# /ticktick:enrich

Turn a thin, one-line TickTick task into a well-formed, actionable one:

- A sharper, action-first **title**
- A fleshed-out **description** (context, goal, acceptance criteria, notes)
- A **subtask checklist** breaking the work into concrete steps
- Metadata **you provide** (priority, dates, tags, project) — it asks, never guesses
- Optional **references** you supply (or research it explicitly asks to do)

This command **always shows a before → after preview and waits for your approval** before writing anything back to TickTick.

## Usage

```bash
/ticktick:enrich [task id | search terms]
```

## Arguments

- `[task id | search terms]` (optional):
  - A TickTick task **ID** (24-char hex) → resolved directly via `get_task_by_id`
  - **Search terms** → matched against task titles via `search_task`
  - **Omitted** → ask the user which task to enrich (offer a search)

## Behavior

1. **Resolve** the target task. If search terms match multiple tasks, list the candidates and ask which one. Capture its `projectId` (needed for the write).
2. **Read current state** and **spot gaps**: unclear goal, no steps, ambiguous title, no deadline or stated priority.
3. **Interview** you to fill those gaps — focused questions only; it never invents names, dates, URLs, or scope you didn't state. If you say "you draft it," it proposes and lets you edit.
4. **Draft** from your answers: sharper title, description, subtasks, and only the metadata you supplied.
5. **Preview** a before → after diff of every field that would change. Subtasks and anything "open / not applied" are shown clearly.
6. **Wait for approval.** On yes → call `update_task`. On edits → adjust and re-preview. On no → make no changes.
7. **Confirm** what changed.

## Metadata policy (user-supplied only)

- **Sets metadata only from what you tell it** — it won't infer priority from keywords or invent a due date.
- It never overwrites an existing value without your explicit yes.
- Priority mapping (when you express importance): urgent/critical → 5, high → 3, medium → 1, low/none → 0.
- A project move is *suggested*, not done silently (use `move_task`).

## Implementation

The detailed workflow lives in the **`ticktick-enrich`** skill. Follow its phases:

1. Resolve task → 2. Analyze → 3. Draft enrichment → 4. Preview & gate → 5. Write via `update_task` → 6. Confirm.

`update_task` takes `task_id` **plus a full `task` object** (camelCase fields). The call operates on the whole task, so **read the task with `get_task_by_id`, merge your enrichment into that object, and send it back complete** — this avoids wiping fields you didn't touch.

To get a rich description **and** native checkable subtasks, set the task to checklist kind: a `TEXT`/`NOTE` task shows `content`; a `CHECKLIST` task shows `desc` + checkable `items`.

```python
update_task(
    task_id="<task_id>",
    task={
        "id": "<task_id>",
        "projectId": "<unchanged projectId>",   # carry over; required by the model
        "title": "Sharpened title",
        "kind": "CHECKLIST",                     # so desc + items both render
        "desc": "## Goal\n...\n\n## Acceptance criteria\n- [ ] ...\n\n## References\n- ...",
        "items": [
            {"title": "First step", "status": 0},
            {"title": "Second step", "status": 0},
        ],
        "priority": 3,                           # only if it was empty (conservative)
        "tags": ["existing-tag"],                # carry existing; add only if empty
        # ...carry over any other existing fields unchanged
    },
)
```

- Read with `get_task_by_id` (needs only `task_id`; it scans all projects). Carry its `projectId` and existing fields back in the `task` object.
- **No subtasks** (notes-only enrichment): leave `kind` alone and put the description in `content` instead of `desc`.
- **Clearing a date**: the MCP can't send null — set `dueDate`/`startDate` to `"1970-01-01T00:00:00.000+0000"`.
- **References** (per project default): append a `## References` section to `content` — do not put links in a comment unless the user asks.

## Output

```text
Enriched task:
  Title:    Renew SSL cert for api.example.com  (was: "ssl")
  Project:  Work
  Priority: HIGH (was: none)            ← filled (was empty)
  Subtasks: 4 added
  Notes:    +Goal, +Acceptance criteria, +References (2 links)
  ID:       abc123xyz

Suggestions (not applied):
  - Due date: none set — consider before cert expiry (2026-06-15)
```

## Examples

```bash
# Enrich by search terms
/ticktick:enrich renew ssl cert

# Enrich by explicit task ID
/ticktick:enrich 6f1e2a9c0b3d4e5f60718293

# Interactive (asks which task)
/ticktick:enrich
```

## Notes

- Requires the `ticktick` MCP server (verify with `/ticktick:setup`).
- Read-then-write: a stale read can clobber concurrent edits, so the preview reflects the task as just read — re-resolve if the user pauses for a long time before approving.
- Pairs well with `/ticktick:capture` (create thin) → `/ticktick:enrich` (flesh out) → `/ticktick:today` (work it).
