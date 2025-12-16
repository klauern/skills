# AGENTS.md Template

## Basic Template

```markdown
# AGENTS.md

## What This Is

[One sentence: what is this project?]

**Tech Stack**: [key languages, frameworks, tools]
**Architecture**: [monorepo structure OR single app description]

## Why It Exists

[2-3 sentences: business/technical purpose and key architectural decisions]

## How to Work With It

### Prerequisites
[Installation or setup commands, if any]

### Running Locally
[Development server commands]

### Testing
[Test commands and any critical notes]

### Building
[Build/verification commands]

### Key Conventions
- [Tool preferences: bun vs npm, uv vs pip, etc.]
- [Critical patterns: file references to examples]
- [Lint/format commands if not automated]

### Deep Dives
- [Topic]: [link to detailed doc]
- [Topic]: [link to detailed doc]
```

**Target**: 30-60 lines total

## Template with Examples

### Example 1: Next.js Monorepo

```markdown
# AGENTS.md

## What This Is

E-commerce platform with web storefront, admin dashboard, and mobile app.

**Tech Stack**: TypeScript, Next.js 14, React Native, tRPC, Prisma, PostgreSQL
**Architecture**: Monorepo with 3 apps (`web`, `admin`, `mobile`) and 4 shared packages

## Why It Exists

Provides unified e-commerce solution for small businesses.
Monorepo ensures shared auth, product types, and API client across all platforms.

## How to Work With It

### Prerequisites
- Node.js 20+
- PostgreSQL 15+ running locally
- Install: `bun install` (use bun, not npm)

### Running Locally
- Web storefront: `bun dev:web` (http://localhost:3000)
- Admin dashboard: `bun dev:admin` (http://localhost:3001)
- Mobile: `bun dev:mobile`

### Testing
- Unit tests: `bun test`
- E2E tests: `bun test:e2e` (requires running dev server)

### Building
- All: `bun build`
- Individual: `bun build:web`, `bun build:admin`, `bun build:mobile`

### Key Conventions
- Use tRPC for all API calls (see packages/api/src/router/products.ts:25)
- Prefer server components in Next.js apps
- Shared UI components in packages/ui
- Linting: `bun lint` (enforced by pre-commit hook)

### Deep Dives
- Database schema and migrations: docs/database.md
- Authentication flow: docs/auth.md
- Deployment process: docs/deployment.md
```

**Lines**: ~40

### Example 2: Python CLI Tool

```markdown
# AGENTS.md

## What This Is

Command-line tool for analyzing and optimizing Python dependencies.

**Tech Stack**: Python 3.11+, Click, uv for dependency management
**Architecture**: Single package with pluggable analyzer backends

## Why It Exists

Helps developers identify unused dependencies, version conflicts, and security issues.
Uses uv for fast, reliable dependency resolution.

## How to Work With It

### Prerequisites
- Python 3.11+
- Install: `uv sync` (use uv, not pip)

### Running Locally
- CLI: `uv run depcheck [command]`
- Interactive mode: `uv run depcheck --interactive`

### Testing
- All tests: `uv run pytest`
- With coverage: `uv run pytest --cov`
- Type checking: `uv run mypy src/`

### Building
- Package: `uv build`
- Install locally: `uv pip install -e .`

### Key Conventions
- Use uv for all dependency management
- All CLI commands in src/commands/ (see src/commands/analyze.py:15)
- Type hints required (enforced by mypy)
- Format with ruff: `uv run ruff format`

### Deep Dives
- Plugin system: docs/plugins.md
- Adding new analyzers: docs/analyzers.md
```

**Lines**: ~38

### Example 3: Microservices Project

```markdown
# AGENTS.md

## What This Is

Microservices platform for real-time data processing and analytics.

**Tech Stack**: Go (services), Node.js (gateway), Python (ML), PostgreSQL, Redis, Kafka
**Architecture**: 5 microservices behind Kong API gateway, event-driven via Kafka

## Why It Exists

Processes and analyzes high-volume sensor data from IoT devices.
Service-per-function design allows independent scaling and deployment.

## How to Work With It

### Prerequisites
- Docker Compose for local development
- Start infrastructure: `docker-compose up -d`

### Running Locally
- All services: `make dev`
- Individual service: `cd services/[name] && make run`
- Gateway: `cd gateway && bun dev`

### Testing
- Unit tests (all): `make test`
- Integration tests: `make test-integration` (requires running infra)
- Service-specific: `cd services/[name] && make test`

### Building
- All services: `make build`
- Docker images: `make docker-build`

### Key Conventions
- Go services use standard lib net/http (see services/ingestion/main.go:45)
- Inter-service communication via Kafka (see docs/messaging.md)
- API gateway handles auth/rate limiting
- Use make targets, not direct commands

### Deep Dives
- Service architecture and communication: docs/architecture.md
- Kafka event schemas: docs/events.md
- Deployment and scaling: docs/deployment.md
- Local development setup: docs/local-dev.md
```

