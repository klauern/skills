#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
Capacities API client for Claude Code.

Usage:
    capacities.py spaces [--json] [--no-cache]
    capacities.py space-info <space-id> [--json] [--no-cache]
    capacities.py search <term> --space-ids <ids> [--mode fullText|title] [--filter <ids>] [--json]
    capacities.py save-weblink --space-id <id> --url <url> [--title <t>] [--description <d>] [--tags <t>] [--content <md>] [--json]
    capacities.py daily-note --space-id <id> --text <md> [--no-timestamp] [--json]

Environment:
    CAPACITIES_API_TOKEN - Required API bearer token (get from Capacities Settings > API)

Examples:
    # List all spaces
    capacities.py spaces

    # Get structures for a space
    capacities.py space-info 12345678-1234-1234-1234-123456789abc

    # Search across spaces
    capacities.py search "meeting notes" --space-ids id1,id2 --mode fullText

    # Save a weblink
    capacities.py save-weblink --space-id <id> --url https://example.com --tags "reading,tech"

    # Add to daily note
    capacities.py daily-note --space-id <id> --text "## Today's Progress\\n- Completed feature X"
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

# Constants
API_BASE = "https://api.capacities.io"
CACHE_DIR = Path.home() / ".cache" / "capacities"
CACHE_TTL = {
    "spaces": 300,      # 5 minutes
    "space-info": 600,  # 10 minutes
}


@dataclass
class CacheEntry:
    """Cache entry with timestamp."""
    data: Any
    timestamp: float


def get_token() -> str:
    """Get API token from environment."""
    token = os.environ.get("CAPACITIES_API_TOKEN")
    if not token:
        print("Error: CAPACITIES_API_TOKEN environment variable not set.", file=sys.stderr)
        print("Get your token from Capacities desktop app: Settings > Capacities API", file=sys.stderr)
        print("\nSet it with: export CAPACITIES_API_TOKEN='your-token-here'", file=sys.stderr)
        sys.exit(1)
    return token


