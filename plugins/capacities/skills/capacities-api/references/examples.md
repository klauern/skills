# Capacities API Examples

Detailed examples of using the Capacities API skill.

## Basic Operations

### List All Spaces

```bash
# Human-readable output
/capacities:list-spaces

# JSON output for parsing
uv run plugins/capacities/scripts/capacities.py spaces --json
```

**Output:**
```text
Your Capacities Spaces:
--------------------------------------------------
📝 Personal Notes
  ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

💼 Work Projects
  ID: b2c3d4e5-f6a7-8901-bcde-f12345678901

📚 Reading List
  ID: c3d4e5f6-a7b8-9012-cdef-123456789012
```

---

### Get Space Information

```bash
# With known space ID
/capacities:space-info a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Direct script call
uv run plugins/capacities/scripts/capacities.py space-info \
  a1b2c3d4-e5f6-7890-abcd-ef1234567890 --json
```

**Output:**
```text
Space Structures:
--------------------------------------------------

Note (Notes)
  ID: struct-note-uuid
  Color: blue
  Collections (3):
    - Meeting Notes (coll-meetings)
    - Project Ideas (coll-ideas)
    - Daily Journal (coll-journal)

Weblink (Weblinks)
  ID: struct-weblink-uuid
  Color: green
  Collections (2):
    - Articles (coll-articles)
    - Resources (coll-resources)
```

---

## Search Examples

### Simple Title Search

```bash
/capacities:search "project plan" \
  --space-ids a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Output:**
```text
Found 3 results:
--------------------------------------------------

Q4 Project Plan
  ...quarterly **project plan** review...
  ID: obj-uuid-1

Project Planning Template
  ID: obj-uuid-2

New Project Plan: Mobile App
  ...initial **project plan** for the...
  ID: obj-uuid-3
```

---

### Full-Text Search Across Multiple Spaces

```bash
uv run plugins/capacities/scripts/capacities.py search "API design patterns" \
  --space-ids "space-1,space-2,space-3" \
  --mode fullText \
  --json
```

**JSON Output:**
```json
{
  "results": [
    {
      "id": "obj-uuid-1",
      "title": "REST API Best Practices",
      "spaceId": "space-1",
      "structureId": "weblink-struct",
      "highlights": [
        "discusses common **API design patterns** including..."
      ]
    },
    {
      "id": "obj-uuid-2",
      "title": "Meeting: Architecture Review",
      "spaceId": "space-2",
      "structureId": "note-struct",
      "highlights": [
        "reviewed our **API design** approach and **patterns**..."
      ]
    }
  ]
}
```

---

### Filtered Search

```bash
# Search only in Notes structure
uv run plugins/capacities/scripts/capacities.py search "meeting" \
  --space-ids "work-space-id" \
  --filter "note-struct-uuid" \
  --json
```

---

## Save Weblink Examples

### Simple Save

```bash
/capacities:save-weblink \
  --url "https://docs.python.org/3/" \
  --space-id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Output:**
```text
Weblink saved successfully!
  Title: Python 3.12 Documentation
  ID: new-obj-uuid
```

---

### Save with All Options

```bash
uv run plugins/capacities/scripts/capacities.py save-weblink \
  --space-id "reading-space-uuid" \
  --url "https://example.com/great-article" \
  --title "Must-Read: Great Article on System Design" \
  --description "Comprehensive guide to distributed systems" \
  --tags "system-design,architecture,distributed" \
  --content "## My Notes

### Key Takeaways
- Point 1: Consistency vs Availability trade-offs
- Point 2: Partition tolerance is non-negotiable
- Point 3: Start simple, scale when needed

### Questions
- How does this apply to our current architecture?
- Should we revisit our caching strategy?

### Action Items
- [ ] Share with team
- [ ] Schedule discussion" \
  --json
```

**JSON Output:**
```json
{
  "spaceId": "reading-space-uuid",
  "id": "created-obj-uuid",
  "structureId": "weblink-struct-uuid",
  "title": "Must-Read: Great Article on System Design",
  "description": "Comprehensive guide to distributed systems",
  "tags": ["system-design", "architecture", "distributed"]
}
```

---

## Daily Note Examples

### Quick Thought

```bash
/capacities:daily-note \
  --space-id "personal-space-uuid" \
  --text "Idea: Create a CLI tool for batch API testing"
```

**Result in Capacities:**
```text
12:34 PM - Idea: Create a CLI tool for batch API testing
```

---

### Structured Entry (No Timestamp)

```bash
uv run plugins/capacities/scripts/capacities.py daily-note \
  --space-id "work-space-uuid" \
  --text "## Standup Summary

### Yesterday
- Completed auth module refactor
- Fixed 3 critical bugs

### Today
- Start API documentation
- Review PRs from team

### Blockers
- Waiting on design approval for dashboard" \
  --no-timestamp \
  --json
```

---

### Multi-Line with Formatting

```bash
/capacities:daily-note \
  --space-id "work-space-uuid" \
  --text "## Meeting: Product Review

**Attendees:** Alice, Bob, Charlie

### Decisions
1. Launch date: March 15
2. Pricing: Three tiers

### Action Items
- [ ] @Alice: Finalize copy
- [ ] @Bob: Update landing page
- [ ] @Charlie: Prepare demo

### Notes
> Important quote from stakeholder:
> 'We need to focus on user onboarding experience'

\`\`\`
Key metrics to track:
- DAU/MAU ratio
- Time to first value
- Retention at day 7
\`\`\`"
```

---

## Script Direct Usage

### Check Token

```bash
# Verify token is set
echo $CAPACITIES_API_TOKEN

# If empty, set it
export CAPACITIES_API_TOKEN='your-token-here'
```

### Bypass Cache

```bash
# Force fresh data
uv run plugins/capacities/scripts/capacities.py spaces --no-cache
uv run plugins/capacities/scripts/capacities.py space-info <id> --no-cache
```

### Pipeline Examples

```bash
# Get first space ID
SPACE_ID=$(uv run plugins/capacities/scripts/capacities.py spaces --json | jq -r '.spaces[0].id')

# Search in that space
uv run plugins/capacities/scripts/capacities.py search "meeting" \
  --space-ids "$SPACE_ID" \
  --json | jq '.results[].title'
```

---

## Error Handling Examples

### Missing Token

```bash
$ unset CAPACITIES_API_TOKEN
$ uv run plugins/capacities/scripts/capacities.py spaces

Error: CAPACITIES_API_TOKEN environment variable not set.
Get your token from Capacities desktop app: Settings > Capacities API

Set it with: export CAPACITIES_API_TOKEN='your-token-here'
```

### Rate Limited

```bash
$ uv run plugins/capacities/scripts/capacities.py spaces
# ... called 6 times in 60 seconds ...

Error: Rate limit exceeded. Try again in 45 seconds.
```

### Invalid Space ID

```bash
$ uv run plugins/capacities/scripts/capacities.py space-info "invalid-uuid"

Error: Bad request - Invalid spaceid format. Expected UUID.
```
