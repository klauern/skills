# Ticket Readiness Criteria

This document defines what makes a ticket "Ready for Pointing" (estimation). These criteria help ensure tickets have enough detail for the team to confidently estimate effort.

## Readiness Checklist

A ticket is ready for pointing when it satisfies these categories:

### 1. Requirements (70% weight)
Must have clear, unambiguous requirements:

- **Problem Statement** ✓
  - What problem are we solving?
  - Who is affected by this problem?
  - What is the current behavior?
  - What is the desired behavior?

- **Acceptance Criteria** ✓
  - Clear, testable conditions for "done"
  - Format: "Given [context], When [action], Then [outcome]"
  - Minimum 2-3 criteria for features, 1 for bugs
  - Edge cases and error conditions specified

- **User Stories** (for features) ✓
  - "As a [user type], I want [goal] so that [benefit]"
  - Answers the "why" not just "what"

### 2. Technical Context (20% weight)
Sufficient technical information to estimate complexity:

- **Technical Approach** ✓
  - High-level approach discussed or open questions identified
  - Major components/services affected listed
  - Database schema changes noted if applicable
  - API changes documented if applicable

- **Dependencies** ✓
  - Dependent tickets linked
  - External service dependencies noted
  - Infrastructure requirements specified
  - Feature flag strategy defined if needed

- **Data Considerations** ✓
  - Data models sketched
  - Migration needs identified
  - Performance requirements noted
  - Scale considerations documented

### 3. Testing Requirements (5% weight)
Clear understanding of how to verify the work:

- **Test Scenarios** ✓
  - Happy path described
  - Error cases identified
  - Boundary conditions noted
  - Test data requirements specified

### 4. Context & Constraints (5% weight)
Important context that affects approach or timeline:

- **Security/Compliance** ✓
  - Security requirements noted if applicable
  - PII handling documented if applicable
  - Compliance requirements identified if applicable

- **Deployment** ✓
  - Rollout strategy discussed if non-standard
  - Rollback considerations noted if risky
  - Monitoring requirements specified

- **Timeline** ✓
  - Deadline context provided if time-sensitive
  - Priority justified

## Scoring System

Calculate a readiness score based on completed items:

```
Requirements: (items checked / 3) * 70 = X points
Technical:    (items checked / 3) * 20 = Y points
Testing:      (items checked / 1) * 5  = Z points
Context:      (items checked / 3) * 5  = W points

Total Score = X + Y + Z + W out of 100
```

**Score Interpretation**:
- **90-100**: Excellent - Ready for pointing
- **75-89**: Good - Minor clarifications needed
- **60-74**: Fair - Some gaps to address
- **< 60**: Not Ready - Significant work needed

**Gap Severity Shorthand**:
- 🔴 HIGH – Cannot estimate confidently until resolved.
- 🟡 MEDIUM – Estimatable with caveats; clarify soon.
- 🔵 LOW – Non-blocking hygiene (tests, polish, documentation).

## Common Red Flags

Indicators that a ticket is NOT ready:

🚩 **Vague Language**:
- "Maybe", "probably", "might", "could"
- "Something like", "similar to"
- "etc.", "and so on"

🚩 **Missing Context**:
- No acceptance criteria
- "TBD" or "TODO" in critical sections
- No links to design docs, diagrams, or related tickets

🚩 **Scope Uncertainty**:
- Description keeps growing in comments
- Multiple features mixed in one ticket
- "Part 1", "Phase 1" without defined phases

🚩 **Technical Unknowns**:
- Multiple competing approaches with no decision
- "We'll figure it out during implementation"
- Major dependencies not identified

🚩 **Stakeholder Disagreement**:
- Comments show conflicting requirements
- No resolution to open questions
- Multiple back-and-forth discussions

## Template: Grooming Session Notes

Use this template when grooming a ticket:

```markdown
## Grooming Session: [TICKET-KEY]
**Date**: YYYY-MM-DD
**Participants**: [names]

### Summary
[1-2 sentence ticket summary]

### Questions Raised
1. [Question] - **Answered**: [answer] or **TODO**: [who needs to answer]

### Decisions Made
1. [Decision and rationale]

### Acceptance Criteria (Agreed)
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

### Technical Notes
- Approach: [high-level approach]
- Components affected: [list]
- Dependencies: [linked tickets]

### Action Items Before Pointing
- [ ] [Action item] - Owner: [name]
- [ ] [Action item] - Owner: [name]

### Readiness Score: X/100
[Brief justification]

**Ready for Pointing**: Yes/No
```

## Examples

### Example 1: Well-Groomed Feature Ticket

```
Title: Add bulk export for security scan results

Description:
Users need to export multiple scan results at once for compliance reporting.

Problem Statement:
Currently users must export scan results one at a time, which takes 10-15
minutes for our largest customers with 100+ scans. This creates friction
during audit season.

Acceptance Criteria:
- Given a user has selected 2+ scans, when they click "Export Selected",
  then all scans are exported in a single ZIP file
- Given a user selects >50 scans, when they click export, then they receive
  an email when the export is ready (async processing)
- Given an export fails, when the user checks the export status, then they
  see a clear error message

Technical Notes:
- Add bulk export endpoint: POST /api/exports/bulk
- Use existing export service, add batch processor
- Store export jobs in Redis, process via Sidekiq
- Return job ID immediately, poll for completion

Dependencies:
- FSEC-1234 (Export service refactor) - DONE
- Infrastructure: Need S3 bucket for temporary exports

Test Scenarios:
- Happy path: Select 10 scans, verify ZIP contents
- Large batch: Select 100 scans, verify async email delivery
- Partial failure: If 1 of 10 scans fails, verify others succeed
- Timeout: Verify 1-hour cleanup of old export files

Security:
- Verify user has permission for ALL selected scans before export
- Signed URLs for download (30-min expiry)

Readiness Score: 95/100 - Excellent
```

### Example 2: Incomplete Ticket (NOT Ready)

```
Title: Fix performance issues

Description:
The dashboard is slow and users are complaining.

🚩 Problems:
- No specific problem statement (which dashboard? how slow?)
- No acceptance criteria (when is it "fixed"?)
- No technical context (what's causing the slowness?)
- No test scenarios
- Vague title and description

Readiness Score: 25/100 - Not Ready
```

## Customization Checklist

Tailor the rubric when a squad has different standards:
1. Adjust the weights if, for example, Technical clarity should count more than Requirements.
2. Append red flags you see frequently (e.g., compliance nuances) so they’re captured in readiness scoring.
3. Document any team-specific grooming gates (design review required, SPIKE completion, etc.).
4. Add anonymized examples from real tickets so reviewers know what “ready” looks like for your product area.
