---
name: code-mode-mcp
description: >
  Expert reference for Code Mode MCP — the agent architecture pattern where Claude writes TypeScript/Python code against typed APIs generated from MCP schemas, replacing hundreds of discrete tool calls with a single execute(code) tool (98%+ token reduction, per Anthropic/Cloudflare). USE THIS SKILL whenever a user: has 5+ MCP servers or 50+ tools and asks about context window costs or tool schema bloat; asks "should I use code mode or classic tool calling"; is choosing a sandbox runtime for agent code execution (goja, wazero, starlark-go, E2B, Firecracker, isolated-vm, pyodide, RestrictedPython); asks about auth boundaries or credential hygiene in an execute(code) agent loop; mentions tool definitions eating the context window before conversations start; asks about typed API generation from MCP schemas or the execute(code) pattern; or is implementing Code Mode in Go, Python, or TypeScript. This skill contains a sandbox runtime comparison table (9 options with startup/isolation/host-language tradeoffs), a Go vs Cloudflare implementation table, an 8-item implementation checklist with security constraints, and a decision matrix not reliably in general training data. Prefer this skill over answering from general knowledge whenever MCP architecture, sandbox design, or execute(code) loops are involved.
version: 1.0.0
allowed-tools: Bash Read Grep Glob WebFetch
---

# Code Mode MCP

Agents write code against typed APIs generated from MCP schemas. The code runs in a
sandbox; only `console.log` output returns to the model. Token cost stays flat
regardless of API surface size.

**Reference**: [Full guide with tables and examples](references/guide.md)

## Should they use Code Mode? (decide first)

**Use it when:**
- 5+ MCP servers, or 50+ tools total
- Workflows chain 3+ tool calls together
- Intermediate results are large (transcripts, PDFs, query results > 10K tokens)
- Hitting context-window limits before completing tasks
- Data segregation matters (sensitive payloads must not appear in prompt logs)

**Stay with classic tool calling when:**
- Fewer than 10 tools, rarely chained
- Most calls are one-shot ("what's the weather?")
- End-users review every tool call before it runs
- Can't ship or operate a sandbox
- Compliance posture demands human-readable tool-call records (not code diffs)

**Hybrid answer** (best for most production harnesses): classic tool calls for cheap
one-shot operations + an `execute(code)` tool for chained workflows. Let the model
choose. It generally chooses well.

## Pick a sandbox runtime

This is the single highest-stakes infrastructure decision. See
[references/guide.md](references/guide.md) for the full comparison table.

**Go harness shortlist:**

| Option | Isolation | Effort | Model fluency |
|--------|-----------|--------|---------------|
| `goja` | In-process (language-level) | Low | High (JS) |
| `wazero` | WASM (strong, no CGO) | Medium | High (JS/Python via WASM) |
| `starlark-go` | No I/O by design | Very low | Lower |

Prefer `goja` for fastest path; `wazero` when isolation matters more.
Language choice is the highest-impact lever — TypeScript and Python have far more
LLM training data than Starlark.

**Python harness:** FastMCP's built-in `CodeMode` transform. Swap to E2B for stronger isolation.

**TypeScript/Node:** `isolated-vm` or Cloudflare Workers.

## Eight implementation items

Walk through in order — each has a trust implication:

| # | Item | Key constraint |
|---|------|----------------|
| R.01 | Schema-to-typed-API codegen | Preserve descriptions as doc comments — that's the model's navigation |
| R.02 | Sandbox runtime | No network fetch, no filesystem, no env vars, hard timeout (30s) |
| R.03 | RPC bridge sandbox → host | Shims serialize args → host dispatches to MCP server with auth |
| R.04 | **Auth boundary on host** | Sandbox gets pre-authorized client objects, never raw tokens |
| R.05 | Resource limits + timeout | Kill on overrun; return partial log + error marker |
| R.06 | Output capture + shaping | Truncate, surface exceptions with stack traces |
| R.07 | Progressive disclosure | For 50+ tools: short index + `search()` meta-tool in snippets |
| R.08 | Audit log | Log source code + MCP calls made + results + runtime per snippet |

## Three deployment shapes

- **Client-side** (harness owns sandbox): works with any compliant MCP server today
- **Server-side** (MCP server owns sandbox): any MCP client gets Code Mode for free; FastMCP `CodeMode` transform; Cloudflare MCP Portal
- **Filesystem-mounted discovery**: tools as files, loaded via directory listing on demand — drives the 150K→2K result

## Security: the critical trap

A sandbox prevents *escape* — it doesn't prevent *authorized harm*. If the sandbox
has a binding to `salesforce.deleteRecord`, a prompt-injected model that calls it
will succeed — the runtime did its job.

Treat every binding as a privilege grant. Scope OAuth tokens at auth time. Allowlist
destructive operations per-role. Sandboxing is defense-in-depth, not the perimeter.

## Worked example token comparison

| Approach | Tokens | Round-trips |
|----------|--------|-------------|
| Classic tool calling (Drive → Salesforce, 25K transcript) | ~150K | 2 — transcript crosses model boundary twice |
| Code Mode (same task) | ~2K | 1 — transcript stays in sandbox |

Full worked example with code in [references/guide.md](references/guide.md).
