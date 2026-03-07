#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
TickTick date management — clear due/start dates from tasks.

The upstream ticktick-mcp server skips null values in update_task,
so there is no way to clear dates via MCP. This script calls the
TickTick API directly.

Usage:
    ticktick_dates.py clear-dates --task-id <id> --project-id <id> [--json]

Environment:
    TICKTICK_ACCESS_TOKEN - Required OAuth access token
"""

import argparse
import json
import os
import sys

import httpx

API_BASE = "https://api.ticktick.com/open/v1"


def get_token() -> str:
    """Get access token from environment."""
    token = os.environ.get("TICKTICK_ACCESS_TOKEN")
    if not token:
        print("Error: TICKTICK_ACCESS_TOKEN environment variable not set.", file=sys.stderr)
        print("Run /ticktick:setup to configure authentication.", file=sys.stderr)
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


def request(method: str, path: str, operation: str, **kwargs) -> httpx.Response:
    """Perform an HTTP request with error handling."""
    try:
        with get_client() as client:
            return client.request(method, path, **kwargs)
    except httpx.RequestError as exc:
        print(f"Error: Network problem during {operation}: {exc}", file=sys.stderr)
        sys.exit(1)


def handle_response(response: httpx.Response, operation: str) -> dict | None:
    """Handle API response with error checking."""
    if response.status_code == 200:
        if response.text:
            return response.json()
        return None
    elif response.status_code == 401:
        print("Error: Unauthorized — check TICKTICK_ACCESS_TOKEN or re-run /ticktick:setup", file=sys.stderr)
        sys.exit(1)
    elif response.status_code == 404:
        print(f"Error: Not found — {operation}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Error: {operation} failed with status {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)


def cmd_clear_dates(args: argparse.Namespace) -> None:
    """Clear due date and start date from a task."""
    path = f"/task/{args.task_id}"
    payload = {"id": args.task_id, "projectId": args.project_id, "dueDate": None, "startDate": None}

    response = request("POST", path, f"Clear dates for task {args.task_id}", json=payload)
    data = handle_response(response, f"Clear dates for task {args.task_id}")

    if args.json:
        print(json.dumps(data or {"success": True, "taskId": args.task_id}, indent=2))
    else:
        title = data.get("title", args.task_id) if data else args.task_id
        print(f"Cleared dates for: {title}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="TickTick date management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp_clear = subparsers.add_parser("clear-dates", help="Clear due/start dates from a task")
    sp_clear.add_argument("--task-id", required=True, help="Task ID")
    sp_clear.add_argument("--project-id", required=True, help="Project (list) ID")
    sp_clear.add_argument("--json", action="store_true", help="Output as JSON")
    sp_clear.set_defaults(func=cmd_clear_dates)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
