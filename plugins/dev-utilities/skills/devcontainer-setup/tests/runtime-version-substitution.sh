#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT

marker='<!-- runtime-version-workflow -->'
[ "$(rg -c -F "$marker" "$SKILL_DIR/references/tool-detection.md")" -eq 1 ]
workflow=$(
  awk -v marker="$marker" '
    $0 == marker { marked = 1; next }
    marked && /^```bash$/ { capture = 1; next }
    capture && /^```$/ { exit }
    capture { print }
  ' "$SKILL_DIR/references/tool-detection.md"
)
[ -n "$workflow" ]

printf 'v20.11.1\n' >"$FIXTURE/.nvmrc"
printf 'module example.test/fixture\n\ngo 1.23.4\n' >"$FIXTURE/go.mod"
printf '3.3.6\n' >"$FIXTURE/.ruby-version"
printf '[toolchain]\nchannel = "1.80.1"\n' >"$FIXTURE/rust-toolchain.toml"
cat >"$FIXTURE/runtime.template" <<'EOF'
FROM node:{{NODE_VERSION}}-bookworm
ARG GO_VERSION={{GO_VERSION}}
ARG RUBY_VERSION={{RUBY_VERSION}}
ARG RUST_VERSION={{RUST_VERSION}}
EOF

(
  cd "$FIXTURE"
  RUNTIME_TEMPLATE=runtime.template RUNTIME_OUTPUT=runtime.rendered \
    bash -c "$workflow"
)
rg -q -F 'FROM node:20.11.1-bookworm' "$FIXTURE/runtime.rendered"
rg -q -F 'ARG GO_VERSION=1.23.4' "$FIXTURE/runtime.rendered"
rg -q -F 'ARG RUBY_VERSION=3.3.6' "$FIXTURE/runtime.rendered"
rg -q -F 'ARG RUST_VERSION=1.80.1' "$FIXTURE/runtime.rendered"
if rg -q '\{\{(NODE|GO|RUBY|RUST)_VERSION\}\}' "$FIXTURE/runtime.rendered"; then
  echo "exact rendering retained a runtime placeholder" >&2
  exit 1
fi

printf '>=20\n' >"$FIXTURE/.nvmrc"
if (
  cd "$FIXTURE"
  RUNTIME_TEMPLATE=runtime.template RUNTIME_OUTPUT=range.rejected \
    bash -c "$workflow"
) >"$FIXTURE/range.out" 2>"$FIXTURE/range.err"; then
  echo "ambiguous Node range rendered without confirmation" >&2
  exit 1
fi
rg -q -F "Node.js version '>=20' requires an exact value or confirmed fallback 20" \
  "$FIXTURE/range.err"

(
  cd "$FIXTURE"
  RUNTIME_TEMPLATE=runtime.template RUNTIME_OUTPUT=range.confirmed \
    RUNTIME_VERSION_CONFIRMATION=yes bash -c "$workflow"
)
rg -q -F 'FROM node:20-bookworm' "$FIXTURE/range.confirmed"
rg -q -F 'ARG GO_VERSION=1.23.4' "$FIXTURE/range.confirmed"
rg -q -F 'ARG RUBY_VERSION=3.3.6' "$FIXTURE/range.confirmed"
rg -q -F 'ARG RUST_VERSION=1.80.1' "$FIXTURE/range.confirmed"
if rg -q '\{\{(NODE|GO|RUBY|RUST)_VERSION\}\}' "$FIXTURE/range.confirmed"; then
  echo "confirmed rendering retained a runtime placeholder" >&2
  exit 1
fi

echo "runtime workflow fixtures passed: exact render plus range rejection/confirmation"
