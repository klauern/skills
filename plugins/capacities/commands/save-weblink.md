---
allowed-tools: Bash
description: Save a webpage to a Capacities space
---

# /capacities:save-weblink

Save a webpage URL to a Capacities space, optionally with additional metadata and content.

## Usage

```bash
/capacities:save-weblink --url <url> [--space-id <id>] [options]
```

## Arguments

- `--url` (required): URL of the webpage to save
- `--space-id` (required if not prompted): Target space UUID
- `--title` (optional): Override the page title (max 500 chars)
- `--description` (optional): Override description (max 1000 chars)
- `--tags` (optional): Comma-separated tags (creates if non-existent, max 30)
- `--content` (optional): Additional markdown content (max 200,000 chars)

## Behavior

### With all required arguments:
1. Save the webpage to the specified space
2. Capacities fetches metadata (title, description, image) from the URL
3. Apply any overrides provided
4. Return the created object info

### Hybrid mode (missing space-id):
1. List available spaces
2. Ask user which space to save to
3. Execute save with selected space

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

uv run "$SCRIPT_DIR/capacities.py" save-weblink \
    --space-id "$SPACE_ID" \
    --url "$URL" \
    ${TITLE:+--title "$TITLE"} \
    ${DESCRIPTION:+--description "$DESCRIPTION"} \
    ${TAGS:+--tags "$TAGS"} \
    ${CONTENT:+--content "$CONTENT"} \
    --json
```

## Output

Returns JSON with saved object:
```json
{
  "spaceId": "space-uuid",
  "id": "object-uuid",
  "structureId": "weblink-structure-uuid",
  "title": "Page Title",
  "description": "Page description",
  "tags": ["tag1", "tag2"]
}
```

## Examples

```bash
# Simple save
/capacities:save-weblink --url https://example.com/article --space-id abc-123

# With tags and custom title
/capacities:save-weblink \
    --url https://docs.python.org/3/ \
    --space-id abc-123 \
    --title "Python 3 Documentation" \
    --tags "python,docs,reference"

# With additional notes
/capacities:save-weblink \
    --url https://arxiv.org/paper \
    --space-id abc-123 \
    --content "## My Notes\n- Key finding 1\n- Key finding 2"
```

## Use Cases

- Save interesting articles for later reading
- Build a knowledge base of resources
- Clip web content with your own annotations
- Archive important references

## Notes

- Rate limit: 10 requests per 60 seconds
- Tags are created automatically if they don't exist
- Content field supports full markdown
- Clears local cache after saving (data changed)
