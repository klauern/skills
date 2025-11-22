# Resolution Strategies Reference

This document provides detailed guidance on how to resolve different types of merge conflicts.

## Strategy Selection Decision Tree

```
Is the conflict identical content?
├─ YES → Keep either version (they're the same)
└─ NO
    │
    Is it only whitespace/formatting?
    ├─ YES → Apply project formatting rules
    └─ NO
        │
        Are both changes non-overlapping additions?
        ├─ YES → Keep both changes
        └─ NO
            │
            Do both changes serve different purposes?
            ├─ YES → Merge both implementations
            └─ NO
                │
                Is one change a bug fix and other a feature?
                ├─ YES → Prioritize bug fix, adapt feature
                └─ NO
                    │
                    Does one supersede the other?
                    ├─ YES → Keep newer/better implementation
                    └─ NO → Manual resolution with expert guidance
```

## Intent Analysis

Before selecting a resolution strategy, analyze the intent of each change:

### Step 1: Extract Commit Messages

```bash
# Get commits from ours
git log --format="%h %s" origin/main..HEAD -- path/to/file

# Get commits from theirs
git log --format="%h %s" origin/main..MERGE_HEAD -- path/to/file
```

### Step 2: Categorize Intent

**Feature Addition**:
- Keywords: "add", "implement", "create", "new"
- New functions, classes, or modules
- Expanded functionality

**Bug Fix**:
- Keywords: "fix", "bug", "resolve", "correct"
- Changes to existing logic
- Often smaller in scope

**Refactoring**:
- Keywords: "refactor", "restructure", "reorganize", "extract"
- Structural changes without behavior change
- Improved code quality

**Performance Optimization**:
- Keywords: "optimize", "improve", "speed up", "cache"
- Algorithm improvements
- Resource usage improvements

**Breaking Change**:
- Keywords: "breaking", "BREAKING", "remove", "deprecate"
- API modifications
- Incompatible changes

**Dependency Update**:
- Version bumps
- Package additions/removals
- Lock file changes

### Step 3: Analyze Code Changes

```python
def analyze_intent(ours_diff, theirs_diff, commits):
    ours_intent = categorize_from_commits(commits.ours)
    theirs_intent = categorize_from_commits(commits.theirs)

    # Analyze code patterns
    if has_new_functions(ours_diff):
        ours_intent.add("feature_addition")

    if fixes_issue(theirs_diff):
        theirs_intent.add("bug_fix")

    return ours_intent, theirs_intent
```

## Resolution Strategies by Conflict Type

### Strategy 1: Auto-Resolve

**When to Use**:
- Simple conflicts with clear, safe resolution
- High confidence in automated outcome
- Changes that don't affect semantics

**Applicable to**:
- Whitespace conflicts
- Import ordering
- Identical changes
- Non-overlapping additions

**Process**:

1. Parse conflict markers
2. Apply resolution algorithm
3. Remove markers and save file
4. Stage resolved file
5. Log resolution for review

**Example Implementation**:

```python
def auto_resolve_whitespace(conflict):
    # Normalize both versions
    normalized = normalize_whitespace(conflict.ours)

    # Apply project formatting
    formatted = apply_formatter(normalized)

    # Replace conflict with resolution
    return formatted
```

**Verification**:
```bash
# Ensure no markers remain
git diff --check

# Show resolution
git diff --cached path/to/file
```

### Strategy 2: Merge Both

**When to Use**:
- Both changes are valuable
- Changes serve different purposes
- No semantic conflicts
- Can be combined safely

**Applicable to**:
- Non-overlapping function additions
- Compatible feature additions
- Complementary changes

**Process**:

1. Identify both changes
2. Determine merge order
3. Combine changes preserving intent
4. Verify no duplicate code
5. Apply consistent formatting

**Example**:

```python
# Conflict:
<<<<<<< HEAD
def calculate_tax(total):
    return total * 0.08
=======
def calculate_discount(total, percent):
    return total * (1 - percent / 100)
>>>>>>> add-discount

# Resolution: Keep both
def calculate_tax(total):
    return total * 0.08

def calculate_discount(total, percent):
    return total * (1 - percent / 100)
```

