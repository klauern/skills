---
allowed-tools: Bash(uv run:*)
description: Get structures and collections for a Capacities space
argument-hint: "[space-id]"
---

# /capacities:space-info

Show a space's structures (object types), property definitions, and collections —
useful for finding collection IDs to filter searches and understanding a space before
saving content.

## Usage

```bash
/capacities:space-info abc-123
/capacities:space-info          # lists spaces, then asks which one
```

## Behavior

Follow the **capacities-api** skill (auth check → space resolution → execute):

```bash
# If no space-id argument, list spaces and ask which to inspect
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" spaces

uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" space-info "$SPACE_ID" --json
```

Results are cached 10 minutes per space (rate limit 5/60s); `--no-cache` bypasses.
