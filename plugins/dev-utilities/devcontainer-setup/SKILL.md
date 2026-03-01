---
name: devcontainer-setup
description: Scaffolds DevPod-compatible devcontainers for Claude Code with SSH access, firewall restrictions, and direct host ~/.claude/ + ~/.claude.json bind mounts. Detects project tools and generates Dockerfile, setup scripts, and Taskfile tasks.
version: 1.4.0
author: klauern
allowed-tools: Bash Read Grep Glob Edit Write
---

# Devcontainer Setup for Claude Code + DevPod

Scaffolds a DevPod-compatible devcontainer that runs Claude Code with SSH access, firewall restrictions, and mounts host `~/.claude/` + `~/.claude.json` directly into the container.

## Quick Start

**Command**: `/dev-utilities:devcontainer-setup` — Scaffold a devcontainer for Claude Code

**Documentation**:

- [Tool Detection](references/tool-detection.md) — Runtime/tool detection patterns per ecosystem
- [Templates](references/templates.md) — Base templates for generated files

## When to Use

**Invoke when**:

- User wants to run Claude Code in an isolated container
- User mentions DevPod or devcontainer SSH workflow
- User wants a sandboxed environment for Claude Code with firewall rules
- User asks for headless Claude Code setup (no IDE)

**Don't use for**:

- Standard VS Code devcontainer setup (no DevPod)
- Docker Compose-only workflows
- Claude Code installation on bare metal

## Workflow

### Phase 1: Project Analysis

Detect required tools and runtimes by reading project files. Check sources in priority order:

1. `CLAUDE.md` / `AGENTS.md` — Tool preferences, dev commands
2. `package.json` — Node/bun/npm ecosystem
3. `Gemfile` / `.ruby-version` — Ruby
4. `go.mod` — Go
5. `Cargo.toml` — Rust
6. `pyproject.toml` / `requirements.txt` / `uv.lock` — Python
7. `Taskfile.yml` — go-task
8. `.tool-versions` / `.mise.toml` — mise/asdf version manager
9. `Makefile` / `Justfile` — Build systems
10. `.github/workflows/*.yml` — CI tools hint at required runtimes
11. `docker-compose.yml` — Existing service dependencies

For each detected tool, extract version constraints where available. See [tool-detection.md](references/tool-detection.md) for extraction patterns.

#### API Gateway & MCP Server Detection

Scan `~/.claude/settings.json` and Claude MCP config files (`~/.claude.json`, `~/.claude/.mcp.json`, `~/.claude/mcp.json`, project `.mcp.json`) to detect custom domains the firewall must allow:

1. **Custom API gateways**: Read `env` block in `~/.claude/settings.json`. Look for any `*_BASE_URL` keys (e.g., `ANTHROPIC_BASE_URL`, `ANTHROPIC_BEDROCK_BASE_URL`). Extract the hostname from each URL and add it to the firewall allowlist.

2. **Auth token forwarding**: If a custom `*_BASE_URL` is detected, check whether `ANTHROPIC_AUTH_TOKEN` is set on the host (`printenv ANTHROPIC_AUTH_TOKEN`). Ensure auth env is forwarded via `containerEnv` (and keep in `remoteEnv` for IDE compatibility) so `devpod ssh` sessions see the same credentials.

3. **Remote MCP servers**: Scan MCP config files (`~/.claude.json`, `~/.claude/.mcp.json`, `~/.claude/mcp.json`, project-level `.mcp.json`) for servers with `"type": "sse"`, `"type": "http"`, or `"type": "streamable"`. Extract the hostname from each `"url"` value and add it to the firewall allowlist. Stdio-based MCP servers (those with `"command"`) don't need firewall entries.

**Output**: Present detected tools, gateway domains, and MCP server domains to user for confirmation before generating files.

### Phase 2: Scaffold Generation

Generate files into the **target project directory** (the project being containerized, not this plugin repo).

#### Directory: `.devcontainer-devpod/`

```
.devcontainer-devpod/
├── devcontainer.json          # DevPod-compatible config
├── Dockerfile                 # Official Claude Code base + detected tools
├── init-firewall.sh           # Network restrictions (iptables)
└── setup.sh                   # Post-create: symlinks, tool setup
```

#### Root-level files

