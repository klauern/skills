---
description: Scaffold a DevPod-compatible devcontainer for running Claude Code with SSH access and firewall restrictions
---

# Devcontainer Setup

Scaffold a devcontainer for running Claude Code in an isolated DevPod container with SSH access, firewall restrictions, and direct host `~/.claude/` + `~/.claude.json` bind mounts.

## What This Does

This command will:

1. **Analyze** the current project to detect required tools and runtimes
2. **Scaffold** a `.devcontainer-devpod/` directory with DevPod-compatible configuration
3. **Generate** a Dockerfile based on the official Claude Code devcontainer plus detected tools
4. **Create** an entry script for SSH access and Claude Code launching
5. **Add** Taskfile tasks for common devcontainer operations, including auth preflight checks

## Usage

```bash
/dev-utilities:devcontainer-setup
```

## Generated Files

### In `.devcontainer-devpod/`

| File                | Purpose                                           |
| ------------------- | ------------------------------------------------- |
| `devcontainer.json` | DevPod-compatible container configuration         |
| `Dockerfile`        | Official Claude Code base + project tools         |
| `init-firewall.sh`  | iptables rules restricting outbound traffic       |
| `setup.sh`          | Post-create permissions, symlinks, and tool setup |

### In project root

| File                  | Purpose                                     |
| --------------------- | ------------------------------------------- |
| `devcontainer-ssh.sh` | Entry script: up + ssh + claude             |
| `Taskfile.yml`        | devcontainer:\* tasks (created or appended) |

Generated Taskfile tasks align with script flags:

- `devcontainer:ssh`
- `devcontainer:claude`
- `devcontainer:sync`
- `devcontainer:doctor` (and alias `devcontainer:auth-check`)
- `devcontainer:down`
- `devcontainer:status`
- `devcontainer:rebuild`

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
task devcontainer:doctor

# Option 3: Manual steps
devpod up . --devcontainer-path .devcontainer-devpod/devcontainer.json --ide none
devpod ssh .
# Inside container:
claude
```

Useful maintenance commands after generation:

```bash
task devcontainer:status
task devcontainer:rebuild
task devcontainer:auth-check
```
