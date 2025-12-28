# Skill Authoring Guidelines: Token Efficiency Best Practices

This guide provides comprehensive best practices for creating efficient, maintainable Agent Skills that minimize token consumption while maximizing clarity and usefulness.

## Table of Contents

- [Token Budgets](#token-budgets)
- [Progressive Disclosure Architecture](#progressive-disclosure-architecture)
- [File Organization](#file-organization)
- [Optimization Techniques](#optimization-techniques)
- [Bloat Patterns to Avoid](#bloat-patterns-to-avoid)
- [Frontmatter Best Practices](#frontmatter-best-practices)
- [Model Strategy Guidelines](#model-strategy-guidelines)
- [Checklist](#checklist)

## Token Budgets

The Agent Skills format implements a three-tier context-efficiency model designed to minimize unnecessary token consumption:

### 1. Metadata Layer (~100 tokens)

**What loads**: Only the `name` and `description` fields from frontmatter
**When**: At skill discovery/startup for all skills
**Purpose**: Enable efficient skill selection without loading full instructions

**Guidelines**:
- Keep descriptions under 200 characters for discovery
- Use specific keywords that help agents identify relevant tasks
- Front-load the most important capability descriptors

**Example**:
```yaml
---
name: pr-creator
description: Intelligent pull request creation with template-based field extraction and commit analysis
---
```

### 2. Instructions Layer (<5000 tokens target)

**What loads**: The complete `SKILL.md` body
**When**: Only when the skill is activated
**Target**: Under 500 lines (~5000 tokens)

**Guidelines**:
- Keep main `SKILL.md` focused on essential instructions
- Use tables for dense information (vs. prose paragraphs)
- Link to reference files rather than embedding details
- Prioritize quick-start information at the top

**Token estimation**: ~10 tokens per line of markdown on average

### 3. Resources Layer (on-demand)

**What loads**: Individual files from `references/`, `scripts/`, `assets/`
**When**: Only when explicitly needed by the agent
**Target**: Each reference file under 5000 tokens

**Guidelines**:
- Keep reference depth to one level (don't nest deeply)
- Each reference file should be self-contained
- Use descriptive filenames that indicate content
- Avoid circular or redundant references

## Progressive Disclosure Architecture

Design your skills to reveal information incrementally based on what the agent needs at each stage.

### Tier 1: Quick Start (Top of SKILL.md)

**Purpose**: Get started in under 1 minute
**Content**: Minimal commands, basic usage pattern
**Size target**: 50-100 lines

**Template**:
```markdown
## Quick Start

```bash
User: Create a PR for my changes
# or
User: /pr
```

The skill will: find template → analyze commits → create PR
```

### Tier 2: Core Workflow (Middle of SKILL.md)

**Purpose**: Understand the complete process
**Content**: Phase breakdown, decision points, key commands
**Size target**: 200-300 lines

**Use**:
- Numbered phases with clear boundaries
- Tables for structured data (vs. prose)
- Code blocks for concrete examples
- Bulleted lists for options/alternatives

### Tier 3: Reference Material (Separate files)

**Purpose**: Deep dives, edge cases, comprehensive examples
**Content**: Detailed specifications, extended examples, troubleshooting
**Size target**: 150-250 lines per file

**Common reference files**:
- `references/examples.md` - Real-world usage scenarios
- `references/format-reference.md` - Complete specification details
- `references/best-practices.md` - Guidelines and pitfalls
- `references/workflows.md` - Step-by-step procedures

## File Organization

### Directory Structure

```
skill-name/
├── SKILL.md                    # Core instructions (<500 lines)
├── references/                 # On-demand documentation
│   ├── examples.md            # Real-world scenarios
│   ├── workflows.md           # Step-by-step guides
│   └── format-reference.md    # Detailed specifications
├── scripts/                    # Executable tools (if needed)
│   └── script-name.sh
└── assets/                     # Templates, schemas (if needed)
    └── template.yaml
```

### Reference File Guidelines

**Keep files focused** - Each reference file should cover one topic:
- **examples.md** - Concrete usage scenarios with input/output
- **workflows.md** - Sequential step-by-step procedures
- **best-practices.md** - Guidelines, tips, common pitfalls
- **format-reference.md** - Complete specification/API details

**Avoid reference chains** - Don't have references that link to other references. Keep everything one level deep from `SKILL.md`.

**Size limits per file**:
- Target: 150-250 lines
- Maximum: 500 lines
- If exceeding 500 lines, split into multiple focused files

### When to Split Content

**Keep in SKILL.md** if:
- Information is needed for 80%+ of skill invocations
- Content is under 100 lines
- It's part of the core decision-making process

**Move to references/** if:
- Information is needed for edge cases or specific scenarios
- Content provides extended examples or deep technical details
- It's comprehensive specification material
- It would make SKILL.md exceed 500 lines

## Optimization Techniques

### 1. Use Tables for Dense Information

**Instead of**:
```markdown
The feat type is used for new features. The fix type is used for bug fixes.
The docs type is used for documentation changes. The refactor type is used
for code changes that neither fix bugs nor add features.
```

**Use**:
```markdown
| Type | Purpose |
|------|---------|
| feat | New features |
| fix | Bug fixes |
| docs | Documentation |
| refactor | Code restructuring |
```

**Token savings**: ~40% reduction for structured data

### 2. Consolidate Repetitive Examples

**Instead of**: 5 separate examples showing minor variations

**Use**: 1-2 comprehensive examples with variations noted inline

**Example**:
```markdown
## Example: Feature Addition

```bash
git commit -m "feat(api): add user endpoint"
# Variations: feat(ui), feat(db), feat(auth)
```
```

### 3. Cross-Reference Rather Than Duplicate

**Instead of**:
```markdown
# In SKILL.md
## Commit Format
<type>[scope]: <description>

[body]

[footer]

# Also in format-reference.md
## Commit Format
<type>[scope]: <description>

[body]

[footer]
```

**Use**:
```markdown
# In SKILL.md
## Quick Format Reference

```text
<type>[optional scope]: <description>
```

**For complete specification**, see [`format-reference.md`](references/format-reference.md)
```

### 4. Use Relative Paths

**Always use relative paths** for file references to enable lazy loading:

```markdown
See [workflows.md](references/workflows.md) for detailed steps.
```

**Not**:
```markdown
See workflows.md in the references directory for detailed steps.
```

### 5. Eliminate Excessive Whitespace

**Instead of**:
```markdown
## Section


Some content here.


Another paragraph.


## Next Section
```

**Use**:
```markdown
## Section

Some content here.

Another paragraph.

## Next Section
```

**Rule**: Use single blank lines between elements, double only before major sections.

### 6. Concise Command Documentation

**Instead of**:
```markdown
To view the git status, you should run the following command in your terminal:
```

**Use**:
```markdown
Check status: `git status`
```

**Or for multiple commands**:
```markdown
**Git commands**:
```bash
git status           # Check working tree
git diff HEAD        # View changes
```
```

## Bloat Patterns to Avoid

### 1. Repetitive Examples

**Problem**: Multiple examples showing essentially the same pattern

**Example of bloat**:
```markdown
## Example 1: Feature Commit
git commit -m "feat(api): add endpoint"

## Example 2: Another Feature
git commit -m "feat(ui): add button"

## Example 3: Yet Another Feature
git commit -m "feat(db): add migration"
```

**Solution**: Consolidate into scenario matrix
```markdown
| Scenario | Commit Example |
|----------|---------------|
| API feature | `feat(api): add endpoint` |
| UI feature | `feat(ui): add button` |
| DB feature | `feat(db): add migration` |
```

### 2. Redundant Workflow Descriptions

**Problem**: Describing the same process multiple times in different files

**Solution**:
- Define workflow once in `workflows.md`
- Reference it from `SKILL.md` and examples
- Never duplicate the full process

### 3. Verbose Explanations

**Problem**: Explaining concepts that the AI agent already understands

**Instead of**:
```markdown
Git is a version control system. When you make changes to files, Git tracks
them. To record your changes permanently, you need to create a commit. A
commit is like a snapshot of your code at a specific point in time.
```

**Use**:
```markdown
**Prerequisites**: Git repository with staged changes
```

**Rule**: Assume the agent has general technical knowledge. Focus on skill-specific instructions.

### 4. Deep Reference Chains

**Problem**: SKILL.md → references/overview.md → references/details.md → references/examples.md

**Solution**: Keep all references one level deep from SKILL.md

```
SKILL.md
  ├→ references/workflows.md
  ├→ references/examples.md
  └→ references/format-reference.md
```

### 5. Embedded Large Code Blocks

**Problem**: Including entire scripts or templates inline in SKILL.md

**Solution**:
- Move scripts to `scripts/` directory
- Move templates to `assets/` directory
- Reference them by path: `See scripts/generate.sh`

## Frontmatter Best Practices

### Required Fields

```yaml
---
name: skill-name
description: Concise description of what this skill does and when to use it
version: 1.0.0
author: your-name
---
```

### Field Constraints

| Field | Max Length | Format | Purpose |
|-------|-----------|--------|---------|
| name | 64 chars | `[a-z0-9-]+` | Skill identifier |
| description | 1024 chars | Plain text | Discovery and selection |
| version | - | Semantic versioning | Change tracking |
| author | - | Plain text | Attribution |
| compatibility | 500 chars | Plain text | Environment requirements |

### Description Guidelines

**Good descriptions**:
- Lead with primary capability
- Include relevant keywords for discovery
- Mention key use cases
- Under 200 characters for optimal display

**Example**:
```yaml
description: Creates conventional commits following conventionalcommits.org. Analyzes git changes and generates properly formatted commit messages with types (feat, fix, docs, etc.) and scopes. Supports single/multi-commit workflows and commit-and-push operations.
```

**Not**:
```yaml
description: A tool that helps you commit
```

### Optional: Allowed Tools

**Experimental feature** - Declare pre-approved tools:

```yaml
---
name: skill-name
description: Description here
allowed-tools: Bash Read Write Grep
---
```

**Use when**: You want to restrict which tools the agent can use during skill execution.

## Model Strategy Guidelines

Define when to use different AI models for optimal cost and performance.

### Model Tiers

**Haiku 4.5** - Fast operations (low cost, sub-second response):
- File I/O operations (read, write, parse)
- Pattern matching and simple analysis
- Git command execution
- Template filling
- Simple categorization

**Sonnet 4.5** - Complex reasoning (higher cost, detailed analysis):
- Decision-making with multiple factors
- Natural language synthesis and generation
- Cross-cutting change analysis
- Commit/PR body composition
- Gap detection and inference

### Documentation Pattern

Include a model strategy section in your SKILL.md:

```markdown
## Model Strategy

| Task | Model | Rationale |
|------|-------|-----------|
| File discovery, git ops, parsing | Haiku | Fast, deterministic |
| Commit analysis, PR generation, gap detection | Sonnet | Complex reasoning |
```

### Sub-Agent Instructions

When your skill involves sub-agents, provide explicit guidance:

```markdown
## Sub-Agent Strategy

### Use Haiku 4.5 for

- Quick diff analysis and file categorization
- Simple commit message drafting

### Use Sonnet 4.5 for

- Commit breakpoint determination and multi-commit planning
- Scope identification and complex message composition
- Cross-cutting change analysis
```

## Checklist

Use this checklist when authoring or reviewing skills:

### Structure
- [ ] SKILL.md is under 500 lines (~5000 tokens)
- [ ] Description is under 200 characters
- [ ] Quick Start section appears in first 50 lines
- [ ] Reference files are under 500 lines each
- [ ] Reference depth is one level (no chains)
- [ ] All file references use relative paths

### Content Efficiency
- [ ] Tables used for structured data (vs. prose)
- [ ] Examples are consolidated (not repetitive)
- [ ] No duplicate content across files
- [ ] Cross-references used instead of duplication
- [ ] Minimal whitespace (single blank lines)
- [ ] Concise command documentation

### Organization
- [ ] Essential instructions in SKILL.md
- [ ] Extended examples in references/examples.md
- [ ] Detailed workflows in references/workflows.md
- [ ] Specifications in references/format-reference.md
- [ ] Scripts in scripts/ (not embedded)
- [ ] Templates in assets/ (not embedded)

### Metadata
- [ ] Name follows format: `[a-z0-9-]+`
- [ ] Description includes key use cases
- [ ] Description under 1024 characters
- [ ] Version follows semantic versioning
- [ ] Model strategy documented (if applicable)

### Bloat Patterns Avoided
- [ ] No repetitive examples
- [ ] No redundant workflow descriptions
- [ ] No verbose explanations of basic concepts
- [ ] No deep reference chains
- [ ] No embedded large code blocks
- [ ] Minimal prose, maximum density

## Real-World Examples

### Efficient Skill: pr-creator

**Size**: 138 lines
**Structure**: Core workflow in SKILL.md, no separate references needed
**Efficiency techniques**:
- Tables for checkbox auto-fill rules
- Consolidated git commands in single code block
- Quick start prominently placed
- Model strategy clearly documented

**Location**: `plugins/pull-requests/pr-creator/SKILL.md`

### Efficient Skill: conventional-commits

**Size**: 102 lines (SKILL.md) + 719 lines (references)
**Structure**: Core overview in SKILL.md, detailed content in 4 reference files
**Efficiency techniques**:
- Index-style SKILL.md that links to focused reference files
- Clear separation: workflows vs. examples vs. specification
- Each reference file covers one topic
- Cross-references instead of duplication

**Location**: `plugins/commits/conventional-commits/SKILL.md`

## Additional Resources

- **Agent Skills Specification**: https://agentskills.io/specification
- **This Repository's AGENTS.md**: `/Users/nklauer/dev/klauern-skills/AGENTS.md`
- **Example Skills**: `/Users/nklauer/dev/klauern-skills/plugins/*/*/SKILL.md`

## Summary

**The golden rule**: If an agent doesn't need it for 80% of invocations, move it to a reference file.

By following progressive disclosure principles and keeping token budgets in mind, you create skills that:
- Load quickly during discovery
- Minimize context consumption
- Provide information exactly when needed
- Remain maintainable and extensible

**Target numbers to remember**:
- Metadata: ~100 tokens (description <200 chars)
- SKILL.md: <500 lines (~5000 tokens)
- Reference files: <500 lines each
- Reference depth: 1 level
