# Conventional Commits Examples

The non-obvious cases only — simple `type(scope): description` one-liners need no examples.

## Breaking Change

Changes that break backward compatibility must be clearly marked — `!` after type/scope
plus a `BREAKING CHANGE:` footer with a migration path:

```bash
git commit -m "$(cat <<'EOF'
feat(config)!: change environment variable prefix from APP_ to MYAPP_

BREAKING CHANGE: All environment variables now use MYAPP_ prefix
instead of APP_. Update your .env files:
- APP_API_KEY → MYAPP_API_KEY
- APP_DATABASE_URL → MYAPP_DATABASE_URL

Migration script available at scripts/migrate-env.sh
EOF
)"
```

## Body That Explains "Why"

```bash
git commit -m "$(cat <<'EOF'
fix(validation): correct email validation regex

The previous regex was rejecting valid email addresses
containing plus signs. Updated to follow RFC 5322 spec.

Fixes #456
EOF
)"
```

## Multiple Commits from Unstaged Changes

Breaking mixed work into logical, atomic commits (see the commit-splitter skill for the
analysis workflow):

```bash
git add src/components/ThemeToggle.tsx src/styles/darkMode.css
git commit -m "feat(ui): add dark mode toggle"

git add src/components/Button.tsx
git commit -m "fix(ui): correct button alignment in mobile view"

git add tests/components/ThemeToggle.test.tsx
git commit -m "test(ui): add dark mode toggle tests"
```
