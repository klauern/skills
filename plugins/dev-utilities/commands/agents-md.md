---
description: Migrate CLAUDE.md to AGENTS.md with symlinks for cross-agent compatibility
allowed-tools: Bash, Read, Edit, Grep, Glob
---

# /dev-utilities:agents-md

Migrate this repository's assistant config to the [agents.md](https://agents.md/) convention:
`AGENTS.md` is the source of truth, with `CLAUDE.md` symlinked to it for backward compatibility.

## Steps

1. Check the state of `CLAUDE.md` and `AGENTS.md` in the repository root:
   - `CLAUDE.md` is already a symlink to `AGENTS.md` → nothing to do; report and stop.
   - Only `CLAUDE.md` exists → migrate it:
     ```bash
     mv CLAUDE.md AGENTS.md && ln -s AGENTS.md CLAUDE.md
     ```
   - Both exist as regular files → merge their content into `AGENTS.md`, deduplicating
     overlapping sections, then replace `CLAUDE.md` with the symlink.
   - Neither exists → report that there is nothing to migrate.
2. Update any references to `CLAUDE.md` elsewhere in the repository (docs, scripts, CI)
   to point at `AGENTS.md`.
3. Verify: `ls -la CLAUDE.md` shows the symlink, and `git status` shows the rename plus
   the new link.
