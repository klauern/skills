# Progressive Disclosure for CLAUDE.md

## Core Concept

**Progressive disclosure**: Keep CLAUDE.md lean by linking to separate, focused documentation files. Claude will read these files **when relevant to the current task**.

**Key insight**: Claude ignores content deemed irrelevant. By moving detailed content to separate files, you:
1. Keep CLAUDE.md under the instruction budget
2. Allow Claude to load details only when needed
3. Maintain detailed documentation for complex topics

## When to Use Progressive Disclosure

### Move to Separate Files When:

- **Topic is >10 lines** of explanation in CLAUDE.md
- **Only relevant for specific tasks** (not universally applicable)
- **Requires code examples** or detailed procedures
- **Changes frequently** (isolate churn from stable CLAUDE.md)
- **Deep technical detail** (database schemas, API specs)

### Keep in CLAUDE.md When:

- **Universal workflow** (build, test commands)
- **Tool preferences** (bun vs npm, uv vs pip)
- **Critical architecture** (monorepo structure summary)
- **Can be explained in <5 lines**

## Recommended Structure

```
your-repo/
├── CLAUDE.md              # Main file (30-60 lines)
├── AGENTS.md → CLAUDE.md  # Symlink for compatibility
└── docs/
    ├── architecture.md    # Deep dive on system design
    ├── testing.md         # Testing patterns and examples
    ├── database.md        # Schema, migrations, conventions
    ├── deployment.md      # Deployment procedures
    ├── auth.md           # Authentication implementation
    └── api.md            # API documentation and examples
```

**Alternative locations**:
- `.claude/` directory (hidden from casual browsing)
- `agent_docs/` directory (explicit AI focus)
- Existing `docs/` directory (if already used)

**Recommendation**: Use existing `docs/` directory if present, otherwise create it.

## How to Reference in CLAUDE.md

### Pattern 1: In Context

```markdown
### Testing
- Unit tests: `bun test`
- E2E tests: `bun test:e2e`
- See docs/testing.md for integration test patterns
```

**Why it works**: Provides immediate value (commands), points to details when needed.

### Pattern 2: Deep Dives Section

```markdown
### Deep Dives
- Testing patterns and integration tests: docs/testing.md
- Database schema and migrations: docs/database.md
- Authentication implementation: docs/auth.md
- Deployment procedures: docs/deployment.md
```

**Why it works**: Centralized reference, easy to scan, clear organization.

### Pattern 3: Inline Reference

```markdown
### Database
PostgreSQL 15+ with Prisma ORM. See docs/database.md for schema and migrations.
```

**Why it works**: Brief summary, clear pointer to details.

## What Belongs in Progressive Disclosure Docs

### Architecture (docs/architecture.md)

**Include**:
- Detailed system architecture diagrams or descriptions
- Service communication patterns
- Data flow diagrams
- Design decision records (why X over Y)
- Service responsibilities and boundaries

**Example**:
```markdown
# Architecture

## System Overview

[Detailed description of services, their responsibilities, and how they communicate]

## Service Map

- **API Gateway** (Kong): Routes requests, handles auth, rate limiting
- **User Service** (Go): User management, profiles, preferences
- **Product Service** (Python): Product catalog, inventory
- **Order Service** (Node.js): Order processing, payment integration

## Communication Patterns

### Synchronous (REST/gRPC)
[Details on when and how services call each other]

### Asynchronous (Kafka)
[Event schemas, message patterns, consumer groups]

## Data Flow

[Detailed flow from user request to response]
```

### Testing (docs/testing.md)

**Include**:
- Integration test patterns and examples
- Test data setup procedures
- Mocking strategies
- E2E test organization
- Test environment setup

**Example**:
```markdown
# Testing Guide

## Test Organization

- Unit tests: Colocated with source files (`*.test.ts`)
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`

## Integration Test Patterns

### Database Integration

[Code example showing test database setup]

### API Integration

[Code example showing API test patterns]

## Running Tests

### Unit Tests
```bash
bun test
```

### Integration Tests
```bash
docker-compose up -d postgres redis  # Start dependencies
bun test:integration
```

### E2E Tests
```bash
bun test:e2e  # Starts services automatically
```

## Writing New Tests

[Patterns and examples for writing tests]
```

### Database (docs/database.md)

**Include**:
- Schema overview and entity relationships
- Migration procedures
- Seeding data
- Database conventions
- Query patterns and performance considerations

**Example**:
```markdown
# Database Guide

## Schema Overview

### Core Entities

