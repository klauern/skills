---
allowed-tools: Bash, Read, AskUserQuestion
description: Create well-formatted conventional commits with smart split detection, branch safety, and automatic push
---

## Arguments

- `$ARGUMENTS` - Optional: target branch name (e.g., `main`, `master`, or a feature branch name)
  - If provided, commits directly to the specified branch (bypasses branch safety checks)
  - If omitted, follows branch safety rules (creates feature branch if on main/master)

## Context

- Current git status: !`git status`
- Current git diff: !`git diff HEAD`
- Current branch: !`git branch --show-current`
- File count: !`git diff --staged --name-only | wc -l`
- **Target branch argument: `$ARGUMENTS`**

---

## Phase 1: Analyze Staged Changes

Run these commands in parallel to understand the changes:

```bash
git status
git diff --staged --stat
git log -10 --oneline
```

### Split Detection Heuristics

Check if splitting would be beneficial:

**Indicators that splitting is beneficial**:
- 5+ files changed
- Multiple scopes detected (auth, api, ui, etc.)
- Tests mixed with implementation
- Documentation mixed with code
- Multiple concerns (feature + refactor + fix)

**Analysis to perform**:
1. Count files changed
2. Identify file types (implementation, tests, docs)
3. Detect scopes from file paths
4. Check for mixed concerns

### Ask User

If splitting would be beneficial:

```text
I've analyzed your staged changes and detected [N] files across [M] scopes.

Would you like to split these into atomic commits? [y/N]

Benefits:
- Clearer commit history
- Easier code review
- Better git bisect capability
```

**If user accepts**: Proceed to split workflow (see Phase 3B)
**If user declines**: Proceed with single commit (see Phase 3A)

**If splitting not beneficial**: Proceed directly to Phase 2 (skip the question)

---

## Phase 2: Branch Safety Check

> **CRITICAL**: Check the "Target branch argument" in Context above FIRST. If `$ARGUMENTS` contains a value, skip branch safety checks.

### If `$ARGUMENTS` is provided

**Bypass all safety checks** and commit directly to specified branch:

```bash
# If argument is main/master and not on it, checkout first
if [ "$ARGUMENTS" = "main" ] || [ "$ARGUMENTS" = "master" ]; then
  current_branch=$(git branch --show-current)
  if [ "$current_branch" != "$ARGUMENTS" ]; then
    git checkout "$ARGUMENTS"
  fi
fi

# If argument is different branch, checkout (create if needed)
if [ "$(git branch --show-current)" != "$ARGUMENTS" ]; then
  git checkout "$ARGUMENTS" 2>/dev/null || git checkout -b "$ARGUMENTS"
fi

# Proceed to Phase 3
```

### If `$ARGUMENTS` is empty (Default Behavior)

**Apply branch safety rules**:

```bash
current_branch=$(git branch --show-current)

if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
  # On main/master - create feature branch

  # Determine branch prefix from changes
  if git diff --staged | grep -q "test"; then
    prefix="test"
  elif git diff --staged --name-only | grep -q "README\|docs/"; then
    prefix="docs"
  elif git diff --staged | grep -q "fix\|bug"; then
    prefix="fix"
  else
    prefix="feature"
  fi

  # Create descriptive branch name
  # Extract description from likely commit message
  description=$(echo "placeholder" | tr ' ' '-')  # Will be derived from changes

  branch_name="${prefix}/${description}"

  echo "Creating feature branch: $branch_name"
  git checkout -b "$branch_name"
else
  # Already on feature branch - proceed
  echo "On feature branch: $current_branch"
fi
```

---

## Phase 3: Commit Creation

### Phase 3A: Single Commit (Simple Mode)

If user declined split OR splitting not beneficial:

1. **Run git commands** to analyze changes:
   ```bash
   git status
   git diff
   git log -10 --oneline
   ```

2. **Analyze changes** and create conventional commit message:
   - Determine appropriate type (feat, fix, chore, docs, style, refactor, test, etc.)
   - Identify scope from file paths if relevant
   - Write clear, concise description
   - Add body if changes need explanation
   - Add footer with breaking changes or issue references if needed

3. **Stage relevant untracked files** if needed

4. **Create commit** using heredoc format:
   ```bash
   git commit -m "$(cat <<'EOF'
   type(scope): description

   Optional body explaining the changes in detail.
   Can span multiple lines.

   Optional footer with references or breaking changes.
   EOF
   )"
   ```

5. **Verify** commit succeeded:
   ```bash
   git status
   ```

### Phase 3B: Split Commits (Atomic Mode)

If user accepted split:

#### Step 1: Identify Logical Boundaries

