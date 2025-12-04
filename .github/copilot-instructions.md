# GitHub Copilot Instructions for Beads

## Project Overview

**klauern-skills** is a Claude Code plugin marketplace containing three plugins that automate Git and PR workflows. We use bd (beads) for all task tracking in this project.

**Plugins:**
- **commits** - Conventional commit message creation
- **pull-requests** - Intelligent PR creation with template inference
- **dev-utilities** - Development workflow utilities

## Tech Stack

- **Language**: Markdown (plugin configuration), Bash (command scripts)
- **Plugin System**: Claude Code plugins
- **Issue Tracking**: bd (beads) - Git-backed issue tracker
- **CI/CD**: GitHub Actions

## Coding Guidelines

### Plugin Development
- Each plugin lives in `plugins/<plugin-name>/`
- Commands go in `plugins/<plugin-name>/commands/*.md`
- Skills go in `plugins/<plugin-name>/<skill-name>/SKILL.md`
- Always include frontmatter with metadata

### Git Workflow
- Follow conventional commits (use `/commits:commit` or `/commits:commit-push`)
- Always commit `.beads/issues.jsonl` with code changes
- Run `bd sync` at end of work sessions
- Create feature branches, never commit directly to `main`

## Issue Tracking with bd

**CRITICAL**: This project uses **bd** for ALL task tracking. Do NOT create markdown TODO lists.

### Essential Commands

```bash
# Find work
bd ready --json                    # Unblocked issues
bd list --status open --json       # All open issues

# Create and manage
bd create "Title" -t bug|feature|task -p 0-4 --json
bd create "Subtask" --parent <epic-id> --json
bd update <id> --status in_progress --json
bd close <id> --reason "Done" --json

# Sync (CRITICAL at end of session!)
bd sync  # Force immediate export/commit/push
```

### Workflow

1. **Check ready work**: `bd ready --json`
2. **Claim task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** `bd create "Found bug" -p 1 --deps discovered-from:<parent-id> --json`
5. **Complete**: `bd close <id> --reason "Done" --json`
6. **Sync**: `bd sync` (flushes changes to git immediately)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

## Project Structure

```
klauern-skills/
├── plugins/
│   ├── commits/              # Conventional commit creation
│   ├── pull-requests/        # PR management
│   └── dev-utilities/        # Development tools
├── .claude-plugin/
│   └── marketplace.json      # Plugin registry
├── .github/
│   └── copilot-instructions.md  # This file
└── .beads/
    ├── beads.db              # SQLite database (DO NOT COMMIT)
    └── issues.jsonl          # Git-synced issue storage
```

## Key Documentation

- **AGENTS.md** - Comprehensive AI agent guide
- **README.md** - User-facing documentation
- **plugins/*/SKILL.md** - Individual skill documentation

## CLI Help

Run `bd <command> --help` to see all available flags for any command.
For example: `bd create --help` shows `--parent`, `--deps`, `--assignee`, etc.

## Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Run `bd sync` at end of sessions
- ✅ Follow conventional commits
- ✅ Run `bd <cmd> --help` to discover available flags
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT commit `.beads/beads.db` (JSONL only)
- ❌ Do NOT commit directly to `main`

---

**For detailed workflows and advanced features, see [AGENTS.md](../AGENTS.md)**
