---
name: rule-generator
description: Generate AI coding assistant rules for Cursor, Claude Code, and other tools. Creates AGENTS.md, .cursor/rules/*.mdc, and individual rules following agents.md spec and HumanLayer best practices.
version: 2.0.0
author: klauern
---

# Rule Generator

## Overview

This skill helps generate effective project rules for AI coding agents using:
- **Single file**: AGENTS.md (30-60 lines) with CLAUDE.md symlink
- **Multiple files**: `.cursor/rules/*.mdc` (4-8 files) with frontmatter
- **Individual rule**: Single `.cursor/rules/*.mdc` file

Cursor .mdc format uses YAML frontmatter for intelligent rule loading (alwaysApply, description, globs). All patterns follow the agents.md specification and research-backed best practices from HumanLayer's guide.

## Supported Tools

### Currently Supported
- **Cursor** - `.cursor/rules/*.mdc` with YAML frontmatter (alwaysApply, globs, description)
- **Claude Code** - `AGENTS.md` with `CLAUDE.md` symlink for backwards compatibility

### Cross-Tool Compatibility
- AGENTS.md serves as the universal source of truth following the [agents.md specification](https://agents.md/)
- Tool-specific symlinks created as needed (`CLAUDE.md → AGENTS.md`)
- Progressive disclosure patterns work across all tools
- Cursor automatically reads `.cursor/rules/` files, Claude Code supports both AGENTS.md and .cursor/rules/

### Future Support (Planned)
- **Windsurf** - `.windsurfrules` file
- **Cline** - `.clinerules` or `.clinerules/*.md` files
- **RooCode** - `.roomodes` + `.roo/rules-{mode}/` directories
- **GitHub Copilot** - `.github/copilot-instructions.md` files
- **Replit** - `.replit.md` file

See [references/format-specs/README.md](references/format-specs/README.md) for details on adding support for additional tools.

## Key Principles

**LLMs are stateless.** Project rules go into every conversation, so they must be:
- **Lean**: AGENTS.md <60 lines OR .cursor/rules/ total <200 lines
- **Universal**: Applicable to all tasks, not specific scenarios
- **Structured**: WHAT (tech/architecture), WHY (purpose), HOW (workflows)
- **Progressive**: Link to detailed docs, don't inline everything
- **Standard**: Follow agents.md spec (standard Markdown, no mandatory fields)

## Quick Start

### Slash Commands

- **`/generate-rules`**: Interactive wizard for generating AI coding assistant rules
  - Choose target: AGENTS.md, .cursor/rules/, or individual rule
  - Auto-detects tech stack and existing setup
  - Offers progressive disclosure suggestions

**Note**: `/agents-md` is a separate command for **migration only** (CLAUDE.md to AGENTS.md).

See [`../commands/generate-rules.md`](../commands/generate-rules.md)

### Core Documentation

- **[Guidelines](references/guidelines.md)** - Best practices and what to avoid
- **[Templates](references/templates.md)** - Starting templates with real-world examples
- **[Progressive Disclosure](references/progressive-disclosure.md)** - How to structure supporting docs

### Format Specifications

- **[Cursor .mdc Format](references/format-specs/cursor-mdc.md)** - Frontmatter types and decision tree
- **[Cursor Rules Pattern](references/format-specs/cursor-rules.md)** - .cursor/rules/ multi-file approach
- **[Claude Code Format](references/format-specs/claude-code.md)** - CLAUDE.md symlink and integration
- **[AGENTS.md Spec](references/format-specs/agents-md-spec.md)** - Universal specification reference

## When to Use This Skill

Use this skill when:

- Setting up a new project that will use AI coding assistants (Claude Code, Cursor, etc.)
- Improving an existing CLAUDE.md or AGENTS.md that's too long or unfocused
- User asks to "create project rules", "setup AGENTS.md", "setup Cursor rules", or "add a rule"
- Converting single AGENTS.md to .cursor/rules/ (or vice versa)
- Converting legacy CLAUDE.md to standards-compliant AGENTS.md
- Adding individual .mdc rules to existing setup
- Multi-technology projects that benefit from domain-specific rule files

## Workflow Types

### 1. Full AGENTS.md Generation

Single file at root with CLAUDE.md symlink.

**Use when**: Simple project, unified conventions, want to minimize auto-loaded content

**Process**:
1. Analyze codebase → Detect project type and tech stack
2. Ask key questions → Purpose, workflows, tool preferences
3. Generate AGENTS.md → WHAT/WHY/HOW structure (30-60 lines)
4. Create symlink → `CLAUDE.md → AGENTS.md`
5. Suggest progressive disclosure → Identify topics for separate docs

### 2. Full .cursor/rules/ Generation

Multiple .mdc files with frontmatter for intelligent loading.

**Use when**: Multi-tech stack, domain-specific organization, want granular control

**Process**:
1. Analyze codebase → Detect tech stack and domains
2. Ask key questions → Purpose, workflows, special conventions
3. Generate .mdc files → core.mdc, language.mdc, task.mdc (4-8 files)
4. Add frontmatter → alwaysApply, globs, or description per file
5. Create/verify cross-tool entrypoint → `CLAUDE.md → AGENTS.md` (and optional other compatibility symlinks)
6. Suggest progressive disclosure → Identify topics for separate docs

### 3. Individual .mdc Rule Generation

Single .mdc file with appropriate frontmatter.

**Use when**: Adding to existing setup, task-specific guidance, new domain

**Process**:
1. Ask about rule → Purpose, scope (universal/file-type/task), filename
2. Determine frontmatter → alwaysApply, globs, or description based on scope
3. Generate .mdc file → With correct frontmatter and focused content
4. Quality check → Frontmatter matches scope, appropriate line count

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
- `CLAUDE.md → AGENTS.md` (AGENTS.md remains the cross-tool baseline)

**See [references/guidelines.md](references/guidelines.md) and [references/format-specs/cursor-rules.md](references/format-specs/cursor-rules.md) for detailed criteria.**

## Anti-Patterns to Avoid

**DON'T use AGENTS.md for:**
- ❌ Style guides (use linters/formatters instead)
- ❌ Database schemas (use progressive disclosure)
- ❌ Code snippets (use file:line references)
- ❌ Task-specific instructions (keep universal)
- ❌ Auto-generation without review (manual crafting required)
- ❌ Making AGENTS.md a symlink to CLAUDE.md (reverse is correct)

**See [references/guidelines.md](references/guidelines.md) for complete anti-patterns list.**

## Extensibility Architecture

This skill is designed to support additional AI coding tools without major restructuring.

### Adding New Tool Support

1. Create format spec in `references/format-specs/[tool-name].md`
2. Define:
   - File location(s) and naming convention
   - Format syntax (YAML frontmatter, plain markdown, etc.)
   - Loading behavior (alwaysApply equivalent, globs, task-specific triggers)
   - Symlink strategy for AGENTS.md compatibility
3. Update SKILL.md "Supported Tools" section
4. Update wizard in `generate-rules.md` to offer new format option

### Tool Abstraction Model

All AI coding tools can be mapped to these common concepts:

| Concept | Description | Example (Cursor) | Example (Future: Windsurf) |
|---------|-------------|------------------|----------------------------|
| **Universal rules** | Load for every task | `alwaysApply: true` | `.windsurfrules` (always loaded) |
| **File-type rules** | Load for specific file extensions | `globs: "*.ts"` | Future: file-type triggers |
| **Task-specific rules** | Load on-demand based on context | `description: "..."` | Future: context-aware loading |
| **Source of truth** | Primary reference file | AGENTS.md | AGENTS.md (with symlink) |

All formats should support or symlink to AGENTS.md as the universal baseline.

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

**For complete templates with examples**, see [`references/templates.md`](references/templates.md)

**For progressive disclosure patterns**, see [`references/progressive-disclosure.md`](references/progressive-disclosure.md)

## Documentation Index

### Core Guides

- **[references/guidelines.md](references/guidelines.md)** - Best practices, anti-patterns, quality criteria
- **[references/templates.md](references/templates.md)** - Complete templates with real-world examples
- **[references/progressive-disclosure.md](references/progressive-disclosure.md)** - How to structure supporting docs

### Format Specifications

- **[references/format-specs/cursor-mdc.md](references/format-specs/cursor-mdc.md)** - Cursor .mdc frontmatter format
- **[references/format-specs/cursor-rules.md](references/format-specs/cursor-rules.md)** - .cursor/rules/ multi-file pattern
- **[references/format-specs/claude-code.md](references/format-specs/claude-code.md)** - Claude Code specifics
- **[references/format-specs/agents-md-spec.md](references/format-specs/agents-md-spec.md)** - AGENTS.md specification

### Command Documentation

- **[generate-rules.md](../commands/generate-rules.md)** - Interactive rule generation command
- **[agents-md.md](../commands/agents-md.md)** - Migration-only command (CLAUDE.md to AGENTS.md)

## References

Based on:
- **AGENTS.md specification**: [agents.md](https://agents.md/) - Universal format for AI coding agents
- **HumanLayer best practices**: [Writing a Good CLAUDE.md / AGENTS.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

Key research insight: Frontier LLMs can follow ~150-200 instructions consistently, and many harnesses/tools consume a chunk of that via system prompts and policies.

**Symlink direction**: Always `CLAUDE.md → AGENTS.md` (AGENTS.md is primary per spec)
