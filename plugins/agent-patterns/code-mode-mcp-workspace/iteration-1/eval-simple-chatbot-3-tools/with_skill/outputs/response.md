# Should You Implement Code Mode MCP for Your 3-Tool Chatbot?

**Short answer: No. Stick with classic tool calling.**

## Your Situation

You have a chatbot with 3 MCP tools:
- Google Calendar
- Gmail
- A weather API

## The Decision Framework

Code Mode MCP is designed to solve two problems:

1. **Definition overload** — When too many tool schemas consume too much context window before any work happens (a 4-server gateway can eat ~9,400 tokens just in definitions)
2. **Payload round-tripping** — When large intermediate results (transcripts, PDFs, large query results) must pass through the model even though the model doesn't need to read them

Your setup has neither problem.

### Classic Tool Calling Is the Right Fit When:

- Fewer than 10 tools, rarely chained — **you have 3 tools**
- Most calls are one-shot ("what's the weather?", "what's on my calendar?") — **that's your use case**
- End-users review every tool call before it runs — **typical for a chatbot**
- You can't or don't want to operate a sandbox runtime

Your 3-tool chatbot checks all four of those boxes.

## Why Code Mode Would Be Overkill Here

Code Mode requires you to:

1. Build or operate a **sandbox runtime** (goja, wazero, E2B, isolated-vm, etc.) — real infrastructure with patching, monitoring, escape detection
2. Implement **schema-to-typed-API codegen** — walking each server's `tools/list` and emitting typed declarations
3. Build an **RPC bridge** from the sandbox back to your host process
4. Set up **resource limits, timeouts, output capture**, and an **audit log**

That's 8 non-trivial implementation items for a setup where your context window overhead is modest (3 tools = maybe 500–1,500 tokens of definitions) and your payloads are small (calendar events, email snippets, weather data are not 25,000-token transcripts).

The token savings don't materialize at this scale, and you'd be paying the operational cost for nothing.

## When to Revisit This Decision

Revisit Code Mode if any of these become true:

| Trigger | Threshold |
|---------|-----------|
| Total tools | 5+ MCP servers or 50+ tools |
| Chained calls | Workflows that chain 3+ tool calls in sequence |
| Intermediate payload size | Results exceeding ~10,000 tokens (e.g., long email threads, calendar history exports) |
| Context pressure | Hitting context-window limits before completing tasks |
| Data segregation | Sensitive email/calendar content must not appear in prompt logs |

## A Practical Middle Path (If You Do Scale Up)

If you eventually add more MCP servers, the best production pattern is **hybrid**:

- Classic tool calling for cheap one-shot operations (weather, quick calendar lookup)
- An `execute(code)` tool for chained workflows (e.g., "scan my calendar for the week, cross-reference emails about each meeting, and summarize action items")

The model generally chooses which mode to use correctly. You don't have to pick one globally.

## Bottom Line

Your 3-tool chatbot is exactly the use case that classic tool calling was built for. Code Mode solves a real problem — but it's a problem you don't have yet. Build the simpler thing, and keep this architecture in your back pocket for when you cross the 5-server or 50-tool threshold.
