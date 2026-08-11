---
name: session-capture
description: This skill should be used when the user asks to "capture session notes to Capacities", "save findings to knowledge base", "record debugging insights", or when proactively identifying valuable knowledge artifacts during research and development sessions worth preserving in Capacities.
version: 1.0.0
author: klauern
---

# Session Capture Skill

Proactively identify and save valuable knowledge artifacts to Capacities during development sessions. This skill provides guidelines -- not commands -- for when and how to capture insights.

## When to Capture

Save to Capacities when the session produces durable knowledge worth preserving:

- **Research discoveries**: Useful articles, documentation, tools, or libraries found during investigation
- **Debugging breakthroughs**: Root cause analysis, non-obvious fixes, or patterns that explain recurring issues
- **Architecture decisions**: Design choices with rationale, tradeoff analysis, or rejected alternatives
- **Tool configurations**: CLI flags, editor settings, or environment setups that took effort to figure out
- **Recurring solutions**: Fixes or workarounds applied more than once across projects

## When NOT to Capture

Skip capture for content that is ephemeral, sensitive, or low-value:

- **Secrets**: API keys, passwords, tokens, credentials of any kind
- **Temporary URLs**: localhost links, preview deployments, CI artifacts, short-lived presigned URLs
- **Common knowledge**: Standard library usage, basic CLI commands, well-documented APIs
- **Large code blocks**: Link to the source file or repository instead of pasting inline
- **Session-specific context**: Intermediate debugging steps, temporary workarounds already removed

## Capture Methods

### Weblinks (permanent resources)

Use `/capacities:save-weblink` for URLs worth revisiting:

- Articles, blog posts, and documentation pages
- GitHub repositories, issues, or pull requests
- Stack Overflow answers and forum threads
- Tool homepages and reference documentation

Include tags and a brief description explaining why the resource is useful, not just what it is.

### Daily Notes (temporal insights)

Use `/capacities:daily-note` for text-based insights tied to today:

- "Learned that X behaves differently when Y" observations
- Meeting takeaways and action items
- Progress updates on multi-day investigations
- Quick references to commands or patterns discovered today

Format daily notes with markdown headings and bullet points for scannability.

## Capture Workflow

### 1. Check Prerequisites

Before attempting any capture, verify `CAPACITIES_API_TOKEN` is set in the environment. If missing, inform the user and link to Capacities Settings > API.

### 2. Determine Space

Most users have a primary space. Use `/capacities:list-spaces` to discover available spaces if the target is unknown. Prefer asking the user once and reusing the space ID for the session.

### 3. Choose Method

| Content Type | Method | Example |
|---|---|---|
| URL / webpage | save-weblink | Documentation page, GitHub repo |
| Text insight | daily-note | "TIL: fd uses .gitignore by default" |
| Tool + URL | save-weblink with description | CLI tool homepage + usage notes |
| Decision record | daily-note | "Chose X over Y because Z" |

### 4. Add Context

Always include context that makes the captured item findable and useful later:

- **Weblinks**: Add 2-3 relevant tags, write a description that explains the "why"
- **Daily notes**: Use a heading that categorizes the insight (e.g., `## Debugging`, `## Architecture`)

### 5. Confirm Capture

After saving, briefly confirm what was captured so the user knows it succeeded without interrupting flow.

## Proactive Capture Signals

Watch for these patterns during sessions as signals that capture may be valuable:

- User says "that's useful" or "I'll need this again"
- A web search yields a particularly helpful result
- A non-obvious fix resolves a stubborn issue
- The session involves evaluating or comparing tools/approaches
- An important decision is made with reasoning worth preserving

When a signal is detected, suggest capture concisely -- do not interrupt flow with lengthy explanations.

## Integration with Other Skills

- Use the `capacities-api` skill commands for all API interactions
- Respect the API rate limits documented in the capacities-api skill
- Cache is shared with the CLI client at `~/.cache/capacities/`
