---
allowed-tools: Bash
description: Create a well-formatted commit using the Conventional Commits specification.
---


## Instructions

1. Run `git status` and `git diff` to see all staged and unstaged changes
2. Run `git log -10 --oneline` to see recent commit message style
3. Analyze the changes and create a commit message following the Conventional Commits specification:
   - Use appropriate type (feat, fix, chore, docs, style, refactor, test, etc.)
   - Include scope if relevant
   - Write a clear, concise description
   - Add a body if the changes need explanation
   - Add footer with breaking changes or issue references if needed
4. Stage any relevant untracked files if needed
5. Create the commit using the formatted message
6. Run `git status` to verify the commit succeeded

## Important

- Follow the repository's existing commit message style based on recent commits
- Use a heredoc for the commit message to ensure proper formatting:

  ```bash
  git commit -m "$(cat <<'EOF'
  type(scope): description

  body
  EOF
  )"
  ```