Use commit-splitter skill guidance:

**File-based boundaries**:
- Group by file purpose (implementation, tests, docs)
- Separate different components/modules

**Concern-based boundaries**:
- Separate refactors from features
- Separate bug fixes from new work
- Separate infrastructure from application code

**Scope-based boundaries**:
- Group by component (auth, api, ui, etc.)
- Keep related changes together

**Dependency-based boundaries**:
- Foundation changes first (types, utils)
- Implementation next
- Features using implementation
- Tests last

**Reference**: commit-splitter/references/splitting-strategies.md

#### Step 2: Propose Splits

Present suggested splits to user:

```text
I've analyzed your staged changes. Here's how I suggest splitting them:

Commit #1: feat(auth): add OAuth login
Files:
  - src/auth/oauth.ts (new OAuth implementation)
  - src/auth/types.ts (OAuth type definitions)
Rationale: Core OAuth implementation

Commit #2: test(auth): add OAuth tests
Files:
  - tests/auth/oauth.test.ts (comprehensive test suite)
Rationale: Separate tests from implementation

Commit #3: docs(auth): document OAuth setup
Files:
  - docs/auth.md (OAuth configuration guide)
Rationale: Documentation separate from code
```

#### Step 3: Get User Approval

Use AskUserQuestion:

```text
Does this splitting strategy look good?

Options:
1. "Yes, proceed automatically" - I'll create all commits
2. "Yes, guide me step-by-step" - I'll help you create each commit manually
3. "Suggest changes" - Modify the splitting strategy
```

#### Step 4A: Automatic Mode

If user selects "proceed automatically":

```bash
# Reset staging
git reset

# For each proposed commit:
# 1. Stage files
git add <files-for-commit-1>

# 2. Create commit
git commit -m "$(cat <<'EOF'
type(scope): description

Optional body.
EOF
)"

# 3. Repeat for next commits
git add <files-for-commit-2>
git commit -m "..."

# Continue until all commits created
```

#### Step 4B: Interactive Mode

If user selects "step-by-step":

For each proposed commit:

1. Show the split:
   ```text
   Next commit: feat(auth): add OAuth login
   Files to stage: src/auth/oauth.ts, src/auth/types.ts
   ```

2. Stage files:
   ```bash
   git reset
   git add src/auth/oauth.ts src/auth/types.ts
   ```

3. Show diff:
   ```bash
   git diff --staged
   ```

4. Show proposed message:
   ```text
   Proposed commit message:
   ---
   feat(auth): add OAuth login

   Implement OAuth 2.0 flow for Google and GitHub providers.
   ---
   ```

5. Ask for confirmation:
   ```text
   Create this commit? [yes/edit message/skip]
   ```

6. Create commit based on response

7. Continue to next commit

#### Step 5: Verify Completion

```bash
# Show created commits
git log -<n> --oneline

# Verify no changes remain staged
git status
```

---

## Phase 4: Push to Remote

After commit(s) are created, handle pushing to remote.

### Detect Remote Tracking

```bash
# Check if branch has upstream
upstream=$(git rev-parse --abbrev-ref @{u} 2>/dev/null)

if [ -z "$upstream" ]; then
  # New branch - needs upstream setup
  push_new=true
else
  # Existing branch - simple push
  push_new=false
fi
```

### Ask User

```text
Push to remote? [Y/n]
```

**Default**: Yes for feature branches, No for main/master (unless $ARGUMENTS specified)

### Execute Push

```bash
if [ "$push_new" = true ]; then
  # New branch - set upstream
  current_branch=$(git branch --show-current)
  git push -u origin "$current_branch"
else
  # Existing branch - simple push
  git push
fi
```

### Verify Success

```bash
git status
```

Expected output: `Your branch is up to date with 'origin/<branch>'`

---

## Execution Strategy

**You can call multiple tools in a single response.** Optimize based on workflow:

### For Single Commits
Execute in parallel where possible:
- Branch check + commit creation can be sequential
- Push can follow commit immediately

### For Split Commits
- Create all commits first (sequential, dependent)
- Push once at the end (single operation)

### Use Bash Chaining
Combine independent operations with `&&`:
```bash
git checkout -b feature/new-feature && git commit -m "..." && git push -u origin feature/new-feature
```

---

## Important Notes

### Respect $ARGUMENTS
**CRITICAL**: If user provided a branch name in `$ARGUMENTS`, use it exactly as specified. Do NOT override with feature branch creation.

### Commit Message Format
Always use heredoc for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
type(scope): description

body

