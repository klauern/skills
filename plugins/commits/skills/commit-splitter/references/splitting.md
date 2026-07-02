# Git Commands for Splitting Commits

The non-obvious mechanics. Basic staging (`git add <files>`, `git restore --staged`) is
assumed.

## Hunk-Level Staging

```bash
git add -p [file]
```

Key prompts: `y`/`n` stage or skip, `s` split the hunk smaller, `e` edit manually,
`q` quit. When editing (`e`): delete `+` lines you don't want staged; change `-` to
` ` (space) for deletions you don't want staged; leave context lines alone.

For a brand-new file, `git add -N <file>` first, then `git add -p <file>` works on it.

## Workflow Patterns

### Clean Split Workflow

```bash
git diff HEAD --stat                 # 1. Review all changes
git add <files-for-commit-1>         # 2. Stage first group
git diff --cached --stat             # 3. Verify staged vs remaining
git commit -m "type(scope): description"
# Repeat for remaining groups
```

### Partial File Split Workflow

```bash
git diff <file>                      # 1. Review the mixed file
git add -p <file>                    # 2. Stage only hunks for the first commit
git diff --cached <file>             # 3. Verify
git commit -m "type(scope): first change"
git add <file>                       # 4. Stage the remainder
git commit -m "type(scope): second change"
```

## Splitting an Existing Commit

```bash
git reset HEAD~1        # undo last commit, changes back to unstaged
# then split with the workflows above
```

For a commit deeper in history: `git rebase -i HEAD~N`, mark it `edit`, `git reset HEAD~1`
when stopped, split, then `git rebase --continue`.

## Verification

```bash
git diff --cached            # what will be committed
git log --oneline -n 10      # resulting history
git show --stat HEAD         # files in last commit
```

To verify each commit builds independently: `git stash`, run build/tests, `git stash pop`.
