---
name: capacities-api
description: Integrates the Capacities knowledge-management REST API to list spaces, search content, save weblinks, and append daily notes. Use when the user asks to "list Capacities spaces", "search Capacities", "save a weblink to Capacities", "append to a Capacities daily note", or mentions Capacities API workflows.
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
   export CAPACITIES_API_TOKEN='token-here'
   ```

## Available Commands

| Command | Description |
|---------|-------------|
| `/capacities:list-spaces` | List all Capacities spaces |
| `/capacities:space-info [id]` | Get structures and collections for a space |
| `/capacities:search <term>` | Search content across spaces |
| `/capacities:save-weblink --url <url>` | Save a webpage to a space |
| `/capacities:daily-note --text <md>` | Append to today's daily note |

The backing script also offers `capacities.py lookup <term> --space-id <id>` — title-only
lookup within a single space.

## Execution Workflow

### Phase 1: Authentication Check

Before any API call, verify `CAPACITIES_API_TOKEN` is set. If missing, guide user to obtain and set it.

### Phase 2: Space Discovery

Most operations require a space ID:
- If space ID provided, use it directly
- If not provided, list spaces and ask user to select (space-selection strategies in the API reference)

### Phase 3: Execute Operation

Run the appropriate endpoint via `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" …`.
See [api-reference.md](references/api-reference.md) for complete endpoint specifications.

### Phase 4: Handle Response

- Display results in human-readable format (`--json` for JSON output)
- Rate limits are strict on most endpoints; the script caches spaces/space-info.
  Limits, recovery steps, and script patterns live in the API reference.

## Common Patterns

- **Quick note capture**: "Remember to review the API design tomorrow" → append formatted markdown to the daily note
- **Web clipping**: "Save this article: <url>" → save-weblink with metadata, optional tags/notes
- **Knowledge search**: "What did I write about project planning?" → search across spaces, present highlights

## Progressive Disclosure

- [api-reference.md](references/api-reference.md) — complete endpoint specs,
  rate-limit strategy, space-selection guidance, script patterns, and error recovery

## Requirements

- **Environment**: `CAPACITIES_API_TOKEN` must be set
- **Runtime**: Python 3.11+, UV for script execution
- **Network**: HTTPS access to api.capacities.io

## Limitations

- API is in beta - endpoints may change
- No direct object editing (only create/append)
- No file/image upload support yet
