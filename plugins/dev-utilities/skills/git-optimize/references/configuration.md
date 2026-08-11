# Configuration

Git-trim and git aliases use Git's native configuration system.

## git-trim Options

### trim.bases

Define base branches (comma-separated):
```bash
git config trim.bases "develop,master"     # Git-flow
git config trim.bases "main"               # GitHub flow
```

### trim.exclude

Exclude branches from cleanup (space-separated):
```bash
git config trim.exclude "staging production qa"
```

## Git Aliases

The optimization aliases this skill relies on. **They are not git built-ins** — verify
the complete set before use and offer to install the missing definitions:

```bash
for alias in cleanup sweep pruner repacker optimize trimall; do
  git config --get "alias.$alias" >/dev/null || echo "missing alias: $alias"
done
```

Install these into `~/.gitconfig`. The cleanup function enumerates exact refs, protects
the current/default/common/configured bases, applies `trim.exclude` patterns, previews
the final candidates, and requires confirmation before deleting anything:

```ini
[alias]
    cleanup = "!f() { \
        set -efu; \
        requested=${1:-}; \
        current=$(git branch --show-current); \
        remote_default=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true); \
        remote_default=${remote_default#origin/}; \
        configured=$(git config --get trim.bases 2>/dev/null || true); \
        configured=$(printf '%s' \"$configured\" | tr ',' ' '); \
        excluded=$(git config --get trim.exclude 2>/dev/null || true); \
        targets=${requested:-${configured:-$remote_default}}; \
        [ -n \"$targets\" ] || { echo 'No cleanup base: configure trim.bases, origin/HEAD, or pass a base.' >&2; exit 1; }; \
        protected=\"main master develop trunk $current $remote_default $configured $targets\"; \
        raw_candidates=$(mktemp); \
        candidates=$(mktemp); \
        trap 'rm -f \"$raw_candidates\" \"$candidates\"' EXIT; \
        for target in $targets; do \
            if git show-ref --verify --quiet \"refs/heads/$target\"; then target_ref=$target; \
            elif git show-ref --verify --quiet \"refs/remotes/origin/$target\"; then target_ref=origin/$target; \
            elif git rev-parse --verify --quiet \"$target^{commit}\" >/dev/null; then target_ref=$target; \
            else echo \"Cleanup base not found: $target\" >&2; exit 1; fi; \
            git for-each-ref --format='%(refname:short)' --merged \"$target_ref\" refs/heads/; \
        done | sort -u >\"$raw_candidates\"; \
        while IFS= read -r branch; do \
            skip=; \
            for name in $protected; do \
                [ \"$branch\" = \"$name\" ] && skip=1; \
            done; \
            for pattern in $excluded; do \
                case \"$branch\" in $pattern) skip=1 ;; esac; \
            done; \
            [ -n \"$skip\" ] || printf '%s\\n' \"$branch\"; \
        done <\"$raw_candidates\" >\"$candidates\"; \
        if [ ! -s \"$candidates\" ]; then echo 'No merged local branches eligible for deletion.'; exit 0; fi; \
        echo 'Merged local branches eligible for deletion:'; \
        sed 's/^/  /' \"$candidates\"; \
        printf 'Delete these local branches? [y/N] '; \
        IFS= read -r answer || answer=; \
        case \"$answer\" in \
            y|Y|yes|YES) while IFS= read -r branch; do git branch -d -- \"$branch\"; done <\"$candidates\" ;; \
            *) echo 'Cancelled.'; return 1 ;; \
        esac; \
    }; f"

    sweep = "!f() { \
        if [ $# -gt 0 ]; then git cleanup \"$1\"; else git cleanup; fi; \
    }; f"

    # trimall-workflow
    trimall = "!f() { \
        set -efu; \
        echo '1. Fetching and pruning remotes...'; \
        git fetch --all --prune || { echo 'Fetch failed; stopping.' >&2; return 1; }; \
        echo '2. Previewing git-trim candidates...'; \
        git trim --dry-run || { echo 'git trim dry-run failed; stopping.' >&2; return 1; }; \
        printf 'Continue with confirmed local cleanup and optimization? [y/N] '; \
        IFS= read -r answer || answer=; \
        case \"$answer\" in y|Y|yes|YES) ;; *) echo 'Cancelled.'; return 0 ;; esac; \
        echo '3. Running confirmed cleanup...'; \
        git cleanup || { echo 'Cleanup failed or was cancelled; stopping.' >&2; return 1; }; \
        echo '4. Running confirmed sweep...'; \
        git sweep || { echo 'Sweep failed or was cancelled; stopping.' >&2; return 1; }; \
        echo '5. Optimizing repository...'; \
        git optimize || { echo 'Optimize failed; stopping.' >&2; return 1; }; \
        echo 'Done!'; \
    }; f"

    pruner = "!git prune --expire=now && git reflog expire --expire-unreachable=now --rewrite --all"

    repacker = "!git repack -a -d --depth=250 --window=250"

    optimize = "!git pruner && git repacker && git prune-packed"
```

## Common Configurations

| Workflow | trim.bases | trim.exclude |
|----------|------------|--------------|
| GitHub Flow | `main` | (none) |
| Git-Flow | `develop,master` | `staging production` |
| Trunk-Based | `trunk` | `release-*` |

## View/Remove Config

```bash
# View
git config trim.bases
git config --list | grep trim

# Remove
git config --unset trim.bases
git config --unset trim.exclude
```
