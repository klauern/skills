---
name: pr-conflict-resolver
description: Intelligently resolves merge conflicts by analyzing both branches and suggesting resolution strategies
version: 1.0.0
author: klauern
---

# PR Conflict Resolver

## Overview

The `pr-conflict-resolver` skill provides intelligent analysis and resolution of Git merge conflicts by:

1. **Detecting conflict patterns** and categorizing them by complexity
2. **Analyzing both sides** to understand the intent of each change
3. **Suggesting resolution strategies** based on conflict type and context
4. **Auto-resolving simple conflicts** when safe to do so
5. **Providing context-aware guidance** for manual resolution of complex conflicts

## When to Use This Skill

Use this skill when you need to:

- Resolve merge conflicts intelligently rather than manually
- Understand what changes are conflicting and why
- Get recommendations on resolution strategies
- Auto-resolve simple conflicts (whitespace, imports, formatting)
- Maintain code quality during conflict resolution

## Quick Start

```bash
User: Help me resolve these merge conflicts
# or use the command
User: /merge-conflicts
```

The skill will:

1. Detect all conflicted files
2. Parse and categorize each conflict
3. Analyze the intent of both branches
4. Suggest resolution strategies
5. Auto-resolve simple conflicts where safe
6. Guide you through complex conflicts

## How It Works

### Phase 1: Conflict Detection and Parsing

The skill begins by identifying all files with merge conflicts and parsing the conflict markers:

**Git Commands Used**:

```bash
git status --porcelain          # Find conflicted files
git show :1:path/to/file        # Get base version
git show :2:path/to/file        # Get "ours" (current branch)
git show :3:path/to/file        # Get "theirs" (incoming branch)
git log --oneline --graph -20   # Get commit context
```

**Conflict Marker Parsing**:

```
<<<<<<< HEAD (ours)
Current branch changes
=======
Incoming branch changes
>>>>>>> feature-branch (theirs)
```

**See**: [references/conflict_patterns.md](references/conflict_patterns.md) for detailed parsing rules

### Phase 2: Conflict Classification

Each conflict is categorized to determine the appropriate resolution strategy:

**Simple Conflicts** (Auto-resolvable):

- **Whitespace conflicts**: Different indentation or line endings
- **Import ordering**: Different import statement order
- **Formatting conflicts**: Code style differences
- **Non-overlapping changes**: Changes to different sections of code
- **Identical changes**: Both branches made the same change

**Medium Conflicts** (Suggest strategy):

- **Function signature changes**: Parameter additions/modifications
- **Variable renames**: One branch renamed, other branch used old name
- **Refactoring conflicts**: Structural changes vs. feature changes
- **Dependency updates**: Different versions of same dependency

**Complex Conflicts** (Manual resolution required):

- **Logic conflicts**: Different implementations of same functionality
- **State management conflicts**: Conflicting state handling approaches
- **API contract changes**: Breaking changes on both sides
- **Semantic conflicts**: Code that merges but breaks semantics

