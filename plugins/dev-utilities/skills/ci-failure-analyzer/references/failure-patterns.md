# CI Failure Patterns

Quick reference for failure detection and resolution.

## Pattern Detection Table

| Type | Tool/Signal | Log Pattern | Auto-Fix | Command |
|------|-------------|-------------|----------|---------|
| **Formatting** | Prettier | `prettier`, `Code style issues` | ✅ 99% | `npx prettier --write .` |
| | Black | `black`, `would reformat` | ✅ 99% | `black .` |
| | gofmt | `gofmt`, `not formatted` | ✅ 99% | `gofumpt -w .` |
| | rustfmt | `rustfmt`, `cargo fmt` | ✅ 99% | `cargo fmt` |
| **Linting** | ESLint | `eslint`, `error`, rule name | ⚠️ 60-80% | `npx eslint --fix .` |
| | Ruff | `ruff`, `F841`, `E501` | ⚠️ 70-90% | `ruff check --fix .` |
| | Clippy | `clippy`, warning format | ❌ 20% | Manual |
| | golangci-lint | `golangci-lint` | ⚠️ 40-60% | `golangci-lint run --fix` |
| **Types** | TypeScript | `TS\d{4}`, `error TS` | ❌ 20-30% | Manual (Sonnet) |
| | mypy | `mypy`, `error:` | ❌ 15-25% | Manual |
| **Tests** | Jest | `FAIL`, `expect().toBe()` | ❌ 5-10% | Manual (Sonnet) |
| | pytest | `FAILED`, `AssertionError` | ❌ 5-10% | Manual |
| | Go test | `--- FAIL:`, `want/got` | ❌ 5-10% | Manual |
| **Deps** | npm ci | `out of sync`, lock mismatch | ✅ 95% | `npm install` |
| | poetry | `lock file`, mismatch | ✅ 90% | `poetry lock` (Poetry 2.x) |
| | cargo | `Cargo.lock` | ✅ 90% | `cargo update` |
| **Build** | Webpack/Vite | `Module not found` | ⚠️ 30-40% | Fix imports |
| | tsc build | `TS\d{4}` in build | ❌ 20-30% | Manual |
| **Security** | npm audit | `vulnerabilities found` | ⚠️ 50-70% | `npm audit fix` |
| **Infra** | Secrets | `Resource not accessible`, `##[error]No value` | ❌ 0% | Config fix |
| | Cache | `Failed to restore`, `tar: short read` | ❌ 0% | Bump key / rerun |
| | Timeout | `timeout`, exit 124/143 | ❌ 5% | Optimize / increase limit |
| | Matrix | Only some combinations fail | Varies | Target failing axis |

## Detection Regex Patterns

```regex
# Prettier
prettier|Code style issues found

# Black
black|would reformat|file.*would be reformatted

# ESLint
eslint|\.js:\d+:\d+.*error

# TypeScript
TS\d{4}|\.ts\(\d+,\d+\):.*error

# Jest
FAIL.*\.test\.(js|ts)x?|expect\(.*\)\.toBe\(

# pytest
FAILED\s+([^:]+)::(\w+)

# Lock file
package-lock\.json.*out of sync|lock file.*mismatch

# Import errors
Cannot find module|ModuleNotFoundError

# Secrets/Permissions
Resource not accessible|##\[error\]No value for required secret|exit code 78

# Cache
Failed to restore cache|tar: short read|Artifact has expired

# Timeout
timeout|exceeded.*time limit|operation was canceled
```

## Error Codes Reference

| Code | Meaning | Action |
|------|---------|--------|
| Exit 0 | Success | - |
| Exit 1 | General failure | Analyze logs |
| Exit 2 | Compilation error | Type/build issue |
| Exit 78 | Neutral status (deprecated, pre-2019 actions) | Rare; check action version |
| Exit 124 | Timeout | Optimize or increase limit |
| Exit 143 | SIGTERM (killed) | Resource limit |

# Log Parsing

Techniques for parsing GitHub Actions logs and extracting errors.

## Log Structure

GitHub Actions logs via `gh run view --log-failed`:
```
job-name	step-name	2024-01-15T10:30:45.1234567Z	log-line
```

Extract just the log lines:
```bash
gh run view <run-id> --log-failed | cut -f4-
```

## ANSI Color Stripping

```bash
# Strip color codes
sed 's/\x1b\[[0-9;]*m//g'
```

## Error Location Patterns

### File:Line:Column Formats

| Language | Format | Example |
|----------|--------|---------|
| TypeScript | `file(line,col): error TS####` | `src/index.ts(15,10): error TS2322` |
| ESLint | `file:line:col  level  message  rule` | `/src/file.ts:15:10  error  ...` |
| Python | `file:line: level: message` | `src/utils.py:23: error: ...` |
| Go | `file:line:col: message` | `./main.go:15:10: undefined: foo` |
| Rust | `error[CODE]: message\n  --> file:line:col` | `error[E0425]: ...\n  --> src/main.rs:15:10` |

### Universal Regex
```regex
([A-Za-z0-9_/.-]+\.[A-Za-z]+)[:(\[](\d+)[,:](\d+)?[\])]?.*(?:error|Error|ERROR)
```

## Test Framework Output

### Jest
```
FAIL src/api.test.ts
  ✕ test name (15 ms)
    expect(received).toBe(expected)
    Expected: 5
    Received: 3
    > 12 |     expect(result).toBe(5);
```

Extract: `✕\s+(.+?)\s+\(\d+ ms\)` → test name

### pytest
```
FAILED tests/test_api.py::test_get_data - AssertionError: assert 3 == 5
```

Extract: `FAILED\s+([^:]+)::(\w+)` → file, test name

### Go test
```
--- FAIL: TestGetData (0.00s)
    api_test.go:15: got 3, want 5
```

Extract: `---\s+FAIL:\s+(\w+)` → test name

## Stack Trace Patterns

### JavaScript
```regex
at\s+(?:([\w.<>]+)\s+)?\(([^:]+):(\d+):(\d+)\)
```

### Python
```regex
File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(.+)
```

## Matrix Job Parsing

```bash
# Get all job results
gh run view <run-id> --json jobs --jq '.jobs[] | {name, conclusion}'

# Target specific matrix child
gh run view <run-id> --job "test (node-version: 18, os: ubuntu-latest)" --log-failed
```

## Secret/Permission Indicators

Look for:
- `Resource not accessible by integration`
- `##[error]No value for required secret`
- `HttpError: 403 Forbidden`

Extract secret name: `secrets\.([A-Z0-9_]+)`

## Truncation Handling

If logs are truncated:
```bash
# Focus on errors near the end
gh run view --log-failed | grep -i error | tail -50

# Or download full logs
gh run download <run-id> --name <artifact-name>
```

## Quick Reference Patterns

```regex
# Error keywords
(?i)(error|warning|fail|failed|failure)

# Error codes
(TS|E|W|F)\d{3,4}

# File with line number
([A-Za-z0-9_/.-]+\.[A-Za-z]+):(\d+)

# Expected/Received
Expected:\s*(.+?)\s*Received:\s*(.+)

# Package versions
(\d+)\.(\d+)\.(\d+)
```
