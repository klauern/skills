# FSEC Ticket Patterns Analysis

## Executive Summary

Analysis of 30+ completed FSEC tickets from the past 6 months reveals a **significant disconnect between the current readiness scoring system and FSEC's actual working practices**. Completed, successful tickets score 24-62/100 under current criteria, yet were delivered successfully.

**Key Finding**: FSEC uses a pragmatic, technically-focused style rather than formal product management conventions. The scoring system should be adjusted to value what FSEC actually does well.

## FSEC's Real Ticket Patterns

### Pattern 1: Problem → Technical Solution (40% of tickets)

**Example: FSEC-9793 - Migrate GCP to S3 Lambdas**

```
[Problem Description]
The firehose_to_s3 module uses account-specific KMS keys with no
way to share between accounts.

[Technical Analysis]
- Current state: Lambdas in foundation-secure account
- Issue: KMS key isolation
- Options: CMK sharing OR move lambdas

[Solution]
Move lambdas to zendesk-logs account to simplify pipeline and
enable easier offboarding.
```

**What FSEC includes:**
- ✅ Clear problem statement
- ✅ Technical context (accounts, modules, AWS services)
- ✅ Rationale for chosen approach
- ✅ Implementation details

**What FSEC skips:**
- ❌ Formal "Acceptance Criteria" section
- ❌ Given/When/Then format
- ❌ Explicit test scenarios
- ❌ User stories

### Pattern 2: Technical Specification (30% of tickets)

**Example: FSEC-9757 - Account Provisioning API Gateway**

```
Create HTTP endpoint in API Gateway that:
- Accepts POST requests
- Idempotently inserts into account-requests DDB
- Takes customer identifier + optional tenant_identifier
- Returns account ID or status value

Location: aft-management account
Backend: Lambda/Step Function
```

**What FSEC includes:**
- ✅ Specific technical requirements
- ✅ API contract (inputs/outputs)
- ✅ Infrastructure location
- ✅ Implementation components

**What FSEC skips:**
- ❌ User story format
- ❌ Separate AC section
- ❌ Test scenario documentation

### Pattern 3: Customer Request + FSEC Response (30% of tickets)

**Example: FSEC-9916 - Cloud Custodian Slack Channel Override**

```
[Customer Request - from Slack]
Redirect custodian alerts for key rotation from #chops-pd to #ask-chops
[Links to example alerts]

---

[FSEC Analysis]
The CC slack_notifier currently chooses alert channel over default
[Link to code: specific file and line numbers]

[Solution]
Add override for chat-ops team to choose default channel over alert channel
```

**What FSEC includes:**
- ✅ Original request with context
- ✅ Link to requesting Slack thread
- ✅ Technical investigation (code links)
- ✅ Specific implementation action

**What FSEC skips:**
- ❌ Reformatted as formal AC
- ❌ Test scenarios
- ❌ Formal user story

## Why FSEC's Style Works

1. **Team expertise**: Infrastructure team with deep AWS/security knowledge doesn't need basic explanations
2. **Technical focus**: Requirements ARE technical specifications (APIs, accounts, policies)
3. **Implicit testing**: Code review culture catches issues; tests are in PR, not ticket
4. **Slack-driven**: Many tickets originate from Slack requests, preserving original context
5. **Iterative refinement**: Comments add details as needed, rather than upfront perfection

## Current Scorer vs. FSEC Reality

| Criterion | Current Weight | FSEC Actually Values | Adjustment Needed |
|-----------|---------------|---------------------|-------------------|
| **Formal AC** | 25 points (HIGH) | Implicit in technical description | Reduce to 10 pts |
| **No vague language** | 25 points (HIGH) | Uses "could", "might" for options | Be more lenient |
| **Technical context** | 8 points (MEDIUM) | Core of every ticket | Increase to 30 pts |
| **Test scenarios** | 5 points (LOW) | Handled in PR review | Reduce to 2 pts |
| **Problem statement** | Not scored | Always present | Add 20 pts |
| **Code/system links** | Not scored | Highly valued | Add 15 pts |

## FSEC "Good Enough for Pointing" Baseline

Based on actually completed tickets, a ticket is ready for pointing when it has:

### Requirements (40 points) - REDUCED from 70
1. **Clear problem or request** (15 points)
   - What needs to change and why
   - Who requested it or what's broken

2. **Specific outcome** (15 points)
   - Clear description of end state
   - Can be implicit in technical spec

3. **No critical ambiguities** (10 points)
   - Not "we should figure this out"
   - Technical options are OK ("could use X or Y")

### Technical Context (40 points) - INCREASED from 20
1. **Components/systems affected** (15 points)
   - AWS accounts, services, modules
   - Specific repos or code locations

