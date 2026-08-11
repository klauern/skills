---
allowed-tools: Bash(uv run:*)
description: Search content in Capacities spaces
argument-hint: "<term> [--space-ids <ids>] [--mode fullText|title] [--filter <structure-ids>]"
---

# /capacities:search

Search across one or more Capacities spaces. Modes: `title` (default, fast) or
`fullText` (comprehensive); `--filter` limits results to specific structure IDs.

## Usage

```bash
/capacities:search "project plan" --space-ids abc-123
/capacities:search "quarterly review" --space-ids abc-123,def-456 --mode fullText
```

## Behavior

Follow the **capacities-api** skill (auth check → space resolution → execute):

```bash
# If --space-ids is missing, list spaces and ask which to search
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" spaces

uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" search "$TERM" \
    --space-ids "$SPACE_IDS" --mode "${MODE:-title}" ${FILTER:+--filter "$FILTER"} --json
```

Present results with their highlights, relevance-ordered. Rate limit is a generous
120/60s — see the skill's API reference for schemas.
