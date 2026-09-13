// Repo-onboarding analysis workflow.
// The parent substitutes these before launch:
//   __REPO_PATH__  -> JSON string literal (json.dumps of the absolute repo path)
//   __FACTS_JSON__ -> JSON object literal (output of scripts/repo-facts.py)
//   __QUICK__      -> boolean literal (true for a lightweight 6-scout pass)
const REPO_PATH = __REPO_PATH__;
const FACTS = __FACTS_JSON__;
const QUICK = __QUICK__;

const KEYS = ['goal', 'profile', 'entry', 'ext', 'abs', 'data', 'runtime', 'testing', 'repos', 'contrib', 'rationale'];

const FACTS_BRIEF = {
  repo: FACTS.repo || null,
  remote: FACTS.remote || null,
  languages: FACTS.languageCounts || {},
  manifests: FACTS.manifests || [],
  entryCandidates: FACTS.entryCandidates || [],
  topLevelDirs: FACTS.topLevel || [],
  activeDirs: FACTS.activeDirs || []
};

const WRITING = [
  'WRITING RULES (follow strictly - plain language, ASD-STE100 style):',
  '1. Short sentences. One idea per sentence. About 20 words or fewer for steps.',
  '2. Active voice. Imperative mood for instructions.',
  '3. Use everyday words. Use one term for one thing. No jargon synonyms.',
  '4. Do not hedge. Avoid \'may\', \'might\', \'could\' when a fact is certain.',
  '5. Lead with the answer. Give the detail after.',
  '6. Write for a new teammate who has never seen this repository.'
].join('\n');

function base(role) {
  return [
    'You are a read-only ' + role + ' analyzing the repository at: ' + REPO_PATH,
    'Use only read, grep, ls, and read-only bash commands. Use fd for file searches. Do NOT edit or create files.',
    'Do NOT spawn subagents.',
    WRITING,
    '',
    'Deterministic repository facts (use these to orient; verify by reading files):',
    JSON.stringify(FACTS_BRIEF, null, 2),
    ''
  ].join('\n');
}

function t(agent, key, label, prompt, schema) {
  return { key: key, label: label, agent: agent, task: prompt, outputSchema: schema };
}

// ---- Wave 1: eleven parallel read-only scouts ----

