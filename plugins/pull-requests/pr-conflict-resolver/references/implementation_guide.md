# Implementation Guide

This document provides technical implementation details for the pr-conflict-resolver skill.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Request                            │
│              "Help me resolve conflicts"                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Conflict Detection (Haiku)                      │
│  - git status --porcelain                                    │
│  - Find conflicted files                                     │
│  - Extract git context                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            Conflict Parsing (Haiku)                          │
│  - Read files with conflict markers                          │
│  - Parse <<<<<<, =======, >>>>>>> markers                    │
│  - Extract ours/base/theirs versions                         │
│  - Get surrounding context                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│         Conflict Classification (Sonnet)                     │
│  - Analyze conflict type                                     │
│  - Categorize complexity                                     │
│  - Identify patterns                                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│             Intent Analysis (Sonnet)                         │
│  - Analyze commit messages                                   │
│  - Understand code changes                                   │
│  - Determine purpose of each side                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│       Resolution Strategy Selection (Sonnet)                 │
│  - Match conflict to strategy                                │
│  - Consider intent and priority rules                        │
│  - Choose resolution approach                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                ┌─────┴─────┐
                │           │
┌───────────────▼─┐   ┌─────▼────────────────────────────────┐
│  Auto-Resolve   │   │    Manual Resolution Guidance        │
│     (Haiku)     │   │          (Sonnet)                    │
│  - Apply fix    │   │  - Present both versions             │
│  - Stage file   │   │  - Explain differences               │
└─────────────────┘   │  - Recommend approach                │
                      │  - Assist implementation             │
                      └──────────────────────────────────────┘
```

## Phase 1: Conflict Detection

### Objective

Identify all files with merge conflicts and gather git context.

### Model

**Claude 4.5 Haiku** - Fast I/O operations and simple parsing

### Implementation

```python
def detect_conflicts():
    """Detect all files with merge conflicts."""
    # Check if we're in a merge state
    merge_head = run_git(['rev-parse', '--verify', 'MERGE_HEAD'])
    if not merge_head:
        return None, "Not in a merge state"

    # Get conflicted files
    status = run_git(['status', '--porcelain'])
    conflicted_files = []
    for line in status.splitlines():
        if line.startswith('UU '):  # Both modified
            conflicted_files.append(line[3:])

    # Get git context
    context = {
        'current_branch': run_git(['rev-parse', '--abbrev-ref', 'HEAD']),
        'merging_branch': run_git(['rev-parse', '--abbrev-ref', 'MERGE_HEAD']),
        'commit_graph': run_git(['log', '--oneline', '--graph', '--all', '-20']),
        'our_commits': run_git(['log', '--oneline', 'origin/main..HEAD']),
        'their_commits': run_git(['log', '--oneline', 'origin/main..MERGE_HEAD']),
    }

    return conflicted_files, context
```

### Error Handling

```python
def run_git(args):
    """Run git command with error handling."""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Handle specific git errors
        if 'MERGE_HEAD' in str(e):
            return None  # Not in merge state
        raise
```

## Phase 2: Conflict Parsing

### Objective

Parse conflict markers and extract all versions.

### Model

**Claude 4.5 Haiku** - Pattern matching and file I/O

### Implementation

```python
class Conflict:
    def __init__(self, file_path, start_line, end_line):
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.ours = []
        self.base = []
        self.theirs = []
        self.context_before = []
        self.context_after = []

def parse_conflicts(file_path):
    """Parse conflict markers in a file."""
    conflicts = []
    current_conflict = None
    state = 'NORMAL'

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        if line.startswith('<<<<<<<'):
            # Start of conflict
            current_conflict = Conflict(file_path, i, None)
            current_conflict.context_before = lines[max(0, i-6):i-1]
            state = 'OURS'
        elif line.startswith('|||||||'):
            # Base version (optional)
            state = 'BASE'
        elif line.startswith('======='):
            # Separator
            state = 'THEIRS'
        elif line.startswith('>>>>>>>'):
            # End of conflict
            current_conflict.end_line = i
            current_conflict.context_after = lines[i:min(len(lines), i+5)]
            state = 'NORMAL'
            conflicts.append(current_conflict)
            current_conflict = None
        else:
            # Add line to appropriate section
            if state == 'OURS':
                current_conflict.ours.append(line)
            elif state == 'BASE':
                current_conflict.base.append(line)
            elif state == 'THEIRS':
                current_conflict.theirs.append(line)

    return conflicts
