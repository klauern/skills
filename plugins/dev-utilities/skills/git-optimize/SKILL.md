---
name: git-optimize
description: This skill should be used when the user asks to "clean up merged git branches", "run git trim/cleanup", "optimize repository size", or "perform git maintenance and garbage collection".
version: 1.0.0
allowed-tools: Bash Read
---

# Git Optimize

Repository maintenance through branch cleanup and optimization operations.

## Quick Start

**Command**: `/git-optimize` — Clean branches and optimize repository

**Documentation**:
- [Configuration](references/configuration.md) — Alias and git-trim setup
- [Merge Detection](references/merge_detection.md) — How git-trim detects merges
- [Installation](references/installation.md) — git-trim installation

## When to Use

**Invoke when**:
- User asks to clean up branches or merged PRs
- Repository performance is slow or .git is large
- Preparing repository for archival
- Running maintenance workflows

**Don't use for**:
- Branch creation or checkout
- Commit operations
- Remote management (use standard git)

## Step 1 — Check Prerequisites

The convenience commands below are **git aliases, not built-ins**. Before using any of
them, verify they exist and offer to install the missing ones (definitions in
[configuration.md](references/configuration.md)):

```bash
for alias in cleanup sweep pruner repacker optimize trimall; do
  git config --get "alias.$alias" >/dev/null || echo "missing alias: $alias"
done
command -v git-trim >/dev/null || echo "missing external command: git-trim"
```

Do not treat one present alias as proof that the set is installed. If anything is
missing, offer to install the definitions from `configuration.md`; if the user declines,
use the corresponding raw Git flow and preserve the same preview/confirmation gates.

## Commands

| Alias | Raw-git equivalent | Purpose | Time |
|-------|--------------------|---------|------|
| `git cleanup` | Safe `git for-each-ref` flow in `configuration.md` | Preview and delete merged local branches | Seconds |
| `git sweep` | Same safe flow against the configured/default base | Preview merged local branches | Seconds |
| `git trim` | external tool ([git-trim](references/installation.md)) | Smart detection (merged/stray/squash) | Seconds |
| `git pruner` | `git reflog expire --expire=now --all && git gc --prune=now` | Remove unreachable objects | Minutes-Hours |
| `git repacker` | `git repack -a -d --depth=250 --window=250` | Optimal delta compression | Hours |
| `git optimize` | pruner + repacker + `git prune-packed` | Full optimization cycle | Hours |
| `git trimall` | fetch→trim→cleanup→sweep→optimize | Complete workflow | 10min-Hours |

## Workflows

**After PR merge** (daily):
```bash
DEFAULT_REMOTE="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
[ -n "$DEFAULT_REMOTE" ] || {
  echo "origin/HEAD is unavailable; run 'git remote set-head origin --auto' before maintenance" >&2
  exit 1
}
git checkout "${DEFAULT_REMOTE#origin/}" && git pull && git cleanup
```

**Weekly maintenance**:
```bash
git fetch --all --prune && git trim --dry-run   # then delete per the strategy below
```

**Monthly deep clean**:
```bash
git fetch --all --prune
git trim --dry-run
# Show the dry-run result, then ask for explicit confirmation before git trimall.
```

## git-trim Execution Strategy (non-interactive)

git-trim's confirmation prompt uses terminal control sequences that break under pipes —
**never** use `yes | git trim` or `echo y | git trim`. Instead:

1. Resolve the current branch, `origin/HEAD`, common bases (`main`, `master`,
   `develop`, `trunk`), `trim.bases`, and `trim.exclude` before selecting candidates.
2. Enumerate exact local ref names with `git for-each-ref --format='%(refname:short)'
   --merged <base> refs/heads/`; never parse the decorated output of `git branch`.
3. Remove every protected/configured/excluded ref, show the exact remaining list, and
   require confirmation.
4. Delete confirmed local branches one at a time with `git branch -d -- "$branch"`.
5. Treat remote deletion as a separate operation. Use only a server-protected,
   non-rewritable integration branch as the base, and constrain it to the remote
   default, a common base, or `trim.bases`. Fetch exact refs for both the candidate and
   base, record the candidate's reviewed OID, and verify it is merged into the refreshed
   base. After confirmation, refresh the exact base ref and recheck ancestry again.
   Immediately before deletion, compare `git ls-remote` with the candidate OID. If
   the candidate changed, the base lost ancestry, or either ref cannot be verified, stop.
   Make the candidate deletion atomic with
   `git push --force-with-lease="refs/heads/$branch:$reviewed_oid" origin --delete -- "$branch"`.
6. Verify with `git branch -vv` and `git ls-remote --heads origin`.

Example remote revalidation for one already-reviewed branch:

