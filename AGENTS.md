# AGENTS.md

This file provides guidance to AI coding assistants (Claude Code, Cursor, Windsurf, Cline, etc.) when working with code in this repository.

> **Note**: This repository follows the [agents.md specification](https://agents.md/) for cross-agent compatibility. `CLAUDE.md` is a symbolic link to this file for backward compatibility.

## Project Overview

This is a Claude Code plugin marketplace containing three plugins that automate Git and PR workflows:

1. **commits** - Conventional commit message creation following conventionalcommits.org
2. **pull-requests** - Intelligent PR creation with template-based field extraction
3. **dev-utilities** - Development workflow utilities (agents-md migration, worktrees, GH Actions upgrades)

**Marketplace Name**: `klauern-skills` (published as "klauern" on GitHub)

**Installation**:
```bash
/plugin marketplace add klauern/klauern-skills
/plugin install commits@klauern-skills
/plugin install pull-requests@klauern-skills
/plugin install dev-utilities@klauern-skills
```

## Development Commands

### Adding New Skills

1. Navigate to the appropriate plugin directory: `plugins/<plugin-name>/`
2. Create `skill-name/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: Brief description
   version: 1.0.0
   author: klauern
   ---
   ```
3. Add references documentation in `skill-name/references/`

### Adding New Commands

1. Create `plugins/<plugin-name>/commands/command-name.md` with frontmatter:
   ```yaml
   ---
   allowed-tools: Bash
   description: Command description
   ---
   ```
2. Write bash implementation with clear instructions
3. Test with `/plugin-name:command-name`

## Architecture

### Plugin Organization

Each plugin is self-contained in its own directory under `plugins/`:

```
plugins/
├── commits/                      → Conventional commit creation
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── commands/
│   │   ├── commit.md
│   │   └── commit-push.md
│   └── conventional-commits/     → Skill with docs
│       ├── SKILL.md
│       ├── workflows.md
│       ├── examples.md
│       ├── best-practices.md
│       └── format-reference.md
│
├── pull-requests/                → PR creation and management
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── commands/
│   │   ├── pr.md
│   │   ├── pr-update.md
│   │   ├── pr-comment-review.md
│   │   └── merge-conflicts.md
│   ├── pr-creator/               → PR creation skill
│   │   ├── SKILL.md
│   │   └── references/
│   └── pr-conflict-resolver/     → Conflict resolution skill
│       ├── SKILL.md
│       └── references/
│
└── dev-utilities/                → Development workflow tools
    ├── .claude-plugin/
    │   └── plugin.json
    ├── commands/
    │   ├── agents-md.md
    │   ├── generate-rules.md
    │   ├── continue.md
    │   ├── worktree.md
    │   ├── gh-actions-upgrade.md
    │   ├── gh-checks.md
    │   └── git-optimize.md
    ├── claude-md-generator/      → CLAUDE.md generation skill
    ├── gh-actions-upgrader/      → GH Actions upgrade skill
    ├── ci-failure-analyzer/      → CI failure analysis skill
    └── git-optimize/             → Git optimization skill

.claude-plugin/
└── marketplace.json              → Plugin registry (points to ./plugins/*)
```

### Key Architectural Patterns

**Plugin Isolation**: Each plugin has its own directory with commands and skills, preventing command duplication across plugins.

**Skill Structure**: Each skill contains a `SKILL.md` file with metadata frontmatter plus optional `references/` directory for supporting documentation.

**Command Structure**: Commands are markdown files with frontmatter defining `allowed-tools` and `description`. Commands contain bash scripts and natural language instructions.

**Three-Plugin Architecture**: The marketplace defines three separate plugins, each with distinct responsibilities. Each plugin has its own isolated commands.

**Model Strategy**: Skills explicitly define when to use Haiku vs Sonnet:
- **Haiku 4.5**: Fast operations (file I/O, pattern matching, parsing, git commands)
- **Sonnet 4.5**: Complex reasoning (analysis, generation, decision-making, natural language synthesis)

## Tool Preferences

From `.cursor/rules/development-workflow.mdc` (always active):

**Required**:
- **GitHub**: Use `gh` CLI (not MCP or direct API calls)
- **File Search**: Use `fd` instead of `find`
- **Package Manager**: Use `bun`/`bunx` instead of npm equivalents
- **Python**: Use `uv run` with inline script dependencies
- **Go**: Use `gofumpt` (not standard `gofmt`)

**Context-Specific**:
- **AWS**: Use `aws-sso` for authentication (Zendesk internal)
- **JIRA**: CLI available, project prefixes: FSEC, SECURE

## Conventions

### Conventional Commits

All commits must follow https://www.conventionalcommits.org/:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore

**Creating Commits**:
- Use `/commits:commit` for commit without push
- Use `/commits:commit-push` for commit and push
- Always use heredoc for multi-line messages:
  ```bash
  git commit -m "$(cat <<'EOF'
  feat(scope): add new feature

  Detailed explanation here.
  EOF
  )"
  ```

### Git Workflow

**Branch Management**:
- Always create feature branches from `main` for new work
- Never commit directly to `main` or `master`
- After merging a feature branch to `main`, **always delete the branch** both locally and remotely:
  ```bash
  git branch -d feature-branch-name
  git push origin --delete feature-branch-name
  ```

### PR Creation Workflow

The `pr-creator` skill intelligently infers PR metadata:

1. Auto-discovers PR templates from `.github/`, `.github/PULL_REQUEST_TEMPLATE/`, `docs/`
2. Analyzes commit history to extract PR title, type, related issues
3. Pre-checks template checkboxes based on file changes
4. Minimizes manual input by inferring what it can

**Template Detection**: Uses multiple methods (`fd`, `find`, direct checks) to ensure reliability across environments.

### GitHub Actions Upgrades

The `gh-actions-upgrader` skill:

1. Detects action versions and fork status using `gh api`
2. Identifies breaking changes and parameter updates
3. Migrates forked actions to upstream equivalents
4. Creates comprehensive upgrade PRs with migration notes

**Fork Detection**: Uses GitHub API to check if actions are forks and recommends upstream migrations.

## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**
```bash
bd ready --json
```

**Create new issues:**
```bash
bd create "Issue title" -t bug|feature|task -p 0-4 --json
bd create "Issue title" -p 1 --deps discovered-from:bd-123 --json
bd create "Subtask" --parent <epic-id> --json  # Hierarchical subtask (gets ID like epic-id.1)
```

**Claim and update:**
```bash
bd update bd-42 --status in_progress --json
bd update bd-42 --priority 1 --json
```

**Complete work:**
```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`
6. **Commit together**: Always commit the `.beads/issues.jsonl` file together with the code changes so issue state stays in sync with code state

### Auto-Sync

bd automatically syncs with git:
- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### GitHub Copilot Integration

If using GitHub Copilot, also create `.github/copilot-instructions.md` for automatic instruction loading.
Run `bd onboard` to get the content, or see step 2 of the onboard instructions.

### MCP Server (Recommended)

If using Claude or MCP-compatible clients, install the beads MCP server:

```bash
pip install beads-mcp
```

Add to MCP config (e.g., `~/.config/claude/config.json`):
```json
{
  "beads": {
    "command": "beads-mcp",
    "args": []
  }
}
```

Then use `mcp__beads__*` functions instead of CLI commands.

### Managing AI-Generated Planning Documents

AI assistants often create planning and design documents during development:
- PLAN.md, IMPLEMENTATION.md, ARCHITECTURE.md
- DESIGN.md, CODEBASE_SUMMARY.md, INTEGRATION_PLAN.md
- TESTING_GUIDE.md, TECHNICAL_DESIGN.md, and similar files

**Best Practice: Use a dedicated directory for these ephemeral files**

**Recommended approach:**
- Create a `history/` directory in the project root
- Store ALL AI-generated planning/design docs in `history/`
- Keep the repository root clean and focused on permanent project files
- Only access `history/` when explicitly asked to review past planning

**Example .gitignore entry (optional):**
```
# AI planning documents (ephemeral)
history/
```

**Benefits:**
- ✅ Clean repository root
- ✅ Clear separation between ephemeral and permanent documentation
- ✅ Easy to exclude from version control if desired
- ✅ Preserves planning history for archeological research
- ✅ Reduces noise when browsing the project

### CLI Help

Run `bd <command> --help` to see all available flags for any command.
For example: `bd create --help` shows `--parent`, `--deps`, `--assignee`, etc.

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ✅ Store AI planning docs in `history/` directory
- ✅ Run `bd <cmd> --help` to discover available flags
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems
- ❌ Do NOT clutter repo root with planning documents

For more details, see README.md and QUICKSTART.md.

## Key Files

**Plugin Configuration**:
- `.claude-plugin/marketplace.json` - Plugin registry pointing to `./plugins/*`
- `plugins/*/. claude-plugin/plugin.json` - Individual plugin metadata

**Development Context**:
- `.cursor/rules/development-workflow.mdc` - Tool preferences (always active)
- `.cursor/rules/project-overview.mdc` - Repository structure (always active)

**Skill References**:
- `plugins/commits/conventional-commits/SKILL.md` - Commit message standards
- `plugins/pull-requests/pr-creator/SKILL.md` - PR creation with template inference
- `plugins/dev-utilities/gh-actions-upgrader/SKILL.md` - GitHub Actions upgrade automation

## Versioning

Marketplace uses semantic versioning. When adding features:

1. Update version in `.claude-plugin/marketplace.json`
2. Create conventional commit with `feat(plugin-name):` prefix
3. Tag release if publishing to marketplace

Current version: 2.0.0

## Cross-Agent Compatibility

This repository uses `AGENTS.md` following the [agents.md specification](https://agents.md/) for broader AI assistant support across Claude Code, Cursor, Windsurf, Cline, Roo-Cline, and other coding assistants. The `CLAUDE.md` file is a symbolic link to `AGENTS.md` for backward compatibility.

The `/dev-utilities:agents-md` command can be used to migrate other repositories from `CLAUDE.md` to `AGENTS.md` with automatic symlink creation.
