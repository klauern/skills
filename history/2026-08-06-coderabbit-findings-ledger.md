# CodeRabbit Findings Ledger — PRs #16 and #17

This is an evidence record, not a task tracker. Beads epic `klauern-skills-gon`
owns task state. Repair rows are marked **assigned** until the orchestrator adds
the fixing commit SHA and revalidates the exact pushed head; no unchecked-task
syntax is used here.

## Review scope and exact heads

| PR | CodeRabbit review | Reviewed head | Current remote head checked for evidence |
|---|---|---|---|
| #16 | [review 4869851851](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | `b4ee1808033d32ce6d5099956c1b2d48b8e7c742` | #15 cumulative head `8515964bac597b4a5110dafb1a8d28ef0ab4ca48` |
| #17 | [review 4870123313](https://github.com/klauern/skills/pull/17#pullrequestreview-4870123313) | `ac9385c6834dbd00e68e5ee9871090d6bcead869` | #17 head `ac9385c6834dbd00e68e5ee9871090d6bcead869`; downstream evidence also checked at `8515964bac597b4a5110dafb1a8d28ef0ab4ca48` |
| #17 remediation | [review 4870422817](https://github.com/klauern/skills/pull/17#pullrequestreview-4870422817) | `09ac7a8163d4587052177ddc9b3d2a586b49cc1a` | Exact reviewed remediation head; seven findings comprise six inline threads plus one review-body-only, outside-diff finding. |
| #17 remediation 2 | [review 4870703669](https://github.com/klauern/skills/pull/17#pullrequestreview-4870703669) | `8e24c8ed635f5ff5720fedf6bb0f74485d88fd86` | Exact reviewed second-remediation head; five inline findings. |
| #17 remediation 3 | [review 4870951650](https://github.com/klauern/skills/pull/17#pullrequestreview-4870951650) | `f1f311775f40dd9268a8a228671b64a28dba5513` | Exact reviewed third-remediation head; one inline finding. |

The intervening exact remote heads were #18
`1a36a294c2f3fb78bb8ba14964450baa141c59f5` and #19
`8f5932d5c2c5a12d25195108f8ae9162e83be578`.

Disposition meanings:

- **fixed/superseded** — present cumulative evidence already resolves the
  finding, or a newer #17 finding replaces it with a more exact repair contract.
- **assigned** — valid repair owned by the named Luna worker/stack branch; not
  claimed fixed until a fixing commit and exact-head validation are recorded.
- **policy-rejected** — the requested change conflicts with the repository's
  current documented policy; the evidence and required revalidation are stated.

