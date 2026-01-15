#!/usr/bin/env python3
"""
Analyze Jira ticket readiness for pointing (estimation).

Detects common gaps and calculates a readiness score based on:
- Requirements completeness (70% weight)
- Technical clarity (20% weight)
- Test scenarios (5% weight)
- Context and constraints (5% weight)

Usage:
    uv run analyze_readiness.py FSEC-1234
    uv run analyze_readiness.py FSEC-1234 --verbose
    uv run analyze_readiness.py FSEC-1234 --json

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
import json
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
import click
from atlassian import Jira


@dataclass
class Gap:
    """Represents a detected gap in ticket readiness."""
    category: str  # requirements, technical, testing, context
    severity: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    questions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)


@dataclass
class ReadinessReport:
    """Complete readiness assessment report."""
    issue_key: str
    summary: str
    issue_type: str
    status: str

    requirements_score: float  # 0-70
    technical_score: float     # 0-20
    testing_score: float       # 0-5
    context_score: float       # 0-5
    total_score: float         # 0-100

    gaps: List[Gap] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    ready_for_pointing: bool = False


class ReadinessAnalyzer:
    """Analyzes Jira tickets for pointing readiness."""

    # Pattern keywords
    VAGUE_WORDS = ['maybe', 'probably', 'might', 'could', 'possibly',
                   'something like', 'similar to', 'kind of', 'etc', 'and so on']
    INCOMPLETE_MARKERS = ['TBD', 'TODO', '???', 'unclear', '...']
    AC_KEYWORDS = ['acceptance criteria', 'AC:', 'definition of done',
                   'success criteria', 'given', 'when', 'then']
    TECH_KEYWORDS = ['api', 'endpoint', 'database', 'table', 'schema',
                    'component', 'service', 'architecture']
    TEST_KEYWORDS = ['test', 'happy path', 'edge case', 'error handling',
                    'scenario', 'verify']
    SECURITY_KEYWORDS = ['password', 'token', 'auth', 'permission', 'pii',
                        'gdpr', 'encryption', 'security']

    def __init__(self, jira_client: Jira):
        self.client = jira_client

    def analyze(self, issue_key: str) -> ReadinessReport:
        """Analyze a ticket and return readiness report."""
        issue = self.client.issue(issue_key)
        fields = issue['fields']

        # Extract key fields
        description = fields.get('description', '') or ''
        summary = fields.get('summary', '')
        issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
        status = fields.get('status', {}).get('name', 'Unknown')

        # Get comments
        comments = []
        if 'comment' in fields and 'comments' in fields['comment']:
            comments = [c.get('body', '') for c in fields['comment']['comments']]

        # Combine all text for analysis
        all_text = f"{summary}\n{description}\n" + "\n".join(comments)

        # Run gap detection
        gaps = []
        gaps.extend(self._check_acceptance_criteria(description, issue_type))
        gaps.extend(self._check_vague_language(all_text))
        gaps.extend(self._check_technical_context(description, issue_type))
        gaps.extend(self._check_dependencies(all_text, issue))
        gaps.extend(self._check_test_scenarios(all_text, issue_type))
        gaps.extend(self._check_scope_creep(comments))
        gaps.extend(self._check_security_context(all_text))

        # Identify strengths
        strengths = self._identify_strengths(description, all_text, issue)

        # Calculate scores
        req_score = self._calculate_requirements_score(gaps)
        tech_score = self._calculate_technical_score(gaps)
        test_score = self._calculate_testing_score(gaps)
        ctx_score = self._calculate_context_score(gaps)
        total_score = req_score + tech_score + test_score + ctx_score

        # Determine if ready
        ready = total_score >= 75 and req_score >= 50

        return ReadinessReport(
            issue_key=issue_key,
            summary=summary,
            issue_type=issue_type,
            status=status,
            requirements_score=req_score,
            technical_score=tech_score,
            testing_score=test_score,
            context_score=ctx_score,
            total_score=total_score,
            gaps=gaps,
            strengths=strengths,
            ready_for_pointing=ready
        )

    def _check_acceptance_criteria(self, description: str, issue_type: str) -> List[Gap]:
        """Check for acceptance criteria."""
        gaps = []
        desc_lower = description.lower()

        # Check for AC keywords
        has_ac_section = any(kw in desc_lower for kw in self.AC_KEYWORDS)

        # Check for Given/When/Then format
        has_gwt_format = bool(re.search(r'\bgiven\b.*\bwhen\b.*\bthen\b', desc_lower, re.DOTALL))

        # Check for checkboxes or bullets
        has_criteria_list = bool(re.search(r'[-*•]\s*\[', description)) or \
                           bool(re.search(r'^\s*[-*•]\s+', description, re.MULTILINE))

        if not (has_ac_section or has_gwt_format or has_criteria_list):
            if issue_type.lower() not in ['bug', 'incident', 'hotfix']:
                gaps.append(Gap(
                    category='requirements',
                    severity='HIGH',
                    title='Missing Acceptance Criteria',
                    description='No clear definition of "done". What specific, testable conditions must be met?',
                    questions=[
                        'What are the success criteria?',
                        'How will we know this is working correctly?',
                        'What edge cases must be handled?'
                    ],
                    actions=[
                        'Schedule 15-min session with PO to define AC',
                        'Use format: Given [context], When [action], Then [outcome]',
                        'Document at least 2-3 criteria for features'
                    ]
                ))

        return gaps

    def _check_vague_language(self, text: str) -> List[Gap]:
        """Check for vague or ambiguous language."""
        gaps = []
        text_lower = text.lower()

        found_vague = []
        for word in self.VAGUE_WORDS:
            if word in text_lower:
                # Find context around the vague word
                pattern = rf'.{{0,50}}{re.escape(word)}.{{0,50}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    found_vague.append(f'"{matches[0].strip()}"')

        found_incomplete = []
        for marker in self.INCOMPLETE_MARKERS:
            if marker in text:
                found_incomplete.append(marker)

        if found_vague or found_incomplete:
            examples = found_vague[:3] if found_vague else found_incomplete[:3]
            gaps.append(Gap(
                category='requirements',
                severity='HIGH',
                title='Vague or Ambiguous Requirements',
                description=f'Found ambiguous language: {", ".join(examples)}',
                questions=[
                    'What are the specific requirements?',
                    'Can we remove uncertainty and be more precise?',
                    'What decisions need to be made?'
                ],
                actions=[
                    'Convert vague statements to specific questions',
                    'Assign questions to stakeholders for answers',
                    'Update ticket with specific requirements'
                ]
            ))

        return gaps

    def _check_technical_context(self, description: str, issue_type: str) -> List[Gap]:
        """Check for technical context and approach."""
        gaps = []

        if issue_type.lower() in ['bug', 'incident', 'hotfix']:
            return gaps  # Bugs often don't need upfront technical design

        desc_lower = description.lower()
        has_tech_keywords = any(kw in desc_lower for kw in self.TECH_KEYWORDS)
        has_tech_section = 'technical' in desc_lower and ('approach' in desc_lower or
                                                          'design' in desc_lower or
                                                          'notes' in desc_lower)

        if not (has_tech_keywords or has_tech_section):
            gaps.append(Gap(
                category='technical',
                severity='MEDIUM',
                title='No Technical Context',
                description='No discussion of implementation approach.',
                questions=[
                    'Which components/services are affected?',
                    'Are new API endpoints needed?',
                    'Are database schema changes required?',
                    'What is the high-level technical approach?'
                ],
                actions=[
                    'Tech lead to sketch approach in ticket',
                    'Identify 2-3 possible approaches if unclear',
                    'Note any major technical decisions needed',
                    'List affected components and services'
                ]
            ))

        return gaps

    def _check_dependencies(self, text: str, issue: Dict[str, Any]) -> List[Gap]:
        """Check for missing or unlinked dependencies."""
        gaps = []

        # Check for dependency keywords without links
        dep_pattern = r'\b(depends on|blocked by|requires|needs|after)\b'
        has_dep_mention = bool(re.search(dep_pattern, text, re.IGNORECASE))

        # Check for ticket references without links
        ticket_refs = re.findall(r'\b([A-Z]+-\d+)\b', text)

        # Check if issue has linked issues
        fields = issue.get('fields', {})
        issue_links = fields.get('issuelinks', [])

        if (has_dep_mention or ticket_refs) and not issue_links:
            gaps.append(Gap(
                category='technical',
                severity='MEDIUM',
                title='Missing Dependencies',
                description='Description mentions dependencies but no linked tickets.',
                questions=[
                    'Which tickets must be completed first?',
                    'What are the blocking dependencies?',
                    'Are there external service dependencies?'
                ],
                actions=[
                    'Link to dependent tickets',
                    'Add "blocked by" relationships if applicable',
                    'Document any external service dependencies',
                    'Clarify which dependencies are hard blockers'
                ]
            ))

        return gaps

    def _check_test_scenarios(self, text: str, issue_type: str) -> List[Gap]:
        """Check for test scenarios."""
        gaps = []

        text_lower = text.lower()
        has_test_keywords = any(kw in text_lower for kw in self.TEST_KEYWORDS)
        has_test_section = 'test' in text_lower and ('scenario' in text_lower or
                                                     'case' in text_lower or
                                                     'plan' in text_lower)

        if not (has_test_keywords or has_test_section):
            if issue_type.lower() not in ['spike', 'research']:
                gaps.append(Gap(
                    category='testing',
                    severity='LOW',
                    title='No Test Scenarios',
                    description='No discussion of how to verify this works.',
                    questions=[
                        'What is the happy path scenario?',
                        'What edge cases need testing?',
                        'What error conditions should be tested?',
                        'What test data is needed?'
                    ],
                    actions=[
                        'Document at least happy path + 2 edge cases',
                        'Specify error handling requirements',
                        'Note any special test data needs'
                    ]
                ))

        return gaps

    def _check_scope_creep(self, comments: List[str]) -> List[Gap]:
        """Check for scope creep in comments."""
        gaps = []

        if len(comments) < 5:
            return gaps

        # Look for additive language in comments
        additive_pattern = r'\b(also|additionally|we should also|another thing|plus)\b'
        comment_additions = sum(1 for c in comments if re.search(additive_pattern, c, re.IGNORECASE))

        if comment_additions >= 3:
            gaps.append(Gap(
                category='requirements',
                severity='MEDIUM',
                title='Scope Growing in Comments',
                description=f'Found {comment_additions} comments adding requirements. May need splitting.',
                questions=[
                    'What is the current scope?',
                    'Should this be split into multiple tickets?',
                    'What is the minimum viable implementation?'
                ],
                actions=[
                    'Review all comments for scope changes',
                    'Update description to match current understanding',
                    'Consider splitting into multiple tickets',
                    'Get PO to confirm final scope'
                ]
            ))

        return gaps

    def _check_security_context(self, text: str) -> List[Gap]:
        """Check for security context where needed."""
        gaps = []

        text_lower = text.lower()
        has_security_keywords = any(kw in text_lower for kw in self.SECURITY_KEYWORDS)
        has_security_section = 'security' in text_lower or 'compliance' in text_lower

        if has_security_keywords and not has_security_section:
            gaps.append(Gap(
                category='context',
                severity='HIGH',
                title='Security Review Needed',
                description='Ticket involves sensitive data but lacks security context.',
                questions=[
                    'What are the security requirements?',
                    'Are there compliance considerations (GDPR, SOC2)?',
                    'How is sensitive data protected?',
                    'What audit logging is needed?'
                ],
                actions=[
                    'Schedule security review',
                    'Document security requirements',
                    'Add security-specific acceptance criteria',
                    'Flag for security team review'
                ]
            ))

        return gaps

    def _identify_strengths(self, description: str, all_text: str, issue: Dict[str, Any]) -> List[str]:
        """Identify positive aspects of the ticket."""
        strengths = []

        # Check for good practices
        if any(kw in description.lower() for kw in self.AC_KEYWORDS):
            strengths.append('Has acceptance criteria')

        if any(kw in all_text.lower() for kw in self.TEST_KEYWORDS):
            strengths.append('Test scenarios discussed')

        if any(kw in description.lower() for kw in self.TECH_KEYWORDS):
            strengths.append('Technical context provided')

        fields = issue.get('fields', {})
        if fields.get('issuelinks'):
            strengths.append('Dependencies linked')

        if len(description) > 200:
            strengths.append('Detailed description')

        return strengths

    def _calculate_requirements_score(self, gaps: List[Gap]) -> float:
        """Calculate requirements score (0-70)."""
        req_gaps = [g for g in gaps if g.category == 'requirements']
        high_severity = sum(1 for g in req_gaps if g.severity == 'HIGH')
        medium_severity = sum(1 for g in req_gaps if g.severity == 'MEDIUM')

        # Start at 70, deduct for gaps
        score = 70.0
        score -= high_severity * 25  # Major deduction for missing AC, vague reqs
        score -= medium_severity * 10  # Medium deduction for scope issues

        return max(0, score)

    def _calculate_technical_score(self, gaps: List[Gap]) -> float:
        """Calculate technical score (0-20)."""
        tech_gaps = [g for g in gaps if g.category == 'technical']
        high_severity = sum(1 for g in tech_gaps if g.severity == 'HIGH')
        medium_severity = sum(1 for g in tech_gaps if g.severity == 'MEDIUM')

        score = 20.0
        score -= high_severity * 15
        score -= medium_severity * 8

        return max(0, score)

    def _calculate_testing_score(self, gaps: List[Gap]) -> float:
        """Calculate testing score (0-5)."""
        test_gaps = [g for g in gaps if g.category == 'testing']

        if test_gaps:
            return 0.0
        return 5.0

    def _calculate_context_score(self, gaps: List[Gap]) -> float:
        """Calculate context score (0-5)."""
        ctx_gaps = [g for g in gaps if g.category == 'context']
        high_severity = sum(1 for g in ctx_gaps if g.severity == 'HIGH')

        score = 5.0
        score -= high_severity * 5  # Missing security context is critical

        return max(0, score)


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


def format_report(report: ReadinessReport, verbose: bool = False) -> str:
    """Format readiness report as human-readable text."""
    lines = []

    # Header
    lines.append(f"\n{'='*80}")
    lines.append(f"Readiness Analysis: {report.issue_key}")
    lines.append(f"{'='*80}")
    lines.append(f"Summary: {report.summary}")
    lines.append(f"Type: {report.issue_type} | Status: {report.status}")
    lines.append("")

    # Score
    score_emoji = "✅" if report.total_score >= 90 else "⚠️" if report.total_score >= 75 else "❌"
    lines.append(f"📊 Readiness Score: {report.total_score:.1f}/100 {score_emoji}")
    lines.append(f"   Requirements: {report.requirements_score:.1f}/70")
    lines.append(f"   Technical:    {report.technical_score:.1f}/20")
    lines.append(f"   Testing:      {report.testing_score:.1f}/5")
    lines.append(f"   Context:      {report.context_score:.1f}/5")
    lines.append("")

    if report.total_score >= 90:
        lines.append("✅ READY FOR POINTING - Excellent readiness")
    elif report.total_score >= 75:
        lines.append("⚠️  MOSTLY READY - Minor clarifications needed")
    elif report.total_score >= 60:
        lines.append("❌ NOT READY - Some gaps to address")
    else:
        lines.append("❌ NOT READY - Significant work needed")
    lines.append("")

    # Strengths
    if report.strengths:
        lines.append(f"✅ Strengths:")
        for strength in report.strengths:
            lines.append(f"   • {strength}")
        lines.append("")

    # Gaps
    if report.gaps:
        lines.append(f"❌ Gaps Found ({len(report.gaps)}):")
        lines.append("")

        for i, gap in enumerate(report.gaps, 1):
            severity_emoji = "🔴" if gap.severity == "HIGH" else "🟡" if gap.severity == "MEDIUM" else "🔵"
            lines.append(f"{i}. {severity_emoji} {gap.title} [{gap.severity}]")
            lines.append(f"   {gap.description}")

            if verbose:
                if gap.questions:
                    lines.append("   Questions:")
                    for q in gap.questions:
                        lines.append(f"      • {q}")

                if gap.actions:
                    lines.append("   Actions:")
                    for a in gap.actions:
                        lines.append(f"      • {a}")

            lines.append("")
    else:
        lines.append("✅ No gaps detected!")
        lines.append("")

    # Recommendation
    lines.append("💡 Recommendation:")
    if report.ready_for_pointing:
        lines.append("   This ticket is ready for pointing. Minor gaps can be addressed during planning.")
    else:
        high_gaps = [g for g in report.gaps if g.severity == 'HIGH']
        if high_gaps:
            lines.append("   Address HIGH severity gaps before pointing:")
            for gap in high_gaps[:3]:
                lines.append(f"   • {gap.title}")
                if gap.actions:
                    lines.append(f"     → {gap.actions[0]}")

    lines.append(f"{'='*80}\n")

    return "\n".join(lines)


@click.command()
@click.argument('issue_key')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed questions and actions')
@click.option('--json-output', '--json', is_flag=True, help='Output as JSON')
def main(issue_key: str, verbose: bool, json_output: bool):
    """Analyze a Jira ticket for pointing readiness."""
    try:
        client = get_jira_client()
        analyzer = ReadinessAnalyzer(client)

        click.echo(f"Analyzing {issue_key}...", err=True)
        report = analyzer.analyze(issue_key)

        if json_output:
            # Output as JSON
            output = {
                'issue_key': report.issue_key,
                'summary': report.summary,
                'issue_type': report.issue_type,
                'status': report.status,
                'scores': {
                    'requirements': report.requirements_score,
                    'technical': report.technical_score,
                    'testing': report.testing_score,
                    'context': report.context_score,
                    'total': report.total_score
                },
                'ready_for_pointing': report.ready_for_pointing,
                'gaps': [
                    {
                        'category': g.category,
                        'severity': g.severity,
                        'title': g.title,
                        'description': g.description,
                        'questions': g.questions,
                        'actions': g.actions
                    }
                    for g in report.gaps
                ],
                'strengths': report.strengths
            }
            click.echo(json.dumps(output, indent=2))
        else:
            # Output as formatted text
            click.echo(format_report(report, verbose=verbose))

        # Exit code: 0 if ready, 1 if not ready
        sys.exit(0 if report.ready_for_pointing else 1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(2)


if __name__ == '__main__':
    main()
