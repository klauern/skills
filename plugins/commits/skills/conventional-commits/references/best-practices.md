# Conventional Commits Best Practices

Judgment calls beyond the format spec ([format-reference.md](format-reference.md)).

## Good vs. Bad, By Principle

**Atomic** — one logical change:
✅ `feat(auth): add OAuth2 support`
❌ `feat(auth): add OAuth2 support and fix button styling and update README`

**Imperative mood**:
✅ `add user authentication` ❌ `added user authentication`

**Concise description, details in body**:
✅ `feat(auth): add OAuth2 support` + a body naming providers and refresh logic
❌ `feat(auth): add OAuth2 support with Google and GitHub providers and token refresh`

**Body explains why, not what** (the diff shows what):
✅ "Previous implementation created new connections per query, causing performance
issues under load. Pooling reduces overhead."
❌ "Changed the database connection code to use a pool. Updated all query functions."

## Scope Naming Conventions

Use **consistent scope names** throughout a repository:

- **Component-based**: `feat(header)`, `fix(sidebar)`
- **Layer-based**: `feat(api)`, `fix(database)`
- **Feature-based**: `feat(auth)`, `fix(payments)`

Always check existing conventions first: `git log -10 --oneline` and match the style.

## Pre-Commit Checklist

```bash
git status             # Check what's staged
git diff --cached      # Review staged changes
git log -10 --oneline  # Check recent commit style
```

## Issue References

Link commits to issues in the footer: `Fixes #456`, `Closes #457`, `Related to #458`.

## Common Pitfalls

- **Vague descriptions**: `fix: update code` → `fix(auth): prevent null pointer in token validation`
- **Multiple changes in one commit**: split bug fix / feature / docs into separate commits
- **Missing scope in a large codebase**: `feat: add validation` → `feat(forms): add email validation`
- **Ignoring repo conventions**: match the scope names already in `git log`
- **Silent breaking changes**: always `!` or `BREAKING CHANGE:` footer
