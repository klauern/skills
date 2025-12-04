---
name: pr-creator
description: Intelligent pull request creation with template-based field extraction and commit analysis
version: 1.0.0
author: klauern
---

# PR Creator

## Overview

The `pr-creator` skill helps you create comprehensive, well-structured pull requests by:

1. **Discovering PR templates** in your repository (`.github/PULL_REQUEST_TEMPLATE.md`, `PULL_REQUEST.md`, etc.)
2. **Parsing template fields** to identify required and optional information
3. **Analyzing commits** in your current branch to infer context and changes
4. **Intelligent gap-filling** by prompting for missing information that can't be inferred
5. **Generating PR descriptions** that follow your team's conventions

## When to Use This Skill

Use this skill when you need to:

- Create a pull request with proper template adherence
- Ensure all required PR fields are filled out
- Automatically summarize changes from your branch
- Follow team conventions for PR descriptions
- Generate test plans or checklists based on changes

## Quick Start

```bash
User: Create a PR for my changes
# or
User: /pr
```

The skill will:

1. Find your PR template (if it exists)
2. Analyze your branch commits and changes
3. Infer as much information as possible
4. Ask you only for information it can't determine
5. Create the PR using `gh` CLI

## How It Works

### Phase 1: Discovery

Searches for PR templates in common locations:

- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/pull_request_template.md`
- `PULL_REQUEST_TEMPLATE.md`
- `docs/PULL_REQUEST_TEMPLATE.md`
- `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates)

Then parses the template to identify:

- Required fields (marked with `[Required]`, `*`, or `<!-- Required -->`)
- Optional fields
- Checkboxes that can be auto-filled
- Form fields and dropdowns

**See**: [references/template_patterns.md](references/template_patterns.md) for detailed template parsing rules

### Phase 2: Commit Analysis

Analyzes your branch to extract:

- **Title**: From commit messages or branch name
- **Type**: From conventional commit prefixes (`feat:`, `fix:`, etc.)
- **Related issues**: From `#123`, `closes #123`, `fixes #123` patterns
- **Breaking changes**: From `BREAKING CHANGE:` or '!' markers
- **Scope**: From file paths or commit scopes
- **Test changes**: Detected from test file modifications
- **Documentation changes**: Detected from `.md` file changes

**Git Commands Used**:

```bash
git rev-parse --abbrev-ref HEAD  # Current branch
git log origin/main...HEAD --oneline
git diff origin/main...HEAD --stat
git diff origin/main...HEAD --name-status
```

