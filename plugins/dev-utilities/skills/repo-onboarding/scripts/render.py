#!/usr/bin/env python3
"""Render the repo-onboarding HTML from a JSON data file and the template.

Usage: python3 render.py <data.json> [template.html]
Writes /tmp/repo-onboarding-<repo>.html and prints its path.
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("usage: render.py <data.json> [template.html]", file=sys.stderr)
        sys.exit(2)

    data_path = Path(sys.argv[1]).expanduser()
    data = json.loads(data_path.read_text())

    skill_dir = Path(__file__).resolve().parent.parent
    template_path = Path(sys.argv[2]) if len(sys.argv) > 2 else skill_dir / "template.html"
    template = template_path.read_text()

    rendered = template.replace("%%DATA%%", json.dumps(data, ensure_ascii=False))

    repo = data.get("repo") or "repo"
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in repo).strip("-") or "repo"
    out = Path(f"/tmp/repo-onboarding-{safe}.html")
    out.write_text(rendered)
    print(out)


if __name__ == "__main__":
    main()