- `users`: User accounts and authentication
- `products`: Product catalog
- `orders`: Order transactions
- `order_items`: Line items for orders

### Relationships

[Description or diagram of entity relationships]

## Migrations

### Creating Migrations

```bash
bun migrate:create [name]
```

### Running Migrations

```bash
bun migrate:up    # Apply migrations
bun migrate:down  # Rollback migrations
```

## Seeding Data

### Development
```bash
bun seed:dev  # Seed with test data
```

### Testing
```bash
bun seed:test  # Minimal seed for tests
```

## Conventions

- Use snake_case for column names
- All tables have `id` (UUID), `created_at`, `updated_at`
- Foreign keys: `[table]_id` (e.g., `user_id`)
- Indexes on all foreign keys
```

### Authentication (docs/auth.md)

**Include**:
- Authentication flow details
- Authorization patterns
- Session management
- Token handling
- Security considerations

**Example**:
```markdown
# Authentication Guide

## Flow Overview

1. User submits credentials to `/api/auth/login`
2. Server validates credentials
3. Server creates session in Redis
4. Server returns JWT with session ID
5. Client includes JWT in Authorization header
6. Middleware validates JWT and checks session

## Implementation

### Login Endpoint

See `src/api/auth/login.ts:25` for implementation

### Session Management

Sessions stored in Redis with 24-hour TTL:
```typescript
// Example in src/auth/session.ts:15
```

### Middleware

Auth middleware in `src/middleware/auth.ts:10` validates tokens.

## Security

- Passwords hashed with bcrypt (12 rounds)
- JWTs signed with RS256
- Session IDs are cryptographically random
- CSRF protection via double-submit cookies
```

### Deployment (docs/deployment.md)

**Include**:
- Deployment procedures
- Environment configuration
- CI/CD pipeline details
- Rollback procedures
- Monitoring and alerting

**Example**:
```markdown
# Deployment Guide

## Environments

- **Development**: Local docker-compose
- **Staging**: staging.example.com (auto-deploy from `main`)
- **Production**: app.example.com (manual deploy from tags)

## Deployment Process

### Staging (Automatic)

Merging to `main` triggers GitHub Actions workflow:
1. Run tests
2. Build Docker images
3. Push to container registry
4. Deploy to staging via Kubernetes
5. Run smoke tests

### Production (Manual)

1. Create release tag: `git tag -a v1.2.3 -m "Release 1.2.3"`
2. Push tag: `git push origin v1.2.3`
3. GitHub Actions builds and pushes images
4. Manually trigger deployment in GitHub Actions UI
5. Monitor rollout in Kubernetes dashboard
6. Verify health checks

## Environment Variables

See `.env.example` for required variables.

Production secrets managed in Kubernetes secrets:
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `STRIPE_SECRET_KEY`

## Rollback

```bash
kubectl rollout undo deployment/[service-name]
```

Or via GitHub Actions: Redeploy previous tag.
```

### API Documentation (docs/api.md)

**Include**:
- API endpoint documentation
- Request/response examples
- Error codes and handling
- Rate limiting details
- Versioning strategy

**Example**:
```markdown
# API Documentation

## Overview

RESTful API with JSON request/response bodies.

**Base URL**: `https://api.example.com/v1`

## Authentication

All endpoints (except `/auth/login`, `/auth/register`) require authentication:

```
Authorization: Bearer [JWT_TOKEN]
```

## Endpoints

### Users

#### GET /users/:id

Get user by ID.

**Response**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-15T12:00:00Z"
}
```

#### POST /users

Create new user. See `src/api/users/create.ts:20` for implementation.

**Request**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "secure_password"
}
```

### Products

[... more endpoints ...]

## Error Handling

All errors return standard format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": { "field": "email" }
  }
}
```

### Error Codes

- `VALIDATION_ERROR`: Invalid request data
- `UNAUTHORIZED`: Missing or invalid auth token
- `FORBIDDEN`: Authenticated but insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per authenticated user
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
```

## Best Practices

### 1. Focus Each File

Each progressive disclosure file should have a **single, clear purpose**:

- ✅ `testing.md` covers all testing topics
- ✅ `deployment.md` covers all deployment topics
- ❌ Don't split into `unit-testing.md`, `integration-testing.md`, `e2e-testing.md`

**Why**: Avoids fragmentation. Claude can load one file and get comprehensive context.

### 2. Use Code References, Not Code Dumps

