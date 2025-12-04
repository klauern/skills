# Cursor Rules Pattern

## Overview

The `.cursor/rules/` pattern breaks project rules into multiple small, focused files that all auto-load. Each file covers a specific domain (framework, language, testing, etc.) and stays under 30 lines.

**Key Difference from CLAUDE.md**:
- **CLAUDE.md**: Single file (30-60 lines) with progressive disclosure
- **`.cursor/rules/`**: Multiple files (10-30 lines each) that all auto-load

## When to Use This Pattern

Use `.cursor/rules/` when:
- You have distinct technology domains (React, TypeScript, Python, etc.)
- Each domain has specific conventions worth documenting
- You want all rules loaded automatically
- You prefer focused, single-topic files

Use `CLAUDE.md` when:
- Simpler project with unified conventions
- Want to minimize auto-loaded content
- Prefer progressive disclosure for deep topics

## Recommended Structure

```
.cursor/rules/
├── core.md          # Project overview, purpose, architecture (20-30 lines)
├── react.md         # React-specific patterns (10-20 lines)
├── typescript.md    # TypeScript conventions (10-20 lines)
├── testing.md       # Testing patterns (15-25 lines)
├── api.md           # API conventions (10-20 lines)
└── build.md         # Build and deployment (10-15 lines)
```

**Claude Code Compatibility**: Claude Code also reads `.cursor/rules/` - no separate `.claude/rules/` needed.

## File Guidelines

### Line Limits

Each file should be:
- **Minimum**: 5-10 lines (if less, merge with another file)
- **Target**: 10-20 lines
- **Maximum**: 30 lines (if more, split into multiple files)

**Total budget**: All files combined should stay under 200 lines to leave room for system prompts.

### Content Focus

Each file should cover **one technology or domain**:

✅ **Good** (focused):
- `react.md` - React patterns only
- `typescript.md` - TypeScript conventions only
- `testing.md` - Testing patterns only

❌ **Bad** (mixed):
- `frontend.md` - React + TypeScript + styling + testing
- `backend.md` - API + database + auth + deployment

## Core File Template

Every `.cursor/rules/` setup should have a `core.md` file:

```markdown
# Project Core

## What This Is

[One sentence: project purpose]

**Tech Stack**: [key languages, frameworks]
**Architecture**: [monorepo/single app/microservices]

## Purpose

[2-3 sentences: why this exists, key decisions]

## Workflow

### Development
- Run: `[command]`
- Test: `[command]`
- Build: `[command]`

### Conventions
- Use [tool] not [alternative]
- [Critical pattern with file:line reference]

### Deep Dives
- [Topic]: docs/[file].md
```

**Lines**: 20-30

## Domain File Templates

### React (`react.md`)

```markdown
# React Patterns

## Component Structure

Prefer server components (see app/components/Button.tsx:1)

Client components only when needed:
- Event handlers
- Browser APIs
- React hooks

## State Management

- Server state: tRPC
- Client state: React Context
- Form state: React Hook Form

## Conventions

- Colocate tests: `ComponentName.test.tsx`
- Props interface: `ComponentNameProps`
- Async components use Suspense boundaries
```

**Lines**: 15-20

### TypeScript (`typescript.md`)

```markdown
# TypeScript Conventions

## Type Definitions

- Shared types: `packages/types/src/`
- Local types: Colocated in same file
- No `any` (use `unknown` if needed)

## Naming

- Interfaces: `PascalCase` suffix with `Interface` or describe purpose
- Types: `PascalCase`
- Enums: `PascalCase` with singular name

## Conventions

- Prefer `interface` over `type` for object shapes
- Use `type` for unions, intersections, utilities
- Strict mode enabled (see tsconfig.json:5)
```

**Lines**: 15-18

### Testing (`testing.md`)

```markdown
# Testing Patterns

## Organization

- Unit: Colocated `*.test.ts`
- Integration: `tests/integration/`
- E2E: `tests/e2e/`

## Running Tests

- All: `bun test`
- Watch: `bun test --watch`
- Coverage: `bun test --coverage`

## Conventions

- Test factories in `tests/factories/`
- Mock API calls (see tests/setup.ts:20)
- Integration tests require running services

See docs/testing.md for detailed patterns
```

**Lines**: 18-20

### API (`api.md`)

```markdown
# API Conventions

## Structure

- Routes: `app/api/[resource]/route.ts`
- Validation: Zod schemas in same file
- Error handling: Custom `ApiError` class

## Patterns

- RESTful endpoints (see app/api/users/route.ts:10)
- tRPC for type-safe calls (see packages/api/src/router/)
- Response format: `{ data, error }`

## Authentication

- Middleware: `src/middleware/auth.ts:15`
- JWT tokens in Authorization header
- See docs/auth.md for implementation details
```

**Lines**: 16-18

### Build (`build.md`)

```markdown
# Build & Deployment

## Local Development

- Install: `bun install`
- Dev: `bun dev`
- Build: `bun build`

## Deployment

- Staging: Auto-deploy from `main`
- Production: Manual from tags
- See docs/deployment.md for procedures

## CI/CD

GitHub Actions workflows:
- `.github/workflows/test.yml` - Tests on PR
- `.github/workflows/deploy.yml` - Deployment
```

**Lines**: 15-17

## Language-Specific Examples

### Python Project

```
.cursor/rules/
├── core.md         # Project overview and workflow
├── python.md       # Python conventions, type hints
├── testing.md      # pytest patterns
├── api.md          # FastAPI patterns
└── db.md           # SQLAlchemy patterns
```

