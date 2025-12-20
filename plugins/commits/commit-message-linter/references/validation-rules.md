# Commit Message Validation Rules

Complete specification of all validation rules applied by the commit-message-linter.

## Rule Categories

### Critical Violations

These violations **must** be fixed (severity: CRITICAL):

1. Missing commit type
2. Invalid commit type
3. Malformed header structure
4. Type not lowercase
5. Missing description

### Errors

These violations **should** be fixed (severity: ERROR):

6. Non-imperative mood in description
7. Description too short (< 10 characters)
8. Header too long (> 100 characters)
9. Invalid scope format
10. Invalid breaking change marker

### Warnings

These are best practice violations (severity: WARNING):

11. Description ends with period
12. Body line exceeds 100 characters
13. Missing blank line between header and body
14. Footer format issues
15. Scope conventions not followed

## Detailed Rule Specifications

### Rule 1: Missing Commit Type

**Check**: Header must start with a valid type

**Valid**:
```text
feat: add new feature
```

**Invalid**:
```text
add new feature
Added new feature
```

**Fix**:
```bash
# Analyze git diff to infer type
# Suggest appropriate type
feat: add new feature
```

**Severity**: CRITICAL

---

### Rule 2: Invalid Commit Type

**Check**: Type must be from allowed list

**Allowed types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Add/update tests
- `build`: Build system or dependencies
- `ci`: CI configuration
- `chore`: Other changes (no production code change)
- `revert`: Revert previous commit

**Valid**:
```text
feat: add login
fix: resolve crash
docs: update README
```

**Invalid**:
```text
feature: add login
bugfix: resolve crash
update: change README
```

**Fix**:
```bash
# Map to correct type
feat: add login (was "feature")
fix: resolve crash (was "bugfix")
docs: update README (was "update")
```

**Severity**: CRITICAL

---

### Rule 3: Malformed Header Structure

**Check**: Header must follow format: `type(scope): description`

**Pattern**: `^(type)(\(scope\))?: (.+)$`

**Valid**:
```text
feat(auth): add login
fix: resolve bug
docs(api): update endpoints
```

**Invalid**:
```text
feat(auth) add login (missing colon)
feat:add login (missing space after colon)
feat (auth): add login (space before scope)
```

**Fix**:
```bash
# Correct formatting
feat(auth): add login
feat: add login
feat(auth): add login
```

**Severity**: CRITICAL

---

### Rule 4: Type Not Lowercase

**Check**: Type must be lowercase

**Valid**:
```text
feat: add feature
fix: resolve bug
```

**Invalid**:
```text
Feat: add feature
FIX: resolve bug
DOCS: update readme
```

**Fix**:
```bash
# Convert to lowercase
feat: add feature
fix: resolve bug
docs: update readme
```

**Severity**: CRITICAL

---

### Rule 5: Missing Description

**Check**: Description must be present after colon

**Valid**:
```text
feat: add login
fix(api): resolve error
```

**Invalid**:
```text
feat:
fix(api):
docs
```

**Fix**:
```bash
# Prompt user for description
feat: [description needed]
# Or analyze changes to suggest
feat: add user authentication
```

**Severity**: CRITICAL

---

### Rule 6: Non-Imperative Mood

**Check**: Description should use imperative mood (command form)

**Valid**:
```text
feat: add login
fix: resolve crash
docs: update README
refactor: extract helper
```

**Invalid**:
```text
feat: added login
fix: resolved crash
docs: updated README
refactor: extracted helper
```

**Common violations**:
- Past tense: added → add
- Gerund: adding → add
- Past participle: has added → add

**Fix**:
```bash
# Convert to imperative
feat: add login (was "added")
fix: resolve crash (was "resolved")
docs: update README (was "updated")
```

**Severity**: ERROR

---

### Rule 7: Description Too Short

**Check**: Description must be at least 10 characters (meaningful)

**Valid**:
```text
feat: add login page
fix: resolve null error
```

