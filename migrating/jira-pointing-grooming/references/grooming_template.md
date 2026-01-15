# Ticket Grooming Template

Use this template when grooming a ticket to ensure all necessary information is captured.

## Quick Grooming Checklist

Copy this checklist into your ticket or grooming notes:

```markdown
## Grooming Checklist

### Requirements ✓
- [ ] Clear problem statement or feature description
- [ ] Acceptance criteria defined (Given/When/Then format)
- [ ] Success metrics or definition of done
- [ ] Edge cases and error conditions documented

### Technical Context ✓
- [ ] High-level approach discussed
- [ ] Affected components/services identified
- [ ] API changes documented (if applicable)
- [ ] Database changes noted (if applicable)
- [ ] Dependencies identified and linked

### Testing ✓
- [ ] Happy path scenario described
- [ ] Edge cases identified
- [ ] Error handling requirements specified
- [ ] Test data requirements noted

### Context ✓
- [ ] Security/compliance requirements noted (if applicable)
- [ ] Deployment considerations discussed (if non-standard)
- [ ] Timeline or priority context provided
- [ ] Related tickets linked

**Readiness Score**: __/100
**Ready for Pointing**: Yes / No
**Next Actions**: [List any remaining work before pointing]
```

---

## Full Grooming Template

For more detailed grooming sessions, use this expanded template:

```markdown
# Grooming Session: [TICKET-KEY]

**Date**: YYYY-MM-DD
**Participants**: [names]
**Duration**: [X minutes]

---

## 1. Summary

[1-2 sentence description of what this ticket is about]

---

## 2. Problem Statement / User Story

### Current Situation
[What is the current state? What problem exists?]

### Desired Outcome
[What should happen after this is implemented?]

### User Story (if applicable)
As a [user type],
I want [goal],
So that [benefit].

---

## 3. Acceptance Criteria

These are the specific, testable conditions that define "done":

### Primary Criteria
- [ ] **Given** [context], **When** [action], **Then** [outcome]
- [ ] **Given** [context], **When** [action], **Then** [outcome]
- [ ] **Given** [context], **When** [action], **Then** [outcome]

### Edge Cases
- [ ] [Edge case scenario]
- [ ] [Edge case scenario]

### Error Conditions
- [ ] [Error handling requirement]
- [ ] [Error handling requirement]

---

## 4. Technical Context

### High-Level Approach
[Brief description of how this will be implemented]

### Components Affected
- [Component/Service 1]
- [Component/Service 2]
- [Component/Service 3]

### API Changes
```
[If applicable, document new or modified endpoints]
POST /api/v1/resource
GET /api/v1/resource/:id
```

### Database Changes
```sql
[If applicable, note schema changes]
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP;
CREATE INDEX idx_users_last_login ON users(last_login_at);
```

### Data Model
```
[If applicable, sketch key data structures]
User {
  id: UUID
  email: String
  last_login_at: Timestamp
}
```

### Dependencies
- **Depends On**: [TICKET-123] - [reason]
- **Blocked By**: [TICKET-456] - [reason]
- **Related To**: [TICKET-789] - [context]
- **External**: [External service/system dependencies]

### Technical Decisions Needed
- [ ] [Decision point 1] - Owner: [name]
- [ ] [Decision point 2] - Owner: [name]

---

## 5. Test Scenarios

### Happy Path
**Scenario**: [Description]
- **Given**: [Initial state]
- **When**: [Action taken]
- **Then**: [Expected result]

### Edge Case 1
**Scenario**: [Description]
- **Given**: [Initial state]
- **When**: [Action taken]
- **Then**: [Expected result]

### Edge Case 2
**Scenario**: [Description]
- **Given**: [Initial state]
- **When**: [Action taken]
- **Then**: [Expected result]

### Error Scenarios
**Scenario**: [What goes wrong]
- **Given**: [Initial state]
- **When**: [Triggering action]
- **Then**: [How system should handle it]

### Test Data Requirements
- [Test data needed]
- [Special setup required]

---

## 6. Security & Compliance

### Security Considerations
- [ ] [Security requirement 1]
- [ ] [Security requirement 2]
- [ ] Authentication/authorization changes
- [ ] PII handling considerations
- [ ] Encryption requirements

### Compliance Requirements
- [ ] GDPR considerations
- [ ] SOC2 requirements
- [ ] Audit logging needs
- [ ] Data retention policies

---

## 7. Deployment & Operations

### Deployment Strategy
- [ ] Standard deployment
- [ ] Feature flag required: [flag name]
- [ ] Phased rollout needed
- [ ] Database migration required

### Rollback Plan
[How to roll back if issues arise]

### Monitoring & Alerting
- **Metrics to track**: [metrics]
- **Alerts to configure**: [alert conditions]
- **Dashboards to update**: [dashboard names]

### Performance Considerations
- Expected load: [volume, frequency]
- Performance requirements: [latency, throughput]
- Scale considerations: [how it scales]

---

## 8. Documentation

### User-Facing Documentation
- [ ] User guide updates needed
- [ ] API documentation updates
- [ ] Release notes

### Internal Documentation
- [ ] Architecture decision record (ADR)
- [ ] Runbook updates
- [ ] Team wiki updates

---

## 9. Questions Raised During Grooming

| # | Question | Assigned To | Answer / Status |
|---|----------|-------------|-----------------|
| 1 | [Question] | [name] | [Answer or "TODO"] |
| 2 | [Question] | [name] | [Answer or "TODO"] |

---

## 10. Action Items Before Pointing

These items must be completed before the ticket is ready for estimation:

- [ ] [Action item 1] - Owner: [name] - Due: [date]
- [ ] [Action item 2] - Owner: [name] - Due: [date]
- [ ] [Action item 3] - Owner: [name] - Due: [date]

---

## 11. Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| [Decision 1] | [Why this choice] | YYYY-MM-DD |
| [Decision 2] | [Why this choice] | YYYY-MM-DD |

---

## 12. Readiness Assessment

### Scoring
- **Requirements**: __/70
- **Technical**: __/20
- **Testing**: __/5
- **Context**: __/5
- **Total Score**: __/100

### Readiness Status
- [ ] **Ready for Pointing** (Score ≥ 75, Requirements ≥ 50)
- [ ] **Needs Minor Work** (Score 60-74)
- [ ] **Not Ready** (Score < 60)

### Next Steps
[What needs to happen next]

---

## 13. Grooming Notes

[Any additional context, discussions, or notes from the grooming session]
```

