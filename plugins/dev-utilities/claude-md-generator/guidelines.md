# CLAUDE.md Guidelines

## Core Principles

### 1. LLMs Are Stateless

Every conversation starts fresh. CLAUDE.md is your **only** persistent context mechanism. Make every word count.

### 2. Instruction Budget

- **Total capacity**: ~150-200 instructions
- **Claude Code system**: ~50 instructions used
- **Your budget**: ~100-150 instructions remaining
- **Target**: Under 60 lines (much less than max)

### 3. Universal Applicability

Claude ignores content it deems irrelevant. Task-specific instructions often get dropped. Keep everything universally applicable.

## The WHAT/WHY/HOW Structure

### WHAT: Technology & Architecture

**Purpose**: Help Claude understand your codebase structure

**Include**:
- Tech stack (languages, frameworks, key libraries)
- Architecture type (monorepo, microservices, single app)
- For monorepos: which apps/packages exist and their relationships
- File organization patterns if non-standard

**Example**:
```markdown
**Tech Stack**: TypeScript, React, Next.js 14, Tailwind, tRPC
**Architecture**: Monorepo with 3 apps (web, admin, mobile) and 5 shared packages
```

**Keep it brief**: 3-5 lines maximum

### WHY: Purpose & Context

**Purpose**: Help Claude understand the business/technical goals

**Include**:
- Project's main purpose (1 sentence)
- Why architectural choices were made
- What problems this solves

**Example**:
```markdown
A developer collaboration platform focused on async code review.
Built as a monorepo to share auth, UI components, and API types across web/mobile.
```

**Keep it brief**: 2-4 lines maximum

### HOW: Workflows & Conventions

**Purpose**: Help Claude work effectively in your environment

**Include**:
- How to run tests
- How to build/verify changes
- Tool preferences (bun vs npm, uv vs pip)
- Critical workflow notes
- Links to detailed guides

**Example**:
```markdown
### Running Tests
`bun test` - Use bun, not npm

### Building
`bun run build` - Builds all packages in dependency order

### Key Conventions
- Prefer server components over client components
- See docs/testing.md for integration test patterns
```

**Keep it targeted**: 10-20 lines maximum

## What to Include

### ✅ DO Include

- **Tech stack summary**: Languages, frameworks, key libraries
- **Architecture overview**: Monorepo structure, app purposes
- **Tool preferences**: `bun` not `npm`, `uv` not `pip`
- **Build/test commands**: One-liners for common tasks
- **Critical workflows**: Non-obvious but universally needed info
- **Progressive disclosure links**: Pointers to detailed docs

### ❌ DON'T Include

- **Style guides**: Use linters/formatters/hooks instead
- **Code examples**: Use `file:line` references to source
- **Database schemas**: Put in progressive disclosure docs
- **API documentation**: Put in progressive disclosure docs
- **Task-specific instructions**: "When implementing auth..." type content
- **Outdated information**: Links to docs that might change

## Progressive Disclosure

### When to Use Separate Files

Move content to separate markdown files when:

- Topic is >10 lines of explanation
- Only relevant for specific tasks (auth, testing, deployment)
- Requires code examples or detailed procedures
- Subject to frequent updates

### Example Structure

```
docs/
  architecture.md       # Deep dive on monorepo structure
  testing.md           # Integration test patterns
  deployment.md        # Deployment procedures
  database.md          # Schema, migrations, conventions
```

### How to Reference

In CLAUDE.md:
```markdown
### Testing
`bun test` - See docs/testing.md for integration test patterns

### Architecture
Monorepo with 3 apps and 5 packages - see docs/architecture.md
```

Claude will read these files when relevant to the current task.

## Quality Checklist

### Length

- [ ] Total length < 60 lines (ideal)
- [ ] Total length < 300 lines (maximum)
- [ ] No section >20 lines

### Content

- [ ] WHAT section explains tech stack and architecture
- [ ] WHY section explains purpose
- [ ] HOW section covers common workflows
- [ ] No code snippets (only file:line references)
- [ ] No task-specific instructions
- [ ] No style guide content

### Applicability

- [ ] All content applies to >80% of tasks
- [ ] Tool preferences clearly stated
- [ ] Build/test commands present
- [ ] Progressive disclosure for deep topics

### Maintenance

- [ ] No hard-coded versions/paths that will change
- [ ] File references use project-relative paths
- [ ] Links to stable documentation URLs
- [ ] Manually crafted and reviewed (not auto-generated)

## Common Mistakes

### 1. Too Much Style Guide Content

**Bad**:
```markdown
## Code Style

- Use 2 spaces for indentation
- Always use semicolons
- Prefer const over let
- Use arrow functions
- Max line length 100
```

**Good**:
```markdown
Run `bun lint` before committing (enforced by pre-commit hook)
```

**Why**: Linters handle this better. Don't waste instruction budget.

