---
allowed-tools: Bash, Read, Glob, Grep, AskUserQuestion
description: Update PR title and description based on actual changes
argument-hint: "[pr-number]"
---

# /pr-update

Bring an existing PR's title and description back in sync with what the PR actually
changes (useful after follow-up commits). Uses the PR template if present.

## Usage

```bash
/pr-update           # PR for the current branch
/pr-update 123       # Specific PR
```

## Behavior

Follow the **pr-creator** skill's analysis phases, applied to an existing PR:

1. Fetch the PR's current state:
   ```bash
   gh pr view [number] --json number,title,body,baseRefName
   gh pr diff [number]
   gh pr view [number] --json commits -q '.commits[] | [.messageHeadline, .messageBody] | map(select(. != null and . != "")) | join("\n\n") | select(length > 0)'
   ```
2. Re-run the skill's template discovery and commit/diff analysis against the PR's
   actual base (`baseRefName` — not hardcoded `main`).
3. Generate an updated title and body. **Preserve any manually written content** in the
   existing body (notes, screenshots, discussion links) — merge, don't overwrite.
4. Show a before/after preview and confirm with AskUserQuestion.
   Display:
   ```text
   Current Title:    [existing title]
   Proposed Title:   [updated title]

   Proposed Description:
   [updated body]
   ```
5. Apply the update through a unique body file so multi-line content survives.
   Never pass a description inline or embed it in a fixed-delimiter heredoc:
   ```bash
   # BEGIN PR_UPDATE_APPLY
   set -euo pipefail
   PR_BODY_FILE=$(mktemp "${TMPDIR:-/tmp}/pr-body.md.XXXXXX")
   cleanup_pr_body() { rm -f -- "$PR_BODY_FILE"; }
   trap cleanup_pr_body EXIT
   trap 'exit 129' HUP
   trap 'exit 130' INT
   trap 'exit 143' TERM
   printf '%s\n' "$UPDATED_BODY" >"$PR_BODY_FILE"
   gh pr edit "$PR_NUMBER" --title "$UPDATED_TITLE" --body-file "$PR_BODY_FILE"
   # END PR_UPDATE_APPLY
   ```

   `PR_NUMBER`, `UPDATED_TITLE`, and `UPDATED_BODY` are the confirmed preview
   values. `mktemp` prevents concurrent updates from sharing a path, `printf`
   preserves delimiter-like body content, and the `EXIT` trap removes the file
   after successful and failed edits.
