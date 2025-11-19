# klauern-skills

Custom skills for Claude Code. The plugin is available in the marketplace as **klauern**.

## Overview

This is a Claude Code plugin marketplace repository containing custom skills that extend Claude's capabilities. The repository is organized similarly to the official [Anthropic skills repository](https://github.com/anthropics/skills).

## Installation

### Interactive Installation

```bash
/plugin
```

Select "Browse Plugins" and install plugins from the `klauern-skills` marketplace:
- `commits` - Conventional commit message creation
- `pull-requests` - Intelligent pull request creation
- `dev-utilities` - Development workflow and utilities

### Add Marketplace

Add the marketplace once (GitHub repo or local path):

```bash
# From GitHub repository
/plugin marketplace add klauern/klauern-skills

# Or from local path
/plugin marketplace add /path/to/klauern-skills
```

### Install Plugins

Install all plugins:

```bash
/plugin install commits@klauern-skills
/plugin install pull-requests@klauern-skills
/plugin install dev-utilities@klauern-skills
```

Or install selectively:

```bash
# Just commit tools
/plugin install commits@klauern-skills

# Just PR tools
/plugin install pull-requests@klauern-skills

# Just development utilities
/plugin install dev-utilities@klauern-skills
```

### Verify Installation

```bash
/help
```

You should see the commands listed.

### Local Development

1. Clone this repository:

```bash
git clone https://github.com/klauern/klauern-skills.git
```

1. Add the local marketplace and install plugins:

```bash
/plugin marketplace add /Users/nklauer/dev/klauern-skills
/plugin install commits@klauern-skills
/plugin install pull-requests@klauern-skills
/plugin install dev-utilities@klauern-skills
```

## Available Plugins

### commits

**Plugin**: `commits@klauern-skills`

A skill that helps write conventional commit messages following best practices and the Conventional Commits specification.

**Usage**: Claude will automatically use this skill when you ask for help with commit messages.

**Includes**:
- `/commits:commit` command
- `/commits:commit-push` command

### pull-requests

**Plugin**: `pull-requests@klauern-skills`

An intelligent pull request creation skill that discovers and parses PR templates, analyzes commits to infer context, and prompts only for information that can't be automatically determined.

**Features**:

- Auto-discovers PR templates from common locations
- Analyzes commit history to extract PR title, type, related issues, and breaking changes
- Intelligently fills template fields based on file changes
- Pre-checks template checkboxes (e.g., "Tests added" if test files were modified)
- Minimizes manual input by only prompting for information that can't be inferred
- Creates PRs using GitHub CLI with proper formatting

**Usage**: Claude will automatically use this skill when you ask to create a pull request, or use the `/pr` command.

**Includes**:
- `/pull-requests:pr` command
- `/pull-requests:pr-update` command
- `/pull-requests:pr-comment-review` command
- `/pull-requests:gh-checks` command
- `/pull-requests:merge-conflicts` command

### dev-utilities

**Plugin**: `dev-utilities@klauern-skills`

Development workflow utilities for managing agent configuration standards, work session continuation, and parallel git worktrees.

**Usage**: Use the commands directly when you need workflow automation.

**Includes**:
- `/dev-utilities:agents-md` - Migrate to AGENTS.md standard
- `/dev-utilities:continue` - Resume incomplete work from notebooks
- `/dev-utilities:worktree` - Manage git worktrees for parallel development

## Available Commands

### /commits:commit

**Plugin**: `commits@klauern-skills`

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

### /commits:commit-push

**Plugin**: `commits@klauern-skills`

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

### /pull-requests:merge-conflicts

**Plugin**: `pull-requests@klauern-skills`

Resolve merge conflicts with a concise, prescriptive workflow.

**Usage**:

```bash
/pull-requests:merge-conflicts
```

### /pull-requests:pr

**Plugin**: `pull-requests@klauern-skills`

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

### /pull-requests:pr-update

**Plugin**: `pull-requests@klauern-skills`

Update PR title and description based on actual changes.

**Usage**:

```bash
/pull-requests:pr-update [pr-number]
```

This command will:

- Analyze commits, files, and diff content from the PR
- Look for and use the repository's PR template structure
- Generate an accurate title following conventional commit format
- Create a comprehensive description based on actual changes
- Show a preview and get approval before updating
- Update the PR using GitHub CLI

**Requirements**:

- GitHub CLI (`gh`) must be installed and authenticated
- Current branch associated with a PR or PR number provided
- Permission to edit the PR (author or write access)

### /pull-requests:pr-comment-review

**Plugin**: `pull-requests@klauern-skills`

Review all comments on a pull request and build an actionable task list.

**Usage**:

```bash
/pull-requests:pr-comment-review [pr-number]
```

This command will:

- Fetch both PR conversation comments and inline review comments
- Parse and categorize feedback (blocking, questions, suggestions, nits)
- Group by file/area when applicable
- Build prioritized task list with file paths and line numbers
- Present for user approval before making changes