## PR #16 — 33 Major and 4 Nitpick findings

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 16-01 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Require all four SKILL.md fields | **policy-rejected** | Policy; no repair branch | `docs/skill-authoring-guidelines.md:405-408` defines the fields but `.claude/agents/skill-validator.md:25-27` makes only `name` and `description` required. | Keep validator aligned with the documented contract; validate all skills for the two required discovery fields and treat `version`/`author` as optional metadata. |
| 16-02 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Remove metadata inference from Sonnet duties | **fixed/superseded** | #16 cumulative stack | `ticktick-enrich/SKILL.md:52,62,67` limits output to supplied/approved context; the contradictory phrase is absent. | `git grep -n 'metadata inference' <head> -- plugins/ticktick` must return no matches. |
| 16-03 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Shorten Code Mode discovery description | **assigned** | #19 `claude/audit-4-consolidate-refs` — Luna Tail | `code-mode-mcp/SKILL.md:3-4` is still an overlong trigger/runtime inventory; scoped benchmark text exists at line 89. | Enforce a concise frontmatter capability/trigger summary and run skill validation plus a frontmatter length check. |
| 16-04 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Complete migrated skill paths | **fixed/superseded** | #19 cumulative stack | `commands/skill-lint.md:23-24` and `marketplace-structure.md:86,175` use `plugins/<name>/skills/<skill>/SKILL.md`. | Run plugin-specific and all-plugin discovery and assert both return the expected `SKILL.md` set. |
| 16-05 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Use clear-dates for someday tasks | **fixed/superseded** | #16 cumulative stack | `ticktick-enrich/SKILL.md:36,85` and `enrichment-guide.md:101,149` use `/ticktick:clear-dates`; the script command is documented by `commands/clear-dates.md:23`. | Search the enrichment skill and references for the 1970 sentinel; run the script's argument/parser tests. |
| 16-06 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Avoid stale full-task updates | **fixed/superseded** | #16 cumulative stack | `ticktick-enrich/SKILL.md:75` requires an immediate post-approval re-fetch before merging and updating. | Verify the workflow orders approval → re-fetch → merge → `update_task`; no earlier snapshot may be reused. |
| 16-07 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Make Code Mode audit logs privacy-safe | **fixed/superseded** | #16 cumulative stack | `code-mode-mcp/SKILL.md:72` requires redacted/allowlisted results and access/retention controls; `guide.md:214-216` adds tenant scope, access control, encryption, and retention. | Search both documents for every required control and run the skill evals. |
| 16-08 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Align Code Mode output by runtime | **assigned** | #19 `claude/audit-4-consolidate-refs` — Luna Tail | `code-mode-mcp/SKILL.md:11-15`, `guide.md:46-48`, and `evals/evals.json:6-14` still state a single logs/stdout behavior. | Assert JavaScript logging/stdout and Python/FastMCP returned values are separately documented and evaluated. |
| 16-09 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Split RestrictedPython and pyodide isolation rows | **fixed/superseded** | #16 cumulative stack | `code-mode-mcp/references/guide.md:101-102` has distinct AST-level and WASM rows. | Parse the table and assert two rows with distinct isolation boundaries. |
| 16-10 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Remove internal organizational context | **policy-rejected** | Policy; no repair branch | `history/2026-07-01-skills-audit.md:133,166` intentionally records the audit evidence; `enrichment-guide.md:121` documents configured Jira matching. These identifiers are not credentials or secret values. | Retain evidence/configuration per repository policy; rerun secret scanning and ensure no tokens, private URLs with credentials, or secret values are present. |
| 16-11 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Canonical TickTick priority mapping | **fixed/superseded** | #16 cumulative stack | `ticktick-enrich/SKILL.md:35,84` maps `0/1/3/5`; `enrichment-guide.md:100` uses the same user-word mapping. | Search TickTick enrichment/capture surfaces and reject mappings that write 2 or 4. |
| 16-12 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Add Haiku/Sonnet delegation guidance | **policy-rejected** | Policy; no repair branch | `docs/skill-authoring-guidelines.md:447-451` states prose model labels do not control execution; only model frontmatter or explicit subagents do. | Keep skills runtime-neutral unless they actually delegate; validate any future delegation through supported model controls. |
| 16-13 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Add metadata to all plugin Markdown | **policy-rejected** | Policy; no repair branch | Repository frontmatter validation targets `plugins/*/skills/*/SKILL.md` (`skill-validator.md:18,67`), not every reference Markdown file. The affected `commit-splitter/SKILL.md` independently has `author: klauern`. | Validate SKILL.md discovery metadata; do not invent frontmatter requirements for reference documents. |
| 16-14 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Do not print `CAPACITIES_API_TOKEN` | **fixed/superseded** | #19 cumulative stack | The flagged `capacities-api/references/examples.md` no longer exists in the cumulative tree; `capacities.py:70-74,164` prints only setup/error guidance, never the environment value. | Run a fixture with a unique token and assert it is absent from stdout/stderr. |
| 16-15 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Do not fall back to current branch as base | **fixed/superseded** by [#17 thread](https://github.com/klauern/skills/pull/17#discussion_r3725174876) | #17 `claude/audit-2-functional-fixes` — Luna Functional | The broader #16 base-resolution concern is replaced by #17's exact worktree/default-branch contract; current `commands/worktree.md:18-21` remains unsafe. | Close only with 17-06: nested-directory fixture plus exact `origin/HEAD` ancestry for new branches. |
| 16-16 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Check the staged result after staging | **assigned** | #19 `claude/audit-4-consolidate-refs` — Luna Tail | `pr-conflict-resolver/SKILL.md:108-111` lacks staged-blob marker checking after `git add`. | Require `git diff --cached --check` and `git grep --cached` marker detection in a temporary conflict fixture. |
| 16-17 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Do not overclaim ancestry merge detection | **fixed/superseded** | #16 cumulative stack | `git-optimize/references/merge_detection.md:29,34-40` limits ancestry checks to classic merges and directs squash/rebase cases to patch comparison. | Verify wording and exercise classic-merge and squash-merge fixtures. |
| 16-18 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Add author to affected conventional-commit skills | **fixed/superseded** | #16 cumulative stack | `conventional-commits/SKILL.md:5` and the affected skill frontmatters contain `author: klauern`. | Parse every changed SKILL frontmatter and verify valid YAML where fields are present. |
| 16-19 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Choose split count from logical boundaries | **assigned** | #19 `claude/audit-4-consolidate-refs` — Luna Tail | `conventional-commits/SKILL.md:37-45` still couples analysis to staged-state/count guidance. | Fixtures with staged, unstaged, and mixed changes must yield identical logical boundaries for the same diff. |
| 16-20 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Detect every unmerged index state | **assigned** | #19 `claude/audit-4-consolidate-refs` — Luna Tail | `pr-conflict-resolver/SKILL.md:94-102` retains multiple detectors instead of one canonical `git diff --name-only --diff-filter=U`. | Construct modify/delete, add/add, and rename conflict fixtures and assert every unmerged path is returned once. |
| 16-21 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Use fd and include repository-root templates | **fixed/superseded** | #16 cumulative stack | `pr-creator/SKILL.md:46` uses hidden-aware `fd ... .` and explicitly covers root templates. | Fixture templates at root, `.github/`, and `docs/`; assert all supported candidates are found. |
| 16-22 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Do not choose newer dependency versions by default | **fixed/superseded** | #16 cumulative stack | `patterns-and-strategies.md:13` says compare constraints, compatibility, security fixes, and tests—never default to newer. | Search conflict guidance for an unconditional newer-version preference. |
| 16-23 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Reuse detected PR base everywhere | **fixed/superseded** | #16 cumulative stack | `pr-creator/SKILL.md:28,33,127` resolves `BASE`, forbids hardcoded `main`, and uses the detected default consistently. | Run PR analysis fixture against a repository whose default branch is not `main`. |
| 16-24 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Correct TickTick capture priority keywords | **fixed/superseded** | #16 cumulative stack | `ticktick-capture/SKILL.md:33` and `references/examples.md:39` use `0/1/3/5` and map high to 5. | Validate all capture examples against the native priority enum. |
| 16-25 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Use configured optimization base, not `main` | **fixed/superseded** | #16 cumulative stack | `git-optimize/SKILL.md:63-65` resolves the remote default; `merge_detection.md:45-50` defines the `trim.bases`/remote-default resolution order. | Test a non-main remote default and an explicit `trim.bases` override. |
| 16-26 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Remove “Always safe” from destructive cleanup | **fixed/superseded** | #16 cumulative stack | `git-optimize/SKILL.md:119-124` limits “Always safe” to dry-run/read-only work and moves cleanup/sweep/trimall to review-first. | Search the safety matrix and confirm no ref/object deletion is labelled always safe. |
| 16-27 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Add author to GH Actions skills | **fixed/superseded** | #16 cumulative stack | `gh-actions-upgrader/SKILL.md:5` and its affected peer frontmatter contain `author: klauern`. | Parse the changed SKILL frontmatter. |
| 16-28 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Honor `trim.bases` and `trim.exclude` in aliases | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `git-optimize/references/configuration.md:28-50` still embeds unsafe parsing/deletion logic that does not reliably consume both configs. | Temporary Git fixture must protect current/default/common/configured/excluded branches and pass names after `--`. |
| 16-29 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Propagate detected runtime versions | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `devcontainer-setup/references/tool-detection.md:78-89,165-166` shows version args, but generated template placeholders do not consistently consume detected Node/Go/Ruby/Rust versions. | Generate fixtures from `.nvmrc`, `go.mod`, `.ruby-version`, and `rust-toolchain.toml`; assert exact safe versions and confirmation for ranges. |
| 16-30 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Install resolver used by firewall script | **fixed/superseded** | #16 cumulative stack | `devcontainer-setup/references/templates.md:81` installs `dnsutils`, supplying `dig`. | Build/lint the template and check `command -v dig` in the generated image. |
| 16-31 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Correct checkout fetch-depth breaking-change note | **fixed/superseded** | #16 cumulative stack | The incorrect v3→v4 fetch-depth claim is absent from `gh-actions-upgrader/SKILL.md:98-109`; guidance now requires fetching actual notes. | Search for the old claim and compare future claims to upstream release notes. |
| 16-32 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Correct the reduce example | **fixed/superseded** | #16 cumulative stack | `ci-failure-analyzer/references/examples.md:75-82` deliberately shows the missing-initial-value regression and then restores `reduce(..., 0)`. | Run the corrected example against empty and populated arrays. |
| 16-33 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Add author to CI analyzer skills | **fixed/superseded** | #16 cumulative stack | `ci-failure-analyzer/SKILL.md:5` and affected SKILL frontmatters contain `author: klauern`. | Parse the changed SKILL frontmatter. |
| 16-34 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Use a normal relative enrichment-guide link | **fixed/superseded** | #16 cumulative stack | `ticktick-enrich/SKILL.md:67,91` uses `(references/enrichment-guide.md)`. | Run the relative-link checker from the skill directory. |
| 16-35 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Warn before rewriting published history | **fixed/superseded** | #16 cumulative stack | `commit-splitter/references/splitting.md:44-45` requires checking shared/pushed status, coordination, and `--force-with-lease`. | Search reset/rebase sections and ensure the warning precedes rewrite commands. |
| 16-36 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Align dependency-upgrader PR claim | **fixed/superseded** | #16 cumulative stack | `dependency-upgrader/SKILL.md:11` says it prepares commits and leaves PR creation to the pull-requests plugin. | Compare frontmatter/body claims with executable workflow phases. |
| 16-37 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Remove unsupported Poetry lock flag | **fixed/superseded** | #16 cumulative stack | `dependency-upgrader/references/ecosystems.md:90-91` uses default `poetry lock` and reserves `--regenerate` for full resolution. | Search for `poetry lock --no-update`; validate commands against the supported Poetry major. |

### PR #16 totals

- 37 distinct findings: 33 Major + 4 Nitpick.
- 26 **fixed/superseded**.
- 7 **assigned**: 16-03, 16-08, 16-16, 16-19, 16-20, 16-28, 16-29.
- 4 **policy-rejected**: 16-01, 16-10, 16-12, 16-13.

## PR #17 — 12 inline findings plus 1 outside-diff finding

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17-01 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174855) | Keep accepted commit types aligned with policy | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `validate-commit-format.sh:47-49` still accepts/lists `revert`, while repository types list only feat/fix/docs/style/refactor/perf/test/build/ci/chore. | Shell fixture accepts every policy type and rejects `revert` and unknown types; regex and error list must match. |
| 17-02 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174857) | Add language to repository-tree fence | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `.claude/README.md:7` still opens a bare fence for the text tree. | Markdown lint; assert the opening fence is `text` and tree content is unchanged. |
| 17-03 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174860) | Quote `CLAUDE_PROJECT_DIR` in hooks | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `.claude/settings.json:32,44,49,61,73` contains unquoted path expansion. | Parse JSON and execute hook command fixtures from a temporary path containing spaces. |
| 17-04 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174863) | Export `CLAUDE_PLUGIN_ROOT` before test command | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `docs/script-development.md:195-197` assigns and expands the variable in one command, so the expansion can resolve `/scripts/...`. | Run the documented two-command example and assert the resolved path is under the plugin root. |
| 17-05 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174874) | Remove regular CLAUDE.md before symlinking | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `commands/agents-md.md:19-20` says “replace” but does not explicitly remove/rename before `ln -s`. | Temporary fixture with two regular files: merge/deduplicate, remove old file, create symlink, preserve content. |
| 17-06 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174876) | Detect branch kind and create from remote default | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `commands/worktree.md:18-21` builds a cwd-relative sibling path, suppresses errors, and falls back to caller `HEAD`. | Nested-directory fixtures cover local branch, remote-only branch, and new branch from resolved `origin/HEAD`, with visible failures. |
| 17-07 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174881) | Treat release notes as untrusted data | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `gh-actions-upgrader/SKILL.md:98-109` fetches bodies without untrusted-data delimiters, ignore-directive rules, or approval before edits/PRs. | Review a fixture release body containing prompt injection; ensure it is quoted as data and cannot authorize mutation. |
| 17-08 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174889) | Validate the complete Git alias set | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `git-optimize/SKILL.md:100-104` checks only `cleanup` and `trimall`; the command table uses more aliases. | Empty/partial/full Git-config fixtures must choose installation or raw-git fallbacks for every missing alias. |
| 17-09 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174894) | Do not default monthly maintenance to trimall | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `git-optimize/SKILL.md:72-75` still runs `git trimall` without a confirmation gate. | Documentation assertion: monthly default is dry-run, or an explicit confirmation immediately precedes trimall. |
| 17-10 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174899) | Revalidate remote refs before deletion | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `git-optimize/SKILL.md:82-87` deletes remote names without fetching/comparing the reviewed remote OID or asking for confirmation. | Race fixture changes a remote ref after preview; deletion must stop unless exact state is revalidated and confirmed. |
| 17-11 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174904) | Add bash language to pr-update fence | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `pull-requests/commands/pr-update.md:134` has a bare shell-example fence at the reviewed head. | Markdown lint and exact fence assertion; example contents unchanged. |
| 17-12 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174907) | Use one enrich priority policy | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Cumulative `ticktick-enrich/SKILL.md:84` includes none→0, but `enrichment-guide.md:100` still says “else leave as-is”; command behavior must be made explicit. | Cross-file fixture maps urgent/critical/high→5, medium→3, low→1, none→0, and preserves priority only when unstated. |
| 17-13 | [review body, outside diff](https://github.com/klauern/skills/pull/17#pullrequestreview-4870123313) | Restore metadata on gtd-contexts reference | **policy-rejected** | Policy; no repair branch | `ticktick-review/references/gtd-contexts.md:1` intentionally starts with its title; repository metadata validation targets SKILL.md files, not every reference document (`skill-validator.md:18,67`). | Keep the reference free of invented package metadata; validate its link reachability and the parent SKILL.md frontmatter instead. |

### PR #17 totals

- 13 distinct findings: 12 live inline review comments plus 1 review-body-only,
  outside-diff suggestion.
- 12 **assigned**: 17-01 through 17-12.
- 1 **policy-rejected**: 17-13.
- 17-06 supersedes PR #16 row 16-15; it is counted once in each source review's
  own total but represents one implementation repair.

## PR #17 remediation review — 6 inline findings plus 1 outside-diff finding

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17R-01 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442399) | Fail the hook-path fixture when no commands are discovered | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `.claude/hooks/tests/settings-paths.sh:10-15` lets an empty `jq` result flow through an empty loop to the success message. | Filter to non-empty string commands, explicitly reject an empty command set, and retain the path-with-spaces execution fixture. |
| 17R-02 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442401) | Fetch the remote-only fixture ref explicitly | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `worktree-command.sh:75-80` currently relies on push-side remote-tracking behavior before resolving `origin/remote/topic`. | Add an exact refspec fetch before the remote-tracking checkout and keep the separate never-fetched remote discovery case. |
| 17R-03 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442407) | Protect every explicitly selected cleanup base | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `configuration.md:48-50` protects configured/default bases but omits the resolved `$targets`, so a requested base can enter the candidate set. | Add all resolved targets to the protected set; fixture a requested `release/1` base and prove it cannot be selected. |
| 17R-04 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442418) | Fail clearly when `origin/HEAD` is missing | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `git-optimize/SKILL.md:67-68` can pass an empty branch name to `git checkout`. | Resolve a non-empty default ref or stop with actionable setup guidance before checkout, pull, or cleanup. |
| 17R-05 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442421) | Refresh and revalidate the deletion base | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | The remote deletion flow refreshes the candidate branch but checks ancestry against a potentially stale `$base_ref`. | Fetch the exact base ref immediately before deletion, recheck ancestry, require a protected/non-rewritable base, and retain branch-OID comparison, confirmation, and exact-OID lease deletion. |
| 17R-06 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442423) | Omit priority when the user did not state one | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `ticktick/commands/enrich.md:45-72` says to preserve unstated priority but its example sends `priority: 3`. | Remove the field from the unstated-priority example; fixture explicit medium separately from omitted/empty input. |
| 17R-07 | [review body, outside diff](https://github.com/klauern/skills/pull/17#pullrequestreview-4870422817) | Limit `clear-dates` guidance to clearing both dates | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `ticktick/commands/enrich.md:80` says “Clearing a date,” while the referenced command clears both `dueDate` and `startDate`. | State the two-field behavior explicitly and use the command only when both dates should be removed. |

### PR #17 remediation-review totals

- 7 distinct findings: 6 live inline review comments plus 1 review-body-only,
  outside-diff finding.
- 7 **assigned** pending the next local batch and exact-head review.

## PR #17 second remediation review — 5 inline findings

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17R2-01 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676062) | Keep the mechanical-total explanation in command order | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | The final expected-output sentence lists PR #16 categories in a different order from the preceding commands. | State `fixed/superseded 26`, `assigned 7`, then `policy-rejected 4`; preserve all numeric totals. |
| 17R2-02 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676070) | Fail closed on every remote-verification error | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | The documented deletion block does not establish a strict execution envelope or explicitly preserve every `ls-remote`/fetch failure before consuming refreshed refs. | Execute with strict error and pipeline handling; capture and validate `ls-remote`; explicitly check both initial and post-confirmation exact fetches so stale refs cannot authorize deletion. |
| 17R2-03 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676075) | Exercise the extracted deletion block for the candidate race | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | The base-race and success cases execute the documentation block, but the candidate-advance case still calls standalone `git push`. | Run the extracted block, assert it contains the exact reviewed-OID lease deletion, advance the candidate during confirmation, and prove the advanced remote ref remains. |
| 17R2-04 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676076) | Extract exactly one marked priority example | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | The priority fixture can pass with an empty or ambiguous `update_task` extraction and searches some assertions outside the extracted block. | Add a stable marker, require exactly one extraction, and scope omission/empty/medium assertions to that block. |
| 17R2-05 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676079) | Check single-date wording across all validated TickTick docs | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | The negative clear-dates wording scan does not include `commands/enrich.md` and can miss equivalent single-date phrasing. | Scan all three contract documents for any guidance that presents clear-dates as clearing only one date while retaining positive dueDate/startDate assertions. |

