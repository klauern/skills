---
allowed-tools: Bash, Read, Edit
description: Bump plugin and marketplace versions based on changes
---

# /version-bump

Bump versions for changed plugins in this klauern-skills marketplace repository.

## Usage

```bash
/version-bump [bump-type] [plugin-name]
```

## Arguments

- `$ARGUMENTS` - Optional: bump type and/or plugin name
  - **Bump types**: `major`, `minor`, `patch` (default: `patch`)
  - **Plugin name**: `commits`, `pull-requests`, `dev-utilities`, `capacities`, or `all`
  - Examples:
    - `/version-bump` - Auto-detect changed plugins, patch bump
    - `/version-bump minor` - Auto-detect changed plugins, minor bump
    - `/version-bump patch commits` - Patch bump commits plugin only
    - `/version-bump minor all` - Minor bump all plugins

## Context

- Arguments: `$ARGUMENTS`
- Current branch: !`git branch --show-current`

## Instructions

1. **Parse Arguments**:
   - Extract bump type from `$ARGUMENTS`: `major`, `minor`, or `patch` (default: `patch`)
   - Extract target: specific plugin name, `all`, or auto-detect from changes

2. **Detect Changed Plugins** (if not targeting specific plugin or `all`):
   ```bash
   git diff --name-only main...HEAD 2>/dev/null || git diff --name-only HEAD~10
   ```
   - Map changed files to plugins:
     - `plugins/commits/**` → `commits`
     - `plugins/pull-requests/**` → `pull-requests`
     - `plugins/dev-utilities/**` → `dev-utilities`
     - `plugins/capacities/**` → `capacities`

3. **Read Current Versions**:
   - Plugin versions: `plugins/<name>/.claude-plugin/plugin.json` → `version` field
   - Marketplace version: `.claude-plugin/marketplace.json` → `metadata.version` field

4. **Calculate New Versions**:
   - Parse current version as `MAJOR.MINOR.PATCH`
   - Apply bump:
     - `major`: increment MAJOR, reset MINOR and PATCH to 0
     - `minor`: increment MINOR, reset PATCH to 0
     - `patch`: increment PATCH

5. **Update Versions** using the Edit tool:
   - Update each affected plugin's `plugin.json`
   - Update marketplace `marketplace.json` (always bump if any plugin bumped)

6. **Show Summary**:
   ```
   Version Bump Summary
   ====================
   Bump type: minor

   | Component      | Old Version | New Version |
   |----------------|-------------|-------------|
   | commits        | 1.1.0       | 1.2.0       |
   | marketplace    | 2.2.0       | 2.3.0       |
   ```

## Version Files

| Component | File | JSON Path |
|-----------|------|-----------|
| Marketplace | `.claude-plugin/marketplace.json` | `metadata.version` |
| commits | `plugins/commits/.claude-plugin/plugin.json` | `version` |
| pull-requests | `plugins/pull-requests/.claude-plugin/plugin.json` | `version` |
| dev-utilities | `plugins/dev-utilities/.claude-plugin/plugin.json` | `version` |
| capacities | `plugins/capacities/.claude-plugin/plugin.json` | `version` |

## Important

- **Auto-detection**: Default behavior detects plugins with changes via git diff
- **Marketplace sync**: Always bump marketplace version when any plugin is bumped
- **No commit**: Only updates files - use `/commit` or `/commit-push` afterward
