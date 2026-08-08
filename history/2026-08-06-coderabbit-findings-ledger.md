# CodeRabbit Findings Ledger — PRs #16, #17, and #18

This is an evidence record, not a task tracker. Beads epic `klauern-skills-gon`
owns task state. Repair rows remain **assigned** until the orchestrator adds the
fixing commit SHA and revalidates the exact pushed head; no unchecked-task syntax
is used here. Rows fixed through `c77eb732a6b2952b044ebd7512aeb9942c9b7b7c`
were exercised by the cumulative fixtures. CodeRabbit invocation
`eb3df2fd-5fe9-4a04-9ce4-de0878755f74` completed at that exact head with zero
findings and a successful CodeRabbit status; the repository owner accepted that
clean exact-head result as the serial review gate evidence.

## Review scope and exact heads

| PR | CodeRabbit review | Reviewed head | Current remote head checked for evidence |
|---|---|---|---|
| #16 | [review 4869851851](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | `b4ee1808033d32ce6d5099956c1b2d48b8e7c742` | #15 cumulative head `8515964bac597b4a5110dafb1a8d28ef0ab4ca48` |
| #17 | [review 4870123313](https://github.com/klauern/skills/pull/17#pullrequestreview-4870123313) | `ac9385c6834dbd00e68e5ee9871090d6bcead869` | #17 head `ac9385c6834dbd00e68e5ee9871090d6bcead869`; downstream evidence also checked at `8515964bac597b4a5110dafb1a8d28ef0ab4ca48` |
| #17 remediation | [review 4870422817](https://github.com/klauern/skills/pull/17#pullrequestreview-4870422817) | `09ac7a8163d4587052177ddc9b3d2a586b49cc1a` | Exact reviewed remediation head; seven findings comprise six inline threads plus one review-body-only, outside-diff finding. |
| #17 remediation 2 | [review 4870703669](https://github.com/klauern/skills/pull/17#pullrequestreview-4870703669) | `8e24c8ed635f5ff5720fedf6bb0f74485d88fd86` | Exact reviewed second-remediation head; five inline findings. |
| #17 remediation 3 | [review 4870951650](https://github.com/klauern/skills/pull/17#pullrequestreview-4870951650) | `f1f311775f40dd9268a8a228671b64a28dba5513` | Exact reviewed third-remediation head; one inline finding. |
| #17 remediation 4 | [review 4871336866](https://github.com/klauern/skills/pull/17#pullrequestreview-4871336866) | `54d7083af16f93c7c3d16c55d8655b026f6c670e` | Exact reviewed fourth-remediation head; one review-body-only, outside-diff ledger finding. |
| #17 remediation 5 | [review 4871697177](https://github.com/klauern/skills/pull/17#pullrequestreview-4871697177) | `e5186bce8813d7d4d864147c553791ade293363a` | Exact reviewed fifth-remediation head; one review-body nitpick finding about disposition validation. |
| #17 remediation 6 | [clean invocation eb3df2fd](https://github.com/klauern/skills/pull/17#issuecomment-5201711315) | `c77eb732a6b2952b044ebd7512aeb9942c9b7b7c` | Exact-head incremental review completed with zero findings and successful status; CodeRabbit did not submit an empty GitHub review object. |
| #18 | [review 4889211229](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | `a0a64e66236ecf51336b7eed436ca222eef490a5` | Exact reviewed reconciled head; fourteen actionable findings assigned below. |

The intervening exact remote heads were #18
`1a36a294c2f3fb78bb8ba14964450baa141c59f5` and #19
`8f5932d5c2c5a12d25195108f8ae9162e83be578`.

