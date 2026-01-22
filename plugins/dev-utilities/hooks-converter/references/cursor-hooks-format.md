# Cursor Hooks Format Reference

## hooks.json Schema

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      { "command": ".cursor/hooks/script-name.sh \"${command}\"" }
    ],
    "beforeSubmitPrompt": [...],
    "beforeReadFile": [...],
    "afterFileEdit": [...],
    "stop": [...]
  }
}
```

## Available Events

### beforeShellExecution
Triggered before any shell command runs.

**Input**: `${command}` - The command being executed

### beforeSubmitPrompt
Triggered before user prompt is submitted.

**Input**: `${prompt}` - The user's prompt text

### beforeReadFile
Triggered before reading a file.

**Input**: `${file_path}` - Path to the file

### afterFileEdit
Triggered after a file is edited.

**Input**: `${file_path}` - Path to the edited file

### stop
Triggered when agent stops.

**Input**: `${status}` - Stop status

## Script Output Format

Scripts must output valid JSON to stdout:

### Allow
```json
{"permission": "allow"}
```

### Deny (Block)
```json
{
  "permission": "deny",
  "userMessage": "Message shown to the user",
  "agentMessage": "Message shown to the agent"
}
```

### Ask (Warn)
```json
{
  "permission": "ask",
  "userMessage": "Question for the user",
  "agentMessage": "Context for the agent"
}
```

## Script Template

```bash
#!/bin/bash
# Generated from: .claude/hookify.{name}.local.md
# Description: {description}

INPUT="$1"

# Pattern matching
if echo "$INPUT" | grep -qE '{pattern}'; then
  cat <<'EOF'
{
  "permission": "deny",
  "userMessage": "{user_message}",
  "agentMessage": "{agent_message}"
}
EOF
  exit 0
fi

# Default: allow
echo '{"permission": "allow"}'
```

## Mapping Hookify to Cursor

### Event Mapping

| Hookify `event` | Cursor Event |
|-----------------|--------------|
| `bash` | `beforeShellExecution` |
| `prompt` | `beforeSubmitPrompt` |
| `file` (read) | `beforeReadFile` |
| `file` (edit) | `afterFileEdit` |
| `stop` | `stop` |

### Action Mapping

| Hookify `action` | Cursor `permission` |
|------------------|---------------------|
| `block` | `deny` |
| `warn` | `ask` |

### Pattern Handling

Hookify patterns are regex patterns. In generated scripts:

1. Use `grep -qE` for extended regex matching
2. Escape special characters for shell
3. Handle multi-line patterns with `grep -z` if needed

### Condition Handling

Hookify `conditions` with `regex_match` operator:

```yaml
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: /commit-push|/commits:commit-push
```

Converts to:
```bash
if echo "$INPUT" | grep -qE '/commit-push|/commits:commit-push'; then
```

## Example Conversion

### Input: hookify.block-grep-extended.local.md

```yaml
---
name: block-grep-extended
enabled: true
event: bash
pattern: grep\s+-E\b
action: block
---

The `-E` flag doesn't work correctly on macOS systems.
Use `-e` instead.
```

### Output: .cursor/hooks/hookify-block-grep-extended.sh

```bash
#!/bin/bash
# Generated from: .claude/hookify.block-grep-extended.local.md

INPUT="$1"

if echo "$INPUT" | grep -qE 'grep\s+-E\b'; then
  cat <<'EOF'
{
  "permission": "deny",
  "userMessage": "grep -E blocked! The -E flag doesn't work correctly on macOS systems. Use -e instead.",
  "agentMessage": "The -E flag doesn't work correctly on macOS systems. Use -e instead."
}
EOF
  exit 0
fi

echo '{"permission": "allow"}'
```

### Output: .cursor/hooks.json

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      { "command": ".cursor/hooks/hookify-block-grep-extended.sh \"${command}\"" }
    ]
  }
}
```

## File Naming Convention

Generated scripts follow the pattern:
```
hookify-{rule-name}.sh
```

Where `{rule-name}` is derived from the hookify filename:
- `.claude/hookify.block-grep-extended.local.md` -> `hookify-block-grep-extended.sh`
