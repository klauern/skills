#!/bin/bash
# Generated from: hookify.block-grep-extended.local.md
# Rule: block-grep-extended

INPUT="$1"

if echo "$INPUT" | grep -qE 'grep\s+-E\b'; then
  cat <<'EOF'
{
  "permission": "deny",
  "userMessage": "⚠️ grep -E blocked! The -E flag doesn't work correctly on macOS systems. Use -e instead: grep -e \"pattern\" instead of grep -E \"pattern\" Note: -e specifies the pattern to match, while -E enables extended regex which has compatibility issues on macOS.",
  "agentMessage": "⚠️ grep -E blocked! The -E flag doesn't work correctly on macOS systems. Use -e instead: grep -e \"pattern\" instead of grep -E \"pattern\" Note: -e specifies the pattern to match, while -E enables extended regex which has compatibility issues on macOS."
}
EOF
  exit 0
fi

echo '{"permission": "allow"}'
