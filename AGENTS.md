# AGENTS.md

This file provides guidance to AI coding assistants (Claude Code, Cursor, Windsurf, Cline, etc.) when working with code in this repository.

> **Note**: This repository follows the [agents.md specification](https://agents.md/) for cross-agent compatibility. `CLAUDE.md` is a symbolic link to this file for backward compatibility.

## Project Overview

This is a Claude Code plugin marketplace. The authoritative plugin list lives in
`.claude-plugin/marketplace.json` — currently six plugins:

1. **commits** - Conventional commit creation and splitting following conventionalcommits.org
2. **pull-requests** - PR creation, updating, review-comment triage, and merge conflict resolution
3. **dev-utilities** - Development workflow utilities (agents-md migration, worktrees, GH Actions upgrades, CI analysis, git optimization, devcontainers)
4. **capacities** - Capacities knowledge management API integration
5. **ticktick** - TickTick task management via MCP (capture, review, enrich)
6. **agent-patterns** - Agent architecture patterns (Code Mode MCP)

**Marketplace Name**: `klauern-skills` (published as "klauern" on GitHub)

**Installation**:
```bash
/plugin marketplace add klauern/klauern-skills
/plugin install <plugin-name>@klauern-skills   # e.g. commits, pull-requests, ticktick
```

## Repository Layout

```
.claude-plugin/marketplace.json    # Plugin registry (source of truth for plugins + version)
plugins/<plugin>/
├── .claude-plugin/plugin.json     # Plugin metadata + version
├── commands/*.md                  # Slash commands (thin wrappers that invoke skills)
├── skills/<skill>/SKILL.md        # Skills (MUST live under skills/ for discovery)
│   └── references/*.md            # On-demand documentation
└── scripts/*.py                   # External scripts (invoked via ${CLAUDE_PLUGIN_ROOT})
.claude/                           # Repo-local tooling (agents, hooks, version-manager)
docs/                              # Authoring guidelines, script development, beads workflow
history/                           # AI planning docs and session artifacts
```

## Development Commands

### Adding New Skills

1. Create `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: What it does + when to use it (trigger phrases)
   ---
   ```
   The `skills/` directory is required — Claude Code only discovers plugin skills there.
2. Add on-demand documentation in `skills/<skill-name>/references/`.

**Token Budget Guidelines**:
- **Metadata** (name + description): ~100 tokens - loads at discovery for all skills
- **SKILL.md body**: <500 lines (~5000 tokens) - loads only when skill activates
- **Reference files**: <500 lines each - loads on demand when explicitly needed
- **Progressive disclosure**: Essential instructions in SKILL.md, detailed content in references/ (plain relative links — never `@references/…`, which loads eagerly)

**See [docs/skill-authoring-guidelines.md](docs/skill-authoring-guidelines.md) for comprehensive best practices.**

### Adding New Commands

1. Create `plugins/<plugin-name>/commands/command-name.md` with frontmatter defining
   `allowed-tools`, `description`, and (if it takes arguments) `argument-hint`.
2. Keep commands thin: usage + arguments + examples + "invoke the X skill". Workflow
   logic belongs in the skill so it isn't forked in two places.
3. Test with `/plugin-name:command-name`.

### External Scripts

For complex logic or external dependencies, use scripts in `plugins/<plugin-name>/scripts/`:

```bash
# CLAUDE_PLUGIN_ROOT is set by Claude Code to the installed plugin's root
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py" [args]
```

Never derive script paths from `$0` (command bash blocks run via `bash -c`, so `$0` is
the shell binary) and never hardcode install locations.

**See [docs/script-development.md](docs/script-development.md) for full guidance.**

## Tool Preferences

From `.cursor/rules/development-workflow.mdc` (always active):

- **GitHub**: Use `gh` CLI (not MCP or direct API calls)
- **File Search**: Use `fd` instead of `find`
- **Package Manager**: Use `bun`/`bunx` instead of npm equivalents
- **Python**: Use `uv run` with inline script dependencies
- **Go**: Use `gofumpt` (not standard `gofmt`)

## Conventions

### Conventional Commits

All commits must follow https://www.conventionalcommits.org/:

```
<type>[optional scope]: <description>
```

**Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
(enforced by the `validate-commit-format.sh` PreToolUse hook).

- Use `/commits:commit` (commit only) or `/commits:commit-push` (commit and push)
- Always use heredoc for multi-line messages

### Git Workflow

- Always create feature branches from `main` for new work; never commit directly to `main`/`master`
- After merging a feature branch, delete it locally and remotely

### PR Workflow

The `pr-creator` skill discovers PR templates, analyzes commits and the full diff,
pre-fills template checkboxes from evidence, and never uses `gh pr create --fill`.
Conflict resolution is handled by the `pr-conflict-resolver` skill via
`/pull-requests:merge-conflicts`.

## Issue Tracking with bd (beads)

**IMPORTANT**: Use **bd (beads)** for ALL issue tracking. No markdown TODOs, no external
trackers, no duplicate tracking systems.

```bash
bd ready --json                       # Find available work
bd update <id> --claim --json         # Claim task atomically
bd create "Title" -t task -p 2 --json # Create issue (types: bug/feature/task/epic/chore; priority 0-4)
bd close <id> --reason "Done" --json  # Complete task
```

- Link discovered work: `bd create "Found bug" -p 1 --deps discovered-from:<parent-id>`
- The tracked export file is `.beads/beads.left.jsonl`
- Store AI planning docs in `history/`

**Full documentation**: [docs/beads-workflow.md](docs/beads-workflow.md)

## Key Files

- `.claude-plugin/marketplace.json` — plugin registry and marketplace version (source of truth)
- `plugins/*/.claude-plugin/plugin.json` — individual plugin metadata
- `plugins/*/skills/*/SKILL.md` — the skills themselves
- `.cursor/rules/*.mdc` — tool preferences and repo overview (always active)
- `docs/skill-authoring-guidelines.md` — authoring standards enforced by skill-validator

## Versioning

Semantic versioning at two levels: each plugin's `plugin.json`, plus the marketplace
`metadata.version` (always >= the highest plugin version). After modifying a plugin:

1. Run `/bump-version <plugin-name>` (backed by the `.claude/skills/version-manager` skill)
2. Commit as `chore(release): bump <plugin-name> to <version>`
3. Tag if publishing

## MCP Server Strategy

- **context7** and **exa** are globally configured and available in all projects
- **gh CLI** is preferred over the GitHub MCP server (per Tool Preferences)
- **ticktick** requires a user-level MCP server registered as exactly `ticktick`
  (`claude mcp add --transport http ticktick https://mcp.ticktick.com/ -s user`);
  `/ticktick:setup` verifies the connection
- **Capacities** has no public MCP server; the plugin's Python script via `uv run` is
  the correct approach

No project-level `.mcp.json` is needed.

## Claude Code Automation

**Hooks** (`.claude/hooks/`, registered in `.claude/settings.json`):
- `validate-commit-format.sh` - PreToolUse(Bash): validates conventional commit format
- `workflow-lint.sh` - PostToolUse(Edit|Write): lints GitHub workflow files
- `auto-validate-skill.sh` - PostToolUse(Edit|Write): suggests skill-validator when SKILL.md changes
- `version-bump-reminder.sh` - UserPromptSubmit: reminds to run `/bump-version` before commit-push
- `dev-context.sh` - SessionStart: injects plugin/skill counts

**Subagents** (`.claude/agents/`):
- `skill-validator` - Validates SKILL.md files against authoring guidelines
- `release-checker` - Pre-publish validation across all plugins
- `changelog-detector` - Fetches and summarizes changelogs for upgrades, detecting breaking changes
- `commit-analyzer` - Recommends atomic commit boundaries for splitting large changes
- `pr-preflight-reviewer` - Reviews PR diff against description draft before submission

## Cross-Agent Compatibility

This repository uses `AGENTS.md` following the [agents.md specification](https://agents.md/);
`CLAUDE.md` is a symlink to it. The `/dev-utilities:agents-md` command migrates other
repositories to this convention.

## Landing the Plane (Session Completion)

**When ending a work session**, complete ALL steps below. Work is NOT complete until `git push` succeeds.

1. **File issues for remaining work** (bd)
2. **Run quality gates** (if code changed) — tests, linters, `/skill-lint`
3. **Update issue status** — close finished work
4. **PUSH TO REMOTE** (mandatory):
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** — clear stashes, prune remote branches
6. **Hand off** — provide context for the next session

- NEVER stop before pushing — that leaves work stranded locally
- NEVER say "ready to push when you are" — YOU must push
- If push fails, resolve and retry until it succeeds
