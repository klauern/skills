# PR Creator Implementation Guide

This document provides technical implementation details for the pr-creator skill.

## Workflow Phases

The skill operates in four distinct phases, each with specific responsibilities and model recommendations.

### Phase 1: Discovery

**Purpose**: Locate and parse PR templates

**Model**: Claude 3.5 Haiku (fast, efficient for file operations)

**Tasks**:
1. Search for template files in common locations
2. Read template content
3. Parse template structure
4. Identify required vs. optional fields

**Git Commands**:
```bash
# Find templates
fd -t f PULL_REQUEST_TEMPLATE .github/ docs/
fd -t f pull_request_template .github/

# Or fallback
find .github -name "*PULL_REQUEST*"
find . -maxdepth 2 -name "PULL_REQUEST*"
```

**Template Parsing Logic**:
```typescript
interface TemplateField {
  name: string;
  required: boolean;
  type: 'text' | 'checkbox' | 'select';
  options?: string[];
  defaultValue?: string;
}

function parseTemplate(content: string): TemplateField[] {
  // Extract sections (## Header)
  // Identify required markers ([Required], *, <!-- Required -->)
  // Detect checkboxes (- [ ])
  // Parse form fields (**Key**: value)
}
```

### Phase 2: Commit Analysis

**Purpose**: Analyze branch changes and extract information

**Model**: Mixed
- Claude 3.5 Haiku for git operations
- Claude 3.5 Sonnet for commit analysis and context understanding

**Git Commands**:
```bash
# Determine current and base branches
git rev-parse --abbrev-ref HEAD
git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'

# Alternative method for base branch
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'

# Get commit history
git log origin/main...HEAD --oneline --no-decorate
git log origin/main...HEAD --format='%H|%s|%b'

# Get file changes
git diff origin/main...HEAD --name-status
git diff origin/main...HEAD --stat

# Get detailed diff (for analysis)
git diff origin/main...HEAD

# Count commits
git rev-list --count origin/main...HEAD
```

**Information Extraction**:

| Field | Extraction Method |
|-------|------------------|
| Title | Most recent commit subject OR branch name pattern |
| Type | Conventional commit prefix (`feat:`, `fix:`, etc.) |
| Scope | Conventional commit scope OR common file path prefix |
| Issues | Parse `#123`, `closes #123`, `fixes #123` from commit messages |
| Breaking | Look for `BREAKING CHANGE:` or `!` in commits |
| Files | `git diff --name-status` |
| Test changes | Filter for `*.test.*`, `*_test.*`, `test_*.* ` files |
| Doc changes | Filter for `*.md`, `docs/**/*` files |

**Branch Name Patterns**:
```regex
# Feature
feature/(\d+)-(.+)      → Issue #$1, title from $2
feat/(.+)               → Type: feat, title from $1

# Bug fix
bugfix/(\d+)-(.+)       → Issue #$1, type: fix
fix/issue-(\d+)         → Issue #$1, type: fix
hotfix/(.+)             → Type: fix, urgent

# Other
docs/(.+)               → Type: docs
refactor/(.+)           → Type: refactor
chore/(.+)              → Type: chore
```

### Phase 3: Intelligent Gap Filling

**Purpose**: Determine missing information and prompt user strategically

**Model**: Claude 3.5 Sonnet (complex reasoning required)

**Gap Detection Algorithm**:
```typescript
interface GapAnalysis {
  field: string;
  canInfer: boolean;
  confidence: 'high' | 'medium' | 'low';
  inferredValue?: string;
  needsUserInput: boolean;
  promptSuggestion?: string;
}

function analyzeGaps(
  template: TemplateField[],
  commits: Commit[],
  files: FileChange[]
): GapAnalysis[] {
  // For each required field:
  // 1. Attempt inference
  // 2. Assess confidence
  // 3. Decide if user input needed
}
```

**Inference Confidence Levels**:

