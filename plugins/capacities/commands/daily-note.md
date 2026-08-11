---
allowed-tools: Bash(uv run:*)
description: Add content to today's daily note in Capacities
argument-hint: "--text <markdown> [--space-id <id>] [--no-timestamp]"
---

# /capacities:daily-note

Append markdown content to today's daily note in a Capacities space (creates the note
if it doesn't exist; timestamps by default).

## Usage

```bash
/capacities:daily-note --text "Idea: build a CLI tool" --space-id abc-123
/capacities:daily-note --text "## Team Sync\n- Q4 roadmap" --space-id abc-123 --no-timestamp
```

## Behavior

Follow the **capacities-api** skill (auth check → space resolution → execute):

```bash
# If --space-id is missing, list spaces and ask which to use
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" spaces

uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" daily-note \
    --space-id "$SPACE_ID" --text "$TEXT" ${NO_TIMESTAMP:+--no-timestamp} --json
```

Rate limit is 5/60s — see the skill's API reference for limits and error recovery.
