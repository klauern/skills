---
name: jira-interaction
description: Interact with Jira issues using the jira CLI - view issues, add comments, and update tickets. Use when you need to read Jira tickets or add updates/comments to existing issues.
---

# Jira Interaction Skill

You are a Jira interaction specialist. This skill covers the `jira` CLI (go-jira) for quick operations.

## Default Configuration

- **Default Project Prefix**: FSEC

## Tool Selection

| Tool | Best For |
|------|----------|
| `jira` CLI (go-jira) | Quick views, adding comments, general ticket operations |
| Python scripts (fsec-jira) | FSEC custom fields, bulk updates, dry-run previews, checklists |

**When to use Python scripts instead** (see [fsec-jira skill](fsec-jira/SKILL.md)):
- Setting FSEC custom fields: `--planned`, `--unplanned`, `--work-attribution`, `--points`, `--acceptance-criteria`
- Creating tickets with FSEC-specific fields
- Managing HeroCoders Checklist items
- Previewing changes with `--dry-run`
- Working with components programmatically

## Core Commands

### Viewing Issues

**View an issue:**
```bash
jira issue view <ISSUE-KEY>
```

**View with comments:**
```bash
jira issue view <ISSUE-KEY> --comments 50
```

**View raw JSON (for detailed parsing):**
```bash
jira issue view <ISSUE-KEY> --raw
```

### Adding Comments

**IMPORTANT**: The `jira issue comment add` command does NOT use `--comment` flag!

**Correct usage:**
```bash
# Method 1: Direct string (use for short comments)
jira issue comment add ISSUE-KEY "Your comment here"

# Method 2: Template file (use for long/formatted comments)
jira issue comment add ISSUE-KEY --template /path/to/comment.txt

# Method 3: Stdin (use for piped content)
echo "Comment" | jira issue comment add ISSUE-KEY
jira issue comment add ISSUE-KEY --template -
```

