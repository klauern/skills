#!/usr/bin/env python3
"""Deterministic repository fact-gatherer for repo-onboarding.

Walks the repository and prints one JSON object. No network access.
Safe for directories that are not git repositories.

Usage: python3 repo-facts.py [path]
"""
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

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


def run(cmd, cwd):
    try:
        result = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def main():
    target = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.cwd()
    if not target.exists():
        print(json.dumps({"error": "path not found: %s" % target}))
        sys.exit(1)

    facts = {"path": str(target)}

    remote = run(["git", "config", "--get", "remote.origin.url"], target)
    if remote:
        name = remote.rstrip("/").split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]
        facts["repo"] = name
        facts["remote"] = remote
    else:
        facts["repo"] = target.name
        facts["remote"] = None

    facts["isGitRepo"] = run(["git", "rev-parse", "--is-inside-work-tree"], target) == "true"

    ext_counter = Counter()
    manifest_hits = []
    top_tree = {}
    entries = []
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

    recent = run(["git", "log", "--pretty=format:%s", "-n", "25"], target)
    facts["recentCommits"] = [line for line in recent.splitlines() if line.strip()][:25]

    changed = run(["git", "log", "--pretty=format:", "--name-only", "-n", "200"], target)
    dir_counter = Counter()
    for line in changed.splitlines():
        line = line.strip()
        if not line or "/" not in line:
            continue
        dir_counter[line.split("/")[0]] += 1
    facts["activeDirs"] = [d for d, _ in dir_counter.most_common(12)]

    print(json.dumps(facts, indent=2))


if __name__ == "__main__":
    main()
