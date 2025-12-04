# Troubleshooting

## Common Issues

### git-trim: command not found

**Symptoms**: Running `git-trim` or `git trim` results in "command not found".

**Diagnosis**:
```bash
which git-trim
# (no output)
```

**Solutions**:

1. **Install git-trim**:
   ```bash
   # macOS
   brew install foriequal0/git-trim/git-trim

   # Cargo
   cargo install git-trim
   ```

2. **Check PATH**:
   ```bash
   echo $PATH | tr ':' '\n' | grep -E 'cargo|local'
   # Should include ~/.cargo/bin or /usr/local/bin
   ```

3. **Add to PATH** (if installed but not in PATH):
   ```bash
   # In ~/.bashrc or ~/.zshrc
   export PATH="$HOME/.cargo/bin:$PATH"
   source ~/.bashrc  # or ~/.zshrc
   ```

---

### Nothing to delete (but branches look stale)

**Symptoms**: `git-trim --dry-run` shows no branches to delete, but `git branch -vv` shows stale branches.

**Diagnosis**:
```bash
git branch -vv
# Shows branches with [gone] or no upstream
```

**Root Cause**: Branches without upstream tracking are not detected by git-trim.

**Solutions**:

1. **For [gone] branches** (upstream deleted):
   ```bash
   git branch -vv | grep '\[gone\]' | awk '{print $1}' | xargs git branch -D
   ```

2. **For orphan branches** (no upstream):
   ```bash
   # Check if truly orphan
   git branch -vv | grep -v '\[origin/'

   # Manual deletion
   git branch -d <branch>
   ```

3. **Set upstream** (if branch should track remote):
   ```bash
   git branch --set-upstream-to=origin/<branch> <branch>
   git pull
   git-trim
   ```

---

### "Merged" branch shows as unmerged

**Symptoms**: Branch was merged via GitHub/GitLab, but git-trim doesn't detect it.

**Diagnosis**:
```bash
git log origin/main..<branch> --oneline
# Shows commits that appear to be in main
```

**Root Cause**: Squash merge with edited commits or rebased after merge.

**Solutions**:

1. **Verify manually**:
   ```bash
   git log --all --oneline --grep="<commit subject>"
   # If found on main, safe to delete
   ```

2. **Force delete**:
   ```bash
   git branch -D <branch>
   ```

3. **Update local main**:
   ```bash
   git checkout main
   git pull --rebase
   git-trim
   ```

---

### "Stray" branch but it's actually merged

**Symptoms**: Branch flagged as "stray" with "upstream deleted", but you know it was merged.

**Diagnosis**:
```bash
git log origin/main..<branch>
# Empty output (no unique commits)
```

**Root Cause**: Upstream was deleted after merge (common in GitHub).

**Solution**: Safe to delete manually.
```bash
git branch -D <branch>
```

**Prevention**: Enable auto-delete on GitHub PR merge.

---

### git-trim hangs or is very slow

**Symptoms**: Command runs for minutes without output.

**Diagnosis**:
```bash
# Count branches
git branch -a | wc -l
# Very high number (500+)?
```

**Root Cause**: Large number of branches (remote + local).

**Solutions**:

1. **Prune remote branches first**:
   ```bash
   git fetch --prune
   git remote prune origin
   ```

2. **Use `--no-update`**:
   ```bash
   git-trim --no-update
   ```

3. **Clean in batches**:
   ```bash
   # Delete known stale branches first
   git branch -vv | grep '\[gone\]' | awk '{print $1}' | xargs git branch -D

   # Then run git-trim
   git-trim
   ```

---

### Network errors during fetch

**Symptoms**: git-trim fails with network timeout or connection errors.

**Diagnosis**:
```bash
git fetch
# fatal: unable to access 'https://...': Could not resolve host
```

**Solutions**:

1. **Check network**:
   ```bash
   ping github.com
   ```

2. **Use `--no-update`**:
   ```bash
   git-trim --no-update
   ```

3. **Fix remote URL**:
   ```bash
   git remote -v
   # If using SSH but keys not configured:
   git remote set-url origin https://github.com/user/repo.git
   ```

---

### Permission denied on branch deletion

**Symptoms**: git-trim errors with "cannot delete branch".

**Diagnosis**:
```bash
git branch -D <branch>
# error: branch '<branch>' not found
```

**Root Cause**: Branch already deleted or locked.

**Solutions**:

1. **Check if branch exists**:
   ```bash
   git branch --list <branch>
   ```

2. **Verify not on the branch**:
   ```bash
   git rev-parse --abbrev-ref HEAD
   # If on the branch, switch away:
   git checkout main
   ```

3. **Check file system permissions**:
   ```bash
   ls -la .git/refs/heads/
   ```

---

### Excluded branch still shows in output

**Symptoms**: Branch in `trim.exclude` config still appears.

**Diagnosis**:
```bash
git config trim.exclude
# staging production

git-trim --dry-run | grep staging
# staging appears in output
```

**Root Cause**: Typo or wrong branch name.

**Solutions**:

1. **Verify branch name exactly**:
   ```bash
   git branch --list staging
   # Must match exactly (case-sensitive)
   ```

2. **Check config format** (space-delimited, not comma):
   ```bash
   # Correct
   git config trim.exclude "staging production"

   # Incorrect
   git config trim.exclude "staging,production"
   ```

