#!/usr/bin/env python3
"""
Update Jira ticket fields, status, resolution, and comments.

Usage:
    # Update status
    uv run update_ticket.py FSEC-1234 --status "In Progress"

    # Close ticket
    uv run update_ticket.py FSEC-1234 --status "Done" --resolution "Done"

    # Mark as Won't Do
    uv run update_ticket.py FSEC-1234 --status "Done" --resolution "Won't Do" --comment "Fixed by JIRA-1234"

    # Update components
    uv run update_ticket.py FSEC-1234 --components "AFT,Atlantis"

    # Add comment
    uv run update_ticket.py FSEC-1234 --comment "Completed implementation"

Environment variables:
    JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_DEFAULT_PROJECT
"""

# /// script
# dependencies = [
#   "atlassian-python-api>=4.0.3",
#   "click>=8.1.7",
#   "requests>=2.31.0",
# ]
# ///

import os
import sys
from typing import Optional, List, Dict, Any
import click
from atlassian import Jira

# Import shared utilities from jira_api
from jira_api import (
    get_client,
    get_jira_url,
    get_jira_credentials,
    normalize_issue_key,
    text_to_adf,
    FIELD_PLANNED_UNPLANNED,
    FIELD_ACCEPTANCE_CRITERIA,
    FIELD_WORK_ATTRIBUTION,
    FIELD_STORY_POINTS,
    FIELD_SPRINT,
)


def update_status_and_resolution(
    client: Jira,
    issue_key: str,
    status: Optional[str],
    resolution: Optional[str],
    comment: Optional[str]
) -> None:
    """Update issue status and optionally resolution.

    Args:
        client: Jira client
        issue_key: Issue key
        status: Target status name
        resolution: Resolution name (e.g., 'Done', 'Won't Do')
        comment: Optional comment to add with transition
    """
    if not status:
        return

    # Get available transitions
    transitions = client.get_issue_transitions(issue_key)

    # Handle different API response formats
    transition_list = []
    if isinstance(transitions, dict):
        transition_list = transitions.get('transitions', [])
    elif isinstance(transitions, list):
        transition_list = transitions
    else:
        raise ValueError(f"Unexpected transitions response format: {type(transitions)}")

    # Find matching transition
    transition_id = None
    for t in transition_list:
        if isinstance(t, dict) and t.get('name', '').lower() == status.lower():
            transition_id = t.get('id')
            break

    if not transition_id:
        available = [t.get('name', 'Unknown') for t in transition_list if isinstance(t, dict)]
        raise ValueError(f"Status '{status}' not available. Available: {', '.join(available)}")

    # Prepare transition data
    fields = {}
    if resolution:
        fields['resolution'] = {'name': resolution}

    # Execute transition
    client.set_issue_status(issue_key, status, fields=fields if fields else None)

    # Add comment if provided
    if comment:
        client.issue_add_comment(issue_key, comment)

    resolution_msg = f" with resolution '{resolution}'" if resolution else ""
    click.echo(f"✅ Updated {issue_key} to '{status}'{resolution_msg}")


def update_components(client: Jira, issue_key: str, components: List[str]) -> None:
    """Update issue components.

    Args:
        client: Jira client
        issue_key: Issue key
        components: List of component names
    """
    # Format components for Jira API
    component_list = [{'name': comp.strip()} for comp in components]

    client.update_issue_field(issue_key, {'components': component_list})
    click.echo(f"✅ Updated {issue_key} components: {', '.join(components)}")


def update_priority(client: Jira, issue_key: str, priority: str) -> None:
    """Update issue priority.

    Args:
        client: Jira client
        issue_key: Issue key
        priority: Priority name (e.g., 'High', 'Medium', 'Low')
    """
    client.update_issue_field(issue_key, {'priority': {'name': priority}})
    click.echo(f"✅ Updated {issue_key} priority: {priority}")