### 2. Task-Specific Instructions

**Bad**:
```markdown
When implementing authentication:
1. Use NextAuth.js
2. Store sessions in Redis
3. Implement OAuth providers
```

**Good**:
```markdown
See docs/authentication.md for auth implementation patterns
```

**Why**: Only relevant for auth tasks. Use progressive disclosure.

### 3. Code Examples in Main File

**Bad**:
```markdown
## API Routes

```typescript
export async function GET(req: Request) {
  return Response.json({ data });
}
```
```

**Good**:
```markdown
API routes in app/api/ - see app/api/users/route.ts:15 for example
```

**Why**: File references are always accurate. Code snippets become stale.

### 4. Overly Detailed Architecture

**Bad**:
```markdown
## Architecture

We use a microservices architecture with:
- API Gateway (Kong) on port 8000
- Auth Service (Node.js) on port 3001
- User Service (Go) on port 3002
- Product Service (Python) on port 3003
- Message Queue (RabbitMQ) for async communication
- PostgreSQL for relational data
- Redis for caching
- Elasticsearch for search
[... 20 more lines ...]
```

**Good**:
```markdown
**Architecture**: Microservices with Kong gateway
**Languages**: Node.js (auth), Go (users), Python (products)
See docs/architecture.md for service map and communication patterns
```

**Why**: Keep it lean. Progressive disclosure for details.

## Anti-Patterns

### ❌ The Everything File

Trying to include all project knowledge in one file.

**Solution**: Use progressive disclosure. Link to focused docs.

### ❌ The Style Bible

Extensive code style, naming conventions, formatting rules.

**Solution**: Use linters, formatters, and Claude Code hooks.

### ❌ The Tutorial

Step-by-step "how to implement X" guides for multiple features.

**Solution**: Keep universally applicable commands only. Document patterns elsewhere.

### ❌ The Auto-Generated Blob

Using `/init` or similar tools to auto-generate a massive file.

**Solution**: Manually craft a lean, focused file. Every line should earn its place.

### ❌ The Stale Snapshot

Code examples, hard-coded paths, version numbers that become outdated.

**Solution**: Use file:line references. Link to authoritative sources.

## Real-World Example: Too Long vs Just Right

### ❌ Too Long (180 lines)

```markdown
# MyApp Documentation

## Table of Contents
[30 lines of TOC]

## Technology Stack

**Frontend**:
- React 18.2.0
- TypeScript 5.1.6
- Vite 4.4.5
- React Router 6.14.2
[... 40 more lines of every dependency ...]

## Code Style Guide

### Naming Conventions
- Components: PascalCase
- Functions: camelCase
- Constants: UPPER_SNAKE_CASE
[... 30 more lines ...]

## API Documentation

### User Endpoints
POST /api/users
```json
{ "email": "...", "name": "..." }
```
[... 40 more lines ...]

## Database Schema
[... 30 more lines ...]
```

**Problems**: Too long, includes style guide, has code examples, has task-specific content.

### ✅ Just Right (45 lines)

```markdown
# CLAUDE.md

## What This Is

MyApp is a user management platform with web and mobile clients.

**Tech Stack**: TypeScript, React, React Native, tRPC, Prisma, PostgreSQL
**Architecture**: Monorepo - `apps/web`, `apps/mobile`, `packages/api`

## Why It Exists

Simplifies user onboarding and management for B2B SaaS companies.
Monorepo structure shares types and API client across platforms.

## How to Work With It

### Prerequisites
Install dependencies: `bun install` (use bun, not npm)

### Running Locally
- Web: `bun dev:web`
- Mobile: `bun dev:mobile`
- API: `bun dev:api`

### Testing
- Unit: `bun test`
- E2E: `bun test:e2e` (requires running API)

### Building
`bun build` - Builds all apps and packages in dependency order

### Key Conventions
- Use tRPC for API calls (see packages/api/src/router/users.ts:10)
- Prefer server components in Next.js app
- Code style enforced by `bun lint` (runs on pre-commit)

### Deep Dives
- Database schema and migrations: docs/database.md
- Authentication patterns: docs/auth.md
- Testing integration patterns: docs/testing.md
```

**Why it works**: Concise, structured, universal, uses progressive disclosure.

## Maintenance

### When to Update

Update CLAUDE.md when:
- Tech stack changes (new framework, language)
- Architecture changes (monorepo split, new service)
- Build/test commands change
- Tool preferences change (npm → bun, etc.)

### When NOT to Update

Don't update for:
- New features (unless they change architecture)
- Bug fixes
- Style guide changes (handle with linters)
- Documentation updates (progressive disclosure docs only)

### Review Cadence

- **Quarterly**: Check length, remove cruft
- **On major changes**: Tech stack, architecture, workflows
- **Never**: Automated updates or auto-regeneration
