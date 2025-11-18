#!/usr/bin/env bash
#
# memory-backup.sh - Backup memory database
#
# Usage:
#   memory-backup.sh [--output <path>]
#
# Example:
#   memory-backup.sh
#   memory-backup.sh --output /tmp/memory-backup.db
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
MEMORY_DIR="$GIT_ROOT/.agentic/memory"
BACKUP_DIR="$MEMORY_DIR/backups"
DB_PATH="$MEMORY_DIR/memory.db"

# Parse arguments
OUTPUT_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --output)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [[ ! -f "$DB_PATH" ]]; then
    echo "❌ Memory database not found: $DB_PATH" >&2
    echo "Run setup-memory.sh first to initialize the memory system" >&2
    exit 1
fi

# Determine output path
if [[ -z "$OUTPUT_PATH" ]]; then
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    OUTPUT_PATH="$BACKUP_DIR/memory-$TIMESTAMP.db"
fi

# Create backup
echo "📦 Creating backup of memory database..."
echo "   Source: $DB_PATH"
echo "   Destination: $OUTPUT_PATH"

cp "$DB_PATH" "$OUTPUT_PATH"

# Get file size
SIZE=$(du -h "$OUTPUT_PATH" | cut -f1)

echo "✅ Backup created successfully"
echo "   Size: $SIZE"
echo "   Path: $OUTPUT_PATH"

# Clean up old backups (keep last 10)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/memory-*.db 2>/dev/null | wc -l)
if [[ $BACKUP_COUNT -gt 10 ]]; then
    echo "🧹 Cleaning up old backups (keeping last 10)..."
    ls -1t "$BACKUP_DIR"/memory-*.db | tail -n +11 | xargs rm -f
fi

exit 0
