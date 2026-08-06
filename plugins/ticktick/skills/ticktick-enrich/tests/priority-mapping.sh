#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$(cd "$SKILL_DIR/../.." && pwd)"

mapping='urgent/critical/high → 5, medium → 3, low → 1, none → 0'
rg -q -F "$mapping" "$PLUGIN_DIR/commands/enrich.md"
rg -q -F "$mapping" "$SKILL_DIR/SKILL.md"
rg -q -F 'urgent/critical/high→5, medium→3, low→1, none→0; if unstated, leave as-is' \
  "$SKILL_DIR/references/enrichment-guide.md"

echo "TickTick priority mapping fixtures passed"
