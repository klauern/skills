#!/usr/bin/env python3
"""
Core Jira API wrapper for authentication and common operations.

This module provides shared utilities for all fsec-jira scripts:
- get_client(): Get authenticated Jira client
- normalize_issue_key(): Convert "1234" to "FSEC-1234"
- text_to_adf(): Convert markdown-like text to Atlassian Document Format
- Field constants for FSEC custom fields

Usage:
    uv run jira_api.py --help

Environment variables:
    JIRA_URL: Jira instance URL (defaults to https://zendesk.atlassian.net)
    JIRA_EMAIL: User email for authentication
    JIRA_API_TOKEN: API token from Atlassian account settings
    JIRA_DEFAULT_PROJECT: Default project prefix (defaults to FSEC)
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
import re
import json
from typing import Dict, Any, Optional, List
import click
from atlassian import Jira
from pydantic import BaseModel, ConfigDict

# ==============================================================================
# FSEC Custom Field IDs
# ==============================================================================
FIELD_PLANNED_UNPLANNED = 'customfield_21659'
FIELD_ACCEPTANCE_CRITERIA = 'customfield_19300'
FIELD_WORK_ATTRIBUTION = 'customfield_21051'
FIELD_STORY_POINTS = 'customfield_10004'
FIELD_SPRINT = 'customfield_10009'
FIELD_CHECKLIST = 'customfield_21607'

# Valid issue types for FSEC project
VALID_ISSUE_TYPES = ['Epic', 'Story', 'Bug', 'Task', 'Spike', 'Sub-Task']


# ==============================================================================
# Configuration
# ==============================================================================
class JiraConfig(BaseModel):
    """Configuration for Jira connection."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    email: str
    api_token: str
    _client: Optional[Jira] = None

    @classmethod
    def from_env(cls) -> 'JiraConfig':
        """Create config from environment variables."""
        url = os.getenv('JIRA_URL', 'https://zendesk.atlassian.net')
        email = os.getenv('JIRA_EMAIL', '')
        api_token = os.getenv('JIRA_API_TOKEN', '')

        if not email or not api_token:
            missing = []
            if not email: missing.append('JIRA_EMAIL')
            if not api_token: missing.append('JIRA_API_TOKEN')
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(url=url, email=email, api_token=api_token)

    @property
    def client(self) -> Jira:
        """Lazy-loaded Jira client."""
        if self._client is None:
            self._client = Jira(
                url=self.url,
                username=self.email,
                password=self.api_token,
                cloud=True
            )
        return self._client


def get_client() -> Jira:
    """Get configured Jira client from environment variables."""
    config = JiraConfig.from_env()
    return config.client


def get_jira_url() -> str:
    """Get the Jira URL from environment."""
    return os.getenv('JIRA_URL', 'https://zendesk.atlassian.net')


def get_jira_credentials() -> tuple[str, str, str]:
    """Get Jira credentials from environment.

    Returns:
        Tuple of (url, email, api_token)
    """
    url = os.getenv('JIRA_URL', 'https://zendesk.atlassian.net')
    email = os.getenv('JIRA_EMAIL', '')
    api_token = os.getenv('JIRA_API_TOKEN', '')

    if not email or not api_token:
        raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN environment variables required")

    return url, email, api_token


# ==============================================================================
# Issue Key Normalization
# ==============================================================================
def normalize_issue_key(issue_ref: str) -> str:
    """Normalize issue reference to full key.

    Args:
        issue_ref: Ticket reference (e.g., 'FSEC-1234', '1234', 'PLAN-567')

    Returns:
        Full issue key (e.g., 'FSEC-1234')

    Examples:
        >>> normalize_issue_key('1234')
        'FSEC-1234'
        >>> normalize_issue_key('PLAN-567')
        'PLAN-567'
    """
    # If already in PROJECT-NUMBER format, return as-is
    if re.match(r'^[A-Z]+-\d+$', issue_ref):
        return issue_ref

    # If just a number, prepend default project
    if re.match(r'^\d+$', issue_ref):
        default_project = os.getenv('JIRA_DEFAULT_PROJECT', 'FSEC')
        return f"{default_project}-{issue_ref}"

    # Otherwise return as-is and let Jira API validate
    return issue_ref


