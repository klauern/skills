# Resolve Merge Conflicts

Concise, prescriptive steps to resolve merge conflicts.

## Usage

```bash
/merge-conflicts
```

## Behavior

1. Detect conflicts and list files
   - Run: `git status --porcelain` and collect files with conflicts
2. Inspect context
   - Run: `git log --oneline --graph --all -10`
   - Run: `git show HEAD` and `git show MERGE_HEAD` if present
3. Resolve files iteratively
   - For each conflicted file:
     - Open and review all conflict hunks
     - Decide: keep ours, keep theirs, or merge both
     - Edit to remove markers and finalize the resolution
     - Stage: `git add <file>`
4. Verify state
   - Run: `git diff --cached --stat` and `git status`
5. Optional tests
   - Run the project’s test command if applicable
6. Complete merge
   - Commit with a brief, structured message (example below)

## Example Commit

```bash
git commit -m "$(cat <<'EOF'
merge: resolve conflicts from <branch>

Resolved:
- path/to/fileA
- path/to/fileB
EOF
)"
```

## Notes

- Prefer combining intent when safe; otherwise choose the correct side
- Resolve and stage one file at a time to keep focus
- If the merge is not appropriate, abort with `git merge --abort`
