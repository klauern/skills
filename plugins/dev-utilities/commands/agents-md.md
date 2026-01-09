---
description: Migrate CLAUDE.md to AGENTS.md with symlinks for cross-agent compatibility
---

You will look at the repository and make appropriate changes to CLAUDE.md and AGENTS.md following: https://agents.md/

Per the docs:

```
4.1. Migration Commands

Here's how to move your existing config to AGENTS.md while keeping backward compatibility:

# Cline
mv .clinerules AGENTS.md && ln -s AGENTS.md .clinerules

# Claude Code
mv CLAUDE.md AGENTS.md && ln -s AGENTS.md CLAUDE.md

# Cursor
mv .cursorrules AGENTS.md && ln -s AGENTS.md .cursorrules

# Gemini CLI
mv GEMINI.md AGENTS.md && ln -s AGENTS.md GEMINI.md

# OpenAI Codex
mv AGENTS.md AGENTS.md && ln -s AGENTS.md AGENTS.md

# GitHub Copilot (replace [name] with your actual filename)
mv .github/instructions/[name].instructions.md AGENTS.md && ln -s ../../AGENTS.md .github/instructions/[name].instructions.md

# Replit
mv .replit.md AGENTS.md && ln -s AGENTS.md .replit.md

# Windsurf
mv .windsurfrules AGENTS.md && ln -s AGENTS.md .windsurfrules

These commands move your existing config to AGENTS.md and create symbolic links back to the old locations. Your tools keep working, but now they're all reading from the same source of truth.
```

Check whether we have a CLAUDE.md file in the repository. If it exists, you will move it to AGENTS.md and create a symbolic link back to CLAUDE.md.  If it's already symlinked, you will not do anything.  If both exist, you will attempt to merge the two, deduplicating any overlapping content.  You will also update any references to CLAUDE.md in the repository to point to AGENTS.md instead.  Then, you will create a symlink from CLAUDE.md to AGENTS.md.
