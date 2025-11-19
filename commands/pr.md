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

2. **Look for PR template** in standard locations using robust detection:
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/pull_request_template.md`
   - `PULL_REQUEST_TEMPLATE.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates)

   Uses multiple detection methods (direct file checks, `fd` command, `find` fallback) to ensure templates are found reliably.

3. **Create the PR** with appropriate strategy:

   **If PR template exists:**
   ```bash
   # Read template and use with commit title (non-interactive)
   gh pr create --body-file .github/PULL_REQUEST_TEMPLATE.md --title "$(git log -1 --pretty=%s)" --base <branch>
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
   - Use `--body-file` with the template path and `--title` from commit message to create PR non-interactively
   - The template structure is preserved with placeholders that can be filled in via GitHub web UI after creation
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

# 3. Robust PR template detection - check multiple methods
PR_TEMPLATE=""

# Method 1: Check standard locations directly
if [ -f ".github/PULL_REQUEST_TEMPLATE.md" ]; then
  PR_TEMPLATE=".github/PULL_REQUEST_TEMPLATE.md"
elif [ -f ".github/pull_request_template.md" ]; then
  PR_TEMPLATE=".github/pull_request_template.md"
elif [ -f "PULL_REQUEST_TEMPLATE.md" ]; then
  PR_TEMPLATE="PULL_REQUEST_TEMPLATE.md"
fi

# Method 2: Use fd (if available) to find templates
if [ -z "$PR_TEMPLATE" ] && command -v fd &> /dev/null; then
  TEMPLATE_FILE=$(fd -t f -e md -i "pull_request_template" .github 2>/dev/null | head -1)
  if [ -n "$TEMPLATE_FILE" ] && [ -f "$TEMPLATE_FILE" ]; then
    PR_TEMPLATE="$TEMPLATE_FILE"
  fi
fi

# Method 3: Use find as fallback
if [ -z "$PR_TEMPLATE" ]; then
  TEMPLATE_FILE=$(find .github -type f -iname "*pull_request_template*.md" 2>/dev/null | head -1)
  if [ -n "$TEMPLATE_FILE" ] && [ -f "$TEMPLATE_FILE" ]; then
    PR_TEMPLATE="$TEMPLATE_FILE"
  fi
fi

# Method 4: Check for multiple templates directory
if [ -z "$PR_TEMPLATE" ] && [ -d ".github/PULL_REQUEST_TEMPLATE" ]; then
  TEMPLATE_FILE=$(find .github/PULL_REQUEST_TEMPLATE -name "*.md" -type f 2>/dev/null | head -1)
  if [ -n "$TEMPLATE_FILE" ] && [ -f "$TEMPLATE_FILE" ]; then
    PR_TEMPLATE="$TEMPLATE_FILE"
  fi
fi

# 4. Create PR with appropriate method
if [ -n "$PR_TEMPLATE" ]; then
  echo "Found PR template at $PR_TEMPLATE"
  # Get title from latest commit
  PR_TITLE=$(git log -1 --pretty=format:"%s")
  # Get commit body (everything after title, limit to 20 lines)
  COMMIT_BODY_FILE=$(mktemp)
  git log -1 --pretty=format:"%b" | head -20 > "$COMMIT_BODY_FILE"
  # Check for JIRA ticket in commit message (title + body)
  COMMIT_FULL=$(git log -1 --pretty=format:"%s%n%b")
  JIRA_TICKET=$(echo "$COMMIT_FULL" | grep -oE '(FSEC)-[0-9]+' | head -1)

  # If no JIRA ticket found, prompt user
  if [ -z "$JIRA_TICKET" ]; then
    echo ""
    echo "No JIRA ticket found in commit message."
    read -p "Enter JIRA ticket (e.g., FSEC-1234) or press Enter to skip: " JIRA_TICKET
    if [ -z "$JIRA_TICKET" ]; then
      JIRA_TICKET="N/A"
    fi
  else
    echo "Found JIRA ticket: $JIRA_TICKET"
  fi

  # Create temp file with template, replacing placeholders
  TEMP_BODY=$(mktemp)
  if [ -s "$COMMIT_BODY_FILE" ]; then
    # Replace placeholders using uv run python for reliable multiline handling
    uv run python -c "
import sys
with open(sys.argv[1], 'r') as f:
    template = f.read()
with open(sys.argv[2], 'r') as f:
    body = f.read().strip()
jira = sys.argv[3]

# Replace description placeholder
if body:
    template = template.replace('Description of the PR, is it a new role or changing an existing role', body)

# Replace JIRA ticket placeholder
template = template.replace('- JIRA-1234', f'- {jira}')

with open(sys.argv[4], 'w') as f:
    f.write(template)
" "$PR_TEMPLATE" "$COMMIT_BODY_FILE" "$JIRA_TICKET" "$TEMP_BODY"
  else
    # No commit body, just replace JIRA ticket
    uv run python -c "
import sys
template = open(sys.argv[1]).read()
jira = sys.argv[2]
template = template.replace('- JIRA-1234', f'- {jira}')
open(sys.argv[3], 'w').write(template)
" "$PR_TEMPLATE" "$JIRA_TICKET" "$TEMP_BODY"
  fi
  rm -f "$COMMIT_BODY_FILE"
  # Use template with --body-file to avoid interactive prompts
  gh pr create --base "$BASE_BRANCH" --title "$PR_TITLE" --body-file "$TEMP_BODY" $DRAFT_FLAG
  # Clean up temp file
  rm -f "$TEMP_BODY"
else
  echo "No PR template found, using commit messages"
  # No template, auto-fill from commits
  gh pr create --fill --base "$BASE_BRANCH" $DRAFT_FLAG
fi
```

## Template Detection Helpers

The implementation uses multiple detection methods to ensure templates are found:

1. **Direct file checks**: Tests for existence of standard template file paths
2. **fd command**: Uses `fd` (if available) to search for template files by name pattern
3. **find fallback**: Uses standard `find` command as backup search method
4. **Directory check**: Looks for `.github/PULL_REQUEST_TEMPLATE/` directory with multiple templates

This multi-method approach ensures templates are found even if:
- File names have different cases (PULL_REQUEST vs pull_request)
- Templates are in non-standard locations
- Search tools have different capabilities

## Requirements

- GitHub CLI installed and authenticated (`gh auth status`)
- Current branch pushed to remote (`git push -u origin <branch>`)
- Text editor configured for gh CLI (optional, set via `gh config set editor <editor>`)
- `fd` command (optional, for enhanced template detection)
- `find` command (standard Unix tool, fallback for template detection)
- `uv` (for Python script execution with automatic dependency management)

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
- When a template exists, use `--body-file` with `--title` to create PR non-interactively (no prompts)
- The PR is created with the template structure preserved; edit placeholders in GitHub web UI after creation
- Most repositories use `main` as the default branch (falls back to `master` if needed)
- For repositories with other base branches, specify with `--base <branch>`
- PR title is automatically extracted from the latest commit message
- Template detection uses multiple methods to ensure reliability across different environments
- JIRA ticket detection looks for pattern like "FSEC-1234" in commit messages
- Uses `uv run python -c` for universal Python execution without requiring environment setup
