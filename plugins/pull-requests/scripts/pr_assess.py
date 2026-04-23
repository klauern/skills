#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAX_COMMIT_HEADLINES = 8


@dataclass
class WorktreeResult:
    status: str
    path: str | None = None
    head: str | None = None
    note: str | None = None


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = True) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and proc.returncode != 0:
        message = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
        raise RuntimeError(f"{' '.join(cmd)} failed: {message}")
    return proc.stdout.strip()


def run_json(cmd: list[str], *, cwd: Path | None = None) -> Any:
    return json.loads(run(cmd, cwd=cwd))


def sanitize_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return slug or "pr"


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def excerpt(text: str, limit: int = 160) -> str:
    clean = collapse_whitespace(text)
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def classify_comment(text: str) -> str:
    lower = text.lower()
    blocking_terms = [
        "blocking",
        "must fix",
        "must-fix",
        "must change",
        "required",
        "regression",
        "broken",
        "fails",
        "cannot",
        "can't",
        "need to",
        "needs to",
        "please fix",
        "please change",
    ]
    if any(term in lower for term in blocking_terms):
        return "blocking"
    if "?" in text or lower.startswith(("why ", "what ", "how ", "can you", "could you", "should we")):
        return "actionable"
    suggestion_terms = ["consider", "suggest", "maybe", "could we", "would it make sense", "optional"]
    if any(term in lower for term in suggestion_terms):
        return "suggestion"
    nit_terms = ["nit", "typo", "format", "style", "spacing", "rename"]
    if any(term in lower for term in nit_terms):
        return "nit"
    return "informational"


