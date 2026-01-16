---
name: require-version-bump-before-commit
enabled: true
event: prompt
action: warn
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: /commit-push|/commits:commit-push
---

⚠️ **Version Bump Reminder**

You're about to commit and push changes. Have you run `/version-bump` first?

**Before committing plugin changes, remember to:**
1. Run `/version-bump` to update affected plugin versions
2. The version-bump command will auto-detect changed plugins
3. Marketplace version will also be bumped automatically

If you've already run `/version-bump` or this commit doesn't affect plugins, proceed as normal.