**`python.md`**:
```markdown
# Python Conventions

## Style

- Use uv, not pip
- Format: `ruff format`
- Lint: `ruff check`
- Type check: `mypy src/`

## Patterns

- Type hints required (see src/main.py:10)
- Docstrings: Google style
- Imports: Absolute from `src/`

## Dependencies

- Add: `uv add [package]`
- Sync: `uv sync`
- Scripts: Use uv script dependencies
```

### Go Project

```
.cursor/rules/
├── core.md         # Project overview
├── go.md           # Go conventions
├── testing.md      # Testing patterns
└── api.md          # HTTP/gRPC patterns
```

**`go.md`**:
```markdown
# Go Conventions

## Style

- Format: `gofmt` (on save)
- Lint: `golangci-lint run`
- Standard lib preferred over frameworks

## Patterns

- Errors: Return, don't panic
- Interfaces: Small, focused (see pkg/storage/storage.go:15)
- Context: First parameter in functions

## Structure

- `cmd/` - Application entry points
- `pkg/` - Reusable packages
- `internal/` - Private application code
```

### Monorepo

```
.cursor/rules/
├── core.md         # Monorepo overview
├── typescript.md   # Shared TS conventions
├── react.md        # React patterns (web, mobile)
├── testing.md      # Testing across packages
├── api.md          # tRPC patterns
└── build.md        # Build system, turborepo
```

## Best Practices

### 1. Stay Focused

Each file covers **one topic**:

✅ Good:
```markdown
# React Patterns

[Only React-specific content]
```

❌ Bad:
```markdown
# Frontend

[Mix of React, TypeScript, CSS, testing]
```

### 2. Use File References, Not Code

**Bad**:
```markdown
## Error Handling

```typescript
export class ApiError extends Error {
  constructor(public code: string, message: string) {
    super(message);
  }
}
```
```

**Good**:
```markdown
## Error Handling

Use `ApiError` class (see src/errors.ts:10) for API errors
```

### 3. Cross-Reference Related Files

```markdown
# React Patterns

## Testing

See testing.md for React Testing Library patterns

## Types

TypeScript interfaces in typescript.md
```

### 4. Keep It Universal

Avoid task-specific instructions:

❌ Bad:
```markdown
## Implementing Auth

1. Install NextAuth
2. Configure providers
3. Add middleware
```

✅ Good:
```markdown
## Auth

NextAuth configured (see app/api/auth/[...nextauth]/route.ts:15)
Middleware in middleware.ts:20
```

### 5. Link to Deep Dives

```markdown
# API Conventions

[Brief patterns - 15 lines]

See docs/api.md for:
- Full endpoint documentation
- Request/response schemas
- Error handling details
```

## Migration from CLAUDE.md

### If You Have CLAUDE.md

You can convert a CLAUDE.md to `.cursor/rules/`:

1. **Extract sections by domain**:
   - WHAT/WHY → `core.md`
   - React patterns → `react.md`
   - TypeScript conventions → `typescript.md`
   - Testing → `testing.md`

2. **Keep progressive disclosure**:
   - Still use `docs/` for deep topics
   - Rules reference these docs

3. **Create symlink** (optional):
   ```bash
   ln -s .cursor/rules/core.md CLAUDE.md
   ```

### Example Conversion

**Original CLAUDE.md** (60 lines):
```markdown
# CLAUDE.md

## What This Is
[10 lines - project overview]

## How to Work With It
[15 lines - workflow]

### React Patterns
[15 lines - React-specific]

### TypeScript Conventions
[10 lines - TS-specific]

### Testing
[10 lines - testing]
```

**Converted to `.cursor/rules/`**:
```
.cursor/rules/
├── core.md (25 lines) - Project overview + workflow
├── react.md (15 lines) - React patterns
├── typescript.md (10 lines) - TypeScript conventions
└── testing.md (10 lines) - Testing patterns
```

## Total Budget Management

**Rule of thumb**:
- 5-8 rule files × 15-25 lines each = 75-200 lines total
- Leave buffer for system prompts (~50 lines)
- Target: 150 lines total across all files
- Maximum: 200 lines total

**Example budgets**:

**Simple project** (4 files, 80 lines):
- core.md: 25 lines
- typescript.md: 15 lines
- testing.md: 20 lines
- api.md: 20 lines

**Complex project** (6 files, 150 lines):
- core.md: 30 lines
- react.md: 25 lines
- typescript.md: 20 lines
- testing.md: 25 lines
- api.md: 25 lines
- build.md: 25 lines

**Maximum viable** (8 files, 200 lines):
- core.md: 30 lines
- react.md: 25 lines
- typescript.md: 20 lines
- python.md: 25 lines
- testing.md: 25 lines
- api.md: 25 lines
- db.md: 25 lines
- build.md: 25 lines

## Maintenance

### Adding New Files

Add a file when:
- New technology added to stack
- Existing file exceeds 30 lines
- Distinct domain emerges

### Removing Files

Merge files when:
- File is under 10 lines
- Two files cover related topics
- Total line count approaching budget

### Quarterly Review

Check:
- [ ] Each file 10-30 lines
- [ ] Total under 200 lines
- [ ] No duplicate content
- [ ] File references still accurate
- [ ] All domains represented

## Comparison: CLAUDE.md vs .cursor/rules

| Aspect | CLAUDE.md | .cursor/rules |
|--------|-----------|---------------|
| **Files** | 1 main file | 4-8 focused files |
| **Lines** | 30-60 target | 10-30 per file |
| **Loading** | Always loaded | All auto-load |
| **Organization** | Sections in one file | Separate files by domain |
| **Best for** | Simple projects | Multi-tech stack |
| **Deep topics** | Progressive disclosure | Progressive disclosure |

Both use progressive disclosure for complex topics (architecture, detailed testing patterns, etc.).

The main difference is **organization**, not **total content loaded**.
