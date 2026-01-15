#!/usr/bin/env python3
"""
Find Jira tickets that need grooming.

By default, uses the FSEC team's actual grooming board filter which matches:
https://zendesk.atlassian.net/jira/software/c/projects/FSEC/list

This includes:
- Issue types: Spike, Story, Task
- Statuses: All active workflow states (Backlog, In Progress, Blocked, etc.)
- Sorted by: Most recently updated

Usage:
    # Use default FSEC grooming filter
    uv run find_grooming_candidates.py

    # Grooming filter + only unestimated tickets
    uv run find_grooming_candidates.py --unestimated

    # Custom filters (disables default grooming filter)
    uv run find_grooming_candidates.py --no-grooming-filter --status "Needs More Info"
    uv run find_grooming_candidates.py --no-grooming-filter --label needs-grooming

Environment variables:
    JIRA_URL: Jira instance URL (defaults to https://zendesk.atlassian.net)
    JIRA_EMAIL: User email for authentication
    JIRA_API_TOKEN: API token from Atlassian account settings
"""

# /// script
# dependencies = [
#   "atlassian-python-api>=4.0.3",
#   "click>=8.1.7",
#   "pydantic>=2.11.0",
# ]
# ///

import os
import sys
from typing import List, Dict, Any
from datetime import datetime
import click
from atlassian import Jira


def get_jira_client() -> Jira:
    """Get configured Jira client."""
    import getpass

    url = os.getenv('JIRA_URL', 'https://zendesk.atlassian.net')

    # Default email to {username}@zendesk.com
    default_email = f"{getpass.getuser()}@zendesk.com"
    email = os.getenv('JIRA_EMAIL', default_email)

    token = os.getenv('JIRA_API_TOKEN', '')

    if not token:
        raise ValueError(
            f"Missing JIRA_API_TOKEN environment variable.\n"
            f"Generate a token at: https://id.atlassian.com/manage-profile/security/api-tokens\n"
            f"Then set: export JIRA_API_TOKEN='your_token_here'"
        )

    return Jira(url=url, username=email, password=token, cloud=True)


def get_fsec_grooming_filter(project: str = 'FSEC') -> str:
    """
    Get the standard FSEC grooming filter.

    This matches the team's actual grooming board filter:
    https://zendesk.atlassian.net/jira/software/c/projects/FSEC/list?filter=...

    Issue types: Spike, Story, Task
    Statuses: All active workflow states except Done
    Sorted by: Most recently updated first
    """
    return (
        f'project = {project} AND '
        f'type in (Spike, Story, Task) AND '
        f'status in (Backlog, "In Progress", Blocked, Intake, '
        f'"Ready to Refine", "Ready to Ship", Refined, "To Do", '
        f'Shipping, Testing, Review) '
        f'ORDER BY updated DESC'
    )


def build_jql(
    project: str = None,
    status: str = None,
    label: str = None,
    unestimated: bool = False,
    issue_type: str = None,
    use_grooming_filter: bool = False
) -> str:
    """Build JQL query based on search criteria."""
    # If using preset grooming filter, return it directly
    if use_grooming_filter:
        base_jql = get_fsec_grooming_filter(project or 'FSEC')

        # Add additional filters if specified
        extra_conditions = []
        if label:
            extra_conditions.append(f'labels = {label}')
        if unestimated:
            extra_conditions.append('("Story Points" IS EMPTY OR "Story Points" = 0)')

        if extra_conditions:
            # Insert extra conditions before ORDER BY
            parts = base_jql.split(' ORDER BY ')
            base_jql = parts[0] + ' AND ' + ' AND '.join(extra_conditions) + ' ORDER BY ' + parts[1]

        return base_jql

    # Custom filter building
    conditions = []

    if project:
        conditions.append(f'project = {project}')

    if status:
        conditions.append(f'status = "{status}"')
    else:
        # Default: statuses that typically need grooming
        conditions.append('status IN ("Needs More Info", "Backlog", "To Do")')

    if label:
        conditions.append(f'labels = {label}')

    if unestimated:
        # Assuming Story Points field - adjust field ID as needed
        conditions.append('("Story Points" IS EMPTY OR "Story Points" = 0)')

    if issue_type:
        conditions.append(f'type = "{issue_type}"')
    else:
        # Exclude certain types that don't typically need estimation
        conditions.append('type NOT IN (Epic, Sub-task)')

    # Order by priority and created date
    jql = ' AND '.join(conditions) + ' ORDER BY priority DESC, created ASC'

    return jql


