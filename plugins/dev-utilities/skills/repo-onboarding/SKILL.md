---
name: repo-onboarding
description: Produce a collapsible HTML map of a repository: goal, entry points, extensions, abstractions, stack, and Mermaid diagrams, via parallel subagents. Use to onboard to a new codebase.
version: 1.0.0
author: klauern
---

# Repo Onboarding

Build a collapsible HTML map of a repository. Readable first, pretty second, accurate always.

All paths are relative to this skill's directory. Requires a pi harness with the
`subagent` tool and the `scout`, `reviewer`, and `architect` agents registered.

## Quick Start

```text
User: onboard to this repo     # or /repo-onboarding, "explain this codebase"
```

The skill runs 11 parallel read-only scouts, two reviewers, and one diagram
agent, then opens one HTML file in the browser.

## Writing rules (apply everywhere)

All output uses plain language in the ASD-STE100 style:

1. Short sentences. One idea per sentence. About 20 words or fewer for steps.
2. Active voice. Imperative mood for instructions.
3. Everyday words. One term for one thing. No jargon synonyms.
4. Do not hedge. Avoid "may", "might", "could" when a fact is certain.
5. Lead with the answer. Give the detail after.

## Phase 0 — Verify agents and gather facts

1. Confirm agents exist: `subagent({ action: "list", capabilities: true })` must
   show `scout`, `reviewer`, and `architect`. If `architect` is missing, copy
   `agents/architect.md` to `~/.pi/agent/agents/architect.md`.
2. Gather facts to a file:
   ```bash
   python3 scripts/repo-facts.py <REPO_PATH> > /tmp/repo-onboarding-facts.json
   ```
   If no path is given, use the current directory. Do not ask for a path.

## Phase 1 — Prepare and launch the subagent workflow

```bash
python3 scripts/prepare_workflow.py <REPO_PATH> /tmp/repo-onboarding-facts.json
# add --quick for a 6-scout pass (goal, profile, entry, ext, abs)
```
This writes `/tmp/repo-onboarding-analyze.js`. Launch it (blocking — you need the results):

```js
subagent({
  workflowScriptPath: "/tmp/repo-onboarding-analyze.js",
  cwd: "<REPO_PATH>",
  async: false
});
```

Two waves run inside the script:

- **Wave 1** — 11 parallel read-only `scout` agents: `goal`, `profile`, `entry`,
  `ext`, `abs`, `data`, `runtime`, `testing`, `repos`, `contrib`, `rationale`.
- **Wave 2** — three parallel agents fed wave-1 output: `missed` (reviewer: what
  was omitted), `verify` (reviewer: errors and inconsistencies), `viz`
  (`architect`: Mermaid/SVG diagrams).

The returned JSON is `{ scouts: [{key, data}], missed, verify, diagrams }`.

## Phase 2 — Synthesize the data object

Apply `verify.corrections` to the scout data (fix wrong text and paths, drop
duplicates), then assemble one JSON object for the template. The full schema and
the field-to-scout mapping are in
[references/data-schema.md](references/data-schema.md). Write the object to
`/tmp/repo-onboarding-<repo>.json`.

## Phase 3 — Render and open

```bash
python3 scripts/render.py /tmp/repo-onboarding-<repo>.json
open /tmp/repo-onboarding-<repo>.html
```

## Phase 4 — Recap

Print a 3–4 line plain-language recap, then offer to drill into the single most
interesting section.

## Notes

- Children are read-only. Only the parent writes files.
- `--quick` skips `data`, `runtime`, `testing`, `repos`, `rationale` (6 scouts).
- Helpers are Python on purpose: short, I/O-bound, stdlib-only. The JSON contract
  is fixed, so swapping them for a compiled binary later is a drop-in change.
