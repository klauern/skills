#!/usr/bin/env python3
"""
Manage HeroCoders Checklist items via the checklist field (customfield_21607).

HeroCoders stores checklist data as ADF (Atlassian Document Format) in this field,
parsing [open] and [checked] markers in the text to determine checkbox state.
The read-only summary field (customfield_21653) displays "Checklist: X/Y".

Usage:
    # Add checklist items
    uv run manage_checklist.py FSEC-1234 --add "Complete implementation" --add "Write tests"

    # Add section with items
    uv run manage_checklist.py FSEC-1234 --section "Phase 1" --add "Task 1" --add "Task 2"

    # Check/uncheck items by index (1-based)
    uv run manage_checklist.py FSEC-1234 --check 1 --check 3

    # View current checklist
    uv run manage_checklist.py FSEC-1234 --show

    # Replace entire checklist
    uv run manage_checklist.py FSEC-1234 --replace "* [ ] New item 1\n* [ ] New item 2"

Environment variables:
    JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_DEFAULT_PROJECT
"""

# /// script
# dependencies = [
#   "atlassian-python-api>=4.0.3",
#   "click>=8.1.7",
#   "pydantic>=2.11.0",
# ]
# ///

import re
import sys
from typing import List, Optional
import click
from atlassian import Jira

# Import shared utilities from jira_api
from jira_api import (
    get_client,
    get_jira_url,
    normalize_issue_key,
    FIELD_CHECKLIST,
)


def get_checklist(client: Jira, issue_key: str) -> str:
    """Get current checklist text from issue.

    Returns:
        Current checklist text (empty string if none)
    """
    issue = client.issue(issue_key, fields=FIELD_CHECKLIST)
    checklist = issue.get('fields', {}).get(FIELD_CHECKLIST, '')
    return checklist or ''


def set_checklist(client: Jira, issue_key: str, checklist_text: str) -> None:
    """Set checklist text on issue."""
    client.update_issue_field(issue_key, {FIELD_CHECKLIST: checklist_text})


def parse_checklist(checklist_text: str) -> List[dict]:
    """Parse checklist text into structured items.

    Returns:
        List of items with keys: type (title/section/item/description), text, checked (bool, items only)
    """
    items = []
    for line in checklist_text.split('\n'):
        line = line.rstrip()
        if not line:
            continue

        # Checklist title
        if line.startswith('#'):
            items.append({
                'type': 'title',
                'text': line.lstrip('#').strip()
            })
        # Section header
        elif line.startswith('---'):
            items.append({
                'type': 'section',
                'text': line[3:].strip()
            })
        # Description/note line
        elif line.startswith('>>'):
            items.append({
                'type': 'description',
                'text': line[2:].strip()
            })
        # Checklist item
        elif line.startswith('*'):
            # Extract checkbox state and text
            # Handle [checked], [done], [x], [X] as checked
            if re.search(r'\[(checked|done|x|X)\]', line):
                checked = True
                text = re.sub(r'\*\s*\[(checked|done|x|X)\]\s*', '', line)
            # Handle [open], [ ] as unchecked
            elif re.search(r'\[(open|\s*)\]', line):
                checked = False
                text = re.sub(r'\*\s*\[(open|\s*)\]\s*', '', line)
            else:
                # Plain item without checkbox
                checked = False
                text = line.lstrip('*').strip()

            items.append({
                'type': 'item',
                'text': text,
                'checked': checked
            })

    return items


def format_checklist(items: List[dict]) -> str:
    """Format structured items back to checklist text."""
    lines = []
    for item in items:
        if item['type'] == 'title':
            lines.append(f"# {item['text']}")
        elif item['type'] == 'section':
            lines.append(f"--- {item['text']}")
        elif item['type'] == 'description':
            lines.append(f">> {item['text']}")
        else:  # item
            checkbox = '[checked]' if item['checked'] else '[open]'
            lines.append(f"* {checkbox} {item['text']}")
    return '\n'.join(lines)


def display_checklist(items: List[dict]) -> None:
    """Display checklist items in readable format."""
    if not items:
        click.echo("Checklist is empty")
        return

    item_num = 0
    for item in items:
        if item['type'] == 'title':
            click.echo(f"# {item['text']}\n")
        elif item['type'] == 'section':
            click.echo(f"\n--- {item['text']} ---")
        elif item['type'] == 'description':
            click.echo(f"     >> {item['text']}")
        else:  # item
            item_num += 1
            status = '✓' if item['checked'] else ' '
            click.echo(f"  {item_num}. [{status}] {item['text']}")


@click.command()
@click.argument('issue_ref')
@click.option('--add', 'add_items', multiple=True, help='Add checklist item(s)')
@click.option('--description', 'descriptions', multiple=True, help='Add description/note after last added item')
@click.option('--section', help='Add section header before items')
@click.option('--check', 'check_items', multiple=True, type=int,
              help='Mark item(s) as checked by number (1-based)')
