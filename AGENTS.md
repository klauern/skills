# AGENTS.md

This file provides guidance to AI coding assistants (Claude Code, Cursor, Windsurf, Cline, etc.) when working with code in this repository.

> **Note**: This repository follows the [agents.md specification](https://agents.md/) for cross-agent compatibility. `CLAUDE.md` is a symbolic link to this file for backward compatibility.

## Project Overview

This is a Claude Code plugin marketplace containing four plugins that automate Git and PR workflows:

1. **commits** - Conventional commit creation and splitting following conventionalcommits.org
2. **pull-requests** - Intelligent PR creation with template-based field extraction
3. **dev-utilities** - Development workflow utilities (agents-md migration, worktrees, GH Actions upgrades)
4. **capacities** - Capacities knowledge management API integration

**Marketplace Name**: `klauern-skills` (published as "klauern" on GitHub)

**Installation**:
```bash
/plugin marketplace add klauern/klauern-skills
/plugin install commits@klauern-skills
/plugin install pull-requests@klauern-skills
/plugin install dev-utilities@klauern-skills
/plugin install capacities@klauern-skills
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

**Token Budget Guidelines**:
- **Metadata** (name + description): ~100 tokens - loads at discovery for all skills
- **SKILL.md body**: <500 lines (~5000 tokens) - loads only when skill activates
- **Reference files**: <500 lines each - loads on demand when explicitly needed
- **Progressive disclosure**: Essential instructions in SKILL.md, detailed content in references/

**See [docs/skill-authoring-guidelines.md](docs/skill-authoring-guidelines.md) for comprehensive best practices.**

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

### External Scripts

For complex logic or external dependencies, use scripts in `plugins/<plugin-name>/scripts/`:

```bash
# Standard path resolution pattern (works from source and installed)
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
uv run "$SCRIPT_DIR/my-script.py" [args]
```

**See [docs/script-development.md](docs/script-development.md) for full guidance.**

## Architecture

### Plugin Organization

Each plugin is self-contained in its own directory under `plugins/`:

```
plugins/
├── commits/                      → Conventional commit creation and splitting
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── commands/
│   │   ├── commit.md
│   │   ├── commit-push.md
│   │   └── commit-split.md
│   ├── conventional-commits/     → Skill with docs
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── workflows.md
│   │       ├── examples.md
│   │       ├── best-practices.md
│   │       └── format-reference.md
│   └── commit-splitter/          → Commit splitting skill
│       ├── SKILL.md
│       └── references/
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
│   │   └── SKILL.md
│   └── pr-conflict-resolver/     → Conflict resolution skill
│       ├── SKILL.md
│       └── references/
│
├── dev-utilities/                → Development workflow tools
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── commands/
│   │   ├── agents-md.md
│   │   ├── continue.md
│   │   ├── worktree.md
│   │   ├── gh-actions-upgrade.md
│   │   ├── gh-checks.md
│   │   ├── git-optimize.md
│   │   ├── skill-lint.md
│   │   └── devcontainer-setup.md
│   ├── gh-actions-upgrader/      → GH Actions upgrade skill
│   │   ├── SKILL.md
│   │   └── references/
│   ├── ci-failure-analyzer/      → CI failure analysis skill
│   │   ├── SKILL.md
│   │   └── references/
│   ├── git-optimize/             → Git optimization skill
│   │   ├── SKILL.md
│   │   └── references/
│   ├── dependency-upgrader/      → Dependency upgrade skill
│   │   ├── SKILL.md
│   │   └── references/
│   └── devcontainer-setup/       → DevContainer scaffolding skill
│       ├── SKILL.md
│       └── references/
│
└── capacities/                   → Capacities knowledge management
    ├── .claude-plugin/
    │   └── plugin.json
    ├── commands/
    │   ├── daily-note.md
    │   ├── list-spaces.md
    │   ├── save-weblink.md
    │   ├── search.md
    │   └── space-info.md
    ├── capacities-api/           → Capacities API skill
    │   ├── SKILL.md
    │   └── references/
    ├── session-capture/          → Session capture skill
    │   └── SKILL.md
    └── scripts/
        └── capacities.py

.claude-plugin/
└── marketplace.json              → Plugin registry (points to ./plugins/*)
```

### Key Architectural Patterns

**Plugin Isolation**: Each plugin has its own directory with commands and skills, preventing command duplication across plugins.

**Skill Structure**: Each skill contains a `SKILL.md` file with metadata frontmatter plus optional `references/` directory for supporting documentation.

**Command Structure**: Commands are markdown files with frontmatter defining `allowed-tools` and `description`. Commands contain bash scripts and natural language instructions.

**Four-Plugin Architecture**: The marketplace defines four separate plugins, each with distinct responsibilities. Each plugin has its own isolated commands.

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

**IMPORTANT**: Use **bd (beads)** for ALL issue tracking. No markdown TODOs.

**Essential commands:**
```bash
bd ready                              # Find available work
bd update <id> --status in_progress   # Claim task
bd close <id> --reason "Done"         # Complete task
bd create "Title" -t task -p 2        # Create issue
```

**Rules:**
- ✅ Use bd for ALL task tracking
- ✅ Commit `.beads/issues.jsonl` with code changes
- ✅ Store AI planning docs in `history/` directory
- ❌ No markdown TODOs or external trackers

**Full documentation:** See [docs/beads-workflow.md](docs/beads-workflow.md)

## Key Files

**Plugin Configuration**:
- `.claude-plugin/marketplace.json` - Plugin registry pointing to `./plugins/*`
- `plugins/*/.claude-plugin/plugin.json` - Individual plugin metadata

**Development Context**:
- `.cursor/rules/development-workflow.mdc` - Tool preferences (always active)
- `.cursor/rules/project-overview.mdc` - Repository structure (always active)

**Skill References**:
- `plugins/commits/conventional-commits/SKILL.md` - Commit message standards
- `plugins/commits/commit-splitter/SKILL.md` - Commit splitting into atomic changes
- `plugins/pull-requests/pr-creator/SKILL.md` - PR creation with template inference
- `plugins/pull-requests/pr-conflict-resolver/SKILL.md` - Merge conflict resolution
- `plugins/dev-utilities/gh-actions-upgrader/SKILL.md` - GitHub Actions upgrade automation
- `plugins/dev-utilities/ci-failure-analyzer/SKILL.md` - CI failure analysis and debugging
- `plugins/dev-utilities/git-optimize/SKILL.md` - Git repository optimization
- `plugins/dev-utilities/dependency-upgrader/SKILL.md` - Dependency upgrade automation
- `plugins/dev-utilities/devcontainer-setup/SKILL.md` - DevContainer scaffolding for Claude Code
- `plugins/capacities/capacities-api/SKILL.md` - Capacities knowledge management API integration
- `plugins/capacities/session-capture/SKILL.md` - Session capture for knowledge management

## Versioning

Marketplace uses semantic versioning. When adding features:

1. Update version in `.claude-plugin/marketplace.json`
2. Create conventional commit with `feat(plugin-name):` prefix
3. Tag release if publishing to marketplace

Current version: 2.4.0

## MCP Server Strategy

This repository deliberately has no `.mcp.json` project configuration:

- **context7** and **exa** are globally configured and available in all projects
- **gh CLI** is preferred over GitHub MCP server (per Tool Preferences above)
- **Capacities** has no public MCP server; Python scripts via `uv run` are the correct approach

No project-level MCP servers are needed.

## Claude Code Automation

**Hooks** (`.claude/hooks/`):
- `block-grep-extended.sh` - PreToolUse(Bash): blocks `grep -E` for macOS compatibility
- `validate-commit-format.sh` - PreToolUse: validates conventional commit format before `git commit`
- `version-bump-reminder.sh` - UserPromptSubmit: reminds to run `/version-bump` before commit-push
- `dev-context.sh` - SessionStart: injects plugin/skill counts at session start
- `pr-quality-check.sh` - PostToolUse: validates PR quality after `gh pr create`
- `workflow-lint.sh` - PostToolUse: lints GitHub workflow files after edits
- `auto-validate-skill.sh` - PostToolUse: suggests skill-validator agent when SKILL.md is modified

**Subagents** (`.claude/agents/`):
- `skill-validator.md` - Validates SKILL.md files against authoring guidelines
- `release-checker.md` - Pre-publish validation across all plugins
- `changelog-detector.md` - Fetches and summarizes changelogs for dependency and GitHub Actions upgrades, detecting breaking changes
- `commit-analyzer.md` - Analyzes git diffs and recommends atomic commit boundaries for splitting large changes
- `pr-preflight-reviewer.md` - Reviews PR diff against description draft, flagging inconsistencies before submission

## Cross-Agent Compatibility

This repository uses `AGENTS.md` following the [agents.md specification](https://agents.md/) for broader AI assistant support across Claude Code, Cursor, Windsurf, Cline, Roo-Cline, and other coding assistants. The `CLAUDE.md` file is a symbolic link to `AGENTS.md` for backward compatibility.

The `/dev-utilities:agents-md` command can be used to migrate other repositories from `CLAUDE.md` to `AGENTS.md` with automatic symlink creation.

<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Dolt-powered version control with native sync
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update <id> --claim --json
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
2. **Claim your task atomically**: `bd update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs via Dolt:

- Each write auto-commits to Dolt history
- Use `bd dolt push`/`bd dolt pull` for remote sync
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

<!-- END BEADS INTEGRATION -->

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
