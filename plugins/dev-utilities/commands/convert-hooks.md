---
description: Convert Claude Code hookify rules to Cursor hooks format
---

# Convert Hooks

Convert Claude Code hookify rules (`.claude/hookify.*.local.md`) to Cursor's hook format.

## Usage

Run the conversion script with the desired options:

```bash
# List hookify rules without converting
uv run plugins/dev-utilities/scripts/convert-hooks.py --list

# Preview generated files (dry run)
uv run plugins/dev-utilities/scripts/convert-hooks.py --dry-run

# Convert and write files
uv run plugins/dev-utilities/scripts/convert-hooks.py

# Force overwrite existing hooks
uv run plugins/dev-utilities/scripts/convert-hooks.py --force
```

## Workflow

1. Run `--list` first to see available hookify rules
2. Run `--dry-run` to preview what will be generated
3. Run without flags to create the files
4. Test in Cursor by triggering a hook

## Generated Files

The script creates:
- `.cursor/hooks.json` - Hook configuration
- `.cursor/hooks/*.sh` - Shell scripts for each rule

## Notes

- Disabled rules (`enabled: false`) are skipped
- Existing non-hookify hooks in `hooks.json` are preserved
- Use `--force` to overwrite hookify-generated scripts
