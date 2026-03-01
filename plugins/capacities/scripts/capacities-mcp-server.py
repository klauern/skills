#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp[cli]", "httpx"]
# ///
"""
Capacities MCP server for Claude Code.

Exposes the Capacities API as native MCP tools so Claude can directly
list spaces, search content, save weblinks, and append to daily notes.

Usage:
    # Run as MCP server (stdio transport)
    uv run capacities-mcp-server.py

    # Add to Claude Code MCP config (~/.claude.json or .mcp.json):
    # "capacities": {
    #   "command": "uv",
    #   "args": ["run", "/path/to/capacities-mcp-server.py"],
    #   "env": { "CAPACITIES_API_TOKEN": "your-token" }
    # }

Environment:
    CAPACITIES_API_TOKEN - Required API bearer token (get from Capacities Settings > API)
"""

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Constants
API_BASE = "https://api.capacities.io"
CACHE_DIR = Path.home() / ".cache" / "capacities"
CACHE_TTL = {
    "spaces": 300,      # 5 minutes
    "space-info": 600,  # 10 minutes
}

mcp = FastMCP("capacities", description="Capacities knowledge management API")


# --- HTTP helpers ---

def _get_token() -> str:
    """Get API token from environment."""
    token = os.environ.get("CAPACITIES_API_TOKEN")
    if not token:
        raise RuntimeError(
            "CAPACITIES_API_TOKEN environment variable not set. "
            "Get your token from Capacities desktop app: Settings > Capacities API"
        )
    return token


