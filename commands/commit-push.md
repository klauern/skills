---
allowed-tools: Bash
description: Commit and Push with Conventional Commits
---

Create a well-formatted commit using the Conventional Commits specification and push it to the remote repository.

## Instructions

1. Follow all instructions from [`commit.md`](commit.md)
2. Push the commit to the remote repository with `git push`
3. Run `git status` to verify the push succeeded

## Important

- See [`commit.md`](commit.md) for detailed commit creation instructions
- After committing, push to remote with `git push`
- Verify the push succeeded by checking the output

## Multiple Commits

If the user wants to create multiple commits:

1. Stage changes for the first commit
2. Create the first commit
3. Repeat for additional commits
4. Push all commits at once with `git push`