CodeRabbit's incremental reviews may skip unchanged or similar files, so the
review evidence is cumulative across the exact heads above rather than a claim
that each incremental review freshly reread every earlier file. Review `4870951650`
produced `17R3-01`; its repair and the subsequent `L17-06` and `17R4-01` repairs
were included at exact reviewed head `e5186bce`. Review `4871697177` produced only
`17R5-01`; its repair was the sole change reviewed by invocation
`eb3df2fd-5fe9-4a04-9ce4-de0878755f74` at exact head `c77eb732`, which completed
with zero findings and successful status.

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
| 16-15 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Do not fall back to current branch as base | **fixed/superseded** by [#17 thread](https://github.com/klauern/skills/pull/17#discussion_r3725174876) | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`, hardened in `f1f3117`; the authoritative workflow uses an absolute repository-root sibling path, distinguishes local, cached-remote, unfetched-remote, and new branches, and creates new branches from the fetched and verified server default rather than the caller's current branch. | Shares 17-06 validation: nested local/cached/unfetched/server-default fixtures execute the documented block; reviewed at `f1f3117`. |
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
| 16-28 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Honor `trim.bases` and `trim.exclude` in aliases | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`, hardened through `f1f3117`; `configuration.md` uses formatted ref enumeration, protects configured bases/exclusions, previews candidates, confirms, and passes names after `--`. | `cleanup-alias.sh` executes the documented blocks and proves current/default/common/configured/excluded/requested bases are never selected; reviewed at `f1f3117`. |
| 16-29 | [review](https://github.com/klauern/skills/pull/16#pullrequestreview-4869851851) | Propagate detected runtime versions | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`, hardened in `f1f3117`; the authoritative rendering workflow consumes Node, Go, Ruby, and Rust detections and gates ambiguous ranges. | `runtime-version-substitution.sh` renders `.nvmrc`, `go.mod`, `.ruby-version`, and `rust-toolchain.toml` fixtures with no placeholders left; reviewed at `f1f3117`. |
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
- Initial triage: 26 **fixed/superseded**, 7 **assigned**, and 4
  **policy-rejected**, matching the requested 26/7/4 source-review disposition.
- Current cumulative state: 28 **fixed/superseded** and 5 **assigned**:
  16-03, 16-08, 16-16, 16-19, and 16-20. Rows 16-28 and 16-29 were fixed on
  #17 and reviewed at `f1f3117`.
- 4 **policy-rejected**: 16-01, 16-10, 16-12, 16-13.

## PR #17 — 12 inline findings plus 1 outside-diff finding

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17-01 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174855) | Keep accepted commit types aligned with policy | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; repository policy, hook regex, and hook error text consistently include the eleven accepted types, including `revert`. | `validate-commit-format.sh` fixture accepts all eleven policy types and rejects unknown types; present at reviewed head `f1f3117`. |
| 17-02 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174857) | Add language to repository-tree fence | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; `.claude/README.md` opens the repository tree as `text`. | Markdown/fence assertion passed at reviewed head `f1f3117`. |
| 17-03 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174860) | Quote `CLAUDE_PROJECT_DIR` in hooks | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; every hook command quotes the project-root expansion. | `settings-paths.sh` executes all discovered nonempty commands from a path containing spaces; present at `f1f3117`. |
| 17-04 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174863) | Export `CLAUDE_PLUGIN_ROOT` before test command | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; the documentation assigns the variable before expanding it in the following command. | Documented-command fixture resolves beneath the plugin root at reviewed head `f1f3117`. |
| 17-05 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174874) | Remove regular CLAUDE.md before symlinking | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; migration explicitly removes the regular file before `ln -s`. | Temporary two-file migration preserves merged content and creates the symlink; present at `f1f3117`. |
| 17-06 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174876) | Detect branch kind and create from remote default | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`, hardened in `f1f3117`; the authoritative workflow uses an absolute root sibling and distinguishes local, remote-only, and new branches from verified remote HEAD. | Nested local/cached/unfetched/server-default fixtures execute the documented block; reviewed at `f1f3117`. |
| 17-07 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174881) | Treat release notes as untrusted data | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; fetched notes are delimited as untrusted data, directives are ignored, and approval is required before mutation. | Prompt-injection fixture and skill validation passed; present at reviewed head `f1f3117`. |
| 17-08 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174889) | Validate the complete Git alias set | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; the workflow validates every alias it invokes and falls back to explicit commands when unavailable. | Empty/partial/full Git-config fixtures passed at reviewed head `f1f3117`. |
| 17-09 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174894) | Do not default monthly maintenance to trimall | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; monthly maintenance previews and requires explicit confirmation before destructive phases. | Cleanup/trimall confirmation and cancellation fixtures passed at reviewed head `f1f3117`. |
| 17-10 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174899) | Revalidate remote refs before deletion | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`, hardened by `8e24c8e` and `afb3b00`; deletion verifies candidate/base OIDs, refreshes the base, confirms, and uses an exact-OID lease. | Success, base-rewrite, and candidate-advance fixtures execute the documented block; reviewed at `f1f3117`. |
| 17-11 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174904) | Add bash language to pr-update fence | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`; the shell example fence is `bash`. | Exact fence assertion passed at reviewed head `f1f3117`. |
| 17-12 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725174907) | Use one enrich priority policy | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `09ac7a8`, hardened through `f1f3117`; one executable mapping covers 5/3/1/0 and preserves unstated priority. | Table-driven command/skill/reference contract fixture passed at reviewed head `f1f3117`. |
| 17-13 | [review body, outside diff](https://github.com/klauern/skills/pull/17#pullrequestreview-4870123313) | Restore metadata on gtd-contexts reference | **policy-rejected** | Policy; no repair branch | `ticktick-review/references/gtd-contexts.md:1` intentionally starts with its title; repository metadata validation targets SKILL.md files, not every reference document (`skill-validator.md:18,67`). | Keep the reference free of invented package metadata; validate its link reachability and the parent SKILL.md frontmatter instead. |

### PR #17 totals

- 13 distinct findings: 12 live inline review comments plus 1 review-body-only,
  outside-diff suggestion.
- 12 **fixed/superseded**: 17-01 through 17-12, implemented in `09ac7a8`
  and retained through reviewed head `f1f3117`.
- 1 **policy-rejected**: 17-13.
- 17-06 supersedes PR #16 row 16-15; it is counted once in each source review's
  own total but represents one implementation repair.

## PR #17 remediation review — 6 inline findings plus 1 outside-diff finding

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17R-01 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442399) | Fail the hook-path fixture when no commands are discovered | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `8e24c8e`; the fixture filters nonempty commands, rejects zero results, and counts executed hooks. | Empty-command and path-with-spaces cases pass; reviewed at `f1f3117`. |
| 17R-02 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442401) | Fetch the remote-only fixture ref explicitly | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `8e24c8e`; the fixture exact-fetches `origin/remote/topic` before deleting its local peer. | Cached and never-fetched remote cases execute the documented block; reviewed at `f1f3117`. |
| 17R-03 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442407) | Protect every explicitly selected cleanup base | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `8e24c8e`; resolved targets join the protected set before candidate enumeration. | A requested `release/1` base is never selected in `cleanup-alias.sh`; reviewed at `f1f3117`. |
| 17R-04 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442418) | Fail clearly when `origin/HEAD` is missing | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `8e24c8e`; default resolution must produce a nonempty branch before checkout/pull/cleanup. | Missing-default fixture fails before mutation with actionable guidance; reviewed at `f1f3117`. |
| 17R-05 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442421) | Refresh and revalidate the deletion base | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `8e24c8e`, hardened by `afb3b00`; both candidate and protected base are exact-fetched and ancestry is rechecked immediately before lease deletion. | Base-rewrite and candidate-advance races preserve the remote branch; reviewed at `f1f3117`. |
| 17R-06 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725442423) | Omit priority when the user did not state one | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `8e24c8e`; the unstated-priority example omits the field and explicit medium is separate. | Exact marked-block fixture proves empty/unstated preservation; reviewed at `f1f3117`. |
| 17R-07 | [review body, outside diff](https://github.com/klauern/skills/pull/17#pullrequestreview-4870422817) | Limit `clear-dates` guidance to clearing both dates | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `8e24c8e`; all three contract documents state that the command removes both `dueDate` and `startDate`. | Positive and single-date negative contract checks pass; reviewed at `f1f3117`. |

### PR #17 remediation-review totals

- 7 distinct findings: 6 live inline review comments plus 1 review-body-only,
  outside-diff finding.
- 7 **fixed/superseded**, implemented in `8e24c8e` and retained through
  reviewed head `f1f3117`.

## PR #17 second remediation review — 5 inline findings

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17R2-01 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676062) | Keep the mechanical-total explanation in command order | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `afb3b00`; the historical 26/7/4 explanation follows the command order and current-state totals are separate. | Mechanical counts and ledger audit pass; present at reviewed head `f1f3117`. |
| 17R2-02 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676070) | Fail closed on every remote-verification error | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `afb3b00`; the extracted deletion envelope uses strict error/pipeline handling and validates `ls-remote` plus both exact fetches. | Injected verification failures stop before deletion; reviewed at `f1f3117`. |
| 17R2-03 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676075) | Exercise the extracted deletion block for the candidate race | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `afb3b00`; all race cases execute the extracted block and assert the exact reviewed-OID lease command. | Candidate advance is preserved remotely and the workflow fails; reviewed at `f1f3117`. |
| 17R2-04 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676076) | Extract exactly one marked priority example | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `afb3b00`; stable markers yield exactly one example and all assertions are scoped to it. | Missing/duplicate/empty/medium mutations fail as intended; reviewed at `f1f3117`. |
| 17R2-05 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725676079) | Check single-date wording across all validated TickTick docs | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `afb3b00`; the negative scan covers command, skill, and reference guidance while positive checks require both fields. | Single-date variants fail across all three documents; reviewed at `f1f3117`. |

### PR #17 second-remediation-review totals

- 5 distinct findings: 5 live inline review comments.
- 5 **fixed/superseded**, implemented in `afb3b00` and retained through
  reviewed head `f1f3117`.

## Luna whole-diff preflight after the second remediation review

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| L17-01 | Luna fixture audit | Execute the documented worktree workflow rather than a test reimplementation | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `f1f3117`; `worktree-command.sh` extracts and executes the authoritative marked workflow. | Local, cached-remote, unfetched-remote, and new-branch cases pass at reviewed head `f1f3117`. |
| L17-02 | Luna fixture audit | Render runtime substitutions from the authoritative workflow | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `f1f3117`; the runtime fixture extracts the authoritative detection/rendering workflow. | Four ecosystems render exact versions with no placeholders, and ambiguous ranges require confirmation. |
| L17-03 | Luna fixture audit | Execute the complete TickTick priority mapping | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `f1f3117`; the authoritative example covers high/medium/low/none and unstated preservation. | Table-driven mapping and documentation-scope mutations pass at reviewed head `f1f3117`. |
| L17-04 | Luna shell audit | Refresh and verify the current remote default before new-branch creation | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `f1f3117`; new-branch creation resolves server HEAD, exact-fetches the target, and verifies its OID. | Stale and renamed cached-default fixtures descend from the server default. |
| L17-05 | Luna shell audit | Make `trimall` fail fast between phases | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `f1f3117`; every trimall phase is guarded and cancellation/failure stops later destructive phases. | Fetch, dry-run, cleanup, cancellation, and later-phase failure fixtures pass. |

### Luna preflight totals

- 5 distinct high-confidence findings: 3 fixture-validity and 2 shell-safety.
- 5 **fixed/superseded** in `f1f3117`; focused fixtures and an independent Luna
  whole-diff review passed before CodeRabbit review `4870951650`.

## PR #17 third remediation review — 1 inline finding

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17R3-01 | [thread](https://github.com/klauern/skills/pull/17#discussion_r3725871086) | Scope clear-dates validation to its guidance paragraph | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `f079d0e`; the fixture extracts only the associated Markdown paragraph/row and rejects neighboring-text substitution. | Focused fixture, missing-contract mutation, neighboring-text mutation, ShellCheck, diff check, and Luna audit passed; included at exact reviewed head `e5186bce` in review `4871697177`. |

### PR #17 third-remediation-review totals

- 1 distinct finding: 1 live inline review comment.
- 1 **fixed/superseded** in `f079d0e`; included at exact reviewed head
  `e5186bce` in review `4871697177`.

## Luna post-review fixture audit

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| L17-06 | Luna fixture audit | Isolate alias sequencing from executable helper shadowing | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Functional | Fixed in `4edd30d` and hardened in `d00cfe1`; helper creation follows top-level alias assertions, nested calls route through the injection shim, and `git -C` is decoded deterministically. | Cleanup sequencing/failure fixtures, cumulative fixtures, ShellCheck, and Luna review passed; included at exact reviewed head `e5186bce` in review `4871697177`. |

### Luna post-review totals

- 1 distinct fixture finding, **fixed/superseded** in `4edd30d` and `d00cfe1`;
  included at exact reviewed head `e5186bce` in review `4871697177`.

## PR #17 fourth remediation review — 1 outside-diff finding

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17R4-01 | [review body, outside diff](https://github.com/klauern/skills/pull/17#pullrequestreview-4871336866) | Synchronize finding 16-15 with finding 17-06 | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Ledger | Fixed in `e5186bce`; row 16-15 cites the `09ac7a8` repair, `f1f3117` hardening, absolute sibling placement, explicit branch classification, and verified server-default ancestry. | Luna ledger audit and mechanical counts passed; the supersession link was retained and the repair was included at exact reviewed head `e5186bce` in review `4871697177`. |

### PR #17 fourth-remediation-review totals

- 1 distinct finding: 1 review-body-only, outside-diff ledger inconsistency.
- 1 **fixed/superseded** in `e5186bce`; reviewed at that exact head in review
  `4871697177`.

## PR #17 fifth remediation review — 1 nitpick finding

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 17R5-01 | [review body, nitpick](https://github.com/klauern/skills/pull/17#pullrequestreview-4871697177) | Validate remediation dispositions, not only row counts | **fixed/superseded** | #17 `claude/audit-2-functional-fixes` — Luna Ledger Round 5 | Fixed in `c77eb732`; the mechanical section checks row counts and expected dispositions for initial #17, 17R, 17R2, Luna preflight, 17R3, L17-06, 17R4, and 17R5 independently. | Complete ledger count/disposition validation and `git diff --check` passed before exact-head CodeRabbit invocation `eb3df2fd-5fe9-4a04-9ce4-de0878755f74`, which completed with zero findings and successful status. |

### PR #17 fifth-remediation-review totals

- 1 distinct finding: 1 review-body nitpick about ledger validation coverage.
- 1 **fixed/superseded** in `c77eb732`; exact-head CodeRabbit invocation
  `eb3df2fd-5fe9-4a04-9ce4-de0878755f74` completed with zero findings and
  successful status.

## PR #18 full review — 14 actionable findings

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 18R-01 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Make ledger validation commands assert expected counts and dispositions, including the duplicated evidence entry | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger and PR Creator | Fixed in `56fa766`; `history/tests/validate-coderabbit-ledger.sh` fails closed on every historical count/disposition group, PR #18 row validity, and duplicate IDs. | Baseline validation and copied-ledger duplicate-ID/disposition mutations pass through `validate-coderabbit-ledger-test.sh`. |
| 18R-02 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Inspect every untracked file before commit staging and message composition | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commands and CI | Fixed in `56fa766`; `commit-push.md` inventories untracked paths and requires reading every text file or inspecting binary metadata before staging or composing messages, while retaining full tracked-diff review. | Root verified the ordered tracked/untracked gate with focused assertions and `git diff --check`. |
| 18R-03 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Use the namespaced `/dev-utilities:gh-checks` command in its Usage example | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commands and CI | Fixed in `56fa766`; `commands/gh-checks.md` uses `/dev-utilities:gh-checks` in the heading and executable usage block. | Root exact-match assertion and `git diff --check` passed. |
| 18R-04 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Add `bash` to the opening GitHub CLI fence in CI analyzer examples | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commands and CI | Fixed in `56fa766`; the matrix-job GitHub CLI example opens with a `bash` fence. | Root fence assertion and `git diff --check` passed. |
| 18R-05 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Describe `gh run view --job <databaseId>` as failed-log retrieval, not name-based matrix selection | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commands and CI | Fixed in `56fa766`; `log-parsing.md` separates choosing a displayed job from retrieving its failed logs by copied numeric `databaseId`. | Root contract assertion and `git diff --check` passed. |
| 18R-06 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | State that targeted job reruns include dependent jobs | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commands and CI | Fixed in `56fa766`; the skill, workflows, examples, and test matrix consistently state that the selected child and dependent jobs rerun while sibling matrix children do not. | Root cross-document assertions and `git diff --check` passed. |
| 18R-07 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Add `bash` to the merge-conflict commit example fence | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commands and CI | The exact reviewed `a0a64e6` tree already used `bash` for the flagged fence, so no repair edit was necessary. | Root verified the current and reviewed blob at `plugins/pull-requests/commands/merge-conflicts.md:22`; fence assertion passed. |
| 18R-08 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Move review-thread GraphQL implementation from the thin command into an installed-context-safe script | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna GraphQL | Fixed in `56fa766`; `scripts/review_threads.py` owns query, pagination, filtering, and JSON output, while the thin command resolves `CLAUDE_PLUGIN_ROOT` or the source plugin root and passes explicit repository/PR inputs. | Root reran two focused unittest cases, Python compilation, path assertions, and `git diff --check`. |
| 18R-09 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Paginate both review threads and nested comment connections before filtering | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna GraphQL | Fixed in `56fa766`; the helper exhausts `reviewThreads` pages and every thread's nested `comments` pages before applying outdated/resolved filtering. | Mocked fixtures cover two thread pages plus nested pages for open and filtered-out outdated threads; root reran the focused unittest successfully. |
| 18R-10 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Fail closed on operational `gh pr view` errors while allowing only explicit no-PR continuation | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger and PR Creator | Fixed in `56fa766`; `pr-creator/SKILL.md` uses a successful empty `gh pr list` result as the only no-PR case and propagates operational failures. | `workflow-safety.sh` executes existing-PR, explicit no-PR, and authentication-failure cases. |
| 18R-11 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Verify or fetch `origin/$BASE` before PR log/diff analysis | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger and PR Creator | Fixed in `56fa766`; preflight validates the base name, force-refreshes `refs/remotes/origin/$BASE`, and verifies it as a commit before Phase 2. | `workflow-safety.sh` proves fetch-before-verify and refreshes both missing and stale base fixtures. |
| 18R-12 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Use unique temporary files and collision-safe body serialization for PR create/update | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger and PR Creator | Fixed in `56fa766`; PR create and update use `mktemp`, `printf`, and `EXIT` cleanup traps instead of predictable paths and fixed heredocs. | Executed create/update blocks preserve `BODY`, `EOF`, backticks, and literal command-substitution text and remove both body files. |
| 18R-13 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Propagate requested draft state and apply labels/assignees only when permitted and requested | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger and PR Creator | Fixed in `56fa766`; creation propagates explicit `PR_DRAFT`, defaults metadata arrays empty, and permission-gates requested labels/assignees. | Minimal and full-option executable fixtures prove omission by default and requested draft/metadata propagation. |
| 18R-14 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889211229) | Express overdue TickTick filtering as an explicit start-of-today midnight boundary | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commands and CI | Fixed in `56fa766`; `inbox.md` calls for `filter_tasks` with `endDate` set explicitly to the start of today at midnight while preserving today and `next7day` queries. | Root contract assertion and `git diff --check` passed. |

### PR #18 full-review totals

- 14 distinct actionable findings, all **fixed/superseded** in `56fa766` after
  independent root verification.

## PR #18 second full review — 8 actionable findings

Exact reviewed head: `34de155449bd3f5f5ab0979c9be218f4e65f5c4b`.
Submitted CodeRabbit review: [4889772554](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554).
Full-review invocation: `959f86cb-008f-41b3-8cee-7ef474331cbf`.

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 18R2-01 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554) | Correct the documented Luna preflight total so it agrees with the six `L17-*` rows and validator expectations | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger Round 2 | Fixed in `c649f18`; the mechanical prose now distinguishes the first five `L17-*` findings at `f1f3117` from `L17-06` at `e5186bce`. | Root reran baseline and mutation ledger validation, ShellCheck, and `git diff --check`; all passed without changing other historical totals. |
| 18R2-02 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554) | Validate the exact `18R-01` through `18R-14` ID set and add a renamed-ID mutation fixture | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger Round 2 | Fixed in `c649f18`; the validator requires every `18R-01` through `18R-14` and `18R2-01` through `18R2-08` exactly once; mutations rename the final ID in each set. | Root independently reproduced both missing-ID failures, baseline/mutation suites, ShellCheck, and `git diff --check`. |
| 18R2-03 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554) | Treat successful `git push` exit status as remote acceptance and reserve `git status` for local cleanliness | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Workflow Round 2 | Fixed in `c649f18`; `commit-push.md` makes zero push exit status the remote-acceptance proof and uses status only for local cleanliness/tracking. | Root reran the focused executable guidance test, ShellCheck, and `git diff --check`. |
| 18R2-04 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554) | Use `git commit` to complete merges and `git rebase --continue` to continue rebases | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Workflow Round 2 | Fixed in `c649f18`; `merge-conflicts.md` now gives operation-specific merge and rebase completion commands. | Root reran the focused merge/rebase guidance test, ShellCheck, and `git diff --check`. |
| 18R2-05 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554) | Apply the required uv script header, complete Python type annotations, and Black formatting to `test_review_threads.py` | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Python Round 2 | Fixed in `c649f18`; the test uses the uv inline script header, complete generics/return annotations, and Black formatting. | Root reran Black check, Python compilation, and both mocked pagination unittests with isolated caches. |
| 18R2-06 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554) | Remove the conflicting automatic-label rule or make inferred labels suggestions requiring explicit approval | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Workflow Round 2 | Fixed in `c649f18`; inferred labels are preview-only suggestions and only explicitly requested labels populate creation arguments. | Root reran the workflow-safety fixture proving inferred labels are omitted while requested labels remain supported. |
| 18R2-07 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554) | Preserve the before/after preview and explicit approval gate in the TickTick enrichment priority example | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna TickTick Round 2 | Fixed in `c649f18`; the example previews before/after, requests explicit approval, and writes only after approval. | Root executed positive and rejected-approval fixture paths and proved no update occurs before or after a rejection. |
| 18R2-08 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889772554) | Use today's local midnight as the exact overdue `endDate` in the Today command | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna TickTick Round 2 | Fixed in `c649f18`; Today and Inbox now share the exact local-midnight boundary while retaining parallel fetch instructions. | Root reran the whitespace-normalized cross-command contract fixture, ShellCheck, and `git diff --check`. |

### PR #18 second-full-review totals

- 8 distinct actionable findings, all **fixed/superseded** in repair commit
  `c649f18aa131c8f85100591f4f13f2d1f184b5c2` after Luna implementation and
  independent root verification.

## PR #18 third full review — 8 actionable findings

Exact reviewed head: `fca9b57e059ef993d7a3bd06073938e17737465b`.
Submitted CodeRabbit review: [4889943744](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744).
Full-review invocation: `2191ddad-e8b0-43b2-ba86-fc5aa14e4100`.

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| 18R3-01 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744) | Remove the stale hard-coded “20” validator-assertion total from the ledger evidence | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger Round 3 | Repair implemented in the current batch; the evidence now says complete ledger count/disposition validation instead of a stale assertion total. Exact repair SHA will be recorded in the follow-up evidence commit. | Root reran baseline/mutation validation, ShellCheck, the cumulative matrix, and `git diff --check`. |
| 18R3-02 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744) | Require exact `L17-01` through `L17-06` IDs and add an `L17-06` renamed-ID mutation | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Ledger Round 3 | Repair implemented in the current batch; the validator requires each `L17-01` through `L17-06` exactly once and the mutation renames `L17-06` to `L17-99`. Exact repair SHA will be recorded in the follow-up evidence commit. | Root independently reproduced the missing-ID failure and reran baseline/mutation validation plus ShellCheck. |
| 18R3-03 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744) | Select `git push` only when upstream tracking exists; otherwise use `git push -u origin HEAD` | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commits Round 3 | Repair implemented in the current batch; the extracted push block checks `@{upstream}`, selects the correct command, preserves status 42 on either push failure, and skips local status after failure. Exact repair SHA will be recorded in the follow-up evidence commit. | Root executed tracked/untracked upstream paths and both failure paths, then reran ShellCheck and the cumulative matrix. |
| 18R3-04 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744) | Keep `commit-push.md` within the repository thin-command contract | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Commits Round 3 | Repair implemented in the current batch; `commit-push.md` is 28 lines and delegates analysis, splitting, staging, message composition, and commit creation to `conventional-commits`. Exact repair SHA will be recorded in the follow-up evidence commit. | Root verified the authoritative 15–30-line policy, executable delegation/structure fixture, and full cumulative matrix. |
| 18R3-05 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744) | Require confirmation of detected gateway/MCP domains and proposed exact versions before devcontainer scaffolding | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Dev/PR Round 3 | Repair implemented in the current batch; detection is followed by an explicit confirmation gate before generation. Exact repair SHA will be recorded in the follow-up evidence commit. | Root executed the order-sensitive guidance fixture, existing runtime fixture, ShellCheck, and the cumulative matrix. |
| 18R3-06 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744) | Describe `gh run rerun --job` as rerunning the selected job and its dependencies, not dependent jobs | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Dev/PR Round 3 | Repair implemented in the current batch; all cited CI analyzer sites now use selected-job-and-dependencies wording. Exact repair SHA will be recorded in the follow-up evidence commit. | Root executed the cross-file contract fixture, ShellCheck, and the cumulative matrix. |
| 18R3-07 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744) | Align merge/rebase support across the command, delegated conflict-resolver skill, and test | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Dev/PR Round 3 | Repair implemented in the current batch; command, delegated skill, reference, and fixture consistently support active merges only. Exact repair SHA will be recorded in the follow-up evidence commit. | Root executed the cross-layer merge-only fixture, verified abort/commit semantics, and reran the cumulative matrix. |
| 18R3-08 | [review](https://github.com/klauern/skills/pull/18#pullrequestreview-4889943744) | Use portable `mktemp` templates with `.md` before the trailing `XXXXXX` at both PR body sites | **fixed/superseded** | #18 `claude/audit-3-thin-commands` — Luna Dev/PR Round 3 | Repair implemented in the current batch; both templates use `pr-body.md.XXXXXX`. Exact repair SHA will be recorded in the follow-up evidence commit. | Root executed minimal/full create and update paths, proving six-character expansion, three unique paths, cleanup, and full workflow safety. |

### PR #18 third-full-review totals

- 8 distinct actionable findings, all **fixed/superseded** after Luna
  implementation and independent root verification; exact repair SHA remains
  pending orchestration.

## Luna cumulative release preflight after PR #18 review

| ID | Source | Finding | Validity / disposition | Owning PR / branch | Current evidence / location | Planned validation or rationale |
|---|---|---|---|---|---|---|
| L18-01 | Luna release-checker execution | Document all six registered plugins in `AGENTS.md` | **assigned** | #15 `claude/skills-audit-optimization-cejr55` — Luna Release Docs | The #18 cumulative marketplace registers `ticktick` and `agent-patterns`, but `AGENTS.md` does not mention either plugin; the other release structure, frontmatter, line-limit, and relative-link checks passed. | Keep #15 frozen until its parent gates complete; at the #15 stage, update the architecture and key-file inventory, rerun the six-plugin release checker, and preserve exact marketplace/command/skill counts. |

### Luna PR #18 release-preflight totals

- 1 valid downstream documentation finding, **assigned** to the frozen #15
  documentation stage pending its parent review gates.

## Mechanical count validation

Run from the repository root:

```bash
bash history/tests/validate-coderabbit-ledger.sh
bash history/tests/validate-coderabbit-ledger-test.sh
```

The validator compares every stable group to its expected count and disposition,
checks the exact `L17-01` through `L17-06`, `18R-01` through `18R-14`,
`18R2-01` through `18R2-08`, and in-progress `18R3-01` through `18R3-08` ID
sets with valid current repair dispositions, and rejects duplicate IDs. The mutation
fixtures duplicate the `17R5-01` evidence row, change its disposition, rename
`L17-06` to `L17-99`, rename `18R-14` to `18R-99`, and rename `18R2-08` to
`18R2-99`; every mutation must fail validation.

Expected current totals are `37`, `13`, then PR #16's
`fixed/superseded 28`, `assigned 5`, `policy-rejected 4`, and PR #17's
`fixed/superseded 12`, `policy-rejected 1`, followed by `7`
first-remediation, `5` second-remediation, and `6` cumulative `L17-*` Luna
findings. The first five Luna findings are fixed/superseded at reviewed head
`f1f3117`; the sixth is the post-review Luna audit fixed/superseded at exact
reviewed head `e5186bce`. The third-remediation and fourth-remediation reviews
each add `1` fixed/superseded finding included at `e5186bce`. The
fifth-remediation review adds `1` fixed/superseded
disposition-validation finding at `c77eb732`; exact-head CodeRabbit invocation
`eb3df2fd-5fe9-4a04-9ce4-de0878755f74` completed with zero findings and
successful status. The original PR #16 source-review triage remains recorded
above as `26/7/4`. PR #18 has `14` original-review and `8` second-review
findings, all fixed/superseded; the single downstream `L18-*` finding remains
assigned to the frozen #15 documentation stage. Its `8` third-review findings
are fixed/superseded in the current serialized repair batch; exact repair SHA
remains pending orchestration.
