---
allowed-tools: Glob, Grep, Read, Write, Bash, AskUserQuestion
description: Interactive wizard to generate AI coding assistant rules (AGENTS.md, .cursor/rules/, individual rules)
---

## Instructions

Primary interactive wizard for generating AI coding assistant rules.

**Note**: `/agents-md` is a separate command for migration only (CLAUDE.md to AGENTS.md).

Generate lean, effective project rules using:
- **Single file**: AGENTS.md (30-60 lines) with CLAUDE.md symlink
- **Multiple files**: `.cursor/rules/*.mdc` (4-8 files) with frontmatter
- **Individual rule**: Single `.cursor/rules/*.mdc` file

All patterns follow WHAT/WHY/HOW structure, agents.md specification, and use progressive disclosure. Cursor .mdc files use YAML frontmatter (alwaysApply, description, globs) for intelligent loading.

**Important**: Always create AGENTS.md as the primary file (per agents.md spec) with CLAUDE.md symlinked to it.

### Step 0: Choose Pattern

1. Check for existing setup:
   - Look for existing `.cursor/rules/` directory
   - Look for existing `AGENTS.md` file
   - Look for existing `CLAUDE.md` file (legacy)

2. Ask user which pattern to use (via AskUserQuestion):
   - **Option 1: Single AGENTS.md** - One file (30-60 lines), simpler projects
   - **Option 2: Full .cursor/rules/ set** - Multiple .mdc files (4-8 files), multi-tech stack
   - **Option 3: Individual .mdc rule** - Add single rule to existing setup

   **Recommendations**:
   - If `.cursor/rules/` exists, offer Options 2 or 3
   - If `AGENTS.md` or `CLAUDE.md` exists, default to Option 1
   - If neither exists and project has <3 tech domains, suggest Option 1
   - If neither exists and project has 3+ tech domains, suggest Option 2

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

Create `.cursor/rules/` directory and generate .mdc files with frontmatter based on detected domains:

**Always create**:
1. **`core.mdc`** (20-30 lines) - Project overview, purpose, workflow
   ```yaml
   ---
   alwaysApply: true
   ---
   ```

**Create based on tech stack** (use globs for language/framework files):
2. **`react.mdc`** (15-20 lines) - If React detected
   ```yaml
   ---
   globs: *.tsx,*.jsx
   ---
   ```

3. **`typescript.mdc`** (15-20 lines) - If TypeScript detected
   ```yaml
   ---
   globs: *.ts,*.tsx
   ---
   ```

4. **`python.mdc`** (15-20 lines) - If Python detected
   ```yaml
   ---
   globs: *.py,*.pyi
   ---
   ```

5. **`go.mdc`** (15-20 lines) - If Go detected
   ```yaml
   ---
   globs: *.go
   ---
   ```

6. **`testing.mdc`** (15-25 lines) - If tests exist
   ```yaml
   ---
   description: Testing patterns and integration test setup
   ---
   ```

7. **`api.mdc`** (15-20 lines) - If API routes/endpoints detected
   ```yaml
   ---
   description: API conventions and HTTP handler patterns
   ---
   ```

8. **`build.mdc`** (15-20 lines) - If complex build process
   ```yaml
   ---
   description: Build system and deployment procedures
   ---
   ```

**Frontmatter Decision Guide**:
- **core.mdc**: Always use `alwaysApply: true` (universal project info)
- **Language-specific** (react, typescript, python, go): Use `globs: "*.ext"`
- **Task-specific** (testing, api, build): Use `description: "..."`

**Budget check**:
- [ ] Each file 10-30 lines (content only, not including frontmatter)
- [ ] Total all files < 200 lines
- [ ] All alwaysApply files combined < 50 lines
- [ ] No duplicate content across files
- [ ] Uses file:line references, not code snippets
- [ ] Cross-references between related files
- [ ] Appropriate frontmatter for each file's purpose

Use templates from `rule-generator/references/templates.md` (Cursor .mdc Templates section).

Skip to Step 4.

### Step 3C: Generate Individual .mdc Rule (if chosen)

Use AskUserQuestion to gather:

1. **Rule purpose**: What should this rule cover?
   Examples: "Python conventions", "Testing patterns", "Deployment procedures", "Database migrations"

2. **Target scope** (helps determine frontmatter):
   - Is this relevant to ALL tasks? → alwaysApply: true
   - Is this specific to file types? → globs: "*.ext"
   - Is this specific to tasks/workflows? → description: "..."

3. **Content outline**: What are the key points to include?

4. **Filename**: Suggest based on purpose (e.g., `python-conventions.mdc`, `deployment.mdc`, `testing.mdc`)

**Frontmatter Decision Logic**:

```
Is this relevant to EVERY task?
  YES → Is it <30 lines?
    YES → Use alwaysApply: true
    NO  → Too long for alwaysApply, use description instead

  NO  → Is it specific to file types?
    YES → Use globs: "*.ext,*.ext2"

    NO  → Is it specific to tasks/workflows?
      YES → Use description: "Clear task description"
```

**Generate .mdc file** with structure:

For **alwaysApply**:
```markdown
---
alwaysApply: true
---
# [Domain] Core

## [Key Section]

[Brief, universally applicable content]
- [Essential commands or patterns]
- [File references]

## [Optional Section]

[More essential info if needed]
```

For **globs**:
```markdown
---
globs: *.ext,*.ext2
---
# [Language/Framework] Conventions

## Style

- Format: `[command]`
- Lint: `[command]`

## Patterns

[File references to examples]

## [Optional Section]

[Additional conventions]
```

