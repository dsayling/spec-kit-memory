#!/usr/bin/env bash
#
# setup-memory.sh - Initialize Spec-Kit Memory System
#
# This script sets up the spec-kit memory system in your repository.
# It can be run multiple times safely (idempotent).
#
# Usage:
#   ./setup-memory.sh [--target-dir /path/to/repo]
#
# Examples:
#   ./setup-memory.sh                           # Setup in current repo
#   ./setup-memory.sh --target-dir ~/my-repo    # Setup in specific repo
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default target directory
TARGET_DIR=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target-dir)
            TARGET_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--target-dir /path/to/repo]"
            echo ""
            echo "Options:"
            echo "  --target-dir DIR    Target repository directory (default: current directory)"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            exit 1
            ;;
    esac
done

# Find git root
find_git_root() {
    local dir="${1:-$PWD}"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.git" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo ""
}

# Determine target directory
if [[ -z "$TARGET_DIR" ]]; then
    TARGET_DIR=$(find_git_root)
    if [[ -z "$TARGET_DIR" ]]; then
        TARGET_DIR="$PWD"
    fi
else
    TARGET_DIR=$(cd "$TARGET_DIR" && pwd)
fi

# Source directory (where this script is located)
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Spec-Kit Memory System - Installation               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Target Directory:${NC} $TARGET_DIR"
echo -e "${BLUE}Source Directory:${NC} $SOURCE_DIR"
echo ""

# Check if target is a git repository
if [[ ! -d "$TARGET_DIR/.git" ]]; then
    echo -e "${YELLOW}⚠ Warning: Target directory is not a git repository${NC}"
    echo -e "${YELLOW}  The memory system works best in git repositories${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation aborted."
        exit 1
    fi
fi

# Step 1: Check dependencies
echo -e "${BLUE}[1/6]${NC} Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is required but not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}  ✓ Python 3 found: $PYTHON_VERSION${NC}"

# Check if sqlite3 module has FTS5 support
if python3 -c "import sqlite3; conn = sqlite3.connect(':memory:'); conn.execute('CREATE VIRTUAL TABLE test USING fts5(content)')" 2>/dev/null; then
    echo -e "${GREEN}  ✓ SQLite FTS5 support detected${NC}"
else
    echo -e "${YELLOW}  ⚠ SQLite FTS5 support not detected (search may not work)${NC}"
fi

# Step 2: Create directory structure
echo -e "${BLUE}[2/6]${NC} Creating directory structure..."

AGENTIC_DIR="$TARGET_DIR/.agentic"
mkdir -p "$AGENTIC_DIR/memory/backups"
mkdir -p "$AGENTIC_DIR/scripts/bash"
mkdir -p "$AGENTIC_DIR/config"

echo -e "${GREEN}  ✓ Created .agentic/memory/backups/${NC}"
echo -e "${GREEN}  ✓ Created .agentic/scripts/bash/${NC}"
echo -e "${GREEN}  ✓ Created .agentic/config/${NC}"

# Step 3: Copy files
echo -e "${BLUE}[3/6]${NC} Installing files..."

# Function to copy file if source exists
copy_file() {
    local src="$1"
    local dst="$2"
    local name="$3"

    if [[ -f "$src" ]]; then
        cp "$src" "$dst"
        chmod +x "$dst" 2>/dev/null || true
        echo -e "${GREEN}  ✓ Installed $name${NC}"
    else
        echo -e "${YELLOW}  ⚠ Source file not found: $src${NC}"
        return 1
    fi
}

# Copy scripts
copy_file "$SOURCE_DIR/.agentic/memory/schema.sql" \
          "$AGENTIC_DIR/memory/schema.sql" \
          "schema.sql"

copy_file "$SOURCE_DIR/.agentic/scripts/memory-lib.py" \
          "$AGENTIC_DIR/scripts/memory-lib.py" \
          "memory-lib.py"

copy_file "$SOURCE_DIR/.agentic/scripts/memory-cli.py" \
          "$AGENTIC_DIR/scripts/memory-cli.py" \
          "memory-cli.py"

copy_file "$SOURCE_DIR/.agentic/scripts/memory-extractor.py" \
          "$AGENTIC_DIR/scripts/memory-extractor.py" \
          "memory-extractor.py"

copy_file "$SOURCE_DIR/.agentic/scripts/bash/memory-capture.sh" \
          "$AGENTIC_DIR/scripts/bash/memory-capture.sh" \
          "memory-capture.sh"

