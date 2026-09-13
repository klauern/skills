# Data schema and field mapping

The final object is written to `/tmp/repo-onboarding-<repo>.json` and injected
into `template.html` at the `%%DATA%%` placeholder.

## Field to scout mapping

| Field | Source |
|---|---|
| `repo`, `directoryMap` | facts file |
| `tagline`, `goal`, `mentalModel`, `audience` | scout `goal` |
| `profile` | scout `profile` |
| `entryPoint` | scout `entry` |
| `extensionPoints` | scout `ext` |
| `abstractions` | scout `abs` |
| `data` | scout `data` |
| `deployment` | scout `runtime` |
| `testing` | scout `testing` |
| `repos` | scout `repos` |
| `contributing` | scout `contrib` |
| `rationale` | scout `rationale` |
| `diagrams` | workflow `diagrams` |
| `missed`, `nextReads` | workflow `missed` |

## Target schema

```json
{
  "repo": "...",
  "tagline": "...",
  "mentalModel": "...",
  "audience": "...",
  "goal": "...",
  "profile": { "languages": ["..."], "frameworks": ["..."], "runtime": "...", "build": "...", "license": "..." },
  "entryPoint": { "summary": "...", "items": [{ "path": "...", "why": "..." }] },
  "extensionPoints": [{ "name": "...", "location": "...", "how": "..." }],
  "abstractions": [{ "name": "...", "where": "...", "role": "..." }],
  "data": [{ "name": "...", "kind": "db|api|queue|migration|other", "detail": "..." }],
  "deployment": { "summary": "...", "config": ["..."], "secrets": "...", "observability": "..." },
  "testing": { "commands": ["..."], "quality": ["..."], "ci": "..." },
  "repos": [{ "name": "...", "relationship": "...", "note": "..." }],
  "contributing": { "setup": ["..."], "conventions": ["..."], "readingOrder": ["..."] },
  "rationale": { "glossary": { "term": "..." }, "adrs": ["..."], "debt": ["..."], "activity": ["..."] },
  "diagrams": [{ "title": "...", "kind": "mermaid|svg", "code": "..." }],
  "missed": [{ "title": "...", "detail": "..." }],
  "nextReads": ["..."],
  "directoryMap": { "path/": ["subdir", "..."] }
}
```

## Workflow return shape

```json
{
  "scouts": [{ "key": "goal", "data": { "tagline": "...", "goal": "..." } }],
  "missed": { "missed": [{ "title": "...", "detail": "..." }], "nextReads": ["..."] },
  "verify": { "corrections": [{ "target": "...", "issue": "...", "fix": "..." }] },
  "diagrams": [{ "title": "...", "kind": "mermaid|svg", "code": "..." }]
}
```

## Script inventory

| Script | Input | Output |
|---|---|---|
| `scripts/repo-facts.py` | repo path | JSON facts (repo, languages, manifests, dir map, activity) |
| `scripts/prepare_workflow.py` | repo path + facts JSON | prepared `/tmp/repo-onboarding-analyze.js` |
| `scripts/render.py` | data JSON | `/tmp/repo-onboarding-<repo>.html` |