```
devcontainer-ssh.sh            # Entry script: up + ssh + claude
```

If a `Taskfile.yml` exists, append `devcontainer:*` tasks. Otherwise create one.

Use templates from [templates.md](references/templates.md) as the base for each file, substituting detected tools and versions.

### Phase 3: Verification

Run these checks after generation:

1. **DevPod installed**: `which devpod` — warn if missing, link to install docs
2. **DevPod provider config**: Run `devpod provider list` — if it fails with "unknown field", the Docker provider config is corrupted (version mismatch). Fix: `devpod provider delete docker && devpod provider add docker`
3. **Dockerfile syntax**: `docker build --check` or dry-run parse
4. **File permissions**: Ensure `.sh` files are executable (`chmod +x`)
5. **devcontainer.json validity**: Parse as JSON to catch syntax errors
6. **Bind mounts**: Verify `~/.claude/` and `~/.claude.json` exist on host (created by `initializeCommand`)

Report results and next steps to the user.

## Generated File Details

### devcontainer.json

- `build.dockerfile` points to local `Dockerfile`
- `runArgs` includes `--cap-add=NET_ADMIN` and `--cap-add=NET_RAW` (required for iptables firewall)
- Omits `forwardPorts` (DevPod handles port mapping)
- `initializeCommand` ensures `~/.claude/` exists and `~/.claude.json` is present before bind mounts
- Mounts host `~/.claude/` to `/home/node/.claude` and host `~/.claude.json` to `/home/node/.claude.json`
- `containerEnv` forwards auth credentials and gateway env for runtime shells (`devpod ssh` sessions included)
- `remoteEnv` mirrors auth credentials plus `HOST_HOME` for IDE compatibility and host-path symlink setup
- Sets `HOME=/home/node` in container runtime env so Claude resolves config paths consistently
- Do not force `CLAUDE_CONFIG_DIR`; rely on `HOME`-based discovery to avoid MCP visibility issues
- Sets `remoteUser: "node"`
- `postCreateCommand` runs `setup.sh`
- `postStartCommand` runs `init-firewall.sh`
- Includes `customizations.vscode` only as empty object (no IDE dependency)

### Dockerfile

Layered approach:

1. **Base**: `node:20-bookworm` (matches official Claude Code devcontainer)
2. **System packages**: git, sudo, fzf, zsh, curl, iptables, jq, openssh-server
3. **Claude Code**: `npm install -g @anthropic-ai/claude-code@latest`
4. **Project tools**: Detected runtimes from Phase 1 (see [tool-detection.md](references/tool-detection.md))
5. **Firewall**: Copy `init-firewall.sh`, with graceful fallback if `NET_ADMIN` capability unavailable
6. **Cache directory**: `mkdir -p /home/node/.cache && chown node:node` (prevents EACCES from `claude install`)
7. **User**: `node` with `NOPASSWD:ALL` sudo access (standard for devcontainers)

### setup.sh

- Fixes ownership on Docker volumes (`.cache`, etc.) that are created as root
- Creates a symlink from host `~/.claude` path (via `HOST_HOME` env var) to `/home/node/.claude` so hardcoded plugin paths in `installed_plugins.json` resolve in-container
- Creates a symlink from host `~/.claude.json` path (via `HOST_HOME`) to `/home/node/.claude.json`
- Configures git safe directory
- Runs project-specific tool setup (inserted from Phase 1 detection)

### init-firewall.sh

Based on the official Claude Code devcontainer firewall. Restricts outbound traffic to:

- `api.anthropic.com` — Claude API
- `statsig.anthropic.com` — Telemetry
- `sentry.io` — Error reporting
- `*.githubusercontent.com` — GitHub raw content

Plus dynamically detected domains:

- **Custom API gateways**: Domains extracted from `*_BASE_URL` env vars in `~/.claude/settings.json`
- **Remote MCP servers**: Domains extracted from `url` fields in `~/.claude.json` and `.mcp.json` files (sse/http/streamable types only)
- **Project-specific registries**: Domains based on detected tools (see [tool-detection.md](references/tool-detection.md) for per-ecosystem allowlists)

### Entry Script (devcontainer-ssh.sh)