For **description**:
```markdown
---
description: [Clear description of when to use this rule]
---
# [Task/Domain] Guide

## [Main Section]

[Detailed guidance for this specific task]

### [Subsection]

[Step-by-step procedures or detailed patterns]

## [Additional Sections as needed]

[More task-specific content]
```

**Quality Checks**:
- [ ] Frontmatter matches content scope
- [ ] alwaysApply files <30 lines
- [ ] globs files 15-25 lines
- [ ] description files 30-50+ lines (can be longer)
- [ ] Uses file references, not code snippets
- [ ] Description is clear and specific (if using description)
- [ ] Glob patterns are correct (if using globs)
- [ ] Content is focused on one domain/task

**Example Output**:

```
✓ Generated .cursor/rules/python-conventions.mdc (18 lines)

Frontmatter: globs: "*.py,*.pyi"
Content: Python tool preferences (uv), type hints, format/lint commands
Auto-attaches when editing Python files

Quality: ✓ File-type specific, clear patterns, file references
```

Skip to Step 5.

### Step 4: Create Symlinks (for .cursor/rules only)

Always keep `AGENTS.md` as the cross-tool entrypoint, and create compatibility symlinks as needed.

```bash
ln -s AGENTS.md CLAUDE.md
```

This ensures:
- CLAUDE.md → AGENTS.md (Claude Code compatibility)

If you want Cursor to load the same content as `AGENTS.md` (single source of truth) and you don't need `.mdc` frontmatter, you can also symlink:
```bash
ln -s ../../AGENTS.md .cursor/rules/core.md
```

### Step 5: Progressive Disclosure (Optional)

If any topics would make AGENTS.md or .cursor/rules/ too long, ask the user:

**Use AskUserQuestion**:
```
"Would you like help creating supporting documentation files for complex topics?"

Options:
- Yes - I'll create templates for suggested docs
- No - Just suggest what docs I might need
- Skip - Don't need progressive disclosure
```

If user chooses **"Yes"**:

1. Suggest topics based on codebase analysis:
   ```
   docs/
   ├── architecture.md    # If complex system with >3 services/apps
   ├── testing.md        # If testing needs >5 lines of explanation
   ├── database.md       # If database conventions are extensive
   ├── deployment.md     # If deployment is multi-step
   └── auth.md          # If auth implementation is complex
   ```

2. Create `docs/` directory: `mkdir -p docs`

3. For each suggested topic, create a template file using Write tool:

   **Example template for docs/architecture.md**:
   ```markdown
   # Architecture

   ## System Overview

   [High-level description of the system]

   ## Services/Components

   ### [Service/Component Name]
   - **Purpose**: [What it does]
   - **Tech**: [Technologies used]
   - **Location**: [File path]

   ## Communication Patterns

   [How components interact]

   ## Data Flow

   [How data moves through the system]
   ```

4. Update AGENTS.md to reference the created docs:
   ```markdown
   ## Deep Dives

   For detailed information:
   - **Architecture**: See [docs/architecture.md](docs/architecture.md)
   - **Testing**: See [docs/testing.md](docs/testing.md)
   ```

If user chooses **"No"**:
- Just list suggested docs without creating files
- Provide one-line descriptions of what each doc should contain

If user chooses **"Skip"**:
- Move on, don't create or suggest progressive disclosure

## Important Guidelines

### DO:
- ✅ Keep AGENTS.md under 60 lines if possible
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
1. List of files with frontmatter types and line counts
2. Total line count and always-applied count
3. Commands to create symlinks
4. Frontmatter summary
5. Suggested progressive disclosure files (if any)
6. Quality assessment

Example:
```
✓ Created .cursor/rules/ directory

Generated files:
- core.mdc (25 lines) [alwaysApply: true] - Project overview and workflow
- react.mdc (18 lines) [globs: *.tsx,*.jsx] - React patterns
- typescript.mdc (15 lines) [globs: *.ts,*.tsx] - TypeScript conventions
- testing.mdc (20 lines) [description: Testing patterns] - Testing guide
- api.mdc (17 lines) [description: API conventions] - API guide

Total: 95 lines across 5 files
Always-applied: 25 lines (core.mdc only)
On-demand: 70 lines (loaded when relevant)

Compatibility symlinks:
ln -s AGENTS.md CLAUDE.md

Suggested progressive disclosure:
- docs/architecture.md (detailed service map)
- docs/testing.md (integration test examples)

Quality: ✓ Intelligent loading, appropriate frontmatter, focused content, agents.md compliant
```

### For Individual .mdc Rule Pattern

Show the user:
1. Generated filename with line count
2. Frontmatter type and reasoning
3. Content summary
4. Loading behavior
5. Quality assessment

Example (already shown in Step 3C, repeated here for reference):
```
✓ Generated .cursor/rules/python-conventions.mdc (18 lines)

Frontmatter: globs: "*.py,*.pyi"
Content: Python tool preferences (uv), type hints, format/lint commands
Auto-attaches when editing Python files

Quality: ✓ File-type specific, clear patterns, file references
```

## Reference

Based on:
- **AGENTS.md spec**: https://agents.md/ - Universal format for AI coding agents
- **HumanLayer guide**: https://www.humanlayer.dev/blog/writing-a-good-claude-md - Best practices for lean documentation

Key insights:
- LLMs can follow ~150-200 instructions
- Most harnesses/tools consume a chunk of that via system prompts and policies
- Single AGENTS.md: Keep under 60 lines
- .cursor/rules/: Keep total under 200 lines
- Both patterns use progressive disclosure for deep topics
- AGENTS.md is standard Markdown with no mandatory fields
- Always symlink CLAUDE.md → AGENTS.md for Claude Code compatibility
