# Jira Pointing and Grooming Skill

A Claude Code skill for identifying tickets that need more information and building actionable plans to make them ready for estimation (pointing).

## Overview

> Looking for snackable commands and score tables? Jump to [`QUICKREF.md`](QUICKREF.md).

This skill helps you:
- Find tickets that need grooming before they can be estimated
- Analyze ticket readiness using automated gap detection
- Build structured grooming plans with specific action items
- Transform underspecified tickets into clear, estimatable work

## Files

- `SKILL.md` – Model-facing instructions (what Claude does automatically)
- `QUICKREF.md` – Human cheat sheet for the most common commands and score/severity tables
- `scripts/analyze_readiness.py` – Automated readiness analysis and gap detection
- `scripts/find_grooming_candidates.py` – Search for tickets needing grooming
- `scripts/analyze_blocked.py` – Analyze blocked tickets and identify cleanup opportunities
- `scripts/export_blocked_csv.py` – Export blocked tickets to CSV for bulk decision-making
- `scripts/apply_decisions_csv.py` – Apply decisions from CSV back to Jira
- `references/readiness_criteria.md` – Definition of "Ready for Pointing" plus scoring rubric
- `references/gap_patterns.md` – Common gap patterns and detection rules
- `references/grooming_template.md` – Templates for grooming sessions

## Quick Start

### 1. Invoke the Skill

In Claude Code, activate the skill:

```
User: Help me groom FSEC-1234
User: Find tickets that need grooming
User: What's blocking FSEC-5678 from being pointed?
```

### 2. Use the Scripts Directly

