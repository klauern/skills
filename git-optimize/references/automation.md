# Automation

## Overview

This document covers automated branch cleanup strategies using git-trim with Git hooks, aliases, and scripts.

---

## Git Hooks

### Post-Merge Hook

Automatically run git-trim after pulling on main/develop branches.

**Create hook**:
```bash
cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash

# Only run on main branches
BRANCH=$(git rev-parse --abbrev-ref HEAD)
case "$BRANCH" in
  "master"|"main"|"develop")
    echo "🧹 Running git-trim..."
    git trim --no-update || true
    ;;
esac
EOF

chmod +x .git/hooks/post-merge
```

**Features**:
- Runs only on main/develop branches
- Uses `--no-update` (just fetched via pull)
- Doesn't fail if git-trim errors (`|| true`)

**Testing**:
```bash
git pull
# Automatically runs git-trim
```

---

### Post-Checkout Hook

Warn about stale branches when switching to main.

**Create hook**:
```bash
cat > .git/hooks/post-checkout << 'EOF'
#!/bin/bash

NEW_BRANCH=$3
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# Only check on main/master
if [[ "$BRANCH_NAME" == "main" || "$BRANCH_NAME" == "master" ]]; then
  # Count stale branches
  COUNT=$(git trim --dry-run 2>/dev/null | grep -c "merged into" || echo "0")

  if [ "$COUNT" -gt 0 ]; then
    echo "⚠️  You have $COUNT stale branch(es)"
    echo "   Run 'git trim' to clean up"
  fi
fi
EOF

chmod +x .git/hooks/post-checkout
```

**Features**:
- Non-intrusive warning only
- Doesn't auto-delete
- Runs on checkout to main

---

### Pre-Push Hook

Prevent pushing branches that should be cleaned up.

**Create hook**:
```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

# Check current branch
CURRENT=$(git rev-parse --abbrev-ref HEAD)

# Check if current branch is merged
git trim --dry-run 2>/dev/null | grep -q "$CURRENT.*merged into"

if [ $? -eq 0 ]; then
  echo "❌ Branch '$CURRENT' is already merged"
  echo "   Consider deleting instead of pushing:"
  echo "   git checkout main && git branch -D $CURRENT"
  exit 1
fi
EOF

chmod +x .git/hooks/pre-push
```

**Features**:
- Prevents accidental pushes
- Reminds to clean up
- Can be bypassed: `git push --no-verify`

---

## Git Aliases

### Sync Alias

Combine fetch, pull, and trim in one command.

**Setup**:
```bash
git config alias.sync '!git fetch --prune && git pull && git trim'
```

**Usage**:
```bash
git sync
# Fetches, pulls, trims in one step
```

---

### Cleanup Alias

Interactive cleanup with dry-run first.

**Setup**:
```bash
git config alias.cleanup '!git trim --dry-run && read -p "Proceed? [y/N] " -n 1 -r && echo && [[ $REPLY =~ ^[Yy]$ ]] && git trim'
```

**Usage**:
```bash
git cleanup
# Shows preview, asks confirmation, executes
```

---

### Trim-All Alias

Clean all local repos in a directory.

**Setup**:
```bash
git config --global alias.trim-all '!f() { find "${1:-.}" -name .git -type d -execdir sh -c "pwd && git trim --no-update" \; ; }; f'
```

**Usage**:
```bash
# In parent directory
git trim-all

# Specific directory
git trim-all ~/projects
```

---

### Check-Stale Alias

Show count of stale branches without deleting.

**Setup**:
```bash
git config alias.check-stale '!git trim --dry-run | grep -c "merged into" || echo "0 stale branches"'
```

**Usage**:
```bash
git check-stale
# 5
```

---

## Shell Scripts

### Daily Cleanup Script

Run daily via cron or manually.

**Script**: `~/.local/bin/git-daily-cleanup.sh`
```bash
#!/bin/bash

# List of repositories to clean
REPOS=(
  "$HOME/projects/repo1"
  "$HOME/projects/repo2"
  "$HOME/work/client-project"
)

for repo in "${REPOS[@]}"; do
  if [ -d "$repo/.git" ]; then
    echo "Cleaning $repo..."
    cd "$repo" || continue
    git fetch --prune
    git trim --no-update
    echo
  fi
done
```

**Setup**:
```bash
chmod +x ~/.local/bin/git-daily-cleanup.sh

# Add to crontab
crontab -e
# Add line:
# 0 9 * * * ~/.local/bin/git-daily-cleanup.sh
```

---

### Interactive Multi-Repo Cleanup

Review each repository before cleaning.

**Script**: `~/.local/bin/git-interactive-cleanup.sh`
```bash
#!/bin/bash

BASE_DIR="${1:-$HOME/projects}"

find "$BASE_DIR" -name .git -type d | while read gitdir; do
  REPO=$(dirname "$gitdir")
  echo "========================================"
  echo "Repository: $(basename $REPO)"
  echo "========================================"

  cd "$REPO" || continue

  # Show dry-run
  git trim --dry-run

  # Ask for confirmation
  read -p "Clean this repository? [y/N] " -n 1 -r
  echo

  if [[ $REPLY =~ ^[Yy]$ ]]; then
    git trim
  fi

  echo
done
```

**Usage**:
```bash
git-interactive-cleanup.sh ~/projects
```

---

### Repo Health Report

Generate report of all stale branches across repos.