```

### Extracting Git Versions

```bash
# Get the three versions from git index
git show :1:path/to/file  # Base (common ancestor)
git show :2:path/to/file  # Ours (current branch)
git show :3:path/to/file  # Theirs (incoming branch)
```

```python
def get_git_versions(file_path):
    """Get all three versions from git index."""
    versions = {}

    for stage, name in [(1, 'base'), (2, 'ours'), (3, 'theirs')]:
        try:
            content = run_git(['show', f':{stage}:{file_path}'])
            versions[name] = content
        except:
            versions[name] = None  # Version doesn't exist

    return versions
```

## Phase 3: Conflict Classification

### Objective

Categorize conflicts by type and complexity.

### Model

**Claude 4.5 Sonnet** - Pattern recognition and reasoning

### Implementation

```python
def classify_conflict(conflict):
    """Classify a conflict by type."""
    ours = ''.join(conflict.ours)
    theirs = ''.join(conflict.theirs)

    # Check for simple patterns first
    if ours == theirs:
        return ConflictType.IDENTICAL

    if only_whitespace_diff(ours, theirs):
        return ConflictType.WHITESPACE

    if is_import_reorder(ours, theirs):
        return ConflictType.IMPORT_ORDER

    if is_non_overlapping(ours, theirs, conflict.base):
        return ConflictType.NON_OVERLAPPING

    # Check for medium complexity
    if is_signature_change(ours, theirs):
        return ConflictType.SIGNATURE_CHANGE

    if is_rename(ours, theirs):
        return ConflictType.RENAME

    # Default to complex
    return ConflictType.COMPLEX

def only_whitespace_diff(ours, theirs):
    """Check if difference is only whitespace."""
    import re
    # Normalize whitespace
    ours_norm = re.sub(r'\s+', ' ', ours).strip()
    theirs_norm = re.sub(r'\s+', ' ', theirs).strip()
    return ours_norm == theirs_norm

def is_import_reorder(ours, theirs):
    """Check if conflict is just import reordering."""
    # Extract import statements
    import_pattern = r'^(?:import|from)\s+.*$'

    ours_imports = set(re.findall(import_pattern, ours, re.MULTILINE))
    theirs_imports = set(re.findall(import_pattern, theirs, re.MULTILINE))

    # Same imports, different order
    return ours_imports == theirs_imports and len(ours_imports) > 0
```

## Phase 4: Intent Analysis

### Objective

Understand why each change was made.

### Model

**Claude 4.5 Sonnet** - Natural language understanding and code analysis

### Implementation

```python
def analyze_intent(conflict, git_context):
    """Analyze the intent behind both changes."""
    # Get commits that modified this region
    file_path = conflict.file_path
    line_range = f"{conflict.start_line},{conflict.end_line}"

    our_commits = run_git([
        'log',
        '-L', f'{line_range}:{file_path}',
        'origin/main..HEAD',
        '--format=%h %s'
    ])

    their_commits = run_git([
        'log',
        '-L', f'{line_range}:{file_path}',
        'origin/main..MERGE_HEAD',
        '--format=%h %s'
    ])

    # Analyze commit messages
    our_intent = categorize_intent(our_commits)
    their_intent = categorize_intent(their_commits)

    # Analyze code changes
    our_changes = analyze_code_changes(''.join(conflict.ours), conflict.base)
    their_changes = analyze_code_changes(''.join(conflict.theirs), conflict.base)

    return {
        'ours': {
            'intent': our_intent,
            'commits': our_commits,
            'changes': our_changes,
        },
        'theirs': {
            'intent': their_intent,
            'commits': their_commits,
            'changes': their_changes,
        }
    }

def categorize_intent(commits):
    """Categorize intent from commit messages."""
    intents = set()

    for commit in commits.splitlines():
        message = commit.lower()

        if any(kw in message for kw in ['fix', 'bug', 'issue']):
            intents.add('bug_fix')
        if any(kw in message for kw in ['feat', 'add', 'implement']):
            intents.add('feature')
        if any(kw in message for kw in ['refactor', 'restructure']):
            intents.add('refactor')
        if any(kw in message for kw in ['perf', 'optimize']):
            intents.add('performance')
        if any(kw in message for kw in ['breaking', 'remove']):
            intents.add('breaking_change')

    return list(intents)
