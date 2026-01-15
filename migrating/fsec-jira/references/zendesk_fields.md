# Zendesk Jira Custom Field IDs

Discovered custom field IDs for zendesk.atlassian.net instance.

## Common Custom Fields

| Field Name | Field ID | Type | Example Value | CLI Alias |
|------------|----------|------|---------------|-----------|
| Planned / Unplanned Work | `customfield_21659` | option | `{"value":"Planned"}` | `--planned` / `--unplanned` |
| Acceptance Criteria | `customfield_19300` | ADF | Atlassian Document Format | `--acceptance-criteria` |
| Work Attribution | `customfield_21051` | option | `{"value": "Maintenance"}` | `--work-attribution` |
| Story Points | `customfield_10004` | number | `3.0` | `--points` |
| Sprint | `customfield_10009` | array | Sprint names | - |
| Quarter | `customfield_20016` | string | `2025-Q4` | - |
| HeroCoders Checklist | `customfield_21607` | ADF | `[open]`/`[checked]` markers in ADF | `manage_checklist.py` |
| HeroCoders Checklist Summary | `customfield_21653` | string | "Checklist: 0/41" | **Read-only** |

## Field Types and Update Methods

### ADF Fields (Atlassian Document Format)

These fields require special handling - the `jira` CLI `--custom` flag will **hang indefinitely** when updating them.

| Field | Custom Field ID | Update Method |
|-------|----------------|---------------|
| Description | `description` | `jira issue edit -b "text"` (stdin) |
| Acceptance Criteria | `customfield_19300` | Python script `--acceptance-criteria` |
| HeroCoders Checklist | `customfield_21607` | Python script `manage_checklist.py` |
| User Story template | `customfield_21736` | Python script (direct API) |
| Summary template | `customfield_21581` | Python script (direct API) |

**Workaround:** Always use the Python scripts in `scripts/` for ADF fields - they handle the JSON conversion automatically.

### Simple Fields

These can be updated with `jira` CLI or Python scripts:

| Field | Update Method |
|-------|---------------|
| Status | `jira issue edit --status` or `update_ticket.py --status` |
| Priority | `jira issue edit -y` or Python `--priority` |
| Components | `jira issue edit` or Python `--components` |
| Labels | `jira issue edit -l` |
| Story Points | Python script `--points` |

## HeroCoders Checklist

HeroCoders stores checklist data in `customfield_21607` as ADF (Atlassian Document Format) with special text markers:

- `[open]` - unchecked item
- `[checked]` - checked item

The summary field `customfield_21653` displays "Checklist: X/Y" and is **read-only**.

Use `manage_checklist.py` to programmatically add, check, and manage checklist items.

## Usage Examples

### Using CLI Aliases (Recommended)

```bash
# Mark as Planned/Unplanned work
uv run scripts/update_ticket.py FSEC-1234 --planned
uv run scripts/update_ticket.py FSEC-1234 --unplanned

# Set Acceptance Criteria
uv run scripts/update_ticket.py FSEC-1234 --acceptance-criteria "- Tests pass
- Documentation updated"

# Set Work Attribution (valid: "Elective investments", "Maintenance", "Bug Fixes")
uv run scripts/update_ticket.py FSEC-1234 --work-attribution "Maintenance"

# Set Story Points
uv run scripts/update_ticket.py FSEC-1234 --points 3
uv run scripts/update_ticket.py FSEC-1234 --points 5.5

# Combined update
uv run scripts/update_ticket.py FSEC-1234 \
  --components "ZIG" \
  --unplanned \
  --points 2 \
  --acceptance-criteria "- IAM role updated"

# Preview changes without applying (dry run)
uv run scripts/update_ticket.py FSEC-1234 --status "Done" --dry-run
```

### Using Generic Custom Fields

For fields without aliases:
```bash
# Set Story Points
uv run scripts/update_ticket.py FSEC-1234 \
  --custom-field customfield_10004=5.0

# Set Quarter
uv run scripts/update_ticket.py FSEC-1234 \
  --custom-field customfield_20016="2025-Q1"
```

## Field Discovery

```bash
# Search for field by name
uv run scripts/discover_fields.py --search "Sprint"

# Inspect ticket to see all field values
uv run scripts/discover_fields.py --inspect FSEC-1234

# List available components for a project
uv run scripts/discover_fields.py --list-components FSEC
```
