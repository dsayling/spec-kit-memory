#!/usr/bin/env bash
#
# Post-Command Hook for /speckit.tasks
#
# Copy this code to the END of your .claude/commands/speckit.tasks.md file
# to automatically capture tasks and track completion patterns.
#
# This hook:
# - Runs AFTER the tasks.md file is created/updated
# - Tracks completed tasks for pattern detection
# - Updates task completion status
# - Fails gracefully if memory system not installed
#

# === PASTE THIS AT THE END OF YOUR /speckit.tasks COMMAND ===

# Optional: Capture to memory system (if installed)
if [[ -f "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" ]]; then
  echo ""
  echo "📝 Capturing tasks to memory system..."

  # Capture tasks.md (extracts completed tasks automatically)
  "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" \
    --feature-dir "$FEATURE_DIR" \
    --type tasks \
    --file "$TASKS_FILE" || {
    echo "⚠️  Memory capture failed (non-fatal)"
  }

  # Show completion stats
  COMPLETED_COUNT=$(grep -c "^\- \[X\]" "$TASKS_FILE" 2>/dev/null || echo "0")
  TOTAL_COUNT=$(grep -c "^\- \[[X ]\]" "$TASKS_FILE" 2>/dev/null || echo "0")

  echo ""
  echo "✅ Tasks captured to memory"
  echo "   Progress: $COMPLETED_COUNT/$TOTAL_COUNT tasks completed"
  echo "   Patterns tracked for future features"
fi

# === END HOOK CODE ===

# Variables you need to define before this hook:
# - $GIT_ROOT: Path to git repository root
# - $FEATURE_DIR: Path to feature directory (e.g., specs/003-feature-name)
# - $TASKS_FILE: Path to tasks.md file

# Example variable definitions:
# GIT_ROOT="$(git rev-parse --show-toplevel)"
# FEATURE_DIR="specs/${FEATURE_NUMBER}-${FEATURE_SLUG}"
# TASKS_FILE="${FEATURE_DIR}/tasks.md"
