#!/usr/bin/env python3
"""
Infer semantic version bump type from conventional commits.

Usage:
    python infer_bump_type.py [since-ref]

Output (JSON):
    {
        "bump_type": "major|minor|patch",
        "reason": "explanation",
        "commits_analyzed": [...],
        "breaking_changes": [...],
        "features": [...],
        "fixes": [...]
    }
"""

import json
import sys
import subprocess
import re


def get_commits_since(since_ref=None):
    """Get commit messages since reference."""
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
            # No tags, get all commits
            since_ref = None

    if since_ref:
        cmd = ["git", "log", f"{since_ref}..HEAD", "--format=%H%x1f%s%x1f%b%x1e"]
    else:
        cmd = ["git", "log", "HEAD", "--format=%H%x1f%s%x1f%b%x1e"]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    commits = []
    for record in result.stdout.split('\x1e'):
        record = record.strip('\n')
        if not record:
            continue
        parts = record.split('\x1f')
        if len(parts) >= 3:
            commits.append({
                'hash': parts[0],
                'subject': parts[1],
                'body': '\x1f'.join(parts[2:]).strip()
            })

    return commits


def parse_conventional_commit(subject, body):
    """
    Parse conventional commit format.

    Returns: {type, scope, breaking, description}
    """
    # Pattern: <type>[optional scope][optional !]: <description>
    pattern = r'^(\w+)(\([^)]+\))?(!)?: (.+)$'
    match = re.match(pattern, subject)

    if not match:
        return None

    commit_type = match.group(1)
    scope = match.group(2)[1:-1] if match.group(2) else None
    breaking_marker = match.group(3) == '!'
    description = match.group(4)

    # Check for BREAKING CHANGE in body
    breaking_in_body = 'BREAKING CHANGE:' in body or 'BREAKING-CHANGE:' in body

    return {
        'type': commit_type,
        'scope': scope,
        'breaking': breaking_marker or breaking_in_body,
        'description': description
    }


def infer_bump_type(since_ref=None):
    """Infer the bump type from commits."""
    commits = get_commits_since(since_ref)

    breaking_changes = []
    features = []
    fixes = []
    other = []

    for commit in commits:
        parsed = parse_conventional_commit(commit['subject'], commit['body'])

        if parsed:
            if parsed['breaking']:
                breaking_changes.append(commit)
            elif parsed['type'] == 'feat':
                features.append(commit)
            elif parsed['type'] == 'fix':
                fixes.append(commit)
            else:
                other.append(commit)
        else:
            other.append(commit)

    # Determine bump type
    if breaking_changes:
        bump_type = "major"
        reason = f"Found {len(breaking_changes)} breaking change(s)"
    elif features:
        bump_type = "minor"
        reason = f"Found {len(features)} new feature(s)"
    elif fixes:
        bump_type = "patch"
        reason = f"Found {len(fixes)} bug fix(es)"
    else:
        bump_type = "patch"
        reason = "No conventional commits found, defaulting to patch"

    return {
        "bump_type": bump_type,
        "reason": reason,
        "commits_analyzed": len(commits),
        "breaking_changes": [c['subject'] for c in breaking_changes],
        "features": [c['subject'] for c in features],
        "fixes": [c['subject'] for c in fixes],
        "other": [c['subject'] for c in other]
    }


if __name__ == "__main__":
    since_ref = sys.argv[1] if len(sys.argv) > 1 else None
    result = infer_bump_type(since_ref)
    print(json.dumps(result, indent=2))