**Requirements**:

- GitHub CLI (`gh`) must be installed and authenticated
- Valid PR number or current branch with an associated PR

### /pull-requests:gh-checks

**Plugin**: `pull-requests@klauern-skills`

Review GitHub Action check failures and fix issues when possible.

**Usage**:

```bash
/pull-requests:gh-checks
```

This command will:

- Check current branch status and list GitHub Action checks
- Identify failing checks and retrieve failure logs
- Categorize issues (formatting, linting, type errors, tests, dependencies)
- Suggest or apply simple fixes (with approval)
- Provide guidance for complex issues
- Optionally re-run checks after fixes are committed

**Requirements**:

- GitHub CLI (`gh`) must be installed and authenticated
- Current branch with GitHub Actions workflows

### /dev-utilities:agents-md

**Plugin**: `dev-utilities@klauern-skills`

Migrate your repository to the AGENTS.md standard for cross-agent compatibility.

**Usage**:

```bash
/dev-utilities:agents-md
```

This command will:

- Check if CLAUDE.md exists in the repository
- Move CLAUDE.md to AGENTS.md if it exists
- Create a symbolic link from CLAUDE.md to AGENTS.md for backward compatibility
- Merge both files if AGENTS.md already exists, deduplicating content
- Update any references to CLAUDE.md in the repository to point to AGENTS.md

**Benefits**:

- Single source of truth for agent instructions across multiple AI coding assistants
- Backward compatibility with tools still using CLAUDE.md
- Follows the [agents.md specification](https://agents.md/)

### /dev-utilities:continue

**Plugin**: `dev-utilities@klauern-skills`

Resume incomplete work from markdown notebooks and continue failed tasks.

**Usage**:

```bash
/dev-utilities:continue
```

This command will:

- List all .md files in the repository
- Identify working notebooks and plans for future work
- Review the latest status of incomplete items
- Continue working on completing tasks from those notebooks
- Update notebooks with the latest completion status
- Resume work on tasks that failed due to API timeouts or retry errors

**Use cases**:

- Pick up where you left off after a timeout or error
- Continue multi-session projects documented in markdown files
- Track progress on long-running development tasks

### /dev-utilities:worktree

**Plugin**: `dev-utilities@klauern-skills`

Create and manage git worktrees for parallel development work.

**Usage**:

```bash
/dev-utilities:worktree
```

This command will:

- Use the git-worktree-creator sub-agent to manage worktrees
- Create new worktrees for parallel feature development
- Allow working on multiple branches simultaneously without switching contexts
- Keep each branch isolated in its own directory

**Benefits**:

- Work on multiple features or bug fixes in parallel
- No need to stash or commit incomplete work when switching tasks
- Each worktree maintains its own working directory and state
- Ideal for managing concurrent code reviews or experiments

## Repository Structure

```text
klauern-skills/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace configuration
├── commands/                 # Custom slash commands
│   ├── agents-md.md          # AGENTS.md migration command
│   ├── commit.md             # Commit command
│   ├── commit-push.md        # Commit and push command
│   ├── continue.md           # Continue work from notebooks
│   ├── gh-checks.md          # GitHub Actions check review
│   ├── merge-conflicts.md    # Merge conflicts resolution
│   ├── pr.md                 # Pull request command
│   ├── pr-comment-review.md  # Review PR comments
│   ├── pr-update.md          # Update PR title and description
│   └── worktree.md           # Git worktree management
├── conventional-commits/     # Conventional commits skill
│   ├── SKILL.md              # Skill definition
│   └── references/           # Supporting documentation
├── pr-creator/               # Pull request creation skill
│   ├── SKILL.md              # Skill definition
│   └── references/           # Supporting documentation
│       ├── template_patterns.md
│       ├── example_workflows.md
│       └── implementation_guide.md
└── README.md
```

Each skill is self-contained in its own directory with a `SKILL.md` file containing the instructions and metadata that Claude uses. Commands are defined as markdown files in the `commands/` directory.

## Development

### Adding New Skills

1. Create a new directory at the root level:

```bash
mkdir my-new-skill
```

1. Create a `SKILL.md` file in that directory with your skill definition:

```bash
touch my-new-skill/SKILL.md
```

1. Add the skill to `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [{
    "skills": [
      "./my-new-skill"
    ]
  }]
}
```

### Adding New Commands

1. Create a markdown file in the `commands/` directory:

```bash
touch commands/my-command.md
```

1. Define the command behavior in the markdown file with instructions for Claude

1. Test the command:

```bash
/my-command
```

### Marketplace Configuration

Edit `.claude-plugin/marketplace.json` to manage the marketplace:

- `name`: Marketplace identifier
- `version`: Semantic version number
- `owner`: Marketplace owner information
- `plugins`: Array of plugin definitions, each containing a skills array

## Contributing

Feel free to suggest improvements or report issues.
