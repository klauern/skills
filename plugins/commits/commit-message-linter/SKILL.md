---
name: commit-message-linter
description: Validates commit messages against the Conventional Commits specification. Checks format, types, scopes, and breaking changes, providing actionable suggestions for corrections.
version: 1.0.0
author: klauern
---

# Commit Message Linter

## Overview

This skill validates commit messages against the Conventional Commits specification, identifying format violations, invalid types, scope issues, and breaking change problems. It provides clear, actionable suggestions for corrections.

## Quick Start

### Slash Commands

- **`/commit-lint`**: Validate recent commits or staged message - see [`../commands/commit-lint.md`](../commands/commit-lint.md)
- **`/commit-fix`**: Auto-fix common commit message issues - see [`../commands/commit-fix.md`](../commands/commit-fix.md)

### Core Documentation

- **[Validation Rules](references/validation-rules.md)** - Complete linting rules and checks
- **[Common Errors](references/common-errors.md)** - Frequent violations and fixes
- **[Hook Integration](references/hook-integration.md)** - Pre-commit hook setup

## When to Use This Skill

Use this skill when:

- Reviewing commit messages for compliance
- User asks to "lint commits", "check commit messages", or "validate commits"
- Before merging to ensure clean git history
- Setting up commit message enforcement
- Training team on conventional commits

## Workflow Overview

### Validation Process

1. **Parse message** → Extract type, scope, description, body, footer
2. **Check format** → Validate structure against spec
3. **Validate components** → Check types, scopes, lengths, conventions
4. **Identify violations** → List all issues found
5. **Suggest fixes** → Provide corrected version

### Validation Checks

**Format checks**:
- Header format: `type(scope): description`
- Line length limits
- Body/footer separation
- Overall structure

**Content checks**:
- Valid commit type (feat, fix, etc.)
- Proper scope format
- Description quality
- Breaking change format
- Footer references

**Style checks**:
- Lowercase type
- No period at end of description
- Imperative mood ("add" not "added")
- Scope conventions

**See [validation-rules.md](references/validation-rules.md) for complete rules.**

## Sub-Agent Strategy

### Use Haiku 4.5 for

- Parsing commit message structure
- Checking format compliance
- Validating types and scopes
- Simple error detection

### Use Sonnet 4.5 for

- Suggesting improved descriptions
- Detecting imperative mood violations
- Analyzing complex breaking changes
- Generating comprehensive fix suggestions

## Output Format

### Validation Results

```text
❌ Commit message validation failed

Message:
---
Added user authentication
---

Issues found:

1. [CRITICAL] Missing commit type
   Expected: type(scope): description
   Found: Added user authentication

2. [ERROR] Non-imperative mood
   Expected: "add" (imperative)
   Found: "added" (past tense)

Suggested fix:
---
feat(auth): add user authentication
---
```

### Success Output

```text
✅ Commit message is valid

Message follows Conventional Commits specification:
- Type: feat
- Scope: auth
- Description: add user authentication
- Breaking change: no
```

## Validation Levels

### Critical Violations

**Block the commit** (pre-commit hook should reject):

- Missing or invalid type
- Malformed header structure
- Type not lowercase
- Description missing

### Errors

**Should be fixed**:

- Non-imperative mood
- Description too short (< 3 words)
- Description too long (> 100 chars in header)
- Invalid scope format
- Missing scope when required

### Warnings

**Best practices**:

- Description ends with period
- Body line too long
- Missing body when helpful
- Footer format issues

## Linting Modes

### Mode 1: Single Commit

Validate one commit message:

```bash
# Last commit
git log -1 --pretty=format:"%s%n%n%b"

# Or validate text directly
```

### Mode 2: Multiple Commits

Validate recent commits:

```bash
# Last 10 commits
git log -10 --pretty=format:"%s"
```

### Mode 3: Pre-commit Hook

Validate before commit is created:

```bash
# Read from commit message file
cat .git/COMMIT_EDITMSG
```

### Mode 4: Branch Validation

Validate all commits in branch:

```bash
# All commits since main
git log main..HEAD --pretty=format:"%s%n%n%b"
```

## Auto-Fix Capabilities

The linter can automatically fix:

**Format fixes**:
- Add missing type (infer from changes)
- Lowercase type
- Remove trailing period
- Fix spacing

**Content fixes**:
- Convert to imperative mood
- Add scope (suggest based on files)
- Shorten overly long descriptions
- Format breaking changes properly

**User confirmation required for**:
- Changing commit type
- Adding scope
- Rewriting descriptions
- Adding breaking change markers

## Pre-commit Hook Integration

### Basic Hook

```bash
#!/bin/sh
# .git/hooks/commit-msg

# Read commit message
commit_msg=$(cat "$1")

# Validate using claude code
claude "/commit-lint" <<< "$commit_msg"

# Exit with validation result
exit $?
```

### Enhanced Hook with Auto-fix

```bash
#!/bin/sh
# .git/hooks/commit-msg

# Read and validate
commit_msg=$(cat "$1")
fixed_msg=$(claude "/commit-fix" <<< "$commit_msg")

# Write back if fixed
if [ $? -eq 0 ]; then
  echo "$fixed_msg" > "$1"
fi
```

**See [hook-integration.md](references/hook-integration.md) for complete setup.**

## Best Practices

**For validation**:
- Lint early and often
- Validate before pushing
- Use pre-commit hooks
- Provide clear error messages

**For fixes**:
- Prefer suggestions over auto-fixes
- Preserve user intent
- Explain why changes needed
- Allow user override

**For teams**:
- Document scope conventions
- Share hook configuration
- Create commit templates
- Provide training examples

**For detailed guidelines**, see [`references/common-errors.md`](references/common-errors.md)

## Documentation Index

### Core Guides

- **[validation-rules.md](references/validation-rules.md)** - Complete validation rule set
- **[common-errors.md](references/common-errors.md)** - Frequent violations and fixes
- **[hook-integration.md](references/hook-integration.md)** - Pre-commit hook setup

### Command Documentation

- **[commit-lint.md](../commands/commit-lint.md)** - Validate commit messages
- **[commit-fix.md](../commands/commit-fix.md)** - Auto-fix commit message issues
