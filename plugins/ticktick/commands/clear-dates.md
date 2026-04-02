---
allowed-tools: Bash
description: Remove due date and start date from a TickTick task
---

# /ticktick:clear-dates

Clear the due date and start date from a TickTick task. This works around the MCP server's inability to send null date values.

## Usage

```bash
/ticktick:clear-dates
```

The user must provide a task ID and project ID. If not given, ask for them.

## Implementation

Run the script to clear dates:

```bash
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
uv run "$SCRIPT_DIR/ticktick_api.py" clear-dates --task-id <TASK_ID> --project-id <PROJECT_ID> --json
```

Replace `<TASK_ID>` and `<PROJECT_ID>` with the values from the user or from a prior MCP tool call.

## Notes

- Requires `TICKTICK_ACCESS_TOKEN` environment variable
- The project ID is the list/project the task belongs to (often returned as `projectId` in task data)
- Both `dueDate` and `startDate` are cleared simultaneously
