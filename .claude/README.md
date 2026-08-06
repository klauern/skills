# Local Claude Code Configuration

This directory contains local configuration for Claude Code specific to the klauern-skills repository.

## Structure

```text
.claude/
├── agents/            # Local subagents (skill-validator, release-checker, etc.)
├── commands/          # Local slash commands
│   └── bump-version.md
├── hooks/             # Claude Code hooks (see list below)
├── skills/            # Local skills (not distributed)
│   ├── version-manager/
│   └── session-start-hook/
├── settings.json      # Hook registrations and permissions
└── README.md          # This file
```

## Local Skills

### version-manager

A repository-specific skill for managing semantic versions of plugins in this marketplace.

**Purpose**: Helps maintain version consistency across:
- Individual plugin versions (`plugins/*/.claude-plugin/plugin.json`)
- Global marketplace version (`.claude-plugin/marketplace.json`)

**Usage**:
```bash
# Interactive guided workflow
/bump-version <plugin-name>

# Manual script usage
uv run .claude/skills/version-manager/scripts/detect_changes.py plugins/<plugin-name>
uv run .claude/skills/version-manager/scripts/infer_bump_type.py
uv run .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> <major|minor|patch>
```

## Local Commands

### /bump-version

Interactive version bump workflow: detects which plugin changed, shows what changed,
suggests a bump type, confirms with the user, then bumps plugin.json + marketplace.json
and creates a conventional commit.

## Hooks (registered in settings.json)

- `validate-commit-format.sh` — PreToolUse(Bash): validates conventional commit format
- `workflow-lint.sh` — PostToolUse(Edit|Write): lints GitHub workflow files
- `auto-validate-skill.sh` — PostToolUse(Edit|Write): suggests skill-validator when a SKILL.md changes
- `version-bump-reminder.sh` — UserPromptSubmit: reminds to run `/bump-version` before commit-push
- `dev-context.sh` — SessionStart: injects plugin/skill counts

## Agents

- `skill-validator` — validates SKILL.md files against authoring guidelines
- `release-checker` — pre-publish validation across all plugins
- `changelog-detector` — fetches/summarizes changelogs for upgrades
- `commit-analyzer` — recommends atomic commit boundaries
- `pr-preflight-reviewer` — reviews PR diff against description draft

## Why Local?

These skills and commands are specific to managing THIS repository's development workflow.
They are not distributed as part of the plugin marketplace — they're tools FOR developing
the marketplace itself.

**Local skills** (`.claude/skills/`) vs **Distributed skills** (`plugins/*/skills/<skill-name>/`):
- Local: tools for developing this repo
- Distributed: tools for end users of the plugins

## Development Workflow

1. **Make changes** to skills, commands, or plugin code
2. **Run** `/bump-version <plugin-name>` when ready
3. **Review** the suggested changes, **confirm**, and let it update versions
4. **Push** when ready to release
