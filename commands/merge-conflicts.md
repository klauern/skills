---
allowed-tools: Bash
description: Resolve Merge Conflicts
---

Concise, prescriptive steps to resolve merge conflicts.

This command uses the `pr-conflict-resolver` skill to intelligently analyze and resolve conflicts.

## Usage

```bash
/merge-conflicts
```

## Behavior

Leverage the `pr-conflict-resolver` skill to intelligently resolve conflicts:

1. **Detect conflicts and analyze context**
   - Run: `git status --porcelain` and collect files with conflicts
   - Run: `git log --oneline --graph --all -10`
   - Run: `git show HEAD` and `git show MERGE_HEAD` if present

2. **Parse and classify conflicts**
   - For each conflicted file, parse conflict markers
   - Classify conflict type (whitespace, import order, logic, etc.)
   - Analyze intent from commit messages and code changes

3. **Resolve intelligently**
   - **Simple conflicts** (whitespace, imports, identical): Auto-resolve when safe
   - **Medium conflicts** (function signatures, renames): Suggest strategy and apply
   - **Complex conflicts** (logic, refactoring): Provide detailed guidance with recommendations

4. **Apply resolutions iteratively**
   - For each conflict:
     - Show classification and analysis
     - Auto-resolve simple conflicts
     - For complex conflicts, explain both sides and recommend approach
     - Edit to remove markers and finalize
     - Stage: `git add <file>`

5. **Verify state**
   - Run: `git diff --cached --stat` and `git status`
   - Ensure no conflict markers remain: `git diff --check`

6. **Optional tests**
   - Run the project's test command if applicable

7. **Complete merge**
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

- The `pr-conflict-resolver` skill provides intelligent analysis and auto-resolution for simple conflicts
- Prefer combining intent when safe; otherwise choose the correct side based on skill's analysis
- Resolve and stage one file at a time to keep focus
- Trust the skill's classification and follow its recommendations for complex conflicts
- If the merge is not appropriate, abort with `git merge --abort`

## Skill Capabilities

The `pr-conflict-resolver` skill can:
- **Auto-resolve**: Whitespace, import ordering, identical changes, non-overlapping additions
- **Analyze intent**: Extract purpose from commit messages and code changes
- **Suggest strategies**: Merge both, choose side, refactor, or manual resolution with guidance
- **Provide context**: Explain what each side does and recommend best approach

See the skill documentation at `pr-conflict-resolver/SKILL.md` for detailed information.
