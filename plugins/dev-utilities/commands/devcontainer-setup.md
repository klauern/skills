---
allowed-tools: Bash, Read, Grep, Glob, Edit, Write
description: Scaffold a DevPod-compatible devcontainer for running Claude Code with SSH access and firewall restrictions
---

# /dev-utilities:devcontainer-setup

Scaffold a devcontainer for running Claude Code in an isolated DevPod container with SSH
access, firewall restrictions, and host `~/.claude/` bind mounts.

## Usage

```bash
/dev-utilities:devcontainer-setup
```

## Behavior

Invoke the **devcontainer-setup** skill:

1. Detect the project's tools and runtimes (see the skill's tool-detection reference).
2. Present the detected gateway and MCP server domains plus every proposed exact
   runtime version, and require explicit user confirmation before generating files.
3. Scaffold `.devcontainer-devpod/` (devcontainer.json, Dockerfile, firewall + setup
   scripts) plus the root-level `devcontainer-ssh.sh` entry script and `Taskfile.yml`
   tasks, all from the skill's templates reference.
4. Report the generated files and the quick-start commands
   (`./devcontainer-ssh.sh --claude` or `task devcontainer:claude`).

Requirements: Docker, DevPod (`brew install devpod`), and valid `~/.claude/` credentials
on the host.
