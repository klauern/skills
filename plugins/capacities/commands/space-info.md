---
allowed-tools: Bash
description: Get structures and collections for a Capacities space
---

# /capacities:space-info

Get detailed information about a Capacities space including its structures (object types) and collections.

## Usage

```bash
/capacities:space-info [space-id]
```

## Arguments

- `space-id` (optional): UUID of the space. If not provided, list spaces and prompt for selection.

## Behavior

### With space-id provided:
1. Fetch space info directly using the provided ID
2. Display structures, property definitions, and collections

### Without space-id (hybrid mode):
1. First run `/capacities:list-spaces` to show available spaces
2. Ask user to select or provide a space ID
3. Then fetch and display the space info

## Implementation

```bash
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"

if [ -n "$1" ]; then
    # Space ID provided
    uv run "$SCRIPT_DIR/capacities.py" space-info "$1" --json
else
    # List spaces first, then prompt
    echo "Available spaces:"
    uv run "$SCRIPT_DIR/capacities.py" spaces
    echo ""
    echo "Provide a space ID to get detailed info."
fi
```

## Output

Returns JSON with structures:
```json
{
  "structures": [
    {
      "id": "structure-uuid",
      "title": "Note",
      "pluralName": "Notes",
      "labelColor": "blue",
      "propertyDefinitions": [...],
      "collections": [
        {"id": "coll-uuid", "title": "My Collection"}
      ]
    }
  ]
}
```

## Use Cases

- Discover what object types exist in a space
- Find collection IDs for filtering searches
- Understand the structure before saving content

## Notes

- Rate limit: 5 requests per 60 seconds
- Results are cached for 10 minutes per space
- Use `--no-cache` flag to bypass cache
