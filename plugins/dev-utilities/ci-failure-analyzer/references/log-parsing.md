# Log Parsing Guide

Technical guide for parsing GitHub Actions logs and extracting meaningful error information.

## Table of Contents

1. [GitHub Actions Log Structure](#github-actions-log-structure)
2. [ANSI Color Code Handling](#ansi-color-code-handling)
3. [Error Pattern Extraction](#error-pattern-extraction)
4. [Stack Trace Parsing](#stack-trace-parsing)
5. [Test Framework Output](#test-framework-output)
6. [Multi-Job Correlation](#multi-job-correlation)
7. [Matrix & Reusable Workflow Parsing](#matrix--reusable-workflow-parsing)
8. [Secret and Permission Indicators](#secret-and-permission-indicators)
9. [Truncation Handling](#truncation-handling)
10. [Common Regex Patterns](#common-regex-patterns)

---

## GitHub Actions Log Structure

### Log Format from `gh run view --log-failed`

GitHub Actions logs are structured by job and step:

```
job-name	step-name	timestamp	log-line
job-name	step-name	timestamp	log-line
```

**Example**:

```
build	Run tests	2024-01-15T10:30:45.1234567Z	npm test
build	Run tests	2024-01-15T10:30:46.7891011Z	  PASS src/utils.test.ts
build	Run tests	2024-01-15T10:30:47.1234567Z	  FAIL src/api.test.ts
build	Run tests	2024-01-15T10:30:47.5678901Z	    ● API test › returns data
```

### Key Components

1. **Job Name**: First column (tab-separated)
   - Example: `build`, `test`, `lint`

2. **Step Name**: Second column
   - Example: `Run tests`, `Check formatting`

3. **Timestamp**: ISO 8601 format with nanosecond precision
   - Example: `2024-01-15T10:30:45.1234567Z`

4. **Log Line**: The actual output

### Parsing Strategy

**Use tab splitting**:

```bash
# Extract just the log lines (4th field)
gh run view <run-id> --log-failed | cut -f4-
```

**Or in code**:

```python
for line in log_output.split('\n'):
    parts = line.split('\t', 3)
    if len(parts) >= 4:
        job, step, timestamp, message = parts
        # Process message
```

---

## ANSI Color Code Handling

GitHub Actions logs contain ANSI escape codes for colors:

### Common ANSI Codes

```
\x1b[0m     - Reset
\x1b[1m     - Bold
\x1b[31m    - Red (errors)
\x1b[32m    - Green (success)
\x1b[33m    - Yellow (warnings)
\x1b[90m    - Gray (debug)
```

### Example Raw Log Line

```
\x1b[31mError:\x1b[0m \x1b[1msrc/index.ts\x1b[0m:15:10 - \x1b[31merror TS2322\x1b[0m
```

Rendered:

```
Error: src/index.ts:15:10 - error TS2322
```

### Stripping ANSI Codes

**Regex Pattern**:

```regex
\x1b\[[0-9;]*m
```

**Python**:

```python
import re

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)
```

**Bash**:

```bash
# Using sed
sed 's/\x1b\[[0-9;]*m//g'

# Using grep with perl regex
grep -oP '[\x20-\x7E]+' # Keep only printable ASCII
```

**Note**: `gh run view` output may already have ANSI codes stripped, but always verify.

---

## Error Pattern Extraction

### File Path + Line Number Patterns

Most error messages include file paths with line/column numbers:

**Common Formats**:

1. **TypeScript/JavaScript**:

   ```
   src/index.ts(15,10): error TS2322: Type 'string' is not assignable to type 'number'
   ```

   Pattern: `filename(line,col): error CODE: message`

2. **ESLint**:

   ```
   /path/to/file.ts:15:10  error  'x' is defined but never used  @typescript-eslint/no-unused-vars
   ```

   Pattern: `filepath:line:col  level  message  rule-name`

3. **Python (pytest/black)**:

   ```
   src/utils.py:23: error: Incompatible types
   ```

   Pattern: `filepath:line: level: message`

4. **Go**:

   ```
   ./main.go:15:10: undefined: foo
   ```

   Pattern: `filepath:line:col: message`

5. **Rust**:
   ```
   error[E0425]: cannot find value `x` in this scope
     --> src/main.rs:15:10
   ```
   Pattern: `error[CODE]: message\n  --> filepath:line:col`

### Universal Regex Pattern

```regex
(?P<file>[A-Za-z0-9_/.-]+\.[A-Za-z]+)[:(\[](?P<line>\d+)[,:](?P<col>\d+)?[\])]?.*(?:error|Error|ERROR|warning|Warning).*
```

**Explanation**:

- `(?P<file>...)` - Capture filename with extension
- `[:(\[]` - Followed by `:`, `(`, or `[`
- `(?P<line>\d+)` - Line number (required)
- `[,:](?P<col>\d+)?` - Optional column number
- `.*(?:error|warning)` - Contains "error" or "warning"

**Python Usage**:

```python
import re

pattern = r'([A-Za-z0-9_/.-]+\.[A-Za-z]+)[:(\[](\d+)[,:](\d+)?[\])]?.*(?:error|Error|ERROR)'

for line in log_lines:
    match = re.search(pattern, line)
    if match:
        file_path = match.group(1)
        line_num = match.group(2)
        col_num = match.group(3) if match.group(3) else None
        print(f"{file_path}:{line_num}:{col_num}")
```

### Error Message Extraction

After finding file:line:col, extract the actual error message:

**Pattern**: Everything after the location until newline

```python
def extract_error_message(line):
    # Find the part after "error" keyword
    error_match = re.search(r'(?:error|Error|ERROR)[:\s]+(.+)$', line)
    if error_match:
        return error_match.group(1).strip()
    return None
```

---

## Stack Trace Parsing

### JavaScript/TypeScript Stack Traces

**Format**:

```
Error: Something went wrong
    at Object.<anonymous> (/path/to/file.ts:15:10)
    at Module._compile (internal/modules/cjs/loader.js:1138:30)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:1158:10)
```

**Parsing Strategy**:

1. **Detect Start**: Line containing "Error:" or " at"
2. **Extract Frames**: Each line starting with " at"
3. **Parse Frame**:
   ```regex
   at\s+(?:(?P<fn>[\w.<>]+)\s+)?\((?P<file>.+):(?P<line>\d+):(?P<col>\d+)\)
   ```

**Python**:

```python
def parse_js_stack_trace(lines):
    frames = []
    in_stack_trace = False

    for line in lines:
        if 'Error:' in line or line.strip().startswith('at '):
            in_stack_trace = True

        if in_stack_trace and line.strip().startswith('at '):
            match = re.search(r'at\s+(?:([\w.<>]+)\s+)?\((.+):(\d+):(\d+)\)', line)
            if match:
                frames.append({
                    'function': match.group(1) or '<anonymous>',
                    'file': match.group(2),
                    'line': int(match.group(3)),
                    'col': int(match.group(4))
                })
        elif in_stack_trace and not line.strip().startswith('at '):
            # End of stack trace
            break

    return frames
```

### Python Stack Traces

**Format**:

```
Traceback (most recent call last):
  File "/path/to/file.py", line 15, in <module>
    result = foo()
  File "/path/to/utils.py", line 23, in foo
    return bar()
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

**Parsing Strategy**:

1. **Detect Start**: "Traceback (most recent call last):"
2. **Extract Frames**: Lines starting with " File"
3. **Parse Frame**:
   ```regex
   File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(.+)
   ```

**Python**:

```python
def parse_python_stack_trace(lines):
    frames = []
    in_stack_trace = False

    for i, line in enumerate(lines):
        if 'Traceback (most recent call last):' in line:
            in_stack_trace = True
            continue

        if in_stack_trace:
            match = re.search(r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(.+)', line)
            if match:
                frames.append({
                    'file': match.group(1),
                    'line': int(match.group(2)),
                    'function': match.group(3),
                    'code': lines[i+1].strip() if i+1 < len(lines) else ''
                })
            elif not line.strip().startswith('File') and frames:
                # This is the error message
                frames[-1]['error'] = line.strip()
                break

    return frames
```

### Go Stack Traces

**Format**:

```
panic: runtime error: invalid memory address

goroutine 1 [running]:
main.foo(...)
    /path/to/main.go:15
main.main()
    /path/to/main.go:23 +0x45
```

**Parsing Strategy**: Similar to Python, look for file paths and line numbers

---

## Test Framework Output

### Jest (JavaScript/TypeScript)

**Success Pattern**:

```
PASS src/utils.test.ts
  ✓ adds two numbers (3 ms)
```

**Failure Pattern**:

```
FAIL src/api.test.ts
  ✕ API test › returns data (15 ms)

    expect(received).toBe(expected)

    Expected: 5
    Received: 3

      10 | test('returns data', () => {
      11 |   const result = getData();
    > 12 |   expect(result).toBe(5);
         |                  ^
      13 | });
```

**Parsing**:

1. **Identify Failed Test**:

   ```regex
   ✕\s+(.+?)\s+\(\d+ ms\)
   ```

   Captures: Test name

2. **Extract Expectation**:

   ```regex
   Expected:\s*(.+)\s*Received:\s*(.+)
   ```

3. **Find File Location**:
   ```regex
   >\s*(\d+)\s*\|
   ```
   The line with `>` marker

**Python**:

```python
def parse_jest_failure(lines):
    test_name = None
    expected = None
    received = None
    line_num = None

    for i, line in enumerate(lines):
        if '✕' in line or '✓' not in line and 'test' in line.lower():
            match = re.search(r'[✕×]\s+(.+?)\s+\(\d+ ms\)', line)
            if match:
                test_name = match.group(1)

        if 'Expected:' in line:
            expected = line.split('Expected:')[1].strip()
            if i+1 < len(lines) and 'Received:' in lines[i+1]:
                received = lines[i+1].split('Received:')[1].strip()

        if '>' in line and '|' in line:
            match = re.search(r'>\s*(\d+)\s*\|', line)
            if match:
                line_num = int(match.group(1))

    return {
        'test': test_name,
        'expected': expected,
        'received': received,
        'line': line_num
    }
```

### pytest (Python)

**Success Pattern**:

```
tests/test_utils.py::test_add PASSED
```

**Failure Pattern**:

```
FAILED tests/test_api.py::test_get_data - AssertionError: assert 3 == 5
    def test_get_data():
>       assert get_data() == 5
E       assert 3 == 5
```

**Parsing**:

1. **Identify Failed Test**:

   ```regex
   FAILED\s+([^:]+)::(\w+)\s+-\s+(.+)
   ```

   Captures: file, test_name, error_message

2. **Extract Assertion**:
   ```regex
   E\s+assert\s+(.+)
   ```

### Go Test

**Failure Pattern**:

```
--- FAIL: TestGetData (0.00s)
    api_test.go:15: got 3, want 5
```

**Parsing**:

```regex
---\s+FAIL:\s+(\w+).*\n\s+([^:]+):(\d+):\s+(.+)
```

---

## Multi-Job Correlation

When multiple jobs fail, correlate them to find root causes:

### Dependency Detection

**Pattern**: Job B fails because Job A failed

**Example**:

```
Job: build  → FAILED (compilation error)
Job: test   → FAILED (no artifact from build)
Job: lint   → PASSED
```

**Analysis**:

- `test` depends on `build`
- If `build` fails, `test` will also fail
- Fix `build` first

**Detection Strategy**:

1. **Parse Workflow YAML** (if available):

   ```yaml
   jobs:
     test:
       needs: [build]
   ```

2. **Look for Artifact Errors**:

   ```
   Error: Unable to download artifact 'build-output'
   ```

3. **Prioritize by Time**:
   - Earlier jobs are more likely to be root cause

### Common Root Causes

**Dependency Installation Failure**:

- All subsequent jobs fail with "command not found"
- Fix: install job

**Build Failure**:

- Test and deployment jobs fail
- Fix: build job

**Environment Setup**:

- Multiple jobs fail with same error
- Fix: environment configuration

---

## Matrix & Reusable Workflow Parsing

Matrix jobs and reusable workflows add metadata that helps pinpoint the failing axis.

### Extract Matrix Metadata

```bash
gh run view <run-id> --json jobs --jq '
  .jobs[] | {
    name,
    conclusion,
    startedAt,
    completedAt,
    steps: [.steps[] | {name, conclusion}],
    matrix: .strategy?.matrix
  }'
```

- `matrix` contains the parameter set (`{"node-version": "18", "os": "ubuntu-latest"}`)
- Job `name` often repeats these values; parse text between parentheses.

### Target a Specific Matrix Child

```bash
gh run view <run-id> --job "test (node-version: 18, os: ubuntu-latest)" --log-failed
```

- Works even when other matrix children succeed.
- Combine with `cut -f4-` to strip metadata, then search for tool-specific errors.

### Reusable Workflow Calls

Reusable workflows show up as jobs whose `steps[].name` equals `Run workflow`.

1. Inspect parent logs for `workflow_call` metadata.
2. Download child workflow logs via `gh run view <child-run-id> --log`.
3. Note that reusable workflows may hide the true job name; rely on `needs` graph to map dependencies. If you can't find the failing step in parent logs, check the reusable workflow's own run logs separately.

### Prioritization Tips

- Sort jobs by `startedAt` to find earliest failure.
- If multiple children fail with identical matrix values, deduplicate before summarizing for the user.

---

## Secret and Permission Indicators

Some log lines implicitly reveal missing secrets or insufficient permissions.

### Common Patterns

```
Resource not accessible by integration
HttpError: 403 Forbidden
##[error]No value for required secret
fatal: could not read Username for 'https://github.com': No such device or address
Error: Unable to process command '::set-env name=...::...' successfully.
```

### Parsing Strategy

1. Search logs case-insensitively for `secret`, `permission`, `resource not accessible`, `forbidden`, `exit code 78`.
2. Extract the secret/key name using regex:
   ```regex
   secrets\.([A-Z0-9_]+)
   ```
   Note: This won't catch environment variable indirection (e.g., `env: NPM_TOKEN: ${{ secrets.TOKEN }}`); check workflow files if direct references aren't found.
3. For permission blocks, capture YAML snippet around `permissions:` to report missing scopes.
4. Record the step name and workflow file path (e.g., `.github/workflows/deploy.yml:25`) so users can verify configuration.

### Reporting

- Provide the failing step, missing secret/key, and recommended remediation (“Define `NPM_TOKEN` in repo secrets”).
- If the log references organization policies, remind users to contact org admins rather than editing the workflow.

---

## Truncation Handling

GitHub Actions may truncate very large logs.

### Detection

**Indicators**:

- Log ends abruptly mid-line
- Log size is exactly at a round number (1MB, 5MB)
- Missing expected end markers (like "Done")

### Strategies

1. **Request Full Logs**:

   ```bash
   # gh CLI may have limits, download raw logs
   gh run download <run-id> --name <artifact-name>
   ```

2. **Search for Key Patterns**:
   - Don't try to read entire log
   - Search for "error", "fail", "ERROR"

   ```bash
   gh run view --log-failed | grep -i error
   ```

3. **Focus on Recent Output**:
   - Errors usually near the end
   - Scan last 1000 lines first
   - Note: For matrix jobs with many parallel children, errors from failed matrix children typically appear near their own job's conclusion, not necessarily at the end of the entire log

   ```bash
   gh run view --log-failed | tail -1000
   ```

4. **Summarize Missing Context**:
   - If truncated, explain to user:
   ```
   The log was truncated. Based on available output, the error appears to be...
   ```

---

## Common Regex Patterns

Collection of useful regex patterns for log parsing:

### File Paths

```regex
# General file path
[A-Za-z0-9_/.-]+\.[A-Za-z]+

# With line number
([A-Za-z0-9_/.-]+\.[A-Za-z]+):(\d+)

# With line and column
([A-Za-z0-9_/.-]+\.[A-Za-z]+):(\d+):(\d+)

# TypeScript/C# style
([A-Za-z0-9_/.-]+\.[A-Za-z]+)\((\d+),(\d+)\)
```

### Error Keywords

```regex
# Case-insensitive error/warning
(?i)(error|warning|fail|failed|failure)

# Error codes
(?:error|Error|ERROR)[:\s]+([A-Z]+\d+)

# With code
(TS|E|W|F)\d{3,4}
```

### Test Failures

```regex
# Jest/Mocha
(?:FAIL|✕)\s+(.+?)(?:\s+\(\d+\s*ms\))?

# pytest
FAILED\s+([^:]+)::(\w+)

# Go
---\s+FAIL:\s+(\w+)

# Expected/Received
Expected:\s*(.+?)\s*Received:\s*(.+)
```

### Stack Traces

```regex
# JavaScript "at" frames
at\s+(?:([\w.<>]+)\s+)?\(([^:]+):(\d+):(\d+)\)

# Python File lines
File\s+"([^"]+)",\s+line\s+(\d+)

# Generic stack frame with file:line
\s+at\s+.+?\(([^:]+):(\d+)
```

### Version Numbers

```regex
# Semantic version
(\d+)\.(\d+)\.(\d+)(?:-([a-z0-9.-]+))?

# In error messages
version\s+(\d+(?:\.\d+){1,2})

# npm package@version
(@?[a-z0-9-]+(?:\/[a-z0-9-]+)?)@(\d+\.\d+\.\d+)
```

### URLs and Imports

```regex
# Import statements
(?:import|from|require)\s+['""]([^'""]+)['""]

# URLs
https?://[^\s<>""]+
```

---

## Example: Complete Log Parser

**Python implementation**:

```python
import re
from typing import List, Dict, Optional

class LogParser:
    def __init__(self, log_content: str):
        self.log_content = log_content
        self.lines = log_content.split('\n')

    def extract_errors(self) -> List[Dict]:
        """Extract all error messages with file/line info"""
        errors = []

        pattern = r'([A-Za-z0-9_/.-]+\.[A-Za-z]+)[:(\[](\d+)[,:](\d+)?[\])]?.*(?:error|Error|ERROR)'

        for i, line in enumerate(self.lines):
            match = re.search(pattern, line)
            if match:
                errors.append({
                    'file': match.group(1),
                    'line': int(match.group(2)),
                    'col': int(match.group(3)) if match.group(3) else None,
                    'message': line,
                    'context': self.lines[max(0, i-2):min(len(self.lines), i+3)]
                })

        return errors

    def detect_tool(self) -> Optional[str]:
        """Detect which tool is reporting errors"""
        content_lower = self.log_content.lower()

        if 'prettier' in content_lower:
            return 'prettier'
        elif 'eslint' in content_lower:
            return 'eslint'
        elif 'tsc' in content_lower or re.search(r'TS\d{4}', self.log_content):
            return 'typescript'
        elif 'black' in content_lower and 'would reformat' in content_lower:
            return 'black'
        elif 'pytest' in content_lower or 'FAILED tests/' in self.log_content:
            return 'pytest'
        elif 'jest' in content_lower or re.search(r'FAIL.*\.test\.(js|ts)', self.log_content):
            return 'jest'

        return None

    def extract_failed_files(self) -> List[str]:
        """Extract list of files mentioned in errors"""
        file_pattern = r'([A-Za-z0-9_/.-]+\.[A-Za-z]+)[:(\[]?\d+'
        files = set()

        for line in self.lines:
            match = re.search(file_pattern, line)
            if match and ('error' in line.lower() or 'fail' in line.lower()):
                files.add(match.group(1))

        return sorted(list(files))
```

**Usage**:

```python
parser = LogParser(log_content)
errors = parser.extract_errors()
tool = parser.detect_tool()
files = parser.extract_failed_files()

print(f"Detected tool: {tool}")
print(f"Errors found in: {', '.join(files)}")
for error in errors[:5]:  # First 5 errors
    print(f"  {error['file']}:{error['line']} - {error['message']}")
```

---

## Performance Considerations

### Large Logs (> 1MB)

1. **Stream Processing**: Don't load entire log into memory
2. **Early Exit**: Stop after finding enough information
3. **Parallel Processing**: Parse multiple jobs concurrently
4. **Pattern Matching**: Use compiled regex for speed

### Optimization Tips

```python
# Compile regex once
error_pattern = re.compile(r'([A-Za-z0-9_/.-]+\.[A-Za-z]+)[:(\[](\d+)')

# Use generator for large files
def parse_log_stream(file_path):
    with open(file_path) as f:
        for line in f:
            if 'error' in line.lower():
                yield line

# Limit search scope
relevant_lines = [l for l in lines if 'error' in l.lower() or 'fail' in l.lower()]
```

---

## Summary

**Key Takeaways**:

1. **Structure**: GitHub Actions logs are tab-separated (job, step, timestamp, message)
2. **Colors**: Strip ANSI codes before processing
3. **Patterns**: File paths usually follow `file:line:col` format
4. **Stack Traces**: Each language has distinct format - detect and parse accordingly
5. **Tests**: Look for expected/received patterns and test names
6. **Correlation**: Link related failures to find root causes
7. **Truncation**: Handle incomplete logs gracefully
8. **Performance**: Use compiled regex and streaming for large logs

**Model Usage**:

- **Haiku**: Pattern matching, regex application, file extraction
- **Sonnet**: Understanding error semantics, correlating failures, complex diagnostics