**See**: [references/conflict_patterns.md](references/conflict_patterns.md#conflict-classification) for classification algorithm

### Phase 3: Intent Analysis

The skill analyzes git history and code context to understand why each change was made:

**Context Gathering**:

```bash
# Get commit messages for context
git log origin/main..HEAD --oneline
git log origin/main..MERGE_HEAD --oneline

# Get full diff for each side
git diff origin/main...HEAD -- path/to/file
git diff origin/main...MERGE_HEAD -- path/to/file
```

**Intent Detection**:

- **Feature additions**: New functions, classes, or modules
- **Bug fixes**: Changes to existing logic
- **Refactoring**: Structural changes without behavior change
- **Performance optimizations**: Algorithm improvements
- **Breaking changes**: API modifications

**See**: [references/resolution_strategies.md](references/resolution_strategies.md#intent-analysis) for detailed analysis approach

### Phase 4: Resolution Strategy Selection

Based on classification and intent, the skill recommends a resolution approach:

**Auto-Resolve** (Simple conflicts):

1. Take both changes if non-overlapping
2. Standardize formatting to project style
3. Merge imports and sort according to conventions
4. Remove duplicate changes

**Merge Both** (Compatible changes):

1. Combine both implementations if they serve different purposes
2. Refactor to accommodate both approaches
3. Use feature flags if needed

**Choose Side** (Incompatible changes):

1. Take newer implementation if one supersedes the other
2. Prefer bug fix over feature if conflicting
3. Keep breaking change and update other side to match
4. Choose better implementation based on code quality

**Manual Resolution** (Complex conflicts):

1. Provide detailed analysis of both sides
2. Explain trade-offs and implications
3. Suggest refactoring approaches
4. Offer to help implement the resolution

**See**: [references/resolution_strategies.md](references/resolution_strategies.md) for complete strategy guide

### Phase 5: Resolution Execution

The skill applies the resolution strategy:

**For Auto-Resolved Conflicts**:

```bash
# Edit file to remove markers and apply resolution
# Stage the resolved file
git add path/to/file
```

**For Manual Conflicts**:

1. Show both versions with syntax highlighting
2. Explain what each side does
3. Provide recommendation
4. Help implement chosen resolution
5. Stage when complete

**Verification**:

```bash
# Ensure no conflict markers remain
git diff --check

# Show what will be committed
git diff --cached path/to/file
```

## Model Strategy

This skill uses different Claude models for optimal performance:

### Claude 4.5 Haiku

**Use for**:

- Git command execution
- Conflict marker parsing
- File I/O operations
- Pattern matching for simple conflicts
- Import sorting and formatting

### Claude 4.5 Sonnet

**Use for**:

- Intent analysis from commit history
- Complex conflict classification
- Resolution strategy selection
- Code quality assessment
- Natural language explanation of conflicts
- Manual resolution guidance

**See**: [references/implementation_guide.md](references/implementation_guide.md#model-selection-strategy) for detailed guidance

## Integration with /merge-conflicts Command

This skill powers the `/merge-conflicts` command workflow:

1. **/merge-conflicts** command invokes this skill
2. Skill analyzes conflicts and provides recommendations
3. Command guides user through resolution process
4. Skill handles auto-resolvable conflicts automatically
5. User resolves complex conflicts with skill guidance
6. Command commits the resolution

The skill can also be invoked directly for more interactive conflict resolution.

## Examples

### Example 1: Simple Import Conflict

**Scenario**: Both branches added imports in different order

```python
<<<<<<< HEAD
import os
import sys
from typing import Dict
=======
from typing import Dict
import os
import sys
>>>>>>> feature/add-type-hints
```

**Resolution**: Auto-resolve by sorting imports according to PEP 8

**See**: [references/example_resolutions.md](references/example_resolutions.md#example-1-import-ordering)

### Example 2: Function Signature Change

**Scenario**: One branch added a parameter, other branch called the function

**See**: [references/example_resolutions.md](references/example_resolutions.md#example-2-function-signature-conflict)

### Example 3: Refactoring vs. Feature

**Scenario**: Main branch refactored a class, feature branch added methods to old structure

**See**: [references/example_resolutions.md](references/example_resolutions.md#example-3-refactoring-conflict)

### Example 4: Logic Conflict

**Scenario**: Both branches implemented same feature differently

**See**: [references/example_resolutions.md](references/example_resolutions.md#example-4-logic-conflict)

## Best Practices

1. **Understand before resolving**: Always analyze what both sides are trying to achieve
2. **Prefer combining over choosing**: Look for ways to merge both changes when possible
3. **Test after resolution**: Run tests to ensure semantic correctness
4. **Keep commits focused**: Resolve conflicts in logical groups
5. **Document complex resolutions**: Add comments explaining non-obvious choices
6. **Ask for help**: For critical conflicts, involve the original authors

## Limitations

- Cannot detect semantic conflicts (code that merges but breaks semantics)
- May not understand domain-specific business logic
- Relies on good commit messages for intent analysis
- Cannot auto-resolve conflicts requiring new code
- Limited to text-based conflicts (cannot resolve binary conflicts)

## Requirements

- Git repository with merge conflicts
- Git CLI available
- Read access to both branches
- Understanding of the codebase being merged

## Configuration

The skill respects project conventions:

- **Formatting**: Uses existing `.editorconfig`, `.prettierrc`, or similar
- **Import sorting**: Follows language conventions (PEP 8, ESLint, etc.)
- **Code style**: Maintains consistency with surrounding code

## Error Handling

The skill gracefully handles:

- Binary file conflicts (suggests manual resolution)
- Deleted file conflicts (analyzes if deletion was intentional)
- Submodule conflicts (provides git submodule guidance)
- No conflict markers found (verifies merge state)
- Invalid conflict markers (reports parsing errors)

**See**: [references/implementation_guide.md](references/implementation_guide.md#error-handling) for details

## Reference Documentation

- **[Conflict Patterns](references/conflict_patterns.md)**: Detailed conflict type classification
- **[Resolution Strategies](references/resolution_strategies.md)**: Complete strategy guide with decision trees
- **[Example Resolutions](references/example_resolutions.md)**: Real-world conflict resolution examples
- **[Implementation Guide](references/implementation_guide.md)**: Technical implementation details

## Troubleshooting

### Conflict markers appear after resolution

- Check for nested conflict markers
- Ensure all markers removed: `git diff --check`

### Auto-resolution produced wrong result

- Review the change: `git diff --cached`
- Unstage and manually resolve: `git reset HEAD path/to/file`

### Cannot determine resolution strategy

- Provide more context about what each branch does
- Review commit messages: `git log --oneline`
- Consult with original authors

### Tests fail after resolution

- Conflict may be semantic rather than syntactic
- Review both implementations carefully
- Consider if refactoring is needed to accommodate both changes

## Version History

- **1.0.0** (2025-01-21): Initial release
  - Conflict detection and parsing
  - Classification by complexity
  - Intent analysis from git history
  - Resolution strategy recommendation
  - Auto-resolution of simple conflicts
  - Integration with /merge-conflicts command