### PR #17 second-remediation-review totals

- 5 distinct findings: 5 live inline review comments.
- 5 **assigned** pending the next local batch and exact-head review.

## Luna whole-diff preflight after the second remediation review

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| L17-01 | Luna fixture audit | Execute the documented worktree workflow rather than a test reimplementation | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `worktree-command.sh` greps tokens, then runs its own branch-classification algorithm; the documented block can regress independently. | Mark/extract the authoritative block and execute it for local, cached-remote, unfetched-remote, and new-branch cases. |
| L17-02 | Luna fixture audit | Render runtime substitutions from the authoritative workflow | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `runtime-version-substitution.sh` reimplements detection and only checks placeholder presence. | Execute the documented/shared workflow for `.nvmrc`, `go.mod`, `.ruby-version`, and `rust-toolchain.toml`; assert exact rendered versions, no remaining placeholders, and confirmation for ambiguous ranges. |
| L17-03 | Luna fixture audit | Execute the complete TickTick priority mapping | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | The marked example handles only medium while prose asserts the full mapping. | Make one authoritative executable mapping cover urgent/critical/high, medium, low, none, and empty-input preservation; run table-driven assertions. |
| L17-04 | Luna shell audit | Refresh and verify the current remote default before new-branch creation | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `worktree.md` uses the locally cached `origin/HEAD` target/OID; a stale or renamed remote default can create a new branch from the wrong commit. | Resolve remote HEAD from the server, exact-fetch its target, verify the fetched OID, and fixture a stale/renamed cached default. |
| L17-05 | Luna shell audit | Make `trimall` fail fast between phases | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `configuration.md` separates fetch, trim, cleanup, sweep, and optimize with semicolons, so later success can mask an earlier failure or cancellation. | Guard every phase, stop on fetch/dry-run/cleanup failure or cancellation, and fixture failure propagation before destructive later phases. |

