# Tool Detection Guide

How to detect which formatters, linters, and build tools a project uses.

## Table of Contents

1. [Detection Strategy](#detection-strategy)
2. [Monorepo & Subdirectory Detection](#monorepo--subdirectory-detection)
3. [JavaScript/TypeScript Projects](#javascripttypescript-projects)
4. [Python Projects](#python-projects)
5. [Go Projects](#go-projects)
6. [Rust Projects](#rust-projects)
7. [Ruby Projects](#ruby-projects)
8. [CI Workflow Analysis](#ci-workflow-analysis)
9. [Fallback Defaults](#fallback-defaults)

---

## Detection Strategy

### Layered Detection Approach

1. **Explicit CI Workflow** (highest confidence)
   - Check `.github/workflows/*.yml`
   - See what commands CI actually runs

2. **Config Files** (high confidence)
   - `.prettierrc`, `.eslintrc`, `pyproject.toml`
   - Presence indicates tool is used

3. **Package Scripts** (medium confidence)
   - `package.json` scripts section
   - Look for `lint`, `format`, `test` scripts

4. **Dependencies** (medium confidence)
   - Check if tool is in dependencies/devDependencies
   - Installed doesn't always mean configured

5. **Language Defaults** (low confidence)
   - When nothing is configured, assume common defaults
   - Example: Go projects likely use `gofmt`

### Decision Tree

```
Is tool mentioned in CI workflow?
├─ Yes → Use that tool (confidence: 99%)
└─ No → Check config files
    ├─ Config exists → Use that tool (confidence: 90%)
    └─ No config → Check package.json scripts
        ├─ Script exists → Use that tool (confidence: 75%)
        └─ No script → Check if dependency is installed
            ├─ Installed → Use that tool (confidence: 60%)
            └─ Not installed → Use language default (confidence: 40%)
```

---

## Monorepo & Subdirectory Detection

Many repositories contain multiple apps/packages with distinct toolchains. Detect tooling inside each workspace to avoid running the wrong formatter.

### Discovery Steps

1. **Find Manifests**
   ```bash
   fd -tf --max-depth 4 'package.json|pyproject.toml|go.mod|Cargo.toml'
   ```
2. **Group by Directory**
   - Yarn/pnpm workspaces live under `apps/*`, `packages/*`, `services/*`
   - `go.work` and `Cargo.toml` often list member paths
3. **Iterate Per Package**

   ```python
   import json, subprocess, pathlib

   def detect_monorepo_tools(root):
       manifests = subprocess.run(
           ["fd", "-tf", "--max-depth", "4", "package.json"],
           cwd=root, capture_output=True, text=True,
       ).stdout.strip().splitlines()

       per_pkg = {}
       for manifest in manifests:
           pkg_dir = pathlib.Path(root, manifest).parent
           per_pkg[str(pkg_dir)] = detect_all_tools(str(pkg_dir))
       return per_pkg
   ```

### Reporting

```
Detected tools:
- apps/web: prettier, eslint, tsc
- apps/api: prettier, eslint, jest
- services/billing: gofumpt, golangci-lint
```

### Guardrails

- Never run formatters/linters at repo root if tools differ per workspace—scope commands to the failing package.
- When CI logs include a path (e.g., `apps/admin`), restrict detection to that directory first.
- If two workspaces use conflicting formatter versions, mention the conflict before auto-running fixes.

---

## JavaScript/TypeScript Projects

### Prettier Detection

**1. Config Files**:

```bash
# Check for prettier config (any of these)
fd -t f '\.prettierrc|\.prettierrc\.(json|yml|yaml|js|cjs|toml)|prettier\.config\.(js|cjs)$'

# Or in package.json
grep -q '"prettier"' package.json
```

**Files to check**:

- `.prettierrc`
- `.prettierrc.json`, `.prettierrc.yml`, `.prettierrc.yaml`
- `.prettierrc.js`, `.prettierrc.cjs`
- `prettier.config.js`, `prettier.config.cjs`
- `package.json` (with `"prettier"` key)

**2. Package.json Scripts**:

```bash
# Look for format scripts
grep -E '"(format|prettier)".*prettier' package.json
```

**3. Dependencies**:

```bash
# Check if prettier is installed
jq -r '.devDependencies.prettier // .dependencies.prettier // empty' package.json
```

**Detection Code**:

```python
def detect_prettier(project_path):
    # 1. Check config files
    prettier_configs = [
        '.prettierrc',
        '.prettierrc.json',
        '.prettierrc.yml',
        '.prettierrc.js',
        'prettier.config.js'
    ]

    for config in prettier_configs:
        if os.path.exists(os.path.join(project_path, config)):
            return {
                'tool': 'prettier',
                'confidence': 90,
                'config': config
            }

    # 2. Check package.json
    package_json = os.path.join(project_path, 'package.json')
    if os.path.exists(package_json):
        with open(package_json) as f:
            data = json.load(f)

            # Check prettier key
            if 'prettier' in data:
                return {'tool': 'prettier', 'confidence': 85}

            # Check scripts
            scripts = data.get('scripts', {})
            for script in scripts.values():
                if 'prettier' in script:
                    return {'tool': 'prettier', 'confidence': 75}

            # Check dependencies
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            if 'prettier' in deps:
                return {'tool': 'prettier', 'confidence': 60}

    return None
```

---

### ESLint Detection

**1. Config Files**:

```bash
# Check for eslint config
fd -t f '\.eslintrc|\.eslintrc\.(json|yml|yaml|js|cjs)|eslint\.config\.(js|cjs|mjs)$'
```

**Files to check**:

- `.eslintrc`
- `.eslintrc.json`, `.eslintrc.yml`, `.eslintrc.js`, `.eslintrc.cjs`
- `eslint.config.js` (ESLint 9+ flat config)

**2. Package.json**:

```bash
# Check for eslint in scripts or config
grep -E '"(lint|eslint)"' package.json
```

**Detection Code**:

```python
def detect_eslint(project_path):
    eslint_configs = [
        '.eslintrc',
        '.eslintrc.json',
        '.eslintrc.yml',
        '.eslintrc.js',
        'eslint.config.js'
    ]

    for config in eslint_configs:
        if os.path.exists(os.path.join(project_path, config)):
            return {
                'tool': 'eslint',
                'confidence': 90,
                'config': config
            }

    # Check package.json
    package_json = os.path.join(project_path, 'package.json')
    if os.path.exists(package_json):
        with open(package_json) as f:
            data = json.load(f)

            # Check scripts
            scripts = data.get('scripts', {})
            for script_name, script_cmd in scripts.items():
                if 'eslint' in script_cmd:
                    return {
                        'tool': 'eslint',
                        'confidence': 75,
                        'script': script_name
                    }

            # Check dependencies
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            if 'eslint' in deps:
                return {'tool': 'eslint', 'confidence': 60}

    return None
```

---

### TypeScript (tsc) Detection

**1. Config File**:

```bash
# tsconfig.json is definitive
test -f tsconfig.json && echo "TypeScript project"
```

**2. Package.json**:

```bash
# Check for typescript dependency
jq -r '.devDependencies.typescript // .dependencies.typescript // empty' package.json
```

**Detection Code**:

```python
def detect_typescript(project_path):
    tsconfig = os.path.join(project_path, 'tsconfig.json')
    if os.path.exists(tsconfig):
        return {
            'tool': 'typescript',
            'confidence': 95,
            'config': 'tsconfig.json'
        }

    # Check for .ts files
    ts_files = subprocess.run(
        ['fd', '-e', 'ts', '-e', 'tsx'],
        cwd=project_path,
        capture_output=True,
        text=True
    )

    if ts_files.returncode == 0 and ts_files.stdout.strip():
        return {
            'tool': 'typescript',
            'confidence': 80
        }

    return None
```

---

## Python Projects

### Black Detection

**1. Config Files**:

```bash
# Check pyproject.toml for [tool.black]
grep -q '\[tool\.black\]' pyproject.toml

# Or .black file
test -f .black && echo "Black configured"
```

**2. Setup.cfg**:

```bash
grep -q '\[tool:black\]' setup.cfg
```

**3. Dependencies**:

```bash
# Check if black is in requirements or poetry
grep -q '^black' requirements.txt requirements-dev.txt
poetry show black 2>/dev/null
```

**Detection Code**:

```python
def detect_black(project_path):
    # Check pyproject.toml
    pyproject = os.path.join(project_path, 'pyproject.toml')
    if os.path.exists(pyproject):
        with open(pyproject) as f:
            content = f.read()
            if '[tool.black]' in content:
                return {
                    'tool': 'black',
                    'confidence': 90,
                    'config': 'pyproject.toml'
                }

    # Check if black is importable (installed)
    try:
        subprocess.run(['black', '--version'], check=True, capture_output=True)
        return {'tool': 'black', 'confidence': 60}
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return None
```

---

### Ruff Detection

**1. Config Files**:

```bash
# Check pyproject.toml for [tool.ruff]
grep -q '\[tool\.ruff\]' pyproject.toml

# Or ruff.toml
test -f ruff.toml && echo "Ruff configured"
```

**2. Dependencies**:

```bash
grep -q '^ruff' requirements.txt requirements-dev.txt
poetry show ruff 2>/dev/null
```

**Detection Code**:

```python
def detect_ruff(project_path):
    # Check pyproject.toml
    pyproject = os.path.join(project_path, 'pyproject.toml')
    if os.path.exists(pyproject):
        with open(pyproject) as f:
            content = f.read()
            if '[tool.ruff]' in content:
                return {
                    'tool': 'ruff',
                    'confidence': 90,
                    'config': 'pyproject.toml'
                }

    # Check ruff.toml
    ruff_toml = os.path.join(project_path, 'ruff.toml')
    if os.path.exists(ruff_toml):
        return {
            'tool': 'ruff',
            'confidence': 90,
            'config': 'ruff.toml'
        }

    return None
```

---

### mypy Detection

**1. Config Files**:

```bash
# Check mypy.ini
test -f mypy.ini && echo "mypy configured"

# Or pyproject.toml [tool.mypy]
grep -q '\[tool\.mypy\]' pyproject.toml

# Or setup.cfg [mypy]
grep -q '\[mypy\]' setup.cfg
```

**Detection Code**:

```python
def detect_mypy(project_path):
    mypy_configs = [
        ('mypy.ini', 95),
        ('.mypy.ini', 95)
    ]

    for config, confidence in mypy_configs:
        if os.path.exists(os.path.join(project_path, config)):
            return {
                'tool': 'mypy',
                'confidence': confidence,
                'config': config
            }

    # Check pyproject.toml
    pyproject = os.path.join(project_path, 'pyproject.toml')
    if os.path.exists(pyproject):
        with open(pyproject) as f:
            if '[tool.mypy]' in f.read():
                return {
                    'tool': 'mypy',
                    'confidence': 90,
                    'config': 'pyproject.toml'
                }

    return None
```

---

## Go Projects

### gofmt/gofumpt Detection

**Note**: User's CLAUDE.md specifies preference for `gofumpt` over `gofmt`

**1. CI Workflow Check**:

```bash
# Check if gofumpt is used in CI
grep -r 'gofumpt' .github/workflows/
```

**2. Default to gofumpt** (user preference):

```python
def detect_go_formatter(project_path):
    # Check for Go project
    if not os.path.exists(os.path.join(project_path, 'go.mod')):
        return None

    # Check CI workflows
    workflows_dir = os.path.join(project_path, '.github', 'workflows')
    if os.path.exists(workflows_dir):
        for workflow in os.listdir(workflows_dir):
            with open(os.path.join(workflows_dir, workflow)) as f:
                content = f.read()
                if 'gofumpt' in content:
                    return {
                        'tool': 'gofumpt',
                        'confidence': 95
                    }
                elif 'gofmt' in content:
                    return {
                        'tool': 'gofmt',
                        'confidence': 90
                    }

    # Default to gofumpt (user preference per CLAUDE.md)
    return {
        'tool': 'gofumpt',
        'confidence': 70,
        'note': 'User preference (CLAUDE.md)'
    }
```

---

### golangci-lint Detection

**1. Config File**:

```bash
# Check for golangci-lint config
test -f .golangci.yml && echo "golangci-lint configured"
test -f .golangci.yaml && echo "golangci-lint configured"
test -f .golangci.toml && echo "golangci-lint configured"
```

**Detection Code**:

```python
def detect_golangci_lint(project_path):
    configs = ['.golangci.yml', '.golangci.yaml', '.golangci.toml', '.golangci.json']

    for config in configs:
        if os.path.exists(os.path.join(project_path, config)):
            return {
                'tool': 'golangci-lint',
                'confidence': 95,
                'config': config
            }

    return None
```

---

## Rust Projects

### rustfmt Detection

**1. Config File**:

```bash
# Check for rustfmt.toml
test -f rustfmt.toml && echo "rustfmt configured"
test -f .rustfmt.toml && echo "rustfmt configured"
```

**2. Default**:
All Rust projects use `cargo fmt` (rustfmt) by default

**Detection Code**:

```python
def detect_rustfmt(project_path):
    # Check for Rust project
    if not os.path.exists(os.path.join(project_path, 'Cargo.toml')):
        return None

    # Check for config
    if os.path.exists(os.path.join(project_path, 'rustfmt.toml')):
        return {
            'tool': 'rustfmt',
            'confidence': 95,
            'config': 'rustfmt.toml'
        }

    # Default for all Rust projects
    return {
        'tool': 'rustfmt',
        'confidence': 80,
        'note': 'Rust projects use cargo fmt by default'
    }
```

---

### Clippy Detection

**1. Always Available**:
Clippy is part of the Rust toolchain, available for all Rust projects

**Detection Code**:

```python
def detect_clippy(project_path):
    if os.path.exists(os.path.join(project_path, 'Cargo.toml')):
        return {
            'tool': 'clippy',
            'confidence': 90,
            'note': 'Part of Rust toolchain'
        }
    return None
```

---

## Ruby Projects

### RuboCop Detection

**1. Config File**:

```bash
test -f .rubocop.yml && echo "RuboCop configured"
```

**2. Gemfile**:

```bash
grep -q 'rubocop' Gemfile
```

**Detection Code**:

```python
def detect_rubocop(project_path):
    # Check for config
    if os.path.exists(os.path.join(project_path, '.rubocop.yml')):
        return {
            'tool': 'rubocop',
            'confidence': 95,
            'config': '.rubocop.yml'
        }

    # Check Gemfile
    gemfile = os.path.join(project_path, 'Gemfile')
    if os.path.exists(gemfile):
        with open(gemfile) as f:
            if 'rubocop' in f.read():
                return {
                    'tool': 'rubocop',
                    'confidence': 85
                }

    return None
```

---

## CI Workflow Analysis

The most reliable detection: **check what CI actually runs**.

### GitHub Actions Workflow Parsing

**1. Find Workflow Files**:

```bash
fd -t f '\.yml$|\.yaml$' .github/workflows/
```

**2. Parse Workflow**:

```python
import yaml

def parse_ci_workflows(project_path):
    workflows_dir = os.path.join(project_path, '.github', 'workflows')
    if not os.path.exists(workflows_dir):
        return []

    tools = []

    for workflow_file in os.listdir(workflows_dir):
        if not workflow_file.endswith(('.yml', '.yaml')):
            continue

        with open(os.path.join(workflows_dir, workflow_file)) as f:
            try:
                workflow = yaml.safe_load(f)
            except yaml.YAMLError:
                continue

            # Extract commands from steps
            for job in workflow.get('jobs', {}).values():
                for step in job.get('steps', []):
                    run = step.get('run', '')

                    # Detect tools from commands
                    if 'prettier' in run:
                        tools.append(('prettier', 99, workflow_file))
                    if 'eslint' in run:
                        tools.append(('eslint', 99, workflow_file))
                    if 'black' in run:
                        tools.append(('black', 99, workflow_file))
                    if 'tsc' in run:
                        tools.append(('typescript', 99, workflow_file))
                    if 'mypy' in run:
                        tools.append(('mypy', 99, workflow_file))
                    if 'gofumpt' in run or 'gofmt' in run:
                        tool = 'gofumpt' if 'gofumpt' in run else 'gofmt'
                        tools.append((tool, 99, workflow_file))
                    if 'cargo fmt' in run:
                        tools.append(('rustfmt', 99, workflow_file))
                    if 'cargo clippy' in run:
                        tools.append(('clippy', 99, workflow_file))

    return tools
```

**Benefits**:

- 99% confidence - this is what CI actually runs
- Handles custom commands and scripts
- Reveals exact command-line flags used

---

## Fallback Defaults

When no explicit configuration is found, use these language defaults:

### JavaScript/TypeScript

```python
defaults = {
    'formatter': 'prettier',  # Most common
    'linter': 'eslint',       # Most common
    'type_checker': 'typescript' if has_tsconfig else None
}
```

### Python

```python
defaults = {
    'formatter': 'black',     # Most popular
    'linter': 'ruff',         # Modern choice
    'type_checker': 'mypy' if has_type_hints else None
}
```

### Go

```python
defaults = {
    'formatter': 'gofumpt',   # User preference per CLAUDE.md
    'linter': 'golangci-lint'
}
```

### Rust

```python
defaults = {
    'formatter': 'rustfmt',   # Standard
    'linter': 'clippy'        # Standard
}
```

---

## Complete Detection Function

**Combining all strategies**:

```python
def detect_all_tools(project_path):
    tools = {}

    # 1. Check CI workflows (highest priority)
    ci_tools = parse_ci_workflows(project_path)
    for tool, confidence, source in ci_tools:
        tools[tool] = {
            'confidence': confidence,
            'source': f'CI workflow: {source}'
        }

    # 2. Detect from config files (if not in CI)
    detectors = [
        detect_prettier,
        detect_eslint,
        detect_typescript,
        detect_black,
        detect_ruff,
        detect_mypy,
        detect_go_formatter,
        detect_golangci_lint,
        detect_rustfmt,
        detect_clippy
    ]

    for detector in detectors:
        result = detector(project_path)
        if result and result['tool'] not in tools:
            tools[result['tool']] = result

    # 3. Apply fallback defaults
    if not tools:
        # Detect language first
        if os.path.exists(os.path.join(project_path, 'package.json')):
            tools['prettier'] = {'confidence': 40, 'source': 'default'}
            tools['eslint'] = {'confidence': 40, 'source': 'default'}
        elif os.path.exists(os.path.join(project_path, 'pyproject.toml')):
            tools['black'] = {'confidence': 40, 'source': 'default'}
            tools['ruff'] = {'confidence': 40, 'source': 'default'}
        elif os.path.exists(os.path.join(project_path, 'go.mod')):
            tools['gofumpt'] = {'confidence': 40, 'source': 'default'}
        elif os.path.exists(os.path.join(project_path, 'Cargo.toml')):
            tools['rustfmt'] = {'confidence': 40, 'source': 'default'}

    return tools
```

**Usage**:

```python
tools = detect_all_tools('/path/to/project')

print("Detected tools:")
for tool, info in tools.items():
    print(f"  {tool}: {info['confidence']}% confidence ({info.get('source', 'N/A')})")

# Get formatter for auto-fix
formatter = next((t for t in tools if 'confidence' in tools[t] and tools[t]['confidence'] > 60), None)
if formatter:
    print(f"\nRecommended formatter: {formatter}")
```

---

## Model Strategy

**Detection tasks are Haiku-friendly**:

- File existence checks
- Config file reading
- Pattern matching in workflows
- Command detection

**Use Haiku for**:

- Running detection functions
- Parsing config files
- Checking file existence
- Extracting commands from workflows

**Use Sonnet when**:

- User has conflicting tools
- Need to explain trade-offs
- Choosing between multiple valid options
- No clear tool detected and need recommendations

---

## Summary

**Detection Priority Order**:

1. ✅ **CI Workflows** (99% confidence) - What CI actually runs
2. ✅ **Config Files** (90-95% confidence) - Explicit configuration
3. ✅ **Package Scripts** (75-85% confidence) - Defined scripts
4. ⚠️ **Dependencies** (60-70% confidence) - Installed but may not be used
5. ⚠️ **Language Defaults** (40-50% confidence) - Best guess

**Key Insight**: Always check CI workflows first - they represent ground truth.
