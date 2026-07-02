---
name: version-manager
description: Local skill for managing versions in the klauern-skills repository. Use when bumping versions for this repository's plugins after modifying skills, commands, or metadata. Detects changes via git, infers version bump type from conventional commits, and updates plugin.json and marketplace.json. Triggered by /bump-version command or used directly via scripts.
---

# Version Manager (Local Skill)

**Repository-specific version management for klauern-skills.**

Detects what changed, infers the bump type from conventional commits, updates
`plugin.json` + `marketplace.json`, and creates the release commit.

## Workflow

**Recommended entry point**: `/bump-version <plugin-name>` (guided, with confirmation).

The underlying script sequence — used by the command, or directly:

```bash
# 1. Detect changes (JSON: skills_changed, commands_changed, metadata_changed, since_ref)
uv run .claude/skills/version-manager/scripts/detect_changes.py plugins/<plugin-name>

# 2. Infer bump type from conventional commits (JSON: bump_type, reason, commit analysis)
uv run .claude/skills/version-manager/scripts/infer_bump_type.py

# 3. Review the suggestion — automation suggests, you decide. Override the bump type
#    when semantics demand it (known breaking change → major; docs-only → patch).

# 4. Bump (preview first, then apply; updates plugin.json AND marketplace.json)
uv run .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> <major|minor|patch> --dry-run
uv run .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> <major|minor|patch>

# 5. Commit (version bumps stay separate from feature work)
git add .claude-plugin/marketplace.json plugins/<plugin-name>/.claude-plugin/plugin.json
git commit -m "chore(release): bump <plugin-name> to <new-version>"

# 6. Tag if releasing
git tag v<new-version> && git push origin main --tags
```

To inspect without bumping, stop after step 2.

## Bump Type Rules

- **major**: breaking changes (`!` or `BREAKING CHANGE:` commits) — removed/renamed
  skills or commands, incompatible behavior
- **minor**: new features (`feat:`) — added skills/commands or new capabilities
- **patch**: fixes/docs/refactoring (`fix:` or no conventional commits)

Full rules: [references/semver-guide.md](references/semver-guide.md)

## Version Cascade

```
Marketplace (metadata.version)
  └─ Plugin (plugin.json version)
      ├─ Skill   (inherits plugin version)
      └─ Command (inherits plugin version)
```

Skill/command change → plugin bump → marketplace bump; the marketplace version stays
>= the highest plugin version. Details:
[references/marketplace-structure.md](references/marketplace-structure.md)

## Script Reference

| Script | Purpose | Output |
|--------|---------|--------|
| `detect_changes.py <plugin-path>` | What changed since the last version tag | JSON |
| `infer_bump_type.py [since-ref]` | Suggested bump type from commits | JSON |
| `bump_version.py <plugin-path> <type> [--dry-run]` | Update both version files | JSON old/new |
