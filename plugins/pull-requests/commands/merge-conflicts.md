---
allowed-tools: Bash, Read, Edit
description: Resolve Merge Conflicts
---

# /pull-requests:merge-conflicts

Resolve the merge conflicts in the current repository.

## Behavior

Invoke the **pr-conflict-resolver** skill: detect conflicted files, classify each
conflict, apply the skill's resolution strategies within its autonomy guardrails,
and verify with `git diff --check` before staging.

Escape hatch: `git merge --abort` restores the pre-merge state.

## Complete the active operation

After all conflicts are staged, complete the active merge with a message that
records the resolution:

```bash
git commit -m "$(cat <<'EOF'
merge: resolve conflicts between <source> and <target>

Conflicts resolved:
- <file>: <one-line strategy, e.g. combined both import blocks>
EOF
)"
```
