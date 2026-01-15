# Jira Workflow Patterns

Common workflows for FSEC team Jira operations.

## Ticket Analysis Workflow

Start work on a ticket:

```bash
# 1. Fetch and analyze
uv run fetch_ticket.py FSEC-1234

# 2. Build todo list from:
#    - Description and acceptance criteria
#    - Comments for clarifications
#    - Components to understand scope

# 3. Mark as in progress
uv run update_ticket.py FSEC-1234 --status "In Progress"
```

## Common Status Transitions

```bash
# Start work
uv run update_ticket.py FSEC-1234 --status "In Progress"

# Complete work
uv run update_ticket.py FSEC-1234 --status "Done" --resolution "Done"

# Close as Won't Do
uv run update_ticket.py FSEC-1234 --status "Done" --resolution "Won't Do" \
  --comment "Not needed - fixed by JIRA-5678"
```

## Field Updates

```bash
# Update components (single or multiple)
uv run update_ticket.py FSEC-1234 --components "AFT,Atlantis"

# Update priority
uv run update_ticket.py FSEC-1234 --priority "High"

# Update custom fields (after discovering field IDs)
uv run update_ticket.py FSEC-1234 \
  --custom-field customfield_xxxxx="Planned"

# Combined update
uv run update_ticket.py FSEC-1234 \
  --components "AFT" \
  --priority "High" \
  --custom-field customfield_xxxxx="Planned"
```

## Custom Field Discovery

```bash
# Search for specific field
uv run discover_fields.py --search "Work Attribution"
uv run discover_fields.py --search "Sprint"

# List all custom fields
uv run discover_fields.py --all-custom

# Inspect ticket to see field values and IDs
uv run discover_fields.py --inspect FSEC-1234
```

## Environment Setup

Set in `~/.zshrc` or `~/.bashrc`:

```bash
export JIRA_URL="https://zendesk.atlassian.net"
export JIRA_EMAIL="your.email@zendesk.com"
export JIRA_API_TOKEN="your_api_token"
export JIRA_DEFAULT_PROJECT="FSEC"
```

With `JIRA_DEFAULT_PROJECT` set, use short forms:
```bash
uv run fetch_ticket.py 1234  # Same as FSEC-1234
```

## JQL Queries

```bash
# Tickets without components
uv run jira_api.py search "project = FSEC AND component is EMPTY"

# My open tickets
uv run jira_api.py search "project = FSEC AND assignee = currentUser() AND status != Done"

# Multi-project search
uv run jira_api.py search "project in (FSEC, PLAN, LOCKBOX) AND status = 'In Progress'"
```
