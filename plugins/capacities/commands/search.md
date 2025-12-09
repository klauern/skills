---
allowed-tools: Bash
description: Search content in Capacities spaces
---

# /capacities:search

Search for content across one or more Capacities spaces.

## Usage

```bash
/capacities:search <term> [--space-ids <ids>] [--mode fullText|title]
```

## Arguments

- `term` (required): Search query string
- `--space-ids` (required if not prompted): Comma-separated list of space UUIDs
- `--mode` (optional): Search mode - `title` (default) or `fullText`
- `--filter` (optional): Comma-separated structure IDs to filter results

## Behavior

### With all arguments:
1. Execute search with provided parameters
2. Return results with highlights and snippets

### Hybrid mode (missing space-ids):
1. List available spaces
2. Ask user which spaces to search
3. Execute search with selected spaces

## Implementation

```bash
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"

# If no space-ids provided, list spaces first
if [ -z "$SPACE_IDS" ]; then
    echo "Available spaces:"
    uv run "$SCRIPT_DIR/capacities.py" spaces
    echo ""
    echo "Provide --space-ids to search specific spaces"
    exit 0
fi

uv run "$SCRIPT_DIR/capacities.py" search "$TERM" \
    --space-ids "$SPACE_IDS" \
    --mode "${MODE:-title}" \
    --json
```

## Output

Returns JSON with search results:
```json
{
  "results": [
    {
      "id": "object-uuid",
      "title": "Meeting Notes",
      "highlights": ["...matching **text**..."],
      "structureId": "note-structure-uuid"
    }
  ]
}
```

## Search Modes

- **title** (default): Fast search through titles only
- **fullText**: Comprehensive search through all content

## Examples

```bash
# Search titles in a single space
/capacities:search "project plan" --space-ids abc-123

# Full-text search across multiple spaces
/capacities:search "quarterly review" --space-ids abc-123,def-456 --mode fullText

# Filter to specific structure types
/capacities:search "meeting" --space-ids abc-123 --filter note-struct-id
```

## Notes

- Rate limit: 120 requests per 60 seconds (most generous)
- Full-text search is slower but more comprehensive
- Results include relevance-ordered matches with highlights
