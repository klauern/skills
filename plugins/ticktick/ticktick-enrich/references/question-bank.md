# Enrich — Question Bank & Heuristics

Detailed reference for `ticktick-enrich`. Loaded on demand.

## Interview principle

- Walk the tree top-to-bottom; later answers may make a lower question moot.
- Every question carries **your recommended answer** so the user can accept fast.
- **Explore before asking**: if the task text or Phase-2 lookups already answer a
  question, state what you found and skip it (or ask only to confirm).
- **Absorb multi-answer replies**: one user message often resolves several questions
  at once — take all of them and skip the satisfied questions; don't re-ask.
- **Hybrid input style**:
  - *Free-text* for prose fields (Done-when, Context/Links) — offer recommended
    phrasing the user can accept.
  - *AskUserQuestion option prompts* for mechanical fields (Priority, Timeframe,
    Labels). Recommended option **first**, suffixed "(Recommended)". Batch 2–4 into
    one call. Labels = multi-select from the tag vocabulary.

## Already-tracked-elsewhere branch (check before the interview)

If Phase 2 resolved a reference that IS the system of record for this work (open Jira
ticket, owning GitHub issue/PR), ask first whether to **close the TickTick task as a
duplicate** rather than enrich it. Recommend close when:

- The Jira/GitHub item is open and actively owned (has an assignee, recent activity).
- The TickTick task adds no detail the tracker lacks.

Recommend *keep & enrich* only when the user wants it as a personal reminder or
next-action nudge distinct from the tracker. Close via `complete_task`.

## Question tree

### 1. Done when? (acceptance + title)
> "What does *done* look like for this? I'll sharpen the title to match.
> Recommended: `<restated, verb-first title>`."

- Goal: a verb-first, specific title and a one-line acceptance criterion.
- If the title is already a clear action, confirm and move on.
- Capture the criterion into the `## Done when` line of the content block.

### 2. Priority (0 / 1 / 3 / 5)
> "Priority? Recommended: **<n>** because <signal>."

Recommendation heuristics (pick the highest that genuinely applies — lean
conservative; when unsure between two levels, recommend the lower one):
- **5 (high)**: a real near-term deadline, blocks others, active security/compliance
  risk, someone is explicitly waiting, production impact.
- **3 (medium)**: clear owner + this-sprint relevance, a follow-up the user committed to.
- **1 (low)**: useful but no deadline, polish, "should look into", asks/questions.
- **0 (none)**: idea/someday, no commitment.

**Overdue ≠ high.** A passed due date (or a 2099/placeholder date) is a *recency*
signal that the task has been sitting, not evidence of urgency. Do not inflate
priority just because a date is in the past — judge urgency from the work itself.

Never output 2 or 4 — invalid in TickTick.

### 3. Timeframe (date or someday)
> "When does this need to happen? Recommended: <date | 'someday'>."

- Convert relative answers ("Friday", "next week") to ISO 8601 **with offset**,
  respecting the task's `timeZone` (default `America/Chicago`).
- All-day item → keep `isAllDay: true`, time at `00:00` local.
- "Someday" / no date → set `dueDate` (and `startDate` if present) to the clear
  sentinel `1970-01-01T00:00:00.000+0000`. Also treat an existing `2099-01-01` as
  "someday" on read (it is a placeholder, not a real deadline).
- If a recurrence is implied ("every month"), suggest a `repeatFlag` RRULE but only
  set it if the user confirms.

### 4. Labels (tags)
> "Tags? Recommended: <subset of existing vocab>. Add/remove any?"

- Propose from the **existing vocabulary** below. Reuse beats inventing.
- Union with the task's current tags; dedup; lower-case.
- Do not recreate polluted/junk tags (e.g. `16157)`, `3334`, ` ``` `).

### 5. Links / context
> "Any ticket, doc, repo, or person to attach? I found: <Phase-2 results>."

- Fold confirmed links + resolved-reference summaries into `## Links` / `## Context`.
- Keep summaries short (a line or two each), with the URL.

### 6. Next action (optional — chunky items only)
> "First physical step? Recommended: <smallest next action>."

- Only ask when the task is multi-step. Put it first in `## Done when` or as a
  checklist if the user wants sub-items.

## Existing tag vocabulary (controlled list)

Work / security / infra:
`aws`, `azure`, `guild-azure`, `zig`, `zig-taxonomy`, `fsec`, `secure`,
`compliance`, `docs`, `jira`, `ai-tooling`, `research`, `incident-followup`,
`work-link`, `project-pine`, `engineering`, `engineering-all`.

Personal / other (only if clearly relevant):
`finances`, `purchase`, `gift`, `read`, `read-later`, `books`, `watch`,
`veterans`, `ec`, `ec-veterans`, `scouts`, `writing`, `actionable`.

> Ignore junk tags that exist from bad imports: `16157)`, `3334`, `35445`,
> `35542`, ` ``` `, `ask-`, `dsp`, `td`. Do not propose or recreate these.

Refresh the live list anytime with `mcp__ticktick__list_tags`.

## Reference-detection regexes (Phase 2)

Scan `title` + `content`. Resolve only matches that are present.

| Reference | Pattern (illustrative) | Resolver |
|-----------|------------------------|----------|
| Jira key | `\b(FSEC|PCI|SECURE|PLAN|LOCKBOX)-\d+\b` | jira-core skill / `jira` CLI |
| GitHub repo | `\bzendesk/[a-z0-9._-]+\b` | `gh repo view` |
| GitHub PR/issue | `github\.com/[^/]+/[^/]+/(pull|issues)/\d+` | `gh pr view` / `gh issue view` |
| Confluence | `\.atlassian\.net/wiki/` | confluence skill |
| Slack | `\bzendesk\.slack\.com/archives/\S+` | slack read (if available) |
| Capacities | `capacities://|app\.capacities\.io/` | note as external ref (no API here) |
| Google Docs | `docs\.google\.com/\S+` | WebFetch (if allowed) |
| Person | capitalized first-name mentions near "ask/message/follow-up" | cerebro lookup |

Degrade gracefully — a missing/erroring resolver is noted, not fatal.

## Content block template

Compose into `content` (markdown). Preserve meaningful pre-existing notes by folding
them into `## Context`. Omit empty sections.

```markdown
## Done when
<one-line acceptance criterion>

## Context
<why this exists / background, including any prior note text>

## Links
- <label>: <url>
- Jira FSEC-1234: <one-line status summary> — <url>

## Next action
<smallest first step, if captured>
```

## Worked example

Task: "log in to azure zendesk prod through Okta" / content "Why? (review before acting)".

- Phase 2: no Jira/repo/URL references → nothing to resolve.
- Interview:
  1. Done when? → "Confirmed I can reach the Azure prod portal via Okta SSO."
  2. Priority? → recommend **1** (no deadline, exploratory) → user picks 3.
  3. Timeframe? → "this week" → next Friday, all-day, `America/Chicago`.
  4. Labels? → recommend `azure`, `secure`.
  5. Links? → none.
- Write back: content block + `priority: 3` + `tags: [azure, secure]` +
  `dueDate` set to Friday. Confirm before/after, show task id.