def get_client() -> httpx.Client:
    """Create HTTP client with auth headers."""
    return httpx.Client(
        base_url=API_BASE,
        headers={
            "Authorization": f"Bearer {get_token()}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )


def request(method: str, path: str, operation: str, **kwargs: Any) -> httpx.Response:
    """Perform an HTTP request and handle network errors consistently."""
    try:
        with get_client() as client:
            return client.request(method, path, **kwargs)
    except httpx.RequestError as exc:
        print(f"Error: Network problem during {operation}: {exc}", file=sys.stderr)
        print("\nTroubleshooting:", file=sys.stderr)
        print("  - Check your internet connection", file=sys.stderr)
        print("  - Verify api.capacities.io is accessible", file=sys.stderr)
        sys.exit(1)


def load_cache(key: str) -> CacheEntry | None:
    """Load cached data if valid."""
    cache_file = CACHE_DIR / f"{key}.json"
    if not cache_file.exists():
        return None

    try:
        data = json.loads(cache_file.read_text())
        entry = CacheEntry(data=data["data"], timestamp=data["timestamp"])

        # Check TTL
        # Extract base key: "spaces" or "space-info" from cache keys
        base_key = "space-info" if key.startswith("space-info-") else key
        ttl = CACHE_TTL.get(base_key, 300)
        if time.time() - entry.timestamp > ttl:
            return None

        return entry
    except (json.JSONDecodeError, KeyError):
        return None


def save_cache(key: str, data: Any) -> None:
    """Save data to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(json.dumps({
        "data": data,
        "timestamp": time.time(),
    }))


def clear_cache() -> None:
    """Clear all cached data."""
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()


def handle_response(response: httpx.Response, operation: str) -> dict | list | None:
    """Handle API response with error checking."""
    # Check rate limit headers
    remaining = response.headers.get("RateLimit-Remaining")
    if remaining and int(remaining) <= 1:
        print(f"Warning: Rate limit nearly exhausted ({remaining} remaining)", file=sys.stderr)

    if response.status_code == 200:
        if response.text:
            return response.json()
        return None
    elif response.status_code == 401:
        print("Error: Unauthorized - check your CAPACITIES_API_TOKEN", file=sys.stderr)
        sys.exit(1)
    elif response.status_code == 429:
        reset = response.headers.get("RateLimit-Reset", "60")
        print(f"Error: Rate limit exceeded. Try again in {reset} seconds.", file=sys.stderr)
        sys.exit(1)
    elif response.status_code == 400:
        try:
            error = response.json()
            print(f"Error: Bad request - {error.get('message', response.text)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Error: Bad request - {response.text}", file=sys.stderr)
        sys.exit(1)
    elif response.status_code == 404:
        print(f"Error: Not found - {operation}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Error: {operation} failed with status {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)


def format_spaces(spaces: list[dict], as_json: bool) -> None:
    """Format and print spaces list."""
    if as_json:
        print(json.dumps(spaces, indent=2))
    else:
        if not spaces:
            print("No spaces found.")
            return
        print("Your Capacities Spaces:")
        print("-" * 50)
        for space in spaces:
            icon = ""
            if space.get("icon"):
                icon_data = space["icon"]
                if icon_data.get("type") == "emoji":
                    icon = icon_data.get("emoji", "") + " "
            print(f"{icon}{space['title']}")
            print(f"  ID: {space['id']}")
            print()


def format_space_info(info: dict, as_json: bool) -> None:
    """Format and print space info."""
    if as_json:
        print(json.dumps(info, indent=2))
    else:
        structures = info.get("structures", [])
        if not structures:
            print("No structures found in this space.")
            return
        print("Space Structures:")
        print("-" * 50)
        for struct in structures:
            print(f"\n{struct['title']} ({struct.get('pluralName', '')})")
            print(f"  ID: {struct['id']}")
            if struct.get("labelColor"):
                print(f"  Color: {struct['labelColor']}")

            # Collections
            collections = struct.get("collections", [])
            if collections:
                print(f"  Collections ({len(collections)}):")
                for coll in collections[:5]:  # Show first 5
                    print(f"    - {coll['title']} ({coll['id']})")
                if len(collections) > 5:
                    print(f"    ... and {len(collections) - 5} more")


def format_search_results(results: dict, as_json: bool) -> None:
    """Format and print search results."""
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        items = results.get("results", [])
        if not items:
            print("No results found.")
            return
        print(f"Found {len(items)} results:")
        print("-" * 50)
        for item in items:
            print(f"\n{item.get('title', 'Untitled')}")
            if item.get("highlights"):
                for highlight in item["highlights"][:2]:
                    print(f"  ...{highlight}...")
            if item.get("id"):
                print(f"  ID: {item['id']}")


def format_saved(result: dict, as_json: bool, subject: str) -> None:
    """Format and print save result."""
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        if result:
            print(f"{subject} saved successfully!")
            if result.get("title"):
                print(f"  Title: {result['title']}")
            if result.get("id"):
                print(f"  ID: {result['id']}")
        else:
            print(f"{subject} saved successfully!")


# Commands

def cmd_spaces(args: argparse.Namespace) -> None:
    """List all user spaces."""
    # Try cache first
    if not args.no_cache:
        cached = load_cache("spaces")
        if cached:
            format_spaces(cached.data, args.json)
            return

    response = request("GET", "/spaces", "List spaces")
    data = handle_response(response, "List spaces")

    spaces = data.get("spaces", []) if data else []

    # Cache result
    if not args.no_cache:
        save_cache("spaces", spaces)

    format_spaces(spaces, args.json)


def cmd_space_info(args: argparse.Namespace) -> None:
    """Get structures and collections for a space."""
    cache_key = f"space-info-{args.space_id}"

    # Try cache first
    if not args.no_cache:
        cached = load_cache(cache_key)
        if cached:
            format_space_info(cached.data, args.json)
            return

    response = request("GET", "/space-info", f"Get space info for {args.space_id}",
                       params={"spaceid": args.space_id})
    data = handle_response(response, f"Get space info for {args.space_id}")

    # Cache result
    if not args.no_cache and data:
        save_cache(cache_key, data)

    format_space_info(data or {}, args.json)


def cmd_search(args: argparse.Namespace) -> None:
    """Search content across spaces."""
    space_ids = [s.strip() for s in args.space_ids.split(",")]

    payload = {
        "searchTerm": args.term,
        "spaceIds": space_ids,
        "mode": args.mode,
    }

    if args.filter:
        payload["filterStructureIds"] = [s.strip() for s in args.filter.split(",")]

    response = request("POST", "/search", "Search", json=payload)
    data = handle_response(response, "Search")
    format_search_results(data or {}, args.json)


def cmd_save_weblink(args: argparse.Namespace) -> None:
    """Save a webpage to a space."""
    payload = {
        "spaceId": args.space_id,
        "url": args.url,
    }

    if args.title:
        payload["titleOverwrite"] = args.title
    if args.description:
        payload["descriptionOverwrite"] = args.description
    if args.tags:
        payload["tags"] = [t.strip() for t in args.tags.split(",")]
    if args.content:
        payload["mdText"] = args.content

    response = request("POST", "/save-weblink", "Save weblink", json=payload)
    data = handle_response(response, "Save weblink")

    # Clear cache since we modified data
    clear_cache()

    format_saved(data or {}, args.json, "Weblink")


def cmd_daily_note(args: argparse.Namespace) -> None:
    """Append markdown to today's daily note."""
    payload = {
        "spaceId": args.space_id,
        "mdText": args.text,
    }

    if args.no_timestamp:
        payload["noTimeStamp"] = True

    response = request("POST", "/save-to-daily-note", "Save to daily note", json=payload)
    handle_response(response, "Save to daily note")

    # Clear cache since we modified data
    clear_cache()

    if args.json:
        print(json.dumps({"success": True, "message": "Added to daily note"}))
    else:
        print("Added to daily note successfully!")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Capacities API client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # spaces command
    sp_spaces = subparsers.add_parser("spaces", help="List all user spaces")
    sp_spaces.add_argument("--json", action="store_true", help="Output as JSON")
    sp_spaces.add_argument("--no-cache", action="store_true", help="Skip cache")
    sp_spaces.set_defaults(func=cmd_spaces)

    # space-info command
    sp_info = subparsers.add_parser("space-info", help="Get space structures")
    sp_info.add_argument("space_id", help="Space UUID")
    sp_info.add_argument("--json", action="store_true", help="Output as JSON")
    sp_info.add_argument("--no-cache", action="store_true", help="Skip cache")
    sp_info.set_defaults(func=cmd_space_info)

    # search command
    sp_search = subparsers.add_parser("search", help="Search content")
    sp_search.add_argument("term", help="Search term")
    sp_search.add_argument("--space-ids", required=True, help="Comma-separated space IDs")
    sp_search.add_argument("--mode", choices=["fullText", "title"], default="title", help="Search mode")
    sp_search.add_argument("--filter", help="Comma-separated structure IDs to filter")
    sp_search.add_argument("--json", action="store_true", help="Output as JSON")
    sp_search.set_defaults(func=cmd_search)

    # save-weblink command
    sp_weblink = subparsers.add_parser("save-weblink", help="Save webpage to space")
    sp_weblink.add_argument("--space-id", required=True, help="Target space UUID")
    sp_weblink.add_argument("--url", required=True, help="URL to save")
    sp_weblink.add_argument("--title", help="Override title")
    sp_weblink.add_argument("--description", help="Override description")
    sp_weblink.add_argument("--tags", help="Comma-separated tags")
    sp_weblink.add_argument("--content", help="Additional markdown content")
    sp_weblink.add_argument("--json", action="store_true", help="Output as JSON")
    sp_weblink.set_defaults(func=cmd_save_weblink)

    # daily-note command
    sp_daily = subparsers.add_parser("daily-note", help="Add to daily note")
    sp_daily.add_argument("--space-id", required=True, help="Target space UUID")
    sp_daily.add_argument("--text", required=True, help="Markdown text to add")
    sp_daily.add_argument("--no-timestamp", action="store_true", help="Don't add timestamp")
    sp_daily.add_argument("--json", action="store_true", help="Output as JSON")
    sp_daily.set_defaults(func=cmd_daily_note)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