@click.option('--uncheck', 'uncheck_items', multiple=True, type=int,
              help='Mark item(s) as unchecked by number (1-based)')
@click.option('--edit', 'edit_item', type=str,
              help='Edit item text (format: "number:new text", e.g., "1:Updated task description")')
@click.option('--show', is_flag=True, help='Display current checklist')
@click.option('--replace', help='Replace entire checklist with new text')
def main(
    issue_ref: str,
    add_items: tuple,
    descriptions: tuple,
    section: Optional[str],
    check_items: tuple,
    uncheck_items: tuple,
    edit_item: Optional[str],
    show: bool,
    replace: Optional[str]
):
    """Manage HeroCoders Checklist items.

    ISSUE_REF can be a full key (FSEC-1234) or just a number (1234).

    Examples:
        # View checklist
        manage_checklist.py FSEC-1234 --show

        # Add items
        manage_checklist.py FSEC-1234 --add "Complete implementation" --add "Write tests"

        # Add section with items
        manage_checklist.py FSEC-1234 --section "Phase 1" --add "Task 1" --add "Task 2"

        # Check items 1 and 3
        manage_checklist.py FSEC-1234 --check 1 --check 3

        # Replace entire checklist
        manage_checklist.py FSEC-1234 --replace "* [ ] Item 1\\n* [ ] Item 2"
    """
    try:
        issue_key = normalize_issue_key(issue_ref)
        client = get_client()

        # Get current checklist
        current_text = get_checklist(client, issue_key)
        items = parse_checklist(current_text)

        # Show mode
        if show:
            click.echo(f"\nChecklist for {issue_key}:")
            click.echo("=" * 40)
            display_checklist(items)
            click.echo()
            return

        # Replace mode
        if replace:
            set_checklist(client, issue_key, replace)
            click.echo(f"✅ Replaced checklist on {issue_key}")
            return

        # Validate at least one operation
        if not (add_items or check_items or uncheck_items or edit_item or descriptions):
            click.echo("❌ Error: Specify --add, --check, --uncheck, --edit, --description, --show, or --replace", err=True)
            sys.exit(1)

        # Edit item text
        if edit_item:
            if ':' not in edit_item:
                click.echo("❌ Error: --edit format must be 'number:new text'", err=True)
                sys.exit(1)

            try:
                item_num_str, new_text = edit_item.split(':', 1)
                edit_num = int(item_num_str)

                checklist_items = [item for item in items if item['type'] == 'item']
                if 1 <= edit_num <= len(checklist_items):
                    item_count = 0
                    for item in items:
                        if item['type'] == 'item':
                            item_count += 1
                            if item_count == edit_num:
                                item['text'] = new_text.strip()
                                break
                else:
                    click.echo(f"❌ Error: Item {edit_num} out of range (1-{len(checklist_items)})", err=True)
                    sys.exit(1)
            except ValueError:
                click.echo("❌ Error: Invalid --edit format. Use 'number:new text'", err=True)
                sys.exit(1)

        # Add section header
        if section:
            items.append({'type': 'section', 'text': section})

        # Add new items
        for item_text in add_items:
            items.append({
                'type': 'item',
                'text': item_text,
                'checked': False
            })

        # Add descriptions after last added item
        for desc_text in descriptions:
            items.append({
                'type': 'description',
                'text': desc_text
            })

        # Check/uncheck items
        checklist_items = [item for item in items if item['type'] == 'item']

        for idx in check_items:
            if 1 <= idx <= len(checklist_items):
                # Find the actual item in the full list
                item_count = 0
                for item in items:
                    if item['type'] == 'item':
                        item_count += 1
                        if item_count == idx:
                            item['checked'] = True
                            break
            else:
                click.echo(f"⚠️  Warning: Item {idx} out of range (1-{len(checklist_items)})", err=True)

        for idx in uncheck_items:
            if 1 <= idx <= len(checklist_items):
                item_count = 0
                for item in items:
                    if item['type'] == 'item':
                        item_count += 1
                        if item_count == idx:
                            item['checked'] = False
                            break
            else:
                click.echo(f"⚠️  Warning: Item {idx} out of range (1-{len(checklist_items)})", err=True)

        # Update checklist
        new_text = format_checklist(items)
        set_checklist(client, issue_key, new_text)

        click.echo(f"✅ Updated checklist on {issue_key}")

        # Show updated checklist
        click.echo("\nUpdated checklist:")
        click.echo("=" * 40)
        display_checklist(items)
        click.echo()

        click.echo(f"🔗 View in Jira: {get_jira_url()}/browse/{issue_key}\n")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
