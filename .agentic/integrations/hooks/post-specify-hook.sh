#!/usr/bin/env bash
#
# Post-Command Hook for /speckit.specify
#
# Copy this code to the END of your .claude/commands/speckit.specify.md file
# (or wherever your specify command is defined) to automatically capture specs.
#
# This hook:
# - Runs AFTER the spec.md file is created
# - Captures feature metadata and description
# - Fails gracefully if memory system not installed
# - Doesn't break the spec-kit command if capture fails
#

# === PASTE THIS AT THE END OF YOUR /speckit.specify COMMAND ===

# Optional: Capture to memory system (if installed)
if [[ -f "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" ]]; then
  echo ""
  echo "📝 Capturing spec to memory system..."

  # Run capture (|| true ensures spec-kit command doesn't fail if capture fails)
  "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" \
    --feature-dir "$FEATURE_DIR" \
    --type spec \
    --file "$SPEC_FILE" || {
    echo "⚠️  Memory capture failed (non-fatal)"
  }
else
  # Silent if memory system not installed (optional feature)
  :
fi

# === END HOOK CODE ===

# Variables you need to define before this hook:
# - $GIT_ROOT: Path to git repository root
# - $FEATURE_DIR: Path to feature directory (e.g., specs/003-feature-name)
# - $SPEC_FILE: Path to spec.md file

# Example variable definitions (adjust to match your spec-kit command):
# GIT_ROOT="$(git rev-parse --show-toplevel)"
# FEATURE_DIR="specs/${FEATURE_NUMBER}-${FEATURE_SLUG}"
# SPEC_FILE="${FEATURE_DIR}/spec.md"
