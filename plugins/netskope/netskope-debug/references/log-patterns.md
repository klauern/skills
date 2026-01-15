# Netskope Log Patterns Reference

## Log File Location
- **Live logs**: `/Library/Logs/Netskope/nsdebuglog.log`
- **Rotated logs**: `/Library/Logs/Netskope/nsdebuglog.1.log`

## Event Categories

### Blocking Events
Traffic that Netskope actively blocks:

```bash
# UDP connections blocked (common for QUIC/HTTP3)
grep "BypassAppMgr Blocking UDP connection" /Library/Logs/Netskope/nsdebuglog.log

# Pattern: BypassAppMgr Blocking UDP connection from process: <app>, dest IP:<ip>:<port>, src IP <ip>:<port>
```

### Bypass Events
Traffic that bypasses Netskope inspection:

```bash
# Bypassed due to exception host
grep "bypassing flow to exception host" /Library/Logs/Netskope/nsdebuglog.log

# Bypassed connection (cert-pinned or exception)
grep "BypassAppMgr Bypassing connection from process" /Library/Logs/Netskope/nsdebuglog.log

# Bypassed due to private IP exception
grep "Bypassing flow from process.*to private ip" /Library/Logs/Netskope/nsdebuglog.log
```

### Exception Matches
When traffic matches an exception rule:

```bash
# IP found in exception list
grep "ExceptiontMgr IP.*is found in IP address range Exception List" /Library/Logs/Netskope/nsdebuglog.log
```

### Tunneled Traffic
Traffic routed through Netskope proxy:

```bash
# Successfully tunneled connections
grep "Tunneling flow from addr" /Library/Logs/Netskope/nsdebuglog.log

# Pattern: Tunneling flow from addr: <addr>, process: <app> to host: <host>, addr: <ip>:<port> to nsProxy
```

### Connection Errors
Failed connections or flow issues:

```bash
# Flow errors
grep "error.*flow" /Library/Logs/Netskope/nsdebuglog.log

# SSL/TLS issues
grep -i "ssl\|tls\|certificate" /Library/Logs/Netskope/nsdebuglog.log
```

## Useful Compound Queries

### Find all activity for a specific app
```bash
APP="chrome"
grep -i "$APP" /Library/Logs/Netskope/nsdebuglog.log | tail -50
```

### Find all activity for a specific domain
```bash
DOMAIN="google.com"
grep -i "$DOMAIN" /Library/Logs/Netskope/nsdebuglog.log | tail -50
```

### Find all activity for a specific IP
```bash
IP="142.251"
grep "$IP" /Library/Logs/Netskope/nsdebuglog.log | tail -50
```

### Summary of recent blocking events
```bash
grep -i "Blocking" /Library/Logs/Netskope/nsdebuglog.log | \
  sed 's/.*process: \([^,]*\).*/\1/' | \
  sort | uniq -c | sort -rn | head -10
```

### Summary of recent bypassed hosts
```bash
grep "bypassing flow to exception host" /Library/Logs/Netskope/nsdebuglog.log | \
  sed 's/.*host: \([^,]*\).*/\1/' | \
  sort | uniq -c | sort -rn | head -10
```

## Log Timestamp Format
```
YYYY/MM/DD HH:MM:SS.microseconds component pid tid level file:line function message
```

Example:
```
2026/01/15 16:17:14.932647 stAgentNE p18280 t31163 info bypassAppMgr.cpp:1634 BypassAppMgr bypassing flow...
```