footer
EOF
)"
```

### Conventional Commits Specification
- Follow https://www.conventionalcommits.org/
- Use appropriate type (feat, fix, chore, docs, style, refactor, test, build, ci)
- Include scope when relevant
- Use imperative mood ("add" not "added")
- Keep description under 100 characters

**Reference**: conventional-commits/SKILL.md

### Splitting Guidelines

**Do split**:
- Implementation from tests from docs
- Different concerns (refactor vs feature)
- Different components/scopes
- Fixes from features

**Don't split**:
- Tightly coupled changes (would break build)
- Single-purpose changes (already atomic)
- Type definitions from their implementations (same file)

**Reference**: commit-splitter/references/best-practices.md

### Branch Safety
By default (when `$ARGUMENTS` is empty):
- Never commit directly to `main` or `master`
- Always create descriptive feature branches
- **Exception**: If user explicitly provides `main` or `master` as `$ARGUMENTS`

### Each Commit Must
- Build successfully independently
- Pass tests independently
- Have a single, clear purpose
- Follow dependency order

---

## Examples

### Example 1: Simple Commit (No Split, With Push)

**Setup**: Single file change, on feature branch

```bash
echo "new feature" >> src/feature.ts
git add src/feature.ts
```

**Execution**: `/commits:commit`

**Workflow**:
1. Analyze: 1 file, single concern → No split needed
2. Branch check: On feature branch → No action needed
3. Create commit: `feat(core): add new feature`
4. Ask to push: Yes
5. Push: `git push`

---

### Example 2: Auto-Split with Multiple Scopes

**Setup**: Changes across auth, api, and tests

```bash
# Multiple files modified
git add src/auth/login.ts src/api/users.ts tests/auth.test.ts
```

**Execution**: `/commits:commit`

**Workflow**:
1. Analyze: 3 files, 2 scopes + tests → Suggest split
2. User accepts automatic mode
3. Branch check: On main → Create `feature/add-auth-api`
4. Split into 3 commits:
   - `feat(auth): add login functionality`
   - `feat(api): add user endpoints`
   - `test(auth): add login tests`
5. Ask to push: Yes
6. Push: `git push -u origin feature/add-auth-api`

---

### Example 3: Direct Commit to Main (Using $ARGUMENTS)

**Setup**: Hotfix needed on main

```bash
git checkout main
echo "hotfix" >> package.json
git add package.json
```

**Execution**: `/commits:commit main`

**Workflow**:
1. Analyze: 1 file → No split needed
2. Branch check: `$ARGUMENTS=main` → Skip safety, stay on main
3. Create commit: `fix(deps): update critical dependency`
4. Ask to push: Yes
5. Push: `git push`

---

### Example 4: Interactive Split

**Setup**: Complex changes needing manual review

**Execution**: `/commits:commit`

**Workflow**:
1. Analyze: 6 files, multiple concerns → Suggest split
2. User selects "step-by-step" mode
3. For each proposed commit:
   - Show files and message
   - User confirms or edits
   - Create commit
4. Ask to push: Yes
5. Push all commits

---

## Edge Cases

### No Staged Changes
```text
❌ No staged changes found

Please stage your changes first:
  git add <files>
```

### Merge in Progress
```bash
if [ -f .git/MERGE_HEAD ]; then
  echo "❌ Merge in progress"
  echo "Complete or abort merge first:"
  echo "  git merge --continue"
  echo "  git merge --abort"
  exit 1
fi
```

### Large Commit Without Split
If user declines split but commit is large (15+ files):

```text
⚠️  Warning: Large commit detected (15 files)

Consider splitting for better reviewability. Continue anyway? [y/N]
```

### Invalid $ARGUMENTS Branch
```bash
# Check if branch exists
if ! git show-ref --verify --quiet "refs/heads/$ARGUMENTS"; then
  echo "Branch '$ARGUMENTS' does not exist"
  echo "Create new branch '$ARGUMENTS'? [y/N]"
  # Handle response
fi
```

### Detached HEAD
```bash
if [ "$(git symbolic-ref -q HEAD)" = "" ]; then
  echo "❌ Detached HEAD state"
  echo "Checkout a branch first:"
  echo "  git checkout main"
  exit 1
fi
```

---

## Success Criteria

After completion:

- [ ] Commit(s) created with proper conventional commit format
- [ ] Each commit builds independently (if split)
- [ ] Branch safety rules applied (unless $ARGUMENTS provided)
- [ ] Pushed to remote (if user confirmed)
- [ ] Git status clean

---

## References

- **Conventional Commits**: conventional-commits/SKILL.md
- **Splitting Strategies**: commit-splitter/references/splitting-strategies.md
- **Split Examples**: commit-splitter/references/examples.md
- **Best Practices**: commit-splitter/references/best-practices.md
