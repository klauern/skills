# Pre-commit Hook Integration

Guide to integrating commit message linting into your Git workflow using hooks.

## Overview

Git hooks allow you to validate commit messages before they're created, ensuring consistent formatting across your team.

### Available Hooks

**commit-msg**: Validates message after editing, before creating commit

**prepare-commit-msg**: Pre-populates message template (optional)

## Basic Setup

### Manual Hook Installation

#### 1. Create Hook File

```bash
# Create commit-msg hook
touch .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

#### 2. Add Validation Script

```bash
#!/bin/sh
# .git/hooks/commit-msg

# Read commit message from file
commit_msg_file="$1"
commit_msg=$(cat "$commit_msg_file")

# Validate using your linter
# Replace with actual validation command
if ! validate_commit_message "$commit_msg"; then
  echo "❌ Commit message validation failed"
  echo "See errors above"
  exit 1
fi

echo "✅ Commit message is valid"
exit 0
```

### Using Claude Code Linter

```bash
#!/bin/sh
# .git/hooks/commit-msg

commit_msg_file="$1"

# Use Claude Code to validate
claude "/commit-lint" < "$commit_msg_file"
exit_code=$?

if [ $exit_code -ne 0 ]; then
  echo ""
  echo "💡 Fix the commit message or use:"
  echo "   git commit --edit"
  echo "   to edit and retry"
  exit 1
fi

exit 0
```

---

## Advanced Setup

### Hook with Auto-fix

```bash
#!/bin/sh
# .git/hooks/commit-msg

commit_msg_file="$1"
original_msg=$(cat "$commit_msg_file")

# Try to auto-fix
fixed_msg=$(claude "/commit-fix" <<< "$original_msg")
fix_status=$?

if [ $fix_status -eq 0 ]; then
  # Auto-fix succeeded
  echo "$fixed_msg" > "$commit_msg_file"
  echo "✅ Commit message auto-fixed"
  exit 0
else
  # Auto-fix failed, show validation errors
  claude "/commit-lint" <<< "$original_msg"
  echo ""
  echo "❌ Could not auto-fix. Please edit your message."
  exit 1
fi
```

### Hook with User Confirmation

```bash
#!/bin/sh
# .git/hooks/commit-msg

commit_msg_file="$1"
original_msg=$(cat "$commit_msg_file")

# Validate
claude "/commit-lint" <<< "$original_msg"
lint_status=$?

if [ $lint_status -eq 0 ]; then
  # Already valid
  exit 0
fi

# Try to fix
fixed_msg=$(claude "/commit-fix" <<< "$original_msg")
fix_status=$?

if [ $fix_status -ne 0 ]; then
  # Can't fix, reject
  echo "❌ Validation failed and auto-fix unsuccessful"
  exit 1
fi

# Show proposed fix
echo ""
echo "Original:"
echo "---"
echo "$original_msg"
echo "---"
echo ""
echo "Proposed fix:"
echo "---"
echo "$fixed_msg"
echo "---"
echo ""

# Ask for confirmation (in interactive mode)
if [ -t 0 ]; then
  printf "Accept fix? [y/N] "
  read -r response
  case "$response" in
    [yY][eE][sS]|[yY])
      echo "$fixed_msg" > "$commit_msg_file"
      echo "✅ Applied fix"
      exit 0
      ;;
    *)
      echo "❌ Fix rejected. Edit your message."
      exit 1
      ;;
  esac
else
  # Non-interactive, apply automatically
  echo "$fixed_msg" > "$commit_msg_file"
  echo "✅ Applied auto-fix"
  exit 0
fi
```

---

## Template Setup

### Prepare-commit-msg Hook

Pre-populate commit message with template:

```bash
#!/bin/sh
# .git/hooks/prepare-commit-msg

commit_msg_file="$1"
commit_source="$2"

# Only add template for new messages
if [ -z "$commit_source" ]; then
  cat > "$commit_msg_file" << 'EOF'
# type(scope): description
#
# [Optional body]
#
# [Optional footer]
#
# Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
# Scopes: auth, api, ui, db, config (adjust for your project)
#
# Breaking changes: Add ! after type/scope or use BREAKING CHANGE: footer
EOF
fi
```

### Commit Template with Examples

```bash
#!/bin/sh
# .git/hooks/prepare-commit-msg

commit_msg_file="$1"
commit_source="$2"

if [ -z "$commit_source" ]; then
  # Analyze staged changes to suggest type and scope
  files_changed=$(git diff --staged --name-only)

  # Simple heuristics (extend as needed)
  suggested_type="feat"
  suggested_scope=""

  if echo "$files_changed" | grep -q "test"; then
    suggested_type="test"
  elif echo "$files_changed" | grep -q "README\|docs/"; then
    suggested_type="docs"
  fi

  if echo "$files_changed" | grep -q "auth"; then
    suggested_scope="(auth)"
  elif echo "$files_changed" | grep -q "api"; then
    suggested_scope="(api)"
  fi

  cat > "$commit_msg_file" << EOF
$suggested_type$suggested_scope:

# Staged files:
$(git diff --staged --name-only | sed 's/^/#   /')
#
# Examples:
#   feat(auth): add OAuth login
#   fix(api): resolve null pointer error
#   docs(readme): update installation steps
EOF
fi
```

---

## Team Setup

### Shared Hooks with Husky

For teams using Node.js projects:

#### 1. Install Husky

```bash
npm install --save-dev husky
npx husky init
```

#### 2. Create Hook

```bash
# Create commit-msg hook
npx husky add .husky/commit-msg
```

#### 3. Add Validation

Edit `.husky/commit-msg`:

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Validate commit message
npx commitlint --edit $1
```

