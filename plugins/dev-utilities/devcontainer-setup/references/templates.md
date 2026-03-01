# File Templates

Base templates for generated files. Replace `{{placeholders}}` with detected values.

## devcontainer.json

```json
{
  "name": "{{project-name}}-claude-devpod",
  "build": {
    "dockerfile": "Dockerfile",
    "context": "."
  },
  "remoteUser": "node",
  "mounts": [
    "source=${localWorkspaceFolder}/.devcontainer-devpod/devpod-data/claude,target=/home/node/.claude,type=bind,consistency=cached"
  ],
  "postCreateCommand": "bash .devcontainer-devpod/setup.sh",
  "postStartCommand": "sudo bash .devcontainer-devpod/init-firewall.sh",
  "customizations": {},
  "features": {}
}
```

## Dockerfile

```dockerfile
FROM node:20-bookworm

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    fzf \
    zsh \
    curl \
    wget \
    iptables \
    rsync \
    jq \
    openssh-server \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Claude Code
RUN npm install -g @anthropic-ai/claude-code@latest

# {{TOOL_INSTALL_BLOCK}}
# Project-specific tools are inserted here based on Phase 1 detection.
# See tool-detection.md for per-ecosystem Dockerfile snippets.

# Firewall setup
COPY init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod +x /usr/local/bin/init-firewall.sh

# Sudoers for firewall (iptables requires root)
RUN echo "node ALL=(ALL) NOPASSWD: /usr/sbin/iptables, /usr/sbin/ip6tables, /usr/local/bin/init-firewall.sh" >> /etc/sudoers.d/node-firewall \
    && chmod 0440 /etc/sudoers.d/node-firewall

# User setup
RUN usermod -aG sudo node
USER node
WORKDIR /home/node/workspace
```

## init-firewall.sh

```bash
#!/bin/bash
# Network firewall for Claude Code devcontainer
# Based on: https://github.com/anthropics/claude-code/tree/main/.devcontainer
#
# Restricts outbound traffic to approved domains only.
# Run as: sudo bash init-firewall.sh

set -euo pipefail

# Flush existing rules
iptables -F OUTPUT 2>/dev/null || true
ip6tables -F OUTPUT 2>/dev/null || true

# Allow loopback
iptables -A OUTPUT -o lo -j ACCEPT
ip6tables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
ip6tables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow DNS
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT
ip6tables -A OUTPUT -p udp --dport 53 -j ACCEPT
ip6tables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# Allowed domains
ALLOWED_DOMAINS=(
    # Claude API (required)
    "api.anthropic.com"
    "statsig.anthropic.com"
    "sentry.io"

    # GitHub
    "github.com"
    "objects.githubusercontent.com"
    "raw.githubusercontent.com"

    # npm registry (for Claude Code updates)
    "registry.npmjs.org"

    # System package repos
    "deb.debian.org"
    "security.debian.org"
    "deb.nodesource.com"

    # {{TOOL_DOMAINS}}
    # Project-specific domains added here based on detected tools.
    # See tool-detection.md for per-ecosystem firewall allowlists.
)

# Resolve and allow each domain
for domain in "${ALLOWED_DOMAINS[@]}"; do
    # Skip comments
    [[ "$domain" =~ ^# ]] && continue

    # Resolve domain to IPs
    ips=$(dig +short "$domain" 2>/dev/null | grep -E '^[0-9]' || true)
    for ip in $ips; do
        iptables -A OUTPUT -d "$ip" -j ACCEPT 2>/dev/null || true
    done

    # Also resolve AAAA records
    ipv6s=$(dig +short AAAA "$domain" 2>/dev/null | grep -E '^[0-9a-f]' || true)
    for ip6 in $ipv6s; do
        ip6tables -A OUTPUT -d "$ip6" -j ACCEPT 2>/dev/null || true
    done
done

# Default deny outbound
iptables -A OUTPUT -j DROP
ip6tables -A OUTPUT -j DROP

echo "Firewall configured: ${#ALLOWED_DOMAINS[@]} domains allowed, all other outbound blocked."
```

## setup.sh

```bash
#!/bin/bash
# Post-create setup for Claude Code devcontainer
set -euo pipefail

echo "=== Claude Code Devcontainer Setup ==="

# Fix permissions on mounted directories
if [ -d "/home/node/.claude" ]; then
    sudo chown -R node:node /home/node/.claude
fi

# Create Claude config directory if not mounted
mkdir -p /home/node/.claude

# Symlink Claude config files if they exist in mounted volume
if [ -f "/home/node/.claude/.claude.json" ]; then
    ln -sf /home/node/.claude/.claude.json /home/node/.claude.json 2>/dev/null || true
fi

# Configure git to trust workspace
git config --global --add safe.directory /home/node/workspace

# {{TOOL_SETUP_BLOCK}}
# Project-specific post-create setup inserted here.
# Example: mise install, bundle install, npm install, etc.

echo "=== Setup complete ==="
echo "Run 'claude' to start Claude Code"
```

