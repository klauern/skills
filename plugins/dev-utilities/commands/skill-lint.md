---
allowed-tools: Bash Read Grep Glob
description: Validate SKILL.md files against authoring guidelines
---

# /skill-lint

Validate one or all SKILL.md files against the token budget and authoring guidelines.

## Usage

```bash
/dev-utilities:skill-lint              # Validate all skills
/dev-utilities:skill-lint commits      # Validate skills in a specific plugin
```

## Behavior

1. **Discover Skills**
   - If a plugin name is provided, find `plugins/<name>/*/SKILL.md`
   - Otherwise, find all `plugins/*/*/SKILL.md`

2. **For Each SKILL.md, Check**:

   | Check | Pass Criteria | Severity |
   |-------|--------------|----------|
   | Line count | < 500 lines | FAIL if over |
   | Frontmatter `name` | Present, matches `[a-z0-9-]+` | FAIL if missing |
   | Frontmatter `description` | Present, < 1024 chars | FAIL if missing |
   | Description length | < 200 chars | WARN if over |
   | Reference files | Each < 500 lines | FAIL if over |
   | Reference depth | One level only | FAIL if nested |
   | Directory name | Matches frontmatter `name` | WARN if mismatch |

3. **Check Each Reference File** in `references/`:
   - Line count under 500
   - No subdirectories (one-level depth)

4. **Report Results**:
   ```
   plugins/commits/conventional-commits/SKILL.md
     [PASS] 102 lines (limit: 500)
     [PASS] name: conventional-commits
     [PASS] description: 145 chars (limit: 200)
     [PASS] 4 reference files, all valid

   Summary: 8 skills | 8 passed | 0 warnings | 0 failures
   ```

## Implementation Notes

- Use `wc -l` for line counts
- Parse frontmatter between `---` delimiters
- Use `fd` for file discovery when available, fall back to `find`
- Exit with summary showing total pass/warn/fail counts