- `--claude`: Starts container, verifies bind mounts, runs auth/MCP preflight, launches Claude Code
- `--sync`: Verifies Claude bind mounts
- `--doctor` / `--auth-check`: Runs auth + MCP preflight checks without launching Claude
- `--down`: Stops container
- `--status`: Shows container status
- `--rebuild`: Deletes and rebuilds container from scratch
- `(none)`: Starts container, verifies bind mount, opens interactive SSH session

### Taskfile.yml Tasks

| Task                      | Description                                         |
| ------------------------- | --------------------------------------------------- |
| `devcontainer:ssh`        | SSH into running devcontainer (starts it if needed) |
| `devcontainer:claude`     | Start devcontainer and launch Claude Code           |
| `devcontainer:sync`       | Verify Claude config bind mounts                    |
| `devcontainer:doctor`     | Run Claude auth + MCP preflight checks              |
| `devcontainer:auth-check` | Alias for `devcontainer:doctor`                     |
| `devcontainer:down`       | Stop the devcontainer                               |
| `devcontainer:status`     | Show devcontainer status                            |
| `devcontainer:rebuild`    | Rebuild devcontainer from scratch                   |

## Decision Points

Prompt the user for these decisions:

1. **Firewall strictness**: "How strict should the firewall be?"
   - **Strict** (recommended): Only allow Claude API + detected package registries
   - **Permissive**: Allow all outbound (disable firewall)
   - **Custom**: User provides domain allowlist

2. **Auto-start Claude**: "Should the entry script auto-launch Claude Code?"
   - **Yes**: SSH in and immediately run `claude`
   - **No** (recommended): SSH in to a shell, run claude manually

## Model Strategy

| Task                                                   | Model  |
| ------------------------------------------------------ | ------ |
| File detection, version parsing, template substitution | Haiku  |
| Tool analysis, Dockerfile optimization, user decisions | Sonnet |

## Requirements

- Target project directory exists with source code
- Docker installed on host (for building/testing)
- DevPod installed on host (for container management)
- `~/.claude/` exists on host with valid credentials (auto-created by `initializeCommand`)
- `~/.claude.json` is readable on host (auto-created by `initializeCommand` if missing)

## Error Handling

| Issue                                     | Solution                                                                                                                                                                                                             |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DevPod not installed                      | Provide install link: `brew install devpod` or `curl -fsSL https://get.devpod.sh \| bash`                                                                                                                           |
| No project files found                    | Generate minimal Dockerfile with just Claude Code                                                                                                                                                                    |
| Docker build fails                        | Check Dockerfile syntax, verify base image availability                                                                                                                                                              |
| Firewall blocks required domain           | Add domain to allowlist in `init-firewall.sh`                                                                                                                                                                        |
| Bind mount fails                          | Ensure `~/.claude/` exists on host (`initializeCommand` should create it). On Windows, use `${localEnv:USERPROFILE}` instead of `${localEnv:HOME}`                                                                   |
| DevPod "unknown field" in provider config | Provider JSON at `~/.devpod/contexts/default/providers/docker/provider.json` has fields from a newer DevPod version. Fix: `devpod provider delete docker && devpod provider add docker` to regenerate a clean config |
| Firewall script sudo fails                | Ensure sudoers grants NOPASSWD for the firewall script path, iptables, ip6tables, and ipset. Do NOT wrap with `sudo bash` — use `sudo /path/to/script` since scripts have shebangs                                   |

## Version History

- **1.4.0**: Add runtime-safe auth forwarding (`containerEnv` + `remoteEnv`), mount/symlink host `~/.claude.json`, add `--doctor`/`--auth-check` preflight flow, and align Taskfile tasks with script flags
- **1.3.0**: Auto-detect custom API gateways (`*_BASE_URL` in settings.json) and remote MCP servers (sse/http/streamable entries from user/project MCP config) — extract domains for firewall allowlist, forward `ANTHROPIC_AUTH_TOKEN` when custom gateway detected
- **1.2.0**: Add `runArgs` (NET_ADMIN/NET_RAW), `remoteEnv` (ANTHROPIC_API_KEY, HOST_HOME), `.cache` directory fix, host path symlink in setup.sh, bind mount verification in entry script
- **1.1.0**: Replace config sync infrastructure with direct `~/.claude/` host bind mount
- **1.0.0**: Initial release with DevPod + SSH + firewall + config mirroring