## sync-claude-config.sh

```bash
#!/bin/bash
# Sync Claude config from host into devcontainer
# Run from HOST before SSH session
set -euo pipefail

WORKSPACE_NAME="{{project-name}}"
DEVPOD_DATA=".devcontainer-devpod/devpod-data/claude"

echo "Syncing Claude config to devcontainer..."

# Create target directory
mkdir -p "$DEVPOD_DATA"

# Files to sync
SYNC_FILES=(
    "settings.json"
    "credentials.json"
    ".claude.json"
    ".mcp.json"
)

for f in "${SYNC_FILES[@]}"; do
    src="$HOME/.claude/$f"
    if [ -f "$src" ]; then
        cp "$src" "$DEVPOD_DATA/$f"
        echo "  Synced $f"
    fi
done

# Sync directories
SYNC_DIRS=(
    "plugins"
)

for d in "${SYNC_DIRS[@]}"; do
    src="$HOME/.claude/$d"
    if [ -d "$src" ]; then
        rsync -a --delete "$src/" "$DEVPOD_DATA/$d/"
        echo "  Synced $d/"
    fi
done

# Sync project-specific settings (filtered to current project)
PROJECTS_DIR="$HOME/.claude/projects"
if [ -d "$PROJECTS_DIR" ]; then
    mkdir -p "$DEVPOD_DATA/projects"
    rsync -a --delete "$PROJECTS_DIR/" "$DEVPOD_DATA/projects/"
    echo "  Synced projects/"
fi

echo "Config sync complete."
```

## devcontainer-ssh.sh

```bash
#!/bin/bash
# DevPod + Claude Code entry script
# Usage: ./devcontainer-ssh.sh [--claude] [--sync-only]
set -euo pipefail

DEVCONTAINER_PATH=".devcontainer-devpod/devcontainer.json"
SYNC_SCRIPT=".devcontainer-devpod/sync-claude-config.sh"

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --claude       Auto-launch Claude Code after SSH"
    echo "  --sync-only    Only sync config, don't start container"
    echo "  --no-sync      Skip config sync"
    echo "  -h, --help     Show this help"
}

AUTO_CLAUDE=false
SYNC_ONLY=false
NO_SYNC=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --claude) AUTO_CLAUDE=true; shift ;;
        --sync-only) SYNC_ONLY=true; shift ;;
        --no-sync) NO_SYNC=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Step 1: Sync Claude config from host
if [ "$NO_SYNC" = false ]; then
    echo ">>> Syncing Claude config..."
    bash "$SYNC_SCRIPT"
fi

if [ "$SYNC_ONLY" = true ]; then
    echo "Config synced. Exiting."
    exit 0
fi

# Step 2: Start/create DevPod workspace
echo ">>> Starting DevPod workspace..."
devpod up . --devcontainer-path "$DEVCONTAINER_PATH" --ide none

# Step 3: SSH into container
if [ "$AUTO_CLAUDE" = true ]; then
    echo ">>> Connecting and launching Claude Code..."
    devpod ssh . --command "claude --dangerously-skip-permissions"
else
    echo ">>> Connecting via SSH..."
    devpod ssh .
fi
```

## Taskfile.yml (devcontainer tasks)

Append these tasks to an existing `Taskfile.yml` or create a new one:

```yaml
version: "3"

tasks:
  devcontainer:up:
    desc: Start the devcontainer via DevPod
    cmds:
      - devpod up . --devcontainer-path .devcontainer-devpod/devcontainer.json --ide none

  devcontainer:ssh:
    desc: SSH into running container
    cmds:
      - devpod ssh .

  devcontainer:sync:
    desc: Sync Claude config from host
    cmds:
      - bash .devcontainer-devpod/sync-claude-config.sh

  devcontainer:claude:
    desc: "Full workflow: up + sync + ssh + claude"
    cmds:
      - bash devcontainer-ssh.sh --claude

  devcontainer:stop:
    desc: Stop the devcontainer
    cmds:
      - devpod stop .

  devcontainer:delete:
    desc: Delete the workspace entirely
    cmds:
      - devpod delete .

  devcontainer:status:
    desc: Show workspace status
    cmds:
      - devpod status .
```

## .gitignore additions

Add to the target project's `.gitignore`:

```
# DevPod devcontainer data (credentials, local state)
.devcontainer-devpod/devpod-data/
```
