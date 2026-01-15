---
name: fsec-jira
description: Manage Jira tickets for Foundation Security (FSEC) team and related projects (PLAN, LOCKBOX, SECURE). Use when user mentions Jira tickets by key (FSEC-1234, PLAN-567) or number (1234), or requests ticket operations like create ticket, create sub-task, review ticket, analyze ticket, close ticket, update status, set components, mark as planned/unplanned, add comments, manage checklist items, add checklist, check off items, discover custom fields, or build todo lists from ticket requirements.
---

# FSEC Jira Workflow

Manage Jira tickets with CLI scripts using `uv run`.

## Setup

```bash
export JIRA_URL="https://zendesk.atlassian.net"
export JIRA_EMAIL="$(whoami)@zendesk.com"
export JIRA_API_TOKEN="your_token"  # https://id.atlassian.com/manage-profile/security/api-tokens
export JIRA_DEFAULT_PROJECT="FSEC"
```

## Quick Reference

| Task | Command |
|------|---------|
| **Create ticket** | `uv run scripts/create_ticket.py --summary "Title" --type "Task"` |
| **Create sub-task** | `uv run scripts/create_ticket.py --summary "Title" --type "Sub-Task" --parent 1234` |
| Fetch ticket | `uv run scripts/fetch_ticket.py 1234` |
| Start work | `uv run scripts/update_ticket.py 1234 --status "In Progress"` |
| Close ticket | `uv run scripts/update_ticket.py 1234 --status "Done" --resolution "Done"` |
| Set components | `uv run scripts/update_ticket.py 1234 --components "ZIG,IAM"` |
| Mark unplanned | `uv run scripts/update_ticket.py 1234 --unplanned` |
| Set acceptance criteria | `uv run scripts/update_ticket.py 1234 --acceptance-criteria "- Tests pass"` |
| Set work attribution | `uv run scripts/update_ticket.py 1234 --work-attribution "Maintenance"` |
| **Set story points** | `uv run scripts/update_ticket.py 1234 --points 3` |
| **Preview changes** | `uv run scripts/update_ticket.py 1234 --status "Done" --dry-run` |
| List components | `uv run scripts/discover_fields.py --list-components FSEC` |
| Find field ID | `uv run scripts/discover_fields.py --search "Sprint"` |

## FSEC Field Aliases

| Alias | Field |
|-------|-------|
| `--planned` / `--unplanned` | Planned / Unplanned Work |
| `--acceptance-criteria TEXT` | Acceptance Criteria |
| `--work-attribution TEAM` | Work Attribution |
| `--points N` | Story Points |
| `--dry-run` | Preview changes without applying |

## Scripts

| Script | Purpose |
|--------|---------|
| `create_ticket.py` | **Create new tickets** (Task, Story, Bug, Sub-Task, etc.) |
| `fetch_ticket.py` | Display ticket details |
| `update_ticket.py` | Update status, fields, comments |
| `discover_fields.py` | Find field IDs, list components |
| `manage_checklist.py` | Manage rich-text checklist field (see note below) |
| `jira_api.py` | JQL search, raw API |

> **Note on Checklists:** `manage_checklist.py` manages a **rich-text bullets field** (`customfield_21607`), NOT the HeroCoders Checklist addon. The HeroCoders addon uses a proprietary REST API that is not currently supported. For interactive HeroCoders checklist management, use the Jira UI directly.

## Troubleshooting

**Authentication errors:**
```bash
# Verify environment variables are set
echo $JIRA_EMAIL $JIRA_API_TOKEN
```

**Status transition failures:**
```bash
# Check available transitions for the ticket
uv run scripts/jira_api.py get FSEC-1234 | grep -i transition
```

**Custom field not found:**
```bash
# Inspect ticket to find correct field ID
uv run scripts/discover_fields.py --inspect FSEC-1234
```

**Permission errors:**
- Ensure your API token has project permissions
- Check component/field restrictions in Jira

## Related Skills

| Skill | Use For |
|-------|---------|
| [jira-review](../jira-review.md) | Building todo lists from tickets |
| [jira-interaction](../jira-interaction.md) | go-jira CLI for quick operations |
| [jira-pointing-grooming](../jira-pointing-grooming/SKILL.md) | Grooming and pointing workflows |

**When to use go-jira CLI vs Python scripts:**

| go-jira CLI | Python Scripts |
|-------------|----------------|
| Quick ticket viewing | FSEC custom fields |
| Adding comments | Creating tickets with all fields |
| Simple status updates | Dry-run previews |
| | HeroCoders checklists |
| | Bulk/programmatic operations |

## More Info

- [CLI Reference](references/cli_reference.md) - Full command documentation
- [Zendesk Fields](references/zendesk_fields.md) - Custom field IDs
- [Workflow Patterns](references/workflow_patterns.md) - Common workflows
