#!/bin/bash
# Generated from: hookify.require-version-bump.local.md
# Rule: require-version-bump-before-commit

INPUT="$1"

if echo "$INPUT" | grep -qE '/commit-push|/commits:commit-push'; then
  cat <<'EOF'
{
  "permission": "ask",
  "userMessage": "⚠️ Version Bump Reminder You're about to commit and push changes. Have you run /version-bump first? Before committing plugin changes, remember to: 1. Run /version-bump to update affected plugin versions 2. The version-bump command will auto-detect changed plugins 3. Marketplace version will also be bumped automatically If you've already run /version-bump or this commit doesn't affect plugins, proceed as normal.",
  "agentMessage": "⚠️ Version Bump Reminder You're about to commit and push changes. Have you run /version-bump first? Before committing plugin changes, remember to: 1. Run /version-bump to update affected plugin versions 2. The version-bump command will auto-detect changed plugins 3. Marketplace version will also be bumped automatically If you've already run /version-bump or this commit doesn't affect plugins, proceed as normal."
}
EOF
  exit 0
fi

echo '{"permission": "allow"}'
