---
allowed-tools: Bash, Read, Glob, Grep
description: Update PR title and description based on actual changes
---
# /pr-update

Analyze the actual changes in the current PR and update its title and description to accurately reflect what's being changed. Uses the PULL_REQUEST_TEMPLATE.md if present.

## Usage

```bash
/pr-update [pr-number]
```

If no PR number is provided, uses the PR for the current branch.

## Behavior

This command performs a comprehensive review of the PR and updates it to match reality:

### Steps

1. **Determine PR Number and Info**
   - If provided as argument, use it
   - Otherwise, run: `gh pr view --json number,title,body,baseRefName -q '.'`
   - Extract current title, body, and base branch

2. **Analyze Changes**

   **Commits since base branch:**
   ```bash
   # Get all commits in this PR
   gh pr view <number> --json commits -q '.commits[].commit.message'
   # Or via git
   git log <base-branch>..HEAD --oneline
   ```

   **Changed files:**
   ```bash
   gh pr view <number> --json files -q '.files[].path'
   # Or via git
   git diff --name-status <base-branch>...HEAD
   ```

   **Actual diff content:**
   ```bash
   gh pr diff <number>
   # Or via git
   git diff <base-branch>...HEAD
   ```

3. **Look for PR Template**

   Check standard locations:
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/pull_request_template.md`
   - `PULL_REQUEST_TEMPLATE.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates)

   If found, use its structure as the basis for the updated description.

4. **Analyze and Summarize Changes**

   Based on the commits, files, and diff:
   - What type of change is this? (feat, fix, refactor, docs, chore, etc.)
   - What's the primary goal/purpose?
   - What are the key changes across files?
   - Are there any breaking changes?
   - What's the scope/impact?

5. **Generate Updated Title**

   Create a concise, descriptive title following conventions:
   - Use conventional commit format if appropriate: `type(scope): description`
   - Examples:
     - `feat(users): add email address query support`
     - `fix(api): resolve authentication timeout issue`
     - `docs(readme): improve installation instructions`
   - Keep it under 72 characters
   - Make it action-oriented and specific

6. **Generate Updated Description**

   **If PR template exists:**
   - Use the template structure as a guide
   - Fill in sections based on actual changes:
     - **Description/Summary**: What changed and why (from commits and diff)
     - **Changes**: Bulleted list of key modifications
     - **Testing**: What was tested (look for test files)
     - **References**: Extract ticket numbers (JIRA, GitHub issues)
     - **Checklist items**: Mark completed items based on actual state
   - Preserve any sections that require manual input

   **If no template:**
   - Create structured description:
     ```markdown
     ## Summary
     [What changed and why]

     ## Changes
     - [Key change 1]
     - [Key change 2]

     ## Test Plan
     [Testing approach]

     ## References
     - [Related tickets/issues]
     ```

7. **Show Preview and Get Approval**

   Display:
   ```
   Current Title: [old title]
   New Title:     [proposed title]

   Current Description:
   [old body - first 10 lines]

   Proposed Description:
   [new body]
   ```

   Ask user: "Update the PR with these changes?"

8. **Update PR**

   ```bash
   gh pr edit <number> --title "New Title" --body "New Description"
   ```

   Or if body is long:
   ```bash
   echo "New Description" > /tmp/pr-body.md
   gh pr edit <number> --title "New Title" --body-file /tmp/pr-body.md
   ```

## Example Commands

```bash
# Get PR info
gh pr view --json number,title,body,baseRefName,commits,files

# Get commits in PR
gh pr view 123 --json commits -q '.commits[].commit.message'

# Get changed files
gh pr view 123 --json files -q '.files[] | "\(.path) +\(.additions) -\(.deletions)"'

# View the diff
gh pr diff 123

# Update PR
gh pr edit 123 --title "New title" --body-file /tmp/body.md

# View updated PR
gh pr view 123 --web
```

## Special Considerations

### Conventional Commits
If the repository uses conventional commits, analyze the commit messages and ensure the PR title follows the format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `refactor:` for code refactoring
- `test:` for test additions/changes
- `chore:` for maintenance tasks

### Multiple Concerns
If the PR addresses multiple unrelated changes:
- Note this in the analysis
- Suggest splitting into separate PRs (but don't do it automatically)
- Create a title that encompasses all concerns

### Ticket References
Look for ticket references in:
- Commit messages (JIRA-1234, FSEC-5678, #123)
- Branch names (feature/JIRA-1234-description)
- Existing PR body

Ensure they're included in the references section.

## Implementation Notes

- **CRITICAL**: Always analyze the full diff and all commits, not just the most recent one
- Use `gh pr diff` for the most accurate view of what's changing
- Preserve any manually-written context in the existing PR body
- Don't lose important details the user added manually
- If template has required sections (checkboxes, etc.), maintain them
- Focus on accuracy over creativity - describe what's actually there

## Requirements

- GitHub CLI installed and authenticated (`gh auth status`)
- Current branch associated with a PR or PR number provided
- Permission to edit the PR (must be author or have write access)

## Notes

- This command is safe to run multiple times
- It won't automatically push changes - always shows preview first
- Preserves template structure when present
- Falls back to sensible defaults when no template exists
- Can help ensure PR descriptions stay in sync with code changes
