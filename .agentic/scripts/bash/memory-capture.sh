#!/usr/bin/env bash
#
# memory-capture.sh - Capture spec-kit artifacts into memory database
#
# Usage:
#   memory-capture.sh --feature-dir <dir> --type <type> --file <path>
#
# Example:
#   memory-capture.sh --feature-dir specs/003-feature-name --type spec --file specs/003-feature-name/spec.md
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
MEMORY_EXTRACTOR="$SCRIPTS_DIR/memory-extractor.py"

# Parse arguments
FEATURE_DIR=""
ARTIFACT_TYPE=""
FILE_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --feature-dir)
            FEATURE_DIR="$2"
            shift 2
            ;;
        --type)
            ARTIFACT_TYPE="$2"
            shift 2
            ;;
        --file)
            FILE_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate arguments
if [[ -z "$FEATURE_DIR" ]] || [[ -z "$ARTIFACT_TYPE" ]] || [[ -z "$FILE_PATH" ]]; then
    echo "Usage: $0 --feature-dir <dir> --type <type> --file <path>" >&2
    exit 1
fi

# Check if file exists
if [[ ! -f "$FILE_PATH" ]]; then
    echo "Error: File not found: $FILE_PATH" >&2
    exit 1
fi

# Check if memory extractor exists
if [[ ! -f "$MEMORY_EXTRACTOR" ]]; then
    echo "Error: Memory extractor not found: $MEMORY_EXTRACTOR" >&2
    echo "Run setup-memory.sh first to initialize the memory system" >&2
    exit 1
fi

# Run memory extractor
echo "📝 Capturing $ARTIFACT_TYPE from $FILE_PATH..."
python3 "$MEMORY_EXTRACTOR" \
    --feature-dir "$FEATURE_DIR" \
    --type "$ARTIFACT_TYPE" \
    --file "$FILE_PATH"

exit $?
