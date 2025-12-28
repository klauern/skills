# Conflict Resolution Workflows

## Detection Phase

### Check Merge State
```bash
git rev-parse --verify MERGE_HEAD 2>/dev/null && echo "In merge state"
```

### Find Conflicted Files
```bash
git status --porcelain | grep '^UU'    # Both modified (conflict)
git status --porcelain | grep '^DU'    # Deleted by us
git status --porcelain | grep '^UD'    # Deleted by them
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

### Conflict Marker Format
```
<<<<<<< HEAD (ours)
Current branch changes
||||||| base (optional)
Common ancestor content
=======
Incoming branch changes
>>>>>>> feature-branch (theirs)
```

### Parse Steps
1. Track state: NORMAL → OURS → BASE (optional) → THEIRS → NORMAL
2. Capture line ranges for each conflict
3. Extract 5 lines context before/after

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

# Verify no markers remain
git diff --check

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
