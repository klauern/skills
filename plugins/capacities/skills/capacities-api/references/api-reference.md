# Capacities API Reference

Complete specification for the Capacities REST API (Beta).

## Base URL

```text
https://api.capacities.io
```

## Authentication

All requests require a Bearer token in the Authorization header:

```text
Authorization: Bearer <your-api-token>
```

**Getting your token:**
1. Open Capacities desktop app
2. Go to **Settings > Capacities API**
3. Generate or copy your token

**Security Warning:** Tokens grant full data access. Never share or expose them.

## Rate Limiting

Rate limits are per-user, per-endpoint. Response headers provide limit info:

| Header | Description |
|--------|-------------|
| `RateLimit-Policy` | Request allowance and window |
| `RateLimit-Limit` | Max requests per window |
| `RateLimit-Remaining` | Requests remaining |
| `RateLimit-Reset` | Seconds until reset |

Exceeding limits returns `429 Too Many Requests`.

---

## Endpoints

### GET /spaces

List all spaces the user has access to.

**Rate Limit:** 5 requests per 60 seconds

**Request:**
```bash
curl -X GET "https://api.capacities.io/spaces" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "spaces": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Personal Notes",
      "icon": {
        "type": "emoji",
        "emoji": "📝"
      }
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "title": "Work Projects",
      "icon": {
        "type": "iconify",
        "iconId": "mdi:briefcase",
        "color": "blue"
      }
    }
  ]
}
```

**Icon Types:**
- `emoji`: Simple emoji character
- `iconify`: Iconify icon with color (18 color options)

---

### GET /space-info

Get structures (object types) and collections for a space.

**Rate Limit:** 5 requests per 60 seconds

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| spaceid | UUID | Yes | Space identifier |

**Request:**
```bash
curl -X GET "https://api.capacities.io/space-info?spaceid=$SPACE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "structures": [
    {
      "id": "struct-uuid-1",
      "title": "Note",
      "pluralName": "Notes",
      "labelColor": "blue",
      "propertyDefinitions": [
        {
          "id": "prop-uuid",
          "title": "Tags",
          "type": "multi-select"
        }
      ],
      "collections": [
        {
          "id": "coll-uuid-1",
          "title": "Meeting Notes"
        }
      ]
    }
  ]
}
```

---

### POST /lookup

Look up content by title within a single space (lighter than /search; used by
`capacities.py lookup <term> --space-id <id>`).

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| searchTerm | string | Yes | Title search term |
| spaceId | UUID | Yes | Space to look in |

**Response:** `results` array of `{id, title, structureId}` matches.

---

### POST /search

Search for content across spaces.

**Rate Limit:** 120 requests per 60 seconds

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| searchTerm | string | Yes | Query string |
| spaceIds | string[] | Yes | Space UUIDs to search |
| mode | string | No | `title` (default) or `fullText` |
| filterStructureIds | string[] | No | Limit to specific structures |

**Request:**
```bash
curl -X POST "https://api.capacities.io/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "searchTerm": "meeting notes",
    "spaceIds": ["space-uuid-1", "space-uuid-2"],
    "mode": "fullText"
  }'
```

**Response:**
```json
{
  "results": [
    {
      "id": "object-uuid",
      "title": "Q4 Planning Meeting",
      "structureId": "note-struct-uuid",
      "spaceId": "space-uuid-1",
      "highlights": [
        "...discussed **meeting notes** format..."
      ],
      "snippet": "Brief preview of content..."
    }
  ]
}
```

---

### POST /save-weblink

Save a webpage as an object in a space.

**Rate Limit:** 10 requests per 60 seconds

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| spaceId | UUID | Yes | Target space |
| url | string | Yes | URL to save |
| titleOverwrite | string | No | Custom title (max 500 chars) |
| descriptionOverwrite | string | No | Custom description (max 1000 chars) |
| tags | string[] | No | Tag names (max 30, created if new) |
| mdText | string | No | Additional markdown (max 200,000 chars) |

**Request:**
```bash
curl -X POST "https://api.capacities.io/save-weblink" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "spaceId": "space-uuid",
    "url": "https://example.com/article",
    "titleOverwrite": "Custom Title",
    "tags": ["reading", "tech"],
    "mdText": "## My Notes\n- Key point 1\n- Key point 2"
  }'
```

**Response:**
```json
{
  "spaceId": "space-uuid",
  "id": "created-object-uuid",
  "structureId": "weblink-struct-uuid",
  "title": "Custom Title",
  "description": "Page meta description...",
  "tags": ["reading", "tech"]
}
```

---

### POST /save-to-daily-note

Append Markdown text to today's daily note.

**Rate Limit:** 5 requests per 60 seconds

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| spaceId | UUID | Yes | Target space |
| mdText | string | Yes | Markdown to append |
| origin | string | No | Source identifier (e.g., "commandPalette") |
| noTimeStamp | boolean | No | Skip timestamp prefix |

**Request:**
```bash
curl -X POST "https://api.capacities.io/save-to-daily-note" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "spaceId": "space-uuid",
    "mdText": "## Meeting Notes\n- Discussed roadmap\n- Action items assigned",
    "noTimeStamp": false
  }'
```

**Response:**
```text
200 OK
```

(Empty response body on success)

---

## Error Responses

| Status | Meaning | Example |
|--------|---------|---------|
| 400 | Bad Request | Invalid UUID format, missing required field |
| 401 | Unauthorized | Invalid or expired token |
| 404 | Not Found | Space or object doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |

**Error Response Format:**
```json
{
  "message": "Error description",
  "statusCode": 400
}
```

---

## Per-Endpoint Rate Strategy

| Endpoint | Limit | Strategy |
|----------|-------|----------|
| spaces | 5/60s | Cache aggressively (script caches 5 min) |
| space-info | 5/60s | Cache per space (10 min) |
| search | 120/60s | Generous, minimal concern |
| save-weblink | 10/60s | Batch if multiple saves |
| daily-note | 5/60s | Combine entries when possible |

When rate limited: read `RateLimit-Reset`, wait that many seconds, retry.

## Choosing a Space

Most users have several spaces (Personal, Work, …). Selection order:
1. **Explicit** — the user names a space ("save to my Work space")
2. **Context** — infer from content (e.g. "meeting notes" → Work) and confirm
3. **Interactive** — list spaces and ask

## Script Patterns

```bash
# Force fresh data past the cache
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" spaces --no-cache

# Pipeline: resolve a space ID, then search it
SPACE_ID=$(uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" spaces --json | jq -r '.spaces[0].id')
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" search "meeting" --space-ids "$SPACE_ID" --json | jq '.results[].title'
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| 401 Unauthorized | Check `CAPACITIES_API_TOKEN`; regenerate in Capacities Settings > API |
| 404 space not found | `/capacities:list-spaces`, verify the ID, check for deleted/archived space |
| 400 mdText too long | Max 200,000 chars — split into multiple daily-note entries or summarize |
| 429 rate limited | Wait `RateLimit-Reset` seconds, retry |

---

## OpenAPI Specification

Full OpenAPI 3.0 spec available at: [https://api.capacities.io/docs](https://api.capacities.io/docs)

---

## Beta Status

The Capacities API is currently in beta:
- Endpoints may change without notice
- Additional endpoints planned for future releases
- Submit feature requests via Capacities feedback board