#### 4. Configure Commitlint

Create `commitlint.config.js`:

```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore']
    ],
    'scope-enum': [
      2,
      'always',
      ['auth', 'api', 'ui', 'db', 'config'] // Adjust for your project
    ]
  }
};
```

### Shared Hooks with Pre-commit Framework

For Python projects:

#### 1. Install pre-commit

```bash
pip install pre-commit
```

#### 2. Create Configuration

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v2.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [--strict]
```

#### 3. Install Hooks

```bash
pre-commit install --hook-type commit-msg
```

---

## CI Integration

### GitHub Actions

Validate commit messages in pull requests:

```yaml
# .github/workflows/commit-lint.yml
name: Lint Commit Messages

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: wagoid/commitlint-github-action@v5
```

### GitLab CI

```yaml
# .gitlab-ci.yml
commit-lint:
  image: node:18
  stage: lint
  script:
    - npm install -g @commitlint/cli @commitlint/config-conventional
    - npx commitlint --from $CI_MERGE_REQUEST_DIFF_BASE_SHA
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

---

## Configuration

### Project-Specific Rules

Create `.commitlintrc.json`:

```json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [
      2,
      "always",
      ["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore"]
    ],
    "scope-enum": [
      2,
      "always",
      ["auth", "api", "ui", "db", "config", "core"]
    ],
    "scope-empty": [2, "never"],
    "header-max-length": [2, "always", 100],
    "body-max-line-length": [2, "always", 100]
  }
}
```

### Custom Types

Add project-specific types:

```json
{
  "rules": {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "wip",      // Work in progress (not for main branch)
        "hotfix"    // Emergency production fix
      ]
    ]
  }
}
```

---

## Troubleshooting

### Hook Not Running

**Problem**: Hook doesn't execute

**Check**:
```bash
# Verify hook exists
ls -la .git/hooks/commit-msg

# Verify it's executable
chmod +x .git/hooks/commit-msg

# Check git config
git config core.hooksPath
```

### Hook Fails on Merge Commits

**Problem**: Hook rejects merge commit messages

**Solution**: Skip validation for merge commits

```bash
#!/bin/sh
# .git/hooks/commit-msg

commit_msg_file="$1"
commit_source="$2"

# Skip validation for merge commits
if [ "$commit_source" = "merge" ]; then
  exit 0
fi

# Normal validation
# ...
```

### Hook Too Strict for Revert Commits

**Problem**: Git-generated revert messages fail validation

**Solution**: Allow revert commits

```bash
#!/bin/sh
# .git/hooks/commit-msg

commit_msg=$(cat "$1")

# Allow revert commits (start with "Revert ")
if echo "$commit_msg" | grep -q "^Revert "; then
  exit 0
fi

# Normal validation
# ...
```

---

## Bypassing Hooks

### Temporary Bypass

Use `--no-verify` flag:

```bash
git commit --no-verify -m "emergency fix"
```

**Warning**: Only use for emergencies, as this skips all validation.

### Permanent Bypass

Remove or disable hook:

```bash
# Temporarily disable
mv .git/hooks/commit-msg .git/hooks/commit-msg.disabled

# Re-enable
mv .git/hooks/commit-msg.disabled .git/hooks/commit-msg
```

---

## Testing Hooks

### Manual Test

```bash
# Create test message file
echo "feat: test message" > /tmp/test-msg

# Run hook manually
.git/hooks/commit-msg /tmp/test-msg
echo "Exit code: $?"
```

### Automated Test

Create `test-hook.sh`:

```bash
#!/bin/bash

hook=".git/hooks/commit-msg"

test_message() {
  local msg="$1"
  local expected_exit="$2"

  echo "$msg" > /tmp/test-msg
  $hook /tmp/test-msg
  actual_exit=$?

  if [ $actual_exit -eq $expected_exit ]; then
    echo "✅ PASS: $msg"
  else
    echo "❌ FAIL: $msg (expected $expected_exit, got $actual_exit)"
  fi
}

echo "Testing commit-msg hook..."
echo ""

# Should pass
test_message "feat: add login" 0
test_message "fix(api): resolve error" 0

# Should fail
test_message "added login" 1
test_message "Feature: add login" 1

echo ""
echo "Tests complete"
```

Run tests:

```bash
chmod +x test-hook.sh
./test-hook.sh
```

---

## Best Practices

### For Individuals

1. **Install hook** in `.git/hooks/` (not committed)
2. **Test hook** with various messages
3. **Use templates** to avoid common errors
4. **Learn from errors** to improve naturally

### For Teams

1. **Use Husky or pre-commit** to share hooks
2. **Document conventions** in CONTRIBUTING.md
3. **Provide examples** in commit template
4. **Review violations** in code reviews
5. **Adjust rules** based on team feedback

### For CI/CD

1. **Lint all PR commits** in CI
2. **Block merges** with invalid commits
3. **Provide clear error messages**
4. **Link to documentation** in errors

---

## Summary

### Quick Setup

```bash
# 1. Create hook
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/sh
claude "/commit-lint" < "$1" || exit 1
EOF

# 2. Make executable
chmod +x .git/hooks/commit-msg

# 3. Test
git commit --allow-empty -m "test: validate hook"
```

### Features by Complexity

**Basic**: Validate format, reject on error

**Intermediate**: Auto-fix common errors, ask for confirmation

**Advanced**: Suggest type/scope from changes, provide examples

### Recommended Approach

1. **Start simple**: Basic validation only
2. **Add auto-fix**: Once team is comfortable
3. **Customize**: Add project-specific scopes and rules
4. **Share**: Use Husky or pre-commit for teams
5. **Enforce**: Add CI validation for PRs