def summarize_paths(files: list[dict[str, Any]]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for file_info in files:
        path = file_info["path"]
        parts = Path(path).parts
        if len(parts) >= 2:
            if parts[0] in {"plugins", "docs", ".github", "scripts", "tests", ".claude"}:
                scope = "/".join(parts[:2])
            else:
                scope = parts[0]
        else:
            scope = "root"
        counts[scope] = counts.get(scope, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def parse_worktree_list(root: Path) -> list[dict[str, str]]:
    output = run(["git", "worktree", "list", "--porcelain"], cwd=root)
    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            if current:
                worktrees.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    if current:
        worktrees.append(current)
    return worktrees


def choose_worktree_base(root: Path) -> Path:
    for candidate in (root / ".worktrees", root / "worktrees"):
        if candidate.exists():
            return candidate
    return root / ".worktrees"


def ensure_worktree(
    root: Path,
    pr_number: int,
    head_ref_name: str,
    head_ref_oid: str,
    head_repo_url: str,
    repo_name_with_owner: str,
    head_repo_name_with_owner: str,
) -> WorktreeResult:
    target_base = choose_worktree_base(root)
    target_slug = sanitize_slug(head_ref_name or f"pr-{pr_number}")
    target_path = target_base / f"pr-{pr_number}-{target_slug}"

    for worktree in parse_worktree_list(root):
        path = worktree.get("worktree")
        head = worktree.get("HEAD")
        if not path:
            continue
        if Path(path).resolve() == target_path.resolve():
            return WorktreeResult(status="reused", path=path, head=head, note="matched deterministic path")
        if head and head == head_ref_oid:
            return WorktreeResult(status="reused", path=path, head=head, note="matched PR head commit")

    if target_path.exists():
        inside_work_tree = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=target_path, check=False) == "true"
        if (target_path / ".git").exists() or inside_work_tree:
            head = run(["git", "rev-parse", "HEAD"], cwd=target_path, check=False) or None
            return WorktreeResult(status="reused", path=str(target_path), head=head, note="existing checkout at target path")
        return WorktreeResult(
            status="conflict",
            path=str(target_path),
            head=head_ref_oid,
            note="target path exists but is not a git worktree",
        )

    target_base.mkdir(parents=True, exist_ok=True)

    fetch_target = "FETCH_HEAD"
    fetch_source = "origin"
    if head_repo_name_with_owner and head_repo_name_with_owner != repo_name_with_owner and head_repo_url:
        fetch_source = head_repo_url

    try:
        run(["git", "fetch", "--depth=1", fetch_source, head_ref_name], cwd=root)
    except RuntimeError:
        return WorktreeResult(
            status="unavailable",
            path=str(target_path),
            head=head_ref_oid,
            note="could not fetch PR head for worktree creation",
        )

    try:
        run(["git", "worktree", "add", "--detach", str(target_path), fetch_target], cwd=root)
    except RuntimeError as exc:
        return WorktreeResult(
            status="unavailable",
            path=str(target_path),
            head=head_ref_oid,
            note=str(exc),
        )

    return WorktreeResult(
        status="created",
        path=str(target_path),
        head=head_ref_oid,
        note="detached at PR head commit",
    )


def fetch_graphql(repo_owner: str, repo_name: str, pr_number: int) -> dict[str, Any]:
    query = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      number
      title
      url
      state
      body
      headRefName
      headRefOid
      baseRefName
      reviewDecision
      additions
      deletions
      changedFiles
      author { login }
      headRepository { url nameWithOwner }
      commits(first: 100) {
        nodes {
          commit {
            oid
            messageHeadline
            messageBody
          }
        }
      }
      files(first: 100) {
        nodes {
          path
          additions
          deletions
        }
      }
      comments(first: 100) {
        nodes {
          author { login }
          body
          createdAt
          url
        }
      }
      reviewThreads(first: 100) {
        nodes {
          isResolved
          isOutdated
          path
          line
          comments(first: 20) {
            nodes {
              author { login }
              body
              createdAt
            }
          }
        }
      }
    }
  }
}
"""
    payload = run_json(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            f"owner={repo_owner}",
            "-F",
            f"name={repo_name}",
            "-F",
            f"number={pr_number}",
        ]
    )
    if "errors" in payload:
        errors = "; ".join(err.get("message", "unknown error") for err in payload["errors"])
        raise RuntimeError(errors)
    pull_request = payload["data"]["repository"]["pullRequest"]
    if pull_request is None:
        raise RuntimeError(f"pull request #{pr_number} not found")
    return pull_request


def get_repo_identity(root: Path) -> tuple[str, str, str]:
    name_with_owner = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], cwd=root)
    owner, name = name_with_owner.split("/", 1)
    return owner, name, name_with_owner


def get_pr_number(root: Path, explicit: str | None) -> int:
    if explicit:
        return int(explicit)
    return int(run(["gh", "pr", "view", "--json", "number", "-q", ".number"], cwd=root))


def format_comment_item(item: dict[str, Any], *, kind: str, source: str) -> str:
    author = item.get("author", {}).get("login", "unknown")
    path = item.get("path")
    line = item.get("line")
    location = ""
    if path:
        location = path
        if line:
            location = f"{path}:{line}"
    prefix = f"[{kind.upper()}]"
    if source == "thread":
        prefix = f"{prefix} thread"
    else:
        prefix = f"{prefix} comment"
    if location:
        prefix = f"{prefix} {location}"
    body = item.get("body", "")
    return f"- {prefix} @{author}: {excerpt(body)}"


def build_triage(pull_request: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    open_items: list[dict[str, Any]] = []
    resolved_items: list[dict[str, Any]] = []
    outdated_count = 0

    for comment in pull_request.get("comments", {}).get("nodes", []):
        body = comment.get("body", "")
        item = {
            "source": "comment",
            "author": comment.get("author", {}),
            "body": body,
        }
        item["kind"] = classify_comment(body)
        open_items.append(item)

    for thread in pull_request.get("reviewThreads", {}).get("nodes", []):
        comments = thread.get("comments", {}).get("nodes", [])
        if not comments:
            continue
        body = comments[0].get("body", "")
        item = {
            "source": "thread",
            "author": comments[0].get("author", {}),
            "body": body,
            "path": thread.get("path"),
            "line": thread.get("line"),
        }
        item["kind"] = classify_comment(body)
        if thread.get("isOutdated"):
            outdated_count += 1
            continue
        if thread.get("isResolved"):
            resolved_items.append(item)
        else:
            open_items.append(item)

    def sort_key(item: dict[str, Any]) -> tuple[int, str]:
        order = {"blocking": 0, "actionable": 1, "suggestion": 2, "nit": 3, "informational": 4}
        return order.get(item["kind"], 4), item.get("author", {}).get("login", "")

    open_items.sort(key=sort_key)
    resolved_items.sort(key=sort_key)
    return open_items, resolved_items, outdated_count


def build_report(root: Path, pr_number: int) -> str:
    repo_owner, repo_name, repo_name_with_owner = get_repo_identity(root)
    pr = fetch_graphql(repo_owner, repo_name, pr_number)

    head_repo = pr.get("headRepository") or {}
    head_repo_url = head_repo.get("url") or ""
    worktree = ensure_worktree(
        root,
        pr_number=pr["number"],
        head_ref_name=pr.get("headRefName", ""),
        head_ref_oid=pr.get("headRefOid", ""),
        head_repo_url=head_repo_url,
        repo_name_with_owner=repo_name_with_owner,
        head_repo_name_with_owner=head_repo.get("nameWithOwner", ""),
    )

    files = pr.get("files", {}).get("nodes", [])
    commits = pr.get("commits", {}).get("nodes", [])
    open_items, resolved_items, outdated_count = build_triage(pr)

    lines: list[str] = []
    lines.append("# PR Assessment")
    lines.append("")
    lines.append("## PR")
    lines.append(f"- Number: #{pr['number']}")
    lines.append(f"- Title: {pr.get('title', '')}")
    lines.append(f"- URL: {pr.get('url', '')}")
    lines.append(f"- State: {pr.get('state', '')}")
    lines.append(f"- Branch: {pr.get('headRefName', '')} -> {pr.get('baseRefName', '')}")
    author = pr.get("author") or {}
    lines.append(f"- Author: @{author.get('login', 'unknown')}")
    lines.append(f"- Review decision: {pr.get('reviewDecision') or 'unknown'}")
    lines.append("")
    lines.append("## Workspace")
    lines.append(f"- Status: {worktree.status}")
    if worktree.path:
        lines.append(f"- Path: {worktree.path}")
    if worktree.head:
        lines.append(f"- Head: {worktree.head}")
    if worktree.note:
        lines.append(f"- Note: {worktree.note}")
    lines.append("")
    lines.append("## Change Summary")
    lines.append(f"- Files: {pr.get('changedFiles', len(files))}")
    lines.append(f"- Additions: {pr.get('additions', 0)}")
    lines.append(f"- Deletions: {pr.get('deletions', 0)}")
    if files:
        lines.append("- Areas:")
        for scope, count in summarize_paths(files)[:6]:
            lines.append(f"  - {scope}: {count} file(s)")
    if commits:
        lines.append("- Recent commits:")
        for commit in commits[:MAX_COMMIT_HEADLINES]:
            headline = commit.get("commit", {}).get("messageHeadline", "")
            lines.append(f"  - {headline}")
    lines.append("")
    lines.append("## Comment Triage")
    lines.append(f"- Open feedback items: {len(open_items)}")
    if open_items:
        for item in open_items[:20]:
            lines.append(format_comment_item(item, kind=item["kind"], source=item["source"]))
    lines.append(f"- Resolved items: {len(resolved_items)}")
    if resolved_items:
        for item in resolved_items[:10]:
            lines.append(format_comment_item(item, kind=item["kind"], source=item["source"]))
    lines.append(f"- Outdated threads filtered: {outdated_count}")
    lines.append("")
    lines.append("## Follow-up Notes")
    if open_items:
        blocking = sum(1 for item in open_items if item["kind"] == "blocking")
        actionable = sum(1 for item in open_items if item["kind"] == "actionable")
        lines.append(f"- Address {blocking} blocking item(s) and {actionable} question(s)/actionable comment(s) before posting replies.")
    else:
        lines.append("- No open actionable feedback found.")
    if worktree.status == "created":
        lines.append("- Use the dedicated worktree for any follow-up code changes.")
    elif worktree.status == "reused":
        lines.append("- Reused an existing dedicated worktree.")
    elif worktree.status == "conflict":
        lines.append("- Worktree path conflict needs manual resolution before code changes.")
    else:
        lines.append("- Worktree creation was unavailable; inspect the note above.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess a pull request and summarize actionable feedback.")
    parser.add_argument("pr_number", nargs="?", help="Optional PR number. Defaults to the current branch PR.")
    args = parser.parse_args()

    root = Path(run(["git", "rev-parse", "--show-toplevel"]))

    try:
        pr_number = get_pr_number(root, args.pr_number)
        report = build_report(root, pr_number)
    except Exception as exc:  # pragma: no cover - surfaced directly to the user
        print(f"pr-assess: {exc}", file=sys.stderr)
        return 1

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
