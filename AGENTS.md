# AGENTS.md

This file provides guidance to AI coding assistants (Claude Code, Cursor, Windsurf, Cline, etc.) when working with code in this repository.

> **Note**: This repository follows the [agents.md specification](https://agents.md/) for cross-agent compatibility. `CLAUDE.md` is a symbolic link to this file for backward compatibility.

## Project Overview

This is a Claude Code plugin marketplace containing four plugins that automate Git and PR workflows:

1. **commits** - Conventional commit message creation following conventionalcommits.org
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
│       └── references/
│           ├── workflows.md
│           ├── examples.md
│           ├── best-practices.md
│           └── format-reference.md
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
│   │   ├── generate-rules.md
│   │   ├── continue.md
│   │   ├── worktree.md
│   │   ├── gh-actions-upgrade.md
│   │   ├── gh-checks.md
│   │   └── git-optimize.md
│   ├── rule-generator/           → Rule generation skill
│   │   ├── SKILL.md
│   │   └── references/
│   ├── gh-actions-upgrader/      → GH Actions upgrade skill
│   │   ├── SKILL.md
│   │   └── references/
│   ├── ci-failure-analyzer/      → CI failure analysis skill
│   │   ├── SKILL.md
│   │   └── references/
│   └── git-optimize/             → Git optimization skill
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
- `plugins/*/. claude-plugin/plugin.json` - Individual plugin metadata

**Development Context**:
- `.cursor/rules/development-workflow.mdc` - Tool preferences (always active)
- `.cursor/rules/project-overview.mdc` - Repository structure (always active)

**Skill References**:
- `plugins/commits/conventional-commits/SKILL.md` - Commit message standards
- `plugins/pull-requests/pr-creator/SKILL.md` - PR creation with template inference
- `plugins/dev-utilities/gh-actions-upgrader/SKILL.md` - GitHub Actions upgrade automation
- `plugins/dev-utilities/rule-generator/SKILL.md` - Rule generation for AI assistants
- `plugins/dev-utilities/ci-failure-analyzer/SKILL.md` - CI failure analysis and debugging
- `plugins/dev-utilities/git-optimize/SKILL.md` - Git repository optimization
- `plugins/capacities/capacities-api/SKILL.md` - Capacities knowledge management API integration

## Versioning

Marketplace uses semantic versioning. When adding features:

1. Update version in `.claude-plugin/marketplace.json`
2. Create conventional commit with `feat(plugin-name):` prefix
3. Tag release if publishing to marketplace

Current version: 2.0.0

## Cross-Agent Compatibility

This repository uses `AGENTS.md` following the [agents.md specification](https://agents.md/) for broader AI assistant support across Claude Code, Cursor, Windsurf, Cline, Roo-Cline, and other coding assistants. The `CLAUDE.md` file is a symbolic link to `AGENTS.md` for backward compatibility.

The `/dev-utilities:agents-md` command can be used to migrate other repositories from `CLAUDE.md` to `AGENTS.md` with automatic symlink creation.
