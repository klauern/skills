---
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Agent, Skill
description: Autonomous multi-task TDD work loop — runs N tasks (default 5) or M minutes (default 60), test-first, with structured deferral and a Confluence-ready session log
---
# /bd-work-loop

Autonomous multi-task TDD loop. Runs until one of the stop conditions fires. **Do NOT stop the session after the first task** — always return to task discovery and continue unless a stop condition fires.

## Usage

```
/bd-work-loop                        # default: 5 tasks, 60 minutes
/bd-work-loop --tasks=3              # stop after 3 completed tasks
/bd-work-loop --minutes=30           # stop after 30 minutes
/bd-work-loop --tasks=10 --minutes=90
```

Parse `$ARGUMENTS` for `--tasks=N` (default 5) and `--minutes=M` (default 60).

---

## Phase 0: Session Initialization

### 0.1 Parse parameters and record start time

```bash
mkdir -p ~/.cache/bd-work-loop
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
SESSION_LOG="$HOME/.cache/bd-work-loop/$TIMESTAMP.md"
START_EPOCH=$(date +%s)
```

Record `$TIMESTAMP`, `$SESSION_LOG`, `$START_EPOCH`, `TASK_LIMIT` (from --tasks, default 5), `MINUTE_LIMIT` (from --minutes, default 60). Also initialize counters: `COMPLETED_COUNT=0`, `CONSECUTIVE_DEFERRALS=0`.

### 0.2 Detect test stack

Before claiming any task, detect what test tooling is available.

```bash
# Python / pytest — prefer uv run if uv.lock or [tool.uv] present, else poetry run, else python -m
if [ -f uv.lock ] || grep -q '\[tool.uv\]' pyproject.toml 2>/dev/null; then
  PYTEST_CMD="uv run pytest"
elif [ -f poetry.lock ]; then
  PYTEST_CMD="poetry run pytest"
elif [ -f pytest.ini ] || [ -f setup.cfg ] || grep -q '\[tool.pytest' pyproject.toml 2>/dev/null; then
  PYTEST_CMD="python -m pytest"
fi
[ -n "$PYTEST_CMD" ] && echo "pytest via: $PYTEST_CMD"

# TLA+ specs
find . -name "*.tla" -not -path "./.git/*" | head -1

# Go tests
[ -f go.mod ] && echo "go"

# Node / bun tests
[ -f package.json ] && grep -q '"test"' package.json 2>/dev/null && echo "js (bun test or npm test)"
```

Record detected stacks and the resolved `$PYTEST_CMD`. If none are detected, note "no test stack found" in the session log and skip test runs for the session — do not treat absence as a failure.

### 0.3 Run baseline test suite

**Before claiming any task**, run the full detected test suite once and record as `BASELINE`.

```bash
# pytest baseline (use $PYTEST_CMD resolved in Phase 0.2)
$PYTEST_CMD --tb=short -q 2>&1 | tail -20

# TLA+ baseline (if .tla files found and tlc is in PATH)
for spec in $(find . -name "*.tla" -not -path "./.git/*"); do
  tlc "$spec" 2>&1 | tail -10
done

# Go baseline
go test ./... 2>&1 | tail -20
```

If the baseline itself has failures, **record them as pre-existing** and continue — do not stop. The regression trigger is "a test that PASSED in baseline now FAILS after a commit," not any failure.

### 0.4 Initialize session log

Write `$SESSION_LOG`:

```markdown
# BD Work Loop Session

Started: <ISO timestamp>
Limits: <TASK_LIMIT> tasks, <MINUTE_LIMIT> minutes
Repo: <git remote get-url origin or pwd>
Test stack: <detected stacks or "none">

## Baseline
<baseline output: pass/fail counts per stack>

---
```

---

## Phase 1: Loop Guard (evaluate before every iteration)

Before starting each iteration, check ALL stop conditions. **If any fire, jump to Phase 5 immediately.**

| Condition | Check |
|---|---|
| Tasks limit reached | `COMPLETED_COUNT >= TASK_LIMIT` |
| Time limit reached | `$(date +%s) - START_EPOCH >= MINUTE_LIMIT * 60` — check BEFORE starting a task, never mid-iteration |
| Test regression | `REGRESSION_STOP == true` |
| Lint failure | `LINT_STOP == true` |
| Two consecutive deferrals | `CONSECUTIVE_DEFERRALS >= 2` |

If no condition fires: continue to Phase 2.

---

## Phase 2: Task Discovery

### 2.1 Check for in-progress work

