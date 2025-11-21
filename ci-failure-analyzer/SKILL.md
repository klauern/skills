---
name: ci-failure-analyzer
description: Autonomously analyze GitHub Actions CI failures, parse logs, identify root causes, and apply fixes for common issues. Use when CI checks fail, tests break, or user asks to fix CI, check failures, or debug GitHub Actions. Handles formatting, linting, test failures, and dependency problems with intelligent categorization.
version: 1.0.0
author: klauern
---

# CI Failure Analyzer

## Overview

This skill enables automated analysis and resolution of GitHub Actions CI failures. It provides intelligent diagnosis and fix application for common CI issues.

**Core Capabilities**:

1. **Detection** - Identifies failing checks on PRs and branches
2. **Analysis** - Parses failure logs to identify root causes
3. **Categorization** - Classifies issues into fixable vs. non-fixable
4. **Application** - Applies automated fixes for common problems
5. **Guidance** - Suggests debugging approaches for complex failures
6. **Reporting** - Provides comprehensive analysis with actionable recommendations

## Quick Start

### Slash Commands

- **/gh-checks**: Analyze and fix GitHub Actions failures
  - See [`../commands/gh-checks.md`](../commands/gh-checks.md) for command details

### Core Documentation

- **[Workflows](references/workflows.md)** - Step-by-step analysis and fix workflows
- **[Failure Patterns](references/failure-patterns.md)** - Common failure types and solutions
- **[Best Practices](references/best-practices.md)** - Guidelines for autonomous fixes
- **[Log Parsing Guide](references/log-parsing.md)** - Technical details on extracting errors
- **[Tool Detection](references/tool-detection.md)** - Project tool and formatter detection
- **[Examples](references/examples.md)** - Real-world failure scenarios

## When to Use This Skill

### Autonomous Invocation Triggers

Use this skill when:

1. **Explicit CI Requests**:
   - User asks "why is CI failing?"
   - User requests "check CI" or "fix CI"
   - User mentions "GitHub Actions failures"
   - User says "fix the failing tests"
   - User asks to "review check failures"

2. **Contextual Detection**:
   - User mentions a PR is failing checks
   - User is debugging test failures
   - After pushing code and user mentions checks
   - When reviewing PR comments about CI failures
   - User asks about specific test failures

3. **Command Invocation**:
   - `/gh-checks` command is executed
   - Any variation mentioning CI or checks

4. **Post-Push Context**:
   - User just pushed code and asks about status
   - User mentions "did it pass?" or "check status"
   - Within conversation context of recent git push

### Don't Use When

- User is only asking about local test runs (not CI)
- Questions about CI configuration (not failures)
- General GitHub Actions documentation questions
- Setting up CI for the first time (not debugging failures)

## Workflow Overview

### High-Level Process

```
1. Detect Context
   ├─ Current branch
   ├─ PR existence
   └─ Recent pushes

2. List Failing Checks
   ├─ Via gh pr checks (if PR exists)
   └─ Via gh run list (branch-based)

3. Retrieve Failure Logs
   └─ gh run view --log-failed

4. Analyze Root Causes
   ├─ Parse error messages
   ├─ Categorize failure types
   └─ Identify fixability

5. Apply Fix Strategy
   ├─ Autonomous: Format/lint fixes
   ├─ Interactive: Complex issues
   └─ Report: Analysis + recommendations

6. Optional Re-run
   └─ gh run rerun (after fixes)
```

### Decision Process

The skill follows a conservative, user-respecting approach:

**Autonomous Fixes** (apply without asking):
- Code formatting (prettier, black, gofmt, rustfmt)
- Linting with --fix flags (eslint --fix, ruff check --fix)
- Lock file updates (package-lock.json, poetry.lock)
- Simple dependency installations

**Interactive Fixes** (consult user first):
- Type errors requiring code changes
- Test logic failures
- Breaking changes from dependencies
- Complex refactoring needs
- Anything that changes business logic

**Philosophy**: "Don't overdo it" - handle mechanical issues automatically, but respect user control over meaningful code changes.

**See [workflows.md](references/workflows.md) for detailed step-by-step instructions.**

## Model Strategy

### Use Haiku 4.5 for

**Fast I/O Operations**:
- Executing `gh run list`, `gh run view`, `gh pr checks`
- Reading failure logs from files
- Running formatters and linters
- Git status and diff checks
- Pattern matching against known error signatures

