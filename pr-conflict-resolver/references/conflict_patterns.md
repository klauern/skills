# Conflict Patterns Reference

This document provides detailed information about how the pr-conflict-resolver skill identifies, parses, and classifies merge conflicts.

## Conflict Marker Format

Git uses three standard markers to denote conflicts:

```
<<<<<<< HEAD (or branch name)
Content from the current branch ("ours")
=======
Content from the incoming branch ("theirs")
>>>>>>> branch-name (incoming branch)
```

### Extended Conflict Format

Some conflicts include the base version (common ancestor):

```
<<<<<<< HEAD
Content from current branch
||||||| base
Original content before either branch changed it
=======
Content from incoming branch
>>>>>>> feature-branch
```

## Parsing Algorithm

### Step 1: Locate Conflict Markers

```bash
# Find all conflicted files
git status --porcelain | grep '^UU' | awk '{print $2}'
```

### Step 2: Extract Versions

For each conflicted file, extract the three versions:

```bash
git show :1:path/to/file  # Base version (common ancestor)
git show :2:path/to/file  # Ours (current branch)
git show :3:path/to/file  # Theirs (incoming branch)
```

### Step 3: Parse Conflict Hunks

1. Read file line by line
2. Track state: NORMAL, OURS, BASE, THEIRS
3. Build conflict objects with:
   - Line range (start, end)
   - Ours content
   - Base content (if available)
   - Theirs content
   - Surrounding context (5 lines before/after)

## Conflict Classification

### Simple Conflicts (Auto-resolvable)

#### 1. Whitespace Conflicts

**Pattern**: Only difference is whitespace (spaces, tabs, newlines)

```python
<<<<<<< HEAD
def foo(bar,baz):
    return bar + baz
=======
def foo(bar, baz):
    return bar + baz
>>>>>>> format-cleanup
```

**Detection**:
```python
import difflib
ours_normalized = normalize_whitespace(ours)
theirs_normalized = normalize_whitespace(theirs)
if ours_normalized == theirs_normalized:
    return ConflictType.WHITESPACE
```

**Resolution**: Apply project formatting rules

#### 2. Import Ordering

**Pattern**: Same imports, different order

```python
<<<<<<< HEAD
import os
import sys
from typing import Dict, List
=======
from typing import Dict, List
import os
import sys
>>>>>>> reorder-imports
```

**Detection**:
```python
ours_imports = set(extract_imports(ours))
theirs_imports = set(extract_imports(theirs))
if ours_imports == theirs_imports:
    return ConflictType.IMPORT_ORDER
```

**Resolution**: Sort according to language conventions (PEP 8, etc.)

#### 3. Identical Changes

**Pattern**: Both branches made the exact same change

```javascript
<<<<<<< HEAD
const API_URL = 'https://api.example.com/v2';
=======
const API_URL = 'https://api.example.com/v2';
>>>>>>> update-api-url
```

**Detection**:
```python
if ours == theirs:
    return ConflictType.IDENTICAL
```

