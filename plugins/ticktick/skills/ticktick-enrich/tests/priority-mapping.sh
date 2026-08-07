#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
COMMAND_DOC="$PLUGIN_DIR/commands/enrich.md"
SKILL_DOC="$SKILL_DIR/SKILL.md"
GUIDE_DOC="$SKILL_DIR/references/enrichment-guide.md"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT

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

rg -q -F '# Empty or unstated input preserves task["priority"] unchanged.' \
  <<<"$priority_example"
rg -q -F 'priority_input = user_supplied_priority.strip().lower() if user_supplied_priority else ""' \
  <<<"$priority_example"
for entry in '"urgent": 5' '"critical": 5' '"high": 5' '"medium": 3' \
  '"low": 1' '"none": 0'; do
  rg -q -F "$entry" <<<"$priority_example"
done
rg -q -F 'if priority_input:' <<<"$priority_example"
rg -q -F 'task["priority"] = priority_map[priority_input]' <<<"$priority_example"
[ "$(rg -c -F 'update_task(' <<<"$priority_example")" -eq 1 ] || {
  echo "Marked priority example must contain exactly one update_task call" >&2
  exit 1
}
if rg -q '^[[:space:]]*"priority"[[:space:]]*:' <<<"$priority_example"; then
  echo "Marked example must omit a default priority field" >&2
  exit 1
fi

while IFS='|' read -r supplied expected; do
  PRIORITY_EXAMPLE="$priority_example" PRIORITY_INPUT="$supplied" EXPECTED="$expected" \
    uv run --no-project python - <<'PY'
import os

task = {"id": "fixture", "priority": 42}
user_supplied_priority = os.environ["PRIORITY_INPUT"]
written = []

def update_task(task_id, task):
    written.append((task_id, dict(task)))

exec(os.environ["PRIORITY_EXAMPLE"])
expected = int(os.environ["EXPECTED"])
assert task["priority"] == expected, (user_supplied_priority, task)
assert written == [("fixture", task)]
PY
done <<'EOF'
urgent|5
critical|5
high|5
medium|3
low|1
none|0
|42
EOF

extract_clear_dates_paragraphs() {
  awk -v needle='/ticktick:clear-dates' '
    function emit(value) {
      if (index(value, needle)) {
        gsub(/\n/, " ", value)
        print value
      }
    }
    function flush_unit() {
      if (unit != "") emit(unit)
      unit = ""
      kind = ""
    }
    /^[[:space:]]*$/ { flush_unit(); next }
    /^[[:space:]]*\|/ {
      flush_unit()
      emit($0)
      next
    }
    /^[[:space:]]*([-*+]|[0-9]+[.)])[[:space:]]+/ {
      flush_unit()
      unit = $0
      kind = "list"
      next
    }
    kind == "list" && /^[[:space:]]+/ {
      unit = unit "\n" $0
      next
    }
    kind == "list" { flush_unit() }
    {
      if (unit == "") unit = $0
      else unit = unit "\n" $0
      kind = "prose"
    }
    END { flush_unit() }
  ' "$1"
}

validate_clear_dates_contract() {
  doc=$1
  clear_dates_paragraphs="$(extract_clear_dates_paragraphs "$doc")"
  if [ -z "$clear_dates_paragraphs" ]; then
    echo "Missing clear-dates contract: $doc" >&2
    return 1
  fi
  while IFS= read -r paragraph; do
    case "$paragraph" in
      *dueDate*startDate*|*startDate*dueDate*) ;;
      *)
        echo "clear-dates paragraph must name both dueDate and startDate: $paragraph" >&2
        return 1
        ;;
    esac
  done <<<"$clear_dates_paragraphs"
}

contract_docs=("$COMMAND_DOC" "$SKILL_DOC" "$GUIDE_DOC")
for doc in "${contract_docs[@]}"; do
  validate_clear_dates_contract "$doc"
done

# Mutation: required field names in neighboring prose cannot satisfy the command paragraph.
sed "s/clears both \`dueDate\` and \`startDate\`/clears both date fields/" \
  "$COMMAND_DOC" >"$FIXTURE/adjacent-fields.md"
printf '\nNeighboring note: dueDate and startDate are API fields.\n' \
  >>"$FIXTURE/adjacent-fields.md"
if validate_clear_dates_contract "$FIXTURE/adjacent-fields.md" >/dev/null 2>&1; then
  echo "Adjacent text unexpectedly satisfied the clear-dates contract" >&2
  exit 1
fi

# Both field names without the command still fail the missing-contract check.
printf 'The API exposes both dueDate and startDate.\n' >"$FIXTURE/missing-command.md"
if validate_clear_dates_contract "$FIXTURE/missing-command.md" >/dev/null 2>&1; then
  echo "Missing clear-dates command unexpectedly passed contract validation" >&2
  exit 1
fi

echo "TickTick priority block and clear-dates contract fixtures passed"
