---
name: pr-creator
description: This skill should be used when the user asks to "create a PR", "open a pull request", "fill a PR template from commits", or "prepare PR metadata automatically" with GitHub CLI.
version: 1.0.0
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
gh pr view 2>&1 || true                             # Existing PR? Show URL and stop
BASE="${BASE:-$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)}"
git push -u origin "$(git branch --show-current)"   # Ensure branch is on the remote
```

Honor a user-supplied `--base <branch>` over the detected default, and use `$BASE`
everywhere a base branch appears below — never hardcode `main`.

### Phase 1: Template Discovery

Search locations (in order):
1. `.github/PULL_REQUEST_TEMPLATE.md`
2. `.github/pull_request_template.md`
3. `PULL_REQUEST_TEMPLATE.md`
4. `docs/PULL_REQUEST_TEMPLATE.md`
5. `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates)

**Required field markers**: `[Required]`, `*`, `<!-- Required -->`, `(Required)`

**Commands**: `fd -t f PULL_REQUEST_TEMPLATE .github/ docs/` or `find .github -name "*PULL_REQUEST*"`

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
cat <<'BODY' > /tmp/pr-body.md
## Summary
...
BODY
gh pr create --base "$BASE" --title "feat: Add feature" --body-file /tmp/pr-body.md \
  --label "enhancement" --assignee "@me"
rm -f /tmp/pr-body.md
```

**NEVER use `gh pr create --fill`** — it bypasses all analysis and copies commit
messages verbatim.

**Auto-labels**: `feat:` → enhancement, `fix:` → bug, `docs:` → documentation

## Template Patterns

**Checkbox auto-fill rules**:

| Checkbox | Auto-check when... |
|----------|-------------------|
| "Tests added/updated" | Test files modified |
| "Documentation updated" | `.md` files changed |
| "Breaking change" | `!` or `BREAKING CHANGE:` in commits |
| "Version bump" | `package.json`, `Cargo.toml` etc. modified |

**Issue linking patterns**: `Closes #123`, `Fixes #456`, `Resolves #789`, `Related to #111`

## Model Strategy

| Task | Model | Rationale |
|------|-------|-----------|
| File/template discovery, git ops, parsing | Haiku | Fast, deterministic |
| Commit analysis, PR generation, gap detection | Sonnet | Complex reasoning |

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
