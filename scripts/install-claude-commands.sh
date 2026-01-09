#!/usr/bin/env bash
#
# install-claude-commands.sh - Install plugin commands to Claude Code's commands directory
#
# Usage:
#   ./scripts/install-claude-commands.sh [OPTIONS]
#
# Options:
#   -a, --all           Install all plugins
#   -p, --plugin NAME   Plugin to install (can be repeated)
#   -d, --dry-run       Show what would be copied without doing it
#   -f, --force         Overwrite existing commands
#   -v, --verbose       Detailed output
#   -h, --help          Show this help message
#
# Available plugins: commits, pull-requests, dev-utilities, capacities

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Defaults
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PLUGINS_DIR="$REPO_ROOT/plugins"
CLAUDE_COMMANDS_DIR="${CLAUDE_HOME:-$HOME/.claude}/commands"

DRY_RUN=false
FORCE=false
VERBOSE=false
INSTALL_ALL=false
declare -a PLUGINS=()

# Logging functions
log_info() { echo -e "${BLUE}i${NC} $*"; }
log_success() { echo -e "${GREEN}+${NC} $*"; }
log_warn() { echo -e "${YELLOW}!${NC} $*"; }
log_error() { echo -e "${RED}x${NC} $*" >&2; }
log_verbose() { [[ "$VERBOSE" == true ]] && echo -e "  $*" || true; }

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install plugin commands to Claude Code's commands directory (~/.claude/commands/)

Options:
  -a, --all           Install all plugins
  -p, --plugin NAME   Install specific plugin(s), can be repeated
  -d, --dry-run       Show what would be copied without doing it
  -f, --force         Overwrite existing commands
  -v, --verbose       Detailed output
  -h, --help          Show this help message

Available plugins:
  commits         Conventional commit creation (commit, commit-push, commit-split)
  pull-requests   PR creation and conflict resolution (pr, pr-update, merge-conflicts, pr-comment-review)
  dev-utilities   CI analyzer, rule generator, git-optimize, etc.
  capacities      Capacities knowledge management API

Examples:
  $(basename "$0") -p commits -p pull-requests -p dev-utilities  # Install specific plugins
  $(basename "$0") --all                                         # Install all plugins
  $(basename "$0") -p commits -d                                 # Dry run for commits only
  $(basename "$0") -p dev-utilities -f                           # Force overwrite dev-utilities
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--all)
            INSTALL_ALL=true
            shift
            ;;
        -p|--plugin)
            PLUGINS+=("$2")
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate plugin exists
validate_plugin() {
    local plugin="$1"
    if [[ ! -d "$PLUGINS_DIR/$plugin" ]]; then
        log_error "Plugin '$plugin' not found in $PLUGINS_DIR"
        echo "Available plugins:"
        for dir in "$PLUGINS_DIR"/*/; do
            [[ -d "$dir" ]] && echo "  - $(basename "$dir")"
        done
        exit 1
    fi
    if [[ ! -d "$PLUGINS_DIR/$plugin/commands" ]]; then
        log_warn "Plugin '$plugin' has no commands directory"
        return 1
    fi
    return 0
}

# Validate command has required frontmatter
validate_command() {
    local cmd_file="$1"
    local cmd_name
    cmd_name=$(basename "$cmd_file")

    if [[ ! -f "$cmd_file" ]]; then
        log_error "Command file not found: $cmd_file"
        return 1
    fi

    # Check for required frontmatter field
    if ! grep -q "^description:" "$cmd_file"; then
        log_error "Missing 'description' field in $cmd_file"
        return 1
    fi

    log_verbose "Validated: $cmd_name"
    return 0
}

# Find all command files in a plugin
find_commands() {
    local plugin_dir="$1"
    local commands_dir="$plugin_dir/commands"

    if [[ ! -d "$commands_dir" ]]; then
        return
    fi

    # Use fd if available, fallback to find
    if command -v fd &>/dev/null; then
        fd -t f -e md . "$commands_dir" 2>/dev/null
    else
        find "$commands_dir" -name "*.md" -type f 2>/dev/null
    fi
}

# Install a single command
install_command() {
    local cmd_file="$1"
    local cmd_name
    cmd_name=$(basename "$cmd_file")
    local dest_file="$CLAUDE_COMMANDS_DIR/$cmd_name"

    # Check if destination exists
    if [[ -f "$dest_file" ]] && [[ "$FORCE" != true ]]; then
        log_warn "Command '$cmd_name' already exists (use --force to overwrite)"
        return 1
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would copy: $cmd_file -> $dest_file"
        return 0
    fi

    # Copy command file
    cp "$cmd_file" "$dest_file"
    log_success "Installed: $cmd_name"
    return 0
}

# Main
main() {
    # Check if no plugins specified and not --all
    if [[ "$INSTALL_ALL" != true ]] && [[ ${#PLUGINS[@]} -eq 0 ]]; then
        log_error "No plugins specified. Use -p to specify plugins or -a for all."
        echo
        usage
        exit 1
    fi

    log_info "Claude Code Commands Installer"
    log_info "Source: $PLUGINS_DIR"
    log_info "Destination: $CLAUDE_COMMANDS_DIR"
    [[ "$DRY_RUN" == true ]] && log_warn "DRY RUN MODE - no changes will be made"
    echo

    # Create destination directory
    if [[ "$DRY_RUN" != true ]]; then
        mkdir -p "$CLAUDE_COMMANDS_DIR"
    fi

    # Determine which plugins to process
    local plugins_to_process=()
    if [[ "$INSTALL_ALL" == true ]]; then
        for dir in "$PLUGINS_DIR"/*/; do
            [[ -d "$dir" ]] && plugins_to_process+=("$(basename "$dir")")
        done
    else
        plugins_to_process=("${PLUGINS[@]}")
    fi

    # Validate all plugins first
    for plugin in "${plugins_to_process[@]}"; do
        validate_plugin "$plugin" || continue
    done

    local total_installed=0
    local total_skipped=0
    local total_failed=0

    for plugin in "${plugins_to_process[@]}"; do
        local plugin_dir="$PLUGINS_DIR/$plugin"

        if [[ ! -d "$plugin_dir/commands" ]]; then
            continue
        fi

        log_info "Processing plugin: $plugin"

        while IFS= read -r cmd_file; do
            [[ -z "$cmd_file" ]] && continue

            if validate_command "$cmd_file"; then
                if install_command "$cmd_file"; then
                    total_installed=$((total_installed + 1))
                else
                    total_skipped=$((total_skipped + 1))
                fi
            else
                total_failed=$((total_failed + 1))
            fi
        done < <(find_commands "$plugin_dir")
        echo
    done

    # Summary
    log_info "Summary:"
    echo "  Installed: $total_installed"
    echo "  Skipped:   $total_skipped"
    echo "  Failed:    $total_failed"

    if [[ "$DRY_RUN" == true ]]; then
        echo
        log_info "Run without --dry-run to apply changes"
    fi
}

main