- **High**: Can directly extract from commits/files
  - Issue number from commit message
  - Type from conventional commit prefix
  - Files changed from git diff

- **Medium**: Can make educated guess
  - Title from commit messages (multiple commits = need synthesis)
  - Scope from file paths
  - Test status from file changes

- **Low**: Requires user knowledge
  - "Why" or "Motivation" sections
  - Manual test steps
  - Screenshots
  - Migration guides

**Prompting Strategy**:
```typescript
function generatePrompt(gap: GapAnalysis): string {
  if (gap.canInfer && gap.confidence === 'high') {
    // Confirm with user
    return `I inferred "${gap.field}" as: ${gap.inferredValue}. Is this correct? (y/n)`;
  }

  if (gap.canInfer && gap.confidence === 'medium') {
    // Suggest with context
    return `For "${gap.field}", I'm thinking: ${gap.inferredValue}. Does this sound right, or would you like to provide something different?`;
  }

  // Need user input
  return `${gap.promptSuggestion || `Please provide: ${gap.field}`}`;
}
```

### Phase 4: PR Generation

**Purpose**: Compose and create the pull request

**Model**: Claude 3.5 Sonnet (for final composition and formatting)

**PR Creation**:
```bash
# Basic PR creation
gh pr create \
  --title "feat: Add user profile API" \
  --body "$(cat pr_body.md)" \
  --base main

# With additional options
gh pr create \
  --title "..." \
  --body "..." \
  --base main \
  --draft \  # Create as draft
  --label "enhancement,api" \
  --assignee "@me" \
  --reviewer "teammate1,teammate2" \
  --milestone "v2.0"

# Multiple templates (specify which one)
gh pr create \
  --title "..." \
  --body-file .github/PULL_REQUEST_TEMPLATE/feature.md
```

**PR Body Composition**:
```markdown
## [TEMPLATE SECTION 1]
[Filled content from template + inferred/user data]

## [TEMPLATE SECTION 2]
[Filled content]

---
<!-- Auto-generated section -->
### Commits in this PR
- [abc1234] feat(api): add endpoint
- [def5678] test(api): add tests

### Files Changed (N files)
**Added (X files)**
- path/to/new/file.js

**Modified (Y files)**
- path/to/existing/file.js (+10, -5)

**Deleted (Z files)**
- path/to/removed/file.js
```

**Post-Creation Actions**:
```bash
# Add labels based on type
if [[ $type == "feat" ]]; then
  gh pr edit $pr_number --add-label "enhancement"
elif [[ $type == "fix" ]]; then
  gh pr edit $pr_number --add-label "bug"
fi

# Link issues
gh pr edit $pr_number --add-project "Backend API"

# Request reviewers (if configured in .github/CODEOWNERS)
gh pr edit $pr_number --add-reviewer "team-backend"
```

## Model Selection Strategy

### When to Use Claude 3.5 Haiku

**Criteria**: Task is deterministic, well-defined, and requires speed

**Examples**:
- Reading files
- Running git commands
- Parsing template structure
- Extracting field names
- Counting files/commits
- Simple pattern matching

**Code Example**:
```typescript
// Good for Haiku
function findTemplates(): string[] {
  return execSync('fd PULL_REQUEST_TEMPLATE .github').toString().split('\n');
}

function parseCheckboxes(content: string): Checkbox[] {
  const regex = /- \[([ xX])\] (.+)/g;
  // Simple regex parsing
}
```

### When to Use Claude 3.5 Sonnet

**Criteria**: Task requires reasoning, context understanding, or creativity

**Examples**:
- Analyzing commit intent ("Why was this change made?")
- Synthesizing multiple commits into a coherent summary
- Detecting gaps in required information
- Generating natural language descriptions
- Making recommendations
- Complex decision-making

**Code Example**:
```typescript
// Good for Sonnet
function generatePRSummary(commits: Commit[], files: FileChange[]): string {
  // Requires understanding of:
  // - What changes actually mean
  // - How commits relate to each other
  // - What's important vs. trivial
  // - Natural language generation
}

