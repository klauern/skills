# CLI Reference

Complete command reference for jira-team-workflow scripts.

## create_ticket.py

Create new Jira tickets with support for all issue types.

### Basic Usage

```bash
# Create a task (auto-assigns to you)
uv run scripts/create_ticket.py --summary "Fix login bug" --type "Task"

# Create different issue types
uv run scripts/create_ticket.py --summary "New feature" --type "Story"
uv run scripts/create_ticket.py --summary "Fix crash" --type "Bug"
uv run scripts/create_ticket.py --summary "Research auth options" --type "Spike"
uv run scripts/create_ticket.py --summary "Major initiative" --type "Epic"
```

### Sub-Tasks

```bash
# Create sub-task under a parent
uv run scripts/create_ticket.py --summary "Write tests" --type "Sub-Task" --parent FSEC-1234
uv run scripts/create_ticket.py --summary "Write tests" --type "Sub-Task" --parent 1234
```

### Full Options

```bash
uv run scripts/create_ticket.py \
  --summary "Implement user auth" \
  --type "Story" \
  --description "Detailed description here" \
  --components "ZIG,IAM" \
  --priority "High" \
  --planned \
  --work-attribution "Maintenance" \
  --points 5 \
  --acceptance-criteria "- Tests pass\n- Docs updated"
```

### FSEC Field Aliases

```bash
# Planned / Unplanned Work
uv run scripts/create_ticket.py --summary "..." --planned
uv run scripts/create_ticket.py --summary "..." --unplanned

# Work Attribution
# Valid: "Elective investments", "Maintenance", "Bug Fixes"
uv run scripts/create_ticket.py --summary "..." --work-attribution "Maintenance"

# Story Points
uv run scripts/create_ticket.py --summary "..." --points 3
```

### Dry Run (Preview)

```bash
# Preview what would be created without making changes
uv run scripts/create_ticket.py --summary "Test" --type "Task" --dry-run
```

### Assignee Options

```bash
# Auto-assigns to you by default
uv run scripts/create_ticket.py --summary "..."

# Don't assign to anyone
uv run scripts/create_ticket.py --summary "..." --no-assign
```

## fetch_ticket.py

Display ticket details with components, comments, and custom fields.

```bash
uv run scripts/fetch_ticket.py FSEC-1234
uv run scripts/fetch_ticket.py 1234  # Uses JIRA_DEFAULT_PROJECT
```

**Output includes:**
- Summary and description
- Status, priority, assignee
- Components and labels
- Custom field values
- Recent comments

## update_ticket.py

Update ticket fields, status, resolution, and comments.

### Status and Resolution

```bash
# Start work
uv run scripts/update_ticket.py FSEC-1234 --status "In Progress"

# Complete work
uv run scripts/update_ticket.py FSEC-1234 --status "Done" --resolution "Done"

# Close as Won't Do
uv run scripts/update_ticket.py FSEC-1234 \
  --status "Done" \
  --resolution "Won't Do" \
  --comment "Not needed - fixed by JIRA-5678"

# Close as Duplicate
uv run scripts/update_ticket.py FSEC-1234 \
  --status "Done" \
  --resolution "Duplicate" \
  --comment "Duplicate of FSEC-5678"
```

### Components and Priority

```bash
# Set components (comma-separated)
uv run scripts/update_ticket.py FSEC-1234 --components "AFT,Atlantis"

# Update priority
uv run scripts/update_ticket.py FSEC-1234 --priority "High"
```

### FSEC Field Aliases

Shortcuts for common FSEC custom fields:

```bash
# Planned / Unplanned Work
uv run scripts/update_ticket.py FSEC-1234 --planned
uv run scripts/update_ticket.py FSEC-1234 --unplanned

# Acceptance Criteria (supports multiline)
uv run scripts/update_ticket.py FSEC-1234 --acceptance-criteria "- Tests pass
- Documentation updated
- PR approved"

# Work Attribution
# Valid: "Elective investments", "Maintenance", "Bug Fixes"
uv run scripts/update_ticket.py FSEC-1234 --work-attribution "Maintenance"
```

