# Local Claude Code Configuration

This directory contains local configuration for Claude Code specific to the klauern-skills repository.

## Structure

```
.claude/
├── commands/          # Local slash commands
│   └── bump-version.md
├── hooks/             # Claude Code hooks
│   └── tool-use.sh
├── skills/            # Local skills (not distributed)
│   └── version-manager/
└── README.md         # This file
```

## Local Skills

### version-manager

A repository-specific skill for managing semantic versions of plugins in this marketplace.

**Purpose**: Helps maintain version consistency across:
- Individual plugin versions (`plugins/*/. claude-plugin/plugin.json`)
- Global marketplace version (`.claude-plugin/marketplace.json`)
- CHANGELOG.md

**Usage**:
```bash
# Interactive guided workflow
/bump-version <plugin-name>

# Manual script usage
python .claude/skills/version-manager/scripts/detect_changes.py plugins/<plugin-name>
python .claude/skills/version-manager/scripts/infer_bump_type.py
python .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> <major|minor|patch>
python .claude/skills/version-manager/scripts/update_changelog.py <version>
```

**Scripts**:
- `detect_changes.py` - Git-based detection of what changed
- `infer_bump_type.py` - Conventional commit parser for bump suggestions
- `bump_version.py` - Updates plugin.json and marketplace.json
- `update_changelog.py` - Generates changelog entries

## Local Commands

### /bump-version

Interactive version bump workflow that:
1. Detects which plugin changed
2. Shows what changed (skills, commands, metadata)
3. Suggests version bump type
4. Asks for confirmation/override
5. Bumps versions
6. Updates changelog
7. Creates conventional commit

## Hooks

### tool-use.sh

Triggers after Write/Edit operations on:
- Skills (`plugins/*/[skill-name]/`)
- Commands (`plugins/*/commands/`)
- Plugin metadata (`.claude-plugin/*.json`)

Displays a reminder to bump versions with quick reference to commands.

## Why Local?

These skills and commands are specific to managing THIS repository's development workflow. They are not meant to be distributed as part of the plugin marketplace - they're tools FOR developing the marketplace itself.

**Local skills** (`.claude/skills/`) vs **Distributed skills** (`plugins/*/[skill-name]/`):
- Local: Tools for developing this repo
- Distributed: Tools for end users of the plugins

## Development Workflow

When developing plugins in this repository:

1. **Make changes** to skills, commands, or plugin code
2. **Get reminded** by the tool-use hook
3. **Run** `/bump-version <plugin-name>` when ready
4. **Review** the suggested changes
5. **Confirm** and let it update versions + changelog
6. **Push** when ready to release

This ensures version consistency and proper semantic versioning throughout development.
