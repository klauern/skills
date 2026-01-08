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

### Comment States

Review comments can have different states that affect their relevance:

| State | Description | Default Behavior |
|-------|-------------|------------------|
| **Open** | Unresolved, not outdated | Show first - ACTION REQUIRED |
| **Resolved** | Marked as resolved by someone | Show at bottom - de-prioritized |
| **Outdated** | Code has changed since comment | Filter out completely |

### Steps

1. **Determine PR Number**
   - If provided as argument, use it
   - Otherwise, run: `gh pr view --json number -q .number`

2. **Fetch PR Conversation Comments**
   - Run: `gh pr view <number> --json comments -q '.comments[] | "\(.author.login): \(.body)"'`
   - These are general comments on the PR itself

3. **Fetch PR Review Threads (with state)**
   Use GraphQL to get review threads with resolution and outdated status:
   ```bash
   echo '{"query": "query { repository(owner: \"OWNER\", name: \"REPO\") { pullRequest(number: NUM) { reviewThreads(first: 100) { nodes { isResolved isOutdated path line resolvedBy { login } comments(first: 10) { nodes { author { login } body createdAt } } } } } } }"}' | gh api graphql --input -
   ```

   Key fields:
   - `isResolved` - Whether the thread has been resolved
   - `isOutdated` - Whether the code has changed (thread is stale)
   - `resolvedBy` - Who resolved it (if resolved)
   - `path` / `line` - File location

4. **Parse and Categorize**
   - **Filter by state first:**
     - Include: `isResolved == false && isOutdated == false` (open, actionable)
     - De-prioritize: `isResolved == true && isOutdated == false` (resolved)
     - Exclude: `isOutdated == true` (stale, irrelevant)
   - Identify actionable items (requests for changes, questions, concerns)
   - Group by file/area if applicable
   - Note priority based on keywords (blocking, critical, nit, suggestion)

5. **Build Task List**
   - Create organized list of actionable work
   - Include file paths and line numbers for review comments
   - **Prioritize by state and severity:**
     1. Open blocking issues
     2. Open questions
     3. Open suggestions
     4. Open nits
     5. Resolved comments (at bottom, for reference)
   - Note count of filtered outdated comments

6. **Present for Approval**
   - Show the task list to user
   - Ask which items to address or if user wants to prioritize differently

## Example Commands

```bash
# Get PR number from current branch
gh pr view --json number -q .number

# View conversation comments
gh pr view 123 --json comments -q '.comments[] | "\(.author.login): \(.body)"'

# Get review threads with state (GraphQL)
echo '{"query": "query { repository(owner: \"myorg\", name: \"myrepo\") { pullRequest(number: 123) { reviewThreads(first: 100) { nodes { isResolved isOutdated path line resolvedBy { login } comments(first: 10) { nodes { author { login } body } } } } } } }"}' | gh api graphql --input -

# Filter to only open (unresolved, not outdated) threads with jq
... | jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false and .isOutdated == false)'

# Count outdated threads that were filtered
... | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isOutdated == true)] | length'
```

## Example Output

```
## Open Comments (3) - Requires Action
- [BLOCKING] src/auth.ts:42 - @reviewer: "Missing null check"
- [SUGGESTION] src/api.ts:15 - @reviewer: "Consider using async/await"
- [QUESTION] README.md:10 - @reviewer: "Should this include examples?"

---
## Resolved Comments (2) - Already addressed
- src/utils.ts:12 - @reviewer: "Add type annotation" (resolved by @klauern)
- src/config.ts:5 - @reviewer: "Typo in variable name" (resolved by @klauern)

(5 outdated comments filtered)
```

## Notes

- Don't make changes without user approval
- Some comments may be informational only (thanks, LGTM, etc.)
- Focus on actionable feedback that requires code changes
- If unclear about a comment's intent, ask the user for clarification
- Outdated comments are filtered by default since they often come from automated tools (e.g., `atlantis plan`) and are no longer relevant
