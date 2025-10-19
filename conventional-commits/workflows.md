# Conventional Commits Workflows

## Decision Tree

1. **Check staging status**
   - Staged changes → Single commit workflow
   - Unstaged changes → Multi-commit workflow

2. **Push requirement**
   - User mentions "push" → Push after committing
   - Otherwise → Commit only

## Single Commit Workflow

Use when changes are already staged for a single commit.

### Steps

1. **Review staged changes**

   ```bash
   git diff --cached
   git log -10 --oneline  # Check recent commit style
   ```

2. **Analyze and determine**
   - **Type**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`
   - **Scope**: Component, module, or area affected (optional but recommended)
   - **Breaking change**: Does this break existing functionality?

3. **Create commit message**

   ```
   <type>[optional scope]: <description>

   [optional body]

   [optional footer(s)]
   ```

4. **Commit using heredoc**

   ```bash
   git commit -m "$(cat <<'EOF'
   <type>(scope): description

   Optional body explaining the rationale
   for the change and any important context.

   BREAKING CHANGE: description if applicable
   Fixes #123
   EOF
   )"
   ```

5. **Push if requested**

   ```bash
   git push
   ```

**See also**: [`../commands/commit.md`](../commands/commit.md)

## Multi-Commit Workflow

Use when nothing is staged and changes need to be broken into logical commits.

### Steps

1. **Review all changes**

   ```bash
   git status
   git diff
   git log -10 --oneline  # Check recent commit style
   ```

2. **Analyze and categorize (Use Haiku 4.5)**

   Group changes by:
   - **Type**: Features, fixes, documentation, refactoring, etc.
   - **Scope**: Component, module, or area affected
   - **Logical boundaries**: Each commit should be atomic and self-contained

   Example categorization:
   - New authentication feature → `feat(auth)`
   - Bug fix in validation → `fix(validation)`
   - Documentation updates → `docs`
   - Test additions → `test(auth)`

3. **Plan commit breakdown (Use Sonnet 4.5)**

   Create a list of commits, each representing a single logical change:
   1. `feat(auth): add OAuth2 authentication support`
   2. `fix(validation): correct email validation regex`
   3. `docs: update authentication setup guide`
   4. `test(auth): add OAuth2 integration tests`

4. **Stage and commit each change**

   For each planned commit:

   ```bash
   # Stage files for this commit
   git add <files-for-this-commit>

   # Create the commit
   git commit -m "$(cat <<'EOF'
   <type>(scope): description

   Optional body explaining the change.
   EOF
   )"
   ```

5. **Verify commits**

   ```bash
   git log --oneline -n <number-of-commits>
   ```

6. **Push if requested**

   ```bash
   git push
   ```

**See also**: [`../commands/commit.md`](../commands/commit.md), [`../commands/commit-push.md`](../commands/commit-push.md)

## Sub-Agent Strategy

### Use Haiku 4.5 for

- Quick diff analysis
- File categorization by type or component
- Simple commit message drafting

### Use Sonnet 4.5 for

- Commit breakpoint determination
- Multi-commit planning
- Scope identification
- Complex commit message composition with detailed bodies
- Cross-cutting change analysis

**Example**: When analyzing unstaged changes, use Haiku 4.5 to categorize files by type, then Sonnet 4.5 to determine optimal commit breakdown considering atomic commits and logical boundaries.
