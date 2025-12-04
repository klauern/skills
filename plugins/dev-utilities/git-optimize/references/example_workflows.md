# Example Workflows

## Example 1: First-Time Cleanup

### Scenario
Developer has been working on a project for months, merging PRs via GitHub. Local repository has 15 stale branches.

### User Request
```
User: I have a bunch of old branches from merged PRs. Can you help me clean them up?
```

### Assistant Workflow

**Step 1: Check installation**
```bash
which git-trim
# /opt/homebrew/bin/git-trim
```

✓ git-trim is installed

**Step 2: Preview with dry-run**
```bash
git-trim --dry-run
```

**Output**:
```
Fetching from origin...
Analyzing branches...

Branches to delete (merged):
  feature/user-auth (merged into origin/main)
  bugfix/login-error (merged into origin/main)
  feature/api-endpoints (merged into origin/main)
  [... 10 more ...]

Stray branches (upstream deleted, may have unmerged changes):
  feature/experimental-ui (upstream deleted)
  feature/rejected-approach (upstream deleted)

Would delete 13 branches.
Run without --dry-run to delete.
```

**Step 3: Explain results**
```
Assistant: git-trim found:
- 13 merged branches (safe to delete)
- 2 stray branches (upstream deleted - need review)

The merged branches are confirmed to be fully integrated into main.
The stray branches had their upstreams deleted (possibly rejected PRs).

Would you like me to:
1. Delete only the merged branches (safest)
2. Review the stray branches first
3. Delete everything
```

**Step 4: User confirms**
```
User: Review the stray branches first
```

**Step 5: Inspect stray branches**
```bash
git log origin/main..feature/experimental-ui --oneline
# Shows 3 commits not in main

git log origin/main..feature/rejected-approach --oneline
# Shows 0 commits (was squash merged but upstream deleted)
```

**Step 6: Explain findings**
```
Assistant:
- feature/experimental-ui has 3 unmerged commits (keep for now?)
- feature/rejected-approach is actually merged (safe to delete)

I recommend:
1. Keep experimental-ui (has unique work)
2. Delete the 13 merged branches + rejected-approach
```

**Step 7: Execute selective cleanup**
```bash
git-trim
# Interactive prompt:
# Delete merged branches? [y/N] y
# Delete stray branches? [y/N] n
```

**Step 8: Manual cleanup of confirmed stray**
```bash
git branch -D feature/rejected-approach
```

**Step 9: Verify**
```bash
git branch -vv
# Shows only active branches + experimental-ui
```

**Outcome**: 14 branches deleted, 1 preserved for review, repository cleaned.

---

## Example 2: Git-Flow Repository

### Scenario
Project uses git-flow with `develop` and `master` branches. Feature branches merge to develop, releases merge to master.

### User Request
```
User: Clean up my git-flow repo branches
```

### Assistant Workflow

**Step 1: Check configuration**
```bash
git config trim.bases
# (empty output - not configured)
```

**Step 2: Configure git-flow bases**
```bash
git config trim.bases "develop,master"
```

**Step 3: Explain configuration**
```
Assistant: I've configured git-trim for git-flow:
- trim.bases = develop,master

This means branches merged into EITHER develop OR master are safe to delete.
```

**Step 4: Dry-run**
```bash
git-trim --dry-run
```

**Output**:
```
Base branches: origin/develop, origin/master
Excluded branches: (none)

Branches to delete (merged):
  feature/add-users (merged into origin/develop)
  feature/export-data (merged into origin/develop)
  release/v1.2.0 (merged into origin/master)
  hotfix/critical-bug (merged into origin/master)

Would delete 4 branches.
```

**Step 5: Execute**
```bash
git-trim
# [y/N] y
```

**Outcome**: 4 branches deleted, git-flow workflow preserved.

---

## Example 3: Stray Branch Review

### Scenario
Developer has 3 stray branches flagged by git-trim. Needs to decide which are safe to delete.