def update_custom_field(client: Jira, issue_key: str, field_id: str, value: str) -> None:
    """Update a custom field.

    Args:
        client: Jira client
        issue_key: Issue key
        field_id: Custom field ID (e.g., 'customfield_12345')
        value: Field value
    """
    # Try to determine field type and format value appropriately
    if value.lower() in ['true', 'false']:
        formatted_value = value.lower() == 'true'
    elif value.startswith('{') or value.startswith('['):
        import json
        formatted_value = json.loads(value)
    else:
        formatted_value = value

    client.update_issue_field(issue_key, {field_id: formatted_value})
    click.echo(f"✅ Updated {issue_key} field {field_id}: {value}")


def add_comment_to_issue(client: Jira, issue_key: str, comment: str) -> None:
    """Add comment to issue.

    Args:
        client: Jira client
        issue_key: Issue key
        comment: Comment text
    """
    client.issue_add_comment(issue_key, comment)
    click.echo(f"✅ Added comment to {issue_key}")


@click.command()
@click.argument('issue_ref')
@click.option('--status', help='New status (e.g., "In Progress", "Done")')
@click.option('--resolution', help='Resolution (e.g., "Done", "Won\'t Do")')
@click.option('--components', help='Comma-separated list of components')
@click.option('--priority', help='Priority (e.g., "High", "Medium", "Low")')
@click.option('--custom-field', 'custom_fields', multiple=True,
              help='Custom field update (format: fieldId=value)')
