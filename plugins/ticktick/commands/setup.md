---
allowed-tools: ["Bash", "mcp__plugin_ticktick_ticktick__list_projects"]
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

3. If the call fails, display:

```text
TickTick MCP server is not connected.

Troubleshooting:
  1. Run: claude mcp list
  2. Look for "ticktick" — it should show "Connected"
  3. If missing, the plugin may need reinstalling: /plugin install ticktick@klauern-skills
  4. If "Needs authentication", restart Claude Code — it will prompt for OAuth
```

## Notes

- The official TickTick MCP server at mcp.ticktick.com handles OAuth automatically via Claude's MCP auth flow
- No environment variables are needed for the MCP connection itself
- `TICKTICK_ACCESS_TOKEN` is only needed for the `ticktick_api.py` script (clear-dates, delete-task)
