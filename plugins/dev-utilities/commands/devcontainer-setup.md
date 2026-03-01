---
description: Scaffold a DevPod-compatible devcontainer for running Claude Code with SSH access and firewall restrictions
---

# Devcontainer Setup

Scaffold a devcontainer for running Claude Code in an isolated DevPod container with SSH access, firewall restrictions, and automatic config mirroring from the host.

## What This Does

This command will:

1. **Analyze** the current project to detect required tools and runtimes
2. **Scaffold** a `.devcontainer-devpod/` directory with DevPod-compatible configuration
3. **Generate** a Dockerfile based on the official Claude Code devcontainer plus detected tools
4. **Create** entry scripts for SSH access and Claude config syncing
5. **Add** Taskfile tasks for common devcontainer operations

## Usage

```bash
/dev-utilities:devcontainer-setup
```

## Generated Files

### In `.devcontainer-devpod/`

| File | Purpose |
|------|---------|
| `devcontainer.json` | DevPod-compatible container configuration |
| `Dockerfile` | Official Claude Code base + project tools |
| `init-firewall.sh` | iptables rules restricting outbound traffic |
| `setup.sh` | Post-create permissions and tool setup |
| `sync-claude-config.sh` | Mirror host `~/.claude/` into container |
| `devpod-data/.gitkeep` | Persistent config mount point |

### In project root

| File | Purpose |
|------|---------|
| `devcontainer-ssh.sh` | Entry script: up + sync + ssh + claude |
| `Taskfile.yml` | devcontainer:* tasks (created or appended) |

## Requirements

- Docker installed on host
- DevPod installed (`brew install devpod` or `curl -fsSL https://get.devpod.sh | bash`)
- `~/.claude/` with valid credentials

## Quick Start After Generation

```bash
# Option 1: Use the entry script
./devcontainer-ssh.sh --claude

# Option 2: Use Taskfile
task devcontainer:claude

# Option 3: Manual steps
devpod up . --devcontainer-path .devcontainer-devpod/devcontainer.json --ide none
bash .devcontainer-devpod/sync-claude-config.sh
devpod ssh .
# Inside container:
claude
```
