# Solving the 40K Token Schema Problem in a Go Agent Harness

You're hitting a well-documented failure mode of classic MCP at scale. With 8 servers and 120 tools, you're likely paying around 40K tokens _before your first user message_ — and that number will grow with every server you add. The fix is to stop feeding tool definitions to the model and instead give it code to write.

## The Core Problem

Classic MCP exposes every tool definition directly to the model. With 120 tools across 8 servers, each definition (name + input schema + description) lands in context unconditionally. That's your 40K. And it compounds: every intermediate result from a tool call — a document fetch, a search response, a list of records — also round-trips through the model context, even when the model only needs to pass it to the next call.

You're hitting two failure modes at once:
1. **Definition overload** — 40K tokens of schema before any work happens
2. **Payload round-tripping** — intermediate results crossing the model boundary on every tool call

---

## The Answer: Code Mode MCP

Your situation clears every threshold for adopting Code Mode:

- 8 MCP servers (threshold: 5+)
- 120 tools (threshold: 50+)
- Almost certainly chaining 3+ tool calls in workflows (threshold: 3+)
- Already hitting context-window limits (explicit signal)

**Code Mode replaces the 120-tool surface with one tool: `execute(code)`.**

The model receives a typed API header (generated from your MCP schemas) and writes a code snippet instead of making discrete tool calls. The snippet runs in a sandbox. Large intermediate values — documents, search results, paginated lists — stay inside the sandbox and never enter the model's context. Only `console.log` output returns to the model.

The token math: a 4-server, 52-tool setup that consumes ~9,400 tokens of definitions in classic mode collapses to ~2K in Code Mode. Your 40K load could realistically drop to 1–3K.

---

## What to Build (Go Harness Implementation Order)

Walk these eight items in order — each one has a trust implication:

### R.01 — Schema-to-Typed-API Codegen

At startup, connect to each MCP server and call `tools/list`. Translate the JSON Schema definitions into typed declarations in your sandbox language. **Critically: preserve descriptions as doc comments** — these are how the model navigates the API. Without them, the model is guessing at argument semantics.

Output: one declaration file per server (e.g., `./servers/google-drive.d.ts`, `./servers/salesforce.d.ts`), or a flat merged namespace.

### R.02 — Sandbox Runtime

You need a place to run untrusted model-generated code with no network access, no filesystem, no environment variables, and a hard timeout. For a Go harness, your three practical options:

| Option | Isolation | Startup | LLM Fluency | Notes |
|--------|-----------|---------|-------------|-------|
| `goja` | In-process (language-level) | < 1ms | High (JS/TS) | Fastest path; shares your Go process |
| `wazero` | WASM capability-based | ~1ms | High (JS/Python via WASM) | Pure Go, no CGO; stronger isolation |
| `starlark-go` | No I/O by design | < 1ms | Lower | Trivially safe but models are less fluent in Starlark |

**Recommendation: start with `goja`.** It's the fastest path to a working prototype, and JS/TS has far more LLM training data than Starlark. Migrate to `wazero` later if isolation becomes a compliance concern.

The sandbox language choice is the highest-impact lever you control. TypeScript and Python have millions of lines of training data; Starlark has comparatively little.

### R.03 — RPC Bridge (Sandbox → Host)

The typed functions inside the sandbox are shims. When the model calls `gdrive.getDocument({ id: "abc123" })`, that shim serializes the arguments and calls back to your Go host process. The host dispatches to the right MCP server — with authentication already attached — and returns the result.

This bridge is what allows large intermediate payloads to stay inside the sandbox: the host dispatches the MCP call, the result comes back into the sandbox, and the model never sees it unless the snippet explicitly logs it.

### R.04 — Auth Boundary on the Host (Critical)

**The sandbox must never receive OAuth tokens, API keys, or refresh tokens.** Pass pre-authorized client objects into the sandbox instead. The model gets a binding like `codemode.gdrive` that already knows how to make authenticated calls — it can't extract the credential from it.

This is the single biggest security win over "agent executes CLI" patterns. Treat every binding you expose as a privilege grant.

