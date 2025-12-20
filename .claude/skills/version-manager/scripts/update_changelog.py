#!/usr/bin/env python3
"""
Update CHANGELOG.md with new version and commits.

Usage:
    python update_changelog.py <version> [since-ref]

Output: Prepends new changelog entry to CHANGELOG.md
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path
import re


def get_commits_since(since_ref=None):
    """Get commits since reference, grouped by type."""
    if since_ref is None:
        # Get last tag
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0", "--match=v*"],
                capture_output=True,
                text=True,
                check=True
            )
            since_ref = result.stdout.strip()
        except subprocess.CalledProcessError:
            since_ref = None

    if since_ref:
        cmd = ["git", "log", f"{since_ref}..HEAD", "--format=%s"]
    else:
        cmd = ["git", "log", "HEAD", "--format=%s"]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    commits = [line.strip() for line in result.stdout.split('\n') if line.strip()]

    # Group by type
    grouped = {
        'breaking': [],
        'feat': [],
        'fix': [],
        'docs': [],
        'chore': [],
        'refactor': [],
        'test': [],
        'other': []
    }

    for commit in commits:
        # Parse conventional commit
        pattern = r'^(\w+)(\([^)]+\))?(!)?: (.+)$'
        match = re.match(pattern, commit)

        if match:
            commit_type = match.group(1)
            breaking = match.group(3) == '!'
            description = match.group(4)

            if breaking:
                grouped['breaking'].append(description)
            elif commit_type in grouped:
                grouped[commit_type].append(description)
            else:
                grouped['other'].append(commit)
        else:
            grouped['other'].append(commit)

    return grouped


def generate_changelog_entry(version: str, since_ref=None) -> str:
    """Generate changelog entry for version."""
    commits = get_commits_since(since_ref)
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"## [{version}] - {today}",
        ""
    ]

    # Breaking changes first
    if commits['breaking']:
        lines.append("### ⚠️ BREAKING CHANGES")
        lines.append("")
        for item in commits['breaking']:
            lines.append(f"- {item}")
        lines.append("")

    # Features
    if commits['feat']:
        lines.append("### ✨ Features")
        lines.append("")
        for item in commits['feat']:
            lines.append(f"- {item}")
        lines.append("")

    # Bug fixes
    if commits['fix']:
        lines.append("### 🐛 Bug Fixes")
        lines.append("")
        for item in commits['fix']:
            lines.append(f"- {item}")
        lines.append("")

    # Documentation
    if commits['docs']:
        lines.append("### 📚 Documentation")
        lines.append("")
        for item in commits['docs']:
            lines.append(f"- {item}")
        lines.append("")

    # Refactoring
    if commits['refactor']:
        lines.append("### ♻️ Refactoring")
        lines.append("")
        for item in commits['refactor']:
            lines.append(f"- {item}")
        lines.append("")

    # Other
    other_items = commits['chore'] + commits['test'] + commits['other']
    if other_items:
        lines.append("### 🔧 Maintenance")
        lines.append("")
        for item in other_items:
            lines.append(f"- {item}")
        lines.append("")

    return '\n'.join(lines)


def update_changelog(version: str, since_ref=None, changelog_path: str = "CHANGELOG.md"):
    """Update CHANGELOG.md with new entry."""
    changelog_path = Path(changelog_path)

    # Generate new entry
    new_entry = generate_changelog_entry(version, since_ref)

    # Read existing changelog or create new one
    if changelog_path.exists():
        with open(changelog_path) as f:
            existing_content = f.read()

        # Find where to insert (after # Changelog header if it exists)
        if existing_content.startswith("# Changelog"):
            # Split on the first blank line to preserve the rest of the file.
            parts = re.split(r"\n\s*\n", existing_content, maxsplit=1)
            if len(parts) == 2:
                header, rest = parts
                content = f"{header}\n\n{new_entry}\n\n{rest}"
            else:
                content = f"{existing_content}\n\n{new_entry}\n"
        else:
            # Prepend with header
            content = f"# Changelog\n\n{new_entry}\n\n{existing_content}"
    else:
        # Create new changelog
        content = f"# Changelog\n\n{new_entry}\n"

    # Write back
    with open(changelog_path, 'w') as f:
        f.write(content)

    print(f"✅ Updated {changelog_path}")
    print(f"\nNew entry:\n{new_entry}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_changelog.py <version> [since-ref] [changelog-path]", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    since_ref = sys.argv[2] if len(sys.argv) > 2 else None
    changelog_path = sys.argv[3] if len(sys.argv) > 3 else "CHANGELOG.md"

    update_changelog(version, since_ref, changelog_path)
