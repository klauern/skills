#!/usr/bin/env python3
"""
Apply decisions from CSV to blocked tickets.

Reads a CSV exported by export_blocked_csv.py with decisions filled in,
and executes the specified actions on each ticket.

Usage:
    uv run apply_decisions_csv.py blocked_tickets.csv
    uv run apply_decisions_csv.py blocked_tickets.csv --dry-run
    uv run apply_decisions_csv.py blocked_tickets.csv --yes

Supported decisions:
    - CLOSE: Mark ticket as Done with "Won't Do" resolution
    - UNBLOCK: Change status to "To Do"
    - DOCUMENT: Add comment requesting blocker documentation
    - KEEP: No action (leave blocked)
    - (blank/empty): Skip this ticket

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
from typing import List, Dict, Any
from dataclasses import dataclass
import click
from atlassian import Jira


@dataclass
class DecisionRow:
    """A row from the CSV with a decision."""
    key: str
    summary: str
    decision: str
    notes: str
    row_number: int


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


def read_decisions_csv(csv_path: str) -> List[DecisionRow]:
    """Read decisions from CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    decisions = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (account for header)
            key = row.get('Key', '').strip()
            summary = row.get('Summary', '').strip()
            decision = row.get('Decision', '').strip().upper()
            notes = row.get('Notes', '').strip()

            # Skip rows without a key or decision
            if not key or not decision:
                continue

            # Validate decision
            valid_decisions = ['CLOSE', 'UNBLOCK', 'DOCUMENT', 'KEEP']
            if decision not in valid_decisions:
                click.echo(f"⚠️  Row {row_num}: Unknown decision '{decision}' for {key} - skipping", err=True)
                continue

            # Skip KEEP decisions (no action needed)
            if decision == 'KEEP':
                continue

            decisions.append(DecisionRow(
                key=key,
                summary=summary,
                decision=decision,
                notes=notes,
                row_number=row_num
            ))

    return decisions


def preview_actions(decisions: List[DecisionRow]) -> None:
    """Show what actions will be performed."""
    if not decisions:
        click.echo("No actionable decisions found in CSV.")
        return

    click.echo(f"\n{'='*80}")
    click.echo(f"PREVIEW: {len(decisions)} action(s) to perform")
    click.echo(f"{'='*80}\n")

    by_decision = {}
    for d in decisions:
        by_decision.setdefault(d.decision, []).append(d)

    for decision, items in sorted(by_decision.items()):
        action_desc = {
            'CLOSE': '🔴 Will CLOSE (mark as Done - Won\'t Do)',
            'UNBLOCK': '🟢 Will UNBLOCK (change to To Do)',
            'DOCUMENT': '📝 Will REQUEST DOCUMENTATION (add comment)'
        }.get(decision, decision)

        click.echo(f"{action_desc}: {len(items)} ticket(s)")
        for item in items[:5]:  # Show first 5
            click.echo(f"   • {item.key} - {item.summary[:60]}")
        if len(items) > 5:
            click.echo(f"   • ... and {len(items) - 5} more")
        click.echo("")


def apply_decision_close(client: Jira, key: str, notes: str, dry_run: bool) -> bool:
    """Close a ticket with Won't Do resolution."""
    try:
        if dry_run:
            click.echo(f"[DRY RUN] Would close {key} with resolution 'Won't Do'")
            return True

        # Add comment explaining closure
        comment = (
            f"Closing this ticket as part of blocked tickets cleanup.\n\n"
            f"Reason: Blocked for extended period with no clear path forward.\n"
        )
        if notes:
            comment += f"Notes: {notes}\n"

        client.issue_add_comment(key, comment)

        # Transition to Done with Won't Do resolution
        # Note: Transition IDs may vary by Jira instance
        # This attempts to find and use the "Done" transition
        transitions = client.get_issue_transitions(key)
        done_transition = None

        for t in transitions['transitions']:
            if t['name'].lower() in ['done', 'close', 'closed']:
                done_transition = t['id']
                break

        if done_transition:
            client.set_issue_status(key, 'Done', fields={'resolution': {'name': 'Won\'t Do'}})
            click.echo(f"✅ Closed {key}")
        else:
            click.echo(f"⚠️  {key}: Could not find 'Done' transition - added comment only", err=True)

        return True

    except Exception as e:
        click.echo(f"❌ {key}: Failed to close - {e}", err=True)
        return False


