#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


def load_script():
    spec = importlib.util.spec_from_file_location("review_threads", HERE.parent / "review_threads.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class ReviewThreadsTest(unittest.TestCase):
    def test_paginates_both_connection_levels_before_filtering(self):
        module = load_script()
        calls: list[dict] = []

        def graphql(query: str, variables: dict) -> dict:
            calls.append(variables.copy())
            if "repository(owner:" in query:
                return fixture("threads-1.json" if variables["threadsCursor"] is None else "threads-2.json")
            return fixture("open-comments-2.json" if variables["threadId"] == "open" else "outdated-comments-2.json")

        result = module.fetch_and_filter_review_threads(
            owner="klauern", name="skills", number=18, graphql=graphql
        )

        self.assertEqual([thread["id"] for thread in result["open"]], ["open"])
        self.assertEqual([comment["body"] for comment in result["open"][0]["comments"]], ["open-1", "open-2"])
        self.assertEqual([thread["id"] for thread in result["resolved"]], ["resolved"])
        self.assertEqual(result["outdatedCount"], 1)
        self.assertEqual(
            calls,
            [
                {"owner": "klauern", "name": "skills", "number": 18, "threadsCursor": None},
                {"threadId": "open", "commentsCursor": "open-comments-1"},
                {"owner": "klauern", "name": "skills", "number": 18, "threadsCursor": "threads-1"},
                {"threadId": "outdated", "commentsCursor": "outdated-comments-1"},
            ],
        )

    def test_command_supports_installed_and_source_script_roots(self):
        command = (HERE.parent.parent / "commands" / "pr-comment-review.md").read_text()
        self.assertIn("CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)/plugins/pull-requests", command)
        self.assertIn('--repo "$REPOSITORY" --pr "$PR_NUMBER"', command)


if __name__ == "__main__":
    unittest.main()
