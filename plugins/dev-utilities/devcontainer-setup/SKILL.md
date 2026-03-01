---
name: devcontainer-setup
description: Scaffolds DevPod-compatible devcontainers for Claude Code with SSH access, firewall restrictions, and automatic config mirroring. Detects project tools and generates Dockerfile, setup scripts, and Taskfile tasks.
version: 1.0.0
allowed-tools: Bash Read Grep Glob Edit Write
---

# Devcontainer Setup for Claude Code + DevPod

Scaffolds a DevPod-compatible devcontainer that runs Claude Code with SSH access, firewall restrictions, and automatic config mirroring from the host.

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
├── setup.sh                   # Post-create: permissions, symlinks, tool setup
├── sync-claude-config.sh      # Mirror host ~/.claude/ into container
└── devpod-data/
    └── .gitkeep               # Persistent config mount point
```

#### Root-level files

```
devcontainer-ssh.sh            # Entry script: up + sync + ssh + claude
```

If a `Taskfile.yml` exists, append `devcontainer:*` tasks. Otherwise create one.

Use templates from [templates.md](references/templates.md) as the base for each file, substituting detected tools and versions.

### Phase 3: Config Mirroring Setup

The `sync-claude-config.sh` script handles mirroring host `~/.claude/` into the container.

**Files to mirror**:
- `~/.claude/settings.json` — User settings
- `~/.claude/credentials.json` — Auth credentials
- `~/.claude/.claude.json` — Claude state
- `~/.claude/.mcp.json` — MCP server config
- `~/.claude/plugins/` — Plugin configurations
- `~/.claude/projects/` — Project-specific settings (filtered to current project)

**Files to skip**:
- `~/.claude/cache/` — Transient
- `~/.claude/logs/` — Transient
- `~/.claude/teams/` — Session-specific
- `~/.claude/tasks/` — Session-specific

### Phase 4: Verification

Run these checks after generation:

1. **DevPod installed**: `which devpod` — warn if missing, link to install docs
2. **Dockerfile syntax**: `docker build --check` or dry-run parse
3. **File permissions**: Ensure `.sh` files are executable (`chmod +x`)
4. **devcontainer.json validity**: Parse as JSON to catch syntax errors
5. **Git integration**: Suggest adding `.devcontainer-devpod/devpod-data/` to `.gitignore`

Report results and next steps to the user.

## Generated File Details

### devcontainer.json

- `build.dockerfile` points to local `Dockerfile`
- Omits `forwardPorts` (DevPod handles port mapping)
- Mounts `devpod-data/claude/` to `/home/node/.claude` for persistence
- Sets `remoteUser: "node"`
- `postCreateCommand` runs `setup.sh`
- `postStartCommand` runs `init-firewall.sh`
- Includes `customizations.vscode` only as empty object (no IDE dependency)

### Dockerfile

Layered approach:
1. **Base**: `node:20-bookworm` (matches official Claude Code devcontainer)
2. **System packages**: git, sudo, fzf, zsh, curl, iptables, rsync, jq, openssh-server
3. **Claude Code**: `npm install -g @anthropic-ai/claude-code@latest`
4. **Project tools**: Detected runtimes from Phase 1 (see [tool-detection.md](references/tool-detection.md))
5. **Firewall**: Copy `init-firewall.sh`, configure sudoers for iptables
6. **User**: `node` with sudo access

### init-firewall.sh

Based on the official Claude Code devcontainer firewall. Restricts outbound traffic to:
- `api.anthropic.com` — Claude API
- `statsig.anthropic.com` — Telemetry
- `sentry.io` — Error reporting
- `*.githubusercontent.com` — GitHub raw content

Plus project-specific domains based on detected tools (see [tool-detection.md](references/tool-detection.md) for per-ecosystem allowlists).

### Entry Script (devcontainer-ssh.sh)

```bash
#!/bin/bash
# 1. devpod up . --devcontainer-path .devcontainer-devpod/devcontainer.json --ide none
# 2. Run sync-claude-config.sh to mirror host config
# 3. devpod ssh . (opens interactive session)
# 4. Inside container: claude --dangerously-skip-permissions (optional)
```

### Taskfile.yml Tasks

| Task | Description |
|------|-------------|
| `devcontainer:up` | Start the devcontainer via DevPod |
| `devcontainer:ssh` | SSH into running container |
| `devcontainer:sync` | Sync Claude config from host |
| `devcontainer:claude` | Full workflow: up + sync + ssh + claude |
| `devcontainer:stop` | Stop the container |
| `devcontainer:delete` | Delete the workspace |
| `devcontainer:status` | Show workspace status |

## Decision Points

Prompt the user for these decisions:

1. **Firewall strictness**: "How strict should the firewall be?"
   - **Strict** (recommended): Only allow Claude API + detected package registries
   - **Permissive**: Allow all outbound (disable firewall)
   - **Custom**: User provides domain allowlist

2. **Config persistence**: "How should Claude config be persisted?"
   - **Mount** (recommended): Bind-mount `devpod-data/claude/` for persistence across rebuilds
   - **Sync-only**: Rsync on each session start, no persistence
   - **None**: Fresh config each time

3. **Auto-start Claude**: "Should the entry script auto-launch Claude Code?"
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
- `~/.claude/` exists with valid credentials (for mirroring)

## Error Handling

| Issue | Solution |
|-------|----------|
| DevPod not installed | Provide install link: `brew install devpod` or `curl -fsSL https://get.devpod.sh | bash` |
| No project files found | Generate minimal Dockerfile with just Claude Code |
| Docker build fails | Check Dockerfile syntax, verify base image availability |
| Firewall blocks required domain | Add domain to allowlist in `init-firewall.sh` |
| Config sync fails | Check `~/.claude/` permissions, verify rsync installed |

## Version History

- **1.0.0**: Initial release with DevPod + SSH + firewall + config mirroring
