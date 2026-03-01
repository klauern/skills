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
  "runArgs": [
    "--cap-add=NET_ADMIN",
    "--cap-add=NET_RAW",
    "--hostname={{project-name}}"
  ],
  "remoteUser": "node",
  "initializeCommand": "mkdir -p ~/.claude",
  "mounts": [
    "source=${localEnv:HOME}/.claude,target=/home/node/.claude,type=bind"
  ],
  "remoteEnv": {
    "{{ANTHROPIC_AUTH_ENV_VAR}}": "${localEnv:{{ANTHROPIC_AUTH_ENV_VAR}}}",
    "HOST_HOME": "${localEnv:HOME}"
  },
  "postCreateCommand": "bash .devcontainer-devpod/setup.sh",
  "postStartCommand": "sudo .devcontainer-devpod/init-firewall.sh || echo 'WARNING: Firewall init failed (missing NET_ADMIN capability).'",
  "customizations": {},
  "features": {}
}
```

> **Notes on `${localEnv:HOME}`**:
> - `initializeCommand` runs on the **host shell** (where `~` expands normally) to ensure `~/.claude/` exists before Docker attempts the bind mount.
> - `${localEnv:HOME}` is a devcontainer variable resolved on the host. On Windows, use `${localEnv:USERPROFILE}` instead.
> - The mount is **read-write** — changes inside the container (e.g., new credentials, updated settings) persist to the host.
>
> **Notes on `remoteEnv`**:
> - `{{ANTHROPIC_AUTH_ENV_VAR}}` is a placeholder — substitute the correct auth env var based on detection:
>   - If `~/.claude/settings.json` contains any `*_BASE_URL` env (custom API gateway): use `ANTHROPIC_AUTH_TOKEN`
>   - Otherwise (direct Anthropic API): use `ANTHROPIC_API_KEY`
> - `HOST_HOME` is used by `setup.sh` to create a symlink from the host's `~/.claude` path to `/home/node/.claude`, so hardcoded plugin paths in `installed_plugins.json` resolve correctly in-container.

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
RUN echo "node ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/node-nopasswd \
    && chmod 0440 /etc/sudoers.d/node-nopasswd

# User setup
RUN usermod -aG sudo node

# Ensure .cache directory exists with correct ownership (for claude install, etc.)
RUN mkdir -p /home/node/.cache \
    && chown node:node /home/node/.cache

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

# Check for required capabilities (NET_ADMIN)
if ! iptables -L -n >/dev/null 2>&1; then
  echo "WARNING: iptables not available (missing NET_ADMIN capability)."
  echo "Container running without network restrictions."
  echo "To enable firewall, start container with: --cap-add=NET_ADMIN --cap-add=NET_RAW"
  exit 0
fi

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

    # {{GATEWAY_DOMAINS}}
    # Custom API gateway domains extracted from *_BASE_URL env vars
    # in ~/.claude/settings.json (e.g., ANTHROPIC_BASE_URL, ANTHROPIC_BEDROCK_BASE_URL).
    # Only the hostname is added — not the full URL.

    # {{MCP_SERVER_DOMAINS}}
    # Remote MCP server domains extracted from .mcp.json files
    # (sse/http/streamable types only; stdio servers don't need network access).
    # Scanned from: ~/.claude/.mcp.json, ~/.claude/mcp.json, project .mcp.json
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

# Fix ownership on Docker volumes (created as root by default)
for dir in /home/node/.cache; do
  if [ -d "$dir" ]; then
    sudo chown -R node:node "$dir"
  fi
done

# Symlink host .claude path so hardcoded plugin paths resolve in-container
# (installed_plugins.json / known_marketplaces.json reference host absolute paths)
HOST_CLAUDE_DIR="${HOST_HOME:-}/.claude"
if [ -n "${HOST_HOME:-}" ] && [ "$HOST_CLAUDE_DIR" != "/home/node/.claude" ]; then
  sudo mkdir -p "$(dirname "$HOST_CLAUDE_DIR")"
  sudo ln -sfn /home/node/.claude "$HOST_CLAUDE_DIR"
  echo "  Created symlink: $HOST_CLAUDE_DIR -> /home/node/.claude"
fi

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

## devcontainer-ssh.sh

```bash
#!/bin/bash
# DevPod + Claude Code entry script
# Usage: ./devcontainer-ssh.sh [--claude] [--down] [--status] [--rebuild]
set -euo pipefail

