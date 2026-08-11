# Script Development Guide

This guide covers best practices for creating and integrating external scripts in Claude Code plugins.

## When to Use External Scripts

**Use external scripts when:**
- Logic is complex (>50 lines) and benefits from a proper programming language
- You need external dependencies (API clients, parsers, etc.)
- The same logic is reused across multiple commands
- Testing in isolation is valuable

**Use inline code when:**
- Logic is simple (a few bash commands)
- No external dependencies needed
- One-off transformations or validations

## Directory Structure

```
plugins/<plugin-name>/
├── scripts/                 # External scripts
│   ├── my-script.py        # Python with uv inline deps
│   └── helper.sh           # Shell scripts
└── commands/
    └── my-command.md       # Command that calls the script
```

## Path Resolution Pattern

Commands must resolve script paths via `${CLAUDE_PLUGIN_ROOT}`, the environment variable
Claude Code sets to the installed plugin's root directory.

### The Standard Pattern

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py" [args]
```

### Why Not Derive Paths From `$0` or Hardcode Them?

Command markdown is not executed as a script file — Claude runs the bash blocks via
`bash -c`, so `$0` resolves to the shell binary, not the command file. Hardcoded paths
fail across installations. Both classes of pattern break:

**Bad patterns (don't do these):**
```bash
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"   # $0 is /usr/bin/bash
SCRIPT="$(ls -t ~/.claude/plugins/cache/plugin-name/*/scripts/script.py | head -1)"
```

**Good pattern:**
```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py"
```

## Python Script Template

Use uv's inline script dependencies for zero-setup execution:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "pyyaml"]  # Add your deps here
# ///
"""
Brief description of what this script does.

Usage:
    script-name.py <command> [options]

Examples:
    script-name.py list --json
    script-name.py process --input file.txt
"""

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("command", choices=["list", "process"])
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Implementation here

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Key Elements

1. **Shebang**: `#!/usr/bin/env -S uv run --script` - Enables direct execution with uv
2. **Inline metadata**: PEP 723 format declares Python version and dependencies
3. **Docstring**: Usage documentation for the script
4. **Exit codes**: Return 0 for success, non-zero for errors

## Command Template

Commands that call external scripts:

```markdown
---
description: Brief command description
---

# Command Name

One-line description of what this command does.

## Usage

```bash
# List available items
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py" list

# Process with options
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py" process --input file.txt
```

## Examples

```bash
# Example 1: Basic usage
/plugin:command --flag value

# Example 2: With options
/plugin:command --verbose
```
```

## Real-World Examples

### capacities plugin

**Script**: `plugins/capacities/scripts/capacities.py`
- Full API client with caching
- Multiple subcommands (spaces, search, save-weblink, daily-note)
- JSON output mode for programmatic use

**Command**: `plugins/capacities/commands/daily-note.md`
```bash
if [ -z "$SPACE_ID" ]; then
    echo "Available spaces:"
    uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" spaces
    exit 0
fi

uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" daily-note \
    --space-id "$SPACE_ID" \
    --text "$TEXT" \
    --json
```

### dev-utilities plugin

**Script**: `plugins/dev-utilities/scripts/convert-hooks.py`
- Converts hookify rules to Cursor format
- Supports dry-run and force modes
- Preserves existing non-hookify hooks

**Command**: `plugins/dev-utilities/commands/convert-hooks.md`
```bash
# List rules
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/convert-hooks.py" --list

# Convert
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/convert-hooks.py"
```

## Testing Scripts

### Local Testing

```bash
# Run script directly (uv handles dependencies)
uv run plugins/capacities/scripts/capacities.py spaces

# Or make executable
chmod +x plugins/capacities/scripts/capacities.py
./plugins/capacities/scripts/capacities.py spaces
```

### Path Resolution Testing

Verify the command works when `CLAUDE_PLUGIN_ROOT` points at the plugin root:

```bash
export CLAUDE_PLUGIN_ROOT="$PWD/plugins/dev-utilities"
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/convert-hooks.py" --list
```

## Checklist

When adding scripts to plugins:

- [ ] Script in `scripts/` directory with proper shebang
- [ ] PEP 723 inline dependencies declared
- [ ] Command invokes scripts via `${CLAUDE_PLUGIN_ROOT}/scripts/...`
- [ ] Script has docstring with usage examples
- [ ] Works both from source and installed locations
- [ ] Exit codes: 0 for success, non-zero for errors