**Invalid**:
```text
feat: login
fix: bug
docs: update
```

**Fix**:
```bash
# Request more detail
feat: add login page
fix: resolve null error
docs: update API documentation
```

**Severity**: ERROR

---

### Rule 8: Header Too Long

**Check**: Header (type + scope + description) must be ≤ 100 characters

**Valid**:
```text
feat(auth): add OAuth2 authentication with Google and GitHub providers
```

**Invalid**:
```text
feat(authentication): add OAuth2 authentication support with Google and GitHub providers including token refresh
```

**Fix**:
```bash
# Shorten or move detail to body
feat(auth): add OAuth2 authentication

Support for Google and GitHub providers including token refresh.
```

**Severity**: ERROR

---

### Rule 9: Invalid Scope Format

**Check**: Scope must be lowercase alphanumeric with hyphens

**Pattern**: `^[a-z][a-z0-9-]*$`

**Valid**:
```text
feat(auth): add login
fix(api-client): resolve error
docs(user-guide): update
```

**Invalid**:
```text
feat(Auth): add login
fix(API Client): resolve error
docs(user_guide): update
```

**Fix**:
```bash
# Convert to valid format
feat(auth): add login
fix(api-client): resolve error
docs(user-guide): update
```

**Severity**: ERROR

---

### Rule 10: Invalid Breaking Change Marker

**Check**: Breaking changes must use `!` or `BREAKING CHANGE:` footer

**Valid**:
```text
feat(api)!: change response format

feat(api): change response format

BREAKING CHANGE: Response format changed from array to object.
```

**Invalid**:
```text
feat(api): breaking: change response format

feat(api): BREAKING - change response format
```

**Fix**:
```bash
# Use proper format
feat(api)!: change response format

# Or with footer
feat(api): change response format

BREAKING CHANGE: Response format changed.
```

**Severity**: ERROR

---

### Rule 11: Description Ends with Period

**Check**: Description should not end with period

**Valid**:
```text
feat: add login page
fix: resolve null pointer error
```

**Invalid**:
```text
feat: add login page.
fix: resolve null pointer error.
```

**Fix**:
```bash
# Remove trailing period
feat: add login page
fix: resolve null pointer error
```

**Severity**: WARNING

---

### Rule 12: Body Line Too Long

**Check**: Body lines should be ≤ 100 characters

**Valid**:
```text
feat: add feature

Implement new feature with proper error handling
and validation.
```

**Invalid**:
```text
feat: add feature

Implement new feature with proper error handling and validation that checks all edge cases.
```

**Fix**:
```bash
# Wrap lines
feat: add feature

Implement new feature with proper error handling and validation
that checks all edge cases.
```

**Severity**: WARNING

---

### Rule 13: Missing Blank Line

**Check**: Blank line required between header and body

**Valid**:
```text
feat: add feature

This is the body explaining the feature.
```

**Invalid**:
```text
feat: add feature
This is the body explaining the feature.
```

**Fix**:
```bash
# Add blank line
feat: add feature

This is the body explaining the feature.
```

**Severity**: WARNING

---

### Rule 14: Footer Format Issues

**Check**: Footers must follow format: `Token: value` or `Token #value`

**Valid**:
```text
Fixes: #123
Refs: #456
BREAKING CHANGE: API changed
Co-authored-by: Name <email@example.com>
```

**Invalid**:
```text
Fixes #123 (missing colon)
Refs: 456 (missing #)
Breaking change: API changed (not uppercase)
```

**Fix**:
```bash
# Correct format
Fixes: #123
Refs: #456
BREAKING CHANGE: API changed
```

**Severity**: WARNING

---

### Rule 15: Scope Conventions

**Check**: Scope should follow project conventions

**Project-specific**: Each project may define:
- Allowed scopes (e.g., `auth`, `api`, `ui`)
- Required scopes for certain types
- Scope naming patterns

