#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch every PR review thread and nested comment before filtering by state."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Callable
from typing import Any

THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $threadsCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $threadsCursor) {
        nodes {
          id isResolved isOutdated path line resolvedBy { login }
          comments(first: 100) {
            nodes { author { login } body createdAt }
            pageInfo { hasNextPage endCursor }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""

COMMENTS_QUERY = """
query($threadId: ID!, $commentsCursor: String!) {
  node(id: $threadId) {
    ... on PullRequestReviewThread {
      comments(first: 100, after: $commentsCursor) {
        nodes { author { login } body createdAt }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""

GraphQL = Callable[[str, dict[str, Any]], dict[str, Any]]


def run_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is not None:
            command.extend(("-F", f"{key}={value}"))
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def _next_cursor(page_info: dict[str, Any], connection: str) -> str | None:
    if not page_info["hasNextPage"]:
        return None
    cursor = page_info.get("endCursor")
    if not cursor:
        raise RuntimeError(f"{connection} has another page but no end cursor")
    return cursor


def fetch_and_filter_review_threads(
    *, owner: str, name: str, number: int, graphql: GraphQL = run_graphql
) -> dict[str, Any]:
    """Exhaust both connection levels, then group non-outdated threads."""
    all_threads: list[dict[str, Any]] = []
    threads_cursor: str | None = None

    while True:
        response = graphql(
            THREADS_QUERY,
            {
                "owner": owner,
                "name": name,
                "number": number,
                "threadsCursor": threads_cursor,
            },
        )
        connection = response["data"]["repository"]["pullRequest"]["reviewThreads"]
        for node in connection["nodes"]:
            thread = {key: value for key, value in node.items() if key != "comments"}
            comments = list(node["comments"]["nodes"])
            comments_cursor = _next_cursor(
                node["comments"]["pageInfo"], f"comments for thread {node['id']}"
            )
            while comments_cursor is not None:
                comment_response = graphql(
                    COMMENTS_QUERY,
                    {"threadId": node["id"], "commentsCursor": comments_cursor},
                )
                comment_connection = comment_response["data"]["node"]["comments"]
                comments.extend(comment_connection["nodes"])
                comments_cursor = _next_cursor(
                    comment_connection["pageInfo"], f"comments for thread {node['id']}"
                )
            thread["comments"] = comments
            all_threads.append(thread)

        threads_cursor = _next_cursor(connection["pageInfo"], "reviewThreads")
        if threads_cursor is None:
            break

    current = [thread for thread in all_threads if not thread["isOutdated"]]
    return {
        "open": [thread for thread in current if not thread["isResolved"]],
        "resolved": [thread for thread in current if thread["isResolved"]],
        "outdatedCount": sum(thread["isOutdated"] for thread in all_threads),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, metavar="OWNER/NAME")
    parser.add_argument("--pr", required=True, type=int, dest="number")
    args = parser.parse_args()
    try:
        owner, name = args.repo.split("/", 1)
        if not owner or not name:
            raise ValueError
    except ValueError:
        parser.error("--repo must be in OWNER/NAME form")
    print(
        json.dumps(
            fetch_and_filter_review_threads(owner=owner, name=name, number=args.number)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
