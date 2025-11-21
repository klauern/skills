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

1. Create directory: `mkdir skill-name`
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
4. Register in `.claude-plugin/marketplace.json` under the appropriate plugin
5. Bump marketplace version in `marketplace.json`

### Adding New Commands

1. Create `commands/command-name.md` with frontmatter:
   ```yaml
   ---
   allowed-tools: Bash
   description: Command description
   ---
   ```
2. Write bash implementation with clear instructions
3. Register in plugin's `commands` array in `.claude-plugin/marketplace.json`
4. Test with `/command-name`

## Architecture

### Plugin Organization

```
commits/          → Conventional commit creation
  ├── SKILL.md
  ├── workflows.md
  ├── examples.md
  ├── best-practices.md
  └── format-reference.md

pr-creator/       → PR creation with template inference
  ├── SKILL.md
  └── references/

gh-actions-upgrader/  → GitHub Actions upgrade automation
  ├── SKILL.md
  └── references/

commands/         → Slash command implementations
  ├── commit.md
  ├── pr.md
  └── gh-actions-upgrade.md

.claude-plugin/
  └── marketplace.json  → Plugin registry (three plugins defined)

.cursor/rules/    → Cursor IDE context rules (MDC format)
```

### Key Architectural Patterns

**Skill Structure**: Each skill contains a `SKILL.md` file with metadata frontmatter plus optional `references/` directory for supporting documentation.

**Command Structure**: Commands are markdown files with frontmatter defining `allowed-tools` and `description`. Commands contain bash scripts and natural language instructions.

**Three-Plugin Architecture**: The marketplace defines three separate plugins, each with distinct responsibilities. Each plugin can have multiple skills and commands.

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

## Key Files

**Plugin Configuration**:
- `.claude-plugin/marketplace.json` - Three plugin definitions, version tracking

**Development Context**:
- `.cursor/rules/development-workflow.mdc` - Tool preferences (always active)
- `.cursor/rules/project-overview.mdc` - Repository structure (always active)
- `.cursor/rules/conventional-commits-skill.mdc` - Active for `conventional-commits/**`
- `.cursor/rules/pr-creator-skill.mdc` - Active for `pr-creator/**`

**Skill References**:
- `conventional-commits/SKILL.md` - Commit message standards and workflows
- `pr-creator/SKILL.md` - PR creation with template inference logic
- `gh-actions-upgrader/SKILL.md` - GitHub Actions upgrade automation

## Versioning

Marketplace uses semantic versioning. When adding features:

1. Update plugin version in `.claude-plugin/marketplace.json`
2. Create conventional commit with `feat(plugin-name):` prefix
3. Tag release if publishing to marketplace

Current version: 1.2.0

## Cross-Agent Compatibility

This repository uses `AGENTS.md` following the [agents.md specification](https://agents.md/) for broader AI assistant support across Claude Code, Cursor, Windsurf, Cline, Roo-Cline, and other coding assistants. The `CLAUDE.md` file is a symbolic link to `AGENTS.md` for backward compatibility.

The `/dev-utilities:agents-md` command can be used to migrate other repositories from `CLAUDE.md` to `AGENTS.md` with automatic symlink creation.