```bash
bd list --status=in_progress --limit 1
```

If an in-progress task exists, use it — it was started in a prior session.

### 2.2 Pick highest-priority ready task

```bash
bd ready --limit 1
```

If a ready task exists, select it (already sorted by priority).

### 2.3 Handle no available work

```bash
bd list --status=open
```

- No tasks at all → append `## STOP: No tasks found` to session log, jump to Phase 5 with `[BD-WORK-LOOP:NO_TASKS]`
- All tasks blocked → append `## STOP: All tasks blocked` (list blockers) to session log, jump to Phase 5 with `[BD-WORK-LOOP:ALL_BLOCKED]`

---

## Phase 3: Defer Guard

Before claiming the task, evaluate whether it is safe to execute autonomously. Read `bd show <task-id>` carefully.

### Defer signals (any one is sufficient to defer)

**Architectural signals** — task needs a design decision:
- Description contains: "design decision", "RFC", "needs discussion", "TBD", "approach unclear", "choose between", "which library", "schema change", "breaking change", "data migration"
- Task type is `epic` with no subtasks

**Ambiguous scope signals** — no clear definition of done:
- Description is under 20 words with no acceptance criteria
- Description is only a question (ends with `?`)
- No files or components mentioned and no acceptance criteria set on the issue

**Destructive change signals** — irreversible or high blast-radius:
- Description contains: "rm -rf", "drop table", "truncate", "delete all", "force push", "reset --hard", "nuke", "wipe"
- Task affects CI/CD pipeline configs (`*.yml` in `.github/workflows/` or `.gitlab-ci.yml`)
- Task involves credentials, secrets, or auth token rotation

### If deferring

```bash
bd update <task-id> --notes "DEFERRED by bd-work-loop $(date +%Y-%m-%dT%H:%M): <specific reason — which signal fired>. Manual review required before this task can be automated."
```

Append to session log:
```markdown
## Task <N>: <task-id> — DEFERRED
Title: <task title>
Defer reason: <signal that fired>
Beads note: added
```

Increment `CONSECUTIVE_DEFERRALS`. Then **return to Phase 1** (loop guard checks consecutive-defer stop condition).

---

## Phase 4: TDD Implementation Cycle

### 4.1 Claim the task

```bash
bd update <task-id> --status in_progress
```

Reset `CONSECUTIVE_DEFERRALS=0`.

### 4.2 Context exploration

Launch **up to 3 Agent subagents in parallel** (`subagent_type: Explore`) to understand codebase context relevant to this task. Extract file paths, keywords, and related issues from `bd show <task-id>`. Wait for all explorations before proceeding to test writing.

### 4.3 Write the failing test (Red)

Before writing any implementation code:

1. Identify the smallest meaningful test that would pass when the task is complete.
2. Write the test to the appropriate test file (create one if no test file exists for the module).
3. Run the test and confirm it **fails** (red state). If it passes immediately, the task may already be done — verify, close with a note, and return to Phase 1.

```bash
$PYTEST_CMD path/to/test_file.py::test_name -v 2>&1 | tail -20
```

Record: test file path, test name, failure message.

### 4.4 Implement to green

Write the minimum code to make the failing test pass. Follow patterns from exploration. Use `Edit` and `Write` tools for file modifications.

### 4.5 Confirm green

```bash
$PYTEST_CMD path/to/test_file.py::test_name -v 2>&1 | tail -20
```

If still failing after two implementation attempts:
- `bd update <task-id> --notes "DEFERRED by bd-work-loop: could not make test green after 2 attempts. Test: <name>. Last error: <error summary>"`
- Revert working-tree changes: `git checkout -- .`
- Increment `CONSECUTIVE_DEFERRALS`, append to session log, return to Phase 1

### 4.6 Run full test suite (regression check)

Run the complete test suite and compare against `BASELINE`:

```bash
$PYTEST_CMD --tb=short -q 2>&1 | tail -30
for spec in $(find . -name "*.tla" -not -path "./.git/*"); do tlc "$spec" 2>&1 | tail -10; done
```

