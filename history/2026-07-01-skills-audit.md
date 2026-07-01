# Skills Audit — 2026-07-01

Full audit of the klauern-skills marketplace: 6 plugins, 15 shipped skills, 27 commands,
8 hooks, 5 subagents, 2 local skills, ~10,400 lines of markdown. Reviewed against
`docs/skill-authoring-guidelines.md` and current Claude Code plugin/skill documentation.

**Headline numbers:** ~2,400–2,600 lines (~25%) are cuttable duplication or filler;
~20 functional bugs found, including 2 structural issues that may prevent the
marketplace from working at all for installers.

---

## P0 — Structural issues (verify + fix first)

### 1. Plugin skills may not load at all when installed

Current Claude Code docs state plugin skills are discovered in the plugin's `skills/`
directory (or via an explicit `"skills": [...]` field in plugin.json; the only root-level
exception is a *single* `SKILL.md` at plugin root, ≥ v2.1.142). This repo places multiple
skills in named root-level folders (`plugins/commits/conventional-commits/`, etc.), and
**no plugin.json declares a `skills` field**. If the docs describe actual behavior, all 15
marketplace skills are silently ignored on install — only commands work. The session-start
hook's "15 skills" banner is just `find -name SKILL.md`; it proves nothing about loading.

**Action:** verify with a clean test install (`/plugin install commits@klauern-skills`,
then check the skill listing). If skills don't load, either move them under
`plugins/<name>/skills/` or add `"skills": ["./conventional-commits", "./commit-splitter"]`
etc. to each plugin.json.

### 2. marketplace.json ticktick entry drops 5 of 6 commands

`.claude-plugin/marketplace.json:36` has `"commands": ["commands/enrich.md"]` on the
ticktick entry (added in the enrich PR as a mistaken "registration"). Marketplace-entry
component fields **override** plugin defaults — when present, the default `commands/`
directory is not scanned, so `capture`, `inbox`, `today`, `setup`, and `clear-dates`
are dropped for installers. No other plugin has this field.

**Action:** delete the field; default discovery already finds all six commands.

---

## Functional bugs

### Broken script invocation everywhere (capacities + ticktick, 9 sites)

Every command that shells out uses:

```bash
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
```

Command markdown isn't executed as a script file — `$0` resolves to the shell binary, so
`SCRIPT_DIR` becomes `/usr/scripts` and every invocation fails. The correct mechanism,
`${CLAUDE_PLUGIN_ROOT}/scripts/...`, appears nowhere in the repo, and **CLAUDE.md's
"External Scripts" section documents the broken pattern as the standard**, so it keeps
propagating. Affected: capacities `list-spaces.md:27`, `daily-note.md:37`,
`save-weblink.md:41`, `search.md:37`, `space-info.md:34`; ticktick `inbox.md:53,58`,
`today.md:47`, `clear-dates.md:23`. Also `capacities-api/references/examples.md` uses
repo-relative `uv run plugins/capacities/scripts/...` paths that only work from the repo root.

### TickTick priority semantics contradict themselves (7 sites)

Legend tables say TickTick-native `1=low, 3=medium, 5=high`
(`ticktick-capture/SKILL.md:33`, `ticktick-enrich/SKILL.md:35`), but the mapping tables
shift down a level: "high → 3, medium → 1, low → 0"
(`ticktick-capture/references/examples.md:43-51`, `commands/capture.md:98`,
`ticktick-enrich/SKILL.md:84`, `enrichment-guide.md:79`, `question-bank.md:59-63`).
A user saying "high priority" gets a task displaying as **Medium**. `ticktick-enrich/SKILL.md`
contradicts itself within one file. Standardize on TickTick-native and fix all sites.

### "Someday" sentinel date poisons overdue reviews

