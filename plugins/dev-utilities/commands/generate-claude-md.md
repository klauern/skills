---
allowed-tools: Glob, Grep, Read, Write, Bash, AskUserQuestion
description: Interactive wizard to generate high-quality AGENTS.md or .cursor/rules/ following agents.md and humanlayer.dev best practices
---

## Instructions

Generate lean, effective project rules using either:
- **Single file**: AGENTS.md (30-60 lines) with CLAUDE.md symlink for compatibility
- **Multiple files**: `.cursor/rules/` (4-8 files, 10-30 lines each)

Both patterns follow the WHAT/WHY/HOW structure, agents.md specification, and use progressive disclosure for deep topics.

**Important**: Always create AGENTS.md as the primary file (per agents.md spec) with CLAUDE.md symlinked to it.

### Step 0: Choose Pattern

1. Check for existing setup:
   - Look for existing `.cursor/rules/` directory
   - Look for existing `AGENTS.md` file
   - Look for existing `CLAUDE.md` file (legacy)

2. Ask user which pattern to use (via AskUserQuestion):
   - **Option 1: Single AGENTS.md** - One file (30-60 lines), simpler projects
   - **Option 2: .cursor/rules/** - Multiple files (4-8 files), multi-tech stack

   If `.cursor/rules/` exists, default to that pattern.
   If `AGENTS.md` or `CLAUDE.md` exists, default to single file.

### Step 1: Analyze the Codebase

1. Detect project type and tech stack:
   - Run `ls -la` to see root directory structure
   - Look for package.json, requirements.txt, go.mod, Cargo.toml, etc.
   - Check for monorepo indicators (apps/, packages/, workspaces, etc.)
   - Identify primary languages and frameworks
   - Count distinct technology domains (React, TypeScript, Python, testing, API, etc.)

2. Understand architecture:
   - For monorepos: Map out apps and packages
   - For single apps: Identify main components
   - For microservices: List services and their purposes

3. Find existing documentation:
   - Search for existing CLAUDE.md, AGENTS.md, README.md
   - Look for docs/ directory
   - Check for .claude/ or agent_docs/ directories

### Step 2: Gather Key Information

Use AskUserQuestion to clarify:

1. **Project purpose**: What does this project do? (1-2 sentences)
2. **Key workflows**: How do you typically run tests? Build? Deploy?
3. **Tool preferences**: Any specific tools to prefer? (bun vs npm, uv vs pip, etc.)
4. **Special conventions**: Any critical patterns or conventions?
5. **Progressive disclosure needs**: Any complex topics that need separate docs?

### Step 3A: Generate Single AGENTS.md (if chosen)

Create an AGENTS.md file with this structure:

```markdown
# AGENTS.md

## What This Is

[One sentence: project purpose]

**Tech Stack**: [detected languages, frameworks]
**Architecture**: [monorepo structure OR single app description]

## Why It Exists

[User's answer about purpose and key architectural decisions]

## How to Work With It

### Prerequisites
[Installation if non-trivial, otherwise skip]

### Running Locally
[Commands from user or detected from package.json/Makefile]

### Testing
[Test commands]

### Building
[Build commands]

### Key Conventions
- [Tool preferences from user]
- [Critical patterns with file:line references]
- [Lint/format commands if not automated]

### Deep Dives
[Links to progressive disclosure docs if identified]
```

**Quality checks**:
- [ ] Total length < 60 lines (ideal) or < 300 lines (max)
- [ ] Uses file:line references, not code snippets
- [ ] No style guide content (recommend using linters)
- [ ] No task-specific instructions
- [ ] All content universally applicable
- [ ] Follows agents.md specification (standard Markdown, no mandatory fields)

Then create CLAUDE.md symlink for Claude Code compatibility:
```bash
ln -s AGENTS.md CLAUDE.md
```

Skip to Step 5.

### Step 3B: Generate .cursor/rules/ (if chosen)

Create `.cursor/rules/` directory and generate files based on detected domains:

**Always create**:
1. **`core.md`** (20-30 lines) - Project overview, purpose, workflow

**Create based on tech stack**:
2. **`react.md`** (15-20 lines) - If React detected
3. **`typescript.md`** (15-20 lines) - If TypeScript detected
4. **`python.md`** (15-20 lines) - If Python detected
5. **`go.md`** (15-20 lines) - If Go detected
6. **`testing.md`** (15-25 lines) - Always include if tests exist
7. **`api.md`** (15-20 lines) - If API routes/endpoints detected
8. **`build.md`** (15-20 lines) - If complex build process

**Budget check**:
- [ ] Each file 10-30 lines
- [ ] Total all files < 200 lines
- [ ] No duplicate content across files
- [ ] Uses file:line references, not code snippets
- [ ] Cross-references between related files

Use templates from `claude-md-generator/cursor-rules-pattern.md`.

### Step 4: Create Symlinks (for .cursor/rules only)

If using `.cursor/rules/`, create compatibility symlinks:

```bash
ln -s .cursor/rules/core.md AGENTS.md
ln -s AGENTS.md CLAUDE.md
```

This ensures:
- AGENTS.md → core.md (agents.md spec compliance)
- CLAUDE.md → AGENTS.md (Claude Code compatibility)

### Step 5: Suggest Progressive Disclosure

If any topics would make CLAUDE.md too long (>60 lines), suggest creating:

```
docs/
├── architecture.md    # If complex system with >3 services/apps
├── testing.md        # If testing needs >5 lines of explanation
├── database.md       # If database conventions are extensive
├── deployment.md     # If deployment is multi-step
└── auth.md          # If auth implementation is complex
```

Provide brief templates for suggested files.

## Important Guidelines

### DO:
- ✅ Keep CLAUDE.md under 60 lines if possible
- ✅ Use WHAT/WHY/HOW structure
- ✅ Reference code with file:line format
- ✅ Link to progressive disclosure for details
- ✅ Include tool preferences explicitly
- ✅ Focus on universal workflows (build, test, run)

### DON'T:
- ❌ Include style guides (recommend linters instead)
- ❌ Add code snippets (use file:line references)
- ❌ Include task-specific instructions
- ❌ Auto-generate without user review
- ❌ Exceed 300 lines total

## Example Output

### For Single AGENTS.md Pattern

Show the user:
1. Generated AGENTS.md content
2. Command to create CLAUDE.md symlink
3. Suggested progressive disclosure files (if any)
4. Line count and quality assessment

Example:
```
✓ Generated AGENTS.md (45 lines)
✓ Run: ln -s AGENTS.md CLAUDE.md

Suggested progressive disclosure:
- docs/architecture.md (monorepo structure details)
- docs/testing.md (integration test patterns)

Quality: ✓ Under 60 lines, universal content, no code snippets, agents.md compliant
```

### For .cursor/rules/ Pattern

Show the user:
1. List of generated files with line counts
2. Total line count across all files
3. Commands to create symlinks
4. Suggested progressive disclosure files (if any)
5. Quality assessment

Example:
```
✓ Created .cursor/rules/ directory

Generated files:
- core.md (25 lines) - Project overview and workflow
- react.md (18 lines) - React patterns
- typescript.md (15 lines) - TypeScript conventions
- testing.md (20 lines) - Testing patterns
- api.md (17 lines) - API conventions

Total: 95 lines across 5 files

Compatibility symlinks:
ln -s .cursor/rules/core.md AGENTS.md
ln -s AGENTS.md CLAUDE.md

Suggested progressive disclosure:
- docs/architecture.md (detailed service map)
- docs/testing.md (integration test examples)

Quality: ✓ Under 200 lines total, focused files, cross-referenced, agents.md compliant
```

## Reference

Based on:
- **AGENTS.md spec**: https://agents.md/ - Universal format for AI coding agents
- **HumanLayer guide**: https://www.humanlayer.dev/blog/writing-a-good-claude-md - Best practices for lean documentation

Key insights:
- LLMs can follow ~150-200 instructions
- Claude Code uses ~50, leaving ~100-150 for your rules
- Single AGENTS.md: Keep under 60 lines
- .cursor/rules/: Keep total under 200 lines
- Both patterns use progressive disclosure for deep topics
- AGENTS.md is standard Markdown with no mandatory fields
- Always symlink CLAUDE.md → AGENTS.md for Claude Code compatibility
