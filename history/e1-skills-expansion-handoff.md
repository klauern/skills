# E1 Handoff — Cherry-pick `2f87839` (commits skills expansion)

**Status when this doc was written**: PRs #9, #10, #11 merged. E1 is the last salvageable piece of the stale `fix/version-manager-scripts` branch.

## Goal

Cherry-pick commit `2f87839` from branch `fix/version-manager-scripts` onto a fresh branch off `main`, resolve 5 known conflicts, push, open PR.

The commit contains substantial new work that's worth shipping: two new marketplace skills (`changelog-generator`, `commit-message-linter`), a heavily expanded `commit-splitter` skill, a unified `commit.md` command, and a breaking removal of `commit-push.md`.

## Why this was deferred

When the prior session attempted this with a backgrounded `merge-conflict-resolver` agent under `isolation: "worktree"`, the agent escaped its sandbox and corrupted the parent worktree mid-cherry-pick. We rolled back, fixed the bd hooks (PR #10), and shipped the easier sibling (PR #11) but stopped before re-attempting E1. **Lesson**: in this repo, do E1 inline — no subagents with worktree isolation for git history rewrites until that bug is understood.

## Source commit

```
SHA:    2f87839b85697ceb520eddc99531c5b34882196f
Author: Nick Klauer <klauer@gmail.com>
Date:   Sat Dec 20 12:54:23 2025 -0600
Title:  feat(commits): expand commit workflow skills and docs
Source: branch fix/version-manager-scripts (still present locally and on origin)
Size:   ~3,700 lines of additions across plugins/commits/ + AGENTS.md
```

### What it adds (apply as-is)
- `plugins/commits/changelog-generator/SKILL.md` + 3 references (`format-spec.md`, `grouping-rules.md`, `versioning-guide.md`) — **new skill**
- `plugins/commits/commit-message-linter/SKILL.md` + 3 references (`common-errors.md`, `hook-integration.md`, `validation-rules.md`) — **new skill**
- Expanded `plugins/commits/commit-splitter/SKILL.md` (138 lines) + 3 references (`best-practices.md`, `examples.md`, `splitting-strategies.md`)

### What it modifies (conflicts expected)
- `plugins/commits/.claude-plugin/plugin.json` — bumps version `1.1.1` → `3.0.0` and updates description
- `plugins/commits/commands/commit.md` — rewrites to a unified create/split/push flow (~615 lines)
- `plugins/commits/commit-splitter/SKILL.md` — restructured (main has its own restructure)
- `AGENTS.md` — branch's version is **stale** (255 lines vs main's 453), would regress the file

### What it removes (BREAKING)
- `plugins/commits/commands/commit-push.md` — the slash command `/commits:commit-push` is being replaced by an option on `/commits:commit`. Note this in the PR description as a breaking change.

## Pre-requisites (verify in new session)

```bash
# 1. Confirm bd hooks are working (PR #10 must have landed for your local env)
bd doctor                    # Should show 0 errors
git commit --allow-empty -m "test"  # Should succeed (then: git reset HEAD~)

# 2. Confirm source branch and commit still exist
git fetch origin
git log --oneline -1 fix/version-manager-scripts  # should still show f348236 at tip
git log --oneline 2f87839 | head -1                # confirm commit reachable

# 3. Confirm main is current
git checkout main && git pull
```

## Recipe

### 1. Create fresh target branch

```bash
git checkout -b feat/commits-skills-expansion main
```

### 2. Start cherry-pick

```bash
git cherry-pick 2f87839
```

Expect 5 conflicts (file paths from prior attempt — re-verify in case main has moved):

```
AGENTS.md
plugins/commits/.claude-plugin/plugin.json
plugins/commits/commands/commit-push.md
plugins/commits/commit-splitter/SKILL.md
plugins/commits/commit-splitter/references/examples.md
```

### 3. Resolve each conflict

#### `AGENTS.md` — KEEP MAIN'S VERSION (`--ours`)

The branch's version was last edited when this repo had only the `commits` plugin. It deletes sections for `capacities`, `ticktick`, token budget guidelines, external scripts docs, MCP strategy, etc. Accepting any of these deletions would regress the file.

```bash
git checkout --ours AGENTS.md
git add AGENTS.md
```

If `2f87839` adds a *genuinely new* section about the new skills (changelog-generator, commit-message-linter), inspect with:
```bash
git show 2f87839:AGENTS.md | diff main:AGENTS.md - | grep -A3 "changelog-generator\|commit-message-linter"
```
and hand-port any net-new content. Otherwise, just take main verbatim.

#### `plugins/commits/.claude-plugin/plugin.json` — TAKE BRANCH (`--theirs`)

The version bump `1.1.1` → `3.0.0` and updated description are the legitimate semver consequence of this PR. Verify main's current version first — if it's not `1.1.1` anymore, manually merge so the new version is the higher of (current main + 1 major) or `3.0.0`.

```bash
git checkout --theirs plugins/commits/.claude-plugin/plugin.json
# Verify version makes sense:
cat plugins/commits/.claude-plugin/plugin.json | jq .version
git add plugins/commits/.claude-plugin/plugin.json
```

#### `plugins/commits/commands/commit-push.md` — DELETE (`--theirs` = remove)

The branch deletes this file as part of unifying the command into `commit.md`. This is the breaking change.

```bash
git rm plugins/commits/commands/commit-push.md
```

