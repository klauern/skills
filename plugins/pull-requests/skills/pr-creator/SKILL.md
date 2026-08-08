---
name: pr-creator
description: This skill should be used when the user asks to "create a PR", "open a pull request", "fill a PR template from commits", or "prepare PR metadata automatically" with GitHub CLI.
version: 1.0.0
author: klauern
---

# PR Creator

Create comprehensive, well-structured pull requests by discovering templates, analyzing commits, and intelligently filling gaps.

## Quick Start

```bash
User: Create a PR for my changes
# or
User: /pr
```

The skill will: find the PR template → analyze branch commits → infer information → ask only for gaps → create PR with `gh`.

## Workflow

### Phase 0: Preflight

```bash
# BEGIN PR_CREATOR_PREFLIGHT
set -euo pipefail
BRANCH=$(git branch --show-current)
[ -n "$BRANCH" ] || { echo "Detached HEAD cannot create a PR" >&2; exit 1; }
if ! EXISTING_PR_URL=$(gh pr list --head "$BRANCH" --state open --limit 1 \
  --json url --jq '.[0].url // ""'); then
  echo "Unable to check for an existing PR" >&2
  exit 1
fi
if [ -n "$EXISTING_PR_URL" ]; then
  printf 'Existing PR: %s\n' "$EXISTING_PR_URL"
  exit 0
fi
BASE="${BASE:-$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)}"
git check-ref-format --branch "$BASE" >/dev/null
git fetch --no-tags origin "refs/heads/$BASE:refs/remotes/origin/$BASE"
git rev-parse --verify "refs/remotes/origin/$BASE^{commit}" >/dev/null
git push -u origin "$BRANCH"                       # Ensure branch is on the remote
# END PR_CREATOR_PREFLIGHT
```

Honor a user-supplied `--base <branch>` over the detected default, and use `$BASE`
everywhere a base branch appears below — never hardcode `main`. The successful
empty list is the only no-PR result; authentication, network, and repository
errors stop the workflow. Fetch and verify `origin/$BASE` before any log or diff
so a missing or stale tracking ref cannot drive the analysis.

### Phase 1: Template Discovery

Search locations (in order):
1. `.github/PULL_REQUEST_TEMPLATE.md`
2. `.github/pull_request_template.md`
3. `PULL_REQUEST_TEMPLATE.md`
4. `docs/PULL_REQUEST_TEMPLATE.md`
5. `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates)

**Required field markers**: `[Required]`, `*`, `<!-- Required -->`, `(Required)`

**Command**: `fd -H -t f -i 'pull_request_template' .` (hidden-aware, rooted at `.` so root-level `PULL_REQUEST_TEMPLATE.md` is found too)

### Phase 2: Commit Analysis

**Git commands**:
```bash
git rev-parse --abbrev-ref HEAD                        # Current branch
git log origin/"$BASE"...HEAD --oneline                # Commits
git diff origin/"$BASE"...HEAD --stat --name-status    # Files changed
git diff origin/"$BASE"...HEAD                         # Full diff (summarize by area if >500 lines)
```

Analyze **all** commits and the full diff, not just the latest commit — the "why" comes
from commit messages; the "what" comes from the diff.

**Auto-extracted fields**:

| Field | Extraction Method |
|-------|------------------|
| Title | Most recent commit subject OR branch name pattern |
| Type | Conventional commit prefix (`feat:`, `fix:`, etc.) |
| Issues | `#123`, `closes #123`, `fixes #123` from commits |
| Breaking | `BREAKING CHANGE:` or `!` in commits |
| Tests | `*.test.*`, `*_test.*`, `test_*.*` files modified |
| Docs | `*.md` or `docs/**/*` files modified |

**Branch patterns**: `feature/123-name` → Issue #123, `fix/issue-456` → Issue #456, type: fix

### Phase 3: Gap Detection

**Confidence levels**:
- **High (auto-fill)**: Issue numbers, type, files changed, test/doc status
- **Medium (confirm)**: PR title, scope, checkbox items
- **Low (ask user)**: "Why"/motivation, manual test steps, screenshots, migration guides

### Phase 4: Preview and Create

Show the user the proposed title and body and get approval before creating. Then:

