---
name: conventional-commits
description: Creates conventional commits following conventionalcommits.org. Analyzes git changes and generates properly formatted commit messages with types (feat, fix, docs, etc.) and scopes. Supports single/multi-commit workflows and commit-and-push operations.
version: 1.0.0
author: klauern
---

# Conventional Commits

## Overview

This skill enables creating well-formatted commit messages following the Conventional Commits specification. It analyzes git changes, determines appropriate commit types and scopes, and creates structured commits that support semantic versioning and automated changelog generation.

## Quick Start

### Slash Commands

- **`/commit`**: Create a conventional commit without pushing - see [`../commands/commit.md`](../commands/commit.md)
- **`/commit-push`**: Create a conventional commit and push to remote - see [`../commands/commit-push.md`](../commands/commit-push.md)

### Core Documentation

- **[Workflows](workflows.md)** - Step-by-step workflows for single and multi-commit scenarios
- **[Examples](examples.md)** - Real-world commit examples for different scenarios
- **[Best Practices](best-practices.md)** - Guidelines and common pitfalls to avoid
- **[Format Reference](format-reference.md)** - Complete specification details

## When to Use This Skill

Use this skill when:

- Creating commits that follow Conventional Commits format
- User requests "conventional commits" or "semantic commits"
- Breaking down changes into multiple logical commits with proper scoping
- Committing and pushing changes with structured messages
- Working in repositories that enforce commit message conventions

## Workflow Overview

### Decision Process

1. **Staging status** → Staged changes use single commit workflow; unstaged changes use multi-commit workflow
2. **Push requirement** → Push after committing if user mentions "push"

### Single vs Multi-Commit

- **Single commit**: Changes already staged for one logical commit
- **Multi-commit**: Unstaged changes that need to be broken into atomic commits

**See [workflows.md](workflows.md) for detailed step-by-step instructions.**

## Sub-Agent Strategy

### Use Haiku 4.5 for

- Quick diff analysis and file categorization
- Simple commit message drafting

### Use Sonnet 4.5 for

- Commit breakpoint determination and multi-commit planning
- Scope identification and complex message composition
- Cross-cutting change analysis

**See [workflows.md](workflows.md) for detailed agent usage examples.**

## Quick Format Reference

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Common types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`

**Breaking changes**: Use `!` after type/scope or `BREAKING CHANGE:` footer

**For complete specification**, see [`format-reference.md`](format-reference.md)

**For practical examples**, see [`examples.md`](examples.md)

**For guidelines and tips**, see [`best-practices.md`](best-practices.md)

## Documentation Index

### Core Guides

- **[workflows.md](workflows.md)** - Detailed workflows for single and multi-commit scenarios
- **[examples.md](examples.md)** - Real-world commit examples
- **[best-practices.md](best-practices.md)** - Guidelines and common pitfalls

### Reference Materials

- **[format-reference.md](format-reference.md)** - Complete Conventional Commits specification

### Command Documentation

- **[commit.md](../commands/commit.md)** - Create commits without pushing
- **[commit-push.md](../commands/commit-push.md)** - Create commits and push to remote
