---
allowed-tools: Bash(uv run:*)
description: List all Capacities spaces
---

# /capacities:list-spaces

List all spaces in your Capacities account with their names and IDs.

## Behavior

Follow the **capacities-api** skill (verify `CAPACITIES_API_TOKEN` first):

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" spaces --json
```

Results are cached 5 minutes (rate limit 5/60s); add `--no-cache` to bypass. Error
recovery lives in the skill's API reference.
