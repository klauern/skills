---
name: rule-generator
description: Generate AI coding assistant rules (AGENTS.md, .cursor/rules/*.mdc). Use when user asks to create project rules, setup AGENTS.md, or add Cursor rules.
version: 2.0.0
author: klauern
---

# Rule Generator

Generate rules for AI coding assistants using two formats:
- **AGENTS.md** (30-60 lines) with `CLAUDE.md` symlink - Universal, simple
- **.cursor/rules/*.mdc** (4-8 files) with frontmatter - Tech-specific, intelligent loading

## Quick Start

**Command**: `/generate-rules` - Interactive wizard for rule generation

**Migration**: `/agents-md` - Convert legacy CLAUDE.md to AGENTS.md

## Key Principles

1. **LLMs are stateless** - Rules go into every conversation
2. **Instruction budget** - Target <60 lines (AGENTS.md) or <200 lines (.cursor/rules/)
3. **Universal content** - Task-specific content gets ignored
4. **Progressive disclosure** - Link to docs/, don't inline everything

## Documentation

- [Guidelines](references/guidelines.md) - Best practices and anti-patterns
- [Templates](references/templates.md) - Starting templates with examples
- [Progressive Disclosure](references/progressive-disclosure.md) - How to structure docs/

### Format Specs
- [Cursor Format](references/format-specs/cursor-format.md) - .mdc frontmatter and patterns
- [AGENTS.md Spec](references/format-specs/agents-md-spec.md) - Universal specification
- [Claude Code](references/format-specs/claude-code.md) - Claude Code integration

## When to Use

- Setting up new project rules
- Improving existing AGENTS.md/CLAUDE.md that's too long
- Converting single AGENTS.md to .cursor/rules/ (or vice versa)
- Adding individual .mdc rules to existing setup

## Workflow Summary

### AGENTS.md Generation
1. Analyze codebase → Detect tech stack
2. Ask key questions → Purpose, workflows
3. Generate AGENTS.md → WHAT/WHY/HOW (30-60 lines)
4. Create symlink → `ln -s AGENTS.md CLAUDE.md`
5. Suggest progressive disclosure → docs/ for complex topics

### .cursor/rules/ Generation
1. Analyze codebase → Detect tech stack, domains
2. Generate .mdc files → core.mdc, language.mdc, task.mdc
3. Add frontmatter → alwaysApply, globs, or description
4. Create symlink → `CLAUDE.md → AGENTS.md`

## Model Strategy

| Task | Model |
|------|-------|
| Codebase scanning, file detection | Haiku |
| Architecture understanding, content crafting | Sonnet |

## Quick Template

```markdown
# AGENTS.md

## What This Is
[One sentence] **Tech**: [stack] **Architecture**: [type]

## Why It Exists
[2-3 sentences: purpose]

## How to Work With It
### Commands
- Run: `[cmd]` | Test: `[cmd]` | Build: `[cmd]`

### Key Conventions
- [Tool preferences, file:line references]

### Deep Dives
- [Topic]: docs/[file].md
```

**Symlink**: `ln -s AGENTS.md CLAUDE.md`
