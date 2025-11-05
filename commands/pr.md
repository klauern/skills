---
allowed-tools: Bash
description: Create a PR using gh and PR template if present
---
# /pr

Create a pull request using the GitHub CLI. If a PR template is present, it will be used; otherwise a minimal body will be generated from commits.

## Usage

```bash
/pr [--base <branch>] [--draft]
```

## Behavior

1. **Check for existing PR**: First verify if a PR already exists for the current branch:
   ```bash
   gh pr view
   ```

2. **Look for PR template** in standard locations:
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/pull_request_template.md`
   - `PULL_REQUEST_TEMPLATE.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates)

3. **Create the PR** with appropriate strategy:
   
   **If PR template exists:**
   ```bash
   # Read template and incorporate with commit messages
   gh pr create --body-file .github/PULL_REQUEST_TEMPLATE.md --title "$(git log -1 --pretty=%s)" --base <branch>
   ```
   OR let gh handle it interactively:
   ```bash
   # Opens editor with template pre-filled for manual editing
   gh pr create --base <branch>
   ```
   
   **If no template exists:**
   ```bash
   # Auto-fills from commit messages only
   gh pr create --fill --base <branch>
   ```
   
   **For draft PRs:**
   ```bash
   gh pr create --draft --base <branch>
   ```

4. **Template handling approach**:
   - **CRITICAL**: When a template exists at `.github/PULL_REQUEST_TEMPLATE.md`, DO NOT use `--fill` flag
   - Using `gh pr create --base <branch>` (without `--fill`) will automatically load the template
   - The template will open in your editor where you can:
     - Keep template structure and sections
     - Fill in placeholders (JIRA tickets, justifications, etc.)
     - Add commit context where appropriate
   - The `--fill` flag bypasses templates entirely and only uses commit messages

## Implementation Steps

When executing `/pr` command:

```bash
# 1. Check for existing PR
if gh pr view &>/dev/null; then
  echo "PR already exists for this branch"
  gh pr view --web
  exit 0
fi

# 2. Determine base branch (default: main)
BASE_BRANCH="${1:-main}"
DRAFT_FLAG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --base)
      BASE_BRANCH="$2"
      shift 2
      ;;
    --draft)
      DRAFT_FLAG="--draft"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# 3. Check if PR template exists
if [ -f ".github/PULL_REQUEST_TEMPLATE.md" ]; then
  echo "Found PR template at .github/PULL_REQUEST_TEMPLATE.md"
  # Use template (opens in editor or uses --body-file)
  gh pr create --base "$BASE_BRANCH" $DRAFT_FLAG
else
  echo "No PR template found, using commit messages"
  # No template, auto-fill from commits
  gh pr create --fill --base "$BASE_BRANCH" $DRAFT_FLAG
fi
```

## Requirements

- GitHub CLI installed and authenticated (`gh auth status`)
- Current branch pushed to remote (`git push -u origin <branch>`)
- Text editor configured for gh CLI (optional, set via `gh config set editor <editor>`)

## Common Template Sections

When filling out the PR template, pay attention to:

- **Description**: Explain what changed and why
- **New User Justification**: Required for new IAM users - explain why IAM role isn't possible
- **References**: Link JIRA tickets (e.g., `FSEC-1234`, `SECURE-5678`)
- **Tasks/Steps to Merge**: Review and check off checklist items
- **Important Notes**: Review any module-specific behaviors documented in template

## Examples

```bash
# Create PR against main (uses template if found)
/pr --base main

# Create PR against staging branch
/pr --base staging

# Create draft PR
/pr --draft

# Create draft PR against specific base
/pr --base main --draft

# View existing PR in browser
gh pr view --web
```

## Notes

- **KEY**: The `--fill` flag bypasses templates and uses commit messages only - DO NOT use when template exists
- When a template exists, omit `--fill` to ensure the template structure is preserved
- GitHub automatically detects `.github/PULL_REQUEST_TEMPLATE.md` 
- Most repositories use `main` as the default branch
- For repositories with other base branches, specify with `--base <branch>`
- Templates opened in editor allow you to incorporate commit context while keeping required sections