**On regression** (a baseline-passing test now fails):
1. Do NOT commit.
2. Attempt one auto-fix (run the project's formatter/linter: `ruff check --fix`, `gofumpt -w .`, etc.).
3. Re-run. If regression persists:
   - Revert: `git checkout -- .`
   - `bd update <task-id> --notes "DEFERRED by bd-work-loop: implementation caused test regression. Failing: <test names>. Reverted."`
   - Append to session log with regression details
   - Set `REGRESSION_STOP=true`, jump to Phase 5

### 4.7 Run linter

```bash
# Detect and run configured linter
[ -f .pre-commit-config.yaml ] && pre-commit run --all-files 2>&1 | tail -20
grep -q ruff pyproject.toml 2>/dev/null && ruff check . 2>&1 | tail -20
[ -f .golangci.yml ] && golangci-lint run 2>&1 | tail -20
```

On non-zero lint exit:
- Attempt auto-fix (`ruff check --fix`, `gofumpt -w .`, etc.)
- Re-run. If still failing: do NOT commit. Set `LINT_STOP=true`, jump to Phase 5.

### 4.8 Commit and push

Invoke the commit-push skill:

```
skill: "commits:commit-push"
```

### 4.9 Close task and update session log

```bash
bd close <task-id> --reason "Implemented via bd-work-loop: <one-line summary>"
bd sync
```

Capture diff summary:
```bash
git diff HEAD~1 --stat
git rev-parse --short HEAD
```

Append to `$SESSION_LOG`:
```markdown
## Task <N>: <task-id> — COMPLETED
Title: <task title>
Duration: <elapsed minutes since Phase 4.1>
Test written: <file>:<test name>
Full suite: <N passed, M pre-existing failures>
Diff: <git diff --stat output>
Commit: <short SHA>
```

Increment `COMPLETED_COUNT`. **After writing this log entry, return to Phase 1 without ending the conversation turn.**

---

## Phase 5: Session Summary

Write the final section to `$SESSION_LOG` and output it to the conversation.

```markdown
---

## Session Summary

**Status**: <COMPLETED N tasks | STOPPED: <reason>>
**Duration**: <M minutes>
**Started**: <timestamp>
**Ended**: <timestamp>

### Completed Tasks

| Task | Title | Duration | Commit | Tests |
|------|-------|----------|--------|-------|
| bd-42 | Add dark mode toggle | 8m | abc1234 | 45 passed |

### Deferred Tasks

| Task | Title | Reason |
|------|-------|--------|
| bd-47 | Refactor auth layer | Architectural: description says "choose between X and Y" |

### Stop Reason

<One of:>
- Completed N/N tasks (limit reached)
- Time limit reached (M minutes elapsed)
- Test regression in task bd-XX: <failing test name> — changes reverted
- Lint failure in task bd-XX — changes reverted
- Two consecutive deferrals (bd-XX then bd-YY)
- No tasks available
- All tasks blocked

### Recommendations

<For each deferred task: specific action the human should take before automating>
<For regression/lint stop: exact failing test or lint rule with file path>
<For blocked tasks: which blocker should be resolved first>

### Session Log

Full log: `~/.cache/bd-work-loop/<timestamp>.md`
```

Output the summary to the conversation.

---

## Exit Markers

End the conversation turn with exactly one marker:

| Marker | Condition |
|--------|-----------|
| `[BD-WORK-LOOP:COMPLETED]` | All N tasks completed |
| `[BD-WORK-LOOP:TIME_LIMIT]` | Minute limit reached |
| `[BD-WORK-LOOP:REGRESSION]` | Test regression stopped loop |
| `[BD-WORK-LOOP:LINT_FAILURE]` | Lint failure stopped loop |
| `[BD-WORK-LOOP:CONSECUTIVE_DEFERRALS]` | Two deferrals in a row |
| `[BD-WORK-LOOP:NO_TASKS]` | No tasks in beads |
| `[BD-WORK-LOOP:ALL_BLOCKED]` | All tasks blocked by dependencies |

---

## Implementation Notes

- **Single session turn**: the entire loop runs within one conversation turn. Do NOT use ScheduleWakeup. Do NOT end the turn between tasks.
- **Time check placement**: check elapsed time BEFORE starting a new iteration — never mid-task or mid-commit.
- **Baseline is frozen**: record baseline pass/fail set once at Phase 0 and never update it mid-session.
- **Defer is not failure**: structured deferral is the correct outcome for ambiguous work. Two consecutive deferrals stops the loop because it signals a systemic pattern, not because deferral itself is wrong.
- **Revert discipline**: if reverting uncommitted changes use `git checkout -- .` for tracked files. Never force-push or reset commits already pushed.
- **Parallel exploration**: always launch Phase 4.2 subagents in a single message with multiple Agent calls. Context quality directly affects implementation quality.
- **Conventional commits**: let `commits:commit-push` handle commit message format and branch safety — do not manually write commit messages for tasks completed in this loop.
