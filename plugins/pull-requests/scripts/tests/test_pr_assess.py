# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location("pr_assess", HERE.parent / "pr_assess.py")
assert spec and spec.loader
pr_assess = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pr_assess
spec.loader.exec_module(pr_assess)


def fixture():
    return json.loads((HERE / "fixtures" / "pr-assess-feedback.json").read_text())


class PrAssessClassifierInputTest(unittest.TestCase):
    def test_keyword_report_is_unchanged_in_opt_in_output(self):
        pr = fixture()
        with (
            patch.object(
                pr_assess, "get_repo_identity", return_value=("org", "repo", "org/repo")
            ),
            patch.object(pr_assess, "fetch_graphql", return_value=pr),
            patch.object(
                pr_assess,
                "ensure_worktree",
                return_value=pr_assess.WorktreeResult("reused"),
            ),
        ):
            baseline = pr_assess.build_report(Path("."), 9)
            payload = json.loads(
                pr_assess.build_report(Path("."), 9, include_classifier_input=True)
            )
        self.assertEqual(payload["report"], baseline)
        self.assertIn("Open feedback items: 6", baseline)
        self.assertIn("Resolved items: 1", baseline)
        self.assertIn("Outdated threads filtered: 1", baseline)
        self.assertEqual(payload["omitted"], 0)
        self.assertCountEqual(
            [item["feedback"]["opening"] for item in payload["items"]], pr["expected"]
        )
        opened = {item["feedback"]["opening"]: item for item in payload["items"]}
        negation = opened["Not blocking: consider adding an example to the docs."]
        self.assertEqual(negation["baseline"], "blocking")
        hold = opened["I'd hold the merge until the parser handles empty rows."]
        self.assertEqual(hold["baseline"], "informational")

    def test_latest_replies_retain_order_and_opener_without_identity(self):
        open_items, _, _ = pr_assess.build_triage(fixture())
        payload = pr_assess.classifier_input(open_items)
        item = next(
            item
            for item in payload["items"]
            if "duplicate rows" in item["feedback"]["opening"]
        )
        self.assertEqual(item["baseline"], "blocking")
        self.assertEqual(
            item["feedback"],
            {
                "opening": "Must fix: exports can duplicate rows.",
                "replies": [
                    {"text": "I pushed a fix.", "by_opener": False},
                    {
                        "text": "I tried the fix. This is no longer a blocker and I don't need anything else.",
                        "by_opener": True,
                    },
                ],
            },
        )

    def test_sample_is_bounded_by_recency_and_skips_blank_feedback(self):
        pr = fixture()
        pr["reviewThreads"]["nodes"] = []
        pr["comments"]["nodes"] = [
            {"createdAt": f"2026-01-{i:02d}T12:00:00Z", "body": f"{i} " + "x" * 500}
            for i in range(1, 16)
        ]
        pr["comments"]["nodes"][0]["body"] = "Must fix: this is the oldest item."
        pr["comments"]["nodes"][-1]["body"] = " \n "
        open_items, _, _ = pr_assess.build_triage(pr)
        sample = pr_assess.classifier_input(open_items)
        self.assertEqual(sample["omitted"], 3)
        openings = [item["feedback"]["opening"] for item in sample["items"]]
        self.assertEqual(
            [s.split()[0] for s in openings], [str(i) for i in range(14, 2, -1)]
        )
        self.assertTrue(all(len(s) == 320 and s.endswith("…") for s in openings))


if __name__ == "__main__":
    unittest.main()
