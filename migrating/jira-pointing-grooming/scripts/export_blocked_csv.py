#!/usr/bin/env python3
"""
Export blocked tickets to CSV for decision-making.

Creates a CSV with blocked tickets that can be opened in spreadsheet apps.
Add your decisions in the 'Decision' column, then reimport with apply_decisions_csv.py

Usage:
    uv run export_blocked_csv.py --output blocked_tickets.csv
    uv run export_blocked_csv.py --min-age-days 30 --output old_blocked.csv

Decision options:
    - CLOSE: Mark ticket as Done with "Won't Do" resolution
    - UNBLOCK: Change status to "To Do"
    - DOCUMENT: Add comment to document blocker reason
    - KEEP: No action (leave blocked)
    - (blank): No action

Environment variables:
    JIRA_URL: Jira instance URL (defaults to https://zendesk.atlassian.net)
    JIRA_EMAIL: User email for authentication (defaults to {whoami}@zendesk.com)
    JIRA_API_TOKEN: API token from Atlassian account settings
"""

# /// script
# dependencies = [
#   "atlassian-python-api>=4.0.3",
#   "click>=8.1.7",
# ]
# ///

import os
import sys
import csv
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import click
from atlassian import Jira


def get_jira_client() -> Jira:
    """Get configured Jira client."""
    import getpass

    url = os.getenv('JIRA_URL', 'https://zendesk.atlassian.net')
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


def calculate_days_since(date_str: str) -> int:
    """Calculate days since a date string."""
    try:
        date = datetime.strptime(date_str[:10], '%Y-%m-%d')
        return (datetime.now() - date).days
    except:
        return 0


def format_age(days: int) -> str:
    """Format age in human-readable form."""
    if days == 0:
        return "Today"
    elif days == 1:
        return "1 day"
    elif days < 7:
        return f"{days} days"
    elif days < 30:
        weeks = days // 7
        return f"{weeks}w"
    elif days < 365:
        months = days // 30
        return f"{months}mo"
    else:
        years = days // 365
        return f"{years}y"


def extract_blocker_reason(description: str, comments: List[str]) -> str:
    """Extract why the ticket is blocked from description or comments."""
    all_text = f"{description}\n" + "\n".join(comments)

    blocker_patterns = [
        r'(?:blocked by|waiting (?:on|for)|depends on|needs)\s+([^\n.]+)',
        r'(?:blocker|blocking issue):\s*([^\n.]+)',
        r'(?:cannot proceed|can\'t start) (?:until|because)\s+([^\n.]+)',
    ]

    reasons = []
    for pattern in blocker_patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        reasons.extend(matches[:2])

    if reasons:
        cleaned = []
        seen = set()
        for reason in reasons:
            reason = reason.strip()
            if reason.lower() not in seen and len(reason) > 10:
                cleaned.append(reason)
                seen.add(reason.lower())
        return '; '.join(cleaned[:2])  # Max 2 reasons

    return "No documented blocker"


def find_linked_blockers(issue: Dict[str, Any]) -> str:
    """Find tickets that are blocking this issue."""
    blockers = []
    links = issue.get('fields', {}).get('issuelinks', [])

    for link in links:
        link_type = link.get('type', {}).get('name', '')
        if 'inwardIssue' in link and link_type.lower() in ['blocks', 'blocker']:
            blocker_key = link['inwardIssue'].get('key')
            blocker_status = link['inwardIssue'].get('fields', {}).get('status', {}).get('name', 'Unknown')
            if blocker_key:
                blockers.append(f"{blocker_key} ({blocker_status})")

    return '; '.join(blockers) if blockers else "None"