def _client() -> httpx.Client:
    """Create HTTP client with auth headers."""
    return httpx.Client(
        base_url=API_BASE,
        headers={
            "Authorization": f"Bearer {_get_token()}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )


def _handle_response(response: httpx.Response, operation: str) -> dict | list | None:
    """Handle API response, raising on errors."""
    remaining = response.headers.get("RateLimit-Remaining")
    if remaining:
        try:
            if int(remaining) <= 1:
                reset = response.headers.get("RateLimit-Reset", "60")
                raise RuntimeError(
                    f"Rate limit nearly exhausted ({remaining} remaining). "
                    f"Resets in {reset}s."
                )
        except ValueError:
            pass

    if response.status_code == 200:
        return response.json() if response.text else None
    elif response.status_code == 401:
        raise RuntimeError("Unauthorized - check your CAPACITIES_API_TOKEN")
    elif response.status_code == 429:
        reset = response.headers.get("RateLimit-Reset", "60")
        raise RuntimeError(f"Rate limit exceeded. Try again in {reset} seconds.")
    elif response.status_code == 400:
        try:
            error = response.json()
            msg = error.get("message", response.text)
        except json.JSONDecodeError:
            msg = response.text
        raise RuntimeError(f"Bad request during {operation}: {msg}")
    else:
        raise RuntimeError(
            f"{operation} failed with status {response.status_code}: {response.text}"
        )


# --- Cache helpers ---

def _load_cache(key: str) -> Any | None:
    """Load cached data if still valid."""
    cache_file = CACHE_DIR / f"{key}.json"
    if not cache_file.exists():
        return None
    try:
        raw = json.loads(cache_file.read_text())
        base_key = "space-info" if key.startswith("space-info-") else key
        ttl = CACHE_TTL.get(base_key, 300)
        if time.time() - raw["timestamp"] > ttl:
            return None
        return raw["data"]
    except (json.JSONDecodeError, KeyError):
        return None


def _save_cache(key: str, data: Any) -> None:
    """Save data to file-based cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(
        json.dumps({"data": data, "timestamp": time.time()})
    )


def _clear_cache() -> None:
    """Clear all cached data."""
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()


# --- MCP Tools ---

@mcp.tool()
def list_spaces() -> str:
    """List all Capacities spaces with their IDs, titles, and icons.

    Returns a JSON array of spaces. Each space has 'id', 'title', and
    optional 'icon' fields. Use the space ID in other tools that require
    a space_id parameter.

    Cached for 5 minutes.
    """
    cached = _load_cache("spaces")
    if cached is not None:
        return json.dumps(cached, indent=2)

    with _client() as client:
        response = client.get("/spaces")

    data = _handle_response(response, "List spaces")
    spaces = data.get("spaces", []) if data else []
    _save_cache("spaces", spaces)
    return json.dumps(spaces, indent=2)


@mcp.tool()
def get_space_info(space_id: str) -> str:
    """Get structures and collections for a Capacities space.

    Args:
        space_id: The UUID of the space to inspect. Get this from list_spaces().

    Returns a JSON object with 'structures' containing content types
    (pages, tags, weblinks, etc.) and their collections defined in the space.

    Cached for 10 minutes.
    """
    cache_key = f"space-info-{space_id}"
    cached = _load_cache(cache_key)
    if cached is not None:
        return json.dumps(cached, indent=2)

    with _client() as client:
        response = client.get("/space-info", params={"spaceid": space_id})

    data = _handle_response(response, f"Get space info for {space_id}")
    if data:
        _save_cache(cache_key, data)
    return json.dumps(data or {}, indent=2)


@mcp.tool()
def search(
    search_term: str,
    space_ids: list[str],
    mode: str = "title",
    filter_structure_ids: list[str] | None = None,
) -> str:
    """Search content across one or more Capacities spaces.

    Args:
        search_term: The text to search for.
        space_ids: List of space UUIDs to search in. Get these from list_spaces().
        mode: Search mode - "title" for title-only search (default),
              "fullText" for full content search.
        filter_structure_ids: Optional list of structure IDs to narrow results
              to specific content types. Get these from get_space_info().

    Returns a JSON object with 'results' array containing matched items
    with titles, highlights, and IDs.

    Not cached (search results should always be fresh).
    """
    payload: dict[str, Any] = {
        "searchTerm": search_term,
        "spaceIds": space_ids,
        "mode": mode,
    }
    if filter_structure_ids:
        payload["filterStructureIds"] = filter_structure_ids

    with _client() as client:
        response = client.post("/search", json=payload)

    data = _handle_response(response, "Search")
    return json.dumps(data or {}, indent=2)


@mcp.tool()
def save_weblink(
    space_id: str,
    url: str,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    content: str | None = None,
) -> str:
    """Save a webpage URL to a Capacities space as a weblink.

    Args:
        space_id: The UUID of the target space. Get this from list_spaces().
        url: The URL of the webpage to save.
        title: Optional title override. If omitted, Capacities auto-detects
               the page title.
        description: Optional description override.
        tags: Optional list of tag names to apply to the saved weblink.
        content: Optional additional markdown content to attach.

    Returns a JSON object with the saved weblink's details (id, title, etc.).

    Clears the local cache after saving.
    """
    payload: dict[str, Any] = {
        "spaceId": space_id,
        "url": url,
    }
    if title:
        payload["titleOverwrite"] = title
    if description:
        payload["descriptionOverwrite"] = description
    if tags:
        payload["tags"] = tags
    if content:
        payload["mdText"] = content

    with _client() as client:
        response = client.post("/save-weblink", json=payload)

    data = _handle_response(response, "Save weblink")
    _clear_cache()
    return json.dumps(data or {"success": True}, indent=2)


@mcp.tool()
def daily_note(
    space_id: str,
    text: str,
    no_timestamp: bool = False,
) -> str:
    """Append markdown text to today's daily note in a Capacities space.

    Args:
        space_id: The UUID of the target space. Get this from list_spaces().
        text: Markdown-formatted text to append to the daily note.
              Supports full markdown syntax (headings, lists, links, etc.).
        no_timestamp: If True, omit the automatic timestamp prefix that
              Capacities adds. Default is False (timestamp is included).

    Returns a JSON confirmation of the operation.

    Clears the local cache after saving.
    """
    payload: dict[str, Any] = {
        "spaceId": space_id,
        "mdText": text,
    }
    if no_timestamp:
        payload["noTimeStamp"] = True

    with _client() as client:
        response = client.post("/save-to-daily-note", json=payload)

    _handle_response(response, "Save to daily note")
    _clear_cache()
    return json.dumps({"success": True, "message": "Added to daily note"}, indent=2)


if __name__ == "__main__":
    mcp.run()
