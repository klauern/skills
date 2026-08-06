#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$(mktemp -d)"
trap 'rm -r -- "$FIXTURE"' EXIT

printf 'v20.11.1\n' >"$FIXTURE/.nvmrc"
printf 'module example.test/fixture\n\ngo 1.23.4\n' >"$FIXTURE/go.mod"
printf '3.3.6\n' >"$FIXTURE/.ruby-version"
printf '[toolchain]\nchannel = "1.80.1"\n' >"$FIXTURE/rust-toolchain.toml"

node=$(sed -e 's/^[[:space:]]*v//' -e 's/[[:space:]]*$//' "$FIXTURE/.nvmrc")
go=$(awk '/^go / {print $2; exit}' "$FIXTURE/go.mod")
ruby=$(sed -e 's/^[[:space:]]*v//' -e 's/[[:space:]]*$//' "$FIXTURE/.ruby-version")
rust=$(awk -F'"' '/^[[:space:]]*channel[[:space:]]*=/{print $2; exit}' "$FIXTURE/rust-toolchain.toml")

is_exact() {
  [[ $1 =~ ^[0-9]+(\.[0-9]+){0,2}$ ]]
}

for value in "$node" "$go" "$ruby" "$rust"; do
  is_exact "$value" || { echo "expected exact version: $value" >&2; exit 1; }
done
for range in '>=20' '^20' '~> 3.3' '1.80.*'; do
  if is_exact "$range"; then
    echo "range unexpectedly accepted as exact: $range" >&2
    exit 1
  fi
done

rg -q -F 'FROM node:{{NODE_VERSION}}-bookworm' "$SKILL_DIR/references/templates.md"
rg -q -F 'ARG GO_VERSION={{GO_VERSION}}' "$SKILL_DIR/references/tool-detection.md"
rg -q -F 'ARG RUBY_VERSION={{RUBY_VERSION}}' "$SKILL_DIR/references/tool-detection.md"
rg -q -F 'ARG RUST_VERSION={{RUST_VERSION}}' "$SKILL_DIR/references/tool-detection.md"

echo "runtime version fixtures passed: Node $node, Go $go, Ruby $ruby, Rust $rust"
