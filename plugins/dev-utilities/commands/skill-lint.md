---
allowed-tools: Bash, Read, Grep, Glob, Agent
description: Validate SKILL.md files against authoring guidelines
argument-hint: "[plugin-name]"
---

# /skill-lint

Validate one or all SKILL.md files against the token budget and authoring guidelines.

## Usage

```bash
/dev-utilities:skill-lint              # Validate all skills
/dev-utilities:skill-lint commits      # Validate skills in a specific plugin
```

## Behavior

Delegate to the **skill-validator** agent so validation criteria live in exactly one
place (`.claude/agents/skill-validator.md`):

1. Discover targets — `plugins/<name>/skills/*/SKILL.md` if a plugin was named,
   otherwise all `plugins/*/skills/*/SKILL.md`.
2. Launch the skill-validator agent with the target list.
3. Relay its per-skill PASS/WARN/FAIL results and the summary line
   (`N skills | N passed | N warnings | N failures`).