**See**: [references/implementation_guide.md](references/implementation_guide.md#phase-2-commit-analysis) for technical details

### Phase 3: Intelligent Gap Filling

Determines what can be inferred vs. what needs user input:

**High Confidence (Auto-fill)**:

- Issue numbers from commits
- Type from conventional commits
- Files changed from git diff
- Tests added (if test files modified)
- Docs updated (if .md files changed)

**Medium Confidence (Confirm with user)**:

- PR title (synthesized from commits)
- Scope (inferred from file paths)
- Checkbox items (based on file changes)

**Low Confidence (Ask user)**:

- "Why" or "Motivation" sections
- Manual testing steps
- Screenshots
- Migration guides for breaking changes

**Prompting Strategy**: Only asks for information that truly can't be inferred, with context about what was detected.

**See**: [references/implementation_guide.md](references/implementation_guide.md#phase-3-intelligent-gap-filling) for gap detection algorithm

### Phase 4: PR Generation

Composes the final PR:

1. Fills template with inferred + user-provided data
2. Adds auto-generated sections (commit list, file changes)
3. Creates PR using `gh pr create`
4. Optionally adds labels, reviewers, and links issues

**Example Output**:

```bash
gh pr create \
  --title "feat: Add user profile API endpoints" \
  --body "$(cat pr_body.md)" \
  --base main \
  --label "enhancement" \
  --assignee "@me"
```

**See**: [references/implementation_guide.md](references/implementation_guide.md#phase-4-pr-generation) for PR creation details

## Model Strategy

This skill uses different Claude models for optimal performance:

### Claude 4.5 Haiku

**Use for**:

- File and template discovery
- Git command execution
- Template parsing
- Simple pattern matching
- Field extraction

### Claude 4.5 Sonnet

**Use for**:

- Commit analysis and intent understanding
- PR title/description generation
- Gap detection and reasoning
- Complex decision-making
- Natural language generation

**See**: [references/implementation_guide.md](references/implementation_guide.md#model-selection-strategy) for detailed guidance

## Examples

### Example 1: Feature with Full Template

User has implemented a new feature with comprehensive template requirements.

**See**: [references/example_workflows.md](references/example_workflows.md#example-1-feature-pr-with-full-template)

### Example 2: Bug Fix with Minimal Template

Quick hotfix with simple template.

**See**: [references/example_workflows.md](references/example_workflows.md#example-2-bug-fix-with-minimal-template)

### Example 3: No Template

Repository has no template - uses sensible defaults.

**See**: [references/example_workflows.md](references/example_workflows.md#example-3-no-template-default-structure)

### Example 4: Multiple Templates

Repository has multiple templates - skill helps select the right one.

**See**: [references/example_workflows.md](references/example_workflows.md#example-4-multiple-templates-user-selects)

## Requirements

- Git repository with a remote
- GitHub CLI (`gh`) installed and authenticated
- At least one commit on current branch (vs. base branch)

**Installation**:

```bash
# Install gh CLI
brew install gh  # macOS
# or: https://cli.github.com/

# Authenticate
gh auth login
```

## Configuration

### Custom Template Locations

If your team uses non-standard locations, the skill will:

1. Ask you to provide the path
2. Remember it for future PRs in this repository

### Default Base Branch

The skill automatically detects your default branch using:

```bash
git symbolic-ref refs/remotes/origin/HEAD
# or
gh repo view --json defaultBranchRef
```

You can override by specifying: `Create PR targeting develop`

### Labels and Reviewers

The skill can auto-apply labels based on PR type:

- `feat:` → `enhancement` label
- `fix:` → `bug` label
- `docs:` → `documentation` label

And request reviewers from `CODEOWNERS` if configured.

## Error Handling

The skill gracefully handles:

- Missing templates (uses default structure)
- No base branch detected (asks user)
- No commits (warns and exits)
- `gh` not installed (provides installation instructions)
- Not authenticated with `gh` (guides auth process)

**See**: [references/implementation_guide.md](references/implementation_guide.md#error-handling) for details

## Best Practices

1. **Use conventional commits**: Makes type/scope inference more accurate
2. **Reference issues in commits**: Enables automatic issue linking
3. **Write descriptive commit messages**: Helps generate better PR titles/descriptions
4. **Update tests and docs**: Skill will detect and auto-check boxes
5. **Keep templates up to date**: Skill is only as good as your template

## Limitations

- Requires `gh` CLI (doesn't support `hub` or direct GitHub API)
- Works with GitHub only (no GitLab/Bitbucket support)
- Needs internet connection for PR creation
- Cannot infer "why" without user input (requires human reasoning)
- Screenshot requirements always need manual upload

## Reference Documentation

- **[Template Patterns](references/template_patterns.md)**: Detailed template parsing rules and patterns
- **[Example Workflows](references/example_workflows.md)**: Complete examples with different scenarios
- **[Implementation Guide](references/implementation_guide.md)**: Technical implementation details and model strategy

## Troubleshooting

### No commits found

- Ensure you're on a branch (not detached HEAD)
- Check commits exist: `git log origin/main...HEAD`

### gh not authenticated

- Run: `gh auth login`
- Verify: `gh auth status`

### Cannot determine base branch

- Set default: `git remote set-head origin main`
- Or specify in request: `Create PR targeting develop`

### Required field missing

- Review template for required markers
- Provide requested information
- Or update template if field shouldn't be required

## Version History

- **1.0.0** (2025-01-19): Initial release
  - Template discovery and parsing
  - Commit analysis and inference
  - Intelligent gap detection
  - PR generation with `gh` CLI
  - Support for multiple templates
  - Auto-fill checkboxes
  - Model-optimized workflow
