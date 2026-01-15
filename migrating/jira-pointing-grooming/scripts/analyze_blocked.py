#!/usr/bin/env python3
"""
Analyze blocked tickets to understand what's blocking them.

Generates a comprehensive report showing:
- Why tickets are blocked (from description/comments)
- Readiness scores for each blocked ticket
- How long they've been blocked
- Linked blocker tickets
- Recommendations for unblocking

Usage:
    uv run analyze_blocked.py --project FSEC
    uv run analyze_blocked.py --project FSEC --detailed
    uv run analyze_blocked.py --project FSEC --min-age-days 30

Environment variables:
    JIRA_URL: Jira instance URL (defaults to https://zendesk.atlassian.net)
    JIRA_EMAIL: User email for authentication (defaults to {whoami}@zendesk.com)
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
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import click
from atlassian import Jira


@dataclass
class BlockedTicket:
    """Information about a blocked ticket."""
    key: str
    summary: str
    status: str
    priority: str
    age_days: int
    blocked_since_days: Optional[int]
    blocker_reason: str
    linked_blockers: List[str]
    estimated: bool
    readiness_score: Optional[float] = None


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


def find_blocked_tickets(client: Jira, project: str, min_age_days: int = 0) -> List[Dict[str, Any]]:
    """Find all blocked tickets in the project."""
    jql = f'project = {project} AND status = Blocked'

    if min_age_days > 0:
        jql += f' AND created <= -{min_age_days}d'

    jql += ' ORDER BY created ASC'  # Oldest first

    fields = ['summary', 'status', 'priority', 'created', 'updated',
              'description', 'comment', 'issuelinks', 'customfield_10016']  # Story Points

    result = client.jql(jql, limit=100, fields=fields)
    return result.get('issues', [])


def extract_blocker_reason(description: str, comments: List[str]) -> str:
    """Extract why the ticket is blocked from description or comments."""
    all_text = f"{description}\n" + "\n".join(comments)

    # Look for common blocker patterns
    blocker_patterns = [
        r'(?:blocked by|waiting (?:on|for)|depends on|needs)\s+([^\n.]+)',
        r'(?:blocker|blocking issue):\s*([^\n.]+)',
        r'(?:cannot proceed|can\'t start) (?:until|because)\s+([^\n.]+)',
    ]

    reasons = []
    for pattern in blocker_patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        reasons.extend(matches[:2])  # Take first 2 matches of each pattern

    if reasons:
        # Clean up and deduplicate
        cleaned = []
        seen = set()
        for reason in reasons:
            reason = reason.strip()
            if reason.lower() not in seen and len(reason) > 10:
                cleaned.append(reason)
                seen.add(reason.lower())
        return '; '.join(cleaned[:3])  # Max 3 reasons

    # No explicit reason found
    return "No explicit blocker reason documented"


def find_linked_blockers(issue: Dict[str, Any]) -> List[str]:
    """Find tickets that are blocking this issue."""
    blockers = []
    links = issue.get('fields', {}).get('issuelinks', [])

    for link in links:
        # Check if this is an "is blocked by" relationship
        link_type = link.get('type', {}).get('name', '')

        if 'inwardIssue' in link and link_type.lower() in ['blocks', 'blocker']:
            blocker_key = link['inwardIssue'].get('key')
            blocker_status = link['inwardIssue'].get('fields', {}).get('status', {}).get('name', 'Unknown')
            if blocker_key:
                blockers.append(f"{blocker_key} ({blocker_status})")

    return blockers


def calculate_days_since(date_str: str) -> int:
    """Calculate days since a date string."""
    try:
        date = datetime.strptime(date_str[:10], '%Y-%m-%d')
        return (datetime.now() - date).days
    except:
        return 0


def estimate_blocked_since(comments: List[Dict[str, Any]]) -> Optional[int]:
    """Estimate when ticket became blocked from comment history."""
    for comment in reversed(comments):  # Start from oldest
        body = comment.get('body', '').lower()
        if 'blocked' in body or 'blocking' in body:
            created = comment.get('created', '')
            days = calculate_days_since(created)
            if days > 0:
                return days
    return None


def is_estimated(fields: Dict[str, Any]) -> bool:
    """Check if ticket has story points."""
    story_points = fields.get('customfield_10016')  # Story Points field
    return story_points is not None and story_points > 0


def analyze_blocked_tickets(
    client: Jira,
    project: str,
    min_age_days: int = 0,
    include_readiness: bool = False
) -> List[BlockedTicket]:
    """Analyze all blocked tickets."""
    issues = find_blocked_tickets(client, project, min_age_days)

    blocked_tickets = []
    for issue in issues:
        key = issue['key']
        fields = issue['fields']

        # Extract basic info
        summary = fields.get('summary', 'No summary')
        status = fields.get('status', {}).get('name', 'Unknown')
        priority = fields.get('priority', {}).get('name', 'None')
        created = fields.get('created', '')
        age_days = calculate_days_since(created)

        # Extract blocker info
        description = fields.get('description', '') or ''
        comment_data = fields.get('comment', {}).get('comments', [])
        comments = [c.get('body', '') for c in comment_data]

        blocker_reason = extract_blocker_reason(description, comments)
        linked_blockers = find_linked_blockers(issue)
        blocked_since = estimate_blocked_since(comment_data)
        estimated = is_estimated(fields)

        ticket = BlockedTicket(
            key=key,
            summary=summary,
            status=status,
            priority=priority,
            age_days=age_days,
            blocked_since_days=blocked_since,
            blocker_reason=blocker_reason,
            linked_blockers=linked_blockers,
            estimated=estimated
        )

        # Optionally calculate readiness score
        if include_readiness:
            try:
                from analyze_readiness import ReadinessAnalyzer
                analyzer = ReadinessAnalyzer(client)
                report = analyzer.analyze(key)
                ticket.readiness_score = report.total_score
            except:
                pass  # Skip if analyzer fails

        blocked_tickets.append(ticket)

    return blocked_tickets


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
        return f"{weeks} week{'s' if weeks > 1 else ''}"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''}"
    else:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''}"


def format_blocked_report(tickets: List[BlockedTicket], detailed: bool = False) -> str:
    """Format blocked tickets report."""
    if not tickets:
        return "✅ No blocked tickets found!\n"

    lines = []
    lines.append(f"\n{'='*100}")
    lines.append(f"BLOCKED TICKETS REPORT - Found {len(tickets)} blocked ticket(s)")
    lines.append(f"{'='*100}\n")

    # Summary statistics
    total_age = sum(t.age_days for t in tickets)
    avg_age = total_age / len(tickets) if tickets else 0
    estimated_count = sum(1 for t in tickets if t.estimated)
    with_linked_blockers = sum(1 for t in tickets if t.linked_blockers)
    ancient_tickets = sum(1 for t in tickets if t.age_days > 180)  # > 6 months

    lines.append("📊 SUMMARY STATISTICS")
    lines.append(f"   Total blocked: {len(tickets)}")
    lines.append(f"   Average age: {format_age(int(avg_age))}")
    lines.append(f"   Estimated: {estimated_count}/{len(tickets)}")
    lines.append(f"   With linked blockers: {with_linked_blockers}/{len(tickets)}")
    lines.append(f"   Ancient (>6 months): {ancient_tickets}")
    lines.append("")

    # Age distribution
    lines.append("📅 AGE DISTRIBUTION")
    age_buckets = {
        'Recent (< 1 month)': sum(1 for t in tickets if t.age_days < 30),
        'Moderate (1-3 months)': sum(1 for t in tickets if 30 <= t.age_days < 90),
        'Old (3-6 months)': sum(1 for t in tickets if 90 <= t.age_days < 180),
        'Ancient (> 6 months)': sum(1 for t in tickets if t.age_days >= 180),
    }
    for bucket, count in age_buckets.items():
        if count > 0:
            lines.append(f"   {bucket}: {count}")
    lines.append("")

    # Sort by age (oldest first)
    tickets_sorted = sorted(tickets, key=lambda t: t.age_days, reverse=True)

    lines.append("🚫 BLOCKED TICKETS (Oldest First)")
    lines.append(f"{'='*100}\n")

    for i, ticket in enumerate(tickets_sorted, 1):
        # Header
        age_emoji = "🔴" if ticket.age_days > 180 else "🟡" if ticket.age_days > 90 else "🟢"
        est_emoji = "📊" if ticket.estimated else "❓"

        lines.append(f"{i}. {age_emoji} {ticket.key} - {ticket.summary[:70]}")
        lines.append(f"   {est_emoji} Priority: {ticket.priority} | Age: {format_age(ticket.age_days)}", )

        if ticket.blocked_since_days:
            lines.append(f"   ⏱️  Blocked for: ~{format_age(ticket.blocked_since_days)}")

        # Blocker reason
        lines.append(f"   🚧 Blocker: {ticket.blocker_reason[:100]}")

        # Linked blockers
        if ticket.linked_blockers:
            lines.append(f"   🔗 Blocking tickets: {', '.join(ticket.linked_blockers)}")
        else:
            lines.append(f"   🔗 No linked blocker tickets")

        # Readiness score if available
        if ticket.readiness_score is not None:
            score_emoji = "✅" if ticket.readiness_score >= 75 else "⚠️" if ticket.readiness_score >= 60 else "❌"
            lines.append(f"   {score_emoji} Readiness: {ticket.readiness_score:.0f}/100")

        # Recommendation
        if ticket.age_days > 180:
            lines.append(f"   💡 Recommendation: Consider closing if still blocked after 6+ months")
        elif not ticket.linked_blockers and "no explicit" in ticket.blocker_reason.lower():
            lines.append(f"   💡 Recommendation: Document specific blocker or unblock if resolved")
        elif ticket.linked_blockers:
            # Check if any blockers are done
            done_blockers = [b for b in ticket.linked_blockers if 'Done' in b or 'Closed' in b]
            if done_blockers:
                lines.append(f"   💡 Recommendation: Linked blocker(s) are done - unblock this ticket!")

        lines.append("")

    # Action items
    lines.append(f"{'='*100}")
    lines.append("📋 RECOMMENDED ACTIONS\n")

    # Ancient tickets
    ancient = [t for t in tickets if t.age_days > 180]
    if ancient:
        lines.append(f"1. Review {len(ancient)} ancient tickets (>6 months blocked):")
        for t in ancient[:5]:  # Show first 5
            lines.append(f"   • {t.key} - {format_age(t.age_days)} old")
        if len(ancient) > 5:
            lines.append(f"   • ... and {len(ancient) - 5} more")
        lines.append("")

    # No documented blocker
    no_reason = [t for t in tickets if "no explicit" in t.blocker_reason.lower()]
    if no_reason:
        lines.append(f"2. Document blockers for {len(no_reason)} tickets with unclear reasons:")
        for t in no_reason[:5]:
            lines.append(f"   • {t.key}")
        lines.append("")

    # Potentially unblocked
    potentially_unblocked = [t for t in tickets if t.linked_blockers and
                            any('Done' in b or 'Closed' in b for b in t.linked_blockers)]
    if potentially_unblocked:
        lines.append(f"3. Unblock {len(potentially_unblocked)} tickets with completed blockers:")
        for t in potentially_unblocked:
            lines.append(f"   • {t.key} - blockers: {', '.join(t.linked_blockers)}")
        lines.append("")

    # Unestimated blockers
    unestimated = [t for t in tickets if not t.estimated and t.age_days < 90]
    if unestimated:
        lines.append(f"4. Estimate {len(unestimated)} unestimated blocked tickets (when unblocked):")
        for t in unestimated[:5]:
            lines.append(f"   • {t.key}")
        lines.append("")

    lines.append(f"{'='*100}\n")

    return "\n".join(lines)


@click.command()
@click.option('--project', '-p', default='FSEC', help='Project key (default: FSEC)')
@click.option('--min-age-days', type=int, default=0,
              help='Only show tickets blocked for at least N days')
@click.option('--detailed', '-d', is_flag=True,
              help='Include readiness scores (slower, requires analysis)')
@click.option('--output', '-o', type=click.Path(),
              help='Save report to file instead of stdout')
def main(project: str, min_age_days: int, detailed: bool, output: Optional[str]):
    """
    Analyze blocked tickets to understand what's blocking them.

    Examples:
        # All blocked tickets
        uv run analyze_blocked.py

        # Only tickets blocked > 30 days
        uv run analyze_blocked.py --min-age-days 30

        # Include readiness scores
        uv run analyze_blocked.py --detailed

        # Save to file
        uv run analyze_blocked.py --output blocked_report.txt
    """
    try:
        client = get_jira_client()

        click.echo(f"Analyzing blocked tickets in {project}...", err=True)
        if min_age_days > 0:
            click.echo(f"Filtering to tickets blocked > {min_age_days} days...", err=True)
        if detailed:
            click.echo("Including readiness analysis (this may take a while)...", err=True)

        tickets = analyze_blocked_tickets(
            client,
            project,
            min_age_days=min_age_days,
            include_readiness=detailed
        )

        report = format_blocked_report(tickets, detailed=detailed)

        if output:
            with open(output, 'w') as f:
                f.write(report)
            click.echo(f"✅ Report saved to: {output}")
        else:
            click.echo(report)

        # Exit code: 0 if found tickets, 1 if none found
        sys.exit(0 if tickets else 1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
