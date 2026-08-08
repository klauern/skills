# Conflict Resolution Workflows

## Detection Phase

These workflows support conflicts from an active merge only. For rebase
conflicts, abort or continue the rebase directly instead of invoking this skill.

### Check Merge State
```bash
git rev-parse --verify MERGE_HEAD 2>/dev/null && echo "In merge state"
```

### Find Conflicted Files
```bash
git diff --name-only --diff-filter=U   # ALL unmerged files (any conflict state)
git status --porcelain | grep '^UU'    # Both modified
git status --porcelain | grep -E '^(DU|UD|AA|AU|UA|DD)'  # Delete/add conflict states
```

### Get Three Versions
```bash
git show :1:path/to/file  # Base (common ancestor)
git show :2:path/to/file  # Ours (current branch)
git show :3:path/to/file  # Theirs (incoming branch)
```

### Get Context
```bash
git log --oneline origin/main..HEAD       # Our commits
git log --oneline origin/main..MERGE_HEAD # Their commits
git log --format="%h %s" -L <start>,<end>:path/to/file  # Line history
```

## Parsing Phase

Extract each conflict's ours/base/theirs content from the standard markers, capture line
ranges, and keep ~5 lines of context before/after for classification.

## Classification Phase

### Classification Order (fast → slow)
1. **Identical**: `ours == theirs` → auto-resolve
2. **Whitespace**: Normalize and compare → auto-resolve
3. **Import order**: Same imports, different order → auto-resolve
4. **Non-overlapping**: Different additions, no overlap → merge both
5. **Signature change**: Parameter modifications → suggest strategy
6. **Variable rename**: Incomplete rename → suggest strategy
7. **Complex**: Logic/state/API changes → manual with guidance

### Quick Checks
```python
# Identical
if ours == theirs: return IDENTICAL

# Whitespace only
if normalize(ours) == normalize(theirs): return WHITESPACE

# Import reorder
if set(imports(ours)) == set(imports(theirs)): return IMPORT_ORDER
```

## Resolution Phase

### Auto-Resolve Commands
| Type | Action |
|------|--------|
| Whitespace | Apply formatter (black, prettier, gofumpt) |
| Import order | Sort per language convention |
| Identical | Keep either version |
| Non-overlapping | Keep both additions |

### Resolution Execution
```bash
# After editing file to resolve
git add path/to/file

# Verify no markers remain in the STAGED content (plain --check misses staged files)
git diff --cached --check
grep -rn '^\(<<<<<<<\|=======\|>>>>>>>\)' <file> && echo "markers remain" || true

# Show what will be committed
git diff --cached path/to/file
```

### Verification
```bash
# Syntax check
python -m py_compile file.py
tsc --noEmit file.ts

# Run affected tests
pytest path/to/test_file.py
npm test -- --findRelatedTests path/to/file.js
```

## Error Handling

| Issue | Detection | Response |
|-------|-----------|----------|
| Binary conflict | `file` command shows binary | Suggest: `git checkout --ours/theirs` |
| Submodule conflict | Path is submodule | Show commit SHAs, suggest manual |
| Invalid markers | Unmatched `<<<<<<<` / `>>>>>>>` | Report error, manual fix |
| Not in merge | No MERGE_HEAD | Inform user, check state |
