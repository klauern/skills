#!/usr/bin/env python3
"""
Bump semantic version in plugin.json and marketplace.json files.

Usage:
    python bump_version.py <plugin-path> <major|minor|patch> [--dry-run]

Output (JSON):
    {
        "plugin": {
            "old_version": "1.2.3",
            "new_version": "1.3.0",
            "file": "path/to/plugin.json"
        },
        "marketplace": {
            "old_version": "2.0.0",
            "new_version": "2.1.0",
            "file": ".claude-plugin/marketplace.json"
        }
    }
"""

import json
import sys
from pathlib import Path
from typing import Tuple


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse semantic version string."""
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(int(p) for p in parts)


def bump_version(version: str, bump_type: str) -> str:
    """Bump a semantic version."""
    major, minor, patch = parse_version(version)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_json_file(file_path: Path, new_version: str, dry_run: bool = False, is_marketplace: bool = False) -> dict:
    """Update version in JSON file."""
    with open(file_path) as f:
        data = json.load(f)

    # Handle marketplace.json nested structure
    if is_marketplace:
        old_version = data.get("metadata", {}).get("version", "0.0.0")
        if not dry_run:
            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"]["version"] = new_version
    else:
        old_version = data.get("version", "0.0.0")
        if not dry_run:
            data["version"] = new_version

    if not dry_run:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')  # Add trailing newline

    return {
        "old_version": old_version,
        "new_version": new_version,
        "file": str(file_path)
    }


def bump_plugin_version(plugin_path: str, bump_type: str, dry_run: bool = False):
    """Bump plugin and marketplace versions."""
    plugin_path = Path(plugin_path).resolve()
    repo_root = plugin_path.parent.parent  # plugins/plugin-name -> repo root

    # Plugin file
    plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        raise FileNotFoundError(f"Plugin file not found: {plugin_json}")

    # Marketplace file
    marketplace_json = repo_root / ".claude-plugin" / "marketplace.json"
    if not marketplace_json.exists():
        raise FileNotFoundError(f"Marketplace file not found: {marketplace_json}")

    # Read current plugin version
    with open(plugin_json) as f:
        plugin_data = json.load(f)
    current_plugin_version = plugin_data.get("version", "0.0.0")

    # Calculate new version
    new_version = bump_version(current_plugin_version, bump_type)

    # Update plugin.json
    plugin_result = update_json_file(plugin_json, new_version, dry_run)

    # Read current marketplace version
    with open(marketplace_json) as f:
        marketplace_data = json.load(f)
    current_marketplace_version = marketplace_data.get("metadata", {}).get("version", "0.0.0")

    # Marketplace version should track the highest plugin version.
    current_marketplace_tuple = parse_version(current_marketplace_version)
    new_version_tuple = parse_version(new_version)
    marketplace_new_version = current_marketplace_version
    if new_version_tuple > current_marketplace_tuple:
        marketplace_new_version = new_version

    # Update marketplace.json (note: is_marketplace=True for nested structure)
    marketplace_result = update_json_file(marketplace_json, marketplace_new_version, dry_run, is_marketplace=True)

    return {
        "plugin": plugin_result,
        "marketplace": marketplace_result,
        "dry_run": dry_run
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python bump_version.py <plugin-path> <major|minor|patch> [--dry-run]", file=sys.stderr)
        sys.exit(1)

    plugin_path = sys.argv[1]
    bump_type = sys.argv[2]
    dry_run = "--dry-run" in sys.argv

    if bump_type not in ["major", "minor", "patch"]:
        print("Error: bump_type must be 'major', 'minor', or 'patch'", file=sys.stderr)
        sys.exit(1)

    result = bump_plugin_version(plugin_path, bump_type, dry_run)
    print(json.dumps(result, indent=2))
