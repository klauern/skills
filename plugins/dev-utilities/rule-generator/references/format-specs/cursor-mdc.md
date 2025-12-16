# Cursor .mdc Format Reference

## Overview

Cursor rules use the `.mdc` extension (Markdown with YAML frontmatter) to enable intelligent rule loading. Instead of loading all rules into every conversation, frontmatter controls when and how rules are applied.

**Key Benefit**: Optimizes the instruction budget (~150-200 total instructions LLMs can reliably follow) by loading only relevant rules for each task.

**File Location**: `.cursor/rules/*.mdc`

**Compatibility**: Claude Code also reads `.cursor/rules/` - no separate configuration needed.

## Frontmatter Types

Rules use YAML frontmatter to specify loading behavior. Three types available:

### 1. alwaysApply: true

**Use for**: Minimal, universally applicable context that applies to EVERY task.

**How it works**: Rule loads into every conversation automatically.

**Instruction budget**: Competes with system prompts (~50 instructions). Keep total always-applied content under 50 lines across ALL files.

**Examples of good uses**:
- Project structure and entry points
- Essential commands (build, test, run)
- Tool preferences (bun vs npm, fd vs find)
- Authentication methods

**Examples of bad uses**:
- Style guides (use linters instead)
- Detailed deployment procedures (use description)
- Database schemas (use progressive disclosure)
- Task-specific workflows (use description)

**Best practice**: If unsure, DON'T use alwaysApply. Default to description or globs instead.

### 2. description: "..."

**Use for**: Task-specific guidance loaded on demand when the agent determines it's relevant.

**How it works**: Agent reads the description and fetches the rule when it matches the current task context.

**Instruction budget**: Doesn't consume budget until needed. Can be longer (30-50 lines or more).

**Description writing tips**:
- Be specific about WHEN to use the rule
- Use task-oriented language ("deployment procedures", "testing integration patterns")
- Mention key concepts that signal relevance ("migration", "rollback", "CI/CD")

**Examples of good uses**:
- Deployment workflows with rollback steps
- Database migration procedures
- Complex testing patterns
- Integration with external services
- Security review checklists

**Best practice**: Most rules should use description. It's the default for specialized guidance.

### 3. globs: "*.ext,*.ext2"

**Use for**: File-type-specific guidance that auto-attaches when editing matching files.

**How it works**: Rule automatically loads when the agent works with files matching the glob pattern.

**Instruction budget**: Only consumes budget when working with matching file types.

**Glob pattern syntax**:
- Comma-separated, no spaces: `*.py,*.pyi`
- Supports wildcards: `*.tsx`, `test_*.py`
- Multiple extensions: `*.js,*.jsx,*.ts,*.tsx`

**Examples of good uses**:
- Language-specific conventions (Python, TypeScript, Go)
- Framework patterns (React, Vue, Django)
- Test file conventions
- Configuration file formats

**Best practice**: Use globs for anything that only applies to specific file types.

## Decision Tree

```
START
 │
 ├─ Is this relevant to EVERY task in the project?
 │   │
 │   ├─ YES → Is it minimal (<30 lines)?
 │   │   │
 │   │   ├─ YES → Use alwaysApply: true
 │   │   │
 │   │   └─ NO → Too long for alwaysApply
 │   │           Use description: "..." instead
 │   │
 │   └─ NO → Is it specific to certain file types?
 │       │
 │       ├─ YES → Use globs: "*.ext"
 │       │
 │       └─ NO → Is it specific to certain tasks?
 │           │
 │           ├─ YES → Use description: "task description"
 │           │
 │           └─ NO → Probably doesn't belong in rules
 │                   Consider docs/ or README
```

## Complete Examples

### Example 1: Always Applied (Core Project Info)

**Filename**: `.cursor/rules/core.mdc`

```markdown
---
alwaysApply: true
---
# Project Core

## Structure

**Entry**: [main.py](mdc:src/main.py) | **Config**: [settings.py](mdc:src/settings.py)
**Apps**: auth, api, worker

## Commands

- Run: `task run`
- Test: `task test`
- Build: `task build`

## Tools

- Use `bun` instead of npm
- Use `fd` instead of find
- Format: `task fmt`
```

**Why this works**:
- Universal (applies to all tasks)
- Minimal (16 lines)
- Provides orientation without detail
- Links to authoritative files

**Line count**: 16 lines ✓

### Example 2: File-Type Specific (Python Conventions)

**Filename**: `.cursor/rules/python.mdc`

