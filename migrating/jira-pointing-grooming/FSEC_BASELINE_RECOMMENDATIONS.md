# FSEC Baseline Recommendations

## Executive Summary

**Problem**: The standard readiness analyzer scored successfully completed FSEC tickets at 24-62/100, yet these tickets were estimated and delivered successfully.

**Root Cause**: The analyzer was optimized for formal product management practices (Acceptance Criteria, Given/When/Then, explicit test scenarios), but FSEC uses a pragmatic, technically-focused style.

**Solution**: Created FSEC-specific analyzer (`analyze_readiness_fsec.py`) with adjusted scoring that recognizes FSEC's actual working patterns.

## Scoring Comparison: Standard vs. FSEC

| Ticket | Standard Score | FSEC Score | Notes |
|--------|---------------|------------|-------|
| FSEC-9793 | 24/100 ❌ | 88/100 ✅ | Lambda migration - clear problem/solution |
| FSEC-9757 | 62/100 ❌ | 90/100 ✅ | API Gateway - technical specification |
| FSEC-9870 | 62/100 ❌ | 98/100 ✅ | SCP tool - concise with GitHub link |
| FSEC-9877 | N/A | 98/100 ✅ | Org policy - Slack request + solution |

**Result**: Successfully completed tickets now score 88-98/100, accurately reflecting their quality.

## New Scoring Model

### Score Distribution (Total: 100 points)

| Category | Standard | FSEC | Reasoning |
|----------|----------|------|-----------|
| **Requirements** | 70 points | 40 points | FSEC uses implicit acceptance criteria |
| **Technical** | 20 points | 40 points | Core of every FSEC ticket (AWS, systems) |
| **Context** | 5 points | 15 points | Links to code/Slack highly valued |
| **Testing** | 5 points | 5 points | Same (handled in PR review) |

### Ready-for-Pointing Threshold

- **Standard**: 75+ points
- **FSEC**: 60+ points (recognizes pragmatic approach)

## What FSEC Tickets Must Have (60+ points)

### Requirements (40 points)
1. **Clear problem or request** (15 pts)
   - What needs to change
   - Why it's needed
   - Can be from Slack, technical analysis, or customer request

2. **Specific outcome** (15 pts)
   - What will exist after this work
   - Can be implicit in technical specification

3. **No critical ambiguities** (10 pts)
   - No "TBD", "TODO", "???"
   - Technical options ("could use X or Y") are acceptable

### Technical Context (40 points)
1. **AWS/Infrastructure context** (15 pts)
   - AWS accounts, services, resources
   - Modules, repos, or config affected

2. **Implementation approach** (15 pts)
   - What to create/modify/configure
   - High-level technical plan

3. **References** (10 pts)
   - Links to code (GitHub)
   - Links to discussions (Slack)
   - Related Jira tickets

### Context & Links (15 points)
1. **References** (10 pts)
   - Code links, Slack threads, docs

2. **Security context** (5 pts)
   - Only if IAM/policies/auth involved

### Testing (5 points)
- Verification approach mentioned
- Or substantial description (implies testing thought through)

## FSEC Ticket Patterns (From Real Examples)

### Pattern 1: Problem → Technical Solution (Most Common)

```markdown
## Problem
The firehose_to_s3 module uses account-specific KMS keys that can't
be shared between foundation-secure and zendesk-logs accounts.

## Solution
Move the GCP-to-S3 lambdas from foundation-secure to zendesk-logs.

This simplifies the pipeline and enables easier log management offboarding
without granting foundation-secure account access.

**Components**: firehose_to_s3 module, AWS Lambda, KMS
**Accounts**: foundation-secure → zendesk-logs
```

**FSEC Score**: 88/100 ✅

### Pattern 2: Technical Specification

```markdown
## API Gateway for Account Provisioning

Create HTTP endpoint in API Gateway (aft-management account):
- Accepts POST requests
- Idempotently inserts into account-requests DDB table
- Input: customer_id (required) + tenant_id (optional)
- Output: account_id or status value
- Backend: Lambda/Step Function
```

**FSEC Score**: 90/100 ✅

### Pattern 3: Customer Request + FSEC Response

```markdown
## Request (from #ask-chops)
Redirect Cloud Custodian key rotation alerts from #chops-pd to #ask-chops
[Slack link: example alerts]

## Analysis
The slack_notifier currently prioritizes alert channel over default channel:
https://github.com/zendesk/cloud-custodian-deployment/.../custodian.py#L170-L172

## Solution
Add override for chat-ops team to choose default channel over alert channel
```

**FSEC Score**: 98/100 ✅

### Pattern 4: Tool Integration

```markdown
## Minimize SCP Policies

AWS open-sourced a tool specifically for minimizing SCP statements using
wildcards and optimization techniques.

Update our AWS Orgs policies workflow to leverage this tool and roll out
optimized policy changes.

Reference: https://github.com/aws-samples/service-control-policy-preprocessor
```

**FSEC Score**: 98/100 ✅

## FSEC Ticket Template

