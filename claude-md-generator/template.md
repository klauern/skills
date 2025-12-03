# CLAUDE.md Template

## Basic Template

```markdown
# CLAUDE.md

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
# CLAUDE.md

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
# CLAUDE.md

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
# CLAUDE.md

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
# CLAUDE.md

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

**Standard**: Put at repository root as `CLAUDE.md`

**Symlink for compatibility**: Create `AGENTS.md` symlink:
```bash
ln -s CLAUDE.md AGENTS.md
```

This ensures compatibility with tools that look for either name.
