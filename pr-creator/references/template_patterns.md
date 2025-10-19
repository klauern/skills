# PR Template Patterns and Field Detection

This document describes how the pr-creator skill identifies and parses PR template fields.

## Common Template Locations

The skill searches for PR templates in these locations (in order):

1. `.github/PULL_REQUEST_TEMPLATE.md`
2. `.github/pull_request_template.md`
3. `PULL_REQUEST_TEMPLATE.md`
4. `docs/PULL_REQUEST_TEMPLATE.md`
5. `.github/PULL_REQUEST_TEMPLATE/*.md` (multiple templates)

If multiple templates exist in the `PULL_REQUEST_TEMPLATE/` directory, the skill will:
- List all available templates
- Ask the user to select the appropriate one (e.g., bug_report.md vs feature.md)

## Required Field Patterns

The skill recognizes these patterns as indicating required fields:

### Markdown Headers with Markers

```markdown
## Summary [Required]
## Summary*
## Summary <!-- Required -->
## Description (Required)
```

### Inline Field Markers

```markdown
**Issue**: [Required] #
**Related PR**: <!-- Required --> #

Type of change: [Required]
- [ ] Bug fix
- [ ] New feature
```

### HTML Comment Markers

```markdown
<!-- Required: Provide a summary -->
## Summary

<!-- This field is required -->
**Motivation**:
```

### Checkbox Markers

```markdown
- [ ] [Required] I have tested these changes
- [ ] [Required] Breaking change documentation added
```

## Optional Field Detection

Fields without markers are assumed optional:

```markdown
## Summary [Required]
<!-- This is required -->

## Additional Context
<!-- This is optional since no marker -->

## Screenshots
<!-- Optional -->
```

## Section Identification

The skill identifies sections by markdown headers:

```markdown
## Summary              → "summary" section
## Description          → "description" section
## Type of Change       → "type" section
## Testing              → "testing" section
## Checklist            → "checklist" section
## Related Issues       → "issues" section
## Breaking Changes     → "breaking" section
## Screenshots          → "screenshots" section
```

## Checkbox Detection and Auto-Fill

### Common Checkboxes

The skill recognizes and can auto-fill common checkbox patterns:

```markdown
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Breaking change
- [ ] Requires version bump
- [ ] CI/CD pipeline passes
- [ ] Code review completed
- [ ] Security review (if needed)
```

### Inference Rules

| Checkbox Text | Auto-Check If... |
|---------------|------------------|
| "Tests added" or "Tests updated" | Test files modified (e.g., `*.test.js`, `*_test.go`, `test_*.py`) |
| "Documentation updated" | `.md` files changed or `docs/` directory modified |
| "Breaking change" | Commits contain `BREAKING CHANGE:` or `!` after type |
| "Version bump" | `package.json`, `Cargo.toml`, `pyproject.toml`, etc. modified |
| "CI/CD passes" | Can be checked after PR creation via API |

### Checkbox Formatting

Preserved checkbox states:
```markdown
- [x] Checked item
- [ ] Unchecked item
- [X] Also checked (uppercase X)
```

## Form Field Patterns

GitHub-style form fields:

```markdown
**Issue Number**: #___
**Type**: [Bug Fix | Feature | Refactor]
**Priority**: [Low | Medium | High | Critical]
**Reviewers**: @username
```

The skill extracts:
- Field name (before the colon)
- Field type (from options in brackets)
- Default/placeholder values

## Issue Linking Patterns

Automatically detected patterns in commits or branch names:

```markdown
Closes #123
Fixes #456
Resolves #789
Related to #111
Addresses issue #222

<!-- Branch names -->
feature/123-add-user-api
bugfix/issue-456
fix/#789-memory-leak
```

## Breaking Change Detection

Patterns that indicate breaking changes:

### In Commits
```
feat!: change API response format
fix(api)!: remove deprecated endpoint

BREAKING CHANGE: The API now returns...
```

### In Template
```markdown
## Breaking Changes [Required if applicable]

- [ ] This PR introduces breaking changes
- [ ] Migration guide provided
```

## Custom Template Variables

Some templates use variables:

```markdown
<!-- REPLACE_ME: Jira ticket number -->
Ticket: REPLACE_ME

<!-- TODO: Add description here -->
## Description
TODO
```

The skill will:
1. Detect these placeholders
2. Prompt user for values
3. Replace them in the final PR body

## Multi-Template Support

For repositories with multiple templates:

```
.github/PULL_REQUEST_TEMPLATE/
├── bug_fix.md
├── feature.md
├── hotfix.md
└── documentation.md
```

The skill will:
1. Detect which template best matches the changes
2. Suggest the template (e.g., "I see you changed only .md files, use documentation.md template?")
3. Allow user to override the suggestion

## Template Examples

### Minimal Template

```markdown
## Summary
Brief description of changes

## Testing
How to verify these changes
```

### Comprehensive Template

```markdown
## Summary [Required]
<!-- Provide a clear, concise summary -->

## Motivation [Required]
<!-- Why are we making this change? -->

## Changes [Required]
<!-- What specifically changed? -->
-
-

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change

## Testing [Required]
### Unit Tests
- [ ] Added
- [ ] Updated

### Manual Testing
<!-- Steps to manually verify -->

## Related Issues
Closes #

## Screenshots
<!-- If applicable -->

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed
- [ ] Commented complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass locally
```

## Default Template

If no template exists, the skill uses this default structure:

```markdown
## Summary
[Auto-generated from commits]

## Changes
[Auto-generated file change summary]

## Type of Change
[Auto-detected: feat/fix/docs/refactor/etc.]

## Related Issues
[Auto-detected from commits]

## Testing
- Unit tests: [Auto-detected]
- Manual testing: [User-provided if needed]
```
