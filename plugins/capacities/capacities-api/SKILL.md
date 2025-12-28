---
name: capacities-api
description: Interface with Capacities knowledge management app via API. List spaces, search content, save weblinks, and append to daily notes. Use when user mentions Capacities, wants to save information to their knowledge base, or needs to search their notes.
version: 1.0.0
author: klauern
---

# Capacities API Skill

## Overview

This skill integrates with the [Capacities](https://capacities.io) knowledge management app via REST API. It enables listing spaces, searching content, saving weblinks, and capturing notes.

## When to Activate

Invoke this skill when the user:

- Mentions "Capacities" or their knowledge base
- Wants to save a URL/article/resource
- Wants to search their notes or knowledge base
- Wants to add something to their daily notes
- Asks to "capture", "save", or "remember" information
- Wants to explore their Capacities spaces

## Setup

1. Get API token from Capacities desktop app: **Settings > Capacities API**
2. Set environment variable:
   ```bash
   export CAPACITIES_API_TOKEN='your-token-here'
   ```

## Available Commands

| Command | Description |
|---------|-------------|
| `/capacities:list-spaces` | List all Capacities spaces |
| `/capacities:space-info [id]` | Get structures and collections for a space |
| `/capacities:search <term>` | Search content across spaces |
| `/capacities:save-weblink --url <url>` | Save a webpage to a space |
| `/capacities:daily-note --text <md>` | Append to today's daily note |

## Execution Workflow

### Phase 1: Authentication Check

Before any API call, verify `CAPACITIES_API_TOKEN` is set. If missing, guide user to obtain and set it.

### Phase 2: Space Discovery

Most operations require a space ID:
- If space ID provided, use it directly
- If not provided, list spaces and ask user to select

### Phase 3: Execute Operation

Run the appropriate API endpoint with provided/selected parameters. See @references/api-reference.md for complete endpoint specifications.

### Phase 4: Handle Response

- Display results in human-readable format
- Use `--json` flag for JSON output
- Handle rate limits gracefully (wait and retry per RateLimit-Reset header)

## Sub-Agent Strategy

### Use Haiku for:
- Listing spaces (simple API call, parse JSON)
- Fetching space info (simple API call)
- Executing search with known parameters
- Saving weblinks with all parameters provided
- Cache lookups and validation

### Use Sonnet for:
- Understanding user intent to determine operation
- Constructing search queries from natural language
- Deciding target space when user doesn't specify
- Composing markdown content for daily notes
- Synthesizing and summarizing search results
- Handling errors and guiding user through setup

## Common Patterns

### Quick Note Capture
```text
User: "Remember to review the API design tomorrow"
→ Append formatted markdown to daily note
```

### Web Clipping
```text
User: "Save this article: https://example.com/article"
→ Save weblink with auto-detected metadata, optionally add tags/notes
```

### Knowledge Search
```text
User: "What did I write about project planning?"
→ Search across spaces, present results with highlights
```

For detailed workflows, see @references/workflows.md

## API Rate Limits

| Endpoint | Rate Limit | Cache Strategy |
|----------|------------|----------------|
| GET /spaces | 5/60s | Cache 5 min in `~/.cache/capacities/spaces.json` |
| GET /space-info | 5/60s | Cache 10 min in `~/.cache/capacities/space-info-{id}.json` |
| POST /search | 120/60s | No cache (generous limit) |
| POST /save-weblink | 10/60s | Invalidates space cache |
| POST /save-to-daily-note | 5/60s | Invalidates space cache |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| 401 Unauthorized | Invalid/expired token | Regenerate token in Capacities settings |
| 429 Too Many Requests | Rate limit exceeded | Wait for reset (check RateLimit-Reset header) |
| 400 Bad Request | Invalid parameters | Check parameter format (UUIDs, content length) |
| Network Error | Connection issues | Check internet connection |

## Progressive Disclosure

Load additional documentation on-demand:

- **@references/api-reference.md** - Complete API specification with endpoint details, request/response schemas, data types, and OpenAPI link
- **@references/workflows.md** - Common usage patterns including meeting notes capture, research collection, daily review integration, multi-space handling, and error recovery strategies
- **@references/examples.md** - Detailed command examples with output samples for all operations (spaces, search, weblinks, daily notes) plus script direct usage and pipeline patterns

## Requirements

- **Environment**: `CAPACITIES_API_TOKEN` must be set
- **Runtime**: Python 3.11+, UV for script execution
- **Network**: HTTPS access to api.capacities.io

## Limitations

- API is in beta - endpoints may change
- Limited to 5 endpoints (more coming per Capacities roadmap)
- No direct object editing (only create/append)
- No file/image upload support yet
