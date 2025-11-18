#!/usr/bin/env bash
#
# memory-query.sh - Quick memory database queries
#
# Usage:
#   memory-query.sh "search query"
#   memory-query.sh --similar-features "feature description"
#   memory-query.sh --decisions --category technology
#
# Example:
#   memory-query.sh "RBAC patterns"
#   memory-query.sh --similar-features "user dashboard"
#

set -euo pipefail

# Find git root
find_git_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.git" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo "$PWD"
}

GIT_ROOT="$(find_git_root)"
SCRIPTS_DIR="$GIT_ROOT/.agentic/scripts"
MEMORY_CLI="$SCRIPTS_DIR/memory-cli.py"

# Check if memory CLI exists
if [[ ! -f "$MEMORY_CLI" ]]; then
    echo "Error: Memory CLI not found: $MEMORY_CLI" >&2
    echo "Run setup-memory.sh first to initialize the memory system" >&2
    exit 1
fi

# Parse arguments and delegate to memory-cli
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <query> [options]" >&2
    echo "Examples:" >&2
    echo "  $0 \"RBAC patterns\"" >&2
    echo "  $0 \"email integration\" --type decision" >&2
    exit 1
fi

# Run memory CLI search command
python3 "$MEMORY_CLI" search "$@"

exit $?
