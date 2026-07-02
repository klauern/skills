---
name: conventional-commits
description: This skill should be used when the user asks to "create a conventional commit", "write semantic commit messages", or "commit and push with conventional commits".
version: 1.0.0
---

# Conventional Commits

## Overview

This skill creates well-formatted commit messages following the Conventional Commits specification. It analyzes git changes, determines commit types and scopes, and creates structured commits supporting semantic versioning and automated changelog generation.

For splitting mixed changes into multiple atomic commits, use the **commit-splitter**
skill — this skill covers writing the messages and committing.

## Quick Format

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

See [format-reference.md](references/format-reference.md) for the full specification —
types, scopes, and breaking-change syntax live there (single source of truth).

## Workflow

1. **Check staging status**: staged changes → commit them as-is; unstaged mixed changes
   that need splitting → delegate to the commit-splitter skill.
2. Review context: `git diff --cached` and `git log -10 --oneline` (match the repo's
   existing style).
3. Determine type, scope, and breaking-change status per the format reference.
4. Commit with heredoc:
   ```bash
   git commit -m "$(cat <<'EOF'
   <type>(scope): description

   Optional body explaining rationale.

   BREAKING CHANGE: if applicable
   EOF
   )"
   ```
5. Push only if the user asked: `git push`

## Key Principles

- **Atomic commits**: One logical change per commit
- **Imperative mood**: "add" not "added", "fix" not "fixed"
- **Concise descriptions**: ≤72 characters, lowercase, no period
- **Meaningful bodies**: Explain "why" not "what" (diff shows "what")
- **Explicit breaking changes**: Always use '!' or `BREAKING CHANGE:` footer

## Progressive Disclosure

- [format-reference.md](references/format-reference.md) — the complete specification
- [best-practices.md](references/best-practices.md) — judgment calls: scope naming, body writing, common pitfalls
- [examples.md](references/examples.md) — breaking-change and multi-commit examples