**Example conventions**:
```text
# Web app
Allowed: auth, api, ui, db, config

# Monorepo
Allowed: backend, frontend, shared, docs

# Library
Allowed: core, utils, types, cli
```

**Valid** (following convention):
```text
feat(auth): add login
fix(api): resolve error
```

**Invalid** (violating convention):
```text
feat(authentication): add login (should be "auth")
fix(backend-api): resolve error (should be "api")
```

**Fix**:
```bash
# Use conventional scope
feat(auth): add login
fix(api): resolve error
```

**Severity**: WARNING

## Validation Algorithm

### Step 1: Parse Header

```text
Input: "feat(scope): description"

Parse into:
- type: "feat"
- scope: "scope"
- breaking: false
- description: "description"
```

### Step 2: Validate Header Components

```text
1. Check type exists → Rule 1
2. Check type is valid → Rule 2
3. Check type is lowercase → Rule 4
4. Check scope format (if present) → Rule 9
5. Check description exists → Rule 5
6. Check description length → Rule 7, 8
7. Check description mood → Rule 6
8. Check description ending → Rule 11
```

### Step 3: Parse Body (if present)

```text
1. Check blank line after header → Rule 13
2. Split into lines
3. Check line lengths → Rule 12
```

### Step 4: Parse Footers (if present)

```text
1. Extract footer tokens
2. Check footer format → Rule 14
3. Check breaking change format → Rule 10
```

### Step 5: Check Conventions

```text
1. Load project scope conventions
2. Validate scope against conventions → Rule 15
```

## Validation Output Format

### Per-Rule Output

```text
{
  "rule": "Rule 6: Non-Imperative Mood",
  "severity": "ERROR",
  "message": "Description should use imperative mood",
  "found": "added login",
  "expected": "add login",
  "location": "header.description",
  "autofix": true,
  "suggestion": "add login"
}
```

### Summary Output

```text
Validation Results:
- CRITICAL: 0
- ERROR: 2
- WARNING: 1

Status: FAILED
```

## Auto-Fix Priority

When auto-fixing, apply fixes in this order:

1. **Format fixes** (safe):
   - Lowercase type
   - Add/fix spacing
   - Remove trailing period
   - Add blank lines

2. **Content fixes** (review recommended):
   - Convert to imperative mood
   - Shorten description
   - Format breaking changes

3. **Scope fixes** (user approval required):
   - Suggest missing scope
   - Correct scope format

4. **Type fixes** (user approval required):
   - Suggest correct type based on changes

## Configuration

### Customizable Rules

Projects can configure:

```json
{
  "rules": {
    "type-enum": ["feat", "fix", "docs", "custom"],
    "scope-enum": ["auth", "api", "ui"],
    "scope-required": false,
    "header-max-length": 100,
    "body-max-line-length": 100,
    "imperative-mood": true
  }
}
```

### Severity Overrides

```json
{
  "severity": {
    "imperative-mood": "WARNING",
    "description-min-length": "ERROR"
  }
}
```

## Testing Validation

### Test Cases

```bash
# Should pass
feat: add login
fix(api): resolve null error
docs: update README
refactor(auth): extract validators

# Should fail - critical
add login (missing type)
feature: add login (invalid type)
FEAT: add login (not lowercase)

# Should fail - error
feat: added login (past tense)
feat: fix (too short)
feat(Auth): add login (invalid scope)

# Should fail - warning
feat: add login. (trailing period)
```

## Summary

### Validation Checklist

- [ ] Type exists and is valid
- [ ] Type is lowercase
- [ ] Scope format is valid (if present)
- [ ] Description exists and is meaningful
- [ ] Description uses imperative mood
- [ ] Header length ≤ 100 chars
- [ ] Body has blank line after header
- [ ] Body lines ≤ 100 chars
- [ ] Breaking changes properly marked
- [ ] Footers properly formatted
- [ ] Scope follows conventions

### Exit Codes

- **0**: All checks passed
- **1**: Warnings only
- **2**: Errors found
- **3**: Critical violations found
