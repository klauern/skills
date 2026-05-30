---
allowed-tools: Bash, Read, Edit, AskUserQuestion
description: Bump version for a plugin in this repository
---

# Bump Version

Interactive version bump workflow for plugins in the klauern-skills repository.

## Instructions

1. **Determine which plugin to bump**:
   - If user provided plugin name as argument: use it
   - Otherwise: detect from recent git changes using:
     ```bash
     git diff --name-only $(git describe --tags --abbrev=0 --match=v* 2>/dev/null || git rev-list --max-parents=0 HEAD) HEAD
     ```
   - Look for changes in `plugins/*/` and identify which plugin(s) changed
   - If multiple plugins: ask user which one to bump

2. **Detect changes**:
   ```bash
   python3 .claude/skills/version-manager/scripts/detect_changes.py plugins/<plugin-name>
   ```
   Show the user what changed (skills, commands, metadata)

3. **Infer bump type**:
   ```bash
   python3 .claude/skills/version-manager/scripts/infer_bump_type.py
   ```
   Show the suggested bump type and reasoning

4. **Ask user to confirm or override**:
   Use AskUserQuestion with options:
   - "Accept suggestion (<bump-type>)" (recommended)
   - "Override to major"
   - "Override to minor"
   - "Override to patch"

5. **Execute bump**:
   ```bash
   # Dry run first to show what will change
   python3 .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> <bump-type> --dry-run

   # Show output to user

   # If user confirms, do actual bump
   python3 .claude/skills/version-manager/scripts/bump_version.py plugins/<plugin-name> <bump-type>
   ```

6. **Update changelog**:
   ```bash
   NEW_VERSION=$(jq -r '.version' .claude-plugin/marketplace.json)
   python3 .claude/skills/version-manager/scripts/update_changelog.py $NEW_VERSION
   ```

7. **Stage and commit**:
   ```bash
   git add .claude-plugin/marketplace.json \
           plugins/<plugin-name>/.claude-plugin/plugin.json \
           CHANGELOG.md

   git commit -m "$(cat <<'EOF'
   chore(release): bump <plugin-name> to <new-version>

   - Updated <plugin-name> from <old-version> to <new-version>
   - Updated marketplace from <old-marketplace-version> to <new-marketplace-version>
   - Updated CHANGELOG.md
   EOF
   )"
   ```

8. **Show summary**:
   Display what was updated and remind user to push when ready.

## Error Handling

- If no changes detected: inform user and exit
- If scripts fail: show error and suggest checking the script output
- If user cancels at any step: exit gracefully without changes

## Example Usage

```bash
/bump-version commits
/bump-version dev-utilities
/bump-version  # auto-detect
```
