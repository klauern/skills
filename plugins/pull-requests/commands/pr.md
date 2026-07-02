---
allowed-tools: Bash, Read, Glob, Grep, AskUserQuestion
description: Create a PR using gh and PR template if present
argument-hint: "[--base <branch>] [--draft]"
---

# /pr

Create a pull request by analyzing the actual diff, generating a structured description,
and using the PR template if present.

## Usage

```bash
/pr                      # PR against the repo's default branch
/pr --base staging       # PR against a specific base
/pr --draft              # Draft PR
```

## Behavior

Invoke the **pr-creator** skill, passing `--base`/`--draft` through:

1. Preflight: stop if a PR already exists; resolve `$BASE`; push the branch.
2. Discover the PR template and analyze all commits + the full diff against `$BASE`.
3. Generate a conventional-commit title (≤72 chars) and a structured body — template
   sections filled from diff evidence, or the skill's default structure if no template.
4. Preview title and body, confirm with AskUserQuestion, then create via
   `gh pr create --body-file` per the skill. **Never `--fill`.**
5. Report the PR URL.
