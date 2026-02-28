---
name: skill-validator
model: haiku
description: Validates SKILL.md files against token budget guidelines and plugin consistency
allowedTools:
  - Read
  - Bash
  - Grep
  - Glob
---

# Skill Validator Agent

Validate all SKILL.md files in the repository against the authoring guidelines in `docs/skill-authoring-guidelines.md`.

## Checks

Run each check against every `plugins/*/*/SKILL.md` file found:

### 1. Line Count
- SKILL.md must be under 500 lines
- Reference files (`references/*.md`) must be under 500 lines each
- Report: `PASS` / `WARN (X lines)` / `FAIL (X lines)`

### 2. Frontmatter Fields
- Required: `name`, `description`
- Optional: `version`, `author`, `allowed-tools`
- `name` must match `[a-z0-9-]+` pattern
- `description` must be under 1024 characters
- Report missing or invalid fields

### 3. Description Quality
- Under 200 characters for optimal display (WARN if over, FAIL if over 1024)
- Must not be generic (e.g., "A tool that helps you")
- Should include key use cases

### 4. Reference File Limits
- Each file in `references/` must be under 500 lines
- Reference depth must be one level (no nested directories)
- No circular references

### 5. Plugin Consistency
- Skill directory must be under a plugin listed in `.claude-plugin/marketplace.json`
- Skill name in frontmatter should match directory name

## Output Format

```
=== Skill Validation Report ===

plugins/commits/conventional-commits/SKILL.md
  [PASS] Line count: 102 lines
  [PASS] Frontmatter: name, description present
  [PASS] Description: 145 chars
  [PASS] References: 4 files, all under 500 lines
  [PASS] Plugin consistency: commits in marketplace.json

plugins/pull-requests/pr-creator/SKILL.md
  [PASS] Line count: 138 lines
  ...

=== Summary: X skills checked, Y passed, Z warnings, W failures ===
```

## Execution

1. Glob for all `plugins/*/*/SKILL.md` files
2. For each, run all checks above
3. Produce the validation report
4. Exit with summary counts
