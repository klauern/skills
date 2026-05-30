# Code Mode MCP in a Python Agent Harness: Sandbox Runtime & OAuth Token Security

## Overview

When implementing Code Mode MCP (Model Context Protocol with code execution capabilities) in a Python agent harness, you face two intertwined challenges:

1. **Choosing a sandbox runtime** that safely executes untrusted or agent-generated code
2. **Preventing OAuth tokens and other secrets from leaking into the sandbox**

This guide covers both concerns with practical recommendations.

---

## 1. Sandbox Runtime Options

### Recommended: Docker-based Isolation (Production Default)

Docker containers with restricted capabilities are the most practical production choice for Python agent harnesses:

```python
import docker

client = docker.from_env()
container = client.containers.run(
    "python:3.12-slim",
    command=["python", "-c", user_code],
    detach=True,
    network_disabled=True,          # No network access
    read_only=True,                 # Immutable filesystem (mount /tmp separately)
    mem_limit="256m",
    cpu_period=100000,
    cpu_quota=50000,                # 50% of one CPU
    security_opt=["no-new-privileges"],
    cap_drop=["ALL"],               # Drop all Linux capabilities
    user="nobody",
    remove=True,
    environment={},                 # Explicit: pass nothing from host env
)
```

**Pros**: Strong isolation, widely available, supports resource limits, mature ecosystem.
**Cons**: Requires Docker daemon, not feasible inside containers-without-DinD, cold start latency (~200ms+).

---

### Alternative: gVisor (runsc) - Defense in Depth

gVisor intercepts syscalls in user space, providing a second layer under Docker:

```bash
# Configure Docker to use gVisor runtime
docker run --runtime=runsc ...
```

Use gVisor when your threat model includes malicious code exploiting kernel vulnerabilities. It adds latency but significantly reduces the kernel attack surface.

---

### Alternative: Firecracker MicroVMs

For maximum isolation with sub-second cold starts (~125ms), Firecracker provides full VM-level isolation:

- Used by AWS Lambda and Fly.io internally
- Each code execution gets a fresh microVM
- Best for multi-tenant SaaS scenarios

Python SDK: `firecracker-python-sdk` or drive via REST API.
**Cons**: Complex infrastructure, requires KVM.

---

### Alternative: WebAssembly (Wasm) via Pyodide or Wasmtime

Wasm sandboxes provide language-level isolation without OS-level VMs:

```python
# Using wasmtime-py for running compiled code
from wasmtime import Store, Module, Instance
store = Store()
module = Module.from_file(store.engine, "sandbox.wasm")
```

For Python specifically, **Pyodide** (CPython compiled to Wasm) runs in a Wasm sandbox and is useful for browser-side or restricted environments.

**Pros**: No OS-level privileges needed, portable, no Docker required.
**Cons**: Limited stdlib support, no C extensions, slower startup for heavy workloads, limited Python ecosystem compatibility.

---

### Lightweight Option: RestrictedPython

For lower-stakes use cases where you control code quality:

```python
from RestrictedPython import compile_restricted, safe_globals

byte_code = compile_restricted(user_code, '<string>', 'exec')
exec(byte_code, safe_globals)
```

**Warning**: RestrictedPython is NOT a security boundary - it is a policy mechanism. Determined attackers can escape it. Use only for trusted-but-bounded code (e.g., user-defined data transformations where the user is also the operator).

---

### Decision Matrix

| Runtime | Isolation Strength | Cold Start | Complexity | Best For |
|---|---|---|---|---|
| Docker + restricted caps | Strong | ~200ms | Low | Most production cases |
| gVisor (runsc) | Very Strong | ~400ms | Medium | High-security multi-tenant |
| Firecracker MicroVM | Strongest | ~125ms | High | SaaS, per-request VMs |
| Wasm (Pyodide) | Strong (sandboxed) | ~1-5s | Medium | Browser-side or no-Docker |
| RestrictedPython | Weak (policy only) | <1ms | Low | Trusted users only |

**Recommendation for a Python agent harness with MCP**: Use Docker with `cap_drop=ALL`, `network_disabled=True`, and explicit empty `environment={}`. Add gVisor if you need defense-in-depth. Avoid RestrictedPython as your primary boundary.

---

## 2. Preventing OAuth Token Leakage into the Sandbox

This is the more critical concern. OAuth tokens and other credentials can leak through several channels:

### Leak Vectors to Close

1. **Environment variables** - The most common leak; `os.environ` in sandboxed code exposes everything inherited from the host process
2. **Filesystem mounts** - Credential files (`~/.aws/credentials`, `~/.config/gcloud/`, `.env` files) mounted into the container
3. **Network access** - Code calling `169.254.169.254` (AWS IMDS), `metadata.google.internal`, or Azure IMDS to steal ambient cloud credentials
4. **Process inspection** - `/proc/<pid>/environ` of the host process visible inside the container if PID namespace is not isolated
5. **Shared memory / IPC** - Less common but possible in poorly configured containers

---

### Mitigation Strategy

#### A. Strip Environment Completely

Never inherit host environment variables into the sandbox:

```python
# WRONG: inherits host env including tokens
subprocess.run(["python", "-c", code])

# RIGHT: explicit empty environment for Docker
container = client.containers.run(
    "python:3.12-slim",
    command=["python", "-c", code],
    environment={},    # Explicit empty dict - pass NOTHING
)
```

