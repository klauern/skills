# Cursor Rules Format

## Overview

Cursor uses `.cursor/rules/*.mdc` files with YAML frontmatter for intelligent rule loading.

**Location**: `.cursor/rules/`
**Compatibility**: Claude Code also reads these files

## Frontmatter Types

### alwaysApply: true
- Loads into every conversation
- Keep <30 lines per file, <50 total
- Use for: Project structure, essential commands, tool preferences

### globs: "*.ext,*.ext2"
- Auto-attaches when editing matching files
- Comma-separated, no spaces
- Use for: Language/framework conventions

### description: "..."
- Loads on-demand when relevant to task
- Can be longer (30-50+ lines)
- Use for: Deployment, migrations, testing setup

## Decision Tree

```
Is it relevant to EVERY task?
├─ YES → Is it <30 lines?
│   ├─ YES → alwaysApply: true
│   └─ NO → Too long; use description
│
└─ NO → Is it file-type specific?
    ├─ YES → globs: "*.ext"
    └─ NO → Is it task-specific?
        ├─ YES → description: "..."
        └─ NO → Probably docs/, not rules
```

## File Structure

```
.cursor/rules/
├── core.mdc       # alwaysApply - project overview
├── python.mdc     # globs: *.py - Python conventions
├── typescript.mdc # globs: *.ts,*.tsx - TS conventions
├── react.mdc      # globs: *.tsx,*.jsx - React patterns
├── testing.mdc    # description - test setup
└── deploy.mdc     # description - deployment
```

**Budget**: 5-8 files × 15-25 lines = <200 lines total

## Examples

### core.mdc (alwaysApply)
```markdown
---
alwaysApply: true
---
# Project Core

**Tech**: TypeScript, Next.js 14, PostgreSQL
**Apps**: web, api, mobile

## Commands
- Run: `bun dev` | Test: `bun test` | Build: `bun build`

## Tools
Use `bun` not npm.
```

### python.mdc (globs)
```markdown
---
globs: *.py,*.pyi
---
# Python Conventions

## Style
- Format: `ruff format` | Lint: `ruff check`
- Types: `mypy src/`

## Patterns
Use uv for dependencies. See [api.py](mdc:src/api.py:10) for patterns.
```

### testing.mdc (description)
```markdown
---
description: Testing patterns and integration test setup
---
# Testing Guide

## Organization
- Unit: colocated `*.test.ts`
- Integration: `tests/integration/`
- E2E: `tests/e2e/`

## Commands
- All: `bun test`
- Coverage: `bun test --coverage`

## Integration Setup
```bash
docker-compose up -d  # Start dependencies
bun test:integration
```
```

## File References

```markdown
[filename](mdc:path/to/file)        # Link to file
[config.ts](mdc:config.ts:45)       # Line number
[setup](mdc:src/setup.ts:10-25)     # Line range
```

Paths relative to workspace root.

## vs AGENTS.md

| Aspect | AGENTS.md | .cursor/rules/ |
|--------|-----------|----------------|
| Files | 1 main | 4-8 focused |
| Loading | Always | Intelligent (frontmatter) |
| Best for | Simple projects | Multi-tech stacks |

Both use progressive disclosure for complex topics.

**Recommended**: Use AGENTS.md as cross-tool baseline, .cursor/rules/ for tech-specific guidance.

## Anti-Patterns

- ❌ Style guides in alwaysApply (use linters)
- ❌ Code snippets (use `mdc:` references)
- ❌ >30 lines in alwaysApply files
- ❌ Auto-generated without review
- ❌ globs for universal patterns (use alwaysApply)
