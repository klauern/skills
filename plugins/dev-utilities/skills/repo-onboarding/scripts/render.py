#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render the repo-onboarding HTML from a JSON data file and the template.

Usage: uv run render.py <data.json> [template.html]
Writes a uniquely named temporary HTML file and prints its path.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any


def safe_json_for_script(data: Any) -> str:
    """Serialize JSON without allowing data to terminate the HTML script tag."""
    serialized = json.dumps(data, ensure_ascii=False)
    return serialized.translate(str.maketrans({
        "<": r"\u003c",
        ">": r"\u003e",
        "&": r"\u0026",
        "\u2028": r"\u2028",
        "\u2029": r"\u2029",
    }))


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: uv run render.py <data.json> [template.html]", file=sys.stderr)
        sys.exit(2)

    data_path = Path(sys.argv[1]).expanduser()
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("error: data JSON must contain an object", file=sys.stderr)
        sys.exit(1)

    skill_dir = Path(__file__).resolve().parent.parent
    template_path = Path(sys.argv[2]) if len(sys.argv) > 2 else skill_dir / "template.html"
    template = template_path.read_text(encoding="utf-8")

    rendered = template.replace("%%DATA%%", safe_json_for_script(data))

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", prefix="repo-onboarding-", suffix=".html", delete=False
    ) as output:
        output.write(rendered)
        out_path = Path(output.name)
    print(out_path)


if __name__ == "__main__":
    main()
