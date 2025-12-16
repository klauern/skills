# AGENTS.md Specification Reference

## Overview

[AGENTS.md](https://agents.md/) is an open specification for a universal configuration file format that works across all AI coding assistants. It provides a standard way to communicate project context, conventions, and workflows to AI tools.

## Specification Highlights

### Core Principles

1. **Tool-Agnostic**: Works with Claude Code, Cursor, Windsurf, Cline, RooCode, GitHub Copilot, and other AI coding tools
2. **Standard Markdown**: No special syntax, frontmatter, or required fields
3. **Human-Readable**: Designed to be read and understood by developers, not just AI agents
4. **Optional**: Entirely opt-in; tools work without AGENTS.md but benefit from it when present

### File Format

- **Name**: `AGENTS.md` (case-sensitive)
- **Location**: Project root directory
- **Format**: Standard Markdown following CommonMark specification
- **Encoding**: UTF-8

### Content Structure (Recommended)

While no fields are mandatory, the specification recommends a WHAT/WHY/HOW structure:

```markdown
# AGENTS.md

## What This Is

[Brief project description - 1-2 sentences]

**Tech Stack**: [Key technologies]
**Architecture**: [System structure]

## Why It Exists

[Project purpose and goals - 2-3 sentences]

## How to Work With It

### [Workflow 1: e.g., Running Tests]
[Commands or references]

### [Workflow 2: e.g., Building]
[Commands or references]

### Key Conventions
- [Important patterns and preferences]
```

## Tool Compatibility via Symlinks

Many AI tools have their own legacy configuration file names. To maintain compatibility while adopting AGENTS.md as the source of truth, create symlinks:

| Tool | Legacy File | Symlink Command |
|------|-------------|-----------------|
| Claude Code | `CLAUDE.md` | `ln -s AGENTS.md CLAUDE.md` |
| Windsurf | `.windsurfrules` | `ln -s AGENTS.md .windsurfrules` |
| Cline | `.clinerules` | `ln -s AGENTS.md .clinerules` |
| Gemini CLI | `GEMINI.md` | `ln -s AGENTS.md GEMINI.md` |
| Replit | `.replit.md` | `ln -s AGENTS.md .replit.md` |

**Symlink Direction**: Always symlink FROM the tool-specific file TO AGENTS.md (AGENTS.md is the real file, others point to it).

## Best Practices

### Length Guidelines

- **Target**: 30-60 lines for simple projects
- **Maximum**: 300 lines (beyond this, use progressive disclosure)
- **Research-backed**: LLMs can follow ~150-200 instructions; keep within budget

### Content Guidelines

**DO Include**:
- ✅ Project purpose and architecture overview
- ✅ Tech stack and key frameworks
- ✅ Common workflows (test, build, deploy)
- ✅ Tool preferences (e.g., "use bun instead of npm")
- ✅ File:line references to code examples
- ✅ Links to detailed documentation

**DON'T Include**:
- ❌ Style guides (use linters instead)
- ❌ Code snippets (use file references)
- ❌ Task-specific instructions (keep universal)
- ❌ Database schemas (link to docs)
- ❌ Auto-generated content (manually craft for quality)

### Progressive Disclosure

For complex topics, create separate documentation files and reference them:

```
project-root/
├── AGENTS.md              (lean, universal guidance)
└── docs/
    ├── architecture.md    (detailed system design)
    ├── testing.md         (test patterns)
    ├── database.md        (schema and migrations)
    └── deployment.md      (deploy procedures)
```

Reference in AGENTS.md:

```markdown
## Deep Dives

- **Architecture**: See [docs/architecture.md](docs/architecture.md) for service map
- **Testing**: See [docs/testing.md](docs/testing.md) for integration test setup
```

## Migration from Tool-Specific Files

If you have existing configuration files (CLAUDE.md, .cursorrules, etc.):

1. Rename or move content to `AGENTS.md`
2. Create symlink from old filename to `AGENTS.md`
3. Remove tool-specific syntax if any
4. Ensure content is tool-agnostic

Example migration (Claude Code):

```bash
mv CLAUDE.md AGENTS.md
ln -s AGENTS.md CLAUDE.md
```

## Specification Resources

- **Official Website**: [agents.md](https://agents.md/)
- **GitHub Repository**: [github.com/agents-md/agents.md](https://github.com/agents-md/agents.md)
- **Supported Tools**: Listed on [agents.md/#supported-tools](https://agents.md/#supported-tools)

## Relationship to Cursor .mdc Format

AGENTS.md and Cursor's `.cursor/rules/*.mdc` format serve different purposes and can coexist:

- **AGENTS.md**: Universal baseline, cross-tool compatibility, high-level guidance
- **.cursor/rules/*.mdc**: Cursor-specific intelligent loading with frontmatter (alwaysApply/globs/description)

**Recommended Approach**:
- Use AGENTS.md for universal project context
- Use .cursor/rules/ for tech-specific guidance with intelligent loading
- Keep both lean by linking to progressive disclosure docs

## Community and Adoption

The agents.md specification is supported by:
- Claude Code (Anthropic)
- Cursor (Anysphere)
- Windsurf (Codeium)
- Cline (community tool)
- RooCode (community tool)
- Many other AI coding assistants

Check [agents.md](https://agents.md/) for the latest list of supported tools.
