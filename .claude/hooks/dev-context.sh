#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root relative to this script
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# Marketplace version
version=$(jq -r '.metadata.version // "unknown"' "$REPO_ROOT/.claude-plugin/marketplace.json" 2>/dev/null || echo "unknown")

# Plugin count
plugin_count=$(jq -r '.plugins | length' "$REPO_ROOT/.claude-plugin/marketplace.json" 2>/dev/null || echo "?")

# Skill count
skill_count=$(find "$REPO_ROOT/plugins" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')

# Migrating skills
migrating_count=0
if [[ -d "$REPO_ROOT/migrating" ]]; then
  migrating_count=$(find "$REPO_ROOT/migrating" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
fi

# Git branch
branch=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo "unknown")

cat <<EOF
klauern-skills v${version} | ${plugin_count} plugins | ${skill_count} skills | ${migrating_count} migrating | branch: ${branch}
EOF