def apply_decision_unblock(client: Jira, key: str, notes: str, dry_run: bool) -> bool:
    """Unblock a ticket by changing status to To Do."""
    try:
        if dry_run:
            click.echo(f"[DRY RUN] Would unblock {key} (change to To Do)")
            return True

        # Add comment explaining unblock
        comment = (
            f"Unblocking this ticket.\n\n"
        )
        if notes:
            comment += f"Notes: {notes}\n"
        else:
            comment += "Blocker appears to be resolved. Moving to To Do.\n"

        client.issue_add_comment(key, comment)

        # Transition to To Do
        client.set_issue_status(key, 'To Do')
        click.echo(f"✅ Unblocked {key}")
        return True

    except Exception as e:
        click.echo(f"❌ {key}: Failed to unblock - {e}", err=True)
        return False


def apply_decision_document(client: Jira, key: str, notes: str, dry_run: bool) -> bool:
    """Request blocker documentation via comment."""
    try:
        if dry_run:
            click.echo(f"[DRY RUN] Would add documentation request comment to {key}")
            return True

        # Add comment requesting blocker documentation
        comment = (
            f"🚧 Blocker Documentation Needed\n\n"
            f"This ticket has been marked as Blocked but lacks clear blocker documentation.\n\n"
            f"Please update this ticket with:\n"
            f"1. What specifically is blocking this work?\n"
            f"2. Link to any blocking tickets or external dependencies\n"
            f"3. What needs to happen before this can be unblocked?\n\n"
        )
        if notes:
            comment += f"Additional context: {notes}\n\n"

        comment += (
            f"If the blocker is resolved, please move this ticket to 'To Do'. "
            f"If this work is no longer needed, please close it.\n"
        )

        client.issue_add_comment(key, comment)
        click.echo(f"✅ Added documentation request to {key}")
        return True

    except Exception as e:
        click.echo(f"❌ {key}: Failed to add comment - {e}", err=True)
        return False


def apply_decisions(client: Jira, decisions: List[DecisionRow], dry_run: bool = False) -> Dict[str, int]:
    """Apply all decisions."""
    stats = {'success': 0, 'failed': 0, 'skipped': 0}

    for decision_row in decisions:
        key = decision_row.key
        decision = decision_row.decision
        notes = decision_row.notes

        success = False
        if decision == 'CLOSE':
            success = apply_decision_close(client, key, notes, dry_run)
        elif decision == 'UNBLOCK':
            success = apply_decision_unblock(client, key, notes, dry_run)
        elif decision == 'DOCUMENT':
            success = apply_decision_document(client, key, notes, dry_run)
        else:
            click.echo(f"⚠️  {key}: Unknown decision '{decision}' - skipping", err=True)
            stats['skipped'] += 1
            continue

        if success:
            stats['success'] += 1
        else:
            stats['failed'] += 1

    return stats


@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--dry-run', '-n', is_flag=True,
              help='Preview actions without making changes')
@click.option('--yes', '-y', is_flag=True,
              help='Skip confirmation prompt')
def main(csv_file: str, dry_run: bool, yes: bool):
    """
    Apply decisions from CSV to blocked tickets.

    Reads the CSV file with decisions and executes actions on Jira tickets.

    Examples:
        # Preview what will happen
        uv run apply_decisions_csv.py blocked.csv --dry-run

        # Apply with confirmation prompt
        uv run apply_decisions_csv.py blocked.csv

        # Apply without confirmation
        uv run apply_decisions_csv.py blocked.csv --yes
    """
    try:
        # Read decisions
        click.echo(f"Reading decisions from: {csv_file}", err=True)
        decisions = read_decisions_csv(csv_file)

        if not decisions:
            click.echo("✅ No actionable decisions found in CSV (all KEEP or blank).")
            sys.exit(0)

        # Preview
        preview_actions(decisions)

        # Confirm unless --yes or --dry-run
        if not dry_run and not yes:
            if not click.confirm(f"\nProceed with {len(decisions)} action(s)?"):
                click.echo("Aborted.")
                sys.exit(1)

        # Get Jira client
        client = get_jira_client()

        # Apply decisions
        click.echo(f"\n{'='*80}")
        if dry_run:
            click.echo("DRY RUN MODE - No changes will be made")
        else:
            click.echo("Applying decisions...")
        click.echo(f"{'='*80}\n")

        stats = apply_decisions(client, decisions, dry_run=dry_run)

        # Summary
        click.echo(f"\n{'='*80}")
        click.echo("SUMMARY")
        click.echo(f"{'='*80}")
        click.echo(f"✅ Success: {stats['success']}")
        if stats['failed'] > 0:
            click.echo(f"❌ Failed: {stats['failed']}")
        if stats['skipped'] > 0:
            click.echo(f"⚠️  Skipped: {stats['skipped']}")

        if dry_run:
            click.echo("\nThis was a dry run. Use without --dry-run to apply changes.")

        sys.exit(0 if stats['failed'] == 0 else 1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
