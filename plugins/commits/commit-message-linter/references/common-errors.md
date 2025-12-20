# Common Commit Message Errors

Frequent violations and their fixes, organized by frequency and impact.

## Most Common Errors

### 1. Past Tense Instead of Imperative

**Frequency**: Very Common (40% of violations)

**Problem**: Using past tense instead of imperative mood

**Examples**:
```text
❌ feat: added user login
❌ fix: resolved crash on startup
❌ docs: updated installation guide
❌ refactor: extracted validation logic
```

**Correct**:
```text
✅ feat: add user login
✅ fix: resolve crash on startup
✅ docs: update installation guide
✅ refactor: extract validation logic
```

**Why it matters**: Conventional commits describe what the commit *does* when applied, not what was done.

**Quick fix**: Remove `-ed`, `-d` suffix:
- added → add
- resolved → resolve
- updated → update
- extracted → extract

---

### 2. Missing Type

**Frequency**: Very Common (30% of violations)

**Problem**: Commit message doesn't start with a type

**Examples**:
```text
❌ Add user authentication
❌ Fixed bug in login
❌ Update README with examples
```

**Correct**:
```text
✅ feat: add user authentication
✅ fix: resolve bug in login
✅ docs: update README with examples
```

**Why it matters**: Type categorizes the change for changelogs and semantic versioning.

**Quick fix**: Analyze the change and prepend appropriate type:
- New feature → `feat:`
- Bug fix → `fix:`
- Documentation → `docs:`
- Refactoring → `refactor:`

---

### 3. Wrong Type

**Frequency**: Common (15% of violations)

**Problem**: Using non-standard type names

**Examples**:
```text
❌ feature: add login
❌ bugfix: resolve crash
❌ update: change API
❌ new: add dashboard
```

**Correct**:
```text
✅ feat: add login
✅ fix: resolve crash
✅ feat: change API (or refactor: if no new functionality)
✅ feat: add dashboard
```

**Common mappings**:
- feature → feat
- bugfix/bug → fix
- update → feat/fix/refactor (depends on change)
- new → feat
- change → refactor
- improve → perf/refactor

**Why it matters**: Tooling expects standard types for automation.

---

### 4. Uppercase Type

**Frequency**: Common (10% of violations)

**Problem**: Type not in lowercase

**Examples**:
```text
❌ Feat: add login
❌ FIX: resolve error
❌ DOCS: update readme
```

**Correct**:
```text
✅ feat: add login
✅ fix: resolve error
✅ docs: update readme
```

**Why it matters**: Specification requires lowercase types.

**Quick fix**: Convert type to lowercase.

---

### 5. Vague Description

**Frequency**: Common (10% of violations)

**Problem**: Description too short or unclear

**Examples**:
```text
❌ feat: login
❌ fix: bug
❌ docs: update
❌ refactor: code
```

**Correct**:
```text
✅ feat: add OAuth login page
✅ fix: resolve null pointer in auth
✅ docs: update API authentication guide
✅ refactor: extract validation helpers
```

**Why it matters**: Description should be meaningful without reading the code.

**Quick fix**: Add specifics:
- What was added/changed?
- Where was it changed?
- Why was it changed? (if not obvious)

---

### 6. Description with Period

**Frequency**: Moderate (8% of violations)

**Problem**: Description ends with period

**Examples**:
```text
❌ feat: add user login.
❌ fix: resolve crash on startup.
```

**Correct**:
```text
✅ feat: add user login
✅ fix: resolve crash on startup
```

**Why it matters**: Convention is no period in header.

**Quick fix**: Remove trailing period.

---

### 7. Invalid Scope Format

**Frequency**: Moderate (5% of violations)

**Problem**: Scope not lowercase or contains spaces

**Examples**:
```text
❌ feat(Auth): add login
❌ fix(API Client): resolve error
❌ docs(User Guide): update
❌ refactor(front_end): extract component
```

**Correct**:
```text
✅ feat(auth): add login
✅ fix(api-client): resolve error
✅ docs(user-guide): update
✅ refactor(frontend): extract component
```

**Why it matters**: Scope should be machine-readable identifier.

**Quick fix**:
- Lowercase the scope
- Replace spaces/underscores with hyphens
- Use short, conventional names

---

### 8. Missing Space After Colon

**Frequency**: Moderate (4% of violations)

**Problem**: No space between colon and description

**Examples**:
```text
❌ feat:add login
❌ fix(api):resolve error
```

**Correct**:
```text
✅ feat: add login
✅ fix(api): resolve error
```