**Simple Decision Making**:
- Categorizing failures into known types
- Extracting file paths from error messages
- Determining which formatter/linter to run
- Checking if auto-fix is available

### Use Sonnet 4.5 for

**Complex Analysis**:
- Root cause determination for ambiguous failures
- Correlating multiple related failures
- Understanding test failure semantics
- Assessing breaking change impacts

**Reasoning Tasks**:
- Determining if failure is code vs. environment
- Deciding autonomous fix vs. user consultation
- Prioritizing multiple failures
- Risk assessment for automated changes

**Natural Language Generation**:
- Explaining complex failures to users
- Providing debugging guidance
- Suggesting fix approaches for manual issues
- Writing comprehensive analysis reports

**Strategic Decision Making**:
- Whether to batch fixes or apply incrementally
- Determining fix order for dependent failures
- Assessing confidence in proposed solutions

**See [workflows.md](references/workflows.md) for phase-specific model strategy examples.**

## Core Capabilities

### 1. Multi-Repository Pattern Detection

The skill learns and recognizes patterns across different repositories:

- **Project-Specific Linting**: Detects which linters/formatters each project uses
- **Common Failure Signatures**: Builds taxonomy of recognizable error patterns
- **Tool Configuration**: Understands project conventions from config files
- **Test Framework Recognition**: Identifies Jest, pytest, Go test, etc. from output

### 2. Intelligent Log Parsing

Extracts meaningful information from verbose CI logs:

- **Error Extraction**: Identifies actual errors among thousands of log lines
- **Stack Trace Analysis**: Parses stack traces to pinpoint failure locations
- **Multi-Job Correlation**: Links related failures across different CI jobs
- **ANSI Color Stripping**: Handles colored terminal output in logs
- **Truncation Handling**: Works with incomplete logs when truncated

**Technical details**: See [log-parsing.md](references/log-parsing.md)

### 3. Root Cause Analysis

Determines the underlying cause of failures:

- **Code vs. Environment**: Distinguishes code issues from CI environment problems
- **Dependency Conflicts**: Identifies version mismatches and breaking changes
- **Flaky Test Detection**: Recognizes patterns of intermittent failures
- **Infrastructure Issues**: Detects timeouts, rate limits, network errors
- **Breaking Change Detection**: Identifies when upstream dependencies changed APIs

### 4. Automated Fix Application

Applies fixes for mechanical issues:

- **Format Code**: Runs project-detected formatters
- **Lint with Auto-Fix**: Executes linters with --fix flags
- **Update Lock Files**: Regenerates dependency lock files
- **Install Missing Dependencies**: Adds missing packages
- **Simple Type Fixes**: Addresses straightforward type annotation issues

**Safety**: Always verifies project state before and after fixes

### 5. Test Failure Analysis

Deep understanding of test failures:

- **Parse Test Output**: Extracts failing test names and error messages
- **Categorize Failures**: Assertion vs. timeout vs. setup/teardown
- **Identify Related Code**: Links test failures to recent code changes
- **Suggest Debugging**: Provides approaches for investigating failures
- **Detect Patterns**: Recognizes common test failure scenarios

### 6. Breaking Change Detection

Handles dependency updates causing failures:

- **API Change Detection**: Identifies when external APIs changed
- **Migration Path Suggestions**: Recommends how to adapt to breaking changes
- **Version Pinning**: Suggests temporary pins while addressing changes
- **Changelog Analysis**: Reviews dependency changelogs for insights

## Quick Reference

### Common Failure Types

This skill handles these failure categories:

1. **Formatting Failures**
   - Tools: Prettier, Black, gofmt, rustfmt, dprint
   - Auto-fix: Yes
   - Example: "Expected 2 spaces, found 4"

2. **Linting Failures**
   - Tools: ESLint, Ruff, Clippy, golangci-lint, pylint
   - Auto-fix: Often (with --fix flags)
   - Example: "Unused variable 'x'"

3. **Type Checking Failures**
   - Tools: TypeScript, mypy, Flow, Pyright
   - Auto-fix: Sometimes (simple annotations)
   - Example: "Property 'foo' does not exist"

4. **Test Failures**
   - Frameworks: Jest, pytest, Go test, Ruby test, etc.
   - Auto-fix: Rarely (requires logic changes)
   - Example: "Expected 5, received 3"

