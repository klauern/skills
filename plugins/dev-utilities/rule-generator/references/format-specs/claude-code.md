# Claude Code Format Specification

## Overview

Claude Code is Anthropic's official CLI tool for AI-assisted coding. It supports multiple configuration formats for maximum flexibility and cross-tool compatibility.

## Supported Configuration Files

### Primary: AGENTS.md

Claude Code follows the [agents.md specification](https://agents.md/) and recognizes `AGENTS.md` as the primary, tool-agnostic configuration file.

**Location**: `AGENTS.md` in project root

**Format**: Standard Markdown with no mandatory fields or special syntax

**Best Practices**:
- Keep under 60 lines (ideal) or 300 lines (maximum)
- Use WHAT/WHY/HOW structure
- Reference code with `file:line` format, not code snippets
- Link to progressive disclosure docs for complex topics

### Backwards Compatibility: CLAUDE.md

For backwards compatibility with earlier versions, Claude Code also reads `CLAUDE.md`.

**Recommended Setup**: Create a symlink from `CLAUDE.md` to `AGENTS.md`

```bash
ln -s AGENTS.md CLAUDE.md
```

**Important**: The symlink direction should always be `CLAUDE.md → AGENTS.md` (AGENTS.md is the primary file per the agents.md spec).

### Cursor Integration: .cursor/rules/

Claude Code automatically reads `.cursor/rules/*.mdc` files, providing seamless integration with Cursor configurations.

**Location**: `.cursor/rules/` directory in project root

**Format**: Markdown files (`.md` or `.mdc`) with optional YAML frontmatter

**Frontmatter Types**:
- `alwaysApply: true` - Always loaded (keep total <50 lines across all alwaysApply files)
- `globs: "*.ext"` - Auto-attach to specific file types
- `description: "..."` - Load on-demand for specific tasks

See [cursor-mdc.md](cursor-mdc.md) for detailed frontmatter documentation.

## Loading Behavior

Claude Code loads configuration files in this order:

1. **Global user config**: `~/.claude/CLAUDE.md` or `~/.claude/AGENTS.md` (if present)
2. **Project AGENTS.md**: `AGENTS.md` in project root (or `CLAUDE.md` if no AGENTS.md)
3. **Cursor rules**: All `.cursor/rules/*.mdc` files with `alwaysApply: true`
4. **File-specific rules**: `.cursor/rules/*.mdc` files matching current file's glob patterns
5. **Task-specific rules**: `.cursor/rules/*.mdc` files with relevant descriptions (loaded on-demand)

## Recommendation

For new projects:
1. Create `AGENTS.md` as the primary configuration (universal, tool-agnostic)
2. Symlink `CLAUDE.md → AGENTS.md` for backwards compatibility
3. Optionally create `.cursor/rules/*.mdc` for tech-specific guidance with intelligent loading

This approach provides:
- ✅ Cross-tool compatibility (works with Cursor, Windsurf, Cline, etc. via AGENTS.md)
- ✅ Claude Code backwards compatibility (via CLAUDE.md symlink)
- ✅ Intelligent loading (via Cursor .mdc frontmatter)
- ✅ Single source of truth (AGENTS.md)

## Progressive Disclosure

For complex topics that would make AGENTS.md too long, create separate documentation files:

```
project-root/
├── AGENTS.md              (30-60 lines, universal)
├── CLAUDE.md → AGENTS.md  (symlink for compatibility)
├── .cursor/
│   └── rules/
│       ├── core.mdc       (alwaysApply: true)
│       └── *.mdc          (tech-specific rules)
└── docs/
    ├── architecture.md    (detailed system design)
    ├── testing.md         (test patterns and examples)
    └── [topic].md         (other deep dives)
```

Reference these docs in AGENTS.md with brief descriptions:

```markdown
## Deep Dives

For detailed information on specific topics:

- **Architecture**: See [docs/architecture.md](docs/architecture.md) - Service map and communication patterns
- **Testing**: See [docs/testing.md](docs/testing.md) - Integration test setup and patterns
```

## References

- [agents.md specification](https://agents.md/) - Universal format for AI coding agents
- [HumanLayer: Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) - Best practices
- [Cursor .mdc format](cursor-mdc.md) - Frontmatter documentation
- [Claude Code documentation](https://docs.anthropic.com/claude-code) - Official docs
