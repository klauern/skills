#!/usr/bin/env bash
#
# install-codex-skills.sh - Install klauern-skills to Codex's local skills directory
#
# Usage:
#   ./scripts/install-codex-skills.sh [OPTIONS]
#
# Options:
#   -p, --plugin NAME   Plugin to install (default: all)
#   -d, --dry-run       Show what would be copied without doing it
#   -f, --force         Overwrite existing skills
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
CODEX_SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

DRY_RUN=false
FORCE=false
VERBOSE=false
PLUGIN=""
INSTALL_ALL=false

# Logging functions
log_info() { echo -e "${BLUE}ℹ${NC} $*"; }
log_success() { echo -e "${GREEN}✓${NC} $*"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $*"; }
log_error() { echo -e "${RED}✗${NC} $*" >&2; }
log_verbose() { [[ "$VERBOSE" == true ]] && echo -e "  $*" || true; }

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install klauern-skills to Codex's local skills directory (~/.codex/skills/)

Options:
  -a, --all           Install all plugins (default if no plugin specified)
  -p, --plugin NAME   Install a specific plugin
  -d, --dry-run       Show what would be copied without doing it
  -f, --force         Overwrite existing skills
  -v, --verbose       Detailed output
  -h, --help          Show this help message

Available plugins:
  commits         Conventional commit creation (conventional-commits, commit-splitter)
  pull-requests   PR creation and conflict resolution
  dev-utilities   CI analyzer, rule generator, git-optimize, etc.
  capacities      Capacities knowledge management API

Examples:
  $(basename "$0")                      # Install all plugins (default)
  $(basename "$0") --all                # Explicitly install all plugins
  $(basename "$0") -p commits           # Install only commits plugin
  $(basename "$0") -d                   # Dry run (preview only)
  $(basename "$0") -f -p dev-utilities  # Force overwrite dev-utilities
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
            PLUGIN="$2"
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
    if [[ -n "$plugin" ]] && [[ ! -d "$PLUGINS_DIR/$plugin" ]]; then
        log_error "Plugin '$plugin' not found in $PLUGINS_DIR"
        echo "Available plugins:"
        for dir in "$PLUGINS_DIR"/*/; do
            [[ -d "$dir" ]] && echo "  - $(basename "$dir")"
        done
        exit 1
    fi
}

# Validate SKILL.md frontmatter has required fields
validate_skill() {
    local skill_dir="$1"
    local skill_md="$skill_dir/SKILL.md"
    local skill_name
    skill_name=$(basename "$skill_dir")

    if [[ ! -f "$skill_md" ]]; then
        log_error "SKILL.md not found in $skill_dir"
        return 1
    fi

    # Check for required frontmatter fields
    if ! grep -q "^name:" "$skill_md"; then
        log_error "Missing 'name' field in $skill_md"
        return 1
    fi

    if ! grep -q "^description:" "$skill_md"; then
        log_error "Missing 'description' field in $skill_md"
        return 1
    fi

    # Validate name matches directory (Agent Skills spec requirement)
    local yaml_name
    yaml_name=$(grep "^name:" "$skill_md" | head -1 | sed 's/^name:[[:space:]]*//')
    if [[ "$yaml_name" != "$skill_name" ]]; then
        log_warn "Skill name '$yaml_name' doesn't match directory '$skill_name'"
        log_verbose "Agent Skills spec recommends name matches directory"
    fi

    log_verbose "Validated: $skill_name"
    return 0
}

# Find all skills in a plugin directory (using fd for better performance)
find_skills() {
    local plugin_dir="$1"
    # Use fd if available, fallback to find
    if command -v fd &>/dev/null; then
        fd -t f "SKILL.md" "$plugin_dir" 2>/dev/null | while read -r skill_md; do
            dirname "$skill_md"
        done
    else
        find "$plugin_dir" -name "SKILL.md" -type f 2>/dev/null | while read -r skill_md; do
            dirname "$skill_md"
        done
    fi
}

# Install a single skill
install_skill() {
    local skill_dir="$1"
    local skill_name
    skill_name=$(basename "$skill_dir")
    local dest_dir="$CODEX_SKILLS_DIR/$skill_name"

    # Check if destination exists
    if [[ -d "$dest_dir" ]] && [[ "$FORCE" != true ]]; then
        log_warn "Skill '$skill_name' already exists at $dest_dir (use --force to overwrite)"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would copy: $skill_dir → $dest_dir"
        return 0
    fi

    # Remove existing if force
    if [[ -d "$dest_dir" ]] && [[ "$FORCE" == true ]]; then
        log_verbose "Removing existing: $dest_dir"
        rm -rf "$dest_dir"
    fi

    # Copy skill directory
    cp -r "$skill_dir" "$dest_dir"
    log_success "Installed: $skill_name → $dest_dir"
}

# Main
main() {
    log_info "Codex Skills Installer"
    log_info "Source: $PLUGINS_DIR"
    log_info "Destination: $CODEX_SKILLS_DIR"
    [[ "$DRY_RUN" == true ]] && log_warn "DRY RUN MODE - no changes will be made"
    echo

    # Validate plugin if specified
    validate_plugin "$PLUGIN"

    # Create destination directory
    if [[ "$DRY_RUN" != true ]]; then
        mkdir -p "$CODEX_SKILLS_DIR"
    fi

    # Determine which plugins to process
    local plugins_to_process=()
    if [[ -n "$PLUGIN" ]]; then
        plugins_to_process=("$PLUGIN")
    elif [[ "$INSTALL_ALL" == true ]] || [[ -z "$PLUGIN" ]]; then
        # Default behavior: install all plugins
        for dir in "$PLUGINS_DIR"/*/; do
            [[ -d "$dir" ]] && plugins_to_process+=("$(basename "$dir")")
        done
    fi

    local total_installed=0
    local total_skipped=0
    local total_failed=0

    for plugin in "${plugins_to_process[@]}"; do
        local plugin_dir="$PLUGINS_DIR/$plugin"
        log_info "Processing plugin: $plugin"

        while IFS= read -r skill_dir; do
            [[ -z "$skill_dir" ]] && continue

            if validate_skill "$skill_dir"; then
                if install_skill "$skill_dir"; then
                    total_installed=$((total_installed + 1))
                else
                    total_skipped=$((total_skipped + 1))
                fi
            else
                total_failed=$((total_failed + 1))
            fi
        done < <(find_skills "$plugin_dir")
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
