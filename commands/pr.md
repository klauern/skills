---
allowed-tools: Bash
description: Create Pull Request following PULL_REQUEST_TEMPLATE.md
---

Create a well-structured pull request using the pr-creator skill. This command discovers your PR template, analyzes your commits, and intelligently fills in the PR description.

## Instructions

Use the `pr-creator` skill to create a pull request. The skill will:

1. **Discover PR Template**: Search for `.github/PULL_REQUEST_TEMPLATE.md` or other common template locations
2. **Parse Template Fields**: Identify required and optional fields
3. **Analyze Branch Changes**: Run git commands to understand your commits and file changes
4. **Extract Information**: Automatically infer PR title, type, related issues, breaking changes, etc.
5. **Intelligent Gap Filling**: Only prompt for information that can't be inferred from commits
6. **Create PR**: Use `gh pr create` to submit the pull request

## What Gets Auto-Detected

The skill automatically infers:
- **PR Title**: From commit messages or branch name
- **Type of Change**: From conventional commit prefixes (`feat:`, `fix:`, `docs:`, etc.)
- **Related Issues**: From commit messages containing `#123`, `closes #123`, `fixes #123`
- **Breaking Changes**: From `BREAKING CHANGE:` or '!' in commits
- **Tests Added**: If test files were modified
- **Documentation Updated**: If `.md` files were changed
- **Files Changed**: Complete list with add/modify/delete status

## What You Might Be Asked

You'll only be prompted for information that can't be inferred:
- **Why** the change was made (business justification)
- **Manual testing steps** not covered by automated tests
- **Screenshots** or visual demonstrations
- **Migration guides** for breaking changes

## Usage Examples

### Simple Usage
```
User: /pr
```

### With Custom Base Branch
```
User: /pr targeting develop
```

### With Additional Context
```
User: /pr
<!-- Skill will analyze and ask for gaps -->

User: This change enables mobile app support
```

## Requirements

- Git repository with remote
- GitHub CLI (`gh`) installed and authenticated
  - Install: `brew install gh` or https://cli.github.com/
  - Auth: `gh auth login`
- At least one commit on current branch

## Reference

For detailed information about how the pr-creator skill works, see:
- `pr-creator/SKILL.md` - Complete skill documentation
- `pr-creator/references/template_patterns.md` - Template parsing details
- `pr-creator/references/example_workflows.md` - Example scenarios
- `pr-creator/references/implementation_guide.md` - Technical implementation

## Notes

- The skill uses `gh pr create`, so ensure you're authenticated
- If no template is found, a sensible default structure is used
- Multiple templates are supported - you'll be asked to select one
- Labels and reviewers can be auto-applied based on change type
- All git operations are read-only until the final PR creation
