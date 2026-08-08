#!/usr/bin/env bash
set -euo pipefail

COMMAND=$(cd "$(dirname "$0")/.." && pwd)/devcontainer-setup.md

rg -q -F 'detected gateway and MCP server domains' "$COMMAND"
rg -q -F 'every proposed exact' "$COMMAND"
rg -q -F 'require explicit user confirmation before generating files' "$COMMAND"

confirmation_line=$(rg -n -F 'require explicit user confirmation before generating files' "$COMMAND" | cut -d: -f1)
generation_line=$(rg -n -F 'Scaffold `.devcontainer-devpod/`' "$COMMAND" | cut -d: -f1)
[ "$confirmation_line" -lt "$generation_line" ]

echo "devcontainer setup confirmation guidance assertions passed"