def suggest_decision(age_days: int, linked_blockers: str, blocker_reason: str) -> str:
    """Suggest a decision based on ticket metadata."""
    # Ancient tickets likely should be closed
    if age_days > 180:
        return "CLOSE"

    # Resolved blockers suggest unblocking
    if 'Resolved' in linked_blockers or 'Done' in linked_blockers or 'Closed' in linked_blockers:
        return "UNBLOCK"

    # No documented reason needs documentation
    if "no documented" in blocker_reason.lower():
        return "DOCUMENT"

    # Recent tickets with clear blockers should be kept
    if age_days < 90 and linked_blockers != "None":
        return "KEEP"

    return ""  # No suggestion


def export_blocked_to_csv(
    client: Jira,
    project: str,
    min_age_days: int,
    output_path: str
):
    """Export blocked tickets to CSV."""
    # Find blocked tickets
    jql = f'project = {project} AND status = Blocked'
    if min_age_days > 0:
        jql += f' AND created <= -{min_age_days}d'
    jql += ' ORDER BY created ASC'  # Oldest first

    fields = ['summary', 'status', 'priority', 'created', 'updated',
              'description', 'comment', 'issuelinks']

    result = client.jql(jql, limit=100, fields=fields)
    issues = result.get('issues', [])

    if not issues:
        click.echo("No blocked tickets found.", err=True)
        return

    # Prepare CSV data
    rows = []
    for issue in issues:
        key = issue['key']
        fields = issue['fields']

        summary = fields.get('summary', 'No summary')
        priority = fields.get('priority', {}).get('name', 'None')
        created = fields.get('created', '')
        age_days = calculate_days_since(created)
        age_str = format_age(age_days)

        description = fields.get('description', '') or ''
        comment_data = fields.get('comment', {}).get('comments', [])
        comments = [c.get('body', '') for c in comment_data]

        blocker_reason = extract_blocker_reason(description, comments)
        linked_blockers = find_linked_blockers(issue)

        suggested_decision = suggest_decision(age_days, linked_blockers, blocker_reason)

        rows.append({
            'Key': key,
            'Summary': summary,
            'Priority': priority,
            'Age (days)': age_days,
            'Age': age_str,
            'Blocker Reason': blocker_reason,
            'Linked Blockers': linked_blockers,
            'Decision': suggested_decision,
            'Notes': ''
        })

    # Write CSV
    fieldnames = ['Key', 'Summary', 'Priority', 'Age (days)', 'Age',
                  'Blocker Reason', 'Linked Blockers', 'Decision', 'Notes']

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    click.echo(f"✅ Exported {len(rows)} blocked tickets to: {output_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"1. Open the CSV in your spreadsheet app")
    click.echo(f"2. Review the 'Decision' column (suggested values provided)")
    click.echo(f"3. Update decisions as needed:")
    click.echo(f"   - CLOSE: Mark as Done (Won't Do)")
    click.echo(f"   - UNBLOCK: Change to To Do status")
    click.echo(f"   - DOCUMENT: Add blocker documentation comment")
    click.echo(f"   - KEEP: Leave blocked (no action)")
    click.echo(f"   - (blank): Skip this ticket")
    click.echo(f"4. Save the CSV and run: uv run apply_decisions_csv.py {output_path}")


@click.command()
@click.option('--project', '-p', default='FSEC', help='Project key (default: FSEC)')
@click.option('--min-age-days', type=int, default=0,
              help='Only export tickets blocked for at least N days')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output CSV file path')
def main(project: str, min_age_days: int, output: str):
    """
    Export blocked tickets to CSV for decision-making.

    Examples:
        # Export all blocked tickets
        uv run export_blocked_csv.py --output blocked.csv

        # Only ancient tickets (>6 months)
        uv run export_blocked_csv.py --min-age-days 180 --output ancient_blocked.csv
    """
    try:
        client = get_jira_client()

        click.echo(f"Fetching blocked tickets from {project}...", err=True)
        if min_age_days > 0:
            click.echo(f"Filtering to tickets blocked ≥ {min_age_days} days...", err=True)

        export_blocked_to_csv(client, project, min_age_days, output)

        sys.exit(0)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