```

## Phase 5: Resolution Strategy Selection

### Objective

Choose the best resolution approach based on classification and intent.

### Model

**Claude 4.5 Sonnet** - Decision-making and reasoning

### Implementation

```python
def select_strategy(conflict, classification, intent_analysis):
    """Select resolution strategy for a conflict."""
    # Simple conflicts - auto-resolve
    if classification in [
        ConflictType.IDENTICAL,
        ConflictType.WHITESPACE,
        ConflictType.IMPORT_ORDER,
    ]:
        return ResolutionStrategy.AUTO_RESOLVE

    if classification == ConflictType.NON_OVERLAPPING:
        return ResolutionStrategy.MERGE_BOTH

    # Apply priority rules for medium/complex conflicts
    our_intent = intent_analysis['ours']['intent']
    their_intent = intent_analysis['theirs']['intent']

    # Bug fix takes priority
    if 'bug_fix' in our_intent and 'bug_fix' not in their_intent:
        return ResolutionStrategy.CHOOSE_OURS

    if 'bug_fix' in their_intent and 'bug_fix' not in our_intent:
        return ResolutionStrategy.CHOOSE_THEIRS

    # Breaking changes need careful handling
    if 'breaking_change' in our_intent or 'breaking_change' in their_intent:
        return ResolutionStrategy.MANUAL_WITH_GUIDANCE

    # Refactoring vs feature - adapt feature to refactoring
    if 'refactor' in our_intent and 'feature' in their_intent:
        return ResolutionStrategy.ADAPT_TO_REFACTOR

    # Complex logic conflicts
    if classification == ConflictType.COMPLEX:
        return ResolutionStrategy.MANUAL_WITH_GUIDANCE

    # Default
    return ResolutionStrategy.MANUAL_WITH_GUIDANCE
```

## Phase 6: Resolution Execution

### Auto-Resolution (Haiku)

```python
def auto_resolve(conflict, strategy):
    """Automatically resolve simple conflicts."""
    if strategy == ConflictType.WHITESPACE:
        return auto_resolve_whitespace(conflict)
    elif strategy == ConflictType.IMPORT_ORDER:
        return auto_resolve_imports(conflict)
    elif strategy == ConflictType.IDENTICAL:
        return auto_resolve_identical(conflict)
    elif strategy == ConflictType.NON_OVERLAPPING:
        return auto_resolve_non_overlapping(conflict)

