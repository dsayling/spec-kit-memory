#!/usr/bin/env bash
#
# Pre-Command Context Injection for /speckit.plan
#
# Copy this code to the BEGINNING of your .claude/commands/speckit.plan.md file
# (before calling the agent) to inject relevant memory context.
#
# This hook:
# - Runs BEFORE generating the plan
# - Searches memory for similar features
# - Finds relevant decisions by category
# - Recommends proven patterns
# - Injects context into agent prompt
#

# === PASTE THIS BEFORE YOUR AGENT CALL IN /speckit.plan ===

# Optional: Query memory for context (if installed)
if [[ -f "$GIT_ROOT/.agentic/scripts/memory-cli.py" ]]; then
  echo ""
  echo "🧠 Querying memory for relevant context..."

  MEMORY_CLI="python3 $GIT_ROOT/.agentic/scripts/memory-cli.py"

  # 1. Find similar features
  echo "   → Searching for similar features..."
  SIMILAR_FEATURES=$($MEMORY_CLI search "$FEATURE_NAME" --type feature --limit 3 2>/dev/null || echo "")

  # 2. Get relevant decisions by common categories
  echo "   → Retrieving relevant decisions..."
  TECH_DECISIONS=$($MEMORY_CLI search "" --type decision --category technology --limit 5 2>/dev/null || echo "")
  ARCH_DECISIONS=$($MEMORY_CLI search "" --type decision --category architecture --limit 5 2>/dev/null || echo "")

  # 3. Get pattern recommendations
  echo "   → Finding applicable patterns..."
  PATTERNS=$($MEMORY_CLI patterns --recommend-for "$FEATURE_NAME" 2>/dev/null || echo "")

  # 4. Get high-impact reflections
  echo "   → Retrieving key lessons learned..."
  REFLECTIONS=$($MEMORY_CLI search "" --type reflection --limit 5 2>/dev/null || echo "")

  # Build memory context summary
  MEMORY_CONTEXT=""

  if [[ -n "$SIMILAR_FEATURES" ]]; then
    MEMORY_CONTEXT+="## Similar Features (from memory)

$SIMILAR_FEATURES

"
  fi

  if [[ -n "$TECH_DECISIONS" ]] || [[ -n "$ARCH_DECISIONS" ]]; then
    MEMORY_CONTEXT+="## Past Decisions (from memory)

### Technology Decisions
$TECH_DECISIONS

### Architecture Decisions
$ARCH_DECISIONS

"
  fi

  if [[ -n "$PATTERNS" ]]; then
    MEMORY_CONTEXT+="## Recommended Patterns (from memory)

$PATTERNS

"
  fi

  if [[ -n "$REFLECTIONS" ]]; then
    MEMORY_CONTEXT+="## Key Lessons Learned (from memory)

$REFLECTIONS

"
  fi

  if [[ -n "$MEMORY_CONTEXT" ]]; then
    echo ""
    echo "✅ Memory context retrieved"
    echo "   Including: similar features, decisions, patterns, and reflections"
    echo ""

    # Save to temporary file for agent to read
    MEMORY_CONTEXT_FILE="$FEATURE_DIR/.memory-context.md"
    echo "$MEMORY_CONTEXT" > "$MEMORY_CONTEXT_FILE"

    # Update agent prompt to include memory context
    AGENT_PROMPT="You are planning a feature: $FEATURE_NAME

📚 RELEVANT CONTEXT FROM MEMORY:
I have retrieved relevant context from past features. Please review this before planning:

$(cat "$MEMORY_CONTEXT_FILE")

Now, create a comprehensive plan for the new feature following spec-kit guidelines.
Use the memory context to:
- Maintain architectural consistency with past decisions
- Reuse proven patterns where applicable
- Avoid repeating past mistakes
- Build on successful approaches

$ORIGINAL_AGENT_PROMPT"

    echo "🧠 Agent will receive memory context (~${#MEMORY_CONTEXT} characters)"
  else
    echo "   (No relevant context found in memory)"
  fi
else
  # Silent if memory system not installed
  :
fi

# === END HOOK CODE ===

# Variables you need to define before this hook:
# - $GIT_ROOT: Path to git repository root
# - $FEATURE_DIR: Path to feature directory
# - $FEATURE_NAME: Name/description of the feature being planned
# - $ORIGINAL_AGENT_PROMPT: Your original agent prompt (will be enhanced)

# After this hook:
# - Use $AGENT_PROMPT (enhanced with memory) instead of $ORIGINAL_AGENT_PROMPT
# - The agent will receive relevant context from past features

# Example usage:
# FEATURE_NAME="User Authentication System"
# ORIGINAL_AGENT_PROMPT="Create a plan for implementing user authentication..."
#
# # Insert pre-plan context injection hook here
# # ...hook code...
#
# # Call agent with enhanced prompt
# claude --prompt "$AGENT_PROMPT"

# Cleanup (add at end of command):
# rm -f "$FEATURE_DIR/.memory-context.md"
