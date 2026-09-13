#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare the subagent workflow script by inlining the repo path and facts.

Usage: uv run prepare_workflow.py <repo-path> <facts.json> [--quick] [output.js]

Reads workflows/analyze.js, substitutes the placeholders, and writes a uniquely
named temporary workflow (or the given output path).
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any


def sanitize_remote(remote: str) -> str | None:
    """Remove URL userinfo before facts are copied into agent prompts."""
    value = remote.strip()
    if not value:
        return None
    if "://" in value:
        scheme, rest = value.split("://", 1)
        authority, separator, suffix = rest.partition("/")
        authority = authority.rsplit("@", 1)[-1]
        return f"{scheme}://{authority}{separator}{suffix}" if authority else None
    colon = value.find(":")
    boundary = colon if colon >= 0 else len(value)
    at = value.rfind("@", 0, boundary)
    if at >= 0 and (colon >= 0 or "/" not in value[:at]):
        value = value[at + 1:]
    return value or None


def load_facts(path: Path) -> dict[str, Any]:
    """Load the required facts object, rejecting missing or malformed input."""
    if not path.is_file():
        raise ValueError(f"facts JSON path is not a file: {path}")
    try:
        facts = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid facts JSON at {path}: {exc}") from exc
    if not isinstance(facts, dict):
        raise ValueError(f"facts JSON must contain an object: {path}")
    if isinstance(facts.get("remote"), str):
        facts["remote"] = sanitize_remote(facts["remote"])
    return facts


def main() -> None:
    args = [a for a in sys.argv[1:]]
    quick = False
    if "--quick" in args:
        quick = True
        args.remove("--quick")

    if len(args) < 2 or len(args) > 3:
        print("usage: uv run prepare_workflow.py <repo-path> <facts.json> [--quick] [output.js]", file=sys.stderr)
        sys.exit(2)

    repo = args[0]
    facts_path = Path(args[1]).expanduser()
    try:
        facts = load_facts(facts_path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    skill_dir = Path(__file__).resolve().parent.parent
    template = (skill_dir / "workflows" / "analyze.js").read_text(encoding="utf-8")

    out = (
        template
        .replace("__REPO_PATH__", json.dumps(repo))
        .replace("__FACTS_JSON__", json.dumps(facts))
        .replace("__QUICK__", "true" if quick else "false")
    )

    if len(args) == 3:
        out_path = Path(args[2])
        out_path.write_text(out, encoding="utf-8")
    else:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix="repo-onboarding-", suffix=".js", delete=False
        ) as output:
            output.write(out)
            out_path = Path(output.name)
    print(out_path)


if __name__ == "__main__":
    main()
