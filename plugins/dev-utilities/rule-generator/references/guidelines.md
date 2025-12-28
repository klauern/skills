# AGENTS.md Guidelines

## Core Principles

1. **LLMs are stateless** - AGENTS.md is your persistent context. Make every word count.
2. **Instruction budget** - LLMs follow ~150-200 instructions. Target <60 lines.
3. **Universal applicability** - Task-specific content gets ignored. Keep it universal.

## WHAT/WHY/HOW Structure

### WHAT (3-5 lines)
- Tech stack summary
- Architecture type
- Monorepo structure if applicable

### WHY (2-4 lines)
- Project purpose
- Key architectural decisions

### HOW (10-20 lines)
- Build/test/run commands
- Tool preferences
- Links to detailed docs

## Content Guidelines

### ✅ DO Include
- Tech stack summary
- Architecture overview
- Tool preferences (bun vs npm, uv vs pip)
- Build/test commands
- Progressive disclosure links

### ❌ DON'T Include
- Style guides (use linters)
- Code examples (use file:line references)
- Database schemas (link to docs)
- Task-specific instructions
- Auto-generated content

## Quality Checklist

**Length**:
- [ ] Total < 60 lines (ideal) or < 300 lines (max)
- [ ] No section > 20 lines

**Content**:
- [ ] WHAT explains tech and architecture
- [ ] WHY explains purpose
- [ ] HOW covers workflows
- [ ] No code snippets
- [ ] Progressive disclosure for details

## Common Mistakes

### Style Guide Content
❌ `Use 2 spaces... prefer const...`
✅ `Run bun lint (enforced by pre-commit)`

### Task-Specific Instructions
❌ `When implementing auth: 1. Use NextAuth...`
✅ `See docs/auth.md for auth patterns`

### Code Examples
❌ `export async function GET()...` (20 lines)
✅ `See app/api/users/route.ts:15`

### Overly Detailed Architecture
❌ List every service, port, database...
✅ `Microservices with Kong gateway. See docs/architecture.md`

## Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| Everything file | Too long | Progressive disclosure |
| Style bible | Linters do this | Use formatters/hooks |
| Tutorial | Task-specific | Keep universal only |
| Auto-generated | Low quality | Manually craft |
| Stale snapshot | Outdated code | Use file:line refs |

## Maintenance

**Update when**: Tech stack, architecture, workflows change
**Don't update for**: New features, bug fixes, style changes
**Review**: Quarterly - check length, remove cruft
