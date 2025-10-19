# PR Creator Example Workflows

This document provides detailed examples of how the pr-creator skill works in different scenarios.

## Example 1: Feature PR with Full Template

**Scenario**: User has implemented a new feature with a comprehensive PR template

### Initial Request
```
User: Create a PR for my changes
```

### Discovery Phase
```
Assistant: Searching for PR templates...
Found: .github/PULL_REQUEST_TEMPLATE.md
```

### Analysis Phase
```
Assistant: Analyzing your branch changes...

Branch: feature/user-profile-api
Base: main
Commits: 5
Files changed: 8 (3 new, 5 modified)

Commits:
1. feat(api): add user profile endpoint
2. feat(api): add profile validation
3. test(api): add profile endpoint tests
4. docs(api): document profile endpoints
5. chore(api): update OpenAPI spec

Files changed:
+ src/api/routes/profile.js
+ src/api/validators/profile.js
+ tests/api/profile.test.js
~ docs/api.md
~ openapi.yaml
~ package.json
~ src/api/index.js
~ README.md
```

### Inference and Gap Detection
```
Assistant: I found your PR template and analyzed your branch. Here's what I gathered:

✓ Title: feat: Add user profile API endpoints
✓ Type: New feature
✓ Related Issue: Closes #142 (from commits)
✓ Files changed: 8 files (3 new, 5 modified)
✓ Tests: ✓ Added (detected test file changes)
✓ Documentation: ✓ Updated (detected .md changes)
✓ Breaking changes: None detected

Your template requires a few more details:

1. **Why are we making this change?** [Required]
   I see you're adding profile endpoints - what's the business need?

2. **How should reviewers manually test this?** [Required]
   I can see unit tests, but are there manual testing steps?
```

### User Provides Missing Info
```
User: This enables the mobile app to fetch user profiles.
Reviewers can test by calling GET /api/v1/users/:id with a valid user ID.
```

### PR Generation
```
Assistant: Perfect! Creating PR...

Title: feat: Add user profile API endpoints

Body:
## Summary
Add new API endpoints for user profile management to support mobile app requirements.

## Motivation
This enables the mobile app to fetch user profiles efficiently. Previously, profile data had to be assembled from multiple endpoints, causing performance issues.

## Changes
- New GET /api/v1/users/:id endpoint for fetching user profiles
- Profile data validation using Joi schemas
- Comprehensive test coverage with 95%+ code coverage
- OpenAPI specification updated
- API documentation updated

## Type of Change
- [x] New feature (non-breaking)
- [ ] Bug fix (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #142

## Testing
### Unit Tests
- [x] Added comprehensive tests (tests/api/profile.test.js)
- [x] All tests pass locally

### Manual Testing
Reviewers can test by calling:
```bash
curl http://localhost:3000/api/v1/users/:id
```
Replace `:id` with a valid user ID.

## Checklist
- [x] Code follows style guidelines
- [x] Self-reviewed
- [x] Documentation updated
- [x] Tests added
- [x] All tests pass

---
**Commits in this PR:**
- feat(api): add user profile endpoint
- feat(api): add profile validation
- test(api): add profile endpoint tests
- docs(api): document profile endpoints
- chore(api): update OpenAPI spec

Created: https://github.com/user/repo/pull/143
```

---

## Example 2: Bug Fix with Minimal Template

**Scenario**: Hotfix for production bug, minimal template

### Initial Request
```
User: /pr
```

### Discovery
```
Assistant: Found: PULL_REQUEST.md (simple template)

Template structure:
- Summary [Required]
- How to test

Analyzing branch: hotfix/memory-leak
```

### Analysis
```
Commits: 2
1. fix(worker): prevent memory leak in job processor
2. test(worker): add memory leak regression test

Files changed:
~ src/worker/processor.js (12 lines changed)
+ tests/worker/memory.test.js (new file)

No related issues found in commits.
```

### Intelligent Prompting
```
Assistant: I see you're fixing a memory leak. Your template needs:

1. **Summary** - I can infer: "Fix memory leak in job processor"
   Use this? (y/n)

User: y
2. **How to test** - Need more details
   I see you added a regression test. Any manual reproduction steps?

User: Run the worker for 1 hour with continuous jobs, monitor memory usage
```

### PR Generation
```
Assistant: Creating PR...

Title: fix: Prevent memory leak in job processor

Body:
## Summary
Fix memory leak in job processor that occurred when processing long-running job queues.

## How to Test
### Automated
Run `npm test -- tests/worker/memory.test.js`

### Manual
Run the worker for 1 hour with continuous jobs and monitor memory usage.
Memory should remain stable instead of growing indefinitely.

Created: https://github.com/user/repo/pull/144
```

---

## Example 3: No Template (Default Structure)

**Scenario**: Repository has no PR template

### Initial Request
```
User: Create a PR
```

### Discovery
```
Assistant: No PR template found. I'll use a sensible default structure.

Analyzing branch: refactor/api-cleanup
```

### Analysis and Auto-Generation
```
Commits: 3
1. refactor(api): extract validation logic
2. refactor(api): simplify error handling
3. docs(api): update comments

Files changed: 6 (all modified, no new files)

Auto-generating PR...

Title: refactor: Extract validation logic and simplify error handling

Body:
## Summary
Refactor API code to improve maintainability by extracting validation logic
into separate modules and simplifying error handling patterns.

## Changes
- Extract validation logic from route handlers to dedicated validators
- Simplify error handling using consistent middleware pattern
- Update code comments for clarity

**Files Changed:**
- src/api/routes/users.js
- src/api/routes/posts.js
- src/api/validators/index.js (modified)
- src/api/middleware/error.js
- docs/api/validation.md
- README.md

## Type of Change
refactor (no functional changes)

## Testing
- [x] All existing tests pass
- [ ] No new tests needed (refactor only)

Created: https://github.com/user/repo/pull/145
```

---

## Example 4: Multiple Templates (User Selects)

**Scenario**: Repository has multiple PR templates

### Initial Request
```
User: /pr
```

### Discovery
```
Assistant: Found multiple PR templates:

1. .github/PULL_REQUEST_TEMPLATE/bug_fix.md
2. .github/PULL_REQUEST_TEMPLATE/feature.md
3. .github/PULL_REQUEST_TEMPLATE/documentation.md
4. .github/PULL_REQUEST_TEMPLATE/hotfix.md

Analyzing your changes...
- 2 commits, all in docs/ directory
- Only .md files changed

Recommendation: Use #3 (documentation.md)

Which template would you like to use? (1-4, or enter for recommendation)
```

### User Selection
```
User: [Enter]