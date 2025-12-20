#!/bin/bash
# Claude Code tool-use hook for version management
# Triggers after Write/Edit operations on skills or commands

set -e

TOOL_NAME="$1"
TOOL_ARGS="$2"

# Only trigger on Write or Edit tools
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
  exit 0
fi

# Extract file path from tool args (JSON)
FILE_PATH=$(echo "$TOOL_ARGS" | jq -r '.file_path // empty' 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Check if file is a skill or command
if [[ "$FILE_PATH" =~ plugins/[^/]+/[^/]+/SKILL\.md ]] || \
   [[ "$FILE_PATH" =~ plugins/[^/]+/commands/.*\.md ]] || \
   [[ "$FILE_PATH" =~ plugins/[^/]+/[^/]+/(scripts|references)/ ]] || \
   [[ "$FILE_PATH" =~ \.claude-plugin/(plugin|marketplace)\.json ]]; then

  # Determine which plugin was modified
  PLUGIN_NAME=""
  if [[ "$FILE_PATH" =~ plugins/([^/]+)/ ]]; then
    PLUGIN_NAME="${BASH_REMATCH[1]}"
  fi

  # Create reminder message
  cat <<EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Version Management Reminder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Modified: $FILE_PATH
Plugin: ${PLUGIN_NAME:-marketplace}

⚠️  Consider bumping versions when you're ready:

Quick workflow:
   /bump-version $PLUGIN_NAME

Or manual workflow:
1. Detect changes:
   python .claude/skills/version-manager/scripts/detect_changes.py plugins/$PLUGIN_NAME

2. Infer bump type:
   python .claude/skills/version-manager/scripts/infer_bump_type.py

3. Bump version:
   python .claude/skills/version-manager/scripts/bump_version.py plugins/$PLUGIN_NAME <major|minor|patch>

4. Update changelog:
   python .claude/skills/version-manager/scripts/update_changelog.py <version>

5. Commit:
   git commit -m "chore(release): bump $PLUGIN_NAME to <version>"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
fi

exit 0