**Why it matters**: Readability and parser compatibility.

**Quick fix**: Add single space after colon.

---

### 9. Using Gerund (-ing)

**Frequency**: Less Common (3% of violations)

**Problem**: Using gerund form instead of imperative

**Examples**:
```text
❌ feat: adding user login
❌ fix: resolving crash
❌ refactor: extracting helpers
```

**Correct**:
```text
✅ feat: add user login
✅ fix: resolve crash
✅ refactor: extract helpers
```

**Why it matters**: Imperative mood is the standard.

**Quick fix**: Remove `-ing` suffix and use base form.

---

### 10. Header Too Long

**Frequency**: Less Common (2% of violations)

**Problem**: Header exceeds 100 characters

**Examples**:
```text
❌ feat(auth): add OAuth2 authentication support with Google and GitHub providers including automatic token refresh
```

**Correct**:
```text
✅ feat(auth): add OAuth2 authentication with Google and GitHub

Include automatic token refresh and provider management.
```

**Why it matters**: Long headers are hard to scan in git log.

**Quick fix**: Move details to body, keep header concise.

---

## Breaking Change Errors

### 11. Informal Breaking Change Marker

**Frequency**: Moderate (6% of violations)

**Problem**: Breaking change not properly marked

**Examples**:
```text
❌ feat(api): breaking: change response format
❌ feat(api): BREAKING - change response format
❌ feat(api): change response format (breaking change)
```

**Correct**:
```text
✅ feat(api)!: change response format

✅ feat(api): change response format

BREAKING CHANGE: Response format changed from array to object.
```

**Why it matters**: Tooling expects specific breaking change format.

**Quick fix**: Use `!` after type/scope OR add `BREAKING CHANGE:` footer.

---

### 12. Missing Breaking Change Explanation

**Frequency**: Moderate (4% of violations)

**Problem**: Breaking change marker without explanation

**Examples**:
```text
❌ feat(api)!: change response format
```

**Correct**:
```text
✅ feat(api)!: change response format

BREAKING CHANGE: Response format changed from array to nested object.
Migration: Update client code to access data.items instead of data.
```

**Why it matters**: Users need to know what broke and how to migrate.

**Quick fix**: Add `BREAKING CHANGE:` footer with details.

---

## Body and Footer Errors

### 13. No Blank Line Before Body

**Frequency**: Less Common (3% of violations)

**Problem**: Body starts immediately after header

**Examples**:
```text
❌ feat: add login
This implements OAuth2 login with Google.
```

**Correct**:
```text
✅ feat: add login

This implements OAuth2 login with Google.
```

**Why it matters**: Parsers expect blank line separator.

**Quick fix**: Add blank line after header.

---

### 14. Body Lines Too Long

**Frequency**: Less Common (2% of violations)

**Problem**: Body lines exceed 100 characters

**Examples**:
```text
❌ feat: add feature

This implements a new feature with extensive capabilities including validation, error handling, and comprehensive logging.
```

**Correct**:
```text
✅ feat: add feature

This implements a new feature with extensive capabilities including
validation, error handling, and comprehensive logging.
```

**Why it matters**: Line wrapping makes diffs and logs more readable.

**Quick fix**: Wrap lines at 72-100 characters.

---

### 15. Invalid Footer Format

**Frequency**: Less Common (2% of violations)

**Problem**: Footers don't follow `Token: value` format

**Examples**:
```text
❌ Fixes #123 (missing colon)
❌ Refs: 456 (missing #)
❌ Breaking change: API changed (should be uppercase)
```

**Correct**:
```text
✅ Fixes: #123
✅ Refs: #456
✅ BREAKING CHANGE: API changed
```

**Why it matters**: Tooling parses footers for automation.

**Quick fix**: Use `Token: value` or `Token #value` format.

---

## Type Selection Errors

### Feat vs Fix

**Problem**: Unclear when to use `feat` vs `fix`

**Guideline**:
```text
feat: Adds new functionality
fix: Corrects existing functionality

✅ feat: add password reset
❌ feat: fix password reset (should be fix)

✅ fix: resolve login crash
❌ fix: add error handling to login (should be feat if adding new capability)
```

### Refactor vs Feat

**Problem**: Unclear when code changes add features vs refactor

**Guideline**:
```text
refactor: Changes code structure without adding features
feat: Adds new user-facing functionality

✅ refactor: extract validation helpers
❌ refactor: add validation (should be feat)

✅ feat: add validation
❌ feat: reorganize validation code (should be refactor)
```

