# Tool Detection Patterns

Detection patterns for each ecosystem: file markers, version extraction commands, Dockerfile install snippets, and firewall allowlist additions.

## Detection Table

| Ecosystem   | Marker Files                                    | Version Source                            | Priority |
| ----------- | ----------------------------------------------- | ----------------------------------------- | -------- |
| Node.js     | `package.json`                                  | `.node-version`, `engines.node`, `.nvmrc` | High     |
| Bun         | `bun.lockb`, `bunfig.toml`                      | `package.json` engines                    | High     |
| Go          | `go.mod`                                        | `go.mod` go directive                     | High     |
| Python      | `pyproject.toml`, `requirements.txt`, `uv.lock` | `.python-version`, `pyproject.toml`       | High     |
| Ruby        | `Gemfile`, `.ruby-version`                      | `.ruby-version`                           | Medium   |
| Rust        | `Cargo.toml`                                    | `rust-toolchain.toml`                     | Medium   |
| Java/Kotlin | `pom.xml`, `build.gradle`, `build.gradle.kts`   | `.java-version`, `pom.xml`                | Medium   |
| go-task     | `Taskfile.yml`                                  | N/A (latest)                              | Low      |
| mise/asdf   | `.mise.toml`, `.tool-versions`                  | Inline versions                           | High     |
| Just        | `Justfile`                                      | N/A (latest)                              | Low      |

## Runtime Version Substitution Contract

Normalize an optional leading `v`, then accept only an exact numeric runtime version
matching `^[0-9]+(\.[0-9]+){0,2}$` for automatic substitution. Never guess a concrete
version from a range, comparison operator, wildcard, or multi-value constraint. Ask the
user to choose an exact value or explicitly approve the proposed default.

| Runtime | Template placeholder | Confirmed fallback when no version source exists |
| --- | --- | --- |
| Node.js | `{{NODE_VERSION}}` in the base image | `20` |
| Go | `{{GO_VERSION}}` in the install block | `1.23` |
| Ruby | `{{RUBY_VERSION}}` in the install block | `3.3` |
| Rust | `{{RUST_VERSION}}` passed to rustup | `stable` |

Record the source, raw constraint, and final value in the generation preview. A detected
exact value always replaces the fallback.

## Node.js / Bun

### Detection

```bash
# Check for Node ecosystem
test -f package.json

# Detect package manager
test -f bun.lockb && echo "bun"
test -f pnpm-lock.yaml && echo "pnpm"
test -f yarn.lock && echo "yarn"
test -f package-lock.json && echo "npm"
```

### Version Extraction

```bash
# From .nvmrc or .node-version
cat .nvmrc 2>/dev/null || cat .node-version 2>/dev/null

# From package.json engines
jq -r '.engines.node // empty' package.json
```

Use an exact `.nvmrc`/`.node-version` value directly as `{{NODE_VERSION}}`. Treat an
`engines.node` range as ambiguous and ask for an exact image version before replacing
the placeholder.

### Dockerfile Snippet

```dockerfile
# Bun (if bun.lockb detected)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/home/node/.bun/bin:$PATH"

# pnpm (if pnpm-lock.yaml detected)
RUN npm install -g pnpm
```

### Firewall Allowlist

```
registry.npmjs.org
registry.yarnpkg.com
```

## Go

### Detection

```bash
test -f go.mod
```

### Version Extraction

```bash
# From go.mod
awk '/^go / {print $2; exit}' go.mod
```

### Dockerfile Snippet

```dockerfile
# Go installation
ARG GO_VERSION={{GO_VERSION}}
RUN curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" | tar -C /usr/local -xzf -
ENV PATH="/usr/local/go/bin:/home/node/go/bin:$PATH"
ENV GOPATH="/home/node/go"

# gofumpt (if CLAUDE.md mentions it)
RUN go install mvdan.cc/gofumpt@latest
```

### Firewall Allowlist

```
proxy.golang.org
sum.golang.org
storage.googleapis.com
```

## Python

### Detection

```bash
# Check for Python ecosystem
test -f pyproject.toml || test -f requirements.txt || test -f uv.lock

# Detect package manager
test -f uv.lock && echo "uv"
test -f Pipfile && echo "pipenv"
test -f poetry.lock && echo "poetry"
test -f requirements.txt && echo "pip"
```

### Version Extraction

```bash
# From .python-version
cat .python-version 2>/dev/null

# From pyproject.toml
grep 'requires-python' pyproject.toml | grep -oE '[0-9]+\.[0-9]+'
```

### Dockerfile Snippet

```dockerfile
# Python + uv (preferred)
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/node/.local/bin:$PATH"

# Poetry (if poetry.lock detected)
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/home/node/.local/bin:$PATH"
```

### Firewall Allowlist

```
pypi.org
files.pythonhosted.org
astral.sh
```

## Ruby

### Detection

```bash
test -f Gemfile || test -f .ruby-version
```

### Version Extraction

```bash
cat .ruby-version 2>/dev/null
```

### Dockerfile Snippet

```dockerfile
# Ruby via rbenv
RUN apt-get update && apt-get install -y \
    rbenv ruby-build libssl-dev libreadline-dev zlib1g-dev
ARG RUBY_VERSION={{RUBY_VERSION}}
RUN rbenv install ${RUBY_VERSION} && rbenv global ${RUBY_VERSION}
ENV PATH="/home/node/.rbenv/shims:$PATH"
```

