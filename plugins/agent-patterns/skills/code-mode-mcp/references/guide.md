# Code Mode MCP — Full Reference Guide

Source: [Anthropic Engineering Blog (Nov 2025)](https://www.anthropic.com/engineering/code-execution-with-mcp),
[Cloudflare Blog (Sept 2025)](https://blog.cloudflare.com/code-mode/),
[Cloudflare Blog (Feb 2026)](https://blog.cloudflare.com/code-mode-mcp/)

---

## The Problem

Classic MCP exposes every tool directly to the LLM. Each definition lands in the context
window before the user has spoken. Each intermediate result round-trips through the model.

Two failure modes at scale:
- **Definition overload**: A 4-server gateway can expose 52 tools consuming ~9,400 tokens
  of context before any work happens. Cloudflare's full API surface: 1.17M tokens as raw
  tool definitions.
- **Payload round-tripping**: Fetch a long document from Drive, write it to Salesforce.
  The transcript returns to the model, then gets sent back out as a tool argument. The
  model is acting as a copy buffer for data it never needed to read.

> Making an LLM perform tasks with tool calling is like putting Shakespeare through a
> month-long class in Mandarin and then asking him to write a play in it.
> — Kenton Varda & Sunil Pai, Cloudflare

Models have seen millions of lines of real TypeScript/Python. They've seen a comparatively
small, contrived set of tool-call JSON. Writing code uses their strongest muscle.

---

## The Mechanism (5 steps)

1. **Introspect MCP schemas at startup** — connect to each server, pull `tools/list`.
   Schemas are JSON Schema; descriptions become doc comments.

2. **Emit a typed code header** — each tool becomes a function on a generated namespace,
   e.g. `codemode.gdrive.getDocument({ id })`, typed with input/output schemas.

3. **Expose one tool to the model: `execute(code)`** — the generated header loads into
   the system prompt (or referenced via discovery). The model writes a code snippet.

4. **Run the snippet in a sandbox with bound clients** — no internet, no filesystem,
   no env vars. Only escape hatch: pre-authorized RPC bindings back to your harness,
   which dispatches to the right MCP server.

5. **Return only what the script logs** — large intermediate payloads (transcripts,
   paginated lists, file contents) stay inside the sandbox. The model sees only the
   `console.log` tail. Token cost stays flat.

---

## Worked Example: Drive Transcript → Salesforce Record

The transcript is ~25,000 tokens. In classic mode it crosses the model boundary twice.
In Code Mode it never does.

### Before — classic tool calling (~150K tokens, 2 round-trips)

```
// All 19 tool definitions load into context (~12K tokens)
// Model emits:
tool_call gdrive.getDocument({ id: "abc123" })
// → returns 25K-token transcript INTO model context

// Model emits next call with the transcript as argument:
tool_call salesforce.updateRecord({
  recordId: "00Q5f000001abcXYZ",
  data: { Notes: "<25K tokens of transcript>" }
})
```

### After — Code Mode (~2K tokens, 1 call)

```typescript
import * as gdrive from "./servers/google-drive";
import * as sfdc   from "./servers/salesforce";

const doc = await gdrive.getDocument({ id: "abc123" });

await sfdc.updateRecord({
  recordId: "00Q5f000001abcXYZ",
  data: { Notes: doc.content }   // 25K tokens — never leaves sandbox
});

console.log("updated");   // ← this is all the model sees
```

The wins compound when the snippet branches, filters, paginates, or chains across
multiple servers. Each of those operations would be a separate model round-trip in
classic mode.

---

## Sandbox Runtimes — Full Comparison

| Runtime | Startup | Host lang | Sandbox lang | Isolation | When it fits |
|---------|---------|-----------|--------------|-----------|--------------|
| `wasmtime` / `wazero` | ~1 ms | Rust, Go (no CGO for wazero) | WASM (any compiled lang) | Capability-based, very strong | Best general-purpose vendor-neutral option |
| `goja` | < 1 ms | Go | JS / TS (ES5+) | In-process, language-level | Pure-Go JS. Highest LLM fluency. Trades isolation for embedding simplicity. |
| `starlark-go` | < 1 ms | Go | Starlark (Python-ish) | No I/O by design, very strong | Trivially safe to embed. Lower LLM fluency. |
| RestrictedPython / pyodide | ~10–50 ms | Python | Python (subset) | AST restrictions (mid) | Python-native harnesses (FastMCP). RestrictedPython: in-process; pyodide: WASM. |
| Firecracker / microVM | ~125 ms | any | any | Hardware VM, very strong | Lambda-grade isolation. Mature. Used by E2B, Modal under the hood. |
| V8 isolates | ~5 ms | JS/TS (Node, Deno, Bun, CF) | JS / TS | Process boundary within V8 | Cloudflare reference. Elsewhere: `isolated-vm` (Node). |
| Hyperlight | < 10 ms | Rust | WASM | Hardware micro-VM | Microsoft open-source. Strong isolation/startup ratio. Newer. |
| Container (Docker, gVisor) | ~200 ms+ | any | any | Kernel namespaces | Daytona, Modal. Maximum runtime flexibility. |
| Remote sandbox (E2B, Modal) | ~300 ms+ over network | any (HTTP client) | Python, TS, others | Provider-managed | When you don't want to operate the sandbox at all. Network hop per call. |

**For a Go harness:**
- Max fluency path: `goja` (in-process JS, shares your process)
- Max isolation path: `wazero` (pure-Go, no CGO) running a JS or Python WASM build
- Lowest effort, highest model-error rate: `starlark-go`

**For a Python harness:** FastMCP's `CodeMode` transform with MontySandboxProvider is the
fastest path. Swap to E2B if you need stronger isolation than in-process AST restrictions.

---

## Go Implementation Table (vendor-neutral)

| Primitive | Cloudflare's choice | Go-native alternative | Trade |
|-----------|--------------------|-----------------------|-------|
| Sandbox | V8 isolate via Worker Loader | wazero + JS/Python WASM build, or starlark-go, or goja | wazero: strongest isolation. starlark-go: trivially safe. goja: high fluency, weakest isolation. |
| Code language | TypeScript | TypeScript (via goja or wazero+QuickJS), Python, or Starlark | TS/Python have the most LLM training data. |
| Bindings | `env` live objects | Go struct methods exposed via the interpreter's host-binding API | Same capability model, different syntax. |
| Outbound control | `globalOutbound = null` | Don't expose `net/http` or `os` to the sandbox at all | In language-level sandboxes, you control the API surface directly. |
| Schema codegen | Built-in `.d.ts` emitter | Roll your own from `tools/list`, or use `quicktype` / `datamodel-code-generator` | JSON Schema → typed declarations is solved in every language. |
| Disposable per-call | 5ms V8 isolate | Pooled wazero instances with idle eviction; accept ~50ms cold start | Model inference is seconds. Sandbox startup almost never matters. |
| Remote sandbox | — | E2B, Modal, Daytona over HTTP | When you don't want to operate the sandbox at all. |

---

## Three Deployment Shapes

### Client-side (harness owns sandbox)
Your agent loop fetches MCP schemas, generates the typed API, runs snippets. Connected
MCP servers are unmodified — they don't know they're being used this way.
- **Cost**: you operate a code-execution runtime
- **Win**: works with any compliant MCP server today
- **Examples**: Cloudflare Agents SDK; Anthropic's filesystem variant; any custom harness

### Server-side (MCP server or gateway owns sandbox)
The MCP server (or a portal in front of many servers) exposes just two tools:
`codemode_search` and `codemode_execute`. Any MCP-compliant client gets Code Mode for free.
- **Cost**: the server operator runs the sandbox
- **Win**: no harness changes needed
- **Examples**: Cloudflare MCP Portal; FastMCP's `CodeMode` transform

### Filesystem-mounted discovery
Tools are mounted as files in a sandbox filesystem
(`./servers/google-drive/getDocument.ts`). The agent discovers what's available via
directory listing and reading files — loading definitions on demand instead of upfront.
This is what drives the 150K → 2K result. Composes with either deployment shape above.

---

## What Cloudflare Has That's Hard to Replicate

**Genuinely Workers-only:**
1. ~5ms isolate startup (V8 isolates via Worker Loader API)
2. Worker Loader API — beta CF-specific binding that dynamically spawns child Workers
3. Bindings as a first-class platform primitive — live JS objects in the `env` object

**How to get equivalent properties elsewhere:**
1. Don't aim for 5ms — aim for "imperceptible relative to model inference." Pooled
   microVM, recycled container, or in-process interpreter all work.
2. Use an embedded interpreter instead of dynamic Worker loading: `wasmtime`, `goja`,
   `quickjs`, `pyodide`, `starlark-go`.
3. Capability bindings are a coding pattern: define a struct/object that holds the OAuth
   token in instance state and exposes only the safe methods. Pass it into the sandbox.
   Never serialize the credential.

---

## The Eight Implementation Items (expanded)

**R.01 — Schema-to-typed-API codegen**
Walk every connected MCP server's `tools/list`. Translate JSON Schema into your sandbox
language's type system. Preserve descriptions as doc comments — they are how the model
navigates the API.
Output: one declaration file per server, or a flat namespace.

**R.02 — Sandbox runtime**
You need somewhere to run untrusted, model-generated code with no network, no filesystem,
no environment, and a hard timeout. Hard requirement: capability-based access only.

**R.03 — RPC bridge from sandbox back to host**
Generated functions in the sandbox are shims. They serialize their arguments, call out to
the host harness, and the host dispatches to the right MCP server with the right auth
attached. Results return as serialized values.

**R.04 — Auth boundary on the host, never in the sandbox**
The sandbox sees pre-authorized client objects. It never sees OAuth tokens, API keys, or
refresh tokens. This is the single biggest security win of Code Mode over
"agent runs CLI" patterns.

**R.05 — Resource limits and timeout**
30 seconds is typical. Cap memory, CPU, output buffer size (the model gets confused by
100K-line logs). Kill on overrun; return the partial log and an error marker.

**R.06 — Output capture and shaping**
Return whatever the snippet wrote to stdout. Truncate to a sensible window. Surface
uncaught exceptions as model-readable errors with stack traces — the model is good at
fixing TS errors when it can see them.

**R.07 — Progressive disclosure**
For very large API surfaces, load only a short index of servers/tools into context. Give
the model a `search()` meta-tool callable from inside snippets to pull specific schemas on
demand. Cloudflare keeps 2,500 endpoints under 1K tokens this way.

**R.08 — Audit log of every snippet**
Log every execution with: source code, the MCP calls it made, results, and runtime.
Treat snippets like IaC change plans — reviewable artifacts, not opaque tool calls.

---

## Tradeoffs

**What you gain:**
- Flat token cost (adding the 50th MCP server doesn't widen your context budget)
- Stronger LLM performance on large, complex APIs
- Native composition (filter, paginate, branch, retry — in one snippet)
- Credential hygiene (tokens live on the host)
- Data segregation (large payloads never enter prompt logs)

**What you pay:**
- Sandbox infrastructure (real ops surface — patching, monitoring, escape detection)
- Approval UX collapses (approving 15 lines of TypeScript, not a named tool call)
- Harder debugging (trace through generated code with generated bindings)
- Per-call overhead (for one-shot calls, spinning a sandbox is more expensive than one tool call)

---

## Primary Sources

- Cloudflare. *Code Mode: the better way to use MCP.* Sept 2025. https://blog.cloudflare.com/code-mode/
- Anthropic Engineering. *Code execution with MCP: building more efficient AI agents.* Nov 2025. https://www.anthropic.com/engineering/code-execution-with-mcp
- Cloudflare. *Code Mode: give agents an entire API in 1,000 tokens.* Feb 2026. https://blog.cloudflare.com/code-mode-mcp/
- FastMCP. *Code Mode transform.* https://gofastmcp.com/servers/transforms/code-mode
- Modal. *Best Code Execution Sandboxes for MCP Servers in 2026.* https://modal.com/resources/best-code-execution-sandboxes-mcp-servers
