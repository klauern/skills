# Netskope Troubleshooting Guide

## Common Issues and Solutions

### 1. Application Can't Connect (SSL/Certificate Errors)

**Symptoms:**
- App shows "certificate error" or "SSL handshake failed"
- Browser shows security warnings for specific sites
- App works on other networks but not corporate

**Diagnosis:**
```bash
# Check if app is cert-pinned (should bypass inspection)
cat ~/Downloads/nslogs_extracted/nsbypass.json | jq '.certPinnedAppList[] | select(.appName | test("APPNAME"; "i"))'

# Check if traffic is being tunneled (should NOT be for cert-pinned apps)
grep -i "Tunneling.*APPNAME" /Library/Logs/Netskope/nsdebuglog.log | tail -5
```

**Solution:**
- If app is cert-pinned but traffic is tunneled, there may be a process name mismatch
- Check the exact process name in logs vs. bypass config
- Contact IT to add the app to cert-pinned list if missing

---

### 2. UDP/QUIC Traffic Blocked

**Symptoms:**
- Slow video streaming (YouTube, Netflix)
- Slow Google services
- Apps falling back to TCP

**Diagnosis:**
```bash
# Check for UDP blocking
grep "Blocking UDP connection" /Library/Logs/Netskope/nsdebuglog.log | tail -20
```

**Explanation:**
- Netskope blocks QUIC (UDP/443) by default to force TCP inspection
- This is expected behavior, not a bug
- Apps should fall back to HTTPS/TCP automatically

---

### 3. Internal/Private IPs Being Inspected

**Symptoms:**
- Local network resources slow or inaccessible
- VPN tunnel traffic being intercepted

**Diagnosis:**
```bash
# Check private IP exceptions
cat ~/Downloads/nslogs_extracted/nsexception.json | jq '.ips[] | select(.type | contains("local"))'

# Check if specific IP is being bypassed
grep "Bypassing.*PRIVATEIP" /Library/Logs/Netskope/nsdebuglog.log | tail -5
```

**Solution:**
- Private ranges (10.x, 172.16-31.x, 192.168.x) should be in exceptions
- If missing, contact IT to add to exception list

---

### 4. Specific Domain Not Working

**Diagnosis:**
```bash
# Check if domain is in exception list
cat ~/Downloads/nslogs_extracted/nsexception.json | jq '.names[] | select(. | test("DOMAIN"; "i"))'

# Check what's happening to traffic for that domain
grep -i "DOMAIN" /Library/Logs/Netskope/nsdebuglog.log | tail -20
```

**Solution:**
- If domain needs to bypass inspection, contact IT to add exception
- If domain is blocked by policy, this is intentional

---

### 5. Checking Client Status

```bash
# Get Netskope client version
"/Library/Application Support/Netskope/STAgent/nsdiag" -v

# Get NPA (Private Access) status
"/Library/Application Support/Netskope/STAgent/nsdiag" -n

# Check current client status
"/Library/Application Support/Netskope/STAgent/nsdiag" -f
```

---

## Quick Reference: JSON Query Examples

### List all cert-pinned app names
```bash
cat ~/Downloads/nslogs_extracted/nsbypass.json | jq -r '.certPinnedAppList[].appName' | sort -u
```

### List all domain exceptions
```bash
cat ~/Downloads/nslogs_extracted/nsexception.json | jq -r '.names[]' | sort
```

### List all IP range exceptions
```bash
cat ~/Downloads/nslogs_extracted/nsexception.json | jq -r '.ips[] | "\(.type): \(.value)"'
```

### Find bypass config for specific app
```bash
cat ~/Downloads/nslogs_extracted/nsbypass.json | jq '.certPinnedAppList[] | select(.processName | test("PROCESSNAME"; "i"))'
```

### Check steering config name
```bash
cat ~/Downloads/nslogs_extracted/nsexception.json | jq '.steering_config_name'
```