function detectGaps(template: Template, data: InferredData): Gap[] {
  // Requires reasoning about:
  // - What can be inferred vs. what can't
  // - Confidence levels
  // - How to phrase prompts
}
```

## Error Handling

### Common Errors and Recovery

**No base branch found**:
```bash
# Try multiple methods
base=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [[ -z "$base" ]]; then
  base=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name' 2>/dev/null)
fi
if [[ -z "$base" ]]; then
  # Ask user
  echo "Cannot determine base branch. Please specify: (main/master/develop)"
fi
```

**No commits in branch**:
```bash
commit_count=$(git rev-list --count origin/main...HEAD 2>/dev/null)
if [[ $commit_count -eq 0 ]]; then
  echo "Error: No commits found. Are you on the correct branch?"
  echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"
  exit 1
fi
```

**Template not found**:
```bash
# Fallback to default template
if [[ ! -f "$template_path" ]]; then
  echo "No PR template found. Using default structure."
  use_default_template=true
fi
```

**gh CLI not installed**:
```bash
if ! command -v gh &> /dev/null; then
  echo "Error: GitHub CLI (gh) is required but not installed."
  echo "Install: https://cli.github.com/"
  exit 1
fi
```

**Not authenticated with gh**:
```bash
if ! gh auth status &> /dev/null; then
  echo "Not authenticated with GitHub CLI."
  echo "Run: gh auth login"
  exit 1
fi
```

## Performance Optimization

### Parallel Operations

When possible, run independent git commands in parallel:

```bash
# Sequential (slow)
commits=$(git log origin/main...HEAD)
files=$(git diff origin/main...HEAD --name-status)
stat=$(git diff origin/main...HEAD --stat)

# Parallel (fast)
commits=$(git log origin/main...HEAD) &
files=$(git diff origin/main...HEAD --name-status) &
stat=$(git diff origin/main...HEAD --stat) &
wait
```

### Caching

Cache expensive operations:

```bash
# Cache base branch (doesn't change during PR creation)
BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')

# Cache commit list (read once, use multiple times)
COMMITS=$(git log origin/$BASE_BRANCH...HEAD --format='%H|%s|%b')
```

### Minimal Diffs

For large PRs, avoid full diffs:

```bash
# Instead of full diff (can be huge)
git diff origin/main...HEAD

# Use stat for overview
git diff origin/main...HEAD --stat

# Only get full diff if needed
if [[ $needs_detailed_analysis == true ]]; then
  git diff origin/main...HEAD
fi
```

## Testing the Skill

### Manual Testing Scenarios

1. **Feature branch with template**
   ```bash
   git checkout -b feature/123-test-feature
   # Make changes
   # Test: /pr
   ```

2. **Bug fix without template**
   ```bash
   git checkout -b fix/memory-leak
   # Remove .github/PULL_REQUEST_TEMPLATE.md
   # Test: /pr
   ```

3. **Multiple commits**
   ```bash
   # Make 5+ commits with various types
   # Test: Skill should synthesize all commits
   ```

4. **Breaking change**
   ```bash
   git commit -m "feat!: remove deprecated API"
   # Test: Should detect breaking change
   ```

5. **No commits**
   ```bash
   git checkout -b empty-branch
   # Test: Should handle gracefully
   ```

### Validation Checklist

- [ ] Template discovered correctly
- [ ] Required fields identified
- [ ] Optional fields recognized
- [ ] Commits analyzed accurately
- [ ] Issue numbers extracted from commits
- [ ] Breaking changes detected
- [ ] Test file changes detected
- [ ] Documentation changes detected
- [ ] Title generated appropriately
- [ ] Type inferred correctly
- [ ] User prompted only for gaps
- [ ] PR created successfully
- [ ] Labels applied correctly
- [ ] Issues linked properly
