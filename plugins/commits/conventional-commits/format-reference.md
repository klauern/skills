# Conventional Commits Reference Guide

## Format Structure

All commits must follow this pattern:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

### Required Types

- **`fix`**: Patches a bug in the codebase (correlates with PATCH in SemVer)
- **`feat`**: Introduces a new feature to the codebase (correlates with MINOR in SemVer)

### Recommended Additional Types

- **`build`**: Changes affecting the build system or external dependencies
- **`chore`**: Routine tasks, maintenance, or tooling changes
- **`ci`**: Changes to CI configuration files and scripts
- **`docs`**: Documentation only changes
- **`style`**: Changes that don't affect code meaning (white-space, formatting, semicolons, etc.)
- **`refactor`**: Code changes that neither fix a bug nor add a feature
- **`perf`**: Performance improvements
- **`test`**: Adding missing tests or correcting existing tests

## Components

### Type (Required)

The type indicates the nature of the change. Must be lowercase (except for BREAKING CHANGE footer).

### Scope (Optional)

A noun describing a section of the codebase, enclosed in parentheses. Examples:
- `feat(parser): add ability to parse arrays`
- `fix(api): correct endpoint response format`
- `docs(readme): update installation instructions`

Common scopes vary by project but might include:
- Component names: `(auth)`, `(user-profile)`, `(dashboard)`
- Areas: `(api)`, `(ui)`, `(database)`, `(cli)`
- Modules: `(parser)`, `(compiler)`, `(router)`

### Description (Required)

A short summary immediately following the type/scope and colon+space:
- Use imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No period (.) at the end
- Limit to 72 characters or less

### Body (Optional)

Detailed explanation beginning one blank line after the description:
- Use imperative, present tense
- Explain the motivation for the change
- Contrast with previous behavior
- Wrap at 72 characters

### Footer(s) (Optional)

Metadata following a blank line after the body:
- Format: `Token: value` or `Token #value`
- Common tokens: `BREAKING CHANGE`, `Refs`, `Fixes`, `Closes`, `Reviewed-by`, `Acked-by`
- Use hyphens for whitespace in tokens (e.g., `Acked-by`)

## Breaking Changes

Breaking changes MUST be indicated using either method:

### Method 1: Exclamation Mark

Append '!' before the colon:
```
feat!: remove support for Node 6
refactor(api)!: change authentication method
```

### Method 2: Footer

Include a `BREAKING CHANGE` footer:
```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

Breaking changes correlate with MAJOR version bumps in SemVer.

## Examples

### Simple Bug Fix

```
fix: correct typo in user validation message
```

### Feature with Scope

```
feat(auth): add OAuth2 authentication support
```

### Fix with Body

```
fix(parser): handle special characters in input

The parser was failing when encountering Unicode characters.
This change adds proper encoding handling to support all
UTF-8 characters in the input stream.
```

### Breaking Change with Exclamation

```
refactor!: drop support for Python 2.7

Python 2.7 reached end of life. This change removes all
compatibility code for Python 2.7.

BREAKING CHANGE: Python 2.7 is no longer supported. Users must upgrade to Python 3.6+
```

### Feature with References

```
feat(api): add rate limiting to API endpoints

Implements token bucket algorithm for rate limiting.

Closes #123
Refs #456
```

### Multiple Related Changes (Separate Commits)

When changes span multiple concerns, create separate commits:

```
feat(ui): add dark mode toggle
```

```
docs: update theme customization guide
```

```
test(ui): add tests for theme switching
```

## Best Practices

1. **One Logical Change Per Commit**: Each commit should represent a single logical change
2. **Atomic Commits**: Commits should be self-contained and not break functionality
3. **Clear Scopes**: Use consistent scope names across the project
4. **Imperative Mood**: Write as if giving commands ("add", "fix", "update")
5. **Descriptive**: The description should clearly explain what changed
6. **Body When Needed**: Use the body to explain "why" not "what" (the diff shows "what")
7. **Breaking Changes**: Always document breaking changes clearly
8. **Multiple Commits Over Mixed Types**: Better to have separate commits than one commit mixing fixes and features

## Common Patterns

### Database Schema Changes

```
feat(db): add user preferences table
refactor(db): normalize user address data
```

### API Changes

```
feat(api): add pagination to user list endpoint
fix(api): correct status code for validation errors
```

### Documentation Updates

```
docs: add API authentication examples
docs(readme): update installation steps for macOS
```

### Dependency Updates

```
build(deps): bump lodash from 4.17.19 to 4.17.21
chore(deps-dev): update eslint to version 8.0.0
```

### CI/CD Changes

```
ci: add automated security scanning
ci(github): update Node version in actions
```

## Rules Summary

- Types are case-insensitive (except `BREAKING CHANGE` in footers must be uppercase)
- Footers use hyphens for whitespace tokens
- `BREAKING-CHANGE` is synonymous with `BREAKING CHANGE` in footers
- The '!' in `type!:` is an alternative to `BREAKING CHANGE` footer
- Scope is optional but recommended for larger projects
- Body and footers are optional but encouraged for complex changes