### R.05 — Resource Limits and Timeout

Set a hard timeout (30 seconds is typical). Cap memory, CPU, and output buffer size. Kill snippets that overrun; return the partial log and an error marker. Huge output buffers (100K+ lines of logs) confuse the model just as much as huge input contexts do.

### R.06 — Output Capture and Shaping

Return whatever the snippet wrote to stdout, truncated to a sensible window. Surface uncaught exceptions as model-readable errors with stack traces — the model is good at fixing TypeScript errors when it can see them.

### R.07 — Progressive Disclosure (Especially Important at 120 Tools)

With 120 tools, even the typed header can be large. Use progressive disclosure:

- Load only a short index into the system prompt: server names, tool names, one-line descriptions
- Give the model a `search()` meta-tool callable from inside snippets: `codemode.search("drive upload")` returns the full schema for matching tools on demand
- Cloudflare keeps 2,500 endpoints (their full API surface is 1.17M tokens in classic mode) under 1K tokens using this approach

For 120 tools across 8 servers, a well-structured index with one-liner descriptions per tool should fit in 2–4K tokens.

### R.08 — Audit Log

Log every snippet execution: source code, the MCP calls it made, results, and runtime. Treat these like infrastructure change plans — reviewable artifacts, not opaque tool call sequences. This replaces the "human-readable tool-call record" you lose when you move from discrete tool calls to code snippets.

---

## What the Token Reduction Looks Like in Practice

Classic mode with your setup:

```
// 40K tokens of schema definitions load before first message
tool_call drive.getFile({ id: "abc" })
// → 15K token document returns INTO model context
tool_call salesforce.createRecord({ data: "...15K tokens..." })
// Total: ~70K+ tokens for a two-step workflow
```

Code Mode with the same workflow:

```typescript
const doc = await drive.getFile({ id: "abc" });  // stays in sandbox
await salesforce.createRecord({ data: doc.content }); // stays in sandbox
console.log("created");  // ← this is all the model sees
```

Schema tokens in context: 2–3K (index + on-demand lookup).
Intermediate payload tokens: 0 — never leaves the sandbox.

---

## Hybrid Option (If You Want a Staged Migration)

You don't have to do a full Code Mode replacement immediately. A proven pattern for production harnesses:

- Keep classic tool calls for cheap one-shot operations (single-step, no chaining)
- Add an `execute(code)` tool for chained workflows

Let the model choose which to use. It generally chooses well — short one-shot calls get a direct tool call; anything involving multiple steps or large payloads goes through `execute`.

---

## What You Give Up

This isn't free:

- **Sandbox infrastructure** is a real ops surface — you need to patch, monitor, and watch for escape attempts
- **Approval UX collapses**: you're approving 15 lines of TypeScript, not a named tool call. For workflows where an end-user reviews every step, this is a harder UX to build
- **Debugging is harder**: tracing through generated code with generated bindings requires better logging discipline (see R.08)
- **Per-call overhead**: for truly one-shot calls, spinning a sandbox costs more than a single tool call. The hybrid approach above handles this

---

## Security Note

A sandbox prevents _escape_ from your process. It does not prevent _authorized harm_. If the sandbox has a binding to `crm.deleteRecord`, a prompt-injected model that calls it will succeed — the runtime is working correctly. Scope OAuth tokens at auth time. Allowlist destructive operations per role. Sandboxing is defense-in-depth, not your security perimeter.

---

## Quick Start Recommendation

Given you're in Go with 8 servers and 120 tools:

1. Add `goja` as a dependency
2. Write a startup function that calls `tools/list` on each server and emits a TypeScript `.d.ts` header with doc comments
3. Expose one tool to the model: `execute(code string)`
4. Inside `execute`: run the snippet in goja with host-function bindings for each MCP server (no credentials in the sandbox)
5. Return stdout as the tool result
6. Add a short index prompt and a `search()` meta-tool callable from snippets

That's a working proof of concept. R.05–R.08 are hardening steps you layer in before production.
