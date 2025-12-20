#!/usr/bin/env python3
"""
Detect what changed in a plugin since the last version tag.

Usage:
    python detect_changes.py <plugin-path>

Output (JSON):
    {
        "skills_changed": ["skill-name-1", "skill-name-2"],
        "commands_changed": ["command-1.md", "command-2.md"],
        "metadata_changed": bool,
        "other_files": ["file1", "file2"]
    }
"""

import json
import sys
from pathlib import Path
import subprocess


def get_last_version_tag():
    """Get the most recent version tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "--match=v*"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # No tags found, compare against initial commit
        result = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()


def get_changed_files(since_ref):
    """Get list of changed files since reference."""
    result = subprocess.run(
        ["git", "diff", "--name-only", since_ref, "HEAD"],
        capture_output=True,
        text=True,
        check=True
    )
    return [line.strip() for line in result.stdout.split('\n') if line.strip()]


def detect_changes(plugin_path: str):
    """Detect what changed in the plugin."""
    plugin_path = Path(plugin_path).resolve()
    plugin_name = plugin_path.name

    # Get last version tag
    last_tag = get_last_version_tag()

    # Get changed files
    changed_files = get_changed_files(last_tag)

    # Filter files related to this plugin
    plugin_prefix = f"plugins/{plugin_name}/"
    plugin_files = [f for f in changed_files if f.startswith(plugin_prefix)]

    # Also check marketplace.json
    marketplace_changed = ".claude-plugin/marketplace.json" in changed_files

    # Categorize changes
    skills_changed = set()
    commands_changed = []
    metadata_changed = False
    other_files = []

    for file in plugin_files:
        rel_path = file.replace(plugin_prefix, "")

        # Check if it's a skill
        if "/" in rel_path and not rel_path.startswith(".claude-plugin/") and not rel_path.startswith("commands/"):
            skill_name = rel_path.split("/")[0]
            skills_changed.add(skill_name)
        # Check if it's a command
        elif rel_path.startswith("commands/"):
            commands_changed.append(rel_path.replace("commands/", ""))
        # Check if it's metadata
        elif rel_path == ".claude-plugin/plugin.json":
            metadata_changed = True
        else:
            other_files.append(rel_path)

    # Marketplace change affects all plugins
    if marketplace_changed:
        metadata_changed = True

    return {
        "skills_changed": sorted(list(skills_changed)),
        "commands_changed": commands_changed,
        "metadata_changed": metadata_changed,
        "other_files": other_files,
        "since_ref": last_tag
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python detect_changes.py <plugin-path>", file=sys.stderr)
        sys.exit(1)

    result = detect_changes(sys.argv[1])
    print(json.dumps(result, indent=2))
