---
allowed-tools: Bash, AskUserQuestion
description: Analyze changes and split them into multiple atomic commits with proper conventional commit messages.
---

## Instructions

1. Run `git status` to check current staging state
2. Run `git diff --stat` and `git diff --cached --stat` to see change summary
3. Run `git diff --name-status` to list all changed files with status

4. Analyze the changes and group them by:
   - Change type (feat, fix, refactor, test, docs, chore)
   - Scope (module/component based on directory)
   - Logical feature or purpose

5. Present a split plan showing:
   - Number of proposed commits
   - For each commit: type, scope, description, and files included
   - Suggested commit order

6. Use AskUserQuestion to confirm the plan or allow modifications

7. For each commit in the plan:
   - Stage the relevant files: `git add <files>`
   - Create the commit with heredoc:
     ```bash
     git commit -m "$(cat <<'EOF'
     type(scope): description
     EOF
     )"
     ```

8. After all commits, run `git log --oneline -n <count>` to show results

## Split Guidelines

- **Atomic**: Each commit should be self-contained
- **Ordered**: Infrastructure before features, features before tests
- **Scoped**: Use directory names for scopes when clear
- **Independent**: Each commit should build/pass tests independently

## Example Output

```
Proposed Split Plan (3 commits):

1. feat(auth): add user authentication endpoint
   Files: src/auth/login.ts, src/auth/types.ts

2. test(auth): add authentication unit tests
   Files: tests/auth/login.test.ts

3. docs(auth): document authentication API
   Files: docs/api/auth.md

Proceed with this split?
```
