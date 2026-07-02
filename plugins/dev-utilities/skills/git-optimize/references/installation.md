# git-trim Installation

> Note: upstream (foriequal0/git-trim) has been unmaintained for years. It still works,
> but the raw-git equivalents in SKILL.md are the fallback if it misbehaves.

```bash
# macOS
brew install foriequal0/git-trim/git-trim

# Any platform with Rust (Linux needs libssl-dev + pkg-config to build)
cargo install git-trim

# Or download a pre-built binary from
# https://github.com/foriequal0/git-trim/releases and put it on PATH
```

Verify: `git-trim --version`, then `git-trim --dry-run` in a repo.

Once installed, configure it: [Configuration Guide](configuration.md)
