# Examples

Real-world dependency upgrade scenarios.

## Simple npm Upgrade

**Scenario**: Update all npm packages in a project

**Before** (package.json):
```json
{
  "dependencies": {
    "express": "^4.17.0",
    "lodash": "^4.17.20"
  }
}
```

**Commands**:
```bash
npx ncu
# express  ^4.17.0  →  ^4.18.2
# lodash   ^4.17.20 →  ^4.17.21

npx ncu -u
npm install
```

**After**:
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "^4.17.21"
  }
}
```

**Commit**: `chore(deps): upgrade npm dependencies`

## Major Version with Breaking Changes

**Scenario**: React 17 to 18 upgrade with breaking changes

**Detection**:
```bash
npx ncu
# react     ^17.0.2  →  ^18.2.0  (MAJOR)
# react-dom ^17.0.2  →  ^18.2.0  (MAJOR)
```

**Breaking Change Analysis**:
```bash
gh api repos/facebook/react/releases/tags/v18.0.0 --jq '.body' | head -50
# - New root API: createRoot instead of render
# - Automatic batching changes
# - Strict mode behavior changes
```

**Decision Point**:
```
React 17.0.2 → 18.2.0 has breaking changes:
- New root API (ReactDOM.createRoot)
- Automatic batching behavior
- Strict mode double-rendering

Apply upgrade? [Yes / Skip / Show migration guide]
```

**Commit**:
```
chore(deps): upgrade react to v18

- react: 17.0.2 → 18.2.0
- react-dom: 17.0.2 → 18.2.0

Breaking changes addressed:
- Updated to createRoot API
- Verified batching behavior
```

## Multi-Ecosystem Project

**Scenario**: Project with both npm and poetry

**Detection**:
```bash
ls package.json pyproject.toml
# package.json
# pyproject.toml
```

**Decision Point**:
```
Found multiple ecosystems:
1. npm (package.json) - 5 outdated
2. poetry (pyproject.toml) - 3 outdated

Upgrade which? [All / npm only / poetry only]
```

**npm Upgrades**:
```bash
npx ncu -u
npm install
```

**Poetry Upgrades**:
```bash
poetry update
```

**Commit**:
```
chore(deps): upgrade npm and python dependencies

npm:
- express: 4.17.0 → 4.18.2
- typescript: 4.9.0 → 5.0.0

poetry:
- django: 4.1.0 → 4.2.0
- requests: 2.28.0 → 2.31.0
```

## Go Module Upgrade

**Scenario**: Update Go dependencies with major version

**Check outdated**:
```bash
go list -m -u all
# github.com/gin-gonic/gin v1.8.0 [v1.9.1]
# github.com/go-redis/redis/v8 v8.11.5 [v9.0.5]
```

**Note**: redis v8 → v9 requires import path change

**Update minor/patch**:
```bash
go get -u github.com/gin-gonic/gin@v1.9.1
go mod tidy
```

**Major version (redis)**:
```bash
# Update import paths first
sed -i 's|github.com/go-redis/redis/v8|github.com/redis/go-redis/v9|g' *.go

# Then update go.mod
go get github.com/redis/go-redis/v9
go mod tidy
```

**Commit**:
```
chore(deps): upgrade go dependencies

- gin: v1.8.0 → v1.9.1
- redis: v8 → v9 (migrated to redis/go-redis)
```

## Selective Upgrade (Skip Breaking)

**Scenario**: Upgrade only non-breaking changes

**Commands**:
```bash
# npm - minor/patch only
npx ncu --target minor -u

# poetry - update within constraints
poetry update

# go - patch only
go get -u=patch ./...

# cargo - compatible only
cargo upgrade --compatible
```

**Commit**: `chore(deps): upgrade dependencies (non-breaking)`

## Workspace/Monorepo Upgrade

**Scenario**: npm workspaces monorepo

**Detection**:
```bash
jq -r '.workspaces[]' package.json
# packages/*
```

**Upgrade all workspaces**:
```bash
npx ncu --workspaces -u
npm install
```

**Upgrade specific workspace**:
```bash
npx ncu --workspace packages/core -u
npm install
```

**Commit**: `chore(deps): upgrade workspace dependencies`
