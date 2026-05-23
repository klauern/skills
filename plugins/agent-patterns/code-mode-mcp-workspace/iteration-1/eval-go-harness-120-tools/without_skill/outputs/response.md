# Managing Context Window Bloat with 120 MCP Tools in a Go Agent Harness

You're hitting a real architectural ceiling. 40K tokens of schema definitions before a single user message means you're burning 20-40% of most models' usable context on scaffolding alone — and that cost resets every conversation turn that requires tool re-injection. Here's how to approach this systematically.

## Why This Happens

MCP tool schemas are verbose by design. Each tool definition includes the tool name, a description, and a full JSON Schema for its input parameters — including nested objects, enums, descriptions on every field, and `required` arrays. A moderately complex tool easily runs 300-800 tokens. With 120 tools across 8 servers, you're at the upper bound of what naively injecting the full schema set costs.

The model also doesn't need all 120 tools in every conversation. If your agent is doing a git operation, it doesn't need Slack or Google Calendar tool definitions loaded. That mismatch is where most of your savings live.

---

## Strategy 1: Dynamic Tool Injection (Highest Impact)

Don't load all tools at the start of every conversation. Instead, maintain a registry of all tools but only inject the ones relevant to the current task.

**How to implement in Go:**

1. At startup, fetch the full tool manifests from all 8 MCP servers and store them in a local registry (a `map[string]ToolDefinition` keyed by server+tool name).
2. Before sending the first API request, run a lightweight classification step — either a fast, cheap model call with just the user message (no tools), or a rules-based router that looks for keywords.
3. Inject only the tool definitions for the MCP servers and tools likely needed for that task.

```go
type ToolRegistry struct {
    tools map[string]MCPToolDef // server:toolname -> definition
    tags  map[string][]string   // server -> []category_tag
}

func (r *ToolRegistry) ToolsForTask(taskDescription string) []MCPToolDef {
    // Phase 1: cheap classification
    categories := classifyTask(taskDescription) // e.g., ["git", "filesystem"]
    
    // Phase 2: filter tools by category
    var relevant []MCPToolDef
    for _, tag := range categories {
        relevant = append(relevant, r.byCategory[tag]...)
    }
    return relevant
}
```

A conservative approach: start with 15-20 tools for the most likely servers, then dynamically expand if the model requests a tool that isn't loaded yet.

---

## Strategy 2: Tool Description Compression

MCP tool descriptions are written for human readability, not token efficiency. You can post-process them in your Go harness before injection.

**What to strip:**
- Verbose field descriptions that restate the type (e.g., `"description": "A string value representing the file path"` → `"description": "file path"`)
- Examples embedded in descriptions (move to a separate, rarely-injected reference document)
- Redundant enum documentation when the enum values are self-explanatory
- Default values that are already captured in the JSON Schema `default` field

**What to keep:**
- Tool name and top-level description (the model needs these to decide whether to call the tool)
- Parameter names and types
- `required` arrays
- Non-obvious constraints (e.g., `"maximum": 100`, specific format requirements)

A typical 500-token tool definition can often be reduced to 150-200 tokens with no loss of model performance on routine calls. Across 120 tools, that's potentially 36K-42K tokens trimmed to 12K-18K — a 60-70% reduction even if you inject everything.

```go
func compressToolDef(t MCPToolDef) MCPToolDef {
    t.Description = truncateToSentence(t.Description, 1) // first sentence only
    t.InputSchema = stripVerboseDescriptions(t.InputSchema)
    return t
}
```

---

## Strategy 3: Tool Grouping with On-Demand Expansion

Present the model with tool group stubs instead of full schemas, then expand on demand.

The pattern: define a meta-tool called something like `list_available_tools(server: string)` or `expand_tool_schema(tool_name: string)`. The model calls this when it needs to use an unfamiliar tool, your harness returns the full schema for that specific tool, and the model proceeds.

This is the most aggressive reduction — you can drop from 40K to under 5K tokens at conversation start — but it adds a round-trip for each new tool the model encounters. This round-trip cost is worth it when conversations are long or when most tasks only use 5-10 distinct tools.

**Harness-side implementation:**

