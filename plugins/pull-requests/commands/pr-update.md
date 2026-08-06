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
   gh pr view [number] --json commits -q '.commits[].commit.message'
   ```
2. Re-run the skill's template discovery and commit/diff analysis against the PR's
   actual base (`baseRefName` — not hardcoded `main`).
3. Generate an updated title and body. **Preserve any manually written content** in the
   existing body (notes, screenshots, discussion links) — merge, don't overwrite.
4. Show a before/after preview and confirm with AskUserQuestion. Display:
   ```text
   Current Title:    [existing title]
   Proposed Title:   [updated title]

   Proposed Description:
   [updated body]
   ```
5. Apply the update. Or if body is long (it always is for a description update), write
   it with a heredoc so multi-line content survives:
   ```bash
   cat <<'BODY' > /tmp/pr-body.md
   [updated description]
   BODY
   gh pr edit [number] --title "[updated title]" --body-file /tmp/pr-body.md
   rm -f /tmp/pr-body.md
   ```