3. **Re-set config**:
   ```bash
   git config --unset trim.exclude
   git config trim.exclude "staging production"
   ```

---

### Base branch not detected

**Symptoms**: git-trim errors with "cannot determine base branch".

**Diagnosis**:
```bash
git remote show origin | grep "HEAD branch"
# HEAD branch: (unknown)
```

**Root Cause**: Remote HEAD not set or repository uses non-standard branches.

**Solutions**:

1. **Set remote HEAD**:
   ```bash
   git remote set-head origin main
   ```

2. **Configure base branches explicitly**:
   ```bash
   git config trim.bases "main"
   # or for git-flow:
   git config trim.bases "develop,master"
   ```

3. **Check default branch on remote**:
   ```bash
   git ls-remote --symref origin HEAD
   ```

---

### Cannot recover deleted branch

**Symptoms**: Accidentally deleted branch, need to recover.

**Solution**: Use `git reflog` to find commit SHA.

**Steps**:
1. Find deleted branch commit:
   ```bash
   git reflog | grep <branch-name>
   # Or search by recent activity:
   git reflog | head -20
   ```

2. Recreate branch:
   ```bash
   git branch <branch-name> <commit-sha>
   ```

3. Verify:
   ```bash
   git log <branch-name> --oneline
   ```

**Prevention**: Use `--dry-run` first!

---

### git-trim shows different results than expected

**Symptoms**: Output doesn't match manual inspection.

**Diagnosis**:
```bash
# Manual check
git log origin/main..<branch> --oneline

# git-trim check
git-trim --dry-run | grep <branch>
```

**Root Causes**:
- Out-of-date local refs
- Non-standard base branch
- Squash merge heuristics failed

**Solutions**:

1. **Update refs**:
   ```bash
   git fetch --all --prune
   git remote update
   git-trim --dry-run
   ```

2. **Verify base branches**:
   ```bash
   git config trim.bases
   # Should include all relevant bases
   ```

3. **Manual verification**:
   ```bash
   # For each branch git-trim flags:
   git log origin/main..<branch>
   # Empty = merged, safe to delete
   ```

---

### Hook not running

**Symptoms**: post-merge hook doesn't execute git-trim.

**Diagnosis**:
```bash
ls -l .git/hooks/post-merge
# Should be executable (-rwxr-xr-x)

# Test manually
.git/hooks/post-merge
```

**Solutions**:

1. **Make executable**:
   ```bash
   chmod +x .git/hooks/post-merge
   ```

2. **Check shebang**:
   ```bash
   head -1 .git/hooks/post-merge
   # Should be: #!/bin/bash
   ```

3. **Test hook**:
   ```bash
   bash -x .git/hooks/post-merge
   # Shows execution trace
   ```

---

### Cargo install fails (Linux)

**Symptoms**: `cargo install git-trim` fails with OpenSSL errors.

**Error**:
```
error: failed to run custom build command for `openssl-sys`
```

**Solution**: Install development libraries.

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y libssl-dev pkg-config
cargo install git-trim
```

**Fedora/RHEL**:
```bash
sudo dnf install -y openssl-devel
cargo install git-trim
```

**Arch**:
```bash
sudo pacman -S openssl pkg-config
cargo install git-trim
```

---

### CI/CD job fails

**Symptoms**: GitHub Actions or GitLab CI job fails on git-trim.

**Common Errors**:

1. **git-trim not installed**:
   ```yaml
   - name: Install git-trim
     run: cargo install git-trim
   ```

2. **Shallow clone** (fetch-depth: 1):
   ```yaml
   - uses: actions/checkout@v3
     with:
       fetch-depth: 0  # Full history needed
   ```

3. **Missing git config**:
   ```yaml
   - name: Configure git
     run: |
       git config user.name "CI Bot"
       git config user.email "ci@example.com"
   ```

---

## Diagnostic Commands

### Check git-trim version
```bash
git-trim --version
```

### Show configuration
```bash
git config --list | grep trim
```

### Show branch tracking info
```bash
git branch -vv
```

### Show remote branches
```bash
git ls-remote --heads origin
```

### Show merge status manually
```bash
# For each branch
git log origin/main..<branch> --oneline
```

### Show reflog (recovery)
```bash
git reflog
```

---

## Getting Help

### git-trim help
```bash
git-trim --help
```

### Verbose mode
```bash
# git-trim doesn't have verbose mode, but you can trace:
bash -x $(which git-trim) --dry-run
```

### Report issue
- GitHub: https://github.com/foriequal0/git-trim/issues
- Include:
  - git-trim version
  - Git version
  - OS and version
  - Output of `git-trim --dry-run`
  - Output of `git branch -vv`

---

## Quick Reference

| Issue | Command |
|-------|---------|
| Not installed | `brew install foriequal0/git-trim/git-trim` |
| Not in PATH | `export PATH="$HOME/.cargo/bin:$PATH"` |
| Slow | `git fetch --prune && git-trim --no-update` |
| Network error | `git-trim --no-update` |
| Branch not deleted | `git branch -D <branch>` |
| Recover deleted | `git reflog` → `git branch <name> <sha>` |
| Hook not running | `chmod +x .git/hooks/post-merge` |
