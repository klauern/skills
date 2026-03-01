---
name: devcontainer-setup
description: Scaffolds DevPod-compatible devcontainers for Claude Code with SSH access, firewall restrictions, and direct host ~/.claude/ bind mount. Detects project tools and generates Dockerfile, setup scripts, and Taskfile tasks.
version: 1.2.0
allowed-tools: Bash Read Grep Glob Edit Write
---

# Devcontainer Setup for Claude Code + DevPod

Scaffolds a DevPod-compatible devcontainer that runs Claude Code with SSH access, firewall restrictions, and mounts host `~/.claude/` directly into the container.

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

**Output**: Present detected tools to user for confirmation before generating files.

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
6. **Bind mount**: Verify `~/.claude/` exists on host (created by `initializeCommand`)

Report results and next steps to the user.

## Generated File Details

### devcontainer.json

- `build.dockerfile` points to local `Dockerfile`
- `runArgs` includes `--cap-add=NET_ADMIN` and `--cap-add=NET_RAW` (required for iptables firewall)
- Omits `forwardPorts` (DevPod handles port mapping)
- `initializeCommand` ensures `~/.claude/` exists on host before bind mount
- Mounts host `~/.claude/` to `/home/node/.claude` via `${localEnv:HOME}` bind mount
- `remoteEnv` forwards `ANTHROPIC_API_KEY` and `HOST_HOME` from host into container
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
- Symlinks `.claude.json` to home directory
- Configures git safe directory
- Runs project-specific tool setup (inserted from Phase 1 detection)

### init-firewall.sh

Based on the official Claude Code devcontainer firewall. Restricts outbound traffic to:
- `api.anthropic.com` — Claude API
- `statsig.anthropic.com` — Telemetry
- `sentry.io` — Error reporting
- `*.githubusercontent.com` — GitHub raw content

Plus project-specific domains based on detected tools (see [tool-detection.md](references/tool-detection.md) for per-ecosystem allowlists).

### Entry Script (devcontainer-ssh.sh)

- `--claude`: Starts container, verifies bind mount, forwards `ANTHROPIC_API_KEY`, launches Claude Code
- `--down`: Stops container
- `--status`: Shows container status
- `--rebuild`: Deletes and rebuilds container from scratch
- `(none)`: Starts container, verifies bind mount, opens interactive SSH session

### Taskfile.yml Tasks

| Task | Description |
|------|-------------|
| `devcontainer:up` | Start the devcontainer via DevPod |
| `devcontainer:ssh` | SSH into running container |
| `devcontainer:claude` | Full workflow: up + ssh + claude |
| `devcontainer:stop` | Stop the container |
| `devcontainer:delete` | Delete the workspace |
| `devcontainer:status` | Show workspace status |

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

| Task | Model |
|------|-------|
| File detection, version parsing, template substitution | Haiku |
| Tool analysis, Dockerfile optimization, user decisions | Sonnet |

## Requirements

- Target project directory exists with source code
- Docker installed on host (for building/testing)
- DevPod installed on host (for container management)
- `~/.claude/` exists on host with valid credentials (auto-created by `initializeCommand`)

## Error Handling

| Issue | Solution |
|-------|----------|
| DevPod not installed | Provide install link: `brew install devpod` or `curl -fsSL https://get.devpod.sh | bash` |
| No project files found | Generate minimal Dockerfile with just Claude Code |
| Docker build fails | Check Dockerfile syntax, verify base image availability |
| Firewall blocks required domain | Add domain to allowlist in `init-firewall.sh` |
| Bind mount fails | Ensure `~/.claude/` exists on host (`initializeCommand` should create it). On Windows, use `${localEnv:USERPROFILE}` instead of `${localEnv:HOME}` |
| DevPod "unknown field" in provider config | Provider JSON at `~/.devpod/contexts/default/providers/docker/provider.json` has fields from a newer DevPod version. Fix: `devpod provider delete docker && devpod provider add docker` to regenerate a clean config |
| Firewall script sudo fails | Ensure sudoers grants NOPASSWD for the firewall script path, iptables, ip6tables, and ipset. Do NOT wrap with `sudo bash` — use `sudo /path/to/script` since scripts have shebangs |

## Version History

- **1.2.0**: Add `runArgs` (NET_ADMIN/NET_RAW), `remoteEnv` (ANTHROPIC_API_KEY, HOST_HOME), `.cache` directory fix, host path symlink in setup.sh, bind mount verification in entry script
- **1.1.0**: Replace config sync infrastructure with direct `~/.claude/` host bind mount
- **1.0.0**: Initial release with DevPod + SSH + firewall + config mirroring