**Script**: `~/.local/bin/git-health-report.sh`
```bash
#!/bin/bash

BASE_DIR="${1:-$HOME/projects}"
REPORT_FILE="/tmp/git-health-$(date +%Y%m%d).txt"

echo "Git Repository Health Report" > "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

find "$BASE_DIR" -name .git -type d | while read gitdir; do
  REPO=$(dirname "$gitdir")
  REPO_NAME=$(basename "$REPO")

  cd "$REPO" || continue

  # Count stale branches
  COUNT=$(git trim --dry-run 2>/dev/null | grep -c "merged into" || echo "0")

  if [ "$COUNT" -gt 0 ]; then
    echo "[$REPO_NAME]: $COUNT stale branches" >> "$REPORT_FILE"
    git trim --dry-run >> "$REPORT_FILE" 2>&1
    echo >> "$REPORT_FILE"
  fi
done

cat "$REPORT_FILE"
echo
echo "Report saved to: $REPORT_FILE"
```

**Usage**:
```bash
git-health-report.sh ~/projects
```

---

## CI/CD Integration

### GitHub Actions - Branch Health Check

**File**: `.github/workflows/branch-health.yml`
```yaml
name: Branch Health

on:
  pull_request:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday 9 AM

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Install git-trim
        run: cargo install git-trim

      - name: Check for stale branches
        run: |
          git fetch --all --prune
          OUTPUT=$(git trim --dry-run)
          COUNT=$(echo "$OUTPUT" | grep -c "merged into" || echo "0")

          if [ "$COUNT" -gt 0 ]; then
            echo "::warning::$COUNT stale branch(es) found"
            echo "$OUTPUT"
          else
            echo "✅ No stale branches"
          fi
```

---

### GitLab CI - Weekly Cleanup

**File**: `.gitlab-ci.yml`
```yaml
cleanup:
  stage: maintenance
  only:
    - schedules
  script:
    - cargo install git-trim
    - git fetch --all --prune
    - git trim --dry-run > report.txt
    - cat report.txt
  artifacts:
    paths:
      - report.txt
    expire_in: 1 week
```

**Setup schedule**:
- Go to CI/CD > Schedules
- Create schedule: "Weekly Branch Cleanup"
- Cron: `0 9 * * 0` (Sunday 9 AM)

---

## Systemd Timers (Linux)

### Service Definition

**File**: `~/.config/systemd/user/git-trim.service`
```ini
[Unit]
Description=Git branch cleanup

[Service]
Type=oneshot
ExecStart=%h/.local/bin/git-daily-cleanup.sh
```

### Timer Definition

**File**: `~/.config/systemd/user/git-trim.timer`
```ini
[Unit]
Description=Daily git cleanup timer

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable**:
```bash
systemctl --user enable git-trim.timer
systemctl --user start git-trim.timer
systemctl --user status git-trim.timer
```

---

## macOS LaunchAgent

**File**: `~/Library/LaunchAgents/com.user.git-trim.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.git-trim</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOU/.local/bin/git-daily-cleanup.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

**Load**:
```bash
launchctl load ~/Library/LaunchAgents/com.user.git-trim.plist
launchctl start com.user.git-trim
```

---

## Shell Integration

### Zsh Plugin

**File**: `~/.oh-my-zsh/custom/plugins/git-trim/git-trim.plugin.zsh`
```bash
# Aliases
alias gt='git trim'
alias gtd='git trim --dry-run'
alias gts='git trim --no-update'

# Auto-cleanup on cd to main/master
function chpwd() {
  if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
      COUNT=$(git trim --dry-run 2>/dev/null | grep -c "merged into" || echo "0")
      if [ "$COUNT" -gt 0 ]; then
        echo "💡 Tip: Run 'gt' to clean $COUNT stale branch(es)"
      fi
    fi
  fi
}
```

**Enable**:
```bash
# In ~/.zshrc
plugins=(... git-trim)
```

---

### Fish Shell Functions

**File**: `~/.config/fish/functions/gt.fish`
```fish
function gt --description 'Git trim with smart defaults'
    if test (count $argv) -eq 0
        git trim --dry-run
        read -P "Proceed? [y/N] " -n 1 confirm
        if test "$confirm" = "y"
            git trim
        end
    else
        git trim $argv
    end
end
```

---

## Best Practices for Automation

1. **Always use `--dry-run` first** in scripts
2. **Skip fetch** (`--no-update`) in hooks (already fetched)
3. **Non-interactive for CI/CD** (no prompts)
4. **Log results** for auditing
5. **Handle errors gracefully** (`|| true`)
6. **Test in isolation** before deploying widely
7. **Document automation** in README

---

## Troubleshooting Automation

### Hook not running

```bash
# Check if executable
ls -l .git/hooks/post-merge

# Test manually
.git/hooks/post-merge
```

### Alias not found

```bash
# Check alias definition
git config alias.sync

# Re-add if missing
git config alias.sync '!git fetch --prune && git pull && git trim'
```

### Cron job failing

```bash
# Check cron logs
grep CRON /var/log/syslog

# Test script manually
~/.local/bin/git-daily-cleanup.sh
```

---

## Security Considerations

- **Never auto-delete without confirmation** in production repos
- **Review stray branches** before automated deletion
- **Backup important branches** before experimenting
- **Use `--dry-run`** extensively when testing
- **Limit automation** to low-risk repositories initially