# ==============================================================================
# Atlassian Document Format (ADF) Conversion
# ==============================================================================
def text_to_adf(text: str) -> Dict[str, Any]:
    """Convert text to Atlassian Document Format.

    Supports:
    - Bullet points (- or *)
    - Markdown links [text](url)
    - Jira wiki links [text|url]
    - Headers (# and ##)

    Args:
        text: Plain text or markdown-like content

    Returns:
        ADF document dictionary
    """
    def parse_inline_content(line: str) -> List[Dict[str, Any]]:
        """Parse a line and extract text and links as ADF nodes."""
        content = []
        # Pattern for markdown [text](url) or wiki [text|url] links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)|\[([^\]|]+)\|([^\]]+)\]'

        last_end = 0
        for match in re.finditer(link_pattern, line):
            # Add text before the link
            if match.start() > last_end:
                text_before = line[last_end:match.start()]
                if text_before:
                    content.append({"type": "text", "text": text_before})

            # Determine which pattern matched
            if match.group(1) and match.group(2):  # Markdown [text](url)
                link_text, link_url = match.group(1), match.group(2)
            else:  # Wiki [text|url]
                link_text, link_url = match.group(3), match.group(4)

            content.append({
                "type": "text",
                "text": link_text,
                "marks": [{"type": "link", "attrs": {"href": link_url}}]
            })
            last_end = match.end()

        # Add remaining text
        if last_end < len(line):
            remaining = line[last_end:]
            if remaining:
                content.append({"type": "text", "text": remaining})

        # If no links found, return simple text
        if not content and line:
            content = [{"type": "text", "text": line}]

        return content

    lines = text.strip().split('\n')
    doc_content = []
    bullet_items = []

    def flush_bullets():
        """Add accumulated bullet items as a bulletList."""
        nonlocal bullet_items
        if bullet_items:
            doc_content.append({"type": "bulletList", "content": bullet_items})
            bullet_items = []

    for line in lines:
        stripped = line.strip()

        # Headers (h2)
        if stripped.startswith('## '):
            flush_bullets()
            header_text = stripped[3:]
            doc_content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": parse_inline_content(header_text)
            })
        # Headers (h1)
        elif stripped.startswith('# '):
            flush_bullets()
            header_text = stripped[2:]
            doc_content.append({
                "type": "heading",
                "attrs": {"level": 1},
                "content": parse_inline_content(header_text)
            })
        # Bullet points
        elif stripped.startswith('- ') or stripped.startswith('* '):
            bullet_text = stripped[2:]
            bullet_items.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": parse_inline_content(bullet_text)
                }]
            })
        # Regular paragraphs
        else:
            flush_bullets()
            if stripped:
                doc_content.append({
                    "type": "paragraph",
                    "content": parse_inline_content(stripped)
                })

    # Flush any remaining bullets
    flush_bullets()

    return {"type": "doc", "version": 1, "content": doc_content}


def extract_text_from_adf(adf_content: Optional[Dict]) -> str:
    """Extract plain text from Atlassian Document Format (ADF).

    Args:
        adf_content: ADF content dictionary

    Returns:
        Plain text string
    """
    if not adf_content:
        return ""

    def extract_from_node(node: Dict) -> str:
        if isinstance(node, str):
            return node

        node_type = node.get('type', '')
        text_parts = []

        # Extract text content
        if 'text' in node:
            text_parts.append(node['text'])

        # Recursively process content
        if 'content' in node:
            for child in node['content']:
                child_text = extract_from_node(child)
                if child_text:
                    text_parts.append(child_text)

        # Add newlines for certain node types
        result = ' '.join(text_parts)
        if node_type in ['paragraph', 'heading', 'codeBlock']:
            result += '\n'

        return result

    return extract_from_node(adf_content).strip()


def get_issue(issue_key: str) -> Dict[str, Any]:
    """Get issue details by key.

    Args:
        issue_key: Issue key (e.g., FSEC-1234)

    Returns:
        Issue data dictionary
    """
    client = get_client()
    return client.issue(issue_key)


def update_issue_fields(issue_key: str, fields: Dict[str, Any]) -> None:
    """Update issue fields.

    Args:
        issue_key: Issue key (e.g., FSEC-1234)
        fields: Dictionary of field updates
    """
    client = get_client()
    client.update_issue_field(issue_key, fields)


def add_comment(issue_key: str, comment: str) -> None:
    """Add comment to issue.

    Args:
        issue_key: Issue key (e.g., FSEC-1234)
        comment: Comment text
    """
    client = get_client()
    client.issue_add_comment(issue_key, comment)


def transition_issue(issue_key: str, status: str) -> None:
    """Transition issue to new status.

    Args:
        issue_key: Issue key (e.g., FSEC-1234)
        status: Target status name (e.g., 'In Progress', 'Done')
    """
    client = get_client()
    client.set_issue_status(issue_key, status)


def get_all_fields() -> List[Dict[str, Any]]:
    """Get all available fields including custom fields.

    Returns:
        List of field definitions
    """
    client = get_client()
    return client.get_all_fields()


def search_issues(jql: str, fields: Optional[List[str]] = None, max_results: int = 50) -> Dict[str, Any]:
    """Search issues using JQL.

    Args:
        jql: JQL query string
        fields: List of field names to return (None = all)
        max_results: Maximum number of results

    Returns:
        Search results dictionary
    """
    client = get_client()
    return client.jql(jql, limit=max_results, fields=fields)


@click.group()
def cli():
    """Jira API command-line interface."""
    pass


@cli.command()
@click.argument('issue_key')
def get(issue_key: str):
    """Get issue details."""
    try:
        issue = get_issue(issue_key)
        click.echo(json.dumps(issue, indent=2))
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def fields():
    """List all available fields."""
    try:
        all_fields = get_all_fields()
        for field in all_fields:
            custom_marker = " [CUSTOM]" if field.get('custom') else ""
            click.echo(f"{field['id']}: {field['name']}{custom_marker}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('issue_key')
@click.argument('comment')
def comment(issue_key: str, comment: str):
    """Add comment to issue."""
    try:
        add_comment(issue_key, comment)
        click.echo(f"✅ Comment added to {issue_key}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('jql')
@click.option('--limit', default=50, help='Maximum results')
def search(jql: str, limit: int):
    """Search issues using JQL."""
    try:
        results = search_issues(jql, max_results=limit)
        click.echo(f"Found {results.get('total', 0)} issues:")
        for issue in results.get('issues', []):
            key = issue['key']
            summary = issue['fields'].get('summary', 'No summary')
            click.echo(f"  {key}: {summary}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