@click.option('--comment', help='Comment to add')
# FSEC field aliases
@click.option('--planned', is_flag=True, help='Mark as Planned work (FSEC)')
@click.option('--unplanned', is_flag=True, help='Mark as Unplanned work (FSEC)')
@click.option('--acceptance-criteria', 'acceptance_criteria', help='Set acceptance criteria text (FSEC)')
@click.option('--work-attribution', 'work_attribution', help='Work attribution: "Elective investments", "Maintenance", or "Bug Fixes"')
@click.option('--points', type=float, help='Story points (FSEC)')
@click.option('--sprint', help='Sprint name (FSEC)')
# Utility options
@click.option('--dry-run', is_flag=True, help='Preview changes without applying')
def main(
    issue_ref: str,
    status: Optional[str],
    resolution: Optional[str],
    components: Optional[str],
    priority: Optional[str],
    custom_fields: tuple,
    comment: Optional[str],
    planned: bool,
    unplanned: bool,
    acceptance_criteria: Optional[str],
    work_attribution: Optional[str],
    points: Optional[float],
    sprint: Optional[str],
    dry_run: bool,
):
    """Update Jira ticket fields, status, and resolution.

    ISSUE_REF can be a full key (FSEC-1234) or just a number (1234).

    Examples:
        # Change status to In Progress
        update_ticket.py FSEC-1234 --status "In Progress"

        # Close ticket as Won't Do with comment
        update_ticket.py FSEC-1234 --status "Done" --resolution "Won't Do" --comment "Fixed by JIRA-1234"

        # Update components
        update_ticket.py FSEC-1234 --components "AFT,Atlantis"

        # FSEC shortcuts for common fields
        update_ticket.py FSEC-1234 --planned --components "ZIG"
        update_ticket.py FSEC-1234 --unplanned --acceptance-criteria "- Tests pass"
        update_ticket.py FSEC-1234 --work-attribution "Maintenance"
        update_ticket.py FSEC-1234 --points 3 --sprint "2025-Sprint 1"

        # Update custom field (generic)
        update_ticket.py FSEC-1234 --custom-field customfield_12345="value"

        # Preview changes without applying
        update_ticket.py FSEC-1234 --status "Done" --dry-run
    """
    try:
        issue_key = normalize_issue_key(issue_ref)

        # Validate at least one update is provided
        has_update = any([status, components, priority, custom_fields, comment,
                         planned, unplanned, acceptance_criteria, work_attribution,
                         points is not None, sprint])
        if not has_update:
            click.echo("❌ Error: At least one update option must be provided", err=True)
            click.echo("Use --help for usage information", err=True)
            sys.exit(1)

        # Validate mutually exclusive options
        if planned and unplanned:
            click.echo("❌ Error: Cannot specify both --planned and --unplanned", err=True)
            sys.exit(1)

        # Dry run - show what would be updated
        if dry_run:
            click.echo("\n" + "=" * 60)
            click.echo(f"DRY RUN - Would update {issue_key} with:")
            click.echo("=" * 60)
            if status:
                click.echo(f"  Status: {status}")
                if resolution:
                    click.echo(f"  Resolution: {resolution}")
            if components:
                click.echo(f"  Components: {components}")
            if priority:
                click.echo(f"  Priority: {priority}")
            if planned:
                click.echo(f"  Planned/Unplanned: Planned")
            if unplanned:
                click.echo(f"  Planned/Unplanned: Unplanned")
            if acceptance_criteria:
                click.echo(f"  Acceptance Criteria: {acceptance_criteria[:50]}{'...' if len(acceptance_criteria) > 50 else ''}")
            if work_attribution:
                click.echo(f"  Work Attribution: {work_attribution}")
            if points is not None:
                click.echo(f"  Story Points: {points}")
            if sprint:
                click.echo(f"  Sprint: {sprint}")
            if comment:
                click.echo(f"  Comment: {comment[:50]}{'...' if len(comment) > 50 else ''}")
            for cf in custom_fields:
                click.echo(f"  Custom Field: {cf}")
            click.echo("=" * 60)
            click.echo("\nNo changes made (dry run)")
            return

        client = get_client()

        # Update status and resolution (if provided)
        if status:
            update_status_and_resolution(client, issue_key, status, resolution, None)

        # Update components
        if components:
            component_list = [c.strip() for c in components.split(',')]
            update_components(client, issue_key, component_list)

        # Update priority
        if priority:
            update_priority(client, issue_key, priority)

        # Update custom fields
        for custom_field in custom_fields:
            if '=' not in custom_field:
                click.echo(f"⚠️  Warning: Invalid custom field format '{custom_field}'. Use fieldId=value", err=True)
                continue
            field_id, value = custom_field.split('=', 1)
            update_custom_field(client, issue_key, field_id, value)

        # FSEC field aliases
        if planned:
            update_custom_field(client, issue_key, FIELD_PLANNED_UNPLANNED, '{"value":"Planned"}')
        if unplanned:
            update_custom_field(client, issue_key, FIELD_PLANNED_UNPLANNED, '{"value":"Unplanned"}')
        if acceptance_criteria:
            # Acceptance criteria requires Atlassian Document Format
            # Use direct REST API call since the library method doesn't handle ADF correctly
            import requests
            url, email, api_token = get_jira_credentials()

            adf_content = text_to_adf(acceptance_criteria)
            response = requests.put(
                f"{url}/rest/api/3/issue/{issue_key}",
                auth=(email, api_token),
                headers={"Content-Type": "application/json"},
                json={"fields": {FIELD_ACCEPTANCE_CRITERIA: adf_content}}
            )
            if response.status_code == 204:
                click.echo(f"✅ Updated {issue_key} acceptance criteria")
            else:
                raise ValueError(f"Failed to update acceptance criteria: {response.text}")
        if work_attribution:
            update_custom_field(client, issue_key, FIELD_WORK_ATTRIBUTION, f'{{"value":"{work_attribution}"}}')
        if points is not None:
            client.update_issue_field(issue_key, {FIELD_STORY_POINTS: points})
            click.echo(f"✅ Updated {issue_key} story points: {points}")
        if sprint:
            # Note: Sprint assignment via API can be complex due to board/sprint IDs
            # This is a basic implementation that may need adjustment
            click.echo(f"⚠️  Sprint assignment via CLI is limited. Use Jira board for sprint management.")

        # Add comment (separate from status transition)
        if comment and not status:
            add_comment_to_issue(client, issue_key, comment)

        click.echo(f"\n🔗 View changes: {get_jira_url()}/browse/{issue_key}\n")

    except Exception as e:
        click.echo(f"❌ Error updating {issue_ref}: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
