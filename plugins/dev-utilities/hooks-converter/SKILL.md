---
name: hooks-converter
description: Convert Claude Code hookify rules to Cursor hooks format. Use when user wants to port hookify rules to Cursor.
allowed-tools: Bash Read Grep Glob Edit Write
---

# Hooks Converter

Convert Claude Code hookify rules (`.claude/hookify.*.local.md`) to Cursor's hook format (`.cursor/hooks.json` + shell scripts).

## Quick Start

**Command**: `/dev-utilities:convert-hooks`

## Event & Action Mapping

| Hookify Event | Cursor Event | Input Variable |
|---------------|--------------|----------------|
| `bash` | `beforeShellExecution` | `${command}` |
| `prompt` | `beforeSubmitPrompt` | `${prompt}` |
| `file` | `beforeReadFile` / `afterFileEdit` | `${file_path}` |
| `stop` | `stop` | `${status}` |

| Hookify Action | Cursor Output |
|----------------|---------------|
| `block` | `{"permission": "deny", ...}` |
| `warn` | `{"permission": "ask", ...}` |

## Options

```bash
/convert-hooks              # Convert all hookify rules
/convert-hooks --list       # List rules without converting
/convert-hooks --dry-run    # Preview generated files
/convert-hooks --force      # Overwrite existing Cursor hooks
```

## Workflow

1. **Discovery**: Find all `.claude/hookify.*.local.md` files
2. **Parse**: Extract YAML frontmatter and markdown body
3. **Filter**: Skip rules with `enabled: false`
4. **Convert**: Generate Cursor-compatible scripts
5. **Output**: Write `.cursor/hooks.json` and scripts
6. **Verify**: Report conversion summary

## Generated Output

```
.cursor/
├── hooks.json                           # Hook configuration
└── hooks/
    ├── hookify-block-grep-extended.sh   # Generated script
    └── hookify-require-version-bump.sh
```

## References

- [Cursor Hooks Format](references/cursor-hooks-format.md) - JSON schema and script format

## Design Notes

- **Integration**: Convert-only mode. Use `/hookify:hookify` separately to create rules first.
- **Conflict handling**: Merges with existing `.cursor/hooks.json`, preserving non-hookify hooks.
- **Disabled rules**: Skips rules with `enabled: false`.

## Model Strategy

| Task | Model |
|------|-------|
| File discovery, YAML parsing | Haiku |
| Pattern translation, message formatting | Haiku |