**Lines**: ~42

### Example 4: React Component Library

```markdown
# AGENTS.md

## What This Is

React component library for building accessible enterprise applications.

**Tech Stack**: TypeScript, React 18, Radix UI primitives, Tailwind CSS, Storybook
**Architecture**: Single package with tree-shakeable exports

## Why It Exists

Provides accessible, customizable UI components for internal products.
Built on Radix primitives to ensure WCAG 2.1 AA compliance.

## How to Work With It

### Prerequisites
- Node.js 20+
- Install: `bun install`

### Running Locally
- Storybook: `bun storybook` (http://localhost:6006)
- Dev mode: `bun dev`

### Testing
- Unit tests: `bun test`
- Visual regression: `bun test:visual`
- Accessibility: `bun test:a11y`

### Building
- Library: `bun build`
- Storybook: `bun build:storybook`

### Key Conventions
- All components must have Storybook stories
- Use Radix primitives for interactive components
- Accessibility required (enforced by test:a11y)
- Component template: src/components/Button/Button.tsx:1

### Deep Dives
- Creating new components: docs/component-guide.md
- Accessibility guidelines: docs/accessibility.md
- Theming system: docs/theming.md
```

**Lines**: ~40

## Cursor .mdc Templates

When using `.cursor/rules/` with frontmatter, each file needs appropriate YAML frontmatter. See [cursor-mdc-format.md](cursor-mdc-format.md) for complete guide.

### Individual .mdc Rule Templates

#### Always Applied Rule Template

Use for universal, minimal context that applies to EVERY task.

```markdown
---
alwaysApply: true
---
# [Domain] Core

## [Key Section]

[Brief, universally applicable content]

**Key Points**:
- [Essential command or pattern]
- [Critical tool preference]
- [File reference for examples]

### [Optional Section]

[More essential info if needed]
```

**Target**: <30 lines
**Use for**: Project structure, essential commands, tool preferences
**Example**: `core.mdc` with project overview and workflow

#### File-Type Specific Rule Template

Use for language or framework-specific conventions.

```markdown
---
globs: *.ext,*.ext2
---
# [Language/Framework] Conventions

## Style

- Format: `[command]`
- Lint: `[command]`
- [Tool preferences]

## Patterns

[File references to examples]
- Pattern 1: [file](mdc:path/file.ext:line)
- Pattern 2: [file](mdc:path/file.ext:line)

## [Optional Section]

[Additional conventions if needed]
```

**Target**: 15-25 lines
**Use for**: Python conventions, React patterns, TypeScript rules
**Glob syntax**: Comma-separated, no spaces: `*.py`, `*.tsx,*.jsx`, `*.go`

#### Task-Specific Rule Template

Use for specialized workflows loaded on demand.

```markdown
---
description: [Clear description of when to use this rule]
---
# [Task/Domain] Guide

## [Main Section]

[Detailed guidance for this specific task]

### [Subsection]

[Step-by-step procedures or detailed patterns]

## [Additional Section]

[More task-specific info]

### [Safety Checks / Best Practices]

- [ ] Checklist item
- [ ] Checklist item

## [Optional: Common Patterns]

[Detailed examples or procedures]
```

