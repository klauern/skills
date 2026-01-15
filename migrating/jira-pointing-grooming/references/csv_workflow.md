# CSV Workflow for Bulk Decisions

This workflow allows bulk decision-making on blocked tickets using spreadsheet applications.

## Overview

Instead of updating tickets one-by-one in Jira, you can:
1. Export blocked tickets to CSV
2. Make decisions in your spreadsheet app (Google Sheets, Excel, Numbers)
3. Import the CSV and apply all decisions at once

## Workflow Steps

### Step 1: Export to CSV

```bash
cd ~/.claude/skills/jira-pointing-grooming/scripts

# Export all blocked tickets
uv run export_blocked_csv.py --output ~/blocked_tickets.csv

# Export only tickets blocked > 30 days
uv run export_blocked_csv.py --min-age-days 30 --output ~/old_blocked.csv

# Export only ancient tickets (> 6 months)
uv run export_blocked_csv.py --min-age-days 180 --output ~/ancient_blocked.csv
```

**CSV Columns**:
- `Key` - Jira ticket key (e.g., FSEC-1234)
- `Summary` - Ticket title
- `Priority` - Priority level
- `Age (days)` - Days since created
- `Age` - Human-readable age (e.g., "2y", "3mo", "1w")
- `Blocker Reason` - Extracted from ticket description/comments
- `Linked Blockers` - Other tickets blocking this one
- `Decision` - **YOUR DECISION** (pre-filled with suggestions)
- `Notes` - **YOUR NOTES** (optional context)

### Step 2: Review and Decide

Open the CSV in your spreadsheet application:

**Decision Options**:
- `CLOSE` - Mark ticket as Done with "Won't Do" resolution
- `UNBLOCK` - Change status to "To Do"
- `DOCUMENT` - Add comment requesting blocker documentation
- `KEEP` - No action (leave blocked)
- (blank) - Skip this ticket

**Suggested Workflow**:
1. Sort by Age (oldest first)
2. Review each ticket's blocker reason
3. Update the Decision column
4. Add notes explaining your reasoning (optional)
5. Save the CSV

**Decision Criteria**:
- **CLOSE**: Ancient tickets (>6mo), no longer relevant, no clear path forward
- **UNBLOCK**: Blocker is resolved (check Linked Blockers status)
- **DOCUMENT**: Unclear why it's blocked, no linked tickets, vague blocker reason
- **KEEP**: Valid blocker, actively being worked on, clear reason

### Step 3: Preview Changes (Dry Run)

Always preview before applying:

```bash
uv run apply_decisions_csv.py ~/blocked_tickets.csv --dry-run
```

This shows:
- Breakdown by decision type
- Which tickets will be affected
- What action will be taken on each
- Total count

**Review the preview carefully** - once applied, actions cannot be easily undone.

### Step 4: Apply Decisions

After reviewing the dry-run output:

```bash
# With confirmation prompt
uv run apply_decisions_csv.py ~/blocked_tickets.csv

# Skip confirmation (use with caution!)
uv run apply_decisions_csv.py ~/blocked_tickets.csv --yes
```

**What Happens**:

For each decision type, the script:

**CLOSE**:
1. Adds comment explaining closure (includes your notes if provided)
2. Marks ticket as Done with "Won't Do" resolution

**UNBLOCK**:
1. Adds comment explaining unblock (includes your notes if provided)
2. Changes status to "To Do"

**DOCUMENT**:
1. Adds comment requesting blocker documentation
2. Includes template for what information is needed
3. Suggests next steps (close if no longer needed, unblock if resolved)

**KEEP**:
- No action (these are filtered out automatically)

### Step 5: Verify Results

Check the summary output:
```
================================================================================
SUMMARY
================================================================================
✅ Success: 28
❌ Failed: 2
⚠️  Skipped: 1
```

- **Success**: Action completed
- **Failed**: Error occurred (check error message)
- **Skipped**: Invalid decision or blank

## Examples

### Example 1: Close Ancient Tickets

```bash
# Export tickets blocked > 6 months
uv run export_blocked_csv.py --min-age-days 180 --output ancient.csv

# Open ancient.csv, review, verify all have CLOSE decision
# Add notes explaining why they should be closed

# Preview
uv run apply_decisions_csv.py ancient.csv --dry-run

# Apply
uv run apply_decisions_csv.py ancient.csv
```

### Example 2: Mixed Decisions

```bash
# Export all blocked tickets
uv run export_blocked_csv.py --output blocked.csv

# Open blocked.csv in spreadsheet app
# Sort by age and linked blockers
# Make decisions:
#   - CLOSE for >1 year old with no linked blockers
#   - UNBLOCK for tickets where blockers are Done/Resolved
#   - DOCUMENT for tickets with unclear blocker reasons
#   - KEEP for valid blockers

# Preview
uv run apply_decisions_csv.py blocked.csv --dry-run

# Review preview output carefully
# Apply if everything looks good
uv run apply_decisions_csv.py blocked.csv
```

### Example 3: Iterative Approach