### Generic Custom Fields

For fields without aliases:

```bash
uv run scripts/update_ticket.py FSEC-1234 \
  --custom-field 'customfield_10004=5.0'  # Story points

uv run scripts/update_ticket.py FSEC-1234 \
  --custom-field 'customfield_21659={"value":"Planned"}'  # JSON format
```

### Comments

```bash
# Add standalone comment
uv run scripts/update_ticket.py FSEC-1234 \
  --comment "Completed API integration. Ready for testing."

# Comment with status change
uv run scripts/update_ticket.py FSEC-1234 \
  --status "In Review" \
  --comment "PR #123 ready for review"
```

### Story Points

```bash
uv run scripts/update_ticket.py FSEC-1234 --points 3
uv run scripts/update_ticket.py FSEC-1234 --points 5.5
```

### Combined Updates

```bash
uv run scripts/update_ticket.py FSEC-1234 \
  --components "ZIG" \
  --unplanned \
  --acceptance-criteria "- IAM role updated" \
  --points 2 \
  --comment "Created from GH Actions failure"
```

### Dry Run (Preview)

```bash
# Preview what would be updated without making changes
uv run scripts/update_ticket.py FSEC-1234 --status "Done" --dry-run
uv run scripts/update_ticket.py FSEC-1234 --points 3 --components "ZIG" --dry-run
```

## discover_fields.py

Find custom field IDs and inspect ticket field values.

```bash
# Search for fields by name
uv run scripts/discover_fields.py --search "Work Attribution"
uv run scripts/discover_fields.py --search "Sprint"

# List all custom fields
uv run scripts/discover_fields.py --all-custom

# List all fields (including standard)
uv run scripts/discover_fields.py --all

# Inspect ticket to see field values and IDs
uv run scripts/discover_fields.py --inspect FSEC-1234

# List available components for a project
uv run scripts/discover_fields.py --list-components FSEC
```

## manage_checklist.py

Manage rich-text checklist field (`customfield_21607`).

> **Note:** This script manages a **rich-text bullets field**, NOT the HeroCoders Checklist addon. The HeroCoders addon uses a proprietary REST API. For interactive HeroCoders checklist management, use the Jira UI directly.

```bash
# View current checklist
uv run scripts/manage_checklist.py FSEC-1234 --show

# Add checklist items
uv run scripts/manage_checklist.py FSEC-1234 \
  --add "Complete implementation" \
  --add "Write tests" \
  --add "Update documentation"

# Add section with items
uv run scripts/manage_checklist.py FSEC-1234 \
  --section "Phase 1" \
  --add "Design review" \
  --add "Implementation"

# Mark items as complete (by number)
uv run scripts/manage_checklist.py FSEC-1234 --check 1 --check 3

# Uncheck items
uv run scripts/manage_checklist.py FSEC-1234 --uncheck 2
```

## jira_api.py

Low-level API operations and JQL search.

### JQL Queries

```bash
# Tickets without components
uv run scripts/jira_api.py search "project = FSEC AND component is EMPTY"

# My open tickets
uv run scripts/jira_api.py search \
  "project = FSEC AND assignee = currentUser() AND status != Done"

# Recently updated
uv run scripts/jira_api.py search \
  "project = FSEC AND updated >= -7d ORDER BY updated DESC"

# Multi-project search
uv run scripts/jira_api.py search \
  "project in (FSEC, PLAN, LOCKBOX) AND status = 'In Progress'"
```

## Troubleshooting

**Authentication errors**: Verify environment variables are set:
```bash
echo $JIRA_EMAIL $JIRA_API_TOKEN
```

**Status transition failures**: Check available transitions:
```bash
uv run scripts/jira_api.py get FSEC-1234 | grep -i transition
```

**Custom field not found**: Inspect ticket to find correct field ID:
```bash
uv run scripts/discover_fields.py --inspect FSEC-1234
```

**Permission errors**: Ensure your API token has project permissions.
