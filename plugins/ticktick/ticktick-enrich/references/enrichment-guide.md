# TickTick Enrichment Guide

Detailed patterns for the `ticktick-enrich` skill. Load when actually drafting an enrichment.

## Description template (markdown)

Goes in `desc` when the task is a `CHECKLIST` (has subtasks), or `content` for a plain `TEXT`/`NOTE` task.

Adapt to the task — drop sections that add no value rather than padding.

```markdown
## Goal
One or two sentences: what "done" looks like and why it matters.

## Acceptance criteria
- [ ] Concrete, checkable outcome
- [ ] Another verifiable condition

## Notes
Context, constraints, links to prior decisions, gotchas.

## References
- [Title](https://example.com) — why it's relevant
```

- Keep **Goal** even on small tasks — it forces clarity.
- Use **Acceptance criteria** when "done" is ambiguous; skip for trivial tasks.
- **References** is appended only when web research was done (per project default — links go in the description, not a comment).

## Interview prompts (the heart of enrichment)

Enrichment is an interview, not a guess. Read the task, then ask only for what's missing — batch the questions, keep them short, and accept "skip" for any.

- **Goal**: "What does *done* look like for this?"
- **Ambiguous title**: "What is '<bare word>' here — a place, person, tool?" (e.g. "Gable")
- **Steps**: "Any steps you already have in mind? I can propose a draft if not."
- **Deadline / priority**: "Is there a deadline? How important — urgent / important / whenever?"
- **Context / links**: "Any links, people, or background I should capture?"
- **Research offer**: "Want me to look up <X> and add a couple of links?" — only with a yes.

Rules:
- Never fabricate a name, date, URL, or scope the user didn't give.
- If the user says "you draft it," propose clearly-labeled options and let them edit; nothing is applied until they approve at the preview gate.
- Don't re-ask anything the task's existing fields already answer.

## Title rewriting

Sharpen, don't rephrase for its own sake. Preserve the user's intent.

| Before | After | Why |
|--------|-------|-----|
| `ssl` | `Renew SSL cert for api.example.com` | Verb + specific object |
| `taxes` | `File 2025 federal taxes` | Scope + timeframe |
| `call dr` | `Schedule annual physical with Dr. Lee` | Action is the next physical step |
| `look into k8s thing` | `Diagnose pod OOMKills in prod cluster` | Names the actual problem |

Rules: action verb first; one specific object; drop filler ("look into", "the thing"); keep it short enough to scan in a list.

## Subtask heuristics (`items`)

- 2–7 steps. Fewer means the task was already atomic; more means it's really an epic — flag splitting instead of cramming.
- Each subtask is a concrete next physical action, ordered as you'd actually do them.
- Don't restate the title as a subtask. Don't add "done?"-style checkboxes — acceptance criteria live in the description.
- **Recurring tasks** (`repeatFlag` set): do NOT convert to `CHECKLIST` — native `items` re-check oddly each cycle. Keep `kind: TEXT`, embed a markdown `- [ ]` checklist in `content`, and leave `dueDate`/`repeatFlag`/`reminders` untouched. Enrichment here is lighter: a short Goal + a repeatable mini-procedure.

Example for "Renew SSL cert for api.example.com":
1. Confirm current cert expiry and issuer
2. Generate CSR for api.example.com
3. Request/issue renewed cert
4. Deploy cert and reload the load balancer
5. Verify chain with `openssl s_client`

## Conservative metadata rules

All live inside the `task` object (camelCase). **Set only from what the user tells you — never infer.**

| Field | `task` field | Set when… | Notes |
|-------|--------------|-----------|-------|
| Priority | `priority` | the user states importance | urgent/critical→5, important→3, nice-to-have→1; else leave as-is |
| Due date | `dueDate` | the user gives a deadline | ISO 8601; clear with `1970-01-01T00:00:00.000+0000` |
| Start date | `startDate` | the user gives a start | rarely; ISO 8601 |
| Tags | `tags` | the user names tags | reuse existing (`list_tags`); confirm new ones |
| Project | `projectId` | the user asks to move | prefer `move_task`; otherwise just *suggest* |

Never change an existing value without the user's explicit yes. Anything unconfirmed goes under **"Open / suggested (not applied)"** in the preview.

## Research / links

- Only search when external context genuinely helps (APIs, products, how-to, vendor docs).
- 1–3 links max, each with a one-line "why relevant".
- Verify the link resolves (`WebFetch`) before adding; drop dead links.
- Append under `## References` in `content`. Never replace the user's existing notes — append.

## Worked example

**Before**
```
Title:    deploy thing
content:  (empty)
priority: 0 (none)
items:    none
tags:     none
project:  Inbox
```

**After (previewed, then written on approval)**
```
Title:    Deploy v2.3 API to staging and smoke-test
kind:     CHECKLIST          ← so desc + items both render
desc:
  ## Goal
  Get v2.3 onto staging so QA can validate before the prod release.

  ## Acceptance criteria
  - [ ] v2.3 image running on staging
  - [ ] Smoke tests green
  - [ ] Release notes linked in #releases

  ## References
  - [Staging deploy runbook](https://wiki/…) — exact steps + rollback
priority: 3 (medium)        ← set (you said "important")
tags:     [deploy]          ← set (you named #deploy; matched existing tag)
items:                      ← 4 subtasks from the steps you described (kind → CHECKLIST)
  - Tag and build the v2.3 image
  - Apply the staging manifest
  - Run the smoke-test suite
  - Post status in #releases

Suggestions (not applied):
  - Move out of Inbox → "Work" project (needs move_task)
  - Due date: none — set before the prod release window?
```
