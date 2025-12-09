# Capacities API Workflows

Common usage patterns and workflows for the Capacities API skill.

## Quick Note Capture

**Goal:** Rapidly save a thought or note to your daily journal.

**Steps:**
1. User expresses thought/idea
2. Claude formats as markdown
3. Append to daily note

**Example:**
```
User: "Remember to review the API design tomorrow"

Claude executes:
/capacities:daily-note --space-id <default-space> --text "- [ ] Review API design"
```

**Best for:**
- Quick thoughts during work
- Task reminders
- Ideas that pop up mid-conversation

---

## Web Clipping Workflow

**Goal:** Save interesting URLs with context and annotations.

**Steps:**
1. User shares URL
2. Optionally add title, description, tags
3. Save with any additional notes

**Example:**
```
User: "Save this article about Rust async: https://tokio.rs/blog/post"

Claude executes:
/capacities:save-weblink \
  --url "https://tokio.rs/blog/post" \
  --space-id <reading-space> \
  --tags "rust,async,programming"
```

**Variations:**
- With user notes: Add `--content` with user's commentary
- Quick save: Just URL and auto-detected metadata
- Categorized: Use specific space for topic

---

## Knowledge Search

**Goal:** Find information in your knowledge base.

**Steps:**
1. User asks a question or describes what they're looking for
2. Claude constructs search query
3. Execute search across relevant spaces
4. Present results with context

**Example:**
```
User: "What did I write about project planning last month?"

Claude executes:
/capacities:search "project planning" --space-ids <all-spaces> --mode fullText
```

**Search Strategies:**
- **Title search** (default): Fast, good for known items
- **Full-text search**: Comprehensive, finds mentions anywhere
- **Filtered search**: Narrow to specific structures (notes, weblinks, etc.)

---

## Space Exploration

**Goal:** Understand what's in a Capacities space.

**Steps:**
1. List all spaces
2. Get detailed info for space of interest
3. Explore structures and collections

**Example:**
```
User: "What kinds of things are in my Work space?"

Claude executes:
/capacities:list-spaces
/capacities:space-info <work-space-id>
```

**Use for:**
- Onboarding to a new Capacities setup
- Finding the right space for saving content
- Understanding available object types

---

## Meeting Notes Capture

**Goal:** Log meeting notes to daily journal.

**Steps:**
1. User describes meeting outcomes
2. Claude formats as structured markdown
3. Append to daily note (with or without timestamp)

**Example:**
```
User: "We just finished the standup. Discussed blockers on the auth feature,
       and John will handle the code review by EOD."

Claude formats and executes:
/capacities:daily-note --space-id <work-space> --text "## Standup Notes

### Discussed
- Auth feature blockers

### Action Items
- [ ] John: Code review by EOD"
```

---

## Research Collection

**Goal:** Build a collection of resources on a topic.

**Steps:**
1. Save multiple URLs with consistent tags
2. Add notes/annotations for each
3. Search later by tag or content

**Example:**
```
User: "I'm researching database optimization. Save these links..."

Claude executes (for each URL):
/capacities:save-weblink \
  --url <url> \
  --space-id <research-space> \
  --tags "database,optimization,research" \
  --content "## Summary\n<brief summary>"
```

---

## Daily Review Integration

**Goal:** Use Capacities as part of daily workflow.

**Morning:**
```
/capacities:search "today" --space-ids <work-space> --mode title
# See what's scheduled

/capacities:daily-note --text "## Today's Focus\n- ..."
# Set intentions
```

**Throughout Day:**
```
/capacities:daily-note --text "- Completed: <task>"
# Log progress
```

**End of Day:**
```
/capacities:daily-note --text "## Wrap-up\n- Accomplishments: ...\n- Tomorrow: ..."
# Reflect and plan
```

---

## Handling Multiple Spaces

Most users have multiple spaces (Personal, Work, Projects, etc.).

**Strategy 1: Explicit Selection**
```
User: "Save to my Work space"
Claude: Uses work space ID directly
```

**Strategy 2: Context-Based Selection**
```
User: "Save this meeting notes article"
Claude: Infers Work space from "meeting"
```

**Strategy 3: Interactive Selection**
```
User: "Save this article"
Claude: "Which space? You have: Personal, Work, Reading"
User: "Reading"
Claude: Saves to Reading space
```

---

## Rate Limit Management

The API has strict rate limits. Handle gracefully:

| Endpoint | Limit | Strategy |
|----------|-------|----------|
| spaces | 5/60s | Cache aggressively (5 min) |
| space-info | 5/60s | Cache per space (10 min) |
| search | 120/60s | Generous, minimal concern |
| save-weblink | 10/60s | Batch if multiple saves |
| daily-note | 5/60s | Combine entries when possible |

**When Rate Limited:**
1. Check `RateLimit-Reset` header
2. Wait specified seconds
3. Retry operation

---

## Error Recovery

### Token Issues
```
Error: 401 Unauthorized

Recovery:
1. Check CAPACITIES_API_TOKEN is set
2. Regenerate token in Capacities settings
3. Update environment variable
```

### Space Not Found
```
Error: 404 Not Found (space)

Recovery:
1. Run /capacities:list-spaces
2. Verify space ID is correct
3. Check if space was deleted/archived
```

### Content Too Long
```
Error: 400 Bad Request (mdText exceeds limit)

Recovery:
1. Check content length (max 200,000 chars)
2. Split into multiple daily-note entries
3. Or summarize content before saving
```