copy_file "$SOURCE_DIR/.agentic/scripts/bash/memory-query.sh" \
          "$AGENTIC_DIR/scripts/bash/memory-query.sh" \
          "memory-query.sh"

copy_file "$SOURCE_DIR/.agentic/scripts/bash/memory-backup.sh" \
          "$AGENTIC_DIR/scripts/bash/memory-backup.sh" \
          "memory-backup.sh"

# Copy config if it doesn't exist (don't overwrite existing config)
if [[ ! -f "$AGENTIC_DIR/config/memory-config.yaml" ]]; then
    copy_file "$SOURCE_DIR/.agentic/config/memory-config.yaml" \
              "$AGENTIC_DIR/config/memory-config.yaml" \
              "memory-config.yaml"
else
    echo -e "${YELLOW}  ⚠ Config exists, skipping (preserving existing configuration)${NC}"
fi

# Step 4: Initialize database
echo -e "${BLUE}[4/6]${NC} Initializing database..."

DB_PATH="$AGENTIC_DIR/memory/memory.db"

if [[ -f "$DB_PATH" ]]; then
    echo -e "${YELLOW}  ⚠ Database already exists: $DB_PATH${NC}"
    echo -e "${YELLOW}    Skipping initialization (preserving existing data)${NC}"
else
    # Initialize database using Python
    python3 -c "
import sys
sys.path.insert(0, '$AGENTIC_DIR/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('memory_lib', '$AGENTIC_DIR/scripts/memory-lib.py')
memory_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_lib)
db = memory_lib.MemoryDB('$DB_PATH')
print('Database initialized successfully')
" && echo -e "${GREEN}  ✓ Database created: $DB_PATH${NC}" || {
        echo -e "${RED}  ✗ Failed to initialize database${NC}"
        exit 1
    }
fi

# Step 5: Update .gitignore
echo -e "${BLUE}[5/6]${NC} Updating .gitignore..."

GITIGNORE="$TARGET_DIR/.gitignore"

if [[ -f "$GITIGNORE" ]]; then
    # Check if memory entries already exist
    if grep -q "^.agentic/memory/memory.db" "$GITIGNORE" 2>/dev/null; then
        echo -e "${YELLOW}  ⚠ .gitignore already contains memory entries${NC}"
    else
        echo "" >> "$GITIGNORE"
        echo "# Spec-Kit Memory System" >> "$GITIGNORE"
        echo ".agentic/memory/memory.db" >> "$GITIGNORE"
        echo ".agentic/memory/backups/*.db" >> "$GITIGNORE"
        echo -e "${GREEN}  ✓ Added memory entries to .gitignore${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ No .gitignore found, creating one${NC}"
    cat > "$GITIGNORE" <<EOF
# Spec-Kit Memory System
.agentic/memory/memory.db
.agentic/memory/backups/*.db
EOF
    echo -e "${GREEN}  ✓ Created .gitignore with memory entries${NC}"
fi

# Step 6: Verify installation
echo -e "${BLUE}[6/6]${NC} Verifying installation..."

# Test CLI
if python3 "$AGENTIC_DIR/scripts/memory-cli.py" stats >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Memory CLI is working${NC}"
else
    echo -e "${RED}  ✗ Memory CLI test failed${NC}"
    exit 1
fi

# Test capture script
if [[ -x "$AGENTIC_DIR/scripts/bash/memory-capture.sh" ]]; then
    echo -e "${GREEN}  ✓ Capture script is executable${NC}"
else
    echo -e "${YELLOW}  ⚠ Capture script is not executable${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Installation Completed Successfully!            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. View statistics:"
echo -e "   ${YELLOW}cd $TARGET_DIR${NC}"
echo -e "   ${YELLOW}python3 .agentic/scripts/memory-cli.py stats${NC}"
echo ""
echo "2. Search memory:"
echo -e "   ${YELLOW}.agentic/scripts/bash/memory-query.sh \"your query\"${NC}"
echo ""
echo "3. Add a reflection:"
echo -e "   ${YELLOW}python3 .agentic/scripts/memory-cli.py reflect${NC}"
echo ""
echo "4. Capture a spec-kit artifact:"
echo -e "   ${YELLOW}.agentic/scripts/bash/memory-capture.sh --feature-dir specs/001-... --type spec --file specs/001-.../spec.md${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "   ${YELLOW}cat README.md${NC}"
echo ""
echo -e "${GREEN}Happy coding with institutional memory! 🧠✨${NC}"
echo ""