```bash
# Export all blocked
uv run export_blocked_csv.py --output blocked_all.csv

# Make a copy for first batch (only ancient tickets)
# Edit only ancient tickets, set others to blank
# Save as blocked_ancient.csv

# Apply ancient tickets first
uv run apply_decisions_csv.py blocked_ancient.csv

# Later, make another pass for recent tickets
# Edit blocked_all.csv again
# Save as blocked_recent.csv
uv run apply_decisions_csv.py blocked_recent.csv
```

## Tips and Best Practices

### Spreadsheet Tips

**Sorting**:
- Sort by Age (days) descending to see oldest first
- Sort by Decision to group by action type

**Filtering**:
- Filter "Linked Blockers" != "None" to see tickets with dependencies
- Filter "Blocker Reason" contains "No documented" to find undocumented blockers

**Formulas** (Google Sheets / Excel):
```
# Suggest CLOSE if age > 180 days and no linked blockers
=IF(AND(D2>180, G2="None"), "CLOSE", "")

# Suggest UNBLOCK if linked blocker contains "Resolved" or "Done"
=IF(OR(ISNUMBER(SEARCH("Resolved",G2)), ISNUMBER(SEARCH("Done",G2))), "UNBLOCK", "")
```

### Safety Tips

1. **Always use --dry-run first** - Preview before applying
2. **Start with small batches** - Test with 5-10 tickets first
3. **Be conservative with CLOSE** - When in doubt, use DOCUMENT instead
4. **Add notes for controversial decisions** - Explain your reasoning
5. **Keep the original CSV** - Save a backup before editing
6. **Review Linked Blockers** - Check if blockers are actually resolved

### Collaboration

The CSV workflow is great for team collaboration:

1. Export CSV and share with team
2. Team members add their recommendations in separate columns
3. Discuss decisions in team meeting
4. Finalize Decision column
5. One person runs the apply script

Example collaborative CSV:
```csv
Key,Summary,...,Decision,Notes,John's Rec,Maria's Rec
FSEC-1234,Old ticket,...,CLOSE,"No longer needed",CLOSE,KEEP
FSEC-5678,Recent ticket,...,DOCUMENT,"Need more info",UNBLOCK,DOCUMENT
```

## Troubleshooting

### "No actionable decisions found"

All tickets in CSV have either:
- KEEP decision (intentionally no action)
- Blank/empty decision
- Invalid decision value

**Fix**: Review Decision column and ensure valid values (CLOSE, UNBLOCK, DOCUMENT)

### "Failed to close" or "Failed to unblock"

Jira API error. Common causes:
- Permissions issue (can't transition or close tickets)
- Workflow doesn't support the transition
- Ticket is in a status that can't transition to Done/To Do

**Fix**: Check error message, verify Jira permissions, try --dry-run to see if issue persists

### "Unknown decision" warning

Decision column contains invalid value (not CLOSE, UNBLOCK, DOCUMENT, or KEEP).

**Fix**: Correct the Decision value or leave blank to skip

### Script hangs or times out

Large CSV with many actions, or Jira is slow.

**Fix**:
- Split CSV into smaller batches
- Retry failed tickets separately
- Check Jira status page for outages

## Advanced Usage

### Custom Export Filters

You can manually edit the JQL in `export_blocked_csv.py`:

```python
# Add custom filters
jql = f'project = {project} AND status = Blocked'
jql += ' AND priority = High'  # Only high priority
jql += ' AND labels = needs-review'  # Specific label
```

### Custom Decision Types

To add new decision types, edit `apply_decisions_csv.py`:

1. Add new decision to `valid_decisions` list
2. Create new `apply_decision_X()` function
3. Add to decision mapping in `apply_decisions()`

Example: Add "REASSIGN" decision:

```python
def apply_decision_reassign(client, key, notes, dry_run):
    """Reassign ticket to different owner."""
    # Implementation here
    pass
```

## Version Control

Consider version controlling your CSVs:

```bash
# Save with timestamp
cp blocked_tickets.csv blocked_tickets_$(date +%Y%m%d).csv

# Or use git
git add blocked_tickets.csv
git commit -m "Blocked tickets cleanup decisions - 2024-01-15"
```

This provides:
- Audit trail of decisions
- Ability to revert if needed
- History of cleanup efforts over time

## Integration with Other Tools

The CSV format makes it easy to integrate with other tools:

### Import to Google Sheets
1. Open Google Sheets
2. File → Import → Upload → Select CSV
3. Use filters, pivot tables, charts

### Import to Jira (for viewing)
Use Jira's import feature to create a temporary project for review.

### Export to Reports
Use the CSV for monthly cleanup reports:
- How many tickets closed?
- How many unblocked?
- Average age of closed tickets?

## Summary

The CSV workflow is ideal for:
- ✅ Bulk cleanup of blocked tickets
- ✅ Team collaboration on decisions
- ✅ Audit trail of actions
- ✅ Iterative decision-making
- ✅ Safe preview before applying

Remember:
1. Export → Edit → Dry-run → Apply
2. Always start with --dry-run
3. Be conservative with CLOSE decisions
4. Document your reasoning in Notes
5. Keep backups of CSVs