2. **Implementation approach** (15 points)
   - High-level technical plan
   - Links to relevant code/docs

3. **Infrastructure considerations** (10 points)
   - Deployment location
   - Dependencies or integrations

### Context & References (15 points) - INCREASED from 5
1. **Links to code/docs** (10 points)
   - GitHub repos, file references
   - Slack threads, related tickets

2. **Security/compliance notes** (5 points)
   - Only if relevant (IAM, policies, auth)

### Testing (5 points) - SAME
1. **Verification approach** (5 points)
   - Can be implicit ("deploy and verify")
   - Or explicit test scenarios

**New Threshold: 60+/100 = Ready for pointing**

## Recommended Scoring Adjustments

### Modify `analyze_readiness.py`

```python
# Current scoring
def _calculate_requirements_score(self, gaps: List[Gap]) -> float:
    score = 70.0
    score -= high_severity * 25  # Missing AC
    score -= medium_severity * 10
    return max(0, score)

# Proposed FSEC-specific scoring
def _calculate_requirements_score_fsec(self, description: str, gaps: List[Gap]) -> float:
    score = 40.0  # Reduced base

    # Check for problem statement (FSEC always has this)
    has_problem = any(word in description.lower() for word in
                     ['problem', 'issue', 'currently', 'need to', 'should'])
    if not has_problem:
        score -= 15

    # Check for clear outcome
    has_outcome = len(description) > 100  # FSEC writes detailed descriptions
    if not has_outcome:
        score -= 15

    # Penalize only CRITICAL vague language
    critical_gaps = [g for g in gaps if g.category == 'requirements'
                     and 'TBD' in g.description or '???' in g.description]
    score -= len(critical_gaps) * 10  # Reduced penalty

    return max(0, score)

def _calculate_technical_score_fsec(self, description: str, issue: Dict) -> float:
    score = 0  # Start at 0, award points for what's present

    # Award points for technical elements
    has_aws_context = any(word in description.lower() for word in
                         ['account', 'lambda', 's3', 'iam', 'api', 'policy'])
    if has_aws_context:
        score += 15

    has_implementation = any(word in description.lower() for word in
                            ['create', 'update', 'modify', 'deploy', 'configure'])
    if has_implementation:
        score += 15

    has_links = 'github.com' in description or 'slack.com' in description
    if has_links:
        score += 10

    return min(40, score)  # Cap at 40
```

## FSEC-Optimized Ticket Template

```markdown
## Problem / Request
[What needs to change and why - can be copied from Slack]

## Current State
[Brief description of how it works now, if applicable]

## Solution
[What we're going to do - can be technical specification]

### Technical Details
- **Components**: [AWS services, accounts, repos affected]
- **Implementation**: [High-level approach]
- **Location**: [Where this code/config lives]

### References
- [Link to relevant code]
- [Link to Slack discussion]
- [Link to AWS docs or related tickets]

### Security / Compliance
[Only if relevant - IAM, policies, PII, etc.]
```

## Example "Good" FSEC Ticket (Using New Baseline)

### Ticket: Migrate Logging Lambda to Consolidated Account

**Problem**
The firehose_to_s3 module in foundation-secure can't access zendesk-logs
account because KMS keys are account-specific and can't be shared via RAM.

**Solution**
Move GCP-to-S3 lambdas from foundation-secure to zendesk-logs account.

This simplifies the pipeline and makes it easier to delegate log management
without granting foundation-secure access.

**Technical Details**
- Modules: `firehose_to_s3`
- Source account: `foundation-secure`
- Target account: `zendesk-logs`
- Approach: Redeploy lambdas with updated IAM roles

**References**
- Related: FSEC-XXXX (KMS key management)
- Code: github.com/zendesk/aws-infrastructure/tree/main/firehose

**New Score: 75/100 ✅**
- Requirements: 35/40 (clear problem, solution, minor ambiguity on rollback)
- Technical: 35/40 (components, approach, location specified)
- Context: 10/15 (code links present, Slack thread missing)
- Testing: 0/5 (implicit - deploy and verify)

## Next Steps

1. **Create FSEC mode in analyzer**: `--fsec-mode` flag that uses adjusted scoring
2. **Update readiness criteria**: Add `fsec_readiness_criteria.md` with team-specific rubric
3. **Socialize with team**: Share examples of "60+" tickets vs. old "75+" standard
4. **Iterate based on feedback**: Adjust weights based on what team finds useful

## Questions for FSEC Team

1. What's the minimum information YOU need to confidently estimate a ticket?
2. Are test scenarios actually useful in tickets, or is PR review sufficient?
3. Should we track "links to code/Slack" as a quality metric?
4. What makes a ticket too vague to estimate? (Real examples?)
