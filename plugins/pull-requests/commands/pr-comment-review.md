---
allowed-tools: Bash
description: Review PR comments and build actionable task list
---
# /pr-comment-review

Review all comments on a pull request and build an actionable task list to address feedback.

## Usage

```bash
/pr-comment-review [pr-number]
```

If no PR number is provided, determine it from the current branch.

## Behavior

This command checks **both** types of PR comments:

1. **PR Conversation Comments**: General discussion comments on the PR
2. **PR Review Comments**: Inline code review comments on specific lines/files

### Steps

1. **Determine PR Number**
   - If provided as argument, use it
   - Otherwise, run: `gh pr view --json number -q .number`

2. **Fetch PR Conversation Comments**
   - Run: `gh pr view <number> --json comments -q '.comments[] | "\(.author.login): \(.body)"'`
   - These are general comments on the PR itself

3. **Fetch PR Review Comments**
   - Run: `gh api repos/{owner}/{repo}/pulls/<number>/comments --jq '.[] | "[\(.path):\(.line)] \(.user.login): \(.body)"'`
   - These are inline code review comments with file and line references
   - Alternative: `gh pr view <number> --json reviews -q '.reviews[].body'`

4. **Parse and Categorize**
   - Identify actionable items (requests for changes, questions, concerns)
   - Group by file/area if applicable
   - Note priority based on keywords (blocking, critical, nit, suggestion)

5. **Build Task List**
   - Create organized list of actionable work
   - Include file paths and line numbers for review comments
   - Prioritize: blocking issues → questions → suggestions → nits

6. **Present for Approval**
   - Show the task list to user
   - Ask which items to address or if user wants to prioritize differently

## Example Commands

```bash
# View conversation comments
gh pr view 123 --json comments -q '.comments[] | "\(.author.login): \(.body)"'

# View inline review comments with file context
gh api repos/klauern/skills/pulls/123/comments --jq '.[] | "[\(.path):\(.line)] \(.user.login): \(.body)"'

# Get PR reviews (includes conversation and inline reviews)
gh pr view 123 --json reviews
```

## Notes

- Don't make changes without user approval
- Some comments may be informational only (thanks, LGTM, etc.)
- Focus on actionable feedback that requires code changes
- If unclear about a comment's intent, ask the user for clarification