### Docs vs Feat

**Problem**: Unclear when documentation is separate

**Guideline**:
```text
docs: Only documentation changes
feat: Code + docs together

✅ docs: update API guide (only .md files)
❌ docs: add API endpoint and docs (should be feat + separate docs commit)
```

### Chore vs Other Types

**Problem**: Overusing `chore`

**Guideline**:
```text
chore: Changes that don't affect production code
build: Dependencies, build tools
ci: CI configuration
test: Test changes

✅ build: update webpack to v5
❌ chore: update webpack (should be build)

✅ ci: add GitHub Actions workflow
❌ chore: add CI (should be ci)

✅ test: add validation tests
❌ chore: add tests (should be test)
```

---

## Scope Errors

### Too Broad

**Problem**: Scope too generic

**Examples**:
```text
❌ feat(app): add feature
❌ fix(code): resolve bug
❌ docs(files): update docs
```

**Better**:
```text
✅ feat(auth): add login
✅ fix(api): resolve null error
✅ docs(installation): update setup guide
```

### Too Narrow

**Problem**: Scope too specific

**Examples**:
```text
❌ feat(login-button): add click handler
❌ fix(user-service-validator): fix regex
```

**Better**:
```text
✅ feat(auth): add login button click handler
✅ fix(user): correct email validation regex
```

### Inconsistent Naming

**Problem**: Same scope named differently

**Examples**:
```text
❌ Inconsistent:
feat(auth): add login
fix(authentication): resolve error
docs(user-auth): update guide
```

**Correct**:
```text
✅ Consistent:
feat(auth): add login
fix(auth): resolve error
docs(auth): update guide
```

---

## Real-World Examples

### Example 1: Multiple Violations

**Before**:
```text
❌ Feature: Added new login page.
```

**Violations**:
1. Invalid type ("Feature" should be "feat")
2. Uppercase type
3. Past tense ("Added" should be "add")
4. Ends with period

**After**:
```text
✅ feat(auth): add login page
```

---

### Example 2: Vague and Incomplete

**Before**:
```text
❌ fix: bug
```

**Violations**:
1. Too vague ("bug" doesn't describe what was fixed)
2. Too short (< 10 characters)

**After**:
```text
✅ fix(auth): resolve null pointer in token validation
```

---

### Example 3: Wrong Format

**Before**:
```text
❌ Updated README with new installation instructions
```

**Violations**:
1. Missing type
2. Past tense ("Updated" should be "update")

**After**:
```text
✅ docs(installation): update README with new instructions
```

---

### Example 4: Breaking Change

**Before**:
```text
❌ feat(api): change response format (BREAKING)
```

**Violations**:
1. Informal breaking change marker
2. Missing breaking change explanation

**After**:
```text
✅ feat(api)!: change response format

BREAKING CHANGE: Response format changed from array to nested object
with metadata. Update client code to access data.items instead of data.
```

---

## Quick Reference

### Common Fixes

| Violation | Fix |
|-----------|-----|
| `added` | `add` |
| `fixed` | `fix` |
| `updated` | `update` |
| `Feature:` | `feat:` |
| `bugfix:` | `fix:` |
| `Feat:` | `feat:` |
| `feat:login` | `feat: login` |
| `feat(Auth):` | `feat(auth):` |
| `feat: login.` | `feat: login` |
| `feat: fix` | Too vague, expand |

### Type Selection

| Change | Type |
|--------|------|
| New feature | `feat` |
| Bug fix | `fix` |
| Documentation | `docs` |
| Refactoring | `refactor` |
| Performance | `perf` |
| Tests | `test` |
| Build/deps | `build` |
| CI config | `ci` |
| Other | `chore` |

### Mood Conversion

| Wrong | Right |
|-------|-------|
| added | add |
| adding | add |
| has added | add |
| fixed | fix |
| fixing | fix |
| updated | update |
| updating | update |

## Prevention Tips

1. **Use commit templates** with format reminders
2. **Set up pre-commit hooks** to validate before commit
3. **Review examples** before committing
4. **Install editor plugins** that lint commit messages
5. **Practice** until it becomes natural

## Summary

**Most frequent errors** (fix these first):
1. Past tense instead of imperative (40%)
2. Missing type (30%)
3. Wrong type name (15%)

**Quick wins**:
- Remove `-ed` from verbs
- Prepend type if missing
- Lowercase the type
- Remove trailing periods

**For complex messages**:
- Check scope format
- Verify breaking change markers
- Add body for explanation
- Include footers for references