def auto_resolve_whitespace(conflict):
    """Resolve whitespace conflicts."""
    # Use project formatter if available
    content = ''.join(conflict.ours)

    # Try formatters in order
    formatters = [
        ('python', ['black', '-']),
        ('javascript', ['prettier', '--stdin-filepath', 'file.js']),
        ('go', ['gofmt']),
    ]

    for lang, cmd in formatters:
        try:
            result = subprocess.run(
                cmd,
                input=content,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except:
            continue

    # Fallback: normalize whitespace manually
    return normalize_whitespace(content)
```

### Manual Resolution Guidance (Sonnet)

```python
def provide_guidance(conflict, intent_analysis):
    """Provide detailed guidance for manual resolution."""
    guidance = {
        'location': f"{conflict.file_path}:{conflict.start_line}-{conflict.end_line}",
        'type': classify_conflict(conflict),
        'our_changes': {
            'content': ''.join(conflict.ours),
            'intent': intent_analysis['ours']['intent'],
            'commits': intent_analysis['ours']['commits'],
        },
        'their_changes': {
            'content': ''.join(conflict.theirs),
            'intent': intent_analysis['theirs']['intent'],
            'commits': intent_analysis['theirs']['commits'],
        },
        'recommendation': generate_recommendation(conflict, intent_analysis),
        'trade_offs': analyze_trade_offs(conflict, intent_analysis),
    }

    return format_guidance(guidance)

def generate_recommendation(conflict, intent_analysis):
    """Generate resolution recommendation."""
    # Analyze both approaches
    our_approach = analyze_approach(''.join(conflict.ours))
    their_approach = analyze_approach(''.join(conflict.theirs))

    # Compare and recommend
    if our_approach['complexity'] < their_approach['complexity']:
        return {
            'choice': 'ours',
            'reason': 'Simpler implementation with same functionality'
        }

    # More sophisticated analysis using Sonnet...
    return generate_detailed_recommendation(
        our_approach,
        their_approach,
        intent_analysis
    )
```

## Model Selection Strategy

### When to Use Haiku 4.5

Use Haiku for operations that are:

1. **I/O-bound**: File reading, git commands, status checks
2. **Pattern matching**: Regex, simple string comparisons
3. **Deterministic**: Clear rules, no ambiguity
4. **Fast-path**: Operations in the critical path

**Examples**:
- Detecting conflicted files
- Parsing conflict markers
- Running git commands
- Formatting code
- Applying auto-resolutions

### When to Use Sonnet 4.5

Use Sonnet for operations requiring:

1. **Reasoning**: Understanding intent, making decisions
2. **Analysis**: Code understanding, trade-off evaluation
3. **Natural language**: Generating explanations, recommendations
4. **Ambiguity handling**: Multiple valid approaches

**Examples**:
- Classifying complex conflicts
- Analyzing commit history for intent
- Selecting resolution strategies
- Generating resolution guidance
- Explaining trade-offs

### Workflow Example

```python
# Detection phase - Haiku (fast I/O)
conflicts = detect_conflicts()  # Haiku

for conflict in conflicts:
    # Parsing - Haiku (pattern matching)
    parsed = parse_conflicts(conflict)  # Haiku

    # Classification - Sonnet (reasoning)
    classification = classify_conflict(parsed)  # Sonnet

    if classification.is_simple:
        # Auto-resolve - Haiku (deterministic)
        resolution = auto_resolve(parsed)  # Haiku
    else:
        # Guidance - Sonnet (analysis & explanation)
        guidance = provide_guidance(parsed)  # Sonnet
```

## Error Handling

### Binary File Conflicts

```python
def handle_binary_conflict(file_path):
    """Handle binary file conflicts."""
    return {
        'type': 'binary',
        'message': f'Binary file conflict in {file_path}',
        'options': [
            'Choose ours (git checkout --ours <file>)',
            'Choose theirs (git checkout --theirs <file>)',
            'Use external merge tool (git mergetool)',
        ]
    }
```

### Submodule Conflicts

```python
def handle_submodule_conflict(file_path):
    """Handle submodule conflicts."""
    our_commit = run_git(['ls-files', '-u', '--stage', file_path])
    their_commit = run_git(['ls-files', '-u', '--stage', file_path])

    return {
        'type': 'submodule',
        'message': f'Submodule conflict in {file_path}',
        'our_commit': parse_submodule_commit(our_commit),
        'their_commit': parse_submodule_commit(their_commit),
        'recommendation': 'Choose the newer commit or update submodule manually'
    }
```

### Invalid Conflict Markers

```python
def validate_conflict_markers(file_path):
    """Validate conflict marker structure."""
    with open(file_path, 'r') as f:
        content = f.read()

    markers = {
        'start': content.count('<<<<<<<'),
        'separator': content.count('======='),
        'end': content.count('>>>>>>>'),
    }

    if markers['start'] != markers['end']:
        return False, 'Unmatched conflict markers'

    if markers['separator'] != markers['end']:
        return False, 'Missing separator markers'

    return True, 'Valid'
```

## Performance Optimization

### Conflict Parsing

- Parse conflicts lazily (only when needed)
- Cache parsed results
- Limit context lines to reasonable amount (5-10 lines)

### Git Operations

- Batch git commands when possible
- Use --cached to avoid unnecessary disk I/O
- Limit log output with -n flag

### Model Usage

- Use Haiku for the fast path (detection, parsing, auto-resolve)
- Use Sonnet only when reasoning is needed
- Cache classification results

## Testing

### Unit Tests

```python
def test_parse_simple_conflict():
    """Test parsing a simple conflict."""
    content = """
line 1
<<<<<<< HEAD
ours
=======
theirs
>>>>>>> feature
line 2
"""
    conflicts = parse_conflicts_from_string(content)
    assert len(conflicts) == 1
    assert conflicts[0].ours == ['ours\n']
    assert conflicts[0].theirs == ['theirs\n']

def test_classify_whitespace_conflict():
    """Test whitespace conflict classification."""
    conflict = Conflict(
        ours=['def foo():\n', '    pass\n'],
        theirs=['def foo():\n', '\tpass\n']
    )
    assert classify_conflict(conflict) == ConflictType.WHITESPACE
```

### Integration Tests

```python
def test_resolve_real_conflict():
    """Test resolving a real merge conflict."""
    # Set up git repository with conflict
    repo = create_test_repo()
    create_conflict(repo)

    # Run resolver
    conflicts = detect_conflicts()
    resolutions = [resolve_conflict(c) for c in conflicts]

    # Verify
    assert all(r.success for r in resolutions)
    assert no_conflict_markers_remain(repo)
```

## Configuration

Allow users to configure resolution preferences:

```yaml
# .pr-conflict-resolver.yml
auto_resolve:
  enabled: true
  types:
    - whitespace
    - import_order
    - identical

formatting:
  python: black
  javascript: prettier
  go: gofumpt

priorities:
  bug_fix: highest
  security: highest
  feature: medium
  refactor: medium
  docs: low
```

```python
def load_config():
    """Load user configuration."""
    config_path = find_config_file()
    if config_path:
        with open(config_path) as f:
            return yaml.safe_load(f)
    return default_config()
```
