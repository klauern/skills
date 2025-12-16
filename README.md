# klauern-skills

Custom skills and commands for Claude Code.

## Overview

This is a Claude Code plugin marketplace repository containing three plugins that automate Git workflows, pull request management, and development utilities. The repository is organized similarly to the official [Anthropic skills repository](https://github.com/anthropics/skills).

**Plugins**:
- **commits** - Conventional commit message creation following conventionalcommits.org
- **pull-requests** - Intelligent PR creation, updates, conflict resolution, and comment review
- **dev-utilities** - Development workflow utilities (AGENTS.md generation, GH Actions upgrades, CI analysis, git optimization, worktrees)

## Installation

### Interactive Installation

```bash
/plugin
```

Select "Browse Plugins" and install the desired plugins from the `klauern-skills` marketplace.

### Add Marketplace

Add the marketplace once (GitHub repo or local path):

```bash
# From GitHub repository
/plugin marketplace add klauern/klauern-skills

# Or from local path
/plugin marketplace add /path/to/klauern-skills
```

### Install Plugins

Install one or more plugins from the marketplace:

```bash
# Install all three plugins
/plugin install commits@klauern-skills
/plugin install pull-requests@klauern-skills
/plugin install dev-utilities@klauern-skills

# Or install selectively
/plugin install commits@klauern-skills
```

### Verify Installation

```bash
/help
```

You should see the commands from installed plugins listed.

### Local Development

1. Clone this repository:

```bash
git clone https://github.com/klauern/klauern-skills.git
```

2. Add the local marketplace and install plugins:

```bash
/plugin marketplace add /Users/nklauer/dev/klauern-skills
/plugin install commits@klauern-skills
/plugin install pull-requests@klauern-skills
/plugin install dev-utilities@klauern-skills
```

## Available Skills

### commits Plugin

#### conventional-commits

A skill that helps write conventional commit messages following best practices and the Conventional Commits specification.

**Usage**: Claude will automatically use this skill when you ask for help with commit messages.

### pull-requests Plugin

#### pr-creator

An intelligent pull request creation skill that discovers and parses PR templates, analyzes commits to infer context, and prompts only for information that can't be automatically determined.

**Features**:

- Auto-discovers PR templates from common locations
- Analyzes commit history to extract PR title, type, related issues, and breaking changes
- Intelligently fills template fields based on file changes
- Pre-checks template checkboxes (e.g., "Tests added" if test files were modified)
- Minimizes manual input by only prompting for information that can't be inferred
- Creates PRs using GitHub CLI with proper formatting

**Usage**: Claude will automatically use this skill when you ask to create a pull request, or use the `/pull-requests:pr` command.

#### pr-conflict-resolver

Intelligently resolves merge conflicts by analyzing both branches, detecting conflict patterns, and suggesting resolution strategies.

**Features**:

- Categorizes conflicts by complexity
- Analyzes intent of changes on both sides
- Auto-resolves simple conflicts (whitespace, imports, formatting) when safe
- Provides context-aware guidance for complex manual resolution
- Maintains code quality during conflict resolution

**Usage**: Claude will use this skill when resolving merge conflicts, or use the `/pull-requests:merge-conflicts` command.

### dev-utilities Plugin

#### claude-md-generator

A skill that generates high-quality AGENTS.md files following the agents.md specification and HumanLayer's best practices. Supports both single-file and multi-file patterns.

**Features**:

- **Two patterns**: Single AGENTS.md (30-60 lines) OR .cursor/rules/ (4-8 files, 10-30 lines each)
- Interactive wizard to choose and configure pattern
- Generates files with WHAT/WHY/HOW structure
- Always creates CLAUDE.md → AGENTS.md symlink for Claude Code compatibility
- Follows agents.md spec (universal format for all AI coding assistants)
- Suggests progressive disclosure patterns for complex topics
- Follows instruction budget best practices (~150-200 total)
- Avoids anti-patterns (style guides, code snippets, task-specific content)
- Domain-specific files for multi-tech stacks (react.md, typescript.md, testing.md, etc.)

**Usage**: Use `/dev-utilities:generate-rules` to launch the interactive wizard.

#### gh-actions-upgrader

Automatically detects, analyzes, and upgrades GitHub Actions in workflows. Identifies forked actions and recommends upstream equivalents, handles major version upgrades with breaking change detection.

**Features**:

- Scans all workflow files to identify action versions
- Uses GitHub API to detect forked actions and recommend upstream alternatives
- Identifies breaking changes in major version upgrades
- Plans upgrade strategies with parameter updates
- Creates comprehensive upgrade PRs with migration notes

**Usage**: Use the `/dev-utilities:gh-actions-upgrade` command.

#### ci-failure-analyzer

Autonomously analyzes GitHub Actions CI failures, parses logs, identifies root causes, and applies fixes for common issues.

**Features**:

- Detects failing checks on PRs and branches
- Parses failure logs to identify root causes
- Categorizes issues into fixable vs. non-fixable
- Applies automated fixes for formatting, linting, test failures, and dependency problems
- Provides comprehensive analysis with actionable recommendations

**Usage**: Use the `/dev-utilities:gh-checks` command when CI checks fail.

#### git-optimize

Comprehensive Git repository optimization including branch cleanup, garbage collection, and repository maintenance.

**Features**:

- Smart merge-aware branch detection and cleanup (git-trim integration)
- Remote maintenance and pruning
- Repository optimization through garbage collection and repacking
- Combined workflows for one-command full optimization

**Usage**: Use the `/dev-utilities:git-optimize` command.

## Available Commands

Commands are organized by plugin. Each command is invoked with the format `/plugin-name:command-name`.

### commits Plugin

#### /commits:commit

Create a well-formatted commit using the Conventional Commits specification.

**Usage**:

```bash
/commits:commit
```

This command will:

- Analyze your staged and unstaged changes
- Review recent commit history for style consistency
- Create a properly formatted conventional commit message
- Commit the changes (does not push to remote)

#### /commits:commit-push

Create a well-formatted commit and push it to the remote repository.

**Usage**:

```bash
/commits:commit-push
```

This command will:

- Analyze your staged and unstaged changes
- Review recent commit history for style consistency
- Create a properly formatted conventional commit message
- Commit the changes
- Push to the remote repository

### pull-requests Plugin

#### /pull-requests:pr

Create an intelligent pull request with automatic template filling.

**Usage**:

```bash
/pull-requests:pr
```

This command will:

- Discover and parse your repository's PR template
- Analyze commit history to infer PR title, type, and related issues
- Detect breaking changes from commit messages
- Pre-fill template checkboxes based on file changes (tests, docs, etc.)
- Only prompt for information that can't be automatically determined
- Create the PR using GitHub CLI (`gh`)
- Return the PR URL

**Requirements**:

- GitHub CLI (`gh`) must be installed and authenticated
- Current branch must have commits not in the base branch

**Example**:

```bash
/pull-requests:pr

# Output:
# I found your PR template and analyzed your branch:
# ✓ Title: feat: Add user authentication
# ✓ Type: New feature
# ✓ Related Issue: Closes #42
# ✓ Tests: Added
#
# Your template requires:
# 1. Why are we making this change?
# > [You provide context]
#
# Created: https://github.com/user/repo/pull/123
```

#### /pull-requests:pr-update

Update an existing PR's title and description based on actual changes.

**Usage**:

```bash
/pull-requests:pr-update [pr-number]
```

If no PR number is provided, uses the PR for the current branch. This command analyzes the actual changes in the PR and updates its metadata to accurately reflect what's being changed.

#### /pull-requests:pr-comment-review

Review all comments on a pull request and build an actionable task list to address feedback.

**Usage**:

```bash
/pull-requests:pr-comment-review [pr-number]
```

If no PR number is provided, determines it from the current branch. This command checks both review comments and issue comments to create a comprehensive action plan.

#### /pull-requests:merge-conflicts

Resolve merge conflicts with intelligent analysis and resolution strategies.

**Usage**:

```bash
/pull-requests:merge-conflicts
```

This command provides a concise, prescriptive workflow for resolving conflicts by analyzing both branches and suggesting appropriate resolution strategies.

### dev-utilities Plugin

#### /dev-utilities:generate-rules

Generate a high-quality AGENTS.md file for your project using an interactive wizard.

**Usage**:

```bash
/dev-utilities:generate-rules
```

This command will:

- Choose between single AGENTS.md or .cursor/rules/ pattern
- Analyze your codebase to detect tech stack and architecture
- Ask key questions about project purpose and conventions
- Generate AGENTS.md (single file, target <60 lines) OR .cursor/rules/ (multi-file)
- Create CLAUDE.md → AGENTS.md symlink for Claude Code compatibility
- Suggest progressive disclosure docs for complex topics
- Provide quality assessment and line count

**Based on**:
- [agents.md specification](https://agents.md/) - Universal format for AI assistants
- [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) - Best practices

#### /dev-utilities:agents-md

Migrate existing CLAUDE.md to AGENTS.md following the agents.md specification, creating a symlink for backward compatibility.

**Usage**:

```bash
/dev-utilities:agents-md
```

This command implements the migration pattern: `mv CLAUDE.md AGENTS.md && ln -s AGENTS.md CLAUDE.md`

#### /dev-utilities:gh-actions-upgrade

Automatically detect, analyze, and upgrade GitHub Actions in your repository's workflows.

**Usage**:

```bash
/dev-utilities:gh-actions-upgrade
```

This command will:

1. Scan all workflow files in `.github/workflows/`
2. Analyze each action to determine current version, fork status, and available upgrades
3. Generate upgrade plans with breaking change summaries and fork-to-upstream migration recommendations
4. Apply upgrades to all workflow files
5. Create a comprehensive PR with upgrade details

#### /dev-utilities:gh-checks

Review and fix GitHub Action check failures on the current branch.

**Usage**:

```bash
/dev-utilities:gh-checks
```

This command will:

1. Check branch and workspace status
2. Fetch and analyze failing GitHub Action checks
3. Parse logs to identify root causes
4. Apply automated fixes when possible
5. Provide guidance for manual resolution

#### /dev-utilities:git-optimize

Optimize Git repository with branch cleanup and garbage collection.

**Usage**:

```bash
/dev-utilities:git-optimize
```

This command helps you optimize your Git repository using configured aliases and git-trim:

- **Quick cleanup** (after PR merge): Use configured `git cleanup` alias
- **Weekly maintenance**: Use `git trim` or `git sweep`
- **Deep optimization** (monthly/quarterly): Use `git optimize`
- **Full workflow**: Use `git trimall`

#### /dev-utilities:worktree

Create and manage git worktrees for parallel development work.

**Usage**:

```bash
/dev-utilities:worktree
```

This command uses the git-worktree-creator agent to set up separate working directories for different branches.

#### /dev-utilities:continue

Resume work from previous sessions by reviewing planning documents and notebooks.

**Usage**:

```bash
/dev-utilities:continue
```

This command lists and reviews .md files to identify working notebooks and plans for future work, then continues completing items from where you left off.

## Repository Structure

```text
klauern-skills/
├── .claude-plugin/
│   └── marketplace.json              # Marketplace configuration pointing to plugins/*
├── plugins/
│   ├── commits/                      # Conventional commit creation plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── commands/
│   │   │   ├── commit.md
│   │   │   └── commit-push.md
│   │   └── conventional-commits/     # Skill
│   │       ├── SKILL.md
│   │       ├── best-practices.md
│   │       ├── examples.md
│   │       ├── format-reference.md
│   │       └── workflows.md
│   │
│   ├── pull-requests/                # PR creation and management plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── commands/
│   │   │   ├── pr.md
│   │   │   ├── pr-update.md
│   │   │   ├── pr-comment-review.md
│   │   │   └── merge-conflicts.md
│   │   ├── pr-creator/               # Skill
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   └── pr-conflict-resolver/     # Skill
│   │       ├── SKILL.md
│   │       └── references/
│   │
│   └── dev-utilities/                # Development workflow utilities plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── commands/
│       │   ├── generate-rules.md
│       │   ├── agents-md.md
│       │   ├── gh-actions-upgrade.md
│       │   ├── gh-checks.md
│       │   ├── git-optimize.md
│       │   ├── worktree.md
│       │   └── continue.md
│       ├── claude-md-generator/      # Skill
│       │   ├── SKILL.md
│       │   ├── guidelines.md
│       │   ├── template.md
│       │   ├── cursor-rules-pattern.md
│       │   └── progressive-disclosure.md
│       ├── gh-actions-upgrader/      # Skill
│       │   ├── SKILL.md
│       │   └── references/
│       ├── ci-failure-analyzer/      # Skill
│       │   ├── SKILL.md
│       │   └── references/
│       └── git-optimize/             # Skill
│           ├── SKILL.md
│           └── references/
│
├── AGENTS.md                         # Project documentation
├── CLAUDE.md -> AGENTS.md            # Symlink for Claude Code compatibility
└── README.md
```

Each plugin is self-contained with its own commands and skills. Skills are defined in directories containing a `SKILL.md` file with instructions and metadata. Commands are markdown files in each plugin's `commands/` directory.

## Development

### Adding New Skills

1. Navigate to the appropriate plugin directory:

```bash
cd plugins/<plugin-name>
```

2. Create a new skill directory with `SKILL.md`:

```bash
mkdir my-new-skill
touch my-new-skill/SKILL.md
```

3. Add skill metadata in the frontmatter:

```yaml
---
name: my-new-skill
description: Brief description
version: 1.0.0
author: klauern
---
```

4. Skills are automatically discovered - no need to register in plugin.json

### Adding New Commands

1. Navigate to the plugin's commands directory:

```bash
cd plugins/<plugin-name>/commands
```

2. Create a markdown file for your command:

```bash
touch my-command.md
```

3. Add command metadata in the frontmatter:

```yaml
---
allowed-tools: Bash, Read, Grep
description: Command description
---
```

4. Define the command behavior in markdown with instructions for Claude

5. Test the command:

```bash
/<plugin-name>:my-command
```

### Creating a New Plugin

1. Create plugin directory structure:

```bash
mkdir -p plugins/my-plugin/.claude-plugin
mkdir -p plugins/my-plugin/commands
```

2. Create `plugins/my-plugin/.claude-plugin/plugin.json`:

```json
{
  "name": "my-plugin",
  "description": "Plugin description",
  "version": "1.0.0",
  "author": {
    "name": "klauern",
    "email": "klauer@gmail.com"
  }
}
```

3. Add plugin to `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "my-plugin",
      "description": "Plugin description",
      "source": "./plugins/my-plugin"
    }
  ]
}
```

### Marketplace Configuration

Edit `.claude-plugin/marketplace.json` to manage the marketplace:

- `name`: Marketplace identifier
- `version`: Semantic version number
- `owner`: Marketplace owner information
- `plugins`: Array of plugin definitions with names, descriptions, and source paths

## Contributing

Feel free to suggest improvements or report issues.