If the sandboxed code needs some runtime values (e.g., a per-request nonce), pass only those explicitly and treat them as public:

```python
safe_env = {
    "EXECUTION_ID": str(uuid.uuid4()),  # Non-secret runtime context only
    # Never: OAUTH_TOKEN, AWS_SECRET_ACCESS_KEY, etc.
}
container = client.containers.run(..., environment=safe_env)
```

#### B. Disable Network Access

Prevents IMDS credential theft and exfiltration:

```python
container = client.containers.run(
    ...,
    network_disabled=True,
    # OR use a network with no external routing:
    network="none",
)
```

If the code legitimately needs network access (e.g., to call an API), proxy it through a controlled sidecar that holds credentials:

```
Agent Harness -> Sandbox (no credentials)
                     |
                     v HTTP to localhost:8080
             Credential Proxy Sidecar
                     |
                     v Authenticated request with real token
             External API
```

The proxy validates what the sandbox is allowed to call and injects credentials itself.

#### C. Mount No Credential Files

```python
# WRONG: mounts home directory which may contain .aws, .ssh, etc.
volumes={"/home/user": {"bind": "/home/user", "mode": "ro"}}

# RIGHT: mount only explicitly prepared scratch directories
volumes={"/tmp/sandbox-workdir": {"bind": "/workspace", "mode": "rw"}}
```

Scan your volume mounts for implicit credential exposure.

#### D. Isolate PID and IPC Namespaces

```python
container = client.containers.run(
    ...,
    pid_mode="",        # Private PID namespace (default for Docker, but be explicit)
    ipc_mode="private", # Isolate shared memory
)
```

This prevents the sandbox from using `/proc` to inspect the host agent process environment.

#### E. Block Cloud Metadata Endpoints (Defense in Depth)

Even with `network_disabled=True`, add firewall rules if you run on cloud VMs to block IMDS from containers:

```bash
# AWS: block IMDS from container network range
iptables -I DOCKER-USER -d 169.254.169.254 -j DROP
```

#### F. Use Short-Lived, Scoped Tokens if You Must Pass Any

If sandboxed code genuinely needs an auth credential:

1. Issue a **short-lived, minimum-scope** token specifically for the sandbox execution
2. Revoke it immediately after the execution completes
3. Log its usage

```python
sandbox_token = oauth_client.create_token(
    scopes=["read:only-needed-resource"],
    expires_in=60,  # seconds
)
try:
    run_sandbox(code, env={"SANDBOX_TOKEN": sandbox_token})
finally:
    oauth_client.revoke(sandbox_token)
```

---

### Architecture Pattern: Credential Boundary Layer

The cleanest architecture separates the agent harness (which holds credentials) from the sandbox (which holds none) with an explicit boundary:

```
+-----------------------------------------------------+
|  Agent Harness Process                               |
|  - Holds OAuth tokens, API keys                      |
|  - Manages MCP tool registry                         |
|  - Orchestrates LLM calls                            |
|                                                      |
|  +----------------------------+                      |
|  |  MCP Tool Executor         |                      |
|  |  - Receives tool calls     |                      |
|  |  - Validates parameters    |                      |
|  |  - Calls real APIs         | <--- credentials     |
|  |  - Returns results only    |      stay here       |
|  +----------------------------+                      |
|             |  result (no tokens)                    |
|             v                                        |
|  +----------------------------+                      |
|  |  Code Sandbox              |                      |
|  |  (Docker/gVisor/Wasm)      |                      |
|  |  - Executes generated code |                      |
|  |  - No env vars             |                      |
|  |  - No credential files     |                      |
|  |  - No network (or proxied) |                      |
|  +----------------------------+                      |
+-----------------------------------------------------+
```

In this model, the sandbox calls back to the harness via a local Unix socket or localhost API - the harness acts as the credential holder and enforces what operations are permitted.

---

## 3. MCP-Specific Considerations

When implementing Code Mode MCP:

- **Tool call results** returned from MCP servers should be sanitized before being passed into the sandbox - a malicious MCP server response could include tokens injected into tool outputs
- **Prompt injection via code output** - Treat stdout/stderr from the sandbox as untrusted user data when feeding back to the LLM; an attacker could craft output that looks like a system prompt
- **Audit the tool schema** - Ensure no MCP tool definition exposes auth endpoints or token-refresh flows that sandboxed code could invoke indirectly
- **Structured output only** - Prefer returning structured data (JSON) from the sandbox rather than raw text to reduce prompt injection surface

---

## Summary Recommendations

| Concern | Recommendation |
|---|---|
| Sandbox runtime | Docker + `cap_drop=ALL` + `network_disabled=True` as baseline |
| High-security multi-tenant | Add gVisor (`--runtime=runsc`) |
| No Docker available | Wasm/Pyodide for Python-in-browser or Wasmtime for compiled code |
| Environment variables | Pass `environment={}` (empty dict) explicitly - never inherit |
| Filesystem | Mount only scratch dirs; never mount home or credential paths |
| Network | Disable by default; proxy through a credential-holding sidecar if needed |
| Cloud credentials | Block IMDS via iptables as defense-in-depth |
| Any token that must enter sandbox | Issue short-lived, minimum-scope, revoke-on-completion |
| MCP tool results | Sanitize before passing to sandbox; treat as untrusted input |
