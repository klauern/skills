#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Convert Claude Code hookify rules to Cursor hooks format.

Usage:
    convert-hooks.py [--list] [--dry-run] [--force]

Options:
    --list      List hookify rules without converting
    --dry-run   Preview generated files without writing
    --force     Overwrite existing Cursor hooks

Examples:
    # List available rules
    convert-hooks.py --list

    # Preview conversion
    convert-hooks.py --dry-run

    # Convert and write files
    convert-hooks.py

    # Force overwrite
    convert-hooks.py --force
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Event mapping: hookify event -> cursor event
EVENT_MAP = {
    "bash": "beforeShellExecution",
    "prompt": "beforeSubmitPrompt",
    "file": "beforeReadFile",  # Default for file events
    "stop": "stop",
}

# Action mapping: hookify action -> cursor permission
ACTION_MAP = {
    "block": "deny",
    "warn": "ask",
}

# Input variable for each cursor event
INPUT_VAR_MAP = {
    "beforeShellExecution": "${command}",
    "beforeSubmitPrompt": "${prompt}",
    "beforeReadFile": "${file_path}",
    "afterFileEdit": "${file_path}",
    "stop": "${status}",
}


@dataclass
class HookifyRule:
    """Parsed hookify rule."""
    name: str
    enabled: bool
    event: str
    pattern: str
    action: str
    conditions: list[dict[str, Any]]
    message: str
    source_file: Path


def find_hookify_rules(base_dir: Path) -> list[Path]:
    """Find all hookify rule files."""
    claude_dir = base_dir / ".claude"
    if not claude_dir.exists():
        return []
    return sorted(claude_dir.glob("hookify.*.local.md"))


def parse_hookify_rule(rule_file: Path) -> HookifyRule | None:
    """Parse a hookify rule file."""
    content = rule_file.read_text()

    # Split frontmatter and body
    if not content.startswith("---"):
        print(f"Warning: {rule_file.name} has no frontmatter, skipping", file=sys.stderr)
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"Warning: {rule_file.name} has invalid frontmatter, skipping", file=sys.stderr)
        return None

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"Warning: {rule_file.name} has invalid YAML: {e}", file=sys.stderr)
        return None

    body = parts[2].strip()

    # Extract rule name from filename: hookify.{name}.local.md
    match = re.match(r"hookify\.(.+)\.local\.md", rule_file.name)
    if not match:
        print(f"Warning: {rule_file.name} has unexpected filename format", file=sys.stderr)
        return None

    rule_name = match.group(1)

    # Get pattern from either top-level or conditions
    pattern = frontmatter.get("pattern", "")
    conditions = frontmatter.get("conditions", [])

    # If no top-level pattern, extract from conditions
    if not pattern and conditions:
        for cond in conditions:
            if cond.get("operator") == "regex_match":
                pattern = cond.get("pattern", "")
                break

    # Extract message from body (capture meaningful content)
    message_lines = []
    empty_line_count = 0
    for line in body.split("\n"):
        stripped = line.strip()
        # Skip markdown headers
        if stripped.startswith("#"):
            continue
        # Track empty lines - stop after 2 consecutive
        if not stripped:
            empty_line_count += 1
            if empty_line_count >= 2:
                break
            continue
        empty_line_count = 0
        # Skip list markers but keep content
        if stripped.startswith("- "):
            stripped = stripped[2:]
        message_lines.append(stripped)

    message = " ".join(message_lines)
    # Clean up markdown formatting
    message = re.sub(r"\*\*([^*]+)\*\*", r"\1", message)  # Remove bold
    message = re.sub(r"`([^`]+)`", r"\1", message)  # Remove code
    message = message.replace("  ", " ")  # Clean double spaces

    return HookifyRule(
        name=frontmatter.get("name", rule_name),
        enabled=frontmatter.get("enabled", True),
        event=frontmatter.get("event", "bash"),
        pattern=pattern,
        action=frontmatter.get("action", "block"),
        conditions=conditions,
        message=message[:500] if message else f"Rule: {rule_name}",  # Truncate long messages
        source_file=rule_file,
    )


def generate_script(rule: HookifyRule) -> str:
    """Generate a Cursor hook script from a hookify rule."""
    permission = ACTION_MAP.get(rule.action, "deny")

    # Escape pattern for shell
    pattern = rule.pattern.replace("'", "'\"'\"'")

    # Create user and agent messages
    user_message = rule.message.replace('"', '\\"')
    agent_message = user_message

    # Generate script
    script = f'''#!/bin/bash
# Generated from: {rule.source_file.name}
# Rule: {rule.name}

INPUT="$1"

if echo "$INPUT" | grep -qE '{pattern}'; then
  cat <<'EOF'
{{
  "permission": "{permission}",
  "userMessage": "{user_message}",
  "agentMessage": "{agent_message}"
}}
EOF
  exit 0
fi

echo '{{"permission": "allow"}}'
'''
    return script