```markdown
---
globs: *.py,*.pyi
---
# Python Conventions

## Script Dependencies

Use `uv run` with inline dependencies:
```python
# /// script
# dependencies = ["requests", "pandas==2.0.0"]
# ///
```

See [example.py](mdc:scripts/example.py:1-6)

## Formatting

- Use `ruff format` (not black)
- Run on save or before commit
- Config: [ruff.toml](mdc:ruff.toml)

## Type Hints

Required for all public functions (see [api.py](mdc:src/api.py:45))
```

**Why this works**:
- Only loads when editing Python files
- Specific to Python conventions
- File references stay accurate
- Respects glob pattern with comma separator

**Line count**: 18 lines ✓

### Example 3: Task-Specific (Database Migrations)

**Filename**: `.cursor/rules/database-migrations.mdc`

```markdown
---
description: Database migration procedures, rollback steps, and safety checks
---
# Database Migrations

## Creating Migrations

1. Generate migration: `task db:migrate:create <name>`
2. Review SQL in `migrations/<timestamp>_<name>.sql`
3. Test locally: `task db:migrate:up`
4. Verify schema: `task db:schema:dump`

## Rollback Procedure

If migration fails in production:

1. Check current version: `task db:version`
2. Rollback: `task db:migrate:down`
3. Verify: `task db:schema:dump`
4. Alert team via #db-changes

## Safety Checks

**Before merging migration PR**:
- [ ] Migration is idempotent
- [ ] Down migration tested
- [ ] No data loss in down migration
- [ ] Indexes created CONCURRENTLY (Postgres)
- [ ] Large tables use batching

**Production deployment**:
- Run during low-traffic window
- Monitor query performance for 15min
- Keep rollback ready

## Common Patterns

**Add nullable column** (safe):
```sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
```

**Add non-null column** (requires backfill):
See [migrations/backfill-pattern.sql](mdc:migrations/examples/backfill-pattern.sql)
```

**Why this works**:
- Description clearly states when to load
- Contains detailed procedures (not appropriate for alwaysApply)
- Provides checklists and safety guidance
- Links to example patterns

**Line count**: 47 lines ✓ (OK for description-based rules)

### Example 4: File-Type Specific (TypeScript + React)

**Filename**: `.cursor/rules/react.mdc`

```markdown
---
globs: *.tsx,*.jsx
---
# React Conventions

## Component Structure

Prefer server components by default. See [Button.tsx](mdc:app/components/Button.tsx:1)

Use client components only when needed:
- Event handlers
- Browser APIs
- State/effects

## Patterns

- Props interfaces: `ButtonProps` (PascalCase + Props suffix)
- Server components: async functions
- Client components: `'use client'` directive at top

## Styling

Use Tailwind classes. See [tailwind.config.ts](mdc:tailwind.config.ts)
```

**Why this works**:
- Auto-attaches for React files (.tsx, .jsx)
- Framework-specific patterns
- Brief and focused (17 lines)
- Multiple extensions in glob

**Line count**: 17 lines ✓

## File References

Reference project files using `mdc:` protocol:

```markdown
[filename](mdc:path/to/file)           # Link to file
[config.ts](mdc:config.ts:45)          # Link to specific line
[setup](mdc:src/setup.ts:10-25)        # Link to line range
```

**Paths**: Relative to workspace root, not to the .mdc file location.

**Why references over snippets**:
- Snippets become stale as code changes
- References point to source of truth
- Agent can read current version
- Reduces duplication

## Best Practices

### 1. Less is More for alwaysApply

**Target**: <50 lines total across all alwaysApply files

**Why**: alwaysApply rules compete with system prompts for the instruction budget. Every line costs context space in EVERY conversation.

**Guideline**: If you have 3 alwaysApply files averaging 15 lines each (45 total), you're at capacity. Don't add more.

### 2. Universal Applicability Only

**alwaysApply rules should apply to ALL tasks**. If a rule only matters for some tasks:
- Use `description: "..."` for task-specific rules
- Use `globs: "*.ext"` for file-specific rules

**Test**: "Would this help someone debugging a bug?" "Would this help someone adding a feature?" "Would this help someone writing tests?"

If not all YES, don't use alwaysApply.

### 3. Progressive Disclosure

Keep .mdc rules lean by linking to detailed docs:

```markdown
---
alwaysApply: true
---
# Core

## Deployment

For deployment procedures, see [docs/deployment.md](mdc:docs/deployment.md)
Quick deploy: `task deploy:staging`
```

