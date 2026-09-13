#!/usr/bin/env python3
"""Prepare the subagent workflow script by inlining the repo path and facts.

Usage: python3 prepare_workflow.py <repo-path> <facts.json> [--quick] [output.js]

Reads workflows/analyze.js, substitutes the placeholders, and writes the
result to /tmp/repo-onboarding-analyze.js (or the given output path).
"""
import json
import sys
from pathlib import Path


def main():
    args = [a for a in sys.argv[1:]]
    quick = False
    if "--quick" in args:
        quick = True
        args.remove("--quick")

    if len(args) < 2:
        print("usage: prepare_workflow.py <repo-path> <facts.json> [--quick] [output.js]", file=sys.stderr)
        sys.exit(2)

    repo = args[0]
    facts_path = Path(args[1]).expanduser()
    facts = json.loads(facts_path.read_text()) if facts_path.exists() else {}

    skill_dir = Path(__file__).resolve().parent.parent
    template = (skill_dir / "workflows" / "analyze.js").read_text()

    out = (
        template
        .replace("__REPO_PATH__", json.dumps(repo))
        .replace("__FACTS_JSON__", json.dumps(facts))
        .replace("__QUICK__", "true" if quick else "false")
    )

    out_path = Path(args[2]) if len(args) > 2 else Path("/tmp/repo-onboarding-analyze.js")
    out_path.write_text(out)
    print(out_path)


if __name__ == "__main__":
    main()
