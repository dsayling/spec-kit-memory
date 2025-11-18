#!/usr/bin/env bash
#
# Post-Command Hook for /speckit.plan
#
# Copy this code to the END of your .claude/commands/speckit.plan.md file
# to automatically capture plans and extract decisions.
#
# This hook:
# - Runs AFTER the plan.md file is created
# - Automatically extracts design decisions from plan.md
# - Captures research.md if it exists
# - Fails gracefully if memory system not installed
#

# === PASTE THIS AT THE END OF YOUR /speckit.plan COMMAND ===

# Optional: Capture to memory system (if installed)
if [[ -f "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" ]]; then
  echo ""
  echo "📝 Capturing plan to memory system..."

  # Capture plan.md (extracts decisions automatically)
  "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" \
    --feature-dir "$FEATURE_DIR" \
    --type plan \
    --file "$PLAN_FILE" || {
    echo "⚠️  Memory capture failed (non-fatal)"
  }

  # Capture research.md if it exists
  if [[ -f "$RESEARCH_FILE" ]]; then
    echo "📝 Capturing research to memory system..."
    "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" \
      --feature-dir "$FEATURE_DIR" \
      --type research \
      --file "$RESEARCH_FILE" || {
      echo "⚠️  Research capture failed (non-fatal)"
    }
  fi

  # Show what was captured
  echo ""
  echo "✅ Plan captured to memory"
  echo "   Decisions extracted and indexed for future reference"
fi

# === END HOOK CODE ===

# Variables you need to define before this hook:
# - $GIT_ROOT: Path to git repository root
# - $FEATURE_DIR: Path to feature directory (e.g., specs/003-feature-name)
# - $PLAN_FILE: Path to plan.md file
# - $RESEARCH_FILE: Path to research.md file (optional)

# Example variable definitions:
# GIT_ROOT="$(git rev-parse --show-toplevel)"
# FEATURE_DIR="specs/${FEATURE_NUMBER}-${FEATURE_SLUG}"
# PLAN_FILE="${FEATURE_DIR}/plan.md"
# RESEARCH_FILE="${FEATURE_DIR}/research.md"
