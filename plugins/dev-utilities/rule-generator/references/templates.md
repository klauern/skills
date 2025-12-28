# Rule Generation Templates

## AGENTS.md Template

```markdown
# AGENTS.md

## What This Is

[One sentence: what is this project?]

**Tech Stack**: [key languages, frameworks, tools]
**Architecture**: [monorepo/single app/microservices]

## Why It Exists

[2-3 sentences: purpose and key architectural decisions]

## How to Work With It

### Prerequisites
[Installation commands, if non-trivial]

### Running Locally
[Dev server commands]

### Testing
[Test commands]

### Building
[Build commands]

### Key Conventions
- [Tool preferences: bun vs npm, uv vs pip]
- [Critical patterns: file:line references]

### Deep Dives
- [Topic]: docs/[file].md
```

**Target**: 30-60 lines | **Symlink**: `ln -s AGENTS.md CLAUDE.md`

---

## AGENTS.md Example

```markdown
# AGENTS.md

## What This Is

E-commerce platform with web, admin, and mobile apps.

**Tech Stack**: TypeScript, Next.js 14, React Native, tRPC, Prisma, PostgreSQL
**Architecture**: Monorepo with 3 apps and 4 shared packages

## Why It Exists

Unified e-commerce for small businesses. Monorepo shares auth, types, and API client.

## How to Work With It

### Prerequisites
- Node.js 20+, PostgreSQL 15+
- Install: `bun install`

### Running Locally
- All: `bun dev` | Web: `bun dev:web` | Mobile: `bun dev:mobile`

### Testing
- Unit: `bun test` | E2E: `bun test:e2e`

### Building
`bun build`

### Key Conventions
- Use bun, not npm
- tRPC for API calls (see packages/api/src/router/products.ts:25)
- Prefer server components

### Deep Dives
- Database: docs/database.md
- Auth: docs/auth.md
- Deployment: docs/deployment.md
```

**Lines**: ~35

---

## .cursor/rules/ Setup

### core.mdc (alwaysApply)
```markdown
---
alwaysApply: true
---
# Project Core

**Entry**: [main.py](mdc:src/main.py) | **Apps**: web, api, mobile

## Commands
- Run: `bun dev` | Test: `bun test` | Build: `bun build`

## Tools
Use `bun` not npm. Use `fd` not find.
```
**Target**: <30 lines

### [language].mdc (globs)
```markdown
---
globs: *.py,*.pyi
---
# Python Conventions

## Style
- Format: `ruff format` | Lint: `ruff check` | Types: `mypy src/`

## Patterns
Type hints required (see [api.py](mdc:src/api.py:10))
```
**Target**: 15-25 lines

### [task].mdc (description)
```markdown
---
description: Testing patterns and integration test setup
---
# Testing Guide

## Organization
- Unit: `*.test.ts` colocated | Integration: `tests/integration/`

## Commands
- All: `bun test` | Coverage: `bun test --coverage`

## Patterns
See [factories.py](mdc:tests/factories.py) for test data
```
**Target**: 30-50+ lines (on-demand loading)

---

## Frontmatter Decision

```
Is it relevant to EVERY task?
  YES → Is it <30 lines? → alwaysApply: true
  NO → File-type specific? → globs: "*.ext"
       Task-specific? → description: "..."
       Neither? → Probably docs/, not rules
```

**Budget**: alwaysApply total <50 lines | globs 15-25 lines each | All files <200 lines total
