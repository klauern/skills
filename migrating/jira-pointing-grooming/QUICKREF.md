# Quick Reference – Pointing & Grooming

Use this cheat sheet for day-to-day commands and score reminders. For the full narrative, workflows, and rationale, see [`README.md`](README.md) and the reference docs linked below.

## Commands at a Glance

```bash
# Find candidates (FSEC filter by default)
cd ~/.claude/skills/jira-pointing-grooming/scripts
uv run find_grooming_candidates.py
uv run find_grooming_candidates.py --unestimated   # only unpointed
uv run find_grooming_candidates.py --limit 20      # cap results
uv run find_grooming_candidates.py --label needs-grooming

# Analyze readiness for a specific ticket
uv run analyze_readiness.py FSEC-1234
uv run analyze_readiness.py FSEC-1234 --verbose    # include questions/actions
uv run analyze_readiness.py FSEC-1234 --json       # machine-readable

# Review blocked work
uv run analyze_blocked.py
uv run analyze_blocked.py --min-age-days 30
uv run analyze_blocked.py --detailed --output blocked_report.txt

# CSV workflow for bulk decisions
uv run export_blocked_csv.py --output blocked.csv
# (edit CSV in spreadsheet app, add decisions)
uv run apply_decisions_csv.py blocked.csv --dry-run  # preview
uv run apply_decisions_csv.py blocked.csv            # apply

# Batch check several tickets
for ticket in FSEC-1234 FSEC-1235; do
  echo \"=== $ticket ===\"
  uv run analyze_readiness.py \"$ticket\"
done
```

## Score & Severity Cheatsheet

| Score | Status | Meaning |
|-------|--------|---------|
| 90–100 | ✅ Ready | Excellent – point it |
| 75–89  | ⚠️ Mostly ready | Minor clarifications |
| 60–74  | ❌ Needs work | Missing clarity |
| < 60   | ❌ Not ready | Significant gaps |

| Severity | Examples | Impact |
|----------|----------|--------|
| 🔴 HIGH | Missing AC, vague requirements, missing security context | Blocks estimation |
| 🟡 MEDIUM | No technical outline, missing dependencies, scope creep | Hard to estimate |
| 🔵 LOW | Missing test scenarios or DoD | Nice-to-have |

## Grooming Flow (Three Beats)

1. **Find candidates** with the FSEC filter (`find_grooming_candidates.py`) and note key metadata.
2. **Analyze readiness** (checklists + `analyze_readiness.py`) and capture gaps using the template from `references/grooming_template.md`.
3. **Plan actions** (TodoWrite, Jira labels/comments, re-run analysis until ≥75). Full workflow details live in [`README.md`](README.md).

## Filters, Checklists & References

- **Default filter details** – statuses, issue types, and rationale: [`references/fsec_grooming_filter.md`](references/fsec_grooming_filter.md)
- **Readiness rubric & examples** – scoring weights, red flags: [`references/readiness_criteria.md`](references/readiness_criteria.md)
- **Gap detection patterns** – phrases to scan for + recommended remediations: [`references/gap_patterns.md`](references/gap_patterns.md)
- **Grooming templates** – quick checklist + full session notes: [`references/grooming_template.md`](references/grooming_template.md)

## Handy JQL Snippets

```sql
-- Guardians grooming board (default)
project = FSEC
AND type in (Spike, Story, Task)
AND status in (Backlog, "In Progress", Blocked, Intake,
               "Ready to Refine", "Ready to Ship", Refined,
               "To Do", Shipping, Testing, Review)
ORDER BY updated DESC

-- Backlog + unestimated
project = FSEC AND status = Backlog
AND "Story Points" IS EMPTY

-- Flagged for grooming
project = FSEC AND labels = needs-grooming
ORDER BY priority DESC
```

## Troubleshooting Nuggets

- Missing Jira auth? Set `JIRA_EMAIL` + `JIRA_API_TOKEN` (see README for instructions).
- Filter returns nothing? Add `--no-grooming-filter` and supply your own `--jql` or status constraints.
- Scores feel off? Calibrate thresholds in `references/readiness_criteria.md` and detection patterns in `references/gap_patterns.md`.