### Luna preflight totals

- 5 distinct high-confidence findings: 3 fixture-validity and 2 shell-safety.
- 5 **assigned** pending local repair and independent review.

## PR #17 third remediation review — 1 inline finding

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17R3-01 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725871086) | Scope clear-dates validation to its guidance paragraph | **assigned** | #17 `claude/audit-2-functional-fixes` — Luna Functional | `priority-mapping.sh:80-95` extracts a broad matched bullet block, so neighboring text can provide `dueDate`/`startDate` and mask a deficient clear-dates paragraph. | Extract only the paragraph associated with `/ticktick:clear-dates`, require both fields inside it, and preserve the missing-contract failure. |

### PR #17 third-remediation-review totals

- 1 distinct finding: 1 live inline review comment.
- 1 **assigned** pending local repair and exact-head review.

## Mechanical count validation

Run from the repository root:

```bash
rtk rg -c '^\| 16-[0-9]{2} \|' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 17-[0-9]{2} \|' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 16-.*\*\*fixed/superseded\*\*' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 16-.*\*\*assigned\*\*' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 16-.*\*\*policy-rejected\*\*' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 17-.*\*\*assigned\*\*' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 17-.*\*\*policy-rejected\*\*' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 17R-[0-9]{2} \|' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 17R2-[0-9]{2} \|' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| L17-[0-9]{2} \|' history/2026-08-06-coderabbit-findings-ledger.md
rtk rg -c '^\| 17R3-[0-9]{2} \|' history/2026-08-06-coderabbit-findings-ledger.md
```

Expected totals are `37`, `13`, then PR #16's `fixed/superseded 26`,
`assigned 7`, `policy-rejected 4`, and PR #17's `assigned 12`,
`policy-rejected 1`, followed by `7` first-remediation and `5`
second-remediation PR #17 findings, then `5` Luna preflight findings.
The third-remediation review adds `1` finding.