ticktick-enrich instructs setting `1970-01-01T00:00:00.000+0000` for someday tasks
(`SKILL.md:36,85`, `enrichment-guide.md:80`, `question-bank.md:78-81`), while the same
plugin ships `ticktick_api.py clear-dates` specifically to null dates. A 1970 dueDate makes
every someday task maximally **overdue** in ticktick-review's overdue query. Also:
`gtd-contexts.md:19` defines someday as `priority: [0]`, which matches every untriaged task.
Standardize on the clear-dates script. Related: capture uses ISO offset `+00:00` while
enrich uses `+0000` (TickTick's API expects `+0000`); and `ticktick_api.py`'s auth error
points at `/ticktick:setup`, which configures the MCP server, not `TICKTICK_ACCESS_TOKEN`.

### pull-requests

- `commands/merge-conflicts.md:2` — `allowed-tools: Bash` but step 4 requires editing files
  to remove conflict markers. Needs `Bash, Read, Edit`. As shipped, Claude is forced into
  error-prone `sed`/heredoc rewrites.
- `commands/pr.md` — line 25 documents a `--base` flag, but lines 38–49 and 160 hardcode
  `main` in every `git log`/`git diff`. With `--base staging` the analysis still diffs
  against main. Use a `$BASE` variable.
- `commands/pr-update.md:135` — `echo "New Description" > /tmp/pr-body.md` loses multi-line
  bodies; use the heredoc pattern pr.md already uses. Also missing `AskUserQuestion` in
  allowed-tools despite requiring user approval at step 7.
- `plugin.json` description "Intelligent pull request creation skill" omits conflict
  resolution, comment review, and PR update.

### dev-utilities

- `commands/worktree.md` — delegates to `@agent-git-worktree-creator`, which exists nowhere
  in the repo (README.md:401 advertises it too). Broken as shipped.
- `gh-actions-upgrader/SKILL.md:104` + `commands/gh-actions-upgrade.md:196-197` — false
  breaking-change claims (checkout v3→v4 did **not** change the fetch-depth default;
  `set-safe-directory` was not removed). Hardcoded "latest version" tables are also stale
  (checkout/setup-node at v5) — self-defeating in a skill that teaches
  `gh api .../releases/latest`. Cut the table; trust the API.
- `git-optimize` — the whole skill invokes the author's personal gitconfig aliases
  (`cleanup`, `sweep`, `trimall`, …) as if universally available; marketplace users fail at
  step 1. Make alias installation step 1 (definitions already exist in configuration.md) or
  use raw git. Also: frontmatter `1.0.0` vs "Version History: 1.1.0" mismatch; broken link
  to nonexistent `example_workflows.md`.
- `poetry lock --no-update` (removed in Poetry 2.0) in `ci-failure-analyzer/SKILL.md:54`,
  `commands/gh-checks.md:43`, `dependency-upgrader/references/ecosystems.md:91`.
- `ci-failure-analyzer/references/failure-patterns.md:95` — exit code 78 is not "permission
  denied"; it was Actions' deprecated *neutral* status.
- `commands/gh-actions-upgrade.md:289-290` — dead links to `./commit-push.md` / `./pr.md`
  (live in other plugins). Missing `allowed-tools`. `commands/gh-checks.md:92` — broken
  heading anchor.
- `commands/agents-md.md:27` — the quoted upstream migration table includes the
  self-referential `mv AGENTS.md AGENTS.md && ln -s AGENTS.md AGENTS.md`, which an agent
  might actually run. Quote only the Claude Code–relevant instruction.

### Repo infrastructure

- **All 5 subagents** (`.claude/agents/*.md`) use `allowedTools:` — the documented key is
  `tools:`. Unknown keys are ignored, so every agent silently gets **all** tools; intended
  restrictions (e.g. read-only skill-validator) never applied.
- **3 PostToolUse hooks are invisible** (`pr-quality-check.sh`, `workflow-lint.sh`,
  `auto-validate-skill.sh`): they print plain stdout, which for PostToolUse goes to the
  transcript only — Claude never sees the warnings. They need
  `hookSpecificOutput.additionalContext` JSON (or exit 2 + stderr).
- `block-grep-extended.sh` — false premise (BSD grep supports `-E`; `-e` is not a
  substitute), over-broad matching (fires on `... | sed -E`), and emits decision JSON on
  stderr where it isn't parsed (blocking works only via exit-2 side effect). Delete or rewrite.
- `pr-quality-check.sh` — hardcoded Zendesk `FSEC-` JIRA check warns on every PR in this
  public repo; no `--body-file` handling; sed extraction fails on multiline bodies.
- `validate-commit-format.sh` — type list omits `revert`; `-m "$MSG"` (variable) or escaped
  quotes → hard deny; heredoc extraction grabs the wrong heredoc if one precedes the commit.
- `tool-use.sh` — unregistered in settings.json AND reads positional args instead of stdin
  JSON. Doubly dead; delete. The two `hookify.*.local.md` files duplicate existing hooks and
  are referenced by nothing.
- `.claude/commands/bump-version.md:53` — `jq -r '.version'` reads the wrong path (it's
  `.metadata.version`), yielding `null` → `update_changelog.py null`.
- `.claude/commands/version-bump.md` — hardcoded four-plugin tables; misses ticktick and
  agent-patterns entirely, so version detection skips the two newest plugins. Two overlapping
  commands (`/bump-version` script-driven vs `/version-bump` manual) with different docs/hooks
  pointing at each — keep one.
- `capacities.py` implements a `lookup` command documented nowhere.
- `code-mode-mcp/SKILL.md` description is 1,315 chars — over the 1,024-char cap enforced by
  the repo's own skill-validator (which would FAIL it; the hook that should suggest running
  it is one of the invisible PostToolUse hooks — the automation chain is broken at both ends).

