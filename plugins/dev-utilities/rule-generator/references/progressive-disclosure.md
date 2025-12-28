# Progressive Disclosure

Keep AGENTS.md lean by linking to focused documentation. Agents read linked files when relevant.

## When to Use

**Move to docs/ when**:
- Topic >10 lines in AGENTS.md
- Only relevant for specific tasks
- Requires code examples or procedures
- Changes frequently

**Keep in AGENTS.md when**:
- Universal workflow (build, test commands)
- Tool preferences
- Architecture summary
- Can be explained in <5 lines

## Recommended Structure

```
project/
├── AGENTS.md              # 30-60 lines
├── CLAUDE.md → AGENTS.md  # Symlink
└── docs/
    ├── architecture.md    # System design
    ├── testing.md         # Test patterns
    ├── database.md        # Schema, migrations
    └── deployment.md      # Deploy procedures
```

## How to Reference

### In-Context
```markdown
### Testing
- Unit: `bun test` | E2E: `bun test:e2e`
- See docs/testing.md for integration patterns
```

### Deep Dives Section
```markdown
### Deep Dives
- Architecture: docs/architecture.md
- Testing: docs/testing.md
- Database: docs/database.md
```

## Progressive Doc Content

### architecture.md
- Service map and responsibilities
- Communication patterns (REST, gRPC, events)
- Data flow diagrams
- Design decisions (why X over Y)

### testing.md
- Test organization (unit/integration/e2e)
- Running tests by type
- Test factories and patterns
- Mocking strategies

### database.md
- Schema overview
- Migration commands
- Seeding procedures
- Conventions (naming, indexes)

### deployment.md
- Environment differences (dev/staging/prod)
- Deploy procedures
- Rollback steps
- Environment variables

## Best Practices

1. **Focus each file** - One topic per doc (testing.md, not unit-testing.md + integration-testing.md)
2. **Use file references** - `See src/auth.ts:15` not code snippets
3. **Add "When to read"** - Help agents know relevance
4. **Keep examples minimal** - Patterns, not exhaustive lists

## Don'ts

- ❌ Duplicate content between AGENTS.md and docs
- ❌ Include code dumps (use file:line references)
- ❌ Fragment topics into many small files
- ❌ Auto-generate without review
