# klauern-skills

Custom skills for Claude Code.

## Overview

This is a Claude Code plugin marketplace repository containing custom skills that extend Claude's capabilities. The repository is organized similarly to the official [Anthropic skills repository](https://github.com/anthropics/skills).

## Installation

### Interactive Installation

```bash
/plugin
```

Select “Browse Plugins” and install the `klauern-skills` plugin from the `klauern-skills` marketplace.

### Add Marketplace

Add the marketplace once (GitHub repo or local path):

```bash
# From GitHub repository
/plugin marketplace add klauern/skills

# Or from local path
/plugin marketplace add /path/to/klauern-skills
```

### Install Plugin (brings all skills and commands)

```bash
/plugin install klauern-skills@klauern-skills
```

### Verify Installation

```bash
/help
```

You should see the commands listed.

### Local Development

1. Clone this repository:

```bash
git clone https://github.com/klauern/skills.git
```

1. Add the local marketplace and install the plugin:

```bash
/plugin marketplace add /Users/nklauer/dev/klauern-skills
/plugin install klauern-skills@klauern-skills
```

## Available Skills

### claude-md-generator

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

**Usage**: Use the `/generate-claude-md` command to launch the interactive wizard.

### conventional-commits

A skill that helps write conventional commit messages following best practices and the Conventional Commits specification.

**Usage**: Claude will automatically use this skill when you ask for help with commit messages.

### pr-creator

An intelligent pull request creation skill that discovers and parses PR templates, analyzes commits to infer context, and prompts only for information that can't be automatically determined.

**Features**:

- Auto-discovers PR templates from common locations
- Analyzes commit history to extract PR title, type, related issues, and breaking changes
- Intelligently fills template fields based on file changes
- Pre-checks template checkboxes (e.g., "Tests added" if test files were modified)
- Minimizes manual input by only prompting for information that can't be inferred
- Creates PRs using GitHub CLI with proper formatting

**Usage**: Claude will automatically use this skill when you ask to create a pull request, or use the `/pr` command.

## Available Commands

### /generate-claude-md

Generate a high-quality AGENTS.md file for your project using an interactive wizard.

**Usage**:

```bash
/generate-claude-md
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

### /commit

Create a well-formatted commit using the Conventional Commits specification.

**Usage**:

```bash
/commit
```

This command will:

- Analyze your staged and unstaged changes
- Review recent commit history for style consistency
- Create a properly formatted conventional commit message
- Commit the changes (does not push to remote)

### /commit-push

Create a well-formatted commit and push it to the remote repository.

**Usage**:

```bash
/commit-push
```

This command will:

- Analyze your staged and unstaged changes
- Review recent commit history for style consistency
- Create a properly formatted conventional commit message
- Commit the changes
- Push to the remote repository

### /merge-conflicts

Resolve merge conflicts with a concise, prescriptive workflow.

**Usage**:

```bash
/merge-conflicts
```

### /pr

Create an intelligent pull request with automatic template filling.

**Usage**:

```bash
/pr
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
/pr

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

## Repository Structure

```text
klauern-skills/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace configuration
├── commands/                 # Custom slash commands
│   ├── commit.md             # Commit command
│   ├── commit-push.md        # Commit and push command
│   ├── generate-claude-md.md # CLAUDE.md generator command
│   ├── merge-conflicts.md    # Merge conflicts resolution
│   └── pr.md                 # Pull request command
├── claude-md-generator/      # CLAUDE.md generator skill
│   ├── SKILL.md              # Skill definition
│   ├── guidelines.md         # Best practices and anti-patterns
│   ├── template.md           # Templates and examples
│   └── progressive-disclosure.md  # Progressive disclosure patterns
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