**Target**: 30-50+ lines (can be longer since it's loaded on demand)
**Use for**: Deployment procedures, database migrations, testing setup, CI/CD
**Description tips**: Be specific about when this rule is relevant

### .mdc Examples by Project Type

#### Python CLI Project

**`core.mdc`** (alwaysApply):
```markdown
---
alwaysApply: true
---
# Project Core

## What This Is

CLI tool for analyzing Python dependencies.

**Tech**: Python 3.11+, Click, uv
**Entry**: [main.py](mdc:src/main.py)

## Commands

- Run: `uv run depcheck [cmd]`
- Test: `uv run pytest`
- Build: `uv build`

## Tools

Use `uv`, not pip for all dependency management.
```

**`python.mdc`** (globs):
```markdown
---
globs: *.py,*.pyi
---
# Python Conventions

## Dependencies

Use `uv` with inline script dependencies:
```python
# /// script
# dependencies = ["requests"]
# ///
```

## Format & Lint

- Format: `uv run ruff format`
- Lint: `uv run ruff check`
- Types: `uv run mypy src/`

## Patterns

Type hints required (see [api.py](mdc:src/api.py:10))
```

**`testing.mdc`** (description):
```markdown
---
description: Testing patterns, fixtures, and integration test setup
---
# Testing Guide

## Organization

- Unit: Colocated `*_test.py`
- Integration: `tests/integration/`
- Fixtures: `tests/fixtures/`

## Running Tests

- All: `uv run pytest`
- With coverage: `uv run pytest --cov`
- Specific: `uv run pytest tests/unit/test_analyzer.py`

## Patterns

### Test Factories

Use factories for test data (see [factories.py](mdc:tests/factories.py:1))

### Mocking

Mock external services (see [test_api.py](mdc:tests/unit/test_api.py:15))

### Integration Tests

Require running dependencies:
```bash
docker-compose -f tests/docker-compose.yml up -d
uv run pytest tests/integration/
```
```

#### TypeScript Monorepo

**`core.mdc`** (alwaysApply):
```markdown
---
alwaysApply: true
---
# Monorepo Core

## Structure

**Apps**: web, admin, mobile
**Packages**: ui, api, types, utils

## Commands

- Dev: `bun dev:[app]`
- Test: `bun test`
- Build: `bun build`

## Tools

Use `bun`, not npm or yarn.
```

**`typescript.mdc`** (globs):
```markdown
---
globs: *.ts,*.tsx
---
# TypeScript Conventions

## Types

- Shared: `packages/types/src/`
- Local: Colocated in same file
- No `any` (use `unknown`)

## Naming

- Interfaces: `PascalCase`
- Types: `PascalCase`
- Props: `ComponentNameProps`

## Patterns

Strict mode enabled (see [tsconfig.json](mdc:tsconfig.json:5))
```

**`react.mdc`** (globs):
```markdown
---
globs: *.tsx,*.jsx
---
# React Patterns

## Components

Prefer server components (see [Button.tsx](mdc:packages/ui/Button.tsx:1))

Client components only for:
- Event handlers
- Browser APIs
- React hooks

## Structure

- Props: `ComponentNameProps` interface
- Tests: Colocated `ComponentName.test.tsx`
- Styles: Tailwind classes

## State

- Server state: tRPC
- Client state: React Context
```

**`testing.mdc`** (description):
```markdown
---
description: Testing patterns for unit, integration, and E2E tests
---
# Testing Guide

## Organization

- Unit: Colocated `*.test.ts`
- Integration: `apps/[app]/tests/integration/`
- E2E: `apps/[app]/tests/e2e/`

## Running Tests

- All: `bun test`
- App-specific: `bun test:[app]`
- E2E: `bun test:e2e` (requires dev server)
- Coverage: `bun test --coverage`

## Unit Testing

### React Testing Library

See [Button.test.tsx](mdc:packages/ui/Button.test.tsx:1) for pattern

### Test Factories

Use factories in `tests/factories/` (see [user.factory.ts](mdc:tests/factories/user.factory.ts:1))

## Integration Testing

Requires running services:
```bash
docker-compose up -d
bun test:integration
```

## E2E Testing

Uses Playwright. See [e2e.config.ts](mdc:tests/e2e.config.ts:1) for setup.
```

#### Go Microservices

**`core.mdc`** (alwaysApply):
```markdown
---
alwaysApply: true
---
# Services Core

## Structure

**Services**: auth, api, worker, gateway
**Shared**: `pkg/` packages

## Commands

- Run: `make run-[service]`
- Test: `make test`
- Build: `make build`

## Tools

Use standard lib over frameworks where possible.
```

**`go.mdc`** (globs):
```markdown
---
globs: *.go
---
# Go Conventions

## Style

- Format: `gofumpt -w .`
- Lint: `golangci-lint run`

## Patterns

- Errors: Return, don't panic
- Context: First param (see [handler.go](mdc:services/api/handler.go:15))
- Interfaces: Small, focused (see [storage.go](mdc:pkg/storage/storage.go:10))

## Structure

- `cmd/` - Entry points
- `pkg/` - Reusable packages
- `internal/` - Private code
```

**`api.mdc`** (description):
```markdown
---
description: API conventions, HTTP handlers, and service communication patterns
---
# API Patterns

## HTTP Handlers

### Structure

```go
func (h *Handler) HandleResource(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    // handler logic
}
```

See [handler.go](mdc:services/api/handler.go:25) for full pattern

### Error Handling

Use `pkg/errors` for structured errors (see [errors.go](mdc:pkg/errors/errors.go:1))

## Service Communication

### Internal APIs

Use gRPC for service-to-service (see [proto/](mdc:proto/))

### Event-Driven

Kafka for async communication (see [events.go](mdc:pkg/events/events.go:1))

## Middleware

Auth, logging, tracing (see [middleware.go](mdc:services/gateway/middleware.go:1))
```

### Frontmatter Decision Guide

Use this to decide which frontmatter type for your .mdc file:

```
Is this relevant to EVERY task?
  YES → Is it <30 lines?
    YES → alwaysApply: true
    NO  → Too long, use description instead

  NO  → Is it specific to file types?
    YES → globs: "*.ext,*.ext2"

    NO  → Is it specific to tasks?
      YES → description: "Clear task description"

      NO  → Probably doesn't belong in rules
```

**Budget Check**:
- All `alwaysApply` files combined: <50 lines total
- Each `globs` file: 15-25 lines
- Each `description` file: 30-50+ lines (can be longer)
- Total all files: <200 lines

## Filling Out the Template

### 1. Start with WHAT

**Questions to answer**:
- What type of project is this? (web app, CLI, library, platform)
- What are the 3-5 key technologies?
- What's the high-level structure? (monorepo, single app, microservices)

**Keep it to**: 3-5 lines

### 2. Add WHY

**Questions to answer**:
- What problem does this solve?
- Why was this architectural approach chosen?
- What's the core value proposition?

**Keep it to**: 2-4 lines

### 3. Detail HOW

**Questions to answer**:
- What commands start the dev environment?
- What commands run tests?
- What commands build/verify changes?
- What tool preferences exist? (bun vs npm, uv vs pip)
- What critical patterns should Claude know?
- What topics need deeper documentation?

**Keep it to**: 15-25 lines

### 4. Review and Trim

**Check**:
- [ ] Total < 60 lines (stretch: < 300 lines max)
- [ ] No code snippets (only file:line references)
- [ ] No style guide content
- [ ] No task-specific instructions
- [ ] All content applies to >80% of tasks
- [ ] Complex topics moved to progressive disclosure

## Advanced: Multiple Environments

If you have significantly different workflows for different environments (local dev vs production, frontend vs backend in monorepo), consider:

### Option 1: Single File with Sections

```markdown
## How to Work With It

### Frontend Development
- Start: `bun dev:web`
- Test: `bun test:web`

### Backend Development
- Start: `bun dev:api`
- Test: `bun test:api`

### Full Stack
- Start all: `bun dev`
- Test all: `bun test`
```

### Option 2: Progressive Disclosure

```markdown
## How to Work With It

### Quick Start
- Full stack: `bun dev`
- Tests: `bun test`

### Deep Dives
- Frontend development: docs/frontend.md
- Backend development: docs/backend.md
- Infrastructure setup: docs/infrastructure.md
```

**Prefer Option 2** if any section would be >5 lines.

## Common Sections (Optional)

### Prerequisites

Include if setup is non-trivial:
```markdown
### Prerequisites
- Node.js 20+
- PostgreSQL 15+ running on port 5432
- Redis running on port 6379
- Install: `bun install`
```

Skip if setup is just "install dependencies":
```markdown
### Running Locally
`bun install && bun dev`
```

### Environment Variables

Only if universally needed:
```markdown
### Prerequisites
Copy `.env.example` to `.env` and configure:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
```

If environment-specific or task-specific, use progressive disclosure:
```markdown
### Prerequisites
See docs/environment.md for required environment variables
```

### Deployment

Usually too task-specific. Use progressive disclosure:
```markdown
### Deep Dives
- Deployment process: docs/deployment.md
```

Only include if universally relevant:
```markdown
### Deployment
Merging to `main` auto-deploys to staging via GitHub Actions
```

## Customization Notes

### Adjust for Your Context

This template assumes:
- You use modern tooling (bun, uv, etc.)
- You have automated linting/formatting
- You follow common conventions

**Customize**:
- Change tool names to match your stack
- Add sections specific to your domain
- Remove sections that don't apply

**But maintain**:
- WHAT/WHY/HOW structure
- Under 60 lines target
- Progressive disclosure for details
- No code snippets
- No task-specific content

### File Location

**Standard**: Put at repository root as `AGENTS.md`

**Symlink for compatibility**: Create `AGENTS.md` symlink:
```bash
ln -s AGENTS.md CLAUDE.md
```

This ensures compatibility with tools that look for either name.
