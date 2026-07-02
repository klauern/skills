---
name: pr-conflict-resolver
description: This skill should be used when the user asks to "resolve merge conflicts", "fix PR conflicts", "analyze conflict markers", or "apply conflict resolution strategies" during git merge workflows.
version: 1.0.0
---

# PR Conflict Resolver

Automated analysis and resolution of Git merge conflicts.

## Quick Start

**Command**: `/merge-conflicts` — Analyze and resolve merge conflicts

**Documentation**:
- [Workflows](references/workflows.md) — Detection, parsing, and execution flows
- [Patterns & Strategies](references/patterns-and-strategies.md) — Conflict types and resolution approaches
- [Examples](references/examples.md) — Real-world resolution scenarios

## When to Use

**Invoke when**:
- User asks to resolve merge conflicts
- Repository is in merge state with conflicts
- User runs `/merge-conflicts` command

**Don't use for**:
- Rebasing (different workflow)
- Cherry-picking conflicts (use git directly)
- Non-Git version control

## Workflow Overview

```
User Request → Detection (Haiku) → Parse (Haiku) → Classify (Sonnet)
    → Strategy Selection (Sonnet) → [Auto-fix (Haiku) | Guide (Sonnet)]
```

**Phases**:
1. **Detect**: Find conflicted files, check merge state
2. **Parse**: Extract ours/base/theirs content from markers
3. **Classify**: Categorize by type and complexity
4. **Strategize**: Select resolution approach
5. **Execute**: Auto-resolve or guide manual resolution
6. **Verify**: Check no markers remain, run tests

## Conflict Categories & Strategies

The full taxonomy (whitespace/import/identical/non-overlapping auto-fix; signature and
rename suggestions; logic and API-contract guidance) and the five resolution strategies
live in [patterns-and-strategies.md](references/patterns-and-strategies.md) — one home
for both tables. Operational classification order and quick checks are in
[workflows.md](references/workflows.md).

## Autonomy Guardrails

| Action | Auto-run? | Notes |
|--------|-----------|-------|
| Whitespace/import fixes | ✅ Yes | Show diff afterward |
| Identical/non-overlapping | ✅ Yes | Log resolution |
| Signature changes | ⚠️ Suggest | Present strategy, await approval |
| Logic conflicts | ❌ Never | Explain trade-offs, guide user |
| API changes | ❌ Never | User must decide direction |

## Git Commands Reference

All detection, three-version extraction, and verification commands live in
[workflows.md](references/workflows.md).

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not in merge state | Check `git status`, ensure merge started |
| Binary file conflict | Use `git checkout --ours/--theirs` |
| Nested markers | Manual fix, likely editing error |
| Tests fail after resolve | May be semantic conflict, review both sides |
| Cannot determine strategy | Ask user for context about intent |