PROJECT_NAME="{{project-name}}"
DEVCONTAINER_PATH=".devcontainer-devpod/devcontainer.json"
CONTAINER_LABEL="dev.containers.id=$PROJECT_NAME"

# ── Helpers ──────────────────────────────────────────────────────────────────
get_container_name() {
  docker ps -q --filter "label=$CONTAINER_LABEL" | head -1
}

sync_claude_config() {
  echo "==> Claude config is bind-mounted from host. No sync needed."

  local container
  container=$(get_container_name)
  if [ -z "$container" ]; then
    echo "  ERROR: Container not running. Start it first."
    return 1
  fi

  # Verify the bind mount is working
  if docker exec "$container" test -f /home/node/.claude/settings.json; then
    echo "  Bind mount verified: /home/node/.claude"
  else
    echo "  WARNING: /home/node/.claude/settings.json not found. Check bind mount."
  fi
}

ensure_running() {
  local container
  container=$(get_container_name)
  if [ -z "$container" ]; then
    echo "==> Starting container..."
    devpod up . --devcontainer-path "$DEVCONTAINER_PATH" --id "$PROJECT_NAME" --ide none
  fi
}

# ── Commands ─────────────────────────────────────────────────────────────────
case "${1:-}" in
  --claude)
    ensure_running
    sync_claude_config
    echo "==> Launching Claude Code..."
    claude_cmd="cd /home/node/workspace && claude --dangerously-skip-permissions"
    # Forward the auth token matching the API configuration:
    #   Custom gateway (*_BASE_URL in settings.json) → ANTHROPIC_AUTH_TOKEN
    #   Direct Anthropic API                         → ANTHROPIC_API_KEY
    if [ -n "${ANTHROPIC_AUTH_TOKEN:-}" ]; then
      claude_cmd="export ANTHROPIC_AUTH_TOKEN='${ANTHROPIC_AUTH_TOKEN}' && ${claude_cmd}"
    elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
      claude_cmd="export ANTHROPIC_API_KEY='${ANTHROPIC_API_KEY}' && ${claude_cmd}"
    fi
    devpod ssh "$PROJECT_NAME" --command "$claude_cmd"
    ;;

  --down)
    echo "==> Stopping container..."
    devpod stop "$PROJECT_NAME"
    ;;

  --status)
    devpod status "$PROJECT_NAME" 2>/dev/null || echo "Container not found. Run ./devcontainer-ssh.sh to start."
    ;;

  --rebuild)
    echo "==> Rebuilding container from scratch..."
    devpod delete "$PROJECT_NAME" 2>/dev/null || true
    devpod up . --devcontainer-path "$DEVCONTAINER_PATH" --id "$PROJECT_NAME" --ide none
    sync_claude_config
    echo "==> Rebuild complete. Run ./devcontainer-ssh.sh to connect."
    ;;

  --help|-h)
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  (none)      SSH into the devcontainer (default)"
    echo "  --claude    Launch Claude Code inside the container"
    echo "  --down      Stop the container"
    echo "  --status    Show container status"
    echo "  --rebuild   Delete and rebuild the container"
    echo "  --help      Show this help"
    ;;

  "")
    ensure_running
    sync_claude_config
    echo "==> Connecting via SSH..."
    devpod ssh "$PROJECT_NAME"
    ;;

  *) echo "Unknown option: $1"; exit 1 ;;
esac
```

## Taskfile.yml (devcontainer tasks)

Append these tasks to an existing `Taskfile.yml` or create a new one:

```yaml
version: "3"

tasks:
  devcontainer:up:
    desc: Start the devcontainer via DevPod
    cmds:
      - devpod up . --devcontainer-path .devcontainer-devpod/devcontainer.json --id {{project-name}} --ide none

  devcontainer:ssh:
    desc: SSH into running container
    cmds:
      - devpod ssh .

  devcontainer:claude:
    desc: "Full workflow: up + ssh + claude"
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

