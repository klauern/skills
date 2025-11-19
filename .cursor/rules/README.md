# Cursor Rules for Klauern Skills

This directory contains Cursor Rules that enhance the development experience for the klauern-skills repository.

## Rules Overview

### Always Applied Rules

1. **project-overview.mdc**
   - Provides constant context about repository structure
   - Quick navigation links to all major components
   - Understanding of the marketplace architecture

2. **development-workflow.mdc**
   - Enforces your personal tool preferences (gofumpt, aws-sso, jira, etc.)
   - Conventional commits standards
   - CLI tool usage patterns

### Context-Specific Rules

3. **conventional-commits-skill.mdc**
   - **Globs**: `conventional-commits/**`, `commands/commit*.md`
   - Commit format specifications
   - Single vs multi-commit workflows
   - Sub-agent strategy guidance

4. **pr-creator-skill.mdc**
   - **Globs**: `pr-creator/**`, `commands/pr.md`
   - Template discovery patterns
   - Commit analysis workflows
   - Intelligent gap-filling strategies
   - Model optimization (Haiku vs Sonnet)

5. **code-formatting.mdc**
   - **Globs**: `*.go`, `*.py`, `*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.md`
   - Language-specific formatting standards
   - File naming conventions
   - Documentation standards

6. **command-development.mdc**
   - **Globs**: `commands/*.md`, `.claude-plugin/marketplace.json`
   - Slash command creation patterns
   - Command registration process
   - Testing strategies

## How Rules Work

- **Always Applied**: Rules with `alwaysApply: true` are active in every conversation
- **Glob-based**: Rules with `globs` patterns activate when working on matching files
- **MDC Links**: Use `[text](mdc:path)` format to create navigable links to files

## Adding New Rules

1. Create a new `.mdc` file in this directory
2. Add appropriate frontmatter:
   ```yaml
   ---
   alwaysApply: true  # OR
   globs: "pattern1,pattern2"  # OR
   description: "Rule description for manual activation"
   ---
   ```
3. Write the rule content in Markdown
4. Use MDC links for file references: `[file.ext](mdc:path/to/file.ext)`

## Benefits

- **Contextual Awareness**: Always know where you are in the project
- **Consistent Standards**: Automatic enforcement of coding standards
- **Efficient Navigation**: Quick jumps between related files
- **Tool Integration**: Seamless use of your preferred tools
- **Skill-Specific Guidance**: Targeted help when working on specific components