### Firewall Allowlist

```
rubygems.org
index.rubygems.org
```

## Rust

### Detection

```bash
test -f Cargo.toml
```

### Version Extraction

```bash
# From rust-toolchain.toml
awk -F'"' '/^[[:space:]]*channel[[:space:]]*=/{print $2; exit}' rust-toolchain.toml 2>/dev/null
```

### Dockerfile Snippet

```dockerfile
# Rust via rustup
ARG RUST_VERSION={{RUST_VERSION}}
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y --default-toolchain "${RUST_VERSION}"
ENV PATH="/home/node/.cargo/bin:$PATH"
```

### Firewall Allowlist

```
crates.io
static.crates.io
static.rust-lang.org
```

## Java / Kotlin

### Detection

```bash
test -f pom.xml || test -f build.gradle || test -f build.gradle.kts
```

### Version Extraction

```bash
# From .java-version
cat .java-version 2>/dev/null

# From pom.xml
grep '<java.version>' pom.xml | grep -oE '[0-9]+'
```

### Dockerfile Snippet

```dockerfile
# Java via Eclipse Temurin
ARG JAVA_VERSION=21
RUN apt-get update && apt-get install -y wget apt-transport-https gpg \
    && wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /usr/share/keyrings/adoptium.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb bookworm main" > /etc/apt/sources.list.d/adoptium.list \
    && apt-get update && apt-get install -y temurin-${JAVA_VERSION}-jdk
```

### Firewall Allowlist

```
repo1.maven.org
plugins.gradle.org
services.gradle.org
```

## go-task

### Detection

```bash
test -f Taskfile.yml || test -f Taskfile.yaml
```

### Dockerfile Snippet

```dockerfile
# go-task
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
```

## mise / asdf

### Detection

```bash
test -f .mise.toml || test -f .tool-versions
```

### Version Extraction

```bash
# Parse .tool-versions (space-separated: tool version)
cat .tool-versions

# Parse .mise.toml
cat .mise.toml
```

### Dockerfile Snippet

```dockerfile
# mise
RUN curl https://mise.run | sh
ENV PATH="/home/node/.local/share/mise/shims:$PATH"

# Activate and install tools
RUN mise install
```

## Just

### Detection

```bash
test -f Justfile || test -f justfile
```

### Dockerfile Snippet

```dockerfile
# just
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
```

## Custom API Gateways

### Detection

```bash
# Read *_BASE_URL env vars from settings.json
jq -r '.env // {} | to_entries[] | select(.key | endswith("_BASE_URL")) | .value' ~/.claude/settings.json
```

### Domain Extraction

```bash
# Extract hostname from each URL
echo "https://ai-gateway.example.com/bedrock" | sed 's|https\?://||; s|/.*||'
# → ai-gateway.example.com
```

### Auth Token Selection

If **any** `*_BASE_URL` is found in `~/.claude/settings.json`:

- Ensure `ANTHROPIC_AUTH_TOKEN` is forwarded in `containerEnv` (and optionally `remoteEnv`) since custom gateways commonly use token auth
- Verify it's set on the host: `printenv ANTHROPIC_AUTH_TOKEN`

If **no** `*_BASE_URL` is found:

- Ensure `ANTHROPIC_API_KEY` is forwarded in `containerEnv` (and optionally `remoteEnv`) for direct Anthropic API auth

### Firewall Allowlist

Add the extracted hostnames. Example:

```
# From ANTHROPIC_BEDROCK_BASE_URL=https://ai-gateway.example.com/bedrock
ai-gateway.example.com
```

## Remote MCP Servers

### Detection

```bash
# Find all MCP config files that Claude may load
# User config: ~/.claude.json (contains mcpServers from `claude mcp add`)
# Global: ~/.claude/.mcp.json, ~/.claude/mcp.json
# Project: ./.mcp.json
# Scan for remote servers (type: sse, http, or streamable)
for f in ~/.claude.json ~/.claude/.mcp.json ~/.claude/mcp.json .mcp.json; do
  [ -f "$f" ] && jq -r '
    (.mcpServers // {}) | to_entries[]
    | select(.value.type == "sse" or .value.type == "http" or .value.type == "streamable")
    | .value.url
  ' "$f" 2>/dev/null
done
```

### Domain Extraction

```bash
# Same as gateway — extract hostname from URL
echo "https://mcp.slack.com/mcp" | sed 's|https\?://||; s|/.*||'
# → mcp.slack.com
```

### Firewall Allowlist

Add each extracted hostname. Stdio-based MCP servers (`"command": "bunx ..."`) don't need firewall entries since they run locally.

```
# Example: from .mcp.json with type: "http", url: "https://mcp.slack.com/mcp"
mcp.slack.com
```

## Common Firewall Domains (Always Included)

These domains are always allowed regardless of detected tools:

```
# Claude API (required)
api.anthropic.com
statsig.anthropic.com
sentry.io

# GitHub (common for most projects)
github.com
*.githubusercontent.com
objects.githubusercontent.com

# System
*.debian.org
*.ubuntu.com
deb.nodesource.com
```
