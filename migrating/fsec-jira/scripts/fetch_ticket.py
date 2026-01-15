#!/usr/bin/env python3
"""
Fetch and display Jira ticket details in a structured format.

Usage:
    uv run fetch_ticket.py FSEC-1234
    uv run fetch_ticket.py 1234  # Assumes FSEC project
    uv run fetch_ticket.py PLAN-567

Environment variables:
    JIRA_URL: Jira instance URL (defaults to https://zendesk.atlassian.net)
    JIRA_EMAIL: User email for authentication
    JIRA_API_TOKEN: API token
    JIRA_DEFAULT_PROJECT: Default project prefix (defaults to FSEC)
"""

# /// script
# dependencies = [
#   "atlassian-python-api>=4.0.3",
#   "click>=8.1.7",
#   "prettytable>=3.11.0",
# ]
# ///

import os
import sys
from typing import Dict, Any
import click
from prettytable import PrettyTable

# Import shared utilities from jira_api
from jira_api import (
    get_client,
    get_jira_url,
    normalize_issue_key,
    extract_text_from_adf,
)


def format_ticket_details(issue: Dict[str, Any]) -> None:
    """Format and display ticket details.

    Args:
        issue: Issue data from Jira API
    """
    fields = issue['fields']
    key = issue['key']

    # Header
    click.echo(f"\n{'='*80}")
    click.echo(f"  {key}: {fields.get('summary', 'No summary')}")
    click.echo(f"{'='*80}\n")

    # Basic Info Table
    basic_table = PrettyTable()
    basic_table.field_names = ["Field", "Value"]
    basic_table.align["Field"] = "r"
    basic_table.align["Value"] = "l"

    basic_table.add_row(["Status", fields.get('status', {}).get('name', 'Unknown')])
    basic_table.add_row(["Type", fields.get('issuetype', {}).get('name', 'Unknown')])
    basic_table.add_row(["Priority", fields.get('priority', {}).get('name', 'None')])
    basic_table.add_row(["Assignee", fields.get('assignee', {}).get('displayName', 'Unassigned')])
    basic_table.add_row(["Reporter", fields.get('reporter', {}).get('displayName', 'Unknown')])

    # Components
    components = fields.get('components', [])
    if components:
        comp_names = ', '.join([c['name'] for c in components])
        basic_table.add_row(["Components", comp_names])
    else:
        basic_table.add_row(["Components", "❌ None"])

    # Labels
    labels = fields.get('labels', [])
    if labels:
        basic_table.add_row(["Labels", ', '.join(labels)])

    click.echo(basic_table)
    click.echo()

    # Description
    description = fields.get('description')
    if description:
        desc_text = extract_text_from_adf(description)
        if desc_text:
            click.echo("📝 Description:")
            click.echo("-" * 80)
            click.echo(desc_text)
            click.echo("-" * 80)
            click.echo()

    # Custom Fields (common ones)
    custom_fields = {}

    # Try to find common custom fields by name
    for field_key, field_value in fields.items():
        if field_key.startswith('customfield_') and field_value:
            custom_fields[field_key] = field_value

    if custom_fields:
        click.echo("🔧 Custom Fields:")
        for field_key, field_value in custom_fields.items():
            # Try to format based on type
            if isinstance(field_value, dict):
                if 'name' in field_value:
                    click.echo(f"  {field_key}: {field_value['name']}")
                elif 'value' in field_value:
                    click.echo(f"  {field_key}: {field_value['value']}")
                else:
                    click.echo(f"  {field_key}: {field_value}")
            elif isinstance(field_value, list):
                if field_value and isinstance(field_value[0], dict) and 'name' in field_value[0]:
                    names = ', '.join([item['name'] for item in field_value])
                    click.echo(f"  {field_key}: {names}")
                else:
                    click.echo(f"  {field_key}: {field_value}")
            else:
                click.echo(f"  {field_key}: {field_value}")
        click.echo()

    # Comments
    comment_data = fields.get('comment', {})
    comments = comment_data.get('comments', [])
    if comments:
        click.echo(f"💬 Comments ({len(comments)}):")
        click.echo("-" * 80)
        for idx, comment in enumerate(comments[-5:], 1):  # Show last 5
            author = comment.get('author', {}).get('displayName', 'Unknown')
            created = comment.get('created', 'Unknown date')
            body = extract_text_from_adf(comment.get('body', {}))
            click.echo(f"[{idx}] {author} on {created[:10]}:")
            click.echo(f"    {body[:200]}{'...' if len(body) > 200 else ''}")
            click.echo()
        click.echo("-" * 80)

    # URL
    click.echo(f"\n🔗 View in Jira: {get_jira_url()}/browse/{key}\n")


@click.command()
@click.argument('issue_ref')
@click.option('--json', is_flag=True, help='Output raw JSON instead of formatted view')
def main(issue_ref: str, json: bool):
    """Fetch and display Jira ticket details.

    ISSUE_REF can be a full key (FSEC-1234), number (1234), or any project key.
    """
    try:
        issue_key = normalize_issue_key(issue_ref)
        client = get_client()
        issue = client.issue(issue_key)

        if json:
            import json as json_module
            click.echo(json_module.dumps(issue, indent=2))
        else:
            format_ticket_details(issue)

    except Exception as e:
        click.echo(f"❌ Error fetching {issue_ref}: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
