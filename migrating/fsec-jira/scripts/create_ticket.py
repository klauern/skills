#!/usr/bin/env python3
"""
Create Jira tickets with support for all issue types and FSEC custom fields.

Usage:
    # Create a task (auto-assigns to you)
    uv run create_ticket.py --summary "Fix login bug" --type "Task"

    # Create a sub-task under a parent
    uv run create_ticket.py --summary "Write tests" --type "Sub-Task" --parent FSEC-1234

    # Create with all options
    uv run create_ticket.py --summary "New feature" --type "Story" \
        --description "Detailed description" --components "ZIG,IAM" \
        --priority "High" --planned --work-attribution "Maintenance" --points 3

    # Preview without creating
    uv run create_ticket.py --summary "Test" --type "Task" --dry-run

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
    VALID_ISSUE_TYPES,
)


def get_current_user_account_id(client: Jira) -> str:
    """Get the account ID for the current user."""
    user = client.myself()
    return user.get('accountId', '')


def build_issue_fields(
    summary: str,
    issue_type: str,
    project: str,
    description: Optional[str],
    parent: Optional[str],
    components: Optional[List[str]],
    priority: Optional[str],
    assignee_id: Optional[str],
    planned: bool,
    unplanned: bool,
    work_attribution: Optional[str],
    points: Optional[float],
    sprint: Optional[str],
    acceptance_criteria: Optional[str],
) -> Dict[str, Any]:
    """Build the fields dictionary for issue creation."""
    fields: Dict[str, Any] = {
        "project": {"key": project},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }

    # Description (ADF format)
    if description:
        fields["description"] = text_to_adf(description)

    # Parent for sub-tasks
    if parent:
        fields["parent"] = {"key": parent}

    # Components
    if components:
        fields["components"] = [{"name": comp.strip()} for comp in components]

    # Priority
    if priority:
        fields["priority"] = {"name": priority}

    # Assignee
    if assignee_id:
        fields["assignee"] = {"accountId": assignee_id}

    # FSEC custom fields
    if planned:
        fields[FIELD_PLANNED_UNPLANNED] = {"value": "Planned"}
    elif unplanned:
        fields[FIELD_PLANNED_UNPLANNED] = {"value": "Unplanned"}

    if work_attribution:
        fields[FIELD_WORK_ATTRIBUTION] = {"value": work_attribution}

    if points is not None:
        fields[FIELD_STORY_POINTS] = points

    if acceptance_criteria:
        fields[FIELD_ACCEPTANCE_CRITERIA] = text_to_adf(acceptance_criteria)

    # Sprint requires finding the sprint ID - skip for now as it's complex
    # Sprint assignment typically done via board/backlog

    return fields


@click.command()
@click.option('--summary', '-s', required=True, help='Issue summary/title')
@click.option('--type', '-t', 'issue_type', default='Task',
              type=click.Choice(VALID_ISSUE_TYPES, case_sensitive=False),
              help='Issue type (default: Task)')
@click.option('--project', '-p', default=None,
              help='Project key (default: JIRA_DEFAULT_PROJECT or FSEC)')
@click.option('--description', '-d', help='Issue description')
@click.option('--parent', help='Parent issue key for Sub-Tasks (e.g., FSEC-1234 or 1234)')
@click.option('--components', '-c', help='Comma-separated list of components')
@click.option('--priority', type=click.Choice(['Highest', 'High', 'Medium', 'Low', 'Lowest'], case_sensitive=False),
              help='Issue priority')
@click.option('--no-assign', is_flag=True, help='Do not auto-assign to yourself')
# FSEC field aliases
@click.option('--planned', is_flag=True, help='Mark as Planned work (FSEC)')
@click.option('--unplanned', is_flag=True, help='Mark as Unplanned work (FSEC)')
@click.option('--work-attribution', 'work_attribution', help='Work attribution: "Elective investments", "Maintenance", or "Bug Fixes"')
@click.option('--points', type=float, help='Story points (FSEC)')
@click.option('--sprint', help='Sprint name (FSEC) - note: sprint assignment may require board access')
@click.option('--acceptance-criteria', 'acceptance_criteria', help='Acceptance criteria text (FSEC)')
# Utility options
@click.option('--dry-run', is_flag=True, help='Preview what would be created without making changes')
def main(
    summary: str,
    issue_type: str,
    project: Optional[str],
    description: Optional[str],
    parent: Optional[str],
    components: Optional[str],
    priority: Optional[str],
    no_assign: bool,
    planned: bool,
    unplanned: bool,
    work_attribution: Optional[str],
    points: Optional[float],
    sprint: Optional[str],
    acceptance_criteria: Optional[str],
    dry_run: bool,
):
    """Create a new Jira ticket.

    Examples:
        # Create a simple task (auto-assigns to you)
        create_ticket.py --summary "Fix login bug"

        # Create a sub-task under a parent
        create_ticket.py --summary "Write tests" --type Sub-Task --parent 1234

        # Create with FSEC fields
        create_ticket.py --summary "New feature" --type Story \\
            --components "ZIG,IAM" --planned --work-attribution "Maintenance"

        # Preview without creating
        create_ticket.py --summary "Test" --dry-run
    """
    try:
        # Validate options
        if planned and unplanned:
            click.echo("Error: Cannot specify both --planned and --unplanned", err=True)
            sys.exit(1)

        if issue_type.lower() == 'sub-task' and not parent:
            click.echo("Error: --parent is required for Sub-Task issue type", err=True)
            sys.exit(1)

        # Resolve project
        project_key = project or os.getenv('JIRA_DEFAULT_PROJECT', 'FSEC')

        # Normalize parent key if provided
        parent_key = normalize_issue_key(parent) if parent else None

        # Parse components
        component_list = [c.strip() for c in components.split(',')] if components else None

        # Get client and current user
        client = get_client()

        # Auto-assign unless --no-assign
        assignee_id = None
        if not no_assign:
            assignee_id = get_current_user_account_id(client)

        # Build fields
        fields = build_issue_fields(
            summary=summary,
            issue_type=issue_type,
            project=project_key,
            description=description,
            parent=parent_key,
            components=component_list,
            priority=priority,
            assignee_id=assignee_id,
            planned=planned,
            unplanned=unplanned,
            work_attribution=work_attribution,
            points=points,
            sprint=sprint,
            acceptance_criteria=acceptance_criteria,
        )

        # Dry run - just show what would be created
        if dry_run:
            click.echo("\n" + "=" * 60)
            click.echo("DRY RUN - Would create issue with:")
            click.echo("=" * 60)
            click.echo(f"  Project: {project_key}")
            click.echo(f"  Type: {issue_type}")
            click.echo(f"  Summary: {summary}")
            if description:
                click.echo(f"  Description: {description[:100]}{'...' if len(description) > 100 else ''}")
            if parent_key:
                click.echo(f"  Parent: {parent_key}")
            if component_list:
                click.echo(f"  Components: {', '.join(component_list)}")
            if priority:
                click.echo(f"  Priority: {priority}")
            if not no_assign:
                click.echo(f"  Assignee: (current user)")
            if planned:
                click.echo(f"  Planned/Unplanned: Planned")
            if unplanned:
                click.echo(f"  Planned/Unplanned: Unplanned")
            if work_attribution:
                click.echo(f"  Work Attribution: {work_attribution}")
            if points:
                click.echo(f"  Story Points: {points}")
            if acceptance_criteria:
                click.echo(f"  Acceptance Criteria: {acceptance_criteria[:50]}{'...' if len(acceptance_criteria) > 50 else ''}")
            click.echo("=" * 60)
            click.echo("\nNo changes made (dry run)")
            return

        # Create the issue using REST API directly (handles ADF better than library)
        import requests
        url, email, api_token = get_jira_credentials()

        response = requests.post(
            f"{url}/rest/api/3/issue",
            auth=(email, api_token),
            headers={"Content-Type": "application/json"},
            json={"fields": fields}
        )

        if response.status_code not in (200, 201):
            raise ValueError(f"Failed to create issue: {response.text}")

        result = response.json()
        issue_key = result.get('key', 'Unknown')

        click.echo(f"\n Created {issue_key}: {summary}")
        if parent_key:
            click.echo(f"   Parent: {parent_key}")
        click.echo(f"\n View: {get_jira_url()}/browse/{issue_key}\n")

    except Exception as e:
        click.echo(f"Error creating issue: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
