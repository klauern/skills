---
name: commit-splitter
description: Analyzes large diffs and suggests how to split them into multiple atomic commits with proper conventional commit scopes. Identifies logical boundaries by file, function, and concern to create focused, reviewable commits.
version: 1.0.0
author: klauern
---

# Commit Splitter

## Overview

This skill analyzes large staged changes and intelligently splits them into multiple atomic commits following the Conventional Commits specification. It identifies logical boundaries based on files, functions, and concerns to create focused, reviewable commits.

## Quick Start

### Slash Commands

- **`/commit-split`**: Analyze staged changes and split into atomic commits - see [`../commands/commit-split.md`](../commands/commit-split.md)

### Core Documentation

- **[Splitting Strategies](references/splitting-strategies.md)** - Methods for identifying commit boundaries
- **[Examples](references/examples.md)** - Real-world splitting scenarios
- **[Best Practices](references/best-practices.md)** - Guidelines for atomic commits

## When to Use This Skill

Use this skill when:

- You have large staged changes that should be split into smaller commits
- Changes affect multiple concerns that should be committed separately
- Refactoring and feature work are mixed together
- You want to create a more reviewable commit history
- User mentions "split commits", "break up changes", or "atomic commits"

## Workflow Overview

### Analysis Process

1. **Parse diff** → Analyze all staged changes using `git diff --staged`
2. **Identify groups** → Group changes by:
   - File type and purpose (tests, docs, implementation)
   - Logical concern (feature, refactor, fix)
   - Scope (component, module, function)
3. **Suggest boundaries** → Propose logical commit boundaries
4. **Create commits** → Either guide user or apply splits automatically

### Splitting Criteria

Changes are grouped by:

- **File-based**: Different files with independent purposes
- **Concern-based**: Features vs refactors vs fixes
- **Scope-based**: Different components or modules
- **Dependency-based**: Changes that depend on each other stay together

**See [splitting-strategies.md](references/splitting-strategies.md) for detailed criteria.**

## Sub-Agent Strategy

### Use Haiku 4.5 for

- Parsing git diff output
- File categorization by extension/path
- Simple grouping by file patterns

### Use Sonnet 4.5 for

- Identifying logical boundaries across files
- Determining commit dependencies
- Crafting conventional commit messages for each split
- Complex refactor vs feature separation

## Output Format

For each suggested commit, provide:

```text
Commit #1: feat(auth): add login validation
Files:
  - src/auth/validator.ts (new function)
  - src/auth/types.ts (new type)

Commit #2: test(auth): add validator tests
Files:
  - tests/auth/validator.test.ts (new tests)

Commit #3: docs(auth): document login validation
Files:
  - docs/auth.md (updated)
```

## Interactive Mode

When running interactively:

1. Show suggested splits with rationale
2. Ask user to confirm or modify
3. Guide through creating each commit:
   - Stage specific files/hunks
   - Show proposed commit message
   - Create commit
   - Proceed to next split

## Automatic Mode

When user approves, automatically:

1. Stage files for first commit
2. Create commit with generated message
3. Repeat for remaining splits
4. Show summary of created commits

## Best Practices

- Keep related changes together (don't over-split)
- Separate tests from implementation
- Separate docs from code changes
- Keep refactors separate from new features
- Maintain commit dependencies (don't break builds)

**For detailed guidelines**, see [`references/best-practices.md`](references/best-practices.md)

**For splitting strategies**, see [`references/splitting-strategies.md`](references/splitting-strategies.md)

**For practical examples**, see [`references/examples.md`](references/examples.md)

## Documentation Index

### Core Guides

- **[splitting-strategies.md](references/splitting-strategies.md)** - Detailed splitting methodologies
- **[examples.md](references/examples.md)** - Real-world splitting scenarios
- **[best-practices.md](references/best-practices.md)** - Guidelines for atomic commits

### Command Documentation

- **[commit-split.md](../commands/commit-split.md)** - Split large changes into atomic commits
