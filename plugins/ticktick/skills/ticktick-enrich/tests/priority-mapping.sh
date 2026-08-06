#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$(cd "$SKILL_DIR/../.." && pwd)"

mapping='urgent/critical/high → 5, medium → 3, low → 1, none → 0'
rg -q -F "$mapping" "$PLUGIN_DIR/commands/enrich.md"
rg -q -F "$mapping" "$SKILL_DIR/SKILL.md"
rg -q -F 'urgent/critical/high→5, medium→3, low→1, none→0; if unstated, leave as-is' \
  "$SKILL_DIR/references/enrichment-guide.md"

generic_example="$(awk '
  /^update_task\($/ { capture = 1 }
  capture { print }
  capture && /^\)$/ { exit }
' "$PLUGIN_DIR/commands/enrich.md")"
if rg -q '^[[:space:]]*"priority"[[:space:]]*:' <<<"$generic_example"; then
  echo "Empty/unstated-priority example must omit the priority field" >&2
  exit 1
fi
rg -q -F 'When priority input is empty or unstated, do not add or change' \
  "$PLUGIN_DIR/commands/enrich.md"

rg -q -F '# The user explicitly stated "medium".' "$PLUGIN_DIR/commands/enrich.md"
rg -q -F 'task["priority"] = 3' "$PLUGIN_DIR/commands/enrich.md"

# Literal backticks are part of the Markdown contract under test.
# shellcheck disable=SC2016
clear_dates_contract='`/ticktick:clear-dates` (the `ticktick_api.py` script) clears both `dueDate` and `startDate`; use it only when both should be removed. Never imply that it clears a single date'
rg -q -F "$clear_dates_contract" "$PLUGIN_DIR/commands/enrich.md"
rg -q -F '/ticktick:clear-dates` removes both `dueDate` and `startDate`' \
  "$SKILL_DIR/SKILL.md"
rg -q -F '/ticktick:clear-dates` removes both `dueDate` and `startDate`' \
  "$SKILL_DIR/references/enrichment-guide.md"
if rg -q -F 'To clear a date, use `/ticktick:clear-dates`' \
  "$SKILL_DIR/SKILL.md" "$SKILL_DIR/references/enrichment-guide.md"; then
  echo "clear-dates guidance must not imply single-date clearing" >&2
  exit 1
fi

echo "TickTick priority mapping and clear-dates fixtures passed"