```bash
# BEGIN PR_CREATOR_CREATE
set -euo pipefail
# PR_TITLE/PR_BODY are approved values. Populate these arrays only with
# explicitly requested metadata; leave them empty by default.
declare -p REQUESTED_LABELS >/dev/null 2>&1 || REQUESTED_LABELS=()
declare -p REQUESTED_ASSIGNEES >/dev/null 2>&1 || REQUESTED_ASSIGNEES=()
PR_DRAFT="${PR_DRAFT:-false}"

PR_BODY_FILE=$(mktemp "${TMPDIR:-/tmp}/pr-body.XXXXXX.md")
cleanup_pr_body() { rm -f -- "$PR_BODY_FILE"; }
trap cleanup_pr_body EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
printf '%s\n' "$PR_BODY" >"$PR_BODY_FILE"

create_args=(--base "$BASE" --title "$PR_TITLE" --body-file "$PR_BODY_FILE")
case "$PR_DRAFT" in
  true) create_args+=(--draft) ;;
  false) ;;
  *) echo "PR_DRAFT must be true or false" >&2; exit 1 ;;
esac
if ((${#REQUESTED_LABELS[@]} > 0 || ${#REQUESTED_ASSIGNEES[@]} > 0)); then
  VIEWER_PERMISSION=$(gh repo view --json viewerPermission -q .viewerPermission) || {
    echo "Unable to verify permission for requested PR metadata" >&2; exit 1;
  }
  case "$VIEWER_PERMISSION" in
    ADMIN|MAINTAIN|WRITE|TRIAGE) ;;
    *) echo "Requested metadata requires triage or write permission" >&2; exit 1 ;;
  esac
fi
for label in "${REQUESTED_LABELS[@]}"; do
  [ -n "$label" ] && create_args+=(--label "$label")
done
for assignee in "${REQUESTED_ASSIGNEES[@]}"; do
  [ -n "$assignee" ] && create_args+=(--assignee "$assignee")
done
gh pr create "${create_args[@]}"
# END PR_CREATOR_CREATE
```

`PR_DRAFT=true` comes only from an explicit `--draft` request. Do not infer
labels or self-assignment; apply requested metadata only after the permission
check succeeds. Commit- or branch-derived labels may be shown as suggestions in
the preview, but they must not populate `REQUESTED_LABELS` until the user
explicitly requests them. `mktemp` prevents path collisions,
`printf` preserves text that contains delimiter-like lines such as `BODY` or
`EOF`, and the `EXIT` trap removes the file after success, failure, or a trapped
signal.

**NEVER use `gh pr create --fill`** — it bypasses all analysis and copies commit
messages verbatim.

**Label suggestions**: `feat:` may suggest enhancement, `fix:` may suggest bug,
and `docs:` may suggest documentation. Apply a suggestion only when the user
explicitly requests that label.

## Template Patterns

**Checkbox auto-fill rules**:

| Checkbox | Auto-check when... |
|----------|-------------------|
| "Tests added/updated" | Test files modified |
| "Documentation updated" | `.md` files changed |
| "Breaking change" | `!` or `BREAKING CHANGE:` in commits |
| "Version bump" | `package.json`, `Cargo.toml` etc. modified |

**Issue linking patterns**: `Closes #123`, `Fixes #456`, `Resolves #789`, `Related to #111`

## Requirements

- Git repository with remote
- GitHub CLI (`gh`) installed and authenticated
- At least one commit on branch vs. base

```bash
brew install gh && gh auth login
```

## Error Handling

| Error | Recovery |
|-------|----------|
| No base branch | Try `gh repo view --json defaultBranchRef`, then ask user |
| No commits | Warn and exit |
| No template | Use default structure |
| `gh` not installed | Provide install instructions |
| Not authenticated | Guide: `gh auth login` |

## Example Scenarios

| Scenario | Commits | Template | Skill Behavior |
|----------|---------|----------|----------------|
| Feature + full template | `feat(api): add endpoint` | Comprehensive | Auto-fill type, tests, docs; ask for motivation |
| Hotfix + minimal template | `fix: memory leak` | Summary only | Confirm inferred title, ask for test steps |
| Refactor + no template | `refactor: cleanup` | None | Generate default structure from commits |
| Docs change + multi-template | `docs: update API` | 4 templates | Suggest documentation.md template |

## Limitations

- Requires `gh` CLI (no `hub` or direct API)
- GitHub only (no GitLab/Bitbucket)
- Cannot infer "why" without user input
- Screenshots always need manual upload