```go
// Stub tool always injected
stubTool := MCPToolDef{
    Name: "get_tool_schema",
    Description: "Retrieve the full parameter schema for a tool before calling it. " +
        "Available servers: git, filesystem, github, slack, gcal, gdrive, jira, postgres",
    InputSchema: SchemaForGetToolSchema(),
}

// Handler
func handleGetToolSchema(server, toolName string) string {
    full := registry.Get(server, toolName)
    return json.Marshal(full)
}
```

The model will learn quickly (within a conversation) which tools it regularly needs and can batch-expand several at once.

---

## Strategy 4: Conversation-Level Tool Caching with Prompt Caching

If you're using Anthropic's API, use the `cache_control` breakpoint feature (available on Claude 3.5+ models). Place a cache breakpoint immediately after the tool definitions block. On subsequent turns within the same conversation, the tool definitions hit cache rather than being re-tokenized and re-charged.

```go
// In your message construction:
systemMessages := []anthropic.MessageParam{
    {
        Role: "system",
        Content: []anthropic.ContentBlock{
            {
                Type: "text",
                Text: toolDefsAsSystemPrompt,
                CacheControl: &anthropic.CacheControlEphemeral{Type: "ephemeral"},
            },
        },
    },
}
```

This doesn't reduce your input token count on the first turn, but it reduces cost and latency on all subsequent turns in the same session — critical for multi-step agentic tasks where the same 40K schema block would otherwise be re-processed 10-20 times.

**Important caveat**: Prompt caching works on the full prefix up to the breakpoint. If your tool list changes between turns (because you dynamically add tools), the cache is invalidated. Keep the cached portion stable and append dynamic content after the breakpoint.

---

## Strategy 5: Schema Externalization + Retrieval

For very large tool sets, treat tool documentation as a retrieval problem rather than an injection problem.

Build a local vector index of your tool definitions (using something lightweight like `go-faiss` or a BM25 index with `go-bleve`). At conversation start, embed the user's task description and retrieve the top-K most semantically similar tools.

This is overkill for 120 tools but becomes necessary above 500+ tools. The approach generalizes to any size and handles cases where keyword routing breaks down for ambiguous tasks.

---

## Practical Recommendation for Your Situation

Given 8 servers and 120 tools, I'd recommend combining strategies 1, 2, and 4:

1. **Immediate win**: Compress all tool descriptions (Strategy 2). This is a one-time preprocessing step, requires no architectural change, and should get you from 40K to roughly 15K tokens.

2. **Structural win**: Group tools by MCP server and inject only the servers relevant to the task (Strategy 1). Build a simple keyword classifier that maps task phrases to server names. Expected result: 3-5 servers active per task, down to 8K-12K tokens of compressed schemas.

3. **Cost win**: Add prompt cache breakpoints after the tool definitions (Strategy 4). Subsequent turns in a multi-step task are dramatically cheaper in both tokens and latency.

This combination should get you from 40K tokens to under 8K for typical tasks, with the caching layer making multi-turn conversations far more efficient.

---

## Things to Measure

Before optimizing, instrument your harness to capture:

- Token count per tool definition (so you know which tools are the most expensive)
- Tool usage frequency per server (so you know which servers to keep in the "always load" set)
- Task classification accuracy (so you know if your router is excluding tools that get called)

The last point matters: if your router incorrectly excludes a tool and the model needs it, you need a fallback. The cleanest fallback is a `get_tool_schema` meta-tool (Strategy 3) combined with a re-injection mechanism — the model requests the schema, your harness adds it to the active tool list, and the next API call includes it.

---

## Go-Specific Notes

- The `mark3labs/mcp-go` and `modelcontextprotocol/go-sdk` libraries both expose tool listing endpoints — use these at startup to build your registry, not at request time.
- Tool schema fetching from remote MCP servers (SSE/HTTP transport) should be cached aggressively; they rarely change during a session.
- Consider storing compressed tool definitions in a struct that retains the original for debugging but sends the compressed version to the API.
- If you're running multiple agents concurrently, share the tool registry across goroutines (read-only after initialization) to avoid redundant schema fetches.