**Resolution**: Keep one version (they're the same)

#### 4. Non-overlapping Additions

**Pattern**: Both branches added different content to the same location

```python
<<<<<<< HEAD
def calculate_total(items):
    return sum(item.price for item in items)

def calculate_tax(total):
    return total * 0.08
=======
def calculate_total(items):
    return sum(item.price for item in items)

def calculate_discount(total, percent):
    return total * (1 - percent / 100)
>>>>>>> add-discount
```

**Detection**: Different function/class names, no semantic overlap

**Resolution**: Keep both additions

### Medium Conflicts (Suggest strategy)

#### 5. Function Signature Changes

**Pattern**: One branch modified signature, other branch calls the function

```python
<<<<<<< HEAD
def process_user(user_id, email):
    # Implementation
=======
def process_user(user_id):
    # Implementation using user_id only
>>>>>>> simplify-user-processing
```

**Detection**:
- Parameter count changed
- Parameter names changed
- Return type changed

**Resolution Strategy**: Update all call sites to match new signature

#### 6. Variable Renames

**Pattern**: One branch renamed, other branch used old name

```javascript
<<<<<<< HEAD
const userData = fetchUserData(userId);
console.log(userData.name);
=======
const user = fetchUserData(userId);
console.log(userData.name);  // Still using old name
>>>>>>> rename-user-data
```

**Detection**: Identifier changed in declaration but not in usage

**Resolution Strategy**: Complete the rename consistently

#### 7. Dependency Version Conflicts

**Pattern**: Different versions of same dependency

```json
<<<<<<< HEAD
"lodash": "^4.17.20"
=======
"lodash": "^4.17.21"
>>>>>>> update-lodash
```

**Detection**: Same package, different versions

**Resolution Strategy**: Choose newer version unless breaking changes exist

### Complex Conflicts (Manual resolution required)

#### 8. Logic Conflicts

**Pattern**: Different implementations of same functionality

```python
<<<<<<< HEAD
def validate_email(email):
    # Regex-based validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
=======
def validate_email(email):
    # Library-based validation
    return email_validator.validate(email)
>>>>>>> use-email-validator-lib
```

**Detection**:
- Same function/method name
- Different implementation approach
- Different dependencies or logic

**Resolution Strategy**:
- Evaluate both approaches
- Consider performance, maintainability, correctness
- Choose or refactor to combine best aspects

#### 9. State Management Conflicts

**Pattern**: Different approaches to managing state

```javascript
<<<<<<< HEAD
// Using local state
const [user, setUser] = useState(null);
const [loading, setLoading] = useState(false);
=======
// Using context
const { user, loading } = useUserContext();
>>>>>>> add-user-context
```

**Detection**: Different state management patterns

**Resolution Strategy**: Align on one state management approach

#### 10. API Contract Changes

**Pattern**: Both branches changed API differently

```typescript
<<<<<<< HEAD
interface User {
    id: string;
    email: string;
    role: 'admin' | 'user';
}
=======
interface User {
    id: number;
    email: string;
    permissions: string[];
}
>>>>>>> new-permission-system
```

**Detection**: Breaking changes to shared interfaces/types

**Resolution Strategy**: Design migration path for both changes

## Classification Algorithm

```python
def classify_conflict(conflict):
    # Quick checks for simple conflicts
    if is_identical(conflict):
        return ConflictType.IDENTICAL

    if is_whitespace_only(conflict):
        return ConflictType.WHITESPACE

    if is_import_reorder(conflict):
        return ConflictType.IMPORT_ORDER

    if is_non_overlapping(conflict):
        return ConflictType.NON_OVERLAPPING

    # Check for medium complexity
    if is_signature_change(conflict):
        return ConflictType.SIGNATURE_CHANGE

    if is_rename(conflict):
        return ConflictType.RENAME

    if is_version_conflict(conflict):
        return ConflictType.VERSION

    # Default to complex
    if has_logic_changes(conflict):
        return ConflictType.LOGIC

    if has_state_changes(conflict):
        return ConflictType.STATE

    if has_api_changes(conflict):
        return ConflictType.API

    return ConflictType.UNKNOWN
```

## Context Analysis

For each conflict, gather surrounding context:

### Code Context
```python
# Get 10 lines before and after conflict
context_before = file_lines[conflict.start - 10:conflict.start]
context_after = file_lines[conflict.end:conflict.end + 10]
```

### Commit Context
```bash
# Get commits that touched this region
git log -L <start>,<end>:path/to/file --oneline
```

### Semantic Context
- Function/class containing the conflict
- Module/file purpose
- Related changes in same commit
- Test files that cover this code

## Edge Cases

### Nested Conflicts

Git doesn't create nested markers, but manual editing might:

```python
<<<<<<< HEAD
<<<<<<< HEAD
x = 1
=======
x = 2
>>>>>>> inner
=======
x = 3
>>>>>>> outer
```

**Handling**: Detect and report as error, ask user to resolve manually

### Resolved Markers in Code

If conflict markers appear in strings or comments:

```python
code = """
<<<<<<< HEAD
This is not a real conflict
=======
"""
```

**Handling**: Parse as strings, not conflict markers

### Binary Files

```
<<<<<<< HEAD
Binary files differ
=======
>>>>>>> feature-branch
```

**Handling**: Report as binary conflict, suggest manual resolution tools

## Language-Specific Patterns

### Python
- Import sorting per PEP 8
- Docstring conflicts (often mergeable)
- Type hint additions

### JavaScript/TypeScript
- Import sorting (relative before absolute)
- Semicolon conflicts
- Type definition changes

### Go
- Import grouping (standard, external, internal)
- gofmt differences
- Interface method additions

### Rust
- Import consolidation
- Trait implementations
- Macro conflicts

## Performance Considerations

- Parse conflicts lazily (only when needed)
- Cache parsed results
- Limit context lines to reasonable amount
- Use Haiku for parsing, Sonnet for classification