---

## Stale documentation

`AGENTS.md`/`CLAUDE.md` is ~45–50% stale or redundant (~220 of 453 lines):

- Says "four plugins" (line 9) and "Current version: 2.4.0" (line 306) — actual: six, 2.9.0.
- Install list, 82-line structure diagram, and "Skill References" all omit ticktick and
  agent-patterns (4 skills missing). Replace the diagram with a pointer to `plugins/`.
- **Two contradictory "Issue Tracking with bd" sections** (lines 255–273 vs 342–427): one
  says commit `.beads/issues.jsonl`, the other says Dolt-sync with no manual export. The
  actual file is `.beads/beads.left.jsonl`. Keep one short section pointing at
  `docs/beads-workflow.md` (and fix the filename there too).
- References nonexistent `docs/QUICKSTART.md`; both version commands and the
  version-manager skill reference a nonexistent root `CHANGELOG.md`.
- Zendesk-internal context (aws-sso, FSEC/SECURE JIRA prefixes) in a public marketplace repo.
- "MCP Server Strategy" claims no project MCP servers are needed — stale now that the
  ticktick plugin requires one.
- `README.md:7,41` says "three plugins". `.cursor/rules/project-overview.mdc:60` instructs
  installing plugin names that never existed (`conventional-commits@klauern-skills`).
- `.claude/README.md` lists 1 command (2 exist) and 1 hook (8 exist), omits `agents/`.
- `release-checker.md`'s own checks ("AGENTS.md mentions all plugins") would currently fail —
  it evidently hasn't run since ticktick/agent-patterns landed.

---

## Bloat and consolidation (~2,400–2,600 cuttable lines)

### Pattern 1: commands fork their skills instead of delegating (~600 lines)

The single largest source of bloat and drift. Each of these commands re-implements its
skill's workflow, and they already disagree in places:

| Command | Skill it forks | Cuttable |
|---|---|---|
| `dev-utilities/commands/gh-actions-upgrade.md` (290) | gh-actions-upgrader | ~250 |
| `dev-utilities/commands/git-optimize.md` (196) | git-optimize | ~140* |
| `pull-requests/commands/pr.md` (215) | pr-creator | ~90 |
| `pull-requests/commands/merge-conflicts.md` (82) | pr-conflict-resolver | ~55 |
| `dev-utilities/commands/gh-checks.md` (93) | ci-failure-analyzer | ~60 |
| `commits/commands/commit-split.md` (58) | commit-splitter | ~40 |
| `ticktick/commands/capture.md`, `enrich.md`, `today.md`, `inbox.md` | their skills | ~130 |
| `dev-utilities/commands/devcontainer-setup.md` (83) | devcontainer-setup | ~55 |

