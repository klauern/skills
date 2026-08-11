---
allowed-tools: Bash(uv run:*)
description: Save a webpage to a Capacities space
argument-hint: "--url <url> [--space-id <id>] [--title <t>] [--tags <t,t>] [--content <md>]"
---

# /capacities:save-weblink

Save a webpage URL to a Capacities space. Capacities fetches page metadata; `--title`
(≤500 chars), `--description` (≤1000), `--tags` (≤30, auto-created), and `--content`
(markdown notes, ≤200k) override or extend it.

## Usage

```bash
/capacities:save-weblink --url https://example.com/article --space-id abc-123
/capacities:save-weblink --url https://docs.python.org/3/ --space-id abc-123 \
    --title "Python 3 Documentation" --tags "python,docs,reference"
```

## Behavior

Follow the **capacities-api** skill (auth check → space resolution → execute):

```bash
# If --space-id is missing, list spaces and ask which to use
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" spaces

uv run "${CLAUDE_PLUGIN_ROOT}/scripts/capacities.py" save-weblink \
    --space-id "$SPACE_ID" --url "$URL" \
    ${TITLE:+--title "$TITLE"} ${DESCRIPTION:+--description "$DESCRIPTION"} \
    ${TAGS:+--tags "$TAGS"} ${CONTENT:+--content "$CONTENT"} --json
```

Rate limit is 10/60s — see the skill's API reference for schemas and error recovery.
