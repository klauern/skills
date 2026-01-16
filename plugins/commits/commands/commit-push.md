---
allowed-tools: Bash
description: Commit and Push with Conventional Commits
---

Create a well-formatted commit using the Conventional Commits specification and push it to the remote repository.

## Arguments

- `$ARGUMENTS` - Optional: target branch or natural language instruction
  - Examples: `main`, `to main`, `on master`, `feature/my-branch`, `push to main`
  - If a branch name is detected, commits directly to that branch (skips feature branch creation)
  - If omitted or empty, follows the default branch safety check behavior

### Argument Parsing

Extract the target branch from `$ARGUMENTS` by looking for:
- Direct branch names: `main`, `master`, `develop`, `feature/xyz`
- Preposition phrases: `to main`, `on main`, `to master`, `on develop`
- Verbose phrases: `push to main`, `commit to main`, `directly to main`

**Examples**:
| `$ARGUMENTS` value | Extracted branch |
|-------------------|------------------|
| `main` | `main` |
| `to main` | `main` |
| `on master` | `master` |
| `push to main` | `main` |
| `feature/add-auth` | `feature/add-auth` |
| *(empty)* | *(none - use default behavior)* |

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- **Target branch argument: `$ARGUMENTS`**

## Instructions

> **CRITICAL**: Check the "Target branch argument" above FIRST. If it contains a branch name (directly or in a phrase like "to main"), you MUST commit directly to that branch. Do NOT create a new feature branch when a target branch is specified.

1. **Parse Target Branch from `$ARGUMENTS`**:
   - If `$ARGUMENTS` contains text, extract the branch name:
     - Strip prepositions: "to", "on", "push to", "commit to", "directly to"
     - The remaining word is the branch name (e.g., "to main" → `main`)
   - Store this as `TARGET_BRANCH` for the next step

2. **Branch Safety Check**:
   - **If `TARGET_BRANCH` was extracted** (e.g., `main`, `master`, `feature/xyz`):
     - This is an **explicit user request** - proceed without warnings
     - If `TARGET_BRANCH` is `main` or `master` and you're not on that branch, checkout to it first
     - If `TARGET_BRANCH` matches current branch, proceed directly to commit
     - If `TARGET_BRANCH` is a different branch name, checkout to it (create if needed)
   - **If `$ARGUMENTS` is empty/not provided** (default behavior):
     - If current branch is `main` or `master`, create a new feature branch first
     - Use a descriptive branch name based on the changes being committed
     - Examples: `git checkout -b feature/add-user-auth`, `git checkout -b fix/memory-leak`, `git checkout -b chore/update-deps`
     - If already on a feature branch, proceed to next step

3. Follow all instructions from [`commit.md`](commit.md) to create the commit(s)
   - Analyze the changes and create appropriate conventional commit message(s)
   - Stage relevant untracked files if needed
   - Create commit(s) with well-formatted messages

4. Push the commit(s) to the remote repository:
   - For existing branches: `git push`
   - For new branches: `git push -u origin <branch-name>`

5. Run `git status` to verify the push succeeded

## Execution Strategy

- You have the capability to call multiple tools in a single response
- **For single commits**: Execute branch creation (if needed), commit, and push in parallel where possible
- **For multiple commits**: Create all commits first, then push once at the end
- Use efficient bash chaining with `&&` where appropriate

## Important

- **RESPECT USER'S EXPLICIT INTENT**: When `$ARGUMENTS` contains a branch reference (e.g., "main", "to main", "push to main"), the user is **explicitly requesting** to commit to that branch. Honor this request without creating a feature branch or asking for confirmation.
- **Argument parsing**: Extract branch names from phrases - "to main" means branch `main`, "on master" means branch `master`
- See [`commit.md`](commit.md) for detailed commit creation instructions
- **Default behavior** (when `$ARGUMENTS` is empty): never commit directly to `main` or `master` - create a feature branch first
- **Explicit request** (when `$ARGUMENTS` specifies `main`/`master`): commit directly to that branch - this overrides the default safety behavior
- Follow the repository's existing commit style based on recent commit history
- Use heredoc for multi-line commit messages
- Verify the push succeeded by checking the output

## Multiple Commits

If the user wants to create multiple commits:

1. Perform branch safety check (create new branch if on main)
2. Stage changes for the first commit
3. Create the first commit
4. Repeat staging and committing for additional commits
5. Push all commits at once with `git push` (or `git push -u origin <branch>` for new branches)