**Bad**:
```markdown
## Example Implementation

```typescript
export async function authenticateUser(
  email: string,
  password: string
): Promise<User> {
  const user = await db.user.findUnique({ where: { email } });
  if (!user) throw new AuthError('Invalid credentials');

  const valid = await bcrypt.compare(password, user.password_hash);
  if (!valid) throw new AuthError('Invalid credentials');

  return user;
}
```
```

**Good**:
```markdown
## Example Implementation

See `src/auth/authenticate.ts:15` for the user authentication function.

Key points:
- Uses bcrypt for password comparison
- Returns User object on success
- Throws AuthError on failure
```

**Why**: Code references stay accurate. Code snippets become stale.

### 3. Include "When to Read This"

Help Claude (and humans) know when each file is relevant:

```markdown
# Testing Guide

**Read this when**: Writing new tests, debugging test failures, setting up test environment

[... rest of content ...]
```

### 4. Link Back to Source

Progressive disclosure docs should reference the actual source code:

```markdown
## Login Flow

The login endpoint (`src/api/auth/login.ts:25`) handles user authentication.

See implementation for full details on validation, session creation, and response format.
```

**Why**: Claude can verify current implementation against documentation.

### 5. Keep Examples Minimal

Provide **patterns**, not exhaustive examples:

**Bad** (exhaustive):
```markdown
## Test Examples

### User Creation Test
[50 lines of code]

### User Update Test
[50 lines of code]

### User Deletion Test
[50 lines of code]
```

**Good** (pattern):
```markdown
## Test Patterns

### Standard Entity Test Pattern

See `tests/integration/users.test.ts:15` for example.

Pattern:
1. Setup test data
2. Make request
3. Assert response
4. Verify database state
5. Cleanup
```

**Why**: Patterns apply broadly. Exhaustive examples waste context.

## Maintenance

### Keep Files Synchronized

When code changes significantly:

- [ ] Update relevant progressive disclosure docs
- [ ] Update file:line references if code moved
- [ ] Add new topics if needed

### Prune Stale Content

Quarterly review:

- [ ] Remove outdated procedures
- [ ] Update examples to reflect current patterns
- [ ] Remove redundant content
- [ ] Consolidate fragmented topics

### Avoid Duplication

If content appears in multiple places:

- **CLAUDE.md**: One-line summary + link
- **Progressive disclosure**: Full details

Never duplicate full explanations.

## Example: Full Progressive Disclosure Setup

### CLAUDE.md (42 lines)

```markdown
# CLAUDE.md

## What This Is

E-commerce API platform with web and mobile clients.

**Tech Stack**: TypeScript, Next.js 14, React Native, tRPC, Prisma, PostgreSQL
**Architecture**: Monorepo with 3 apps and 4 shared packages

## Why It Exists

Unified e-commerce solution for small businesses.
Monorepo shares auth, types, and API client across platforms.

## How to Work With It

### Prerequisites
- Node.js 20+, PostgreSQL 15+
- Install: `bun install`

### Running Locally
- All: `bun dev`
- Web only: `bun dev:web`
- API only: `bun dev:api`

### Testing
- Unit: `bun test`
- E2E: `bun test:e2e`

### Building
`bun build` - Builds all packages in dependency order

### Key Conventions
- Use bun, not npm
- tRPC for API calls (see packages/api/src/router/products.ts:25)
- Prefer server components in Next.js
- Lint: `bun lint` (enforced by pre-commit)

### Deep Dives
- Architecture and services: docs/architecture.md
- Testing patterns: docs/testing.md
- Database schema: docs/database.md
- Authentication: docs/auth.md
- Deployment: docs/deployment.md
```

### docs/ Structure

```
docs/
├── architecture.md     # System design, service map, data flow (120 lines)
├── testing.md         # Test patterns, integration examples (80 lines)
├── database.md        # Schema, migrations, conventions (100 lines)
├── auth.md           # Auth flow, session management (60 lines)
└── deployment.md     # Deploy procedures, environments (90 lines)
```

**Total**:
- CLAUDE.md: 42 lines (well under budget)
- Progressive docs: 450 lines (loaded on-demand)
- **Effective context**: 42 lines default, up to 492 when all topics relevant

**Without progressive disclosure**:
- Single CLAUDE.md: 492 lines (exceeds budget, wastes context)

## Summary

Progressive disclosure allows you to:

- ✅ Keep CLAUDE.md under 60 lines
- ✅ Maintain detailed documentation
- ✅ Load context only when relevant
- ✅ Stay within instruction budget
- ✅ Provide comprehensive guidance

**Rule of thumb**: If it's >10 lines in CLAUDE.md, it belongs in progressive disclosure.
