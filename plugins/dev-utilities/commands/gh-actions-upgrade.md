---
description: Automatically detect, analyze, and upgrade GitHub Actions in workflows
allowed-tools: Bash, Read, Edit, Glob, Grep, AskUserQuestion
---

# /dev-utilities:gh-actions-upgrade

Upgrade GitHub Actions across this repository's workflows.

## Usage

```bash
/dev-utilities:gh-actions-upgrade
```

## Behavior

Invoke the **gh-actions-upgrader** skill against `.github/workflows/`:

1. Scan workflows for `uses:` references and detect current vs. latest versions (`gh api`).
2. Detect forked actions and recommend upstream migrations.
3. Pull breaking changes from each action's release notes — never from memory.
4. Confirm the upgrade plan with the user before editing.
5. Apply upgrades on a `chore/upgrade-github-actions-<date>` branch and offer to commit
   (`/commits:commit-push`) and open a PR (`/pull-requests:pr`) with per-action notes.

The full workflow, decision tables, and fork-migration guidance live in the skill and its
references — follow those rather than re-deriving steps here.
