# Action Detection Patterns

This document describes how to detect and parse GitHub Actions references in workflow files.

## Action Reference Formats

GitHub Actions can be referenced in several formats:

### 1. Standard Format

```yaml
uses: owner/repo@ref
```

**Examples**:
- `actions/checkout@v4`
- `actions/setup-node@v3.8.0`
- `azure/login@v1`

**Components**:
- `owner`: GitHub organization or user
- `repo`: Repository name
- `ref`: Version reference (tag, branch, or SHA)

### 2. Subdirectory Actions

```yaml
uses: owner/repo/path/to/action@ref
```

**Examples**:
- `actions/aws/ec2@v1`
- `custom-org/monorepo/actions/deploy@main`

### 3. Local Actions

```yaml
uses: ./.github/actions/my-action
```

**Note**: Local actions should be skipped during upgrade detection.

### 4. Docker Actions

```yaml
uses: docker://alpine:3.8
```

**Note**: Docker actions should be skipped during upgrade detection.

### 5. Full Repository URL

```yaml
uses: https://github.com/owner/repo@ref
```

**Note**: Rare format, but should be normalized to standard format.

## Detection Algorithm

### Step 1: Find Workflow Files

```bash
find .github/workflows -type f \( -name "*.yml" -o -name "*.yaml" \)
```

### Step 2: Extract Action References

Parse YAML and extract all `uses:` directives:

```bash
# Using yq (recommended)
yq eval '.jobs.*.steps[].uses' .github/workflows/*.yml

# Using grep (fallback)
rg 'uses:\s+(.+)' .github/workflows/ -o -r '$1'
```

### Step 3: Parse Action Components

For each action reference, extract:

```text
actions/checkout@v4
  ↓
owner: actions
repo: checkout
ref: v4
full_name: actions/checkout
```

**Regex pattern**:
```regex
^([^/]+)/([^@/]+)(?:/([^@]+))?@(.+)$
```

**Capture groups**:
1. Owner
2. Repository
3. Subdirectory (optional)
4. Reference

### Step 4: Categorize Actions

**Should analyze**:
- GitHub actions (owner/repo format)
- Has version reference
- Not a local action

**Should skip**:
- Local actions (starts with `./`)
- Docker images (starts with `docker://`)
- Full URLs (convert to standard format first)

## YAML Parsing

### Using yq

```bash
# List all action uses
yq eval '.jobs.*.steps[].uses' workflow.yml

# Get action with job context
yq eval '.jobs[] | .steps[] | select(.uses) | {job: parent | key, name: .name, uses: .uses}' workflow.yml
```

### Using Python

```python
import yaml

with open('.github/workflows/ci.yml') as f:
    workflow = yaml.safe_load(f)

actions = []
for job_name, job in workflow['jobs'].items():
    for step in job.get('steps', []):
        if 'uses' in step:
            actions.append({
                'job': job_name,
                'step_name': step.get('name', 'unnamed'),
                'uses': step['uses'],
                'with': step.get('with', {})
            })
```

### Using Node.js

```javascript
const yaml = require('yaml');
const fs = require('fs');

const workflow = yaml.parse(fs.readFileSync('.github/workflows/ci.yml', 'utf8'));

const actions = [];
for (const [jobName, job] of Object.entries(workflow.jobs)) {
    for (const step of job.steps || []) {
        if (step.uses) {
            actions.push({
                job: jobName,
                stepName: step.name || 'unnamed',
                uses: step.uses,
                with: step.with || {}
            });
        }
    }
}
```

## Version Reference Formats

Actions can be referenced by:

### 1. Tag (Recommended)

```yaml
uses: actions/checkout@v4
uses: actions/checkout@v4.1.0
```

**Semantic version tags**: Most common and recommended.

### 2. Branch

```yaml
uses: actions/checkout@main
uses: actions/checkout@develop
```

**Warning**: Using branches is discouraged (unpredictable changes).

### 3. Commit SHA

```yaml
uses: actions/checkout@a12b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t
```

**Full SHA**: Most secure but hard to upgrade.

### 4. Short SHA

```yaml
uses: actions/checkout@a12b3c4
```

**Warning**: Short SHAs can be ambiguous.

## Common Patterns to Detect

### Pattern 1: Simple Actions

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
```

### Pattern 2: Actions with Parameters

```yaml
steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0
      submodules: true
```

### Pattern 3: Conditional Actions

```yaml
steps:
  - uses: actions/cache@v3
    if: runner.os == 'Linux'
```

### Pattern 4: Matrix Actions

```yaml
strategy:
  matrix:
    node: [16, 18, 20]
steps:
  - uses: actions/setup-node@v4
    with:
      node-version: ${{ matrix.node }}
```

## Edge Cases

### 1. Composite Actions

Composite actions may reference other actions:

```yaml
# .github/actions/my-action/action.yml
runs:
  using: composite
  steps:
    - uses: actions/checkout@v4
```

**Handling**: Parse composite action definitions recursively.

### 2. Reusable Workflows

Workflows can call other workflows:

```yaml
jobs:
  call-workflow:
    uses: owner/repo/.github/workflows/workflow.yml@v1
```

**Handling**: Track separately from actions.

### 3. Action Comments

```yaml
steps:
  # TODO: Upgrade to v4
  - uses: actions/checkout@v3
```

**Handling**: Preserve comments when updating.

### 4. Multiline Actions

```yaml
steps:
  - uses: >-
      actions/checkout@v4
```

**Handling**: Parse YAML correctly to handle multiline strings.

## Detection Output Format

For each detected action, output:

```json
{
  "workflow_file": ".github/workflows/ci.yml",
  "job_name": "build",
  "step_name": "Checkout code",
  "action": {
    "owner": "actions",
    "repo": "checkout",
    "subdirectory": null,
    "ref": "v3",
    "ref_type": "tag",
    "full_name": "actions/checkout"
  },
  "parameters": {
    "fetch-depth": "0"
  },
  "line_number": 15
}
```

## Tools and Libraries

### Recommended Tools

- **yq**: YAML processing (`brew install yq`)
- **jq**: JSON processing (built-in with gh CLI)
- **rg (ripgrep)**: Fast searching (`brew install ripgrep`)

### Recommended Libraries

**Python**:
- `pyyaml`: YAML parsing
- `ruamel.yaml`: YAML parsing with comment preservation

**Node.js**:
- `yaml`: Modern YAML parser
- `js-yaml`: Traditional YAML parser

**Go**:
- `gopkg.in/yaml.v3`: YAML parsing

## Next Steps

After detection:
1. [Analyze each action](analysis_guide.md) to check fork status
2. [Discover available upgrades](upgrade_detection.md)
3. [Generate upgrade plans](planning_strategy.md)