def generate_hooks_json(rules: list[HookifyRule], existing: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate hooks.json content."""
    hooks_json: dict[str, Any] = existing or {
        "version": 1,
        "hooks": {},
    }

    # Migrate from old format: replace $schema with version
    if "$schema" in hooks_json:
        del hooks_json["$schema"]
        hooks_json["version"] = 1

    # Ensure version is present
    if "version" not in hooks_json:
        hooks_json["version"] = 1

    if "hooks" not in hooks_json:
        hooks_json["hooks"] = {}

    # Migrate existing hooks: remove unsupported "description" field
    for event_hooks in hooks_json["hooks"].values():
        for hook in event_hooks:
            if "description" in hook:
                del hook["description"]

    # Track which hooks we're generating (to avoid duplicates)
    hookify_marker = "hookify-"

    for rule in rules:
        cursor_event = EVENT_MAP.get(rule.event)
        if not cursor_event:
            print(f"Warning: Unknown event '{rule.event}' in {rule.name}, skipping", file=sys.stderr)
            continue

        input_var = INPUT_VAR_MAP.get(cursor_event, "${input}")
        script_name = f"hookify-{rule.name}.sh"

        hook_entry = {
            "command": f'.cursor/hooks/{script_name} "{input_var}"',
        }

        # Initialize event array if needed
        if cursor_event not in hooks_json["hooks"]:
            hooks_json["hooks"][cursor_event] = []

        # Remove existing hookify entries for this rule
        hooks_json["hooks"][cursor_event] = [
            h for h in hooks_json["hooks"][cursor_event]
            if hookify_marker not in h.get("command", "")
            or f"hookify-{rule.name}.sh" in h.get("command", "")
        ]

        # Check if this specific rule already exists
        existing_commands = [h.get("command", "") for h in hooks_json["hooks"][cursor_event]]
        if hook_entry["command"] not in existing_commands:
            hooks_json["hooks"][cursor_event].append(hook_entry)

    # Clean up empty event arrays
    hooks_json["hooks"] = {k: v for k, v in hooks_json["hooks"].items() if v}

    return hooks_json


def list_rules(rules: list[HookifyRule]) -> None:
    """Print list of hookify rules."""
    if not rules:
        print("No hookify rules found in .claude/")
        return

    print(f"Found {len(rules)} hookify rule(s):\n")
    print("-" * 60)

    for rule in rules:
        status = "enabled" if rule.enabled else "DISABLED"
        print(f"\n{rule.name} [{status}]")
        print(f"  Event: {rule.event} -> {EVENT_MAP.get(rule.event, 'unknown')}")
        print(f"  Action: {rule.action} -> {ACTION_MAP.get(rule.action, 'unknown')}")
        if rule.pattern:
            print(f"  Pattern: {rule.pattern[:50]}{'...' if len(rule.pattern) > 50 else ''}")
        print(f"  Source: {rule.source_file.name}")


def dry_run(rules: list[HookifyRule], base_dir: Path) -> None:
    """Preview generated files without writing."""
    enabled_rules = [r for r in rules if r.enabled]

    if not enabled_rules:
        print("No enabled rules to convert.")
        return

    print(f"Dry run: Would generate files for {len(enabled_rules)} rule(s)\n")

    # Show hooks.json preview
    print("=" * 60)
    print(".cursor/hooks.json:")
    print("=" * 60)
    hooks_json = generate_hooks_json(enabled_rules)
    print(json.dumps(hooks_json, indent=2))

    # Show script previews
    for rule in enabled_rules:
        print("\n" + "=" * 60)
        print(f".cursor/hooks/hookify-{rule.name}.sh:")
        print("=" * 60)
        print(generate_script(rule))


def convert_rules(rules: list[HookifyRule], base_dir: Path, force: bool = False) -> None:
    """Convert rules and write files."""
    enabled_rules = [r for r in rules if r.enabled]

    if not enabled_rules:
        print("No enabled rules to convert.")
        return

    cursor_dir = base_dir / ".cursor"
    hooks_dir = cursor_dir / "hooks"

    # Create directories
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Load existing hooks.json if present
    hooks_json_path = cursor_dir / "hooks.json"
    existing_hooks = None
    if hooks_json_path.exists():
        try:
            existing_hooks = json.loads(hooks_json_path.read_text())
            print(f"Found existing {hooks_json_path.name}, will merge")
        except json.JSONDecodeError:
            print(f"Warning: Existing {hooks_json_path.name} is invalid, will overwrite", file=sys.stderr)

    # Generate hooks.json
    hooks_json = generate_hooks_json(enabled_rules, existing_hooks)

    # Write hooks.json
    hooks_json_path.write_text(json.dumps(hooks_json, indent=2) + "\n")
    print(f"Wrote {hooks_json_path}")

    # Generate and write scripts
    for rule in enabled_rules:
        script_path = hooks_dir / f"hookify-{rule.name}.sh"

        if script_path.exists() and not force:
            print(f"Skipping {script_path.name} (exists, use --force to overwrite)")
            continue

        script = generate_script(rule)
        script_path.write_text(script)
        script_path.chmod(0o755)  # Make executable
        print(f"Wrote {script_path}")

    print(f"\nConverted {len(enabled_rules)} rule(s) successfully!")
    print("\nNext steps:")
    print("  1. Review generated files in .cursor/")
    print("  2. Test in Cursor by triggering a hook")
    print("  3. Commit the changes if everything works")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Claude Code hookify rules to Cursor hooks format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--list", action="store_true", help="List hookify rules without converting")
    parser.add_argument("--dry-run", action="store_true", help="Preview generated files without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing Cursor hooks")

    args = parser.parse_args()

    # Find project root (look for .claude directory)
    base_dir = Path.cwd()

    # Find and parse rules
    rule_files = find_hookify_rules(base_dir)

    if not rule_files:
        print("No hookify rules found.")
        print("\nLooking for: .claude/hookify.*.local.md")
        print("Create rules with: /hookify:hookify")
        sys.exit(0)

    rules = []
    for rule_file in rule_files:
        rule = parse_hookify_rule(rule_file)
        if rule:
            rules.append(rule)

    if not rules:
        print("No valid hookify rules found.")
        sys.exit(1)

    # Execute requested action
    if args.list:
        list_rules(rules)
    elif args.dry_run:
        dry_run(rules, base_dir)
    else:
        convert_rules(rules, base_dir, args.force)


if __name__ == "__main__":
    main()
