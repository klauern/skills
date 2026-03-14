---
allowed-tools: Bash, Read, Glob, Grep, AskUserQuestion
description: Create a PR using gh and PR template if present
---
# /pr

Create a pull request by analyzing the actual diff, generating a structured description, and using the PR template if present.

## Usage

```bash
/pr [--base <branch>] [--draft]
```

## Behavior

### Step 1: Preflight Checks

1. **Check for existing PR** for the current branch:
   ```bash
   gh pr view 2>&1 || true
   ```
   If a PR already exists, show its URL and stop.

2. **Determine base branch** (default: `main`). Parse `--base` and `--draft` arguments if provided.

3. **Ensure branch is pushed** to remote:
   ```bash
   git push -u origin "$(git branch --show-current)" 2>&1
   ```

### Step 2: Gather Context (run in parallel)

Collect all information needed to write a good PR description:

**Commits in this PR:**
```bash
git log main..HEAD --pretty=format:"%s%n%b" --reverse
```

**Changed files with stats:**
```bash
git diff main...HEAD --stat
git diff --name-status main...HEAD
```

**Full diff:**
```bash
git diff main...HEAD
```

**Branch name** (may contain ticket references):
```bash
git branch --show-current
```

### Step 3: Look for PR Template

Check standard locations using robust detection:

1. `.github/PULL_REQUEST_TEMPLATE.md`
2. `.github/pull_request_template.md`
3. `PULL_REQUEST_TEMPLATE.md`
4. `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates directory)

Use `fd` if available, fall back to `find`:
```bash
fd -t f -e md -i "pull_request_template" .github 2>/dev/null || \
  find .github -type f -iname "*pull_request_template*.md" 2>/dev/null
```

### Step 4: Analyze Changes and Generate Description

**CRITICAL**: This is the key step that makes `/pr` produce useful descriptions. Do NOT skip this and fall back to `--fill`.

Based on the commits, files, and diff, analyze:
- What type of change is this? (feat, fix, refactor, docs, chore, etc.)
- What's the primary goal/purpose?
- What are the key changes across files?
- Are there any breaking changes?
- What's the scope/impact?

**Extract references automatically:**
- JIRA tickets from commits or branch name (e.g., `FSEC-1234`)
- GitHub issue references (`#123`, `closes #123`, `fixes #123`)

**Generate PR title:**
- Use conventional commit format: `type(scope): description`
- Keep under 72 characters
- If the first commit already has a good conventional commit title, use it

**Generate PR description:**

**If PR template exists:**
- Read the template file
- Fill in sections based on actual diff analysis:
  - **Description/Summary**: What changed and why (synthesized from commits and diff)
  - **Changes**: Bulleted list of key modifications with context
  - **Testing**: What was tested (look for test file changes in the diff)
  - **References**: Extracted ticket numbers
  - **Checklist items**: Auto-check items based on actual state (tests added? docs updated?)
- Preserve template structure and any sections that require manual input

**If no PR template exists:**
- Generate a structured description:
  ```markdown
  ## Summary
  [1-2 sentence description of what changed and why, synthesized from diff analysis]

  ## Changes
  - [Key change 1 with context]
  - [Key change 2 with context]

  ## Test Plan
  - [ ] [Testing step based on what changed]

  ## References
  - [Ticket references if found]
  ```

### Step 5: Preview and Confirm

Show the user:
```
Title: [proposed title]

Description:
[proposed body]
```

Ask: "Create PR with this title and description?" using AskUserQuestion.

### Step 6: Create PR

Write the body to a temp file and create the PR non-interactively:

```bash
# Write body to temp file
cat <<'BODY' > /tmp/pr-body.md
[generated description]
BODY

# Create PR
gh pr create --base <branch> --title "<title>" --body-file /tmp/pr-body.md [--draft]

# Clean up
rm -f /tmp/pr-body.md
```

**NEVER use `gh pr create --fill`** — it bypasses all analysis and just copies commit messages verbatim.

### Step 7: Report

Display the PR URL to the user.

## Implementation Notes

- **CRITICAL**: Always analyze the full diff and all commits, not just the most recent one
- **NEVER use `--fill`** — always generate a structured description from diff analysis
- Use `gh pr diff` or `git diff main...HEAD` for the most accurate view of changes
- Focus on accuracy over creativity — describe what's actually there
- The "why" comes from commit messages; the "what" comes from the diff
- If the diff is very large (>500 lines), summarize by file/area rather than line-by-line
- For single-commit PRs, the commit message is a good starting point but still enhance it with diff context

## Conventional Commits

If the repository uses conventional commits, analyze commit messages for the PR title:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `refactor:` for code refactoring
- `test:` for test additions/changes
- `chore:` for maintenance tasks

## Ticket References

Look for ticket references in:
- Commit messages (`JIRA-1234`, `FSEC-5678`, `#123`)
- Branch names (`feature/FSEC-1234-description`, `fix/issue-456`)
- Extract and include in the References section

## Checkbox Auto-fill

When filling template checklists, auto-check based on evidence:

| Checkbox | Auto-check when... |
|----------|-------------------|
| "Tests added/updated" | Test files modified in diff |
| "Documentation updated" | `.md` files changed |
| "Breaking change" | `!` or `BREAKING CHANGE:` in commits |
| "Version bump" | `package.json`, `Cargo.toml`, `plugin.json` etc. modified |

## Requirements

- GitHub CLI installed and authenticated (`gh auth status`)
- Git repository with remote
- At least one commit on branch vs. base
- `fd` command (optional, for enhanced template detection)

## Examples

```bash
# Create PR against main (default)
/pr

# Create PR against staging branch
/pr --base staging

# Create draft PR
/pr --draft

# Create draft PR against specific base
/pr --base develop --draft
```
