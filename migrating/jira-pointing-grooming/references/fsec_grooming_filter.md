# FSEC Team Grooming Filter

This document explains the default grooming filter used by the FSEC team and how it's codified in this skill.

## Source

**Jira Board URL**: https://zendesk.atlassian.net/jira/software/c/projects/FSEC/list

**Filter Parameters** (from URL):
```
filter=type in (Spike, Story, Task)
       AND status in (Backlog, "In Progress", Blocked, Intake,
                      "Ready to Refine", "Ready to Ship", Refined,
                      "To Do", Shipping, Testing, Review)
sortBy=updated
direction=DESC
groupBy=customfield_10004
```

## JQL Query

The filter translates to this JQL:

```sql
project = FSEC
AND type in (Spike, Story, Task)
AND status in (Backlog, "In Progress", Blocked, Intake,
               "Ready to Refine", "Ready to Ship", Refined,
               "To Do", Shipping, Testing, Review)
ORDER BY updated DESC
```

## What This Includes

### Issue Types
- **Spike**: Research or investigation work
- **Story**: User-facing features
- **Task**: Technical work or improvements

**Excluded**:
- Epic (too large for pointing)
- Sub-task (pointed via parent)
- Bug (may use different workflow)

### Statuses (Workflow States)

The filter includes ALL active workflow states for grooming:

1. **Backlog** - Unrefined, not yet groomed
2. **Intake** - Recently created, needs initial triage
3. **Ready to Refine** - Flagged for grooming session
4. **Refined** - Groomed but not yet estimated/pointed
5. **To Do** - Ready for sprint planning
6. **In Progress** - Actively being worked on
7. **Review** - Code review or peer review
8. **Testing** - QA or testing phase
9. **Ready to Ship** - Ready for deployment
10. **Shipping** - Being deployed
11. **Blocked** - Waiting on dependencies

**Excluded**:
- Done (completed work)
- Closed (archived)
- Cancelled (abandoned)

### Sort Order

**Sorted by**: `updated DESC` (most recently updated first)

**Why this sorting?**
- Shows tickets with recent activity/comments
- Surfaces tickets that stakeholders are actively discussing
- Helps identify tickets with growing scope (many recent updates)
- Prioritizes tickets that need immediate attention

### Grouping

**Grouped by**: `customfield_10004` (likely Story Points field)

**Why this grouping?**
- Separates estimated from unestimated tickets
- Helps identify tickets ready for pointing vs. needing grooming
- Shows distribution of work across point values

## How This Differs from Other Filters

### vs. "Needs More Info" Filter
```sql
-- Too narrow - misses many tickets needing grooming
status = "Needs More Info"
```

The grooming filter is broader because tickets can need grooming in ANY status, not just "Needs More Info".

### vs. "Backlog Only" Filter
```sql
-- Too narrow - misses in-flight work needing refinement
status = "Backlog"
```

The grooming filter includes in-progress work because:
- Scope may have changed during implementation
- Dependencies may have been discovered
- Original estimates may need revision

### vs. "All Open Tickets" Filter
```sql
-- Too broad - includes Bugs, Epics, Sub-tasks
status != Done AND status != Closed
```

The grooming filter focuses on work that:
- Can be estimated (excludes Epics)
- Is independently trackable (excludes Sub-tasks)
- Follows the standard workflow (may exclude Bugs)

## Usage in Scripts

### Default Behavior
```bash
# Automatically uses FSEC grooming filter
uv run find_grooming_candidates.py
```

### With Additional Filters
```bash
# Grooming filter + only unestimated
uv run find_grooming_candidates.py --unestimated

# Grooming filter + specific label
uv run find_grooming_candidates.py --label needs-grooming
```

### Disable Grooming Filter
```bash
# Use custom filters instead
uv run find_grooming_candidates.py --no-grooming-filter --status "Needs More Info"
```

## Customization for Other Projects

To use this filter for other projects, update the script:

```python
# In find_grooming_candidates.py
def get_fsec_grooming_filter(project: str = 'FSEC') -> str:
    """Get the standard grooming filter."""
    return (
        f'project = {project} AND '
        f'type in (Spike, Story, Task) AND '
        f'status in (Backlog, "In Progress", Blocked, Intake, '
        f'"Ready to Refine", "Ready to Ship", Refined, "To Do", '
        f'Shipping, Testing, Review) '
        f'ORDER BY updated DESC'
    )
```

**For other teams**: Adjust the status list to match your workflow states.

## Why This Filter Matters for Grooming

This filter is specifically designed for grooming sessions because it:

1. **Captures work at all stages** - Not just backlog, but in-flight work too
2. **Focuses on estimatable work** - Only Spikes, Stories, and Tasks
3. **Shows recent activity** - Sorted by updated date catches growing scope
4. **Matches team's Jira view** - Consistency between CLI and web interface
5. **Excludes completed work** - No noise from Done/Closed tickets

## Grooming Workflow Integration

### Pre-Grooming (Week Before)
```bash
# Find all candidates
uv run find_grooming_candidates.py --limit 100

# Identify unestimated tickets
uv run find_grooming_candidates.py --unestimated
```

### During Grooming Session
1. Use Jira board view: https://zendesk.atlassian.net/jira/software/c/projects/FSEC/list
2. Walk through tickets sorted by updated date
3. For unclear tickets: `uv run analyze_readiness.py FSEC-XXXX`

### Post-Grooming
```bash
# Verify all groomed tickets are ready
for ticket in FSEC-1234 FSEC-1235 FSEC-1236; do
  uv run analyze_readiness.py $ticket
done
```

## Filter Maintenance

**When to update this filter**:
- Team adds new workflow states
- Team changes issue type conventions
- Team adopts new grooming practices
- Jira board configuration changes

**How to update**:
1. Export filter from Jira board: "..." menu → "Export" → "Copy JQL"
2. Update `get_fsec_grooming_filter()` in `find_grooming_candidates.py`
3. Update documentation in this file
4. Update `SKILL.md` with new filter description

## Reference

- **Jira Board**: https://zendesk.atlassian.net/jira/software/c/projects/FSEC/list
- **Project**: FSEC (Foundation Security)
- **Team**: Guardians
- **Maintained by**: Engineering team