Find tickets needing grooming (uses FSEC team's actual grooming board filter):
```bash
cd ~/.claude/skills/jira-pointing-grooming/scripts
uv run find_grooming_candidates.py                  # Default: FSEC grooming filter
uv run find_grooming_candidates.py --unestimated    # Only unestimated tickets
uv run find_grooming_candidates.py --limit 20       # Limit to 20 results
```

Analyze a specific ticket:
```bash
uv run analyze_readiness.py FSEC-1234
uv run analyze_readiness.py FSEC-1234 --verbose  # Show detailed questions/actions
uv run analyze_readiness.py FSEC-1234 --json     # JSON output
```

## FSEC Team Grooming Filter

By default, the skill uses your team's actual grooming board filter:
- **URL**: https://zendesk.atlassian.net/jira/software/c/projects/FSEC/list
- **Issue Types**: Spike, Story, Task
- **Statuses**: Backlog, In Progress, Blocked, Intake, Ready to Refine, Ready to Ship, Refined, To Do, Shipping, Testing, Review
- **Sort**: Most recently updated first

This ensures consistency with what your team sees in Jira during grooming sessions.

## Workflow

### Step 1: Find Candidates
```bash
uv run find_grooming_candidates.py --project FSEC --status "Needs More Info"
```

### Step 2: Analyze Readiness
```bash
uv run analyze_readiness.py FSEC-1234 --verbose
```

### Step 3: Address Gaps
Use the skill in Claude Code to:
- Create a TodoWrite action plan
- Document questions for stakeholders
- Update the ticket with clarifications
- Add grooming notes from the template

### Step 4: Validate
Re-run readiness analysis to confirm score ≥ 75:
```bash
uv run analyze_readiness.py FSEC-1234
```

### Step 5: Mark Ready
```bash
jira issue edit FSEC-1234 --label +ready-for-pointing
jira issue edit FSEC-1234 --label -needs-grooming
```

## Readiness Scoring

Tickets are scored 0-100 based on:
- **Requirements** (70%): Acceptance criteria, clear problem statement, no vague language
- **Technical** (20%): Approach discussed, dependencies identified, components listed
- **Testing** (5%): Test scenarios defined
- **Context** (5%): Security/compliance noted, deployment considerations

**Score Interpretation**:
- 90-100: ✅ Ready for pointing
- 75-89: ⚠️ Mostly ready, minor gaps
- 60-74: ❌ Some gaps to address
- <60: ❌ Significant work needed

**Gap Severity Legend**:
- 🔴 HIGH – Blocks estimation (e.g., missing AC, unclear scope, no security guidance)
- 🟡 MEDIUM – Estimation is risky without clarification (dependencies, technical approach, scope creep)
- 🔵 LOW – Nice-to-have polish (test scenarios, full DoD checklist)

## Gap Detection Patterns

The analyzer detects:

1. **Missing Acceptance Criteria** (HIGH) - No clear definition of "done"
2. **Vague Language** (HIGH) - "maybe", "probably", "TBD", "etc."
3. **No Technical Context** (MEDIUM) - No discussion of approach
4. **Missing Dependencies** (MEDIUM) - Mentions blockers but no links
5. **No Test Scenarios** (LOW) - No testing plan
6. **Scope Creep** (MEDIUM) - Requirements growing in comments
7. **Missing Security Context** (HIGH) - Handles sensitive data without security notes

## Customization

### Define Your Team's Standards

Edit `references/readiness_criteria.md` to add:
- Your team's definition of "Ready for Pointing"
- Team-specific red flags and patterns
- Custom scoring weights

### Add Team-Specific Gap Patterns

Edit `references/gap_patterns.md` to document:
- Gaps you see repeatedly in your backlog
- Team-specific keywords and detection rules
- Custom severity levels

### Customize the Scripts

The Python scripts use environment variables:
- `JIRA_URL` - Your Jira instance (default: https://zendesk.atlassian.net)
- `JIRA_EMAIL` - Your email
- `JIRA_API_TOKEN` - Your API token

## Integration with Other Skills

This skill complements:
- **jira-team-workflow**: Use this for pre-sprint grooming, use team workflow for in-sprint work
- **jira-review**: Use review for building todos from tickets, use this for assessing readiness

## Example Output

```
================================================================================
Readiness Analysis: FSEC-1234
================================================================================
Summary: Add bulk export for security scan results
Type: Story | Status: Needs More Info

📊 Readiness Score: 45.0/100 ❌
   Requirements: 45.0/70
   Technical:    20.0/20
   Context:      5.0/5
   Testing:      0.0/5

❌ NOT READY - Significant work needed

❌ Gaps Found (3):

1. 🔴 Missing Acceptance Criteria [HIGH]
   No clear definition of "done". What specific, testable conditions must be met?

2. 🔵 No Test Scenarios [LOW]
   No discussion of how to verify this works.

3. 🟡 Scope Growing in Comments [MEDIUM]
   Found 5 comments adding requirements. May need splitting.

💡 Recommendation:
   Address HIGH severity gaps before pointing:
   • Missing Acceptance Criteria
     → Schedule 15-min session with PO to define AC
================================================================================
```

## Tips for Success

1. **Run analysis early** - Catch gaps before grooming sessions
2. **Use verbose mode** - Get specific questions to ask stakeholders
3. **Re-run after updates** - Validate that gaps are addressed
4. **Batch analyze** - Find all candidates, prioritize by score
5. **Share reports** - Help team understand readiness standards

## Troubleshooting

**"Missing environment variables"**
- Set `JIRA_EMAIL` and `JIRA_API_TOKEN` in your environment
- Generate token at: https://id.atlassian.com/manage-profile/security/api-tokens

**"No tickets found"**
- Check your JQL syntax
- Verify project key is correct
- Ensure you have permission to view the tickets

**"Low scores for good tickets"**
- Customize `readiness_criteria.md` for your team
- Adjust scoring weights in `analyze_readiness.py`
- Add team-specific patterns

## Contributing

To improve this skill:
1. Document new gap patterns you discover
2. Add team-specific examples to templates
3. Extend detection rules in the analyzer
4. Share learnings with your team

## License

User-created skill for personal/team use.
