#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
COMMAND_DOC="$PLUGIN_DIR/commands/enrich.md"
SKILL_DOC="$SKILL_DIR/SKILL.md"
GUIDE_DOC="$SKILL_DIR/references/enrichment-guide.md"

mapping='urgent/critical/high → 5, medium → 3, low → 1, none → 0'
rg -q -F "$mapping" "$COMMAND_DOC"
rg -q -F "$mapping" "$SKILL_DOC"
rg -q -F 'urgent/critical/high→5, medium→3, low→1, none→0; if unstated, leave as-is' \
  "$GUIDE_DOC"

marker='<!-- ticktick-priority-example -->'
[ "$(rg -c -F "$marker" "$COMMAND_DOC")" -eq 1 ] || {
  echo "Expected exactly one marked TickTick priority example" >&2
  exit 1
}
priority_example=$(
  awk -v marker="$marker" '
    $0 == marker { marked = 1; next }
    marked && /^```python$/ { capture = 1; next }
    capture && /^```$/ { exit }
    capture { print }
  ' "$COMMAND_DOC"
)
[ -n "$priority_example" ] || {
  echo "Marked TickTick priority example is empty" >&2
  exit 1
}

rg -q -F '# Empty or unstated input leaves task["priority"] untouched.' \
  <<<"$priority_example"
rg -q -F 'priority_input = user_supplied_priority.strip().lower() if user_supplied_priority else ""' \
  <<<"$priority_example"
rg -q -F 'if priority_input == "medium":' <<<"$priority_example"
rg -q -F '# The user explicitly stated "medium".' <<<"$priority_example"
rg -q -F 'task["priority"] = 3' <<<"$priority_example"
[ "$(rg -c -F 'update_task(' <<<"$priority_example")" -eq 1 ] || {
  echo "Marked priority example must contain exactly one update_task call" >&2
  exit 1
}
if rg -q '^[[:space:]]*"priority"[[:space:]]*:' <<<"$priority_example"; then
  echo "Marked example must omit a default priority field" >&2
  exit 1
fi

contract_docs=("$COMMAND_DOC" "$SKILL_DOC" "$GUIDE_DOC")
for doc in "${contract_docs[@]}"; do
  if ! clear_dates_lines="$(rg -n -F '/ticktick:clear-dates' "$doc")"; then
    echo "Missing clear-dates contract: $doc" >&2
    exit 1
  fi
  while IFS= read -r guidance; do
    case "$guidance" in
      *dueDate*startDate*|*startDate*dueDate*) ;;
      *)
        echo "clear-dates guidance must name both dueDate and startDate: $guidance" >&2
        exit 1
        ;;
    esac
  done <<<"$clear_dates_lines"
done

echo "TickTick priority block and clear-dates contract fixtures passed"
