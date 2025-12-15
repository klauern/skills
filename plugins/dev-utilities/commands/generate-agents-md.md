---
allowed-tools: Glob, Grep, Read, Write, Bash, AskUserQuestion
description: Interactive wizard to generate AGENTS.md, full .cursor/rules/ set, or individual .mdc rule (preferred name)
---

## Instructions

This is the preferred (tool-agnostic) name for the same wizard as `/generate-claude-md`.

1. Read `plugins/dev-utilities/commands/generate-claude-md.md`
2. Follow those instructions exactly

Notes:
- Treat `AGENTS.md` as the primary entrypoint (per agents.md spec).
- Create `CLAUDE.md → AGENTS.md` as a compatibility symlink when relevant.
