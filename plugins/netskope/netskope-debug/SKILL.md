---
name: netskope-debug
description: Diagnose Netskope blocking events, bypass rules, and cert-pinned app issues
allowed-tools: Bash, Read, Grep
---

# Netskope Debug Skill

## Overview
This skill helps diagnose why applications or connections are being blocked, bypassed, or tunneled by the Netskope client on macOS.

## When to Use This Skill
- User reports an app not working (SSL errors, connection failures)
- Need to check if traffic is being intercepted by Netskope
- Investigating why certain domains/IPs are bypassed
- Checking certificate pinning bypass rules

## Diagnostic Workflow

### Step 1: Export Fresh Logs
Always start by exporting fresh logs to get decrypted config files:

```bash
"/Library/Application Support/Netskope/STAgent/nsdiag" -o ~/Downloads/nslogs.zip
unzip -o ~/Downloads/nslogs.zip -d ~/Downloads/nslogs_extracted
```

### Step 2: Identify the Issue Type

| Symptom | Check | Command |
|---------|-------|---------|
| App not connecting | Blocking events | `grep -i "Blocking" /Library/Logs/Netskope/nsdebuglog.log \| tail -30` |
| SSL/cert errors | Cert-pinned apps | `jq '.certPinnedAppList[] \| select(.processName \| test("APPNAME"; "i"))' ~/Downloads/nslogs_extracted/nsbypass.json` |
| Traffic bypassed | Exception list | `jq '.names[]' ~/Downloads/nslogs_extracted/nsexception.json \| grep -i "DOMAIN"` |
| Connection tunneled | Tunnel events | `grep "Tunneling.*APPNAME" /Library/Logs/Netskope/nsdebuglog.log \| tail -10` |

### Step 3: Deep Dive Based on Issue

#### For Blocking Events
```bash
# Find all blocking events for an app
grep -i "Blocking.*PROCESSNAME" /Library/Logs/Netskope/nsdebuglog.log | tail -20

# Find blocking by destination IP
grep -i "Blocking.*IPADDRESS" /Library/Logs/Netskope/nsdebuglog.log | tail -20
```

#### For Certificate Pinning Issues
```bash
# List all cert-pinned apps
cat ~/Downloads/nslogs_extracted/nsbypass.json | jq -r '.certPinnedAppList[].appName' | sort -u

# Find specific app's bypass config
cat ~/Downloads/nslogs_extracted/nsbypass.json | jq '.certPinnedAppList[] | select(.appName | test("APPNAME"; "i"))'

# Check if process is being bypassed
grep -i "Bypassing.*PROCESSNAME" /Library/Logs/Netskope/nsdebuglog.log | tail -10
```

#### For Exception/Bypass Rules
```bash
# List domain exceptions
cat ~/Downloads/nslogs_extracted/nsexception.json | jq '.names'

# List IP exceptions
cat ~/Downloads/nslogs_extracted/nsexception.json | jq '.ips'

# Check if domain is in exception list
cat ~/Downloads/nslogs_extracted/nsexception.json | jq '.names[] | select(. | test("DOMAIN"; "i"))'
```

## Key Files Reference

| File | Contents |
|------|----------|
| `/Library/Logs/Netskope/nsdebuglog.log` | Live traffic events (blocking, bypass, tunnel) |
| `nsexception.json` | Domain/IP bypass rules |
| `nsbypass.json` | Cert-pinned application list |
| `nsconfig.json` | Client configuration |
| `nssteering.json` | Traffic steering rules |

## Log Event Patterns

See @references/log-patterns.md for complete list of grep patterns.

## Common Issues & Solutions

See @references/troubleshooting.md for common scenarios.

## Sub-Agent Strategy

| Task | Model |
|------|-------|
| Log parsing | Haiku (fast pattern matching) |
| Config analysis | Sonnet (JSON comprehension) |
| Troubleshooting | Sonnet (reasoning about issues) |
