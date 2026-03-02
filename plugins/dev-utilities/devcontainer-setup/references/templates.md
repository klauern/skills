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
  "initializeCommand": "mkdir -p ~/.claude && [ -f ~/.claude.json ] || printf '{}\\n' > ~/.claude.json",
  "mounts": [
    "source=${localEnv:HOME}/.claude,target=/home/node/.claude,type=bind",
    "source=${localEnv:HOME}/.claude.json,target=/home/node/.claude.json,type=bind"
  ],
  "containerEnv": {
    "HOME": "/home/node",
    "ANTHROPIC_AUTH_TOKEN": "${localEnv:ANTHROPIC_AUTH_TOKEN}",
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}",
    "ANTHROPIC_CUSTOM_HEADERS": "${localEnv:ANTHROPIC_CUSTOM_HEADERS}",
    "ANTHROPIC_BEDROCK_BASE_URL": "${localEnv:ANTHROPIC_BEDROCK_BASE_URL}",
    "CLAUDE_CODE_USE_BEDROCK": "${localEnv:CLAUDE_CODE_USE_BEDROCK}",
    "CLAUDE_CODE_SKIP_BEDROCK_AUTH": "${localEnv:CLAUDE_CODE_SKIP_BEDROCK_AUTH}",
    "NODE_USE_SYSTEM_CA": "1"
  },
  "remoteEnv": {
    "ANTHROPIC_AUTH_TOKEN": "${localEnv:ANTHROPIC_AUTH_TOKEN}",
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}",
    "ANTHROPIC_CUSTOM_HEADERS": "${localEnv:ANTHROPIC_CUSTOM_HEADERS}",
    "HOST_HOME": "${localEnv:HOME}"
  },
  "postCreateCommand": "bash .devcontainer-devpod/setup.sh",
  "postStartCommand": "sudo .devcontainer-devpod/init-firewall.sh || echo 'WARNING: Firewall init failed (missing NET_ADMIN capability).'",
  "customizations": {},
  "features": {}
}
```

> **Notes on `${localEnv:HOME}`**:
>
> - `initializeCommand` runs on the **host shell** (where `~` expands normally) to ensure `~/.claude/` and `~/.claude.json` exist before Docker attempts bind mounts.
> - `${localEnv:HOME}` is a devcontainer variable resolved on the host. On Windows, use `${localEnv:USERPROFILE}` instead.
> - The mount is **read-write** — changes inside the container (e.g., new credentials, updated settings) persist to the host.
>
> **Windows host notes**:
>
> - DevPod on Windows uses Git Bash or WSL2, where `mkdir -p` works as-is.
> - If using cmd.exe or PowerShell directly, replace `initializeCommand` with: `"powershell -Command \"New-Item -ItemType Directory -Force -Path $env:USERPROFILE\\.claude | Out-Null; New-Item -ItemType File -Force -Path $env:USERPROFILE\\.claude.json | Out-Null\""`
> - Replace the mount source with `${localEnv:USERPROFILE}/.claude`.
>
> **Notes on auth/env forwarding**:
>
> - Put auth env in `containerEnv` so values exist in `devpod ssh` sessions (not just IDE-attached sessions).
> - Keep matching keys in `remoteEnv` for IDE compatibility.
> - Forward both `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_API_KEY`; Claude/gateway settings determine which is used.
> - `HOST_HOME` is used by `setup.sh` to create symlinks for host-style absolute paths.

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
    # Remote MCP server domains extracted from Claude MCP config files
    # (sse/http/streamable types only; stdio servers don't need network access).
    # Scanned from: ~/.claude.json, ~/.claude/.mcp.json, ~/.claude/mcp.json, project .mcp.json
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

# Symlink host .claude.json path so global MCP/user config resolves in-container.
# Claude plugins may reference the host-absolute path (e.g., /Users/alice/.claude.json).
# The bind mount lands at /home/node/.claude.json, so create a symlink at the host
# path inside the container so those references resolve.  Requires sudo because
# the host home prefix (e.g., /Users) doesn't exist in-container — the Dockerfile
# grants node NOPASSWD:ALL for this purpose.
HOST_CLAUDE_STATE="${HOST_HOME:-}/.claude.json"
if [ -n "${HOST_HOME:-}" ] && [ "$HOST_CLAUDE_STATE" != "/home/node/.claude.json" ]; then
  sudo mkdir -p "$(dirname "$HOST_CLAUDE_STATE")"
  sudo ln -sfn /home/node/.claude.json "$HOST_CLAUDE_STATE"
  echo "  Created symlink: $HOST_CLAUDE_STATE -> /home/node/.claude.json"
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
# Usage: ./devcontainer-ssh.sh [--claude] [--sync] [--doctor|--auth-check] [--down] [--status] [--rebuild]
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

show_auth_preflight() {
  local container
  container=$(get_container_name)
  if [ -z "$container" ]; then
    echo "  ERROR: Container not running. Start it first."
    return 1
  fi

  echo "==> Claude auth preflight (host)"
  if [ -f "$HOME/.claude.json" ]; then
    echo "  present: $HOME/.claude.json"
  else
    echo "  missing: $HOME/.claude.json"
  fi
  if [ -n "${ANTHROPIC_AUTH_TOKEN:-}" ]; then
    echo "  ANTHROPIC_AUTH_TOKEN: set"
  else
    echo "  ANTHROPIC_AUTH_TOKEN: unset"
  fi
  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    echo "  ANTHROPIC_API_KEY: set"
  else
    echo "  ANTHROPIC_API_KEY: unset"
  fi

  echo "==> Claude auth preflight (container)"
  devpod ssh "$PROJECT_NAME" --command "bash -lc 'set -euo pipefail; \
    echo \"  HOME=\$HOME\"; \
    if [ \"\$HOME\" != \"/home/node\" ]; then echo \"  WARNING: HOME is \$HOME (expected /home/node).\"; fi; \
    for f in /home/node/.claude/settings.json /home/node/.claude/.credentials.json /home/node/.claude.json; do \
      if [ -f \"\$f\" ]; then echo \"  present: \$f\"; else echo \"  missing: \$f\"; fi; \
    done; \
    for v in ANTHROPIC_AUTH_TOKEN ANTHROPIC_API_KEY ANTHROPIC_BEDROCK_BASE_URL CLAUDE_CODE_USE_BEDROCK CLAUDE_CODE_SKIP_BEDROCK_AUTH NODE_USE_SYSTEM_CA; do \
      if [ -n \"\${!v:-}\" ]; then echo \"  \$v=set\"; else echo \"  \$v=unset\"; fi; \
    done; \
    echo \"\"; \
    echo \"  claude auth status:\"; \
    claude auth status --text || true; \
    echo \"\"; \
    echo \"  MCP server status:\"; \
    mcp_out=\$(claude mcp list 2>&1 || true); \
    echo \"\$mcp_out\"; \
    if echo \"\$mcp_out\" | grep -q \"No MCP servers configured\"; then \
      echo \"  WARNING: No MCP servers configured in-container. Ensure ~/.claude.json is bind-mounted.\"; \
    fi'"

  if [ -z "${ANTHROPIC_AUTH_TOKEN:-}" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo ""
    echo "  WARNING: Neither ANTHROPIC_AUTH_TOKEN nor ANTHROPIC_API_KEY is set on host."
    echo "  Claude may prompt for authentication."
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
    show_auth_preflight
    echo "==> Launching Claude Code..."
    claude_cmd="cd /home/node/workspace && claude --dangerously-skip-permissions"
    # Auth env is injected by devcontainer.json containerEnv/remoteEnv.
    # Avoid exporting secrets in this command string.
    devpod ssh "$PROJECT_NAME" --command "$claude_cmd"
    ;;

  --sync)
    ensure_running
    sync_claude_config
    ;;

  --doctor|--auth-check)
    ensure_running
    sync_claude_config
    show_auth_preflight
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
    echo "  --sync      Verify Claude bind mounts"
    echo "  --doctor    Run auth + MCP preflight checks"
    echo "  --auth-check Alias for --doctor"
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
  devcontainer:ssh:
    desc: SSH into running devcontainer (starts it if needed)
    cmds:
      - bash devcontainer-ssh.sh

  devcontainer:claude:
    desc: Start devcontainer and launch Claude Code
    cmds:
      - bash devcontainer-ssh.sh --claude

  devcontainer:sync:
    desc: Verify Claude config bind mounts
    cmds:
      - bash devcontainer-ssh.sh --sync

  devcontainer:doctor:
    desc: Run Claude auth + MCP preflight checks
    cmds:
      - bash devcontainer-ssh.sh --doctor

  devcontainer:auth-check:
    desc: Alias for devcontainer:doctor
    cmds:
      - task: devcontainer:doctor

  devcontainer:down:
    desc: Stop the devcontainer
    cmds:
      - bash devcontainer-ssh.sh --down

  devcontainer:status:
    desc: Show devcontainer status
    cmds:
      - bash devcontainer-ssh.sh --status

  devcontainer:rebuild:
    desc: Rebuild devcontainer from scratch
    cmds:
      - bash devcontainer-ssh.sh --rebuild
```