def format_age(created_str: str) -> str:
    """Format ticket age in human-readable form."""
    try:
        created = datetime.strptime(created_str[:10], '%Y-%m-%d')
        age_days = (datetime.now() - created).days

        if age_days == 0:
            return "Today"
        elif age_days == 1:
            return "1 day"
        elif age_days < 7:
            return f"{age_days} days"
        elif age_days < 30:
            weeks = age_days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''}"
        elif age_days < 365:
            months = age_days // 30
            return f"{months} month{'s' if months > 1 else ''}"
        else:
            years = age_days // 365
            return f"{years} year{'s' if years > 1 else ''}"
    except:
        return "Unknown"


def search_tickets(
    client: Jira,
    jql: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Search for tickets using JQL."""
    fields = ['summary', 'status', 'priority', 'created', 'updated',
              'issuetype', 'labels', 'description']

    result = client.jql(jql, limit=limit, fields=fields)
    return result.get('issues', [])


def format_ticket_list(issues: List[Dict[str, Any]]) -> str:
    """Format ticket list as human-readable text."""
    if not issues:
        return "No tickets found matching criteria.\n"

    lines = []
    lines.append(f"\nFound {len(issues)} ticket(s) needing grooming:\n")
    lines.append(f"{'Key':<15} {'Age':<12} {'Priority':<10} {'Status':<20} {'Summary'}")
    lines.append("-" * 120)

    for issue in issues:
        key = issue['key']
        fields = issue['fields']

        summary = fields.get('summary', 'No summary')[:60]
        priority = fields.get('priority', {}).get('name', 'None')
        status = fields.get('status', {}).get('name', 'Unknown')
        created = fields.get('created', '')
        age = format_age(created)

        lines.append(f"{key:<15} {age:<12} {priority:<10} {status:<20} {summary}")

    lines.append("")
    lines.append("💡 Next Steps:")
    lines.append("   1. Analyze individual tickets: uv run analyze_readiness.py <KEY>")
    lines.append("   2. Prioritize HIGH severity gaps")
    lines.append("   3. Schedule grooming sessions for tickets with missing context")
    lines.append("")

    return "\n".join(lines)


@click.command()
@click.option('--project', '-p', default='FSEC', help='Project key (default: FSEC)')
@click.option('--grooming-filter', '-g', is_flag=True, default=True,
              help='Use FSEC team grooming filter (default: True, use --no-grooming-filter to disable)')
@click.option('--status', '-s', help='Filter by status (overrides grooming filter)')
@click.option('--label', '-l', help='Filter by label (e.g., needs-grooming)')
@click.option('--unestimated', '-u', is_flag=True, help='Only show tickets without story points')
@click.option('--issue-type', '-t', help='Filter by issue type (overrides grooming filter)')
@click.option('--limit', default=50, help='Maximum number of results (default: 50)')
@click.option('--jql', help='Custom JQL query (overrides all other filters)')
def main(project: str, grooming_filter: bool, status: str, label: str,
         unestimated: bool, issue_type: str, limit: int, jql: str):
    """
    Find tickets that need grooming before pointing.

    By default, uses the FSEC team's grooming board filter which includes:
    - Issue types: Spike, Story, Task
    - Statuses: Backlog, In Progress, Blocked, Intake, Ready to Refine,
                Ready to Ship, Refined, To Do, Shipping, Testing, Review
    - Sorted by: Most recently updated

    Examples:
        # Use default grooming filter
        uv run find_grooming_candidates.py

        # Grooming filter + only unestimated
        uv run find_grooming_candidates.py --unestimated

        # Custom filters (disables grooming filter)
        uv run find_grooming_candidates.py --no-grooming-filter --status "Needs More Info"
    """
    try:
        client = get_jira_client()

        # Build or use custom JQL
        if jql:
            query = jql
            click.echo(f"Using custom JQL: {query}", err=True)
        else:
            # Use grooming filter by default unless overridden
            use_grooming = grooming_filter and project == 'FSEC' and not status and not issue_type

            if use_grooming:
                click.echo("Using FSEC team grooming filter", err=True)

            query = build_jql(
                project=project,
                status=status,
                label=label,
                unestimated=unestimated,
                issue_type=issue_type,
                use_grooming_filter=use_grooming
            )
            click.echo(f"JQL: {query}", err=True)

        # Search tickets
        click.echo("Searching...", err=True)
        issues = search_tickets(client, query, limit=limit)

        # Format and display
        output = format_ticket_list(issues)
        click.echo(output)

        # Exit code: 0 if found tickets, 1 if none found
        sys.exit(0 if issues else 1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