---

## Tips for Effective Grooming

1. **Be Specific**: Avoid vague language like "maybe", "probably", "etc."
2. **Answer Questions**: Don't leave open questions unanswered
3. **Document Decisions**: Capture why you chose a particular approach
4. **Link Everything**: Related tickets, design docs, diagrams
5. **Think Through Edges**: What can go wrong? What are the boundaries?
6. **Consider Operations**: How will this be deployed, monitored, rolled back?
7. **Involve the Right People**: Dev, QA, Product, Security as needed
8. **Update Regularly**: Keep ticket up to date as understanding evolves

---

## Common Grooming Mistakes to Avoid

❌ **Don't**: Leave acceptance criteria as "works correctly"
✅ **Do**: Define specific, testable conditions

❌ **Don't**: Say "we'll figure out the details during implementation"
✅ **Do**: Make major technical decisions during grooming

❌ **Don't**: Mix multiple features into one ticket
✅ **Do**: Split into focused, estimatable units of work

❌ **Don't**: Ignore dependencies or blockers
✅ **Do**: Identify and link all related work

❌ **Don't**: Skip security or compliance considerations
✅ **Do**: Flag for review early if sensitive

---

## After Grooming

Once grooming is complete:

1. **Update the ticket** with all grooming notes
2. **Add the `ready-for-pointing` label** (or remove `needs-grooming`)
3. **Notify the team** that it's ready for estimation
4. **Schedule pointing session** if part of sprint planning

Remember: The goal is to make the ticket so clear that the team can confidently estimate and implement it.
