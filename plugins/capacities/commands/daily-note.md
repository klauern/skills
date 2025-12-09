---
allowed-tools: Bash
description: Add content to today's daily note in Capacities
---

# /capacities:daily-note

Append markdown content to today's daily note in a Capacities space.

## Usage

```bash
/capacities:daily-note --text <markdown> [--space-id <id>] [--no-timestamp]
```

## Arguments

- `--text` (required): Markdown text to append to the daily note
- `--space-id` (required if not prompted): Target space UUID
- `--no-timestamp` (optional): Don't add a timestamp to the entry

## Behavior

### With all required arguments:
1. Append the markdown text to today's daily note
2. By default, adds a timestamp before the content
3. Creates the daily note if it doesn't exist

### Hybrid mode (missing space-id):
1. List available spaces
2. Ask user which space to use
3. Execute append with selected space

## Implementation

```bash
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"

# If no space-id, list spaces first
if [ -z "$SPACE_ID" ]; then
    echo "Available spaces:"
    uv run "$SCRIPT_DIR/capacities.py" spaces
    echo ""
    echo "Provide --space-id to specify target space"
    exit 0
fi

uv run "$SCRIPT_DIR/capacities.py" daily-note \
    --space-id "$SPACE_ID" \
    --text "$TEXT" \
    ${NO_TIMESTAMP:+--no-timestamp} \
    --json
```

## Output

Returns JSON confirmation:
```json
{
  "success": true,
  "message": "Added to daily note"
}
```

## Examples

```bash
# Quick thought capture
/capacities:daily-note \
    --space-id abc-123 \
    --text "Idea: Build a CLI tool for API testing"

# Meeting notes
/capacities:daily-note \
    --space-id abc-123 \
    --text "## Team Sync\n- Discussed Q4 roadmap\n- Action: Review PRs by Friday"

# Without timestamp (for structured entries)
/capacities:daily-note \
    --space-id abc-123 \
    --text "## End of Day Summary\n- Completed feature X\n- Started on bug Y" \
    --no-timestamp
```

## Use Cases

- **Quick capture**: Jot down thoughts during work
- **Meeting notes**: Log discussion points and action items
- **Task logging**: Record completed work throughout the day
- **Journaling**: Add reflections and insights
- **Integration**: Pipe output from other tools to daily notes

## Markdown Support

The text field supports full markdown:
- Headers (`## Title`)
- Lists (`- item` or `1. item`)
- Bold/italic (`**bold**`, `*italic*`)
- Code blocks (triple backticks)
- Links (`[text](url)`)
- And more...

## Notes

- Rate limit: 5 requests per 60 seconds
- By default, entries get a timestamp prefix
- Use `--no-timestamp` for cleaner structured entries
- Great for automation and integration workflows
- Clears local cache after saving (data changed)