**Decision Factors**:
- Functions have different names/purposes
- No shared state
- Independent implementations
- Both tested

### Strategy 3: Choose Side (Ours)

**When to Use**:
- Our changes supersede theirs
- Our implementation is more complete
- Our branch contains bug fixes
- Theirs is obsoleted by our work

**Process**:

1. Verify our changes are superior
2. Document why theirs was rejected
3. Check if any parts of theirs should be preserved
4. Keep our version
5. Update related code if needed

**Example**:

```python
# Conflict: Both fixed same bug differently
<<<<<<< HEAD
def parse_date(date_str):
    # Comprehensive fix with error handling
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None
=======
def parse_date(date_str):
    # Simple fix
    return datetime.strptime(date_str, "%Y-%m-%d")
>>>>>>> fix-date-parsing

# Resolution: Choose ours (better error handling)
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None
```

### Strategy 4: Choose Side (Theirs)

**When to Use**:
- Their changes supersede ours
- Their implementation is better
- Their branch contains critical fixes
- Our approach is obsolete

**Process**:

1. Verify their changes are superior
2. Document why ours was rejected
3. Check if any parts of ours should be preserved
4. Keep their version
5. Update related code if needed

**Example**:

```javascript
// Conflict: Both added validation
<<<<<<< HEAD
function validateEmail(email) {
    return /\S+@\S+\.\S+/.test(email);
}
=======
function validateEmail(email) {
    // Using well-tested library
    return emailValidator.validate(email);
}
>>>>>>> use-email-validator

// Resolution: Choose theirs (library is better)
function validateEmail(email) {
    return emailValidator.validate(email);
}
```

### Strategy 5: Refactor to Accommodate Both

**When to Use**:
- Both approaches have merit
- Conflict reveals design issue
- Better abstraction needed
- Long-term benefit justifies effort

**Process**:

1. Analyze both approaches
2. Design abstraction that accommodates both
3. Refactor to new design
4. Update both changes to fit
5. Test thoroughly

**Example**:

```python
# Conflict: Different logging approaches
<<<<<<< HEAD
def process_order(order):
    print(f"Processing order {order.id}")
    # process...
    print(f"Order {order.id} complete")
=======
def process_order(order):
    logger.info(f"Processing order {order.id}")
    # process...
    logger.info(f"Order {order.id} complete")
>>>>>>> add-logging

# Resolution: Refactor to accept logger
def process_order(order, logger=None):
    if logger:
        logger.info(f"Processing order {order.id}")
    # process...
    if logger:
        logger.info(f"Order {order.id} complete")
```

### Strategy 6: Apply Both Sequentially

**When to Use**:
- Both changes modify same code path
- Order matters
- Both are necessary
- Can be applied in sequence

**Process**:

1. Determine correct order
2. Apply first change
3. Apply second change on top
4. Resolve any secondary conflicts
5. Test combined result

**Example**:

```python
# Conflict: Both added validation
<<<<<<< HEAD
def create_user(email, password):
    if len(password) < 8:
        raise ValueError("Password too short")
    # create user...
=======
def create_user(email, password):
    if not is_valid_email(email):
        raise ValueError("Invalid email")
    # create user...
>>>>>>> add-email-validation

# Resolution: Apply both validations
def create_user(email, password):
    if not is_valid_email(email):
        raise ValueError("Invalid email")
    if len(password) < 8:
        raise ValueError("Password too short")
    # create user...
```

### Strategy 7: Manual Resolution with Guidance

**When to Use**:
- Complex logic conflicts
- Domain knowledge required
- Multiple valid approaches
- Risk of breaking semantics

**Process**:

1. Present both versions with context
2. Explain what each version does
3. Identify key differences
4. Explain trade-offs
5. Recommend approach with reasoning
6. Assist with implementation
7. Verify with tests

**Guidance Format**:

```markdown
## Conflict Analysis

**Location**: path/to/file.py:42-58

**Type**: Logic conflict

**Our Changes** (current branch):
- Implements caching for user data
- Reduces database queries
- Adds Redis dependency

**Their Changes** (feature-branch):
- Implements real-time updates
- Uses WebSocket connections
- Ensures data freshness

**Key Differences**:
- Our approach optimizes for performance
- Their approach optimizes for data freshness
- Mutually exclusive optimizations

**Recommendation**:
Combine both approaches with a cache invalidation strategy:
1. Use caching for read-heavy operations
2. Use WebSocket for real-time updates
3. Invalidate cache on WebSocket events

**Implementation**:
[Detailed code suggestion]

**Trade-offs**:
- Slightly more complex
- Requires both Redis and WebSocket
- Best of both worlds for performance and freshness
```

## Priority Rules

When multiple strategies apply, use these priority rules:

### Priority 1: Correctness
- Bug fixes > features
- Working code > broken code
- Complete > incomplete

### Priority 2: Safety
- Conservative > aggressive
- Tested > untested
- Reversible > permanent

### Priority 3: Intent Preservation
- Preserve both intents when possible
- Respect architectural decisions
- Maintain code quality

### Priority 4: Simplicity
- Simple > complex
- Clear > clever
- Maintainable > optimized

### Priority 5: Consistency
- Match project conventions
- Follow established patterns
- Maintain API contracts

## Common Patterns and Anti-Patterns

### ✅ Good Patterns

**Preserve Intent**:
```python
# Both added error handling - combine approaches
try:
    result = process()
except ValueError as e:  # From ours
    logger.error(f"Validation error: {e}")  # From theirs
    raise
```

**Maintain Abstraction**:
```python
# Refactor to accommodate both
def send_notification(user, message, channel='email'):
    if channel == 'email':
        send_email(user, message)  # From ours
    elif channel == 'sms':
        send_sms(user, message)    # From theirs
```

### ❌ Anti-Patterns

**Don't Mix Incompatible Approaches**:
```python
# BAD: Mixing sync and async
def fetch_data():
    return requests.get(url).json()  # Sync from ours
    return await aiohttp.get(url)     # Async from theirs - won't work!
```

**Don't Break Abstraction**:
```python
# BAD: Exposing internals
class User:
    def __init__(self):
        self._cache = {}     # Private from ours
        return self._cache   # Exposed from theirs - breaks encapsulation!
```

**Don't Create Dead Code**:
```python
# BAD: Keeping both alternatives without logic
def calculate(x):
    return x * 2        # From ours
    return x ** 2       # From theirs - unreachable!
```

## Testing After Resolution

After resolving conflicts, verify correctness:

### Step 1: Syntax Check
```bash
# Language-specific syntax check
python -m py_compile file.py
tsc --noEmit file.ts
```

### Step 2: Linting
```bash
# Run project linters
npm run lint
flake8 file.py
```

### Step 3: Unit Tests
```bash
# Run tests for affected code
pytest path/to/test_file.py
npm test -- --findRelatedTests path/to/file.js
```

### Step 4: Integration Tests
```bash
# Run broader test suite
pytest
npm test
```

### Step 5: Manual Verification
- Review diff: `git diff --cached`
- Check related files
- Verify behavior matches intent

## Documentation

Document complex resolutions in:

### Commit Message
```bash
git commit -m "$(cat <<'EOF'
merge: resolve user authentication conflicts

Resolved conflicts between caching implementation (main)
and real-time updates (feature-branch) by combining both
approaches with cache invalidation strategy.

- Keep caching for read-heavy operations
- Keep WebSocket for real-time updates
- Add cache invalidation on WebSocket events

Files resolved:
- src/auth/user.py
- src/cache/manager.py
EOF
)"
```

### Code Comments
```python
# NOTE: Conflict resolution (2025-01-21)
# Combined caching and real-time updates. Cache is invalidated
# when WebSocket receives updates to ensure data freshness.
def get_user(user_id):
    cached = cache.get(user_id)
    if cached:
        return cached
    # ...
```

### Pull Request
Add comment explaining resolution strategy and reasoning.