Let description-based rules or docs/ contain the details.

### 4. Pointers Over Copies

**Good** (points to source of truth):
```markdown
See [auth.ts](mdc:src/auth.ts:20-35) for the JWT validation pattern.
```

**Bad** (copies code that will become stale):
```markdown
JWT validation pattern:
```typescript
function validateJWT(token: string) {
  // 20 lines of code that will become outdated
}
```
```

### 5. Descriptive description Strings

**Good descriptions** (clear trigger conditions):
```yaml
description: Database migration procedures and rollback steps
description: CI/CD pipeline configuration and troubleshooting
description: AWS infrastructure deployment with Terraform
```

**Bad descriptions** (vague):
```yaml
description: Database stuff
description: How to deploy
description: Terraform files
```

## Anti-Patterns

### ❌ Don't Use alwaysApply for Style Guides

**Bad**:
```markdown
---
alwaysApply: true
---
# Python Style

Use 4 spaces for indentation.
Functions should use snake_case.
Classes should use PascalCase.
[... 50 more style rules ...]
```

**Why**: Wastes instruction budget on formatting rules. Use linters (ruff, prettier, gofumpt) instead.

**Good**: Configure linters and mention them briefly:
```markdown
---
alwaysApply: true
---
# Python

Format: `ruff format` (config: [ruff.toml](mdc:ruff.toml))
```

### ❌ Don't Stuff alwaysApply Rules

**Bad**: Trying to fit everything into one alwaysApply file with 100+ lines.

**Why**: Degrades instruction-following across ALL conversations. LLMs have finite attention.

**Good**: Keep alwaysApply minimal (<30 lines). Move details to description or docs/.

### ❌ Don't Duplicate Code

**Bad**: Copying example code into rules.

**Why**: Code changes, rules become stale, creates maintenance burden.

**Good**: Link to examples with `mdc:` references.

### ❌ Don't Auto-Generate Without Review

**Bad**: Running a script that generates 20 .mdc files from docstrings.

**Why**: Rules are high-leverage (affect every conversation). Quality > quantity.

**Good**: Manually craft rules. Be intentional about what goes in each file.

### ❌ Don't Use globs for Universal Patterns

**Bad**:
```yaml
---
globs: *.py
---
# Always use git commit messages in conventional format
```

**Why**: Conventional commits apply to ALL files, not just Python files.

**Good**: Use alwaysApply for universal patterns:
```yaml
---
alwaysApply: true
---
# Commits

Follow <https://www.conventionalcommits.org/>: `<type>: <description>`
```

## Integration with Progressive Disclosure

.mdc rules can link to deeper documentation:

```markdown
---
alwaysApply: true
---
# Testing

Run: `task test`

For integration test patterns, see [testing guide](mdc:docs/testing.md)
```

or

```markdown
---
description: Testing patterns and integration test setup
---
# Testing Guide

[Detailed testing documentation...]
```

**Pattern**: alwaysApply gives quick reference, description rules or docs/ provide depth.

## Practical Guidelines

### Starting a New Project

1. Create `core.mdc` with alwaysApply (project structure, commands)
2. Add language-specific rules with globs (python.mdc, typescript.mdc)
3. Add description-based rules as needs emerge (testing.mdc, deployment.mdc)

**Total budget check**: All alwaysApply files combined should be <50 lines.

### Migrating Existing AGENTS.md

If AGENTS.md is >60 lines, split into:

1. **core.mdc** (alwaysApply): Essential project info (<30 lines)
2. **Language .mdc** (globs): Per-language conventions (<20 lines each)
3. **Task .mdc** (description): Complex workflows (30-50 lines each)

### Deciding Frontmatter Type

**Quick decision matrix**:

| Content Type | Frontmatter | File Limit |
|-------------|-------------|-----------|
| Project overview, commands, structure | alwaysApply: true | <30 lines |
| Language/framework conventions | globs: "*.ext" | 15-25 lines |
| Deployment, migrations, CI/CD | description: "..." | 30-50+ lines |

**When in doubt**: Use description. It's safer (doesn't consume budget until needed).

## References

Based on:
- **HumanLayer best practices**: [Writing a Good CLAUDE.md / AGENTS.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- **agents.md specification**: [agents.md](https://agents.md/) - Universal format for AI coding agents
- **Cursor documentation**: Frontmatter types and loading behavior

Key research insight: Frontier LLMs can follow ~150-200 instructions consistently, and many harnesses/tools consume a chunk of that via system prompts and policies. Budget wisely.
