# Beads (bd) Issue Tracking Workflow

This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

## Why bd?

- **Dependency-aware**: Track blockers and relationships between issues
- **Git-friendly**: Auto-syncs to JSONL for version control
- **Agent-optimized**: JSON output, ready work detection, discovered-from links
- **Prevents confusion**: Single source of truth for task tracking

## Quick Reference

### Finding Work

```bash
bd ready                    # Show unblocked issues
bd list --status=open       # All open issues
bd show <id>               # Issue details + dependencies
```

### Creating Issues

```bash
bd create "Title" -t task -p 2              # Basic issue
bd create "Title" -p 1 --deps discovered-from:bd-123  # Linked issue
bd create "Subtask" --parent <epic-id>      # Hierarchical subtask
```

### Working on Issues

```bash
bd update bd-42 --status in_progress   # Claim task
bd close bd-42 --reason "Done"         # Complete task
```

## Issue Types

| Type | Use For |
|------|---------|
| `bug` | Something broken |
| `feature` | New functionality |
| `task` | Work items (tests, docs, refactoring) |
| `epic` | Large features with subtasks |
| `chore` | Maintenance (deps, tooling) |

## Priorities

| Priority | Meaning |
|----------|---------|
| `0` (P0) | Critical - security, data loss, broken builds |
| `1` (P1) | High - major features, important bugs |
| `2` (P2) | Medium - default, nice-to-have |
| `3` (P3) | Low - polish, optimization |
| `4` (P4) | Backlog - future ideas |

## Workflow for AI Agents

1. **Start session**: `bd ready` - see available work
2. **Claim task**: `bd update <id> --status in_progress`
3. **Do work**: Implement, test, document
4. **Found new work?**: `bd create "Found bug" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`
6. **Commit together**: Include `.beads/issues.jsonl` with code changes

## Auto-Sync

bd automatically syncs with git:
- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed

## Rules

- ✅ Use bd for ALL task tracking
- ✅ Use `--json` flag for programmatic access
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers

## MCP Server (Optional)

```bash
pip install beads-mcp
```

Add to MCP config:
```json
{
  "beads": {
    "command": "beads-mcp",
    "args": []
  }
}
```

## CLI Help

Run `bd <command> --help` for all available flags.
