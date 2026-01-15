#!/usr/bin/env python3
"""
Discover Jira custom field IDs by searching field names.

Usage:
    # Search for specific fields
    uv run discover_fields.py --search "Work Attribution"
    uv run discover_fields.py --search "Sprint"

    # List all custom fields
    uv run discover_fields.py --all-custom

    # List all fields
    uv run discover_fields.py --all

    # Get field values from a ticket (useful for understanding structure)
    uv run discover_fields.py --inspect FSEC-1234

Environment variables:
    JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
"""

# /// script
# dependencies = [
#   "atlassian-python-api>=4.0.3",
#   "click>=8.1.7",
#   "prettytable>=3.11.0",
# ]
# ///

import sys
import json
from typing import List, Dict, Any, Optional
import click
from atlassian import Jira
from prettytable import PrettyTable

# Import shared utilities from jira_api
from jira_api import get_client, normalize_issue_key


def search_fields(client: Jira, query: str) -> List[Dict[str, Any]]:
    """Search for fields matching query.

    Args:
        client: Jira client
        query: Search query (case-insensitive)

    Returns:
        List of matching field definitions
    """
    all_fields = client.get_all_fields()
    query_lower = query.lower()

    matches = []
    for field in all_fields:
        field_name = field.get('name', '').lower()
        field_id = field.get('id', '').lower()

        if query_lower in field_name or query_lower in field_id:
            matches.append(field)

    return matches


def display_fields(fields: List[Dict[str, Any]], title: str) -> None:
    """Display fields in a formatted table.

    Args:
        fields: List of field definitions
        title: Table title
    """
    if not fields:
        click.echo(f"\n{title}: No fields found\n")
        return

    table = PrettyTable()
    table.field_names = ["Field ID", "Field Name", "Type", "Custom"]
    table.align["Field ID"] = "l"
    table.align["Field Name"] = "l"
    table.align["Type"] = "l"
    table.align["Custom"] = "c"

    for field in fields:
        field_id = field.get('id', 'N/A')
        field_name = field.get('name', 'N/A')
        field_type = field.get('schema', {}).get('type', 'N/A')
        is_custom = '✓' if field.get('custom', False) else ''

        table.add_row([field_id, field_name, field_type, is_custom])

    click.echo(f"\n{title} ({len(fields)} fields)")
    click.echo(table)
    click.echo()


def list_project_components(client: Jira, project_key: str) -> None:
    """List all components for a project.

    Args:
        client: Jira client
        project_key: Project key (e.g., 'FSEC')
    """
    try:
        # Use the Jira REST API to get components
        components = client.get_project_components(project_key)

        if not components:
            click.echo(f"\n{project_key} has no components configured\n")
            return

        table = PrettyTable()
        table.field_names = ["Component Name", "Lead", "Description"]
        table.align["Component Name"] = "l"
        table.align["Lead"] = "l"
        table.align["Description"] = "l"
        table.max_width["Description"] = 50

        for comp in components:
            name = comp.get('name', 'N/A')
            lead = comp.get('lead', {}).get('displayName', '-') if comp.get('lead') else '-'
            desc = comp.get('description', '-') or '-'
            if len(desc) > 50:
                desc = desc[:47] + '...'
            table.add_row([name, lead, desc])

        click.echo(f"\nComponents for {project_key} ({len(components)} total)")
        click.echo(table)
        click.echo()

    except Exception as e:
        click.echo(f"❌ Error fetching components for {project_key}: {e}", err=True)
        sys.exit(1)


def inspect_ticket_fields(client: Jira, issue_key: str) -> None:
    """Inspect all field values on a specific ticket.

    Args:
        client: Jira client
        issue_key: Issue key
    """
    issue = client.issue(issue_key)
    fields = issue.get('fields', {})

    # Get field metadata to map IDs to names
    all_fields = {f['id']: f['name'] for f in client.get_all_fields()}

    click.echo(f"\n{'='*80}")
    click.echo(f"  Field Values for {issue_key}")
    click.echo(f"{'='*80}\n")

    # Standard fields first
    standard_fields = {
        'summary': 'Summary',
        'description': 'Description',
        'status': 'Status',
        'priority': 'Priority',
        'issuetype': 'Issue Type',
        'assignee': 'Assignee',
        'reporter': 'Reporter',
        'components': 'Components',
        'labels': 'Labels',
    }

    click.echo("📋 Standard Fields:")
    for field_id, field_label in standard_fields.items():
        value = fields.get(field_id)
        if value:
            if isinstance(value, dict) and 'name' in value:
                click.echo(f"  {field_label}: {value['name']}")
            elif isinstance(value, dict) and 'displayName' in value:
                click.echo(f"  {field_label}: {value['displayName']}")
            elif isinstance(value, list) and value:
                if isinstance(value[0], dict) and 'name' in value[0]:
                    names = ', '.join([item['name'] for item in value])
                    click.echo(f"  {field_label}: {names}")
                else:
                    click.echo(f"  {field_label}: {value}")
            else:
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + '...'
                click.echo(f"  {field_label}: {value_str}")

    click.echo()

    # Custom fields
    custom_fields = {k: v for k, v in fields.items() if k.startswith('customfield_') and v is not None}

    if custom_fields:
        click.echo("🔧 Custom Fields:")
        for field_id, field_value in custom_fields.items():
            field_name = all_fields.get(field_id, field_id)

            # Format based on type
            if isinstance(field_value, dict):
                if 'name' in field_value:
                    formatted = field_value['name']
                elif 'value' in field_value:
                    formatted = field_value['value']
                else:
                    formatted = json.dumps(field_value, indent=2)
            elif isinstance(field_value, list):
                if field_value and isinstance(field_value[0], dict) and 'name' in field_value[0]:
                    formatted = ', '.join([item['name'] for item in field_value])
                else:
                    formatted = json.dumps(field_value, indent=2)
            else:
                formatted = str(field_value)

            # Truncate if too long
            if len(formatted) > 100:
                formatted = formatted[:100] + '...'

            click.echo(f"  {field_id} ({field_name}): {formatted}")

        click.echo()


@click.command()
@click.option('--search', help='Search for fields by name')
@click.option('--all-custom', is_flag=True, help='List all custom fields')
@click.option('--all', 'list_all', is_flag=True, help='List all fields')
@click.option('--inspect', help='Inspect field values on a specific ticket')
@click.option('--list-components', 'components_project', help='List available components for a project (e.g., FSEC)')
def main(search: Optional[str], all_custom: bool, list_all: bool, inspect: Optional[str], components_project: Optional[str]):
    """Discover Jira field IDs and inspect field values.

    Examples:
        # Search for specific field
        discover_fields.py --search "Sprint"

        # List all custom fields
        discover_fields.py --all-custom

        # Inspect ticket to see field values
        discover_fields.py --inspect FSEC-1234

        # List components for a project
        discover_fields.py --list-components FSEC
    """
    try:
        client = get_client()

        if components_project:
            list_project_components(client, components_project.upper())
            return

        if inspect:
            issue_key = normalize_issue_key(inspect)
            inspect_ticket_fields(client, issue_key)
            return

        all_fields = client.get_all_fields()

        if search:
            matches = search_fields(client, search)
            display_fields(matches, f"Fields matching '{search}'")

        elif all_custom:
            custom_fields = [f for f in all_fields if f.get('custom', False)]
            display_fields(custom_fields, "All Custom Fields")

        elif list_all:
            display_fields(all_fields, "All Fields")

        else:
            click.echo("❌ Error: Must specify --search, --all-custom, --all, --inspect, or --list-components", err=True)
            click.echo("Use --help for usage information", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