### User Request
```
User: I have stray branches. Help me figure out if I can delete them.
```

### Assistant Workflow

**Step 1: Identify stray branches**
```bash
git-trim --dry-run | grep "upstream deleted"
```

**Output**:
```
  feature/refactor-parser (upstream deleted)
  bugfix/edge-case (upstream deleted)
  experiment/new-algorithm (upstream deleted)
```

**Step 2: Analyze each branch**

**Branch 1: feature/refactor-parser**
```bash
git log origin/main..feature/refactor-parser --oneline
# (empty) - no unique commits
```
✓ Safe to delete (was merged, upstream deleted)

**Branch 2: bugfix/edge-case**
```bash
git log origin/main..bugfix/edge-case --oneline
# a1b2c3d Fix edge case in parser
# (1 commit)

git show a1b2c3d --stat
# Shows changes to parser.js
```
⚠ Has unmerged commit - check if needed

**Branch 3: experiment/new-algorithm**
```bash
git log origin/main..experiment/new-algorithm --oneline
# Shows 15 commits
```
❌ Keep (experimental work)

**Step 3: Explain findings**
```
Assistant: Analysis:
1. feature/refactor-parser: SAFE (merged, upstream deleted)
2. bugfix/edge-case: REVIEW NEEDED (1 unmerged commit)
3. experiment/new-algorithm: KEEP (15 commits of work)

For bugfix/edge-case, let me check if that commit exists elsewhere...
```

**Step 4: Deep dive on bugfix**
```bash
git log --all --grep="edge case" --oneline
# b2c3d4e Fix edge case in parser (on main)

git diff feature/bugfix/edge-case..main -- parser.js
# (no differences)
```

```
Assistant: The bugfix/edge-case commit appears to be already in main (likely squash merged).
It's safe to delete.
```

**Step 5: Selective deletion**
```bash
git branch -D feature/refactor-parser
git branch -D bugfix/edge-case
# Keep experiment/new-algorithm
```

**Step 6: Exclude from future prompts**
```bash
git config trim.exclude "experiment/new-algorithm"
```

**Outcome**: 2 stray branches deleted, 1 preserved and excluded.

---

## Example 4: Automation Setup

### Scenario
Developer wants to automate branch cleanup after every pull on main.

### User Request
```
User: Can you make git-trim run automatically when I pull?
```

### Assistant Workflow

**Step 1: Create post-merge hook**
```bash
cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash

# Only run on main/master/develop branches
BRANCH=$(git rev-parse --abbrev-ref HEAD)
case "$BRANCH" in
  "master"|"main"|"develop")
    echo "Running git-trim..."
    git trim --no-update
    ;;
esac
EOF

chmod +x .git/hooks/post-merge
```

**Step 2: Test hook**
```bash
# Simulate a merge
git checkout main
git merge --ff-only origin/main
# Hook automatically runs git-trim
```

**Step 3: Create helper alias**
```bash
git config alias.sync '!git fetch --prune && git pull && git trim'
```

**Step 4: Explain usage**
```
Assistant: I've set up automatic cleanup:

1. Post-merge hook: Runs git-trim after pulling on main/develop
2. git sync alias: Combines fetch, pull, and trim in one command

Usage:
  git pull          # Automatic cleanup via hook
  git sync          # Manual fetch + pull + trim

The hook uses --no-update to skip fetching (since you just pulled).
```

**Step 5: Test alias**
```bash
git sync
# Fetches, pulls, and trims in one command
```

**Outcome**: Automated cleanup configured, developer saves time.

---

## Example 5: Multi-Repository Cleanup

### Scenario
Developer has 20 repositories in `~/projects/` and wants to clean all of them.

### User Request
```
User: I want to clean up all my repos in ~/projects
```

### Assistant Workflow