**Comment formatting (Jira Wiki Markup):**
- **Headings**: `h1.`, `h2.`, `h3.` (NOT Markdown #)
- **Code blocks**: `{code:language}...{code}` (NOT triple backticks)
- **Inline code**: `{{text}}` (double curly braces)
- **Lists**: `*` or `-` for bullets, `#` for numbered
- **Bold**: `*text*` (single asterisks)
- **Italic**: `_text_` (underscores)
- **Links**: `[text|url]` (pipe separator, NOT parentheses)
- **Preformatted**: `{noformat}...{noformat}` for preserving formatting

**IMPORTANT**: Do NOT use Markdown syntax! Jira doesn't support it and will mangle your content.

### Issue Key Handling

When user provides:
- Just a number (e.g., "123") → Use "FSEC-123"
- Full key (e.g., "PROJ-456") → Use as-is
- URL → Extract key from URL

## Workflow for Adding Comments

1. **Create comment content** in a temp file (use `/tmp/jira-comment.txt`)
2. **Use heredoc** to write multi-line comments to avoid quoting issues
3. **Call jira with --template** flag pointing to the file
4. **Verify success** by checking the output

**Template example:**
```bash
cat > /tmp/jira-comment.txt <<'EOF'
h2. Root Cause Analysis

Found the issue in line 123 of file.go

{code:go}
func example() {
    // problematic code
}
{code}

h3. Fix Applied
- Fixed the bug
- Added tests
- Updated docs
EOF

jira issue comment add FSEC-9884 --template /tmp/jira-comment.txt
```

## Common Patterns

### Adding Investigation Results

```bash
cat > /tmp/jira-comment.txt <<'EOF'
h2. Investigation Results

After debugging in production:

h3. Findings
* Issue occurs in pod998 cluster
* Caused by stuck deletion loops
* 14 resources affected

h3. Metrics
* Log volume: 967K lines/day
* Resources stuck: 30-56 days
* Impact: Datadog quota exceeded

h3. Root Cause
Code at resourceaccess_controller.go:292 has no timeout for stuck deletions.

h3. Proposed Fix
[Attach code snippet or link to PR]
EOF

jira issue comment add FSEC-1234 --template /tmp/jira-comment.txt
```

### Adding Code Proposals

**IMPORTANT**: Use proper comparison operators and escape special characters!

```bash
cat > /tmp/jira-comment.txt <<'EOF'
h2. Proposed Code Fix

h3. Location
{{pkg/controller/resourceaccess/resourceaccess_controller.go:292}}

h3. Current Code
{code:go}
if !safeToDelete(instance.ObjectMeta.DeletionTimestamp, r.config.ResourceAccessDeletionDelay) {
    reqLogger.Info(fmt.Sprintf("Attempted deletion within %d seconds; requeuing", r.config.ResourceAccessDeletionDelay))
    return reconcile.Result{RequeueAfter: r.config.CrRefreshIntervalShort}, nil
}
{code}

h3. Proposed Fix
Add timeout check to prevent infinite loops:

{code:go}
maxDeletionAge := time.Duration(7 * 24 * time.Hour)
if time.Since(instance.ObjectMeta.DeletionTimestamp.Time) > maxDeletionAge {
    reqLogger.Error(fmt.Errorf("resource stuck in deletion for %v, force removing finalizer",
        time.Since(instance.ObjectMeta.DeletionTimestamp.Time)),
        "Forcing finalizer removal")
    // Force remove finalizer
}
{code}

h3. Benefits
* Automatic cleanup after 7 days
* No manual intervention needed
* Prevents infinite logging

h3. Testing
Deploy with shorter timeout first:
{noformat}
RESOURCE_ACCESS_MAX_DELETION_AGE=1h
{noformat}
EOF

jira issue comment add FSEC-1234 --template /tmp/jira-comment.txt
```

**Key points for code:**
- Greater-than/less-than: `>` and `<` work fine inside `{code}` blocks
- Backticks in Go: Use regular backticks - they're preserved in `{code}` blocks
- For commands/config: Use `{noformat}` not `{code}` to preserve exact formatting

### Updating Status/Progress

```bash
cat > /tmp/jira-comment.txt <<'EOF'
h2. Status Update

h3. Completed
* [x] Investigation in pod998
* [x] Root cause identified
* [x] Manual cleanup performed

h3. In Progress
* [ ] Code fix implementation
* [ ] Testing in staging

h3. Blocked
* Waiting for security review on proposed timeout value

h3. Next Steps
1. Get approval on 7-day timeout
2. Implement fix
3. Test in staging
4. Roll out to production
EOF

jira issue comment add FSEC-1234 --template /tmp/jira-comment.txt
```

## Error Handling

**Common errors and solutions:**

1. **"unknown flag: --comment"**
   - ❌ Wrong: `jira issue comment add ISSUE-KEY --comment "text"`
   - ✅ Right: `jira issue comment add ISSUE-KEY "text"`
   - ✅ Right: `jira issue comment add ISSUE-KEY --template /tmp/file.txt`

2. **Quoting issues with special characters**
   - Use heredoc with single quotes to preserve content:
   ```bash
   cat > /tmp/comment.txt <<'EOF'
   Content with $variables and "quotes"
   EOF
   ```

3. **Long comments getting truncated**
   - Always use `--template` for comments > 100 chars
   - Use temp files, not inline strings

## Best Practices

1. **For short comments** (< 50 chars): Use direct string
   ```bash
   jira issue comment add FSEC-1234 "Fixed in PR #123"
   ```

2. **For formatted comments**: Use temp file + template
   ```bash
   cat > /tmp/comment.txt <<'EOF'
   ...
   EOF
   jira issue comment add FSEC-1234 --template /tmp/comment.txt
   ```

3. **Always verify** the comment was added:
   - Check the output for success message
   - Output includes the Jira URL

4. **Structure your comments**:
   - Use headings for organization
   - Use code blocks for code/logs
   - Use lists for action items
   - Add links to PRs, docs, dashboards

5. **Clean up temp files** (optional):
   ```bash
   rm /tmp/jira-comment.txt
   ```

## Integration with Other Skills

- **jira-review**: Use this skill to READ tickets
- **jira-interaction**: Use this skill to ADD COMMENTS or update tickets
- After analysis with jira-review, use jira-interaction to add findings

## Examples

**Quick status update:**
```bash
jira issue comment add FSEC-1234 "Investigation complete. Root cause found in resourceaccess_controller.go:292. Fix proposal in next comment."
```

**Detailed findings:**
```bash
cat > /tmp/jira-comment.txt <<'EOF'
h2. Root Cause Analysis - Excessive Logging

After investigating pod998 cluster, found 14 stuck ResourceAccess resources causing ~967K log lines/day.

h3. Evidence
* Resources stuck in deletion for 30-56 days
* Infinite reconciliation loops every 5 seconds
* Code location: resourceaccess_controller.go:292-296

h3. Impact
* Datadog quota exhausted
* 97% of excessive logs from stuck deletions
* Multiple clusters affected

h3. Immediate Action Taken
Manually removed finalizers from 6 stuck resources in pod998. Log volume reduced by 97%.

h3. Long-term Fix Needed
Add automatic finalizer cleanup after 7 days stuck. Code proposal in follow-up comment.
EOF

jira issue comment add FSEC-9884 --template /tmp/jira-comment.txt
```

## Remember

- ✅ Use `--template` for anything formatted or multi-line
- ✅ Use heredoc with single quotes for safety
- ✅ Structure comments with headings
- ✅ Include evidence (metrics, logs, code)
- ✅ Link to related resources (PRs, docs)
- ❌ Don't use `--comment` flag (doesn't exist!)
- ❌ Don't put complex content in command line strings
- ❌ Don't forget to use code blocks for code snippets
