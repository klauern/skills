---
allowed-tools: Bash, Read, Grep
description: Debug Netskope blocking events, exceptions, and cert-pinned app issues
---

# Netskope Debug

Diagnose why applications are being blocked or bypassed by the Netskope client.

## Quick Start

1. Export fresh logs and analyze:
   ```bash
   "/Library/Application Support/Netskope/STAgent/nsdiag" -o ~/Downloads/nslogs.zip
   unzip -o ~/Downloads/nslogs.zip -d ~/Downloads/nslogs_extracted
   ```

2. Check for blocking events in the last 100 lines:
   ```bash
   grep -i "Blocking" /Library/Logs/Netskope/nsdebuglog.log | tail -20
   ```

3. View exception rules:
   ```bash
   cat ~/Downloads/nslogs_extracted/nsexception.json | jq '.names[:20]'
   ```

4. View cert-pinned apps:
   ```bash
   cat ~/Downloads/nslogs_extracted/nsbypass.json | jq '.certPinnedAppList | .[].appName' | sort -u
   ```

## Usage

If the user provides an app name or domain, search for related events:
- Search logs for the process/app name
- Check if it's in the cert-pinned apps list
- Check if the destination is in exceptions

See @netskope-debug/SKILL.md for detailed diagnostic workflows.
