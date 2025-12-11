---
allowed-tools: Bash
description: List all Capacities spaces
---

# /capacities:list-spaces

List all spaces in your Capacities account.

## Usage

```bash
/capacities:list-spaces
```

## Behavior

1. Check for `CAPACITIES_API_TOKEN` environment variable
2. Execute the capacities.py script to list spaces
3. Display results with space names and IDs
4. Cache results for 5 minutes to respect rate limits

## Implementation

```bash
# Get the script path relative to this command
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"

# Run the capacities script
uv run "$SCRIPT_DIR/capacities.py" spaces --json
```

## Output

Returns JSON array of spaces:
```json
[
  {
    "id": "uuid-here",
    "title": "My Space",
    "icon": {"type": "emoji", "emoji": "📝"}
  }
]
```

## Error Handling

- **Missing token**: Prompts user to set `CAPACITIES_API_TOKEN`
- **Rate limit**: Shows wait time before retry
- **Network error**: Shows connection error message

## Notes

- Rate limit: 5 requests per 60 seconds
- Results are cached for 5 minutes
- Use `--no-cache` flag to bypass cache
