# Gap Detection Patterns

This document catalogs common gaps found in ungroomed tickets and how to detect them automatically.

**Severity legend**: 🔴 HIGH (blocks estimation), 🟡 MEDIUM (estimation risk), 🔵 LOW (hygiene follow-up).

## Pattern Detection Rules

### 1. Missing Acceptance Criteria

**Detection**:
- Description lacks "acceptance criteria", "AC:", "definition of done", "success criteria"
- No bullet points or numbered lists starting with "Given", "When", "Then"
- No checkboxes in description

**Severity**: HIGH (70% of readiness score)

**Action**:
- Ask product owner to define measurable success criteria
- Use template: "Given [context], When [action], Then [outcome]"
- Document at least 2-3 criteria for features, 1 for bugs

**Example Gap Message**:
```
❌ Missing Acceptance Criteria
No clear definition of "done". What specific, testable conditions must be met?

Suggested Action:
- Schedule 15-min session with PO to define AC
- Use format: Given/When/Then
- Document edge cases and error scenarios
```

---

### 2. Vague or Ambiguous Requirements

**Detection**:
- Description contains: "maybe", "probably", "might", "could", "possibly"
- Contains: "something like", "similar to", "kind of"
- Contains: "etc", "and so on", "...", "and more"
- Contains: "TBD", "TODO", "???", "unclear"
- Contains questions without answers in comments

**Severity**: HIGH

**Action**:
- Identify each ambiguous statement
- Convert to specific questions
- Assign questions to stakeholders for answers

**Example Gap Message**:
```
❌ Vague Requirements
Found ambiguous language: "Users probably want to filter by date"

Specific Questions:
1. Do users need date filtering? (If yes, which date fields?)
2. What date range options? (Today, Last 7 days, Custom range?)
3. Should filters persist across sessions?

Suggested Action: Confirm with product owner or user research
```

---

### 3. No Technical Approach Discussed

**Detection**:
- No technical notes or "Technical Details" section
- No mention of components, services, or systems affected
- No API endpoints, database tables, or data models mentioned
- Ticket is a feature/story type (not a bug)

**Severity**: MEDIUM (20% of readiness score)

**Action**:
- Schedule technical grooming session
- Identify affected components/services
- Sketch high-level approach
- Document major technical decisions needed

**Example Gap Message**:
```
❌ No Technical Context
No discussion of implementation approach.

Questions to Answer:
- Which components/services are affected?
- Are new API endpoints needed?
- Are database schema changes required?
- What's the high-level technical approach?

Suggested Action:
- Tech lead to sketch approach in ticket
- Identify 2-3 possible approaches if unclear
- Note any major technical decisions needed
```

---

### 4. Missing or Unlinked Dependencies

**Detection**:
- Description mentions other tickets but no links
- Contains: "depends on", "blocked by", "requires", "needs"
- Contains: "FSEC-", "PROJ-" without hyperlink
- No "Linked Issues" section populated
- References external systems without context

**Severity**: MEDIUM

**Action**:
- Identify all dependencies mentioned
- Create or link related tickets
- Document external service dependencies
- Clarify which must be completed first

**Example Gap Message**:
```
❌ Missing Dependencies
Description mentions "the new auth system" but no linked ticket.

Questions:
- Which ticket implements "new auth system"?
- Must it be completed before starting this work?
- Are there other dependencies?

Suggested Action:
- Link to FSEC-XXXX (auth system ticket)
- Add "blocked by" relationship if applicable
- Document any external service dependencies
```

---

### 5. No Test Scenarios Defined

**Detection**:
- No section for "Test Scenarios", "Test Cases", "Testing"
- No mention of: "happy path", "edge case", "error handling"
- No discussion of test data needs
- Feature ticket with no testing mentioned

**Severity**: LOW (5% of readiness score)

**Action**:
- Document happy path scenario
- Identify 2-3 edge cases
- Note error conditions to test
- Specify test data requirements

**Example Gap Message**:
```
❌ No Test Scenarios
No discussion of how to verify this works.

Minimum Test Scenarios Needed:
1. Happy path: [what's the main success case?]
2. Edge cases: [what boundary conditions exist?]
3. Error cases: [what can go wrong?]
4. Test data: [what data is needed to test?]

Suggested Action:
- Document at least happy path + 2 edge cases
- Specify error handling requirements
```

---

### 6. Scope Creep in Comments

**Detection**:
- 5+ comments that add new requirements
- Comments contain: "also", "additionally", "we should also"
- Comments that contradict earlier requirements
- Description hasn't been updated but comments expand scope

**Severity**: MEDIUM

**Action**:
- Review all comments for scope changes
- Update description to match current understanding
- Split into multiple tickets if scope too large
- Get stakeholder to confirm final scope

**Example Gap Message**:
```
⚠️ Scope Growing in Comments
Original ticket: "Add export button"
Comments added: CSV format, PDF format, email delivery, scheduling

Suggested Action:
1. Update description with current scope
2. Consider splitting:
   - FSEC-XXX1: Basic export (CSV)
   - FSEC-XXX2: PDF export
   - FSEC-XXX3: Email delivery
3. Get PO to prioritize which ships first
```

---

### 7. Missing Security/Compliance Context

**Detection**:
- Ticket involves PII, authentication, authorization, or sensitive data
- Keywords: "user data", "password", "token", "permission", "admin"
- No security or compliance section
- No mention of: "encryption", "audit log", "access control"

**Severity**: HIGH (for sensitive features)

**Action**:
- Flag for security review
- Document security requirements
- Identify compliance requirements (GDPR, SOC2, etc.)
- Add security acceptance criteria

**Example Gap Message**:
```
🚩 Security Review Needed
This ticket handles user passwords but has no security requirements.

Required Security Context:
- How are passwords hashed? (bcrypt with salt?)
- Are passwords logged anywhere?
- What audit logging is needed?
- Are there rate limits on password attempts?

Suggested Action:
- Schedule security review
- Document security requirements
- Add security-specific acceptance criteria
```

---

### 8. No Definition of Done

**Detection**:
- No checklist of completion items
- No mention of: "documentation", "tests", "deployment", "rollback"
- No discussion of: "monitoring", "alerts", "metrics"

**Severity**: LOW

**Action**:
- Add standard definition of done checklist
- Include: tests, docs, monitoring, rollout plan

**Example Gap Message**:
```
❌ No Definition of Done
What must be completed beyond code?

Standard DoD Checklist:
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Documentation updated
- [ ] Monitoring/alerting configured
- [ ] Rollout plan documented
- [ ] Rollback plan documented

Suggested Action: Add relevant items to ticket
```

---

## Automated Detection Script

See `scripts/analyze_readiness.py` for automated gap detection logic.

The script:
1. Fetches ticket via Jira API
2. Runs all pattern detection rules
3. Calculates readiness score
4. Generates gap report
5. Suggests specific action items

Usage:
```bash
cd ~/.claude/skills/jira-pointing-grooming/scripts
uv run analyze_readiness.py FSEC-1234
```

## Customization Notes

Extend these patterns when new anti-patterns emerge:
1. Document recurring gaps (e.g., feature-flag confusion, partner-team dependencies).
2. Add detection heuristics for each gap—keywords, missing sections, or metadata signals.
3. Assign severities that match your workflow’s tolerance for risk.
4. Capture team-specific vocabulary to improve automated detection accuracy.
