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
- Change summary (fetch the full diff on demand): !`git diff HEAD --stat`
- Untracked-file inventory: !`git ls-files --others --exclude-standard`
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

3. **Inspect All Changes Before Staging or Composing Commit Messages**:
   - Review the full tracked diff with `git diff HEAD`
   - Inventory untracked files with `git ls-files --others --exclude-standard`
   - Read every untracked file in full (or inspect binary metadata when it cannot be read as text)
   - Do not stage files or compose commit messages until both tracked and untracked changes have been inspected

4. Create the commit(s) per the **conventional-commits** skill (same behavior as `/commits:commit`)
   - Analyze the changes and create appropriate conventional commit message(s)
   - Stage relevant untracked files if needed
   - Create commit(s) with well-formatted messages

5. Push the commit(s) to the remote repository:
   - For existing branches: `git push`
   - For new branches: `git push -u origin <branch-name>`

6. Run `git status` to verify the push succeeded

## Execution Strategy

- **For single commits**: branch creation (if needed), commit, and push run sequentially — chain with `&&`
- **For multiple commits**: create all commits first, then push once at the end

## Important

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