```bash
set -euo pipefail

read_remote_oid() {
  local remote_branch=$1 remote_line oid
  if ! remote_line="$(git ls-remote --exit-code --heads origin \
    "refs/heads/$remote_branch")"; then
    echo "Could not verify origin/$remote_branch" >&2
    return 1
  fi
  if ! oid="$(printf '%s\n' "$remote_line" | awk \
    -v expected="refs/heads/$remote_branch" '
      NF == 2 && $2 == expected && count == 0 { oid = $1; count++; next }
      { invalid = 1 }
      END {
        if (!invalid && count == 1 && oid ~ /^[0-9a-f]+$/) print oid
        else exit 1
      }
    ')"; then
    echo "Unexpected ls-remote response for origin/$remote_branch" >&2
    return 1
  fi
  printf '%s\n' "$oid"
}

case "$base_ref" in
  refs/remotes/origin/*) base_branch=${base_ref#refs/remotes/origin/} ;;
  origin/*) base_branch=${base_ref#origin/} ;;
  *) echo "Deletion base must be an origin remote-tracking ref" >&2; exit 1 ;;
esac
remote_default="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
remote_default=${remote_default#origin/}
configured="$(git config --get trim.bases 2>/dev/null || true)"
configured="$(printf '%s' "$configured" | tr ',' ' ')"
protected_base=
for name in main master develop trunk "$remote_default" $configured; do
  [ -n "$name" ] && [ "$base_branch" = "$name" ] && protected_base=1
done
[ -n "$protected_base" ] || {
  echo "Deletion base is not a designated protected integration branch: $base_branch" >&2
  exit 1
}
[ "$branch" != "$base_branch" ] || {
  echo "Refusing to delete the selected integration base: $branch" >&2
  exit 1
}
[ "${BASE_IS_PROTECTED:-}" = yes ] || {
  echo "Verify server-side policy prevents force-pushing $base_branch, then set BASE_IS_PROTECTED=yes" >&2
  exit 1
}
if ! git fetch --no-tags origin \
  "+refs/heads/$base_branch:refs/remotes/origin/$base_branch"; then
  echo "Could not refresh deletion base origin/$base_branch" >&2
  exit 1
fi
base_ref="refs/remotes/origin/$base_branch"
if ! git fetch --no-tags origin \
  "+refs/heads/$branch:refs/remotes/origin/$branch"; then
  echo "Could not refresh deletion candidate origin/$branch" >&2
  exit 1
fi
if ! reviewed_oid="$(git rev-parse --verify \
  "refs/remotes/origin/$branch^{commit}")"; then
  echo "Could not resolve the reviewed candidate origin/$branch" >&2
  exit 1
fi
git merge-base --is-ancestor "$reviewed_oid" "$base_ref" || {
  echo "Remote branch is not merged into $base_ref" >&2
  exit 1
}
if ! current_oid="$(read_remote_oid "$branch")"; then
  exit 1
fi
[ "$current_oid" = "$reviewed_oid" ] || {
  echo "Remote branch changed after review; refusing deletion" >&2
  exit 1
}
printf 'Delete origin/%s at %s? [y/N] ' "$branch" "$reviewed_oid"
read -r answer
case "$answer" in
  y|Y|yes|YES)
    if ! git fetch --no-tags origin \
      "+refs/heads/$base_branch:refs/remotes/origin/$base_branch"; then
      echo "Could not revalidate deletion base origin/$base_branch" >&2
      exit 1
    fi
    git merge-base --is-ancestor "$reviewed_oid" "$base_ref" || {
      echo "Remote branch is no longer merged into refreshed $base_ref" >&2
      exit 1
    }
    if ! current_oid="$(read_remote_oid "$branch")"; then
      exit 1
    fi
    [ "$current_oid" = "$reviewed_oid" ] || {
      echo "Remote branch changed after confirmation; refusing deletion" >&2
      exit 1
    }
    git push --force-with-lease="refs/heads/$branch:$reviewed_oid" \
      origin --delete -- "$branch"
    ;;
  *) echo "Cancelled" ;;
esac
```

Note: git-trim upstream (foriequal0/git-trim) has been unmaintained for years — it still
works, but prefer the raw-git equivalents when it misbehaves.

## Model Strategy

| Task | Model |
|------|-------|
| Command execution, alias listing | Haiku |
| Analyzing branches, recommending strategy | Sonnet |

## Configuration

**Git-flow setup** (multiple base branches):
```bash
git config trim.bases "develop,master"
git config trim.exclude "staging production"
```

**Verify aliases**:
```bash
for alias in cleanup sweep pruner repacker optimize trimall; do
  git config --get "alias.$alias" || echo "missing alias: $alias"
done
```

See [configuration.md](references/configuration.md) for full alias definitions.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| git-trim not found | `brew install foriequal0/git-trim/git-trim` |
| Alias not working | Check `git config alias.<name>` |
| Repo still large | `git gc --prune=now --aggressive` |
| Stray branches flagged | `git log origin/main..<branch> --oneline` to check unmerged commits |

## Safety

**Always safe**: trim --dry-run and other read-only previews

**Review first — deletes branch refs**: cleanup, sweep, trimall

**Use caution**: pruner (removes objects), optimize, repacker, sweep -f

**Best practices**:
1. Use `--dry-run` first
2. Push important work before aggressive cleanup
3. Schedule optimize/repacker overnight
4. Use `git reflog` for recovery
