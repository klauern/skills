#!/usr/bin/env python3
"""
FSEC-specific ticket readiness analyzer.

Adjusted scoring based on analysis of 30+ completed FSEC tickets from the past 6 months.
Recognizes FSEC's pragmatic, technically-focused style rather than formal AC.

Key differences from standard analyzer:
- Reduced weight on formal AC (FSEC uses implicit acceptance criteria)
- Increased weight on technical context (core of FSEC tickets)
- Added scoring for code/system links and problem statements
- More lenient on "might"/"could" language (technical options are OK)
- Lower ready-for-pointing threshold (60 vs 75)

Usage:
    uv run analyze_readiness_fsec.py FSEC-1234
    uv run analyze_readiness_fsec.py FSEC-1234 --verbose
    uv run analyze_readiness_fsec.py FSEC-1234 --json

Environment variables:
    JIRA_URL: Jira instance URL (defaults to https://zendesk.atlassian.net)
    JIRA_EMAIL: User email for authentication
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
import json
import re
from typing import Dict, Any, List
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

    requirements_score: float  # 0-40 (reduced from 70)
    technical_score: float     # 0-40 (increased from 20)
    context_score: float       # 0-15 (increased from 5)
    testing_score: float       # 0-5 (same)
    total_score: float         # 0-100

    gaps: List[Gap] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    ready_for_pointing: bool = False
    mode: str = "FSEC"


class FSECReadinessAnalyzer:
    """Analyzes Jira tickets for pointing readiness using FSEC-specific criteria."""

    # FSEC-specific keywords
    CRITICAL_VAGUE = ['TBD', 'TODO', '???', 'unclear', 'figure it out']
    PROBLEM_INDICATORS = ['problem', 'issue', 'currently', 'need to', 'should',
                          'request', 'broken', 'failing']
    AWS_KEYWORDS = ['account', 'lambda', 's3', 'iam', 'api', 'policy', 'kms',
                    'ec2', 'vpc', 'scp', 'role', 'cloudformation', 'terraform']
    IMPLEMENTATION_KEYWORDS = ['create', 'update', 'modify', 'deploy', 'configure',
                               'implement', 'add', 'remove', 'migrate', 'move']
    SECURITY_KEYWORDS = ['iam', 'policy', 'role', 'permission', 'auth', 'encryption',
                        'kms', 'security', 'compliance']
    TEST_KEYWORDS = ['test', 'verify', 'validate', 'check']

    def __init__(self, jira_client: Jira):
        self.client = jira_client

    def analyze(self, issue_key: str) -> ReadinessReport:
        """Analyze a ticket using FSEC-specific criteria."""
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

        # Combine text
        all_text = f"{summary}\n{description}\n" + "\n".join(comments)

        # Run FSEC-specific analysis
        gaps = []
        gaps.extend(self._check_problem_statement(description))
        gaps.extend(self._check_critical_ambiguity(all_text))
        gaps.extend(self._check_aws_context(description, issue_type))
        gaps.extend(self._check_implementation_clarity(description))
        gaps.extend(self._check_references(description))
        gaps.extend(self._check_security_context(all_text))

        # Identify strengths
        strengths = self._identify_strengths(description, all_text, issue)

        # Calculate scores using FSEC weighting
        req_score = self._calculate_requirements_score(description, gaps)
        tech_score = self._calculate_technical_score(description, issue, gaps)
        ctx_score = self._calculate_context_score(description, gaps)
        test_score = self._calculate_testing_score(all_text)
        total_score = req_score + tech_score + ctx_score + test_score

        # FSEC threshold: 60+ (vs standard 75+)
        ready = total_score >= 60 and req_score >= 25

        return ReadinessReport(
            issue_key=issue_key,
            summary=summary,
            issue_type=issue_type,
            status=status,
            requirements_score=req_score,
            technical_score=tech_score,
            context_score=ctx_score,
            testing_score=test_score,
            total_score=total_score,
            gaps=gaps,
            strengths=strengths,
            ready_for_pointing=ready
        )

    def _check_problem_statement(self, description: str) -> List[Gap]:
        """Check for clear problem or request."""
        gaps = []
        desc_lower = description.lower()

        has_problem = any(word in desc_lower for word in self.PROBLEM_INDICATORS)
        has_substance = len(description.strip()) > 50

        if not (has_problem or has_substance):
            gaps.append(Gap(
                category='requirements',
                severity='HIGH',
                title='Missing Problem Statement',
                description='No clear description of what needs to change or why.',
                questions=['What problem are we solving?', 'Who requested this?'],
                actions=['Add context about what needs to change', 'Link to Slack thread or related ticket']
            ))

        return gaps

    def _check_critical_ambiguity(self, text: str) -> List[Gap]:
        """Check for CRITICAL vague language (TBD, ???) but not normal uncertainty."""
        gaps = []

        found_critical = []
        for marker in self.CRITICAL_VAGUE:
            if marker in text:
                pattern = rf'.{{0,50}}{re.escape(marker)}.{{0,50}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    found_critical.append(f'"{matches[0].strip()}"')

        if found_critical:
            gaps.append(Gap(
                category='requirements',
                severity='HIGH',
                title='Critical Ambiguity',
                description=f'Found blockers: {", ".join(found_critical[:2])}',
                questions=['What needs to be decided before we can estimate?'],
                actions=['Convert TBD/TODO into specific questions', 'Assign owners to open questions']
            ))

        return gaps

    def _check_aws_context(self, description: str, issue_type: str) -> List[Gap]:
        """Check for AWS/infrastructure context."""
        gaps = []

        if issue_type.lower() in ['spike', 'research']:
            return gaps

        desc_lower = description.lower()
        has_aws = any(kw in desc_lower for kw in self.AWS_KEYWORDS)

        if not has_aws and len(description) < 100:
            gaps.append(Gap(
                category='technical',
                severity='MEDIUM',
                title='Limited AWS Context',
                description='Minimal technical details about affected systems.',
                questions=['Which AWS accounts/services are affected?',
                          'What infrastructure components need changes?'],
                actions=['List affected accounts, services, or modules',
                        'Add links to relevant code or AWS console']
            ))

        return gaps

    def _check_implementation_clarity(self, description: str) -> List[Gap]:
        """Check for clear implementation approach."""
        gaps = []
        desc_lower = description.lower()

        has_action = any(kw in desc_lower for kw in self.IMPLEMENTATION_KEYWORDS)
        has_substance = len(description) > 100

        if not has_action and not has_substance:
            gaps.append(Gap(
                category='technical',
                severity='MEDIUM',
                title='Unclear Implementation',
                description='No clear description of what to build or change.',
                questions=['What specifically needs to be created/modified?',
                          'What is the high-level approach?'],
                actions=['Add implementation details', 'Describe the solution approach']
            ))

        return gaps

    def _check_references(self, description: str) -> List[Gap]:
        """Check for links to code, Slack, or related resources."""
        gaps = []

        has_github = 'github.com' in description
        has_slack = 'slack.com' in description
        has_jira = bool(re.search(r'\b[A-Z]+-\d+\b', description))

        # Not a gap - just a missed opportunity for 'excellent'
        # Only flag if description is very short
        if not (has_github or has_slack or has_jira) and len(description) < 100:
            gaps.append(Gap(
                category='context',
                severity='LOW',
                title='No References',
                description='Could benefit from links to code, Slack, or related tickets.',
                questions=[],
                actions=['Add link to relevant GitHub repo/file',
                        'Link to Slack discussion if applicable']
            ))

        return gaps

    def _check_security_context(self, text: str) -> List[Gap]:
        """Check for security context when needed."""
        gaps = []
        text_lower = text.lower()

        has_security_keywords = any(kw in text_lower for kw in self.SECURITY_KEYWORDS)
        has_security_section = 'security' in text_lower or 'iam policy' in text_lower

        # Only flag if security keywords present but no discussion
        if has_security_keywords and not has_security_section and len(text) < 300:
            gaps.append(Gap(
                category='context',
                severity='MEDIUM',
                title='Security Implications',
                description='Involves IAM/policies but lacks security discussion.',
                questions=['What are the security implications?',
                          'What permissions are being granted?'],
                actions=['Add brief security context', 'Note if security review needed']
            ))

        return gaps

    def _identify_strengths(self, description: str, all_text: str, issue: Dict[str, Any]) -> List[str]:
        """Identify positive aspects of the ticket."""
        strengths = []

        # Problem statement
        if any(word in description.lower() for word in self.PROBLEM_INDICATORS):
            strengths.append('Clear problem or request')

        # AWS context
        if any(kw in description.lower() for kw in self.AWS_KEYWORDS):
            strengths.append('AWS infrastructure context')

        # Implementation clarity
        if any(kw in description.lower() for kw in self.IMPLEMENTATION_KEYWORDS):
            strengths.append('Clear implementation approach')

        # References
        if 'github.com' in description:
            strengths.append('Code references')
        if 'slack.com' in description:
            strengths.append('Slack thread linked')

        # Links
        fields = issue.get('fields', {})
        if fields.get('issuelinks'):
            strengths.append('Related tickets linked')

        # Detailed
        if len(description) > 200:
            strengths.append('Detailed description')

        return strengths

    def _calculate_requirements_score(self, description: str, gaps: List[Gap]) -> float:
        """Calculate requirements score (0-40) based on FSEC patterns."""
        score = 40.0

        # Deduct for gaps
        req_gaps = [g for g in gaps if g.category == 'requirements']
        high_severity = sum(1 for g in req_gaps if g.severity == 'HIGH')
        medium_severity = sum(1 for g in req_gaps if g.severity == 'MEDIUM')

        score -= high_severity * 15  # Reduced from 25
        score -= medium_severity * 5  # Reduced from 10

        return max(0, score)

    def _calculate_technical_score(self, description: str, issue: Dict, gaps: List[Gap]) -> float:
        """Calculate technical score (0-40) with positive scoring for FSEC elements."""
        score = 0

        # Award points for what's present
        desc_lower = description.lower()

        # AWS context (15 points)
        if any(kw in desc_lower for kw in self.AWS_KEYWORDS):
            score += 15

        # Implementation clarity (15 points)
        if any(kw in desc_lower for kw in self.IMPLEMENTATION_KEYWORDS):
            score += 15

        # References (10 points)
        has_refs = ('github.com' in description or
                   'slack.com' in description or
                   bool(re.search(r'\b[A-Z]+-\d+\b', description)))
        if has_refs:
            score += 10

        # Deduct for gaps
        tech_gaps = [g for g in gaps if g.category == 'technical']
        medium_severity = sum(1 for g in tech_gaps if g.severity == 'MEDIUM')
        score -= medium_severity * 5

        return min(40, max(0, score))

    def _calculate_context_score(self, description: str, gaps: List[Gap]) -> float:
        """Calculate context score (0-15)."""
        score = 15.0

        ctx_gaps = [g for g in gaps if g.category == 'context']
        high_severity = sum(1 for g in ctx_gaps if g.severity == 'HIGH')
        medium_severity = sum(1 for g in ctx_gaps if g.severity == 'MEDIUM')
        low_severity = sum(1 for g in ctx_gaps if g.severity == 'LOW')

        score -= high_severity * 10
        score -= medium_severity * 5
        score -= low_severity * 2

        return max(0, score)

    def _calculate_testing_score(self, text: str) -> float:
        """Calculate testing score (0-5) - lenient for FSEC."""
        text_lower = text.lower()

        # Award points if ANY testing keywords present
        has_test_mention = any(kw in text_lower for kw in self.TEST_KEYWORDS)

        # Or if description is substantial (implies thought about verification)
        if has_test_mention or 'verify' in text_lower:
            return 5.0

        # FSEC often handles testing in PR review, so only deduct 2 points
        return 3.0


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


def format_report(report: ReadinessReport, verbose: bool = False) -> str:
    """Format readiness report as human-readable text."""
    lines = []

    # Header
    lines.append(f"\n{'='*80}")
    lines.append(f"FSEC Readiness Analysis: {report.issue_key}")
    lines.append(f"{'='*80}")
    lines.append(f"Summary: {report.summary}")
    lines.append(f"Type: {report.issue_type} | Status: {report.status}")
    lines.append("")

    # Score
    score_emoji = "✅" if report.total_score >= 80 else "⚠️" if report.total_score >= 60 else "❌"
    lines.append(f"📊 FSEC Readiness Score: {report.total_score:.1f}/100 {score_emoji}")
    lines.append(f"   Requirements: {report.requirements_score:.1f}/40 (problem, outcome, clarity)")
    lines.append(f"   Technical:    {report.technical_score:.1f}/40 (AWS context, implementation, refs)")
    lines.append(f"   Context:      {report.context_score:.1f}/15 (links, security)")
    lines.append(f"   Testing:      {report.testing_score:.1f}/5  (verification approach)")
    lines.append("")

    if report.total_score >= 80:
        lines.append("✅ EXCELLENT - Ready for pointing")
    elif report.total_score >= 60:
        lines.append("⚠️  GOOD ENOUGH - Ready for pointing (FSEC threshold)")
    elif report.total_score >= 45:
        lines.append("❌ NEEDS WORK - Address gaps before pointing")
    else:
        lines.append("❌ NOT READY - Significant gaps to address")
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

            if verbose and gap.actions:
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
        lines.append("   This ticket meets FSEC's baseline for pointing.")
        if report.total_score < 80:
            lines.append("   Consider addressing gaps for even better clarity.")
    else:
        high_gaps = [g for g in report.gaps if g.severity == 'HIGH']
        if high_gaps:
            lines.append("   Address these gaps before pointing:")
            for gap in high_gaps[:3]:
                lines.append(f"   • {gap.title}")
                if gap.actions:
                    lines.append(f"     → {gap.actions[0]}")

    lines.append("")
    lines.append(f"Note: Using FSEC-specific scoring (60+ = ready vs. standard 75+)")
    lines.append(f"{'='*80}\n")

    return "\n".join(lines)


@click.command()
@click.argument('issue_key')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed actions for each gap')
@click.option('--json-output', '--json', is_flag=True, help='Output as JSON')
def main(issue_key: str, verbose: bool, json_output: bool):
    """Analyze a Jira ticket using FSEC-specific readiness criteria."""
    try:
        client = get_jira_client()
        analyzer = FSECReadinessAnalyzer(client)

        click.echo(f"Analyzing {issue_key} (FSEC mode)...", err=True)
        report = analyzer.analyze(issue_key)

        if json_output:
            output = {
                'issue_key': report.issue_key,
                'summary': report.summary,
                'issue_type': report.issue_type,
                'status': report.status,
                'mode': report.mode,
                'scores': {
                    'requirements': report.requirements_score,
                    'technical': report.technical_score,
                    'context': report.context_score,
                    'testing': report.testing_score,
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
            click.echo(format_report(report, verbose=verbose))

        # Exit code: 0 if ready, 1 if not ready
        sys.exit(0 if report.ready_for_pointing else 1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