const SCOUTS = [
  t('scout', 'goal', 'Analyze project goal',
    base('scout') + [
      'OBJECTIVE: State what this project does and why it exists.',
      'LOOK AT: README, docs/, top-level Markdown, package description fields, file headers.',
      'IGNORE: implementation details and build scripts.',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { tagline: { type: 'string' }, goal: { type: 'string' }, mentalModel: { type: 'string' }, audience: { type: 'string' } }, required: ['tagline', 'goal', 'mentalModel'], additionalProperties: false }),

  t('scout', 'profile', 'Analyze languages and frameworks',
    base('scout') + [
      'OBJECTIVE: Identify languages, frameworks, runtime target, build tool, and license.',
      'LOOK AT: manifest and lock files, Dockerfile, license files, config files.',
      'IGNORE: vendored dependencies (node_modules, vendor, .venv).',
      'PRODUCE: languages (array), frameworks (array), runtime (one of: CLI, web server, browser app, library, desktop app, mobile app, daemon/service, other), build (package manager and build command), license (name, or \'not found\').',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { languages: { type: 'array', items: { type: 'string' } }, frameworks: { type: 'array', items: { type: 'string' } }, runtime: { type: 'string' }, build: { type: 'string' }, license: { type: 'string' } }, required: ['languages', 'frameworks', 'runtime', 'build', 'license'], additionalProperties: false }),

  t('scout', 'entry', 'Analyze entry points',
    base('scout') + [
      'OBJECTIVE: Find how the program starts and its main entry points.',
      'LOOK AT: entryCandidates in the facts, package scripts, main/bin files, cmd/ directories.',
      'IGNORE: tests and examples.',
      'PRODUCE: summary (one sentence), items (array of {path, why}) with 3 to 8 entries.',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { summary: { type: 'string' }, items: { type: 'array', items: { type: 'object', properties: { path: { type: 'string' }, why: { type: 'string' } }, required: ['path', 'why'], additionalProperties: false } } }, required: ['summary', 'items'], additionalProperties: false }),

  t('scout', 'ext', 'Analyze extension points',
    base('scout') + [
      'OBJECTIVE: Find extension points: plugins, hooks, interfaces, public APIs, events, config schemas.',
      'LOOK AT: interface/abstract/trait definitions, plugin directories, event or registry code, public exports, config schemas.',
      'IGNORE: internal helpers.',
      'PRODUCE: array of {name, location (path), how (one plain sentence on how to extend)}.',
      'Return the JSON array described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, location: { type: 'string' }, how: { type: 'string' } }, required: ['name', 'location', 'how'], additionalProperties: false } }),

  t('scout', 'abs', 'Analyze architectural abstractions',
    base('scout') + [
      'OBJECTIVE: Identify the major architectural abstractions and module layering.',
      'LOOK AT: top-level directories, core domain modules, class hierarchies, layers (presentation/domain/data), dependency direction.',
      'IGNORE: tests and utilities.',
      'PRODUCE: array of {name, where (path), role (one plain sentence)} - the 4 to 10 most important abstractions.',
      'Return the JSON array described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, where: { type: 'string' }, role: { type: 'string' } }, required: ['name', 'where', 'role'], additionalProperties: false } }),

  t('scout', 'data', 'Analyze data and integrations',
    base('scout') + [
      'OBJECTIVE: Identify persistence, schemas, external services, and message queues.',
      'LOOK AT: ORM models, migrations, schema files, API clients, queue/event code.',
      'IGNORE: unrelated code.',
      'PRODUCE: array of {name, kind (db|api|queue|migration|other), detail (one plain sentence)}.',
      'Return the JSON array described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, kind: { type: 'string', enum: ['db', 'api', 'queue', 'migration', 'other'] }, detail: { type: 'string' } }, required: ['name', 'kind', 'detail'], additionalProperties: false } }),

  t('scout', 'runtime', 'Analyze deployment and ops',
    base('scout') + [
      'OBJECTIVE: Identify how the app runs in production: deployment, configuration, secrets, observability.',
      'LOOK AT: Dockerfiles, compose files, Kubernetes/Terraform/IaC files, env example files, logging/metrics/tracing config.',
      'IGNORE: dev-only scripts.',
      'PRODUCE: summary (one sentence), config (array of env var or config names), secrets (one sentence on how secrets are handled, or \'not found\'), observability (one sentence on logging/metrics/tracing, or \'not found\').',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { summary: { type: 'string' }, config: { type: 'array', items: { type: 'string' } }, secrets: { type: 'string' }, observability: { type: 'string' } }, required: ['summary'], additionalProperties: false }),

  t('scout', 'testing', 'Analyze testing and CI',
    base('scout') + [
      'OBJECTIVE: Identify how quality is enforced: tests, lint, format, type checking, CI.',
      'LOOK AT: test directories, test config, CI workflows (.github/workflows, .gitlab-ci.yml, Jenkinsfile), lint/format configs.',
      'IGNORE: test bodies.',
      'PRODUCE: commands (array of exact commands to test/build/lint), quality (array of lint/format/typecheck tool names), ci (one sentence on what CI does, or \'none found\').',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { commands: { type: 'array', items: { type: 'string' } }, quality: { type: 'array', items: { type: 'string' } }, ci: { type: 'string' } }, required: ['commands'], additionalProperties: false }),

  t('scout', 'repos', 'Analyze multi-repo relationships',
    base('scout') + [
      'OBJECTIVE: Map relationships with other repositories.',
      'LOOK AT: internal package imports (org-scoped names), submodules (.gitmodules), monorepo workspaces, references to sibling repositories in docs and CI, published packages.',
      'IGNORE: third-party external dependencies.',
      'PRODUCE: array of {name, relationship (depends-on|publishes-to|submodule|monorepo-workspace|ci|other), note (one plain sentence)}. Empty array if none.',
      'Return the JSON array described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, relationship: { type: 'string', enum: ['depends-on', 'publishes-to', 'submodule', 'monorepo-workspace', 'ci', 'other'] }, note: { type: 'string' } }, required: ['name', 'relationship', 'note'], additionalProperties: false } }),

  t('scout', 'contrib', 'Analyze contribution workflow',
    base('scout') + [
      'OBJECTIVE: Identify how to contribute and the required developer setup.',
      'LOOK AT: CONTRIBUTING.md, README setup section, AGENTS.md, CODEOWNERS, PR/commit templates, .editorconfig, pre-commit config.',
      'IGNORE: unrelated docs.',
      'PRODUCE: setup (ordered array of commands to get running), conventions (array of code/commit/PR conventions), readingOrder (array of file paths to read first, best first).',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { setup: { type: 'array', items: { type: 'string' } }, conventions: { type: 'array', items: { type: 'string' } }, readingOrder: { type: 'array', items: { type: 'string' } } }, required: ['setup', 'conventions', 'readingOrder'], additionalProperties: false }),

  t('scout', 'rationale', 'Analyze rationale and activity',
    base('scout') + [
      'OBJECTIVE: Identify domain terms, design rationale, tech debt, and active development areas.',
      'LOOK AT: docs/adr and design docs, glossaries, TODO/FIXME/XXX comments, recentCommits and activeDirs in the facts, deprecation notices.',
      'IGNORE: trivial TODOs.',
      'PRODUCE: glossary (object mapping term to a one-sentence plain definition, 0 to 10 entries), adrs (array of decision summaries), debt (array of one-sentence debt or deprecation items), activity (array of one-sentence notes on where recent work is happening).',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { glossary: { type: 'object', additionalProperties: { type: 'string' } }, adrs: { type: 'array', items: { type: 'string' } }, debt: { type: 'array', items: { type: 'string' } }, activity: { type: 'array', items: { type: 'string' } } }, additionalProperties: false })
];

const QUICK_KEYS = ['goal', 'profile', 'entry', 'ext', 'abs', 'contrib'];
const selected = QUICK ? SCOUTS.filter(function (s) { return QUICK_KEYS.indexOf(s.key) !== -1; }) : SCOUTS;
const results = await runs.all(selected);
const scoutData = results.map(function (r, i) {
  return { key: selected[i].key, data: r.structuredOutput || r.output || null };
});

const scoutJSON = JSON.stringify(scoutData, null, 2);

// ---- Wave 2: two fresh reviewers + one diagram specialist, in parallel ----

const [missed, verify, viz] = await runs.all([
  t('reviewer', 'missed', 'Find what scouts missed',
    base('reviewer') + [
      'You are reviewing the structured findings of the scouts who analyzed the repository. Their outputs follow.',
      scoutJSON,
      'OBJECTIVE: Find what the scouts MISSED - things a newcomer needs that no scout covered.',
      'LOOK FOR: gotchas and footguns, build or test quirks, security notes (authentication, trust boundaries, untrusted input), hidden coupling, anything surprising.',
      'PRODUCE: missed (array of {title, detail}; each detail is one or two plain sentences), nextReads (array of paths or docs to read next).',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { missed: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, detail: { type: 'string' } }, required: ['title', 'detail'], additionalProperties: false } }, nextReads: { type: 'array', items: { type: 'string' } } }, required: ['missed', 'nextReads'], additionalProperties: false }),

  t('reviewer', 'verify', 'Verify scout findings',
    base('reviewer') + [
      'You are reviewing the structured findings of the scouts who analyzed the repository. Their outputs follow.',
      scoutJSON,
      'OBJECTIVE: Find ERRORS and INCONSISTENCIES in the findings - wrong claims, wrong paths, duplicated or overlapping items across scouts.',
      'PRODUCE: corrections (array of {target (which scout and item), issue (one sentence), fix (the corrected text)}). Empty array if none.',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { corrections: { type: 'array', items: { type: 'object', properties: { target: { type: 'string' }, issue: { type: 'string' }, fix: { type: 'string' } }, required: ['target', 'issue', 'fix'], additionalProperties: false } } }, required: ['corrections'], additionalProperties: false }),

  t('architect', 'viz', 'Draw architecture diagrams',
    base('architect') + [
      'You are the diagram specialist. The structured findings of the scouts follow.',
      scoutJSON,
      'Produce 2 to 4 diagrams, ordered by importance, following your agent instructions (architecture, dependency direction, main flow, multi-repo).',
      'Return the JSON object described by the schema. No prose, no fences.'
    ].join('\n'),
    { type: 'object', properties: { diagrams: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, kind: { type: 'string', enum: ['mermaid', 'svg'] }, code: { type: 'string' } }, required: ['title', 'kind', 'code'], additionalProperties: false } } }, required: ['diagrams'], additionalProperties: false })
]);

return {
  scouts: scoutData,
  missed: missed.structuredOutput || null,
  verify: verify.structuredOutput || null,
  diagrams: (viz.structuredOutput && viz.structuredOutput.diagrams) || []
};
