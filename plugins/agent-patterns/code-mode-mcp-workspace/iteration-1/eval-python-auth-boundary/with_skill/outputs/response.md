# Code Mode MCP: Python Sandbox Runtime and OAuth Token Hygiene

## Sandbox Runtime Recommendation for Python Harnesses

For a Python agent harness implementing Code Mode MCP, the recommended path depends on your isolation requirements:

### Default Path: FastMCP's Built-in CodeMode Transform

FastMCP ships a `CodeMode` transform with a `MontySandboxProvider`. This is the **fastest path to a working implementation** — you get a pre-wired sandbox, schema-to-typed-API codegen, and the `execute(code)` tool with minimal setup.

```python
from fastmcp import FastMCP
from fastmcp.transforms import CodeMode

mcp = FastMCP("my-server")
# ... register your tools ...

# Wrap with CodeMode — exposes codemode_search and codemode_execute instead
app = CodeMode(mcp)
```

**Tradeoff**: MontySandboxProvider uses AST restrictions (RestrictedPython or similar) — in-process, mid-strength isolation. Adequate for many use cases, but the sandbox runs in your Python process.

### Stronger Isolation: E2B

If your threat model requires stronger isolation (untrusted model-generated code, multi-tenant deployments, or compliance requirements), swap to **E2B**:

- E2B uses Firecracker microVMs under the hood — hardware VM-level isolation
- ~300ms startup latency over a network hop, but model inference is already measured in seconds, so the overhead is imperceptible in practice
- No-ops your sandbox infrastructure concern entirely: E2B operates and patches the sandbox

```python
# FastMCP + E2B sandbox provider
from fastmcp.transforms import CodeMode
from fastmcp.sandboxes import E2BSandboxProvider

app = CodeMode(mcp, sandbox_provider=E2BSandboxProvider(api_key=...))
```

### Full Comparison (Python-relevant runtimes)

| Runtime | Startup | Isolation | Best for |
|---------|---------|-----------|----------|
| RestrictedPython / pyodide | ~10–50 ms | AST restrictions (mid) | FastMCP built-in; Python-native harnesses |
| E2B (Firecracker microVM) | ~300 ms (network) | Hardware VM, very strong | When you don't want to operate a sandbox; stronger isolation needed |
| Remote sandbox (Modal) | ~300 ms (network) | Provider-managed | Similar to E2B; alternative vendor |

---

## Preventing OAuth Tokens from Leaking into the Sandbox

This is implementation item **R.04** — the single biggest security win of Code Mode over "agent runs CLI" patterns. The rule is absolute:

> **The sandbox must never see OAuth tokens, API keys, or refresh tokens. Ever.**

### The Mechanism: Pre-Authorized Client Objects

The sandbox receives pre-authorized *client objects* — structs or instances that hold credentials in their instance state and expose only the safe methods. The credentials are never serialized into the sandbox environment.

**How it works:**

1. **At startup**: Your harness authenticates against each MCP server and holds live, authenticated client objects in host memory.

2. **At sandbox build time**: The generated API stubs (the typed functions the model writes against) are *shims* — they have no credentials. When called, they serialize their arguments and invoke your host-side RPC bridge.

3. **The RPC bridge** (R.03) receives the call, looks up the right pre-authenticated client, dispatches to the MCP server with credentials attached, and returns the result to the sandbox as a plain value.

**What the sandbox sees:**
```python
# Inside the sandbox — model-generated code
result = gdrive.get_document(id="abc123")
print(result["content"][:500])
```

**What the sandbox does NOT see:**
- No `GOOGLE_OAUTH_TOKEN` env var
- No `Authorization: Bearer ...` header construction
- No token refresh logic
- No credential files or secrets

### Python Implementation Pattern

```python
# host_bridge.py — runs OUTSIDE the sandbox

class GDriveBinding:
    """Pre-authorized binding. Credentials live here, never serialized."""
    def __init__(self, oauth_token: str):
        self._client = GoogleDriveClient(token=oauth_token)  # private

    def get_document(self, id: str) -> dict:
        return self._client.files().get(fileId=id).execute()

# sandbox_runner.py — sets up the restricted environment
def build_sandbox_namespace(bindings: dict) -> dict:
    """Expose method handles to sandbox, not credentials."""
    return {
        "gdrive": {
            "get_document": bindings["gdrive"].get_document,
            # Never pass the binding object itself — only named method references
        }
    }
```

**Critical rules for the sandbox environment setup:**
- Do NOT pass `os.environ` into the sandbox
- Do NOT pass `**kwargs` or `**env` that might contain tokens
- Do NOT serialize binding objects in any format (exposes instance state with credentials)
- Expose only named method references, not the parent objects

### Why This Matters More Than the Sandbox Itself

A sandbox prevents *escape* — it doesn't prevent *authorized harm*. If the sandbox has a binding to `salesforce.delete_record`, a prompt-injected model that calls it will succeed — the runtime did its job. Credentials never entering the sandbox is defense against a different threat: a compromised or exfiltrated sandbox image containing live tokens.

Treat every binding as a privilege grant:
- Scope OAuth tokens at auth time (read-only scopes where write isn't needed)
- Allowlist destructive operations per-role before wiring them as bindings
- Sandboxing is defense-in-depth, not the credential perimeter

---

## Quick Decision Summary

| Question | Answer |
|----------|--------|
| What sandbox should I use? | FastMCP's built-in `CodeMode` transform (MontySandboxProvider) for fastest path; E2B for stronger isolation |
| Where do OAuth tokens live? | Host-side only, in pre-authorized client objects with private credential state |
| What enters the sandbox? | Method references (shims), never credentials, env vars, or token strings |
| What's the escape hatch? | RPC bridge from sandbox shim to host dispatcher to MCP server (credentials attached at host) |
| When does data leak to the model? | Only what the snippet explicitly `print()`s — large payloads stay inside the sandbox |

---

## References

- Anthropic Engineering. *Code execution with MCP: building more efficient AI agents.* Nov 2025. https://www.anthropic.com/engineering/code-execution-with-mcp
- Cloudflare. *Code Mode: the better way to use MCP.* Sept 2025. https://blog.cloudflare.com/code-mode/
- Cloudflare. *Code Mode: give agents an entire API in 1,000 tokens.* Feb 2026. https://blog.cloudflare.com/code-mode-mcp/
- FastMCP. *Code Mode transform.* https://gofastmcp.com/servers/transforms/code-mode
- Modal. *Best Code Execution Sandboxes for MCP Servers in 2026.* https://modal.com/resources/best-code-execution-sandboxes-mcp-servers
