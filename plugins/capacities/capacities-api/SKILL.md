---
name: capacities-api
description: Interface with Capacities knowledge management app via API. List spaces, search content, save weblinks, and append to daily notes. Use when user mentions Capacities, wants to save information to their knowledge base, or needs to search their notes.
version: 1.0.0
author: klauern
---

# Capacities API Skill

## Overview

This skill provides integration with the [Capacities](https://capacities.io) knowledge management application through its REST API. It enables Claude to interact with your personal knowledge base - listing spaces, searching content, saving web resources, and capturing notes.

## Quick Start

### Slash Commands

| Command | Description |
|---------|-------------|
| `/capacities:list-spaces` | List all your Capacities spaces |
| `/capacities:space-info [id]` | Get structures and collections for a space |
| `/capacities:search <term>` | Search content across spaces |
| `/capacities:save-weblink --url <url>` | Save a webpage to a space |
| `/capacities:daily-note --text <md>` | Append to today's daily note |

### Setup

1. Get your API token from Capacities desktop app: **Settings > Capacities API**
2. Set the environment variable:
   ```bash
   export CAPACITIES_API_TOKEN='your-token-here'
   ```

## When to Use This Skill

Invoke this skill when:

- User mentions "Capacities" or their knowledge base
- User wants to save a URL/article/resource for later
- User wants to search their notes or knowledge base
- User wants to add something to their daily notes
- User asks to "capture", "save", or "remember" information
- User wants to explore what's in their Capacities spaces

## How It Works

### Phase 1: Authentication Check

Before any API call, verify `CAPACITIES_API_TOKEN` is set. If missing, guide user to obtain and set it.

### Phase 2: Space Discovery

Most operations require a space ID. The skill uses a hybrid approach:
- If space ID is provided, use it directly
- If not provided, list spaces and ask user to select

### Phase 3: Execute Operation

Run the appropriate API endpoint with provided/selected parameters.

### Phase 4: Handle Response

- Display results in human-readable format
- For JSON consumers, use `--json` flag
- Handle rate limits gracefully (wait and retry)

## API Endpoints

| Endpoint | Rate Limit | Use Case |
|----------|------------|----------|
| GET /spaces | 5/60s | List user's spaces |
| GET /space-info | 5/60s | Get structures/collections |
| POST /search | 120/60s | Search content |
| POST /save-weblink | 10/60s | Save webpage |
| POST /save-to-daily-note | 5/60s | Append to daily note |

## Sub-Agent Strategy

### Use Haiku for

- Listing spaces (simple API call, parse JSON)
- Fetching space info (simple API call)
- Executing search with known parameters
- Saving weblinks with all parameters provided
- Cache lookups and validation

### Use Sonnet for

- Understanding user intent to determine which operation to perform
- Constructing search queries from natural language
- Deciding which space to target when user doesn't specify
- Composing markdown content for daily notes
- Synthesizing and summarizing search results
- Handling errors and guiding user through setup

## Caching

The skill caches frequently-accessed data to respect rate limits:

| Data | TTL | Location |
|------|-----|----------|
| Spaces list | 5 minutes | `~/.cache/capacities/spaces.json` |
| Space info | 10 minutes | `~/.cache/capacities/space-info-{id}.json` |

Cache is automatically invalidated on write operations (save-weblink, daily-note).

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| 401 Unauthorized | Invalid/expired token | Regenerate token in Capacities settings |
| 429 Too Many Requests | Rate limit exceeded | Wait for reset (check RateLimit-Reset header) |
| 400 Bad Request | Invalid parameters | Check parameter format (UUIDs, content length) |
| Network Error | Connection issues | Check internet connection |

## Examples

### Save an interesting article

```
User: Save this article to my Capacities: https://example.com/good-article
Claude: I'll save that to your Capacities. Which space should I use?
[Lists spaces]
User: Use my "Reading" space
Claude: [Saves weblink to Reading space]
```

### Quick note capture

```
User: Add to my daily notes: Had a great idea about improving the search algorithm
Claude: [Appends to daily note with timestamp]
```

### Search knowledge base

```
User: Search my notes for anything about "project planning"
Claude: [Searches across spaces, returns results with highlights]
```

## Documentation Index

### References

- **[api-reference.md](references/api-reference.md)** - Complete API specification
- **[workflows.md](references/workflows.md)** - Common usage patterns and workflows
- **[examples.md](references/examples.md)** - Detailed usage examples

### Commands

- **[list-spaces.md](../commands/list-spaces.md)** - List spaces command
- **[space-info.md](../commands/space-info.md)** - Space info command
- **[search.md](../commands/search.md)** - Search command
- **[save-weblink.md](../commands/save-weblink.md)** - Save weblink command
- **[daily-note.md](../commands/daily-note.md)** - Daily note command

## Requirements

- **Environment**: `CAPACITIES_API_TOKEN` must be set
- **Runtime**: Python 3.11+, UV for script execution
- **Network**: HTTPS access to api.capacities.io

## Limitations

- API is in beta - endpoints may change
- Limited to 5 endpoints (more coming per Capacities roadmap)
- No direct object editing (only create/append)
- No file/image upload support yet