If main has further-modified this file in its 64 commits, those modifications are lost. That's intentional — the unified `commit.md` is the replacement.

#### `plugins/commits/commit-splitter/SKILL.md` — HAND-MERGE

This is the genuinely contested file. Both sides restructured it:
- `main` restructured for the commit-splitter improvements that landed via PR #5/6/7/8
- The branch (`2f87839`) restructured to reference the new `commit-message-linter` and `changelog-generator` skills

Approach: open the conflicted file, take main's structure as the base, layer in the branch's added cross-references and new patterns. Spend ~10 minutes here, not 30.

```bash
# Open with your editor of choice and resolve the markers manually
${EDITOR:-vim} plugins/commits/commit-splitter/SKILL.md
git add plugins/commits/commit-splitter/SKILL.md
```

#### `plugins/commits/commit-splitter/references/examples.md` — TAKE BRANCH (`--theirs`)

The branch significantly expands examples; main's changes here are likely minor formatting tweaks. If a quick `git diff main:plugins/commits/commit-splitter/references/examples.md 2f87839:plugins/commits/commit-splitter/references/examples.md | wc -l` shows main only changed ≤10 lines, just take the branch's version.

```bash
git checkout --theirs plugins/commits/commit-splitter/references/examples.md
git add plugins/commits/commit-splitter/references/examples.md
```

### 4. Continue and verify

```bash
git -c core.editor=true cherry-pick --continue   # use --no-edit alternative if hook noise blocks
git log --oneline -1                              # should show the cherry-picked commit
git show --stat HEAD                              # spot-check the final tree
```

### 5. Sanity checks before pushing

```bash
# No leftover conflict markers
grep -rn '<<<<<<< \|=======$\|>>>>>>>' plugins/commits/ AGENTS.md || echo "Clean"

# Plugin version is sane
jq .version plugins/commits/.claude-plugin/plugin.json

# Marketplace.json still references commits plugin correctly
jq '.plugins[] | select(.name=="commits")' .claude-plugin/marketplace.json

# Removed file is actually removed in tree
ls plugins/commits/commands/commit-push.md 2>&1 | grep -q "No such" && echo "commit-push.md correctly removed"

# New skills are on disk
ls plugins/commits/changelog-generator/SKILL.md plugins/commits/commit-message-linter/SKILL.md
```

### 6. Push and PR

```bash
git push -u origin feat/commits-skills-expansion

gh pr create --title "feat(commits): expand commits plugin with changelog and linter skills (BREAKING)" --body "..."
```

PR body should call out:
- **BREAKING**: `/commits:commit-push` removed; use `/commits:commit --push` instead (verify the actual flag name in the new `commit.md`)
- New skills: `changelog-generator`, `commit-message-linter`
- Plugin version bump: `1.1.1` → `3.0.0`
- Provenance: cherry-picked from `fix/version-manager-scripts@2f87839`

## After E1 lands

1. **Delete the source branch** (fully extracted now):
   ```bash
   git branch -D fix/version-manager-scripts
   git push origin --delete fix/version-manager-scripts  # if it exists on origin
   ```
2. **Update marketplace version** in `.claude-plugin/marketplace.json` to reflect the major bump in the commits plugin (use `/version-bump` or the new `.claude/skills/version-manager` tooling that landed in PR #11).

## Cleanup tasks unrelated to E1 (low priority)

These were flagged by `bd doctor` but deferred:

- **`.beads/beads.db` (400 KB SQLite)** — leftover from the pre-Dolt backend. `bd doctor --fix` skipped it as "needs review". Once you confirm Dolt has the data you care about, delete it: `rm .beads/beads.db && bd doctor` should then show "Classic Artifacts: 0".
- **`beads-sync` worktree** (`.git/beads-worktrees/beads-sync/`) and the `beads-sync` branch (3 months stale): part of the old JSONL-export sync pattern. After confirming `bd dolt push/pull` is your sole sync mechanism:
  ```bash
  git worktree remove .git/beads-worktrees/beads-sync --force
  git branch -d beads-sync
  git push origin --delete beads-sync   # if you don't use it on the remote
  ```
- **bd port/server confusion**: `bd dolt status` reports a port (e.g., 14162) that doesn't always match the actually-running server. Cosmetic — file an upstream bd issue if it gets annoying.

## Session lessons (write these to memory if they keep biting)

1. **Don't use `isolation: "worktree"` on agents that do `git checkout -b` + cherry-pick** in this repo. The E1 agent in the prior session escaped its worktree and started writing to the parent. Until reproduced and root-caused (possibly a `.git` path leak, possibly the agent setting `GIT_DIR` wrong), do history-rewriting work inline.

2. **`bd hooks install --force`** is the entire bd hook migration story. The `.beads/hooks/` directory contains correct templates; `.git/hooks/` had stale ones. `bd doctor --fix` does NOT install hooks — only `bd hooks install --force` does.

3. **`bd doctor --fix` requires `--yes` in non-interactive mode** to actually apply fixes (will list them and exit otherwise).

4. **The new bd thin-shim hooks are non-blocking**. They print circuit-breaker warnings but exit 0, so commits succeed even when the Dolt server is having a moment. The old v0.29.0 hooks hard-failed.

5. **Long-lived feature branches in this repo carry stale `AGENTS.md` and `marketplace.json`** that delete sections for plugins added on main while the branch was open. Always `--ours` those two files when cherry-picking from a branch >30 days old; hand-port any genuinely new content.