5. **Dependency Failures**
   - Issues: Lock file mismatches, version conflicts
   - Auto-fix: Often (lock file regeneration)
   - Example: "Package-lock.json out of sync"

6. **Build Failures**
   - Issues: Compilation errors, bundling failures
   - Auto-fix: Sometimes (missing imports)
   - Example: "Cannot find module 'foo'"

7. **Security Failures**
   - Tools: npm audit, Snyk, Dependabot
   - Auto-fix: Sometimes (dependency updates)
   - Example: "Vulnerable dependency detected"

8. **Infrastructure Failures**
   - Issues: Timeouts, rate limits, network errors
   - Auto-fix: No (CI configuration needed)
   - Example: "Connection timeout after 30s"

**For complete taxonomy and fix strategies**, see [failure-patterns.md](references/failure-patterns.md)

## Documentation Index

### Core Guides

- **[workflows.md](references/workflows.md)** - Detailed analysis workflows with model strategy
- **[failure-patterns.md](references/failure-patterns.md)** - Comprehensive failure taxonomy
- **[best-practices.md](references/best-practices.md)** - Guidelines for autonomous fixes

### Reference Materials

- **[log-parsing.md](references/log-parsing.md)** - Log parsing techniques and patterns
- **[tool-detection.md](references/tool-detection.md)** - Project tool/formatter detection
- **[examples.md](references/examples.md)** - Real-world failure scenarios with solutions

### Command Documentation

- **[gh-checks.md](../commands/gh-checks.md)** - CI failure analysis command

## Integration with Other Skills

This skill complements other marketplace skills:

- **conventional-commits**: After fixing CI, create proper commit messages
- **pr-creator**: Check CI status when creating PRs
- **gh-actions-upgrader**: Upgrade action versions causing failures

## Limitations and Boundaries

### What This Skill Does

✅ Analyzes GitHub Actions CI failures
✅ Parses logs and identifies root causes
✅ Applies mechanical fixes (formatting, linting)
✅ Provides debugging guidance for complex issues
✅ Detects project-specific tools and conventions

### What This Skill Doesn't Do

❌ Configure CI from scratch
❌ Write new tests for uncovered code
❌ Fix complex business logic errors
❌ Modify CI workflow YAML files (unless explicitly requested)
❌ Push fixes without user awareness
❌ Make architectural decisions

### Conservative Approach

This skill prioritizes:

1. **User Control**: Always explain what will be done
2. **Safety**: Verify project state before applying fixes
3. **Transparency**: Show commands that will be executed
4. **Reversibility**: Prefer fixes that can be easily undone
5. **Trust**: Build confidence through predictable behavior

**For detailed guidelines**, see [best-practices.md](references/best-practices.md)

## Troubleshooting

### Common Issues

**"No failing checks found"**
- Verify you're on the correct branch
- Check if PR exists: `gh pr view`
- Run `gh run list --branch $(git branch --show-current)` manually

**"Cannot retrieve logs"**
- Logs may not be available yet (run still in progress)
- Check GitHub Actions permissions
- Verify `gh` CLI is authenticated

**"Auto-fix didn't work"**
- Some linters require manual fixes
- Type errors often need code changes
- Test failures usually require logic updates

**"Too many failures"**
- Skill prioritizes by impact
- Fix one category at a time
- Consider addressing root cause first

**For more troubleshooting**, see [workflows.md](references/workflows.md#troubleshooting)

## Version History

### 1.0.0 (Current)
- Initial release
- Core failure detection and analysis
- Pattern-based categorization
- Autonomous fix application for formatting/linting
- Comprehensive reference documentation

## Related Commands

- **/gh-checks** - Analyze and fix CI failures
- **/gh-actions-upgrade** - Upgrade GitHub Actions versions
- **/commit** - Create conventional commit after fixes
- **/pr** - Create PR with CI status check

## Contributing Patterns

If you discover new failure patterns or fix strategies:

1. Document the pattern in [failure-patterns.md](references/failure-patterns.md)
2. Add detection logic to [log-parsing.md](references/log-parsing.md)
3. Include real example in [examples.md](references/examples.md)
4. Update [workflows.md](references/workflows.md) if workflow changes

This skill improves over time as it encounters more failure scenarios.
