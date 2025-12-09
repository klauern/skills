---
allowed-tools: Bash
description: Commit and Push with Conventional Commits
---

Create a well-formatted commit using the Conventional Commits specification and push it to the remote repository.

## Arguments

- `$ARGUMENTS` - Optional: target branch name (e.g., `main`, `master`, or a feature branch name)
  - If provided, commits directly to the specified branch (skips feature branch creation)
  - If omitted, follows the default branch safety check behavior

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Target branch argument: `$ARGUMENTS`

## Instructions

1. **Branch Safety Check**:
   - **If `$ARGUMENTS` is provided**: Skip branch creation and commit directly to current branch
     - If argument is `main` or `master` and you're not on that branch, checkout to it first
     - If argument matches current branch, proceed directly to commit
     - If argument is a different branch name, checkout to it (create if needed)
   - **If `$ARGUMENTS` is empty/not provided** (default behavior):
     - If current branch is `main` or `master`, create a new feature branch first
     - Use a descriptive branch name based on the changes being committed
     - Examples: `git checkout -b feature/add-user-auth`, `git checkout -b fix/memory-leak`, `git checkout -b chore/update-deps`
     - If already on a feature branch, proceed to next step

2. Follow all instructions from [`commit.md`](commit.md) to create the commit(s)
   - Analyze the changes and create appropriate conventional commit message(s)
   - Stage relevant untracked files if needed
   - Create commit(s) with well-formatted messages

3. Push the commit(s) to the remote repository:
   - For existing branches: `git push`
   - For new branches: `git push -u origin <branch-name>`

4. Run `git status` to verify the push succeeded

## Execution Strategy

- You have the capability to call multiple tools in a single response
- **For single commits**: Execute branch creation (if needed), commit, and push in parallel where possible
- **For multiple commits**: Create all commits first, then push once at the end
- Use efficient bash chaining with `&&` where appropriate

## Important

- See [`commit.md`](commit.md) for detailed commit creation instructions
- By default, never commit directly to `main` or `master` - create a feature branch
- **Exception**: If user explicitly provides `main` or `master` as the `$ARGUMENTS`, commit directly to that branch
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
