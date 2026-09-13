#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic repository fact-gatherer for repo-onboarding.

Walks the repository and prints one JSON object. No network access.
Safe for directories that are not git repositories.

Usage: uv run repo-facts.py [path]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

MANIFESTS = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "poetry.lock", "uv.lock",
    "Cargo.toml", "Cargo.lock", "go.mod", "go.sum",
    "Makefile", "CMakeLists.txt", "build.gradle", "build.gradle.kts", "pom.xml",
    "Gemfile", "mix.exs", "composer.json", "composer.lock",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml",
    "README.md", "README", "LICENSE", "LICENSE.md", "CONTRIBUTING.md",
    "AGENTS.md", "CODEOWNERS", ".gitmodules", ".gitlab-ci.yml", "Jenkinsfile",
}

ENTRY_STEMS = {"main", "index", "app", "cli", "server", "cmd", "__main__", "run", "start"}

IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
    "target", ".next", ".cache", ".idea", ".vscode", "vendor",
}

MAX_FILES = 60000


def run(cmd: Sequence[str], cwd: Path) -> str:
    """Run a bounded read-only command, returning no output on failure."""
    try:
        result = subprocess.run(
            list(cmd), cwd=str(cwd), capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def sanitize_remote(remote: str) -> str | None:
    """Remove URL userinfo, including the scp-like ``user@host:path`` form."""
    value = remote.strip()
    if not value:
        return None

    if "://" in value:
        scheme, rest = value.split("://", 1)
        authority, separator, suffix = rest.partition("/")
        if "@" in authority:
            authority = authority.rsplit("@", 1)[-1]
        if not authority:
            return None
        return f"{scheme}://{authority}{separator}{suffix}"

    if "@" in value:
        # Git's scp-like syntax has the host/path separator after userinfo.
        # Keep @ characters that occur later in the repository path.
        colon = value.find(":")
        boundary = colon if colon >= 0 else len(value)
        at = value.rfind("@", 0, boundary)
        if at >= 0 and (colon >= 0 or "/" not in value[:at]):
            value = value[at + 1:]
    return value or None


def main() -> None:
    target = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.cwd()
    if not target.exists():
        print(json.dumps({"error": "path not found: %s" % target}))
        sys.exit(1)

    is_git_repo = run(["git", "rev-parse", "--is-inside-work-tree"], target) == "true"
    facts: dict[str, object] = {"path": str(target), "isGitRepo": is_git_repo}

    remote = sanitize_remote(run(["git", "config", "--get", "remote.origin.url"], target)) if is_git_repo else None
    if remote:
        name = remote.rstrip("/").rsplit("/", 1)[-1]
        if ":" in name:
            name = name.rsplit(":", 1)[-1]
        if name.endswith(".git"):
            name = name[:-4]
        facts["repo"] = name
        facts["remote"] = remote
    else:
        facts["repo"] = target.name
        facts["remote"] = None

    ext_counter: Counter[str] = Counter()
    manifest_hits: list[str] = []
    top_tree: dict[str, list[str]] = {}
    entries: list[str] = []
    file_count = 0

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        rel = Path(root).relative_to(target)
        depth = len(rel.parts)

        if depth <= 2:
            top_tree[str(rel)] = sorted(dirs)

        for f in files:
            file_count += 1
            if file_count > MAX_FILES:
                break
            relstr = str(rel / f)
            if depth <= 3 and f in MANIFESTS:
                manifest_hits.append(relstr)
            ext = Path(f).suffix.lower()
            if ext:
                ext_counter[ext] += 1
            if depth <= 3:
                stem = Path(f).stem.lower()
                if stem in ENTRY_STEMS or any(
                    stem.startswith(c) for c in ENTRY_STEMS if len(c) >= 3
                ):
                    entries.append(relstr)
        if file_count > MAX_FILES:
            break
        if depth > 5:
            dirs[:] = []

    facts["languageCounts"] = dict(ext_counter.most_common(25))
    facts["manifests"] = sorted(manifest_hits)[:100]
    facts["topLevel"] = sorted(top_tree.get(".", []))
    facts["directoryMap"] = {k: v for k, v in sorted(top_tree.items())}
    facts["entryCandidates"] = entries[:60]

    if is_git_repo:
        recent = run(["git", "log", "--pretty=format:%s", "-n", "25"], target)
        facts["recentCommits"] = [line for line in recent.splitlines() if line.strip()][:25]

        changed = run(["git", "log", "--pretty=format:", "--name-only", "-n", "200"], target)
        dir_counter: Counter[str] = Counter()
        for line in changed.splitlines():
            line = line.strip()
            if not line or "/" not in line:
                continue
            dir_counter[line.split("/")[0]] += 1
        facts["activeDirs"] = [d for d, _ in dir_counter.most_common(12)]
    else:
        facts["recentCommits"] = []
        facts["activeDirs"] = []

    print(json.dumps(facts, indent=2))


if __name__ == "__main__":
    main()