```markdown
## Problem / Request
[What needs to change - can be from Slack, technical issue, or customer request]

## Current State (if applicable)
[How it works now, what's broken, or why this is needed]

## Solution
[What we're going to do - technical specification is fine]

### Technical Details
- **Components/Services**: [AWS services, repos, modules]
- **Accounts/Location**: [Where this lives or will be deployed]
- **Approach**: [High-level implementation plan]

### References
- [GitHub: link to relevant code/repo]
- [Slack: link to discussion thread]
- [Related: FSEC-XXXX]

### Security/Compliance (if applicable)
[IAM changes, policy updates, permission grants]

## Verification
[How we'll know this works - can be brief like "deploy and verify" or specific test scenarios]
```

## Usage Guide

### For FSEC Team Members

**Before pointing a ticket:**
```bash
uv run scripts/analyze_readiness_fsec.py FSEC-1234
```

**Score interpretation:**
- **80-100**: Excellent - point with confidence
- **60-79**: Good enough - ready for pointing (FSEC baseline)
- **45-59**: Needs work - address gaps first
- **< 45**: Not ready - significant information missing

**Quick fixes to reach 60+:**
1. Add problem statement (what/why) → +15 pts
2. List AWS accounts/services affected → +15 pts
3. Describe what to build/modify → +15 pts
4. Add GitHub or Slack link → +10 pts

### For Analyzing Old Tickets

**Find oldest unestimated tickets:**
```bash
uv run scripts/find_grooming_candidates.py \
  --unestimated \
  --jql "project = FSEC AND status IN (Backlog, 'To Do') AND 'Story Points' IS EMPTY ORDER BY created ASC" \
  --limit 20
```

**Analyze with FSEC scoring:**
```bash
uv run scripts/analyze_readiness_fsec.py FSEC-1234 --verbose
```

### For Grooming Sessions

1. **Triage first** (for tickets > 2 years old):
   - Close if obsolete or already done
   - Update if still relevant

2. **Analyze readiness**:
   ```bash
   uv run scripts/analyze_readiness_fsec.py FSEC-1234
   ```

3. **Address HIGH severity gaps**:
   - Add problem statement
   - Remove "TBD" / "TODO"
   - Add AWS context

4. **Verify 60+ score**:
   - Re-run analyzer
   - Ready for pointing when 60+

## Recommendations

### Immediate Actions

1. ✅ **Use FSEC analyzer for grooming**: `analyze_readiness_fsec.py`
2. ✅ **Set baseline at 60+**: Not 75+ (too strict for FSEC style)
3. ✅ **Focus on technical context**: AWS accounts, services, implementation approach
4. ✅ **Value code/Slack links**: Quick 10-point boost

### Process Changes

1. **Update grooming checklist**:
   - Replace "Has formal AC" with "Clear problem and solution"
   - Add "AWS context specified" as requirement
   - Add "Links to code/Slack" as quality indicator

2. **Ticket templates**:
   - Create FSEC template (see above)
   - Add to Jira ticket creation screen
   - Include prompts for AWS context

3. **Grooming sessions**:
   - Run FSEC analyzer before session
   - Focus on 45-59 score tickets (close to ready)
   - Use analyzer output to guide discussion

### Long-term Improvements

1. **Customize gap patterns**: Add FSEC-specific red flags
   - "Affects multiple AWS accounts but none listed"
   - "IAM/policy change without security note"
   - "Lambda/API change without account specified"

2. **Dashboard**: Track average scores over time
   - Target: 80% of estimated tickets scored 60+ before grooming
   - Measure: Time from ticket creation to "ready for pointing"

3. **Feedback loop**: Monthly review
   - Which gaps actually blocked estimation?
   - Which "ready" tickets needed clarification anyway?
   - Adjust scoring weights based on reality

## FAQ

### Q: Why not just use formal Acceptance Criteria?
**A**: FSEC's working style is pragmatic and technically focused. Forcing formal AC adds ceremony without value when technical specifications are clearer.

### Q: Won't lower standards (60 vs 75) lead to worse tickets?
**A**: No - we're measuring what FSEC actually values. Completed tickets score 88-98 under FSEC criteria, showing the team already has high standards (just different ones).

### Q: What about test scenarios?
**A**: FSEC handles testing in PR review and has strong code review culture. Documenting test scenarios in tickets adds minimal value.

### Q: Should we abandon the standard analyzer?
**A**: Keep both. Standard is good for product-focused work. FSEC analyzer is calibrated for infrastructure/security engineering.

### Q: How do we handle tickets that score < 45?
**A**: These likely need triage:
- **< 2 months old**: Add context, AWS details, implementation approach
- **> 2 years old**: Close if obsolete, or do major rewrite if still relevant

## Next Steps

1. **Share with FSEC team**: Review patterns and template
2. **Get feedback**: Do these patterns match your experience?
3. **Trial period**: Use FSEC analyzer for 2 weeks
4. **Adjust**: Refine scoring based on what actually helps estimation
5. **Document learnings**: Update this guide with real examples

## Files Created

- `references/fsec_ticket_patterns.md` - Detailed pattern analysis
- `scripts/analyze_readiness_fsec.py` - FSEC-specific analyzer
- `FSEC_BASELINE_RECOMMENDATIONS.md` - This file

## Success Metrics

- **Baseline**: 60+ score = ready for pointing
- **Target**: 80% of tickets reach 60+ before grooming session
- **Excellent**: 80+ score (clear, complete, well-referenced)

Track over time:
- Average score of tickets entering pointing sessions
- % of "ready" tickets that need clarification during planning
- Time from ticket creation to "ready for pointing"