\* **Before stubbing git-optimize.md, salvage lines 85–89 and 152–175** — the git-trim
non-interactive execution strategy (dry-run, parse, delete directly, treat "remote ref does
not exist" as success) is the most valuable content in the whole git-optimize unit and is
absent from the skill. Move it into the skill first.

Target shape: a command is frontmatter + usage/arguments/examples + "invoke the X skill",
~15–30 lines. `ticktick/commands/enrich.md:50` already says "the detailed workflow lives in
the skill" — then re-explains it anyway.

Caveat: fixing P0 #1 is a precondition — commands can only delegate to skills if the skills
actually load.

### Pattern 2: reference files duplicating SKILL.md or each other (~1,200 lines)

- `conventional-commits/references/workflows.md` (146) — near-verbatim copy of SKILL.md's
  Essential Instructions. **Delete the file.** The type list appears 4×, breaking-change
  syntax 4×, imperative-mood rules 3× across this skill's files; consolidate to
  format-reference.md (spec) + a trimmed best-practices.md (judgment only).
- `conventional-commits/references/examples.md` (161) — generic commit-message trivia any
  model produces unprompted; also has an unclosed code fence at EOF. Keep ~30 lines.
- `capacities-api/references/examples.md` (338) — ~85% synthetic command-output theater
  duplicating api-reference.md and the command files. Keep ~40 lines (pipeline pattern,
  `--no-cache`, error samples), fold into api-reference.md, delete the file.
- `capacities-api/references/workflows.md` (257) — ~75% single-command restatements
  ("user shares URL → save the URL"). Keep multi-space selection + error recovery (~50
  lines), delete the rest. Net: capacities-api goes from 3 references/~900 lines to 1
  reference (~300 lines) — api-reference.md is the only load-bearing file and is excellent.
- `ticktick-enrich/references/` — `enrichment-guide.md` and `question-bank.md` are divergent
  forks of the same doc with **conflicting** templates and subtask policy; question-bank is
  never referenced from the SKILL.md (dead as wired), has invented frontmatter fields, and
  contradicts the skill's "never infer priority" rule. Merge to one ~130-line reference.
- `ci-failure-analyzer` — 7 references where 3 would do: delete `best-practices.md` (77,
  generic advice) and `test-matrix.md` (45, author QA notes → `history/`); merge
  `log-parsing.md` into `failure-patterns.md` (duplicated regexes); the auto-fix/consult
  split is stated 3×; examples carry fabricated cost/time metrics.
- `commit-splitter` — `splitting.md` is ~60% textbook git (`git add -p` key legend appears
  twice across files); SKILL.md's Common Patterns table ≈ examples.md's Split Decision table.
- `pr-conflict-resolver` — conflict-type taxonomy appears 3×, strategies 2×, git commands 2×
  across SKILL.md/references; conflict-marker syntax explanation (workflows.md:32-47) is
  textbook. ~130 of 504 lines.
- `git-optimize/references/installation.md` (111) — PATH/chmod/per-distro troubleshooting;
  20 lines suffice. Worth a caveat that git-trim upstream is unmaintained.
- `.claude/skills/version-manager/SKILL.md` (464, near the 500 cap) — the identical 4-script
  sequence is spelled out **six times**. One workflow + one override note.

### Pattern 3: inert "Model Strategy" sections (~140 lines, 15+ files)

Haiku/Sonnet tables in nearly every skill (and Model columns in workflow tables) control
nothing at runtime — a SKILL.md cannot switch models, and none of these skills spawn
subagents. Delete all of them, **and** the guideline section that mandates the pattern
(`docs/skill-authoring-guidelines.md:444-494`, which also still says "Haiku 4.5/Sonnet 4.5").

### Pattern 4: misc dead weight

- `plugins/agent-patterns/code-mode-mcp-workspace/` — 208K of git-tracked eval artifacts
  (transcripts, grading, two byte-identical trigger-evals JSONs) shipped inside the plugin.
  Move to `history/` or delete. Same for `code-mode-mcp/evals/`.
- `dev-utilities/commands/continue.md` (7 lines) — vague, typo'd ("withe"), and
  institutionalizes markdown-notebook tracking that CLAUDE.md forbids. Delete or rewrite
  around `bd ready`.
- Version History changelogs inside SKILL.md bodies (`devcontainer-setup:222-228`,
  `git-optimize:108-111`) — loaded on every activation; move to plugin release notes.
- `commands/commit-push.md` — the branch-override rule is stated 3×; `` !`git diff HEAD` ``
  injects the full diff at invocation (use `--stat`); "commit and push in parallel" is wrong.
- `pr-update.md` is ~60% verbatim overlap with `pr.md`.
- Frontmatter cleanup: `version`/`author` in SKILL.md are silently ignored by Claude Code
  (only plugin.json supports them) — harmless, but the version-bump machinery editing them
  achieves nothing; drop or keep knowingly. Reference files with skill frontmatter
  (`ticktick-capture/references/examples.md:1-6`) likewise inert.

---

## Effectiveness improvements (beyond cutting)

1. **Trigger collision:** conventional-commits' description claims "split changes into
   multiple conventional commits" — commit-splitter's exact job. Two skills advertise the
   same task; discovery is ambiguous. Remove splitting from conventional-commits and
   delegate. (Consider whether commit-splitter should simply be merged into it.)
2. **Descriptions missing WHAT:** capacities-api, gh-actions-upgrader (and others) are
   trigger-phrases-only. Prepend one capability clause: "Upgrades GitHub Actions versions
   and migrates forks to upstream. Use when…".
3. **`@references/` mentions** in conventional-commits and commit-splitter SKILL.md files —
   `@` is eager inclusion in Claude Code, defeating progressive disclosure. Use plain
   relative links (the pull-requests skills do this correctly). Guidelines already say so.
4. **MCP server name fragility (ticktick):** all allowed-tools hardcode `mcp__ticktick__*`;
   a user registering the server as `TickTick` silently breaks every command. State the
   exact-name requirement in setup.md.
5. **allowed-tools scoping:** capacities commands use unscoped `Bash` — scope to
   `Bash(uv run:*)`. ticktick is the good example. `argument-hint` frontmatter is unused
   across all commands that take args.
6. **Three overlapping validation mechanisms** (skill-lint command, skill-validator agent,
   auto-validate-skill hook) with independently drifting criteria — make the command invoke
   the agent.
7. **hedge vendor numbers** in code-mode-mcp ("98%+ token reduction" → "per Cloudflare's
   demo"). Otherwise the strongest knowledge skill in the repo (its own evals show 1.0
   pass rate with skill vs 0.5 without).
8. **pr-comment-review.md** is the best command in the repo (resolved/outdated GraphQL
   filtering is load-bearing knowledge); switch to `gh api graphql -f query= -F owner=…`
   variables instead of echo-pipe with manual substitution.
9. **bd-work-loop.md** is genuinely good; drop the unfulfilled "Confluence-ready" promise,
   verify `bd ready --limit`/`bd list --status=open` flags exist, align `--status
   in_progress` vs `--claim` with CLAUDE.md.

---

## Suggested sequencing

1. **Verify + fix skill loading** (P0.1) and remove the marketplace `commands` override
   (P0.2). Everything else assumes the product actually loads.
2. **Fix functional bugs**: `$0` script paths (+ fix the CLAUDE.md pattern doc),
   `allowedTools` → `tools` in 5 agents, PostToolUse hooks → additionalContext JSON or
   delete, merge-conflicts allowed-tools, pr.md `$BASE`, ticktick priority/sentinel-date,
   bump-version jq path, worktree.md, git-optimize aliases, false gh-actions claims,
   poetry staleness.
3. **Rewrite AGENTS.md** (~half the file) and sync README/cursor rules; run release-checker
   afterward as the gate.
4. **De-fork commands** (delegate to skills) — after step 1 confirms skills load.
5. **Consolidate references** per Pattern 2; strip Model Strategy sections and the
   guideline that mandates them.
6. **Relocate eval/workspace artifacts** out of shipped plugin trees; merge the two
   version-bump commands.

Rough post-cleanup size: ~7,800 lines (from ~10,400), with less drift risk because each
fact lives in exactly one place.