**Step 1: Create cleanup script**
```bash
cat > ~/bin/trim-all-repos.sh << 'EOF'
#!/bin/bash

BASE_DIR="${1:-$HOME/projects}"

echo "Cleaning all repos in: $BASE_DIR"
echo

find "$BASE_DIR" -name ".git" -type d | while read gitdir; do
  REPO_DIR=$(dirname "$gitdir")
  echo "========================================="
  echo "Repository: $REPO_DIR"
  echo "========================================="

  cd "$REPO_DIR" || continue

  # Skip if not on main branch
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  if [[ "$BRANCH" != "main" && "$BRANCH" != "master" ]]; then
    echo "⚠ Not on main/master, skipping"
    echo
    continue
  fi

  # Run git-trim with no-update
  git trim --no-update
  echo
done

echo "========================================="
echo "Done!"
EOF

chmod +x ~/bin/trim-all-repos.sh
```

**Step 2: Dry-run across all repos**
```bash
# Modified version for dry-run
find ~/projects -name ".git" -type d -exec sh -c 'cd "$(dirname {})" && echo "=== $(basename $(dirname {})) ===" && git trim --dry-run' \;
```

**Output**:
```
=== project-a ===
Would delete 3 branches.

=== project-b ===
Would delete 0 branches.

=== project-c ===
Would delete 7 branches.
...
```

**Step 3: Explain and confirm**
```
Assistant: Found cleanable branches in 8 of 20 repositories.
Total branches to delete: 24

Would you like to:
1. Review each repo interactively
2. Clean all automatically
3. Clean only specific repos
```

**Step 4: Execute (user chooses option 2)**
```bash
~/bin/trim-all-repos.sh
```

**Outcome**: 24 branches deleted across 8 repositories, saved hours of manual work.

---

## Example 6: CI/CD Integration

### Scenario
Team wants to validate PRs don't introduce orphaned branches in CI.

### User Request
```
User: Add a CI check that fails if there are orphaned branches
```

### Assistant Workflow

**Step 1: Create CI workflow**
```yaml
# .github/workflows/branch-health.yml
name: Branch Health Check

on:
  pull_request:
  push:
    branches: [main, develop]

jobs:
  check-branches:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history

      - name: Install git-trim
        run: |
          cargo install git-trim

      - name: Check for stale branches
        run: |
          # Fetch all remotes
          git fetch --all --prune

          # Run git-trim in dry-run
          OUTPUT=$(git trim --dry-run)

          # Count branches to delete
          COUNT=$(echo "$OUTPUT" | grep -c "merged into" || true)

          if [ "$COUNT" -gt 0 ]; then
            echo "::warning::Found $COUNT stale branches that can be cleaned up"
            echo "$OUTPUT"
          else
            echo "✓ No stale branches found"
          fi
```

**Step 2: Create scheduled cleanup**
```yaml
# .github/workflows/weekly-cleanup.yml
name: Weekly Branch Cleanup

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday
  workflow_dispatch:  # Manual trigger

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Install git-trim
        run: cargo install git-trim

      - name: Run cleanup
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"

          # List branches to delete
          git trim --dry-run > cleanup-report.txt

          # Create issue with report
          gh issue create \
            --title "Weekly Branch Cleanup Report" \
            --body-file cleanup-report.txt \
            --label "maintenance"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Outcome**: Automated branch health monitoring in CI/CD.

---

## Common Patterns Summary

### Safe First-Time Use
```bash
git-trim --dry-run          # Preview
git-trim                    # Execute with confirmation
```

### Git-Flow Setup
```bash
git config trim.bases "develop,master"
git config trim.exclude "staging production"
git-trim
```

### Investigating Stray Branches
```bash
git log origin/main..<branch> --oneline
git diff origin/main..<branch> --stat
```

### Automation
```bash
# Post-merge hook
.git/hooks/post-merge

# Alias
git config alias.sync '!git fetch --prune && git pull && git trim'
```

### Multi-Repo Cleanup
```bash
find ~/projects -name .git -type d -execdir git trim --no-update \;
```
