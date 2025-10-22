---
allowed-tools: Bash
description: Create a PR using gh and PR template if present
---
# /pr

Create a pull request using the GitHub CLI. If a PR template is present, it will be used; otherwise a minimal body will be generated. If some fields can't be inferred from commits or branch context, you'll be asked to fill them.

## Usage

```bash
/pr [--base <branch>] [--draft]
```

## Behavior

1. Look for a PR template in standard locations:
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/pull_request_template.md`
   - `PULL_REQUEST_TEMPLATE.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates)
2. Create the PR with `gh`:
   - Prefer `gh pr create --fill` to use commit info and apply the template automatically
   - If multiple templates exist, select one or pass `--template <name>`
3. If any required sections remain unclear, you'll be prompted to provide them before submission.

## Requirements

- GitHub CLI installed and authenticated (`gh auth status`)

## Example

```bash
gh pr create --fill
```
