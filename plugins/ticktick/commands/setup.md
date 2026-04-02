---
allowed-tools: ["Bash", "mcp__ticktick__list_projects"]
description: Verify TickTick MCP connection and list projects
---

# /ticktick:setup

Verify the TickTick MCP server is connected and working.

## Usage

```bash
/ticktick:setup
```

## Behavior

1. Call `list_projects` to verify the MCP connection is alive
2. Display the list of projects with their IDs
3. If the connection fails, show troubleshooting steps

## Implementation

1. Call `list_projects` via the MCP server
2. If successful, display the projects:

```text
TickTick connection verified.

Projects:
  - Work (id: abc123)
  - Personal (id: def456)
  - Inbox (id: ghi789)
```

3. If the MCP tool is not available or the call fails, display:

```text
TickTick MCP server is not connected.

To add it, run:
  claude mcp add --transport http ticktick https://mcp.ticktick.com/ -s user

Then restart Claude Code — it will prompt for TickTick OAuth on first use.
```

## Notes

- This plugin requires a global `ticktick` MCP server configured via `claude mcp add`
- The official TickTick MCP server at mcp.ticktick.com handles OAuth automatically
- No environment variables are needed for the MCP connection
- `TICKTICK_ACCESS_TOKEN` is only needed for the `ticktick_api.py` script (clear-dates, delete-task)
