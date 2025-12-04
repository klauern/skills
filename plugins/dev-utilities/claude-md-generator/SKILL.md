---
name: claude-md-generator
description: Generate high-quality AGENTS.md files for projects following agents.md spec and humanlayer.dev best practices. Creates lean, focused documentation with WHAT/WHY/HOW structure and progressive disclosure.
version: 1.0.0
author: klauern
---

# AGENTS.md Generator

## Overview

This skill helps generate effective project rules for AI coding agents using either:
- **Single file**: AGENTS.md (30-60 lines) with CLAUDE.md symlink for Claude Code compatibility
- **Multiple files**: `.cursor/rules/` (4-8 files, 10-30 lines each)

Both patterns follow the agents.md specification and research-backed best practices from HumanLayer's guide. Creates lean, focused documentation that helps AI assistants understand your codebase without overwhelming the context window.

## Key Principles

**LLMs are stateless.** Project rules go into every conversation, so they must be:
- **Lean**: AGENTS.md <60 lines OR .cursor/rules/ total <200 lines
- **Universal**: Applicable to all tasks, not specific scenarios
- **Structured**: WHAT (tech/architecture), WHY (purpose), HOW (workflows)
- **Progressive**: Link to detailed docs, don't inline everything
- **Standard**: Follow agents.md spec (standard Markdown, no mandatory fields)

## Quick Start

### Slash Command

- **`/generate-claude-md`**: Interactive wizard to create AGENTS.md (with CLAUDE.md symlink) - see [`../commands/generate-claude-md.md`](../commands/generate-claude-md.md)

### Core Documentation

- **[Guidelines](guidelines.md)** - Best practices and what to avoid
- **[Template](template.md)** - Starting template with examples
- **[Cursor Rules Pattern](cursor-rules-pattern.md)** - .cursor/rules/ multi-file approach
- **[Progressive Disclosure](progressive-disclosure.md)** - How to structure supporting docs

## When to Use This Skill

Use this skill when:

- Setting up a new project that will use AI coding assistants (Claude Code, Cursor, etc.)
- Improving an existing CLAUDE.md or AGENTS.md that's too long or unfocused
- User asks to "create project rules", "setup AGENTS.md", or "setup Claude documentation"
- Converting single AGENTS.md to .cursor/rules/ (or vice versa)
- Converting legacy CLAUDE.md to standards-compliant AGENTS.md
- Multi-technology projects that benefit from domain-specific rule files

## Workflow Overview

### Interactive Generation Process

1. **Choose pattern** → Single AGENTS.md OR .cursor/rules/ (multi-file)
2. **Analyze codebase** → Detect project type, tech stack, technology domains
3. **Ask key questions** → Purpose, monorepo structure, special workflows
4. **Generate files** → AGENTS.md (single) OR .cursor/rules/*.md (multi)
5. **Create symlinks** → CLAUDE.md → AGENTS.md for Claude Code compatibility
6. **Suggest progressive disclosure** → Identify topics for separate docs

### Quality Checks

**Single AGENTS.md**:
- Line count (target <60, max 300)
- Universal applicability (no task-specific content)
- No code snippets (file:line references only)
- Follows agents.md spec (standard Markdown)
- CLAUDE.md symlinked to AGENTS.md

**.cursor/rules/**:
- Each file 10-30 lines
- Total all files <200 lines
- No duplicate content across files
- Cross-references between related files
- AGENTS.md → core.md, CLAUDE.md → AGENTS.md

**See [guidelines.md](guidelines.md) and [cursor-rules-pattern.md](cursor-rules-pattern.md) for detailed criteria.**

## Anti-Patterns to Avoid

**DON'T use AGENTS.md for:**
- ❌ Style guides (use linters/formatters instead)
- ❌ Database schemas (use progressive disclosure)
- ❌ Code snippets (use file:line references)
- ❌ Task-specific instructions (keep universal)
- ❌ Auto-generation without review (manual crafting required)
- ❌ Making AGENTS.md a symlink to CLAUDE.md (reverse is correct)

**See [guidelines.md](guidelines.md) for complete anti-patterns list.**

## Sub-Agent Strategy

### Use Haiku 4.5 for

- Quick codebase scanning and tech stack detection
- File structure analysis
- Simple template substitution

### Use Sonnet 4.5 for

- Architectural understanding and explanation
- Identifying what content belongs in progressive disclosure
- Crafting clear, concise WHAT/WHY/HOW sections
- Quality review and refinement

## Quick Template

```markdown
# AGENTS.md

## What This Is

[One sentence: project purpose and type]

**Tech Stack**: [key frameworks/languages]
**Architecture**: [monorepo structure OR single app description]

## Why It Exists

[2-3 sentences: business/technical purpose]

## How to Work With It

### Running Tests
[one-liner or file reference]

### Building
[one-liner or file reference]

### Key Conventions
- [Tool preferences: bun vs npm, etc.]
- [Critical workflow notes]

### Deep Dives
- [Link to detailed docs for complex topics]
```

**Don't forget**: `ln -s AGENTS.md CLAUDE.md` for Claude Code compatibility

**For complete template with examples**, see [`template.md`](template.md)

**For progressive disclosure patterns**, see [`progressive-disclosure.md`](progressive-disclosure.md)

## Documentation Index

### Core Guides

- **[guidelines.md](guidelines.md)** - Best practices, anti-patterns, quality criteria for CLAUDE.md
- **[template.md](template.md)** - Complete CLAUDE.md template with real-world examples
- **[cursor-rules-pattern.md](cursor-rules-pattern.md)** - .cursor/rules/ multi-file pattern guide
- **[progressive-disclosure.md](progressive-disclosure.md)** - How to structure supporting docs

### Command Documentation

- **[generate-claude-md.md](../commands/generate-claude-md.md)** - Interactive generation command

## References

Based on:
- **AGENTS.md specification**: [agents.md](https://agents.md/) - Universal format for AI coding agents
- **HumanLayer best practices**: [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

Key research insight: Frontier LLMs can follow ~150-200 instructions consistently. Claude Code's system prompt uses ~50, leaving ~100-150 for your project rules.

**Symlink direction**: Always `CLAUDE.md → AGENTS.md` (AGENTS.md is primary per spec)
