# Spec-Kit Memory System - Integration Guide

This guide shows you how to integrate the memory system with your existing spec-kit workflow at various levels.

## Overview

The memory system provides **optional integration points** that you can adopt gradually:

1. **Post-command hooks** - Automatic capture after spec-kit commands
2. **Pre-command context injection** - Memory queries before planning
3. **Slash commands** - Explicit memory operations (`/memory.recall`, etc.)

**All integrations are optional and non-breaking.** Your spec-kit workflow continues to work whether or not you integrate.

---

## Integration Level 1: Post-Command Hooks

**Goal**: Automatically capture artifacts after spec-kit commands complete

**Effort**: 2-5 minutes per command

**Value**: Zero-effort knowledge capture

### Step 1: Add Hook to `/speckit.specify`

1. Locate your `/speckit.specify` command file (usually `.claude/commands/speckit.specify.md`)

2. At the **very end** of the file, add this code:

```bash
# Optional: Capture to memory system (if installed)
if [[ -f "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" ]]; then
  echo ""
  echo "📝 Capturing spec to memory system..."

  "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" \
    --feature-dir "$FEATURE_DIR" \
    --type spec \
    --file "$SPEC_FILE" || {
    echo "⚠️  Memory capture failed (non-fatal)"
  }
fi
```

3. Ensure these variables are defined in your command:
   - `$GIT_ROOT` - Path to git repository root
   - `$FEATURE_DIR` - Path to feature directory (e.g., `specs/003-feature-name`)
   - `$SPEC_FILE` - Path to `spec.md` file

**Example variable definitions** (adjust to match your command):
```bash
GIT_ROOT="$(git rev-parse --show-toplevel)"
FEATURE_DIR="specs/${FEATURE_NUMBER}-${FEATURE_SLUG}"
SPEC_FILE="${FEATURE_DIR}/spec.md"
```

**Full example file**: See `.agentic/integrations/hooks/post-specify-hook.sh`

### Step 2: Add Hook to `/speckit.plan`

Add this to the end of your `/speckit.plan` command:

```bash
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

  echo ""
  echo "✅ Plan captured to memory"
  echo "   Decisions extracted and indexed for future reference"
fi
```

**Required variables**:
- `$PLAN_FILE` - Path to `plan.md`
- `$RESEARCH_FILE` - Path to `research.md` (optional)

**Full example file**: See `.agentic/integrations/hooks/post-plan-hook.sh`

### Step 3: Add Hook to `/speckit.tasks`

Add this to the end of your `/speckit.tasks` command:

```bash
# Optional: Capture to memory system (if installed)
if [[ -f "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" ]]; then
  echo ""
  echo "📝 Capturing tasks to memory system..."

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
fi
```

**Required variables**:
- `$TASKS_FILE` - Path to `tasks.md`

**Full example file**: See `.agentic/integrations/hooks/post-tasks-hook.sh`

### Testing Post-Command Hooks

After adding hooks, test them:

```bash
# Run your spec-kit command
/speckit.specify "Test Feature"

# You should see:
# 📝 Capturing spec to memory system...
# ✅ Saved artifact: spec (ID: 1)
# ✅ Created feature 001: Test Feature

# Verify capture
python3 .agentic/scripts/memory-cli.py stats
```

---

## Integration Level 2: Pre-Command Context Injection

**Goal**: Query memory before planning to inject relevant context

**Effort**: 10-15 minutes per command

**Value**: Informed planning with architectural consistency

**Prerequisites**: 5+ features in memory database

### Add Context Injection to `/speckit.plan`

1. Locate your `/speckit.plan` command file

2. **Before** you call the agent to generate the plan, add this code:

```bash
# Optional: Query memory for context (if installed)
if [[ -f "$GIT_ROOT/.agentic/scripts/memory-cli.py" ]]; then
  echo ""
  echo "🧠 Querying memory for relevant context..."

  MEMORY_CLI="python3 $GIT_ROOT/.agentic/scripts/memory-cli.py"

  # Find similar features
  echo "   → Searching for similar features..."
  SIMILAR_FEATURES=$($MEMORY_CLI search "$FEATURE_NAME" --type feature --limit 3 2>/dev/null || echo "")

  # Get relevant decisions
  echo "   → Retrieving relevant decisions..."
  TECH_DECISIONS=$($MEMORY_CLI search "" --type decision --category technology --limit 5 2>/dev/null || echo "")
  ARCH_DECISIONS=$($MEMORY_CLI search "" --type decision --category architecture --limit 5 2>/dev/null || echo "")

  # Get pattern recommendations
  echo "   → Finding applicable patterns..."
  PATTERNS=$($MEMORY_CLI patterns --recommend-for "$FEATURE_NAME" 2>/dev/null || echo "")

  # Build memory context
  MEMORY_CONTEXT=""

  if [[ -n "$SIMILAR_FEATURES" ]]; then
    MEMORY_CONTEXT+="## Similar Features

$SIMILAR_FEATURES

"
  fi

  if [[ -n "$TECH_DECISIONS" ]] || [[ -n "$ARCH_DECISIONS" ]]; then
    MEMORY_CONTEXT+="## Past Decisions

### Technology
$TECH_DECISIONS

### Architecture
$ARCH_DECISIONS

"
  fi

  if [[ -n "$PATTERNS" ]]; then
    MEMORY_CONTEXT+="## Recommended Patterns

$PATTERNS

"
  fi

  if [[ -n "$MEMORY_CONTEXT" ]]; then
    echo "✅ Memory context retrieved"

    # Save to file for agent
    MEMORY_CONTEXT_FILE="$FEATURE_DIR/.memory-context.md"
    echo "$MEMORY_CONTEXT" > "$MEMORY_CONTEXT_FILE"

    # Enhance agent prompt
    AGENT_PROMPT="You are planning: $FEATURE_NAME

📚 RELEVANT CONTEXT FROM MEMORY:

$(cat "$MEMORY_CONTEXT_FILE")

Now create a plan that maintains consistency with past decisions and reuses proven patterns.

$ORIGINAL_AGENT_PROMPT"

    echo "🧠 Agent will receive $(wc -l < "$MEMORY_CONTEXT_FILE") lines of context"
  fi
fi
```

3. Update your agent call to use `$AGENT_PROMPT` instead of the original prompt

4. Clean up at the end:
```bash
# Cleanup
rm -f "$FEATURE_DIR/.memory-context.md"
```

**Required variables**:
- `$FEATURE_NAME` - Name/description of the feature being planned
- `$ORIGINAL_AGENT_PROMPT` - Your original agent prompt (will be enhanced)

**Full example file**: See `.agentic/integrations/hooks/pre-plan-context-injection.sh`

### Testing Context Injection

```bash
# Ensure you have 5+ features in memory
python3 .agentic/scripts/memory-cli.py stats

# Run planning with context injection
/speckit.plan

# You should see:
# 🧠 Querying memory for relevant context...
#    → Searching for similar features...
#    → Retrieving relevant decisions...
#    → Finding applicable patterns...
# ✅ Memory context retrieved
# 🧠 Agent will receive 45 lines of context

# The generated plan should reference past decisions
```

---

## Integration Level 3: Slash Commands

**Goal**: Add explicit memory operations as slash commands

**Effort**: 5 minutes (copy files)

**Value**: Direct memory access during development

### Install Slash Commands

1. Copy slash command files to your `.claude/commands/` directory:

```bash
# Copy all memory slash commands
cp .agentic/integrations/slash-commands/memory.*.md .claude/commands/

# Or copy individually
cp .agentic/integrations/slash-commands/memory.recall.md .claude/commands/
cp .agentic/integrations/slash-commands/memory.reflect.md .claude/commands/
cp .agentic/integrations/slash-commands/memory.status.md .claude/commands/
```

2. Verify installation:

```bash
# List available commands
ls .claude/commands/memory.*

# Should show:
# .claude/commands/memory.recall.md
# .claude/commands/memory.reflect.md
# .claude/commands/memory.status.md
```

### Using Slash Commands

#### `/memory.recall` - Search Memory

Search for relevant decisions, patterns, and reflections:

```
/memory.recall RBAC implementation patterns
/memory.recall authentication decisions
/memory.recall similar to: user dashboard
```

The agent will:
- Search the memory database
- Present ranked results by relevance
- Group by type (decisions, patterns, reflections)
- Provide actionable recommendations

#### `/memory.reflect` - Add Reflection

Capture lessons learned, successes, or challenges:

```
/memory.reflect
# Agent will prompt for:
# - Type (success/challenge/lesson/antipattern/recommendation)
# - Impact (high/medium/low)
# - Title
# - Description
# - Category
```

Or provide details directly in conversation:
```
/memory.reflect
I learned that using JSONB columns in PostgreSQL is perfect for flexible metadata fields
```

#### `/memory.status` - View Statistics

Check memory database health:

```
/memory.status
```

The agent will:
- Show database statistics
- Display knowledge coverage
- List top patterns
- Identify knowledge gaps
- Suggest actions

### Slash Command Examples

**Example 1: Before Planning**
```
/memory.recall authentication patterns
# Review past authentication approaches
# Then plan new feature with that context
```

**Example 2: After Implementation**
```
/memory.reflect
I want to capture that FastAPI dependency injection worked really well for RBAC middleware
```

**Example 3: Monthly Review**
```
/memory.status
# Review knowledge base health
# Identify gaps
# Plan documentation improvements
```

---

## Complete Integration Example

Here's what a fully integrated spec-kit workflow looks like:

### 1. Specify a Feature

```bash
/speckit.specify "User Notifications System"

# With post-command hook:
# → Spec.md created
# 📝 Capturing spec to memory system...
# ✅ Created feature 013: User Notifications System
```

### 2. Plan the Feature

```bash
/speckit.plan

# With context injection:
# 🧠 Querying memory for relevant context...
#    → Searching for similar features...
#    → Found: Feature 007 (Email Integration)
#    → Retrieving relevant decisions...
#    → Found: 12 relevant technology decisions
#    → Finding applicable patterns...
#    → Recommended: email-queue-pattern, notification-template-pattern
# ✅ Memory context retrieved
# 🧠 Agent will receive 52 lines of context
#
# → Plan generated with context from past features
# 📝 Capturing plan to memory system...
# ✅ Extracted 8 decision(s) from plan
```

### 3. Create Tasks

```bash
/speckit.tasks

# With post-command hook:
# → Tasks.md created
# 📝 Capturing tasks to memory system...
# ✅ Tasks captured to memory
#    Progress: 0/24 tasks completed
```

### 4. During Implementation

```bash
# Search for implementation patterns
/memory.recall email queue implementation

# Agent shows:
# Found pattern: email-queue-pattern (used 3x, 100% success)
# From Features: 007, 009, 011
# Implementation: Use Celery with Redis backend...
```

### 5. After Completion

```bash
# Add reflection
/memory.reflect

# Agent prompts:
# "I'll help you capture this reflection..."
# You describe the success/challenge
# Agent captures it to memory
```

### 6. Monthly Review

```bash
/memory.status

# Agent shows:
# 📊 Memory System Status
# - 13 features tracked
# - 156 decisions recorded
# - 15 patterns identified
# - Suggestions: Add more security reflections
```

---

## Integration Checklist

Use this checklist to track your integration progress:

### Level 1: Post-Command Hooks
- [ ] Add hook to `/speckit.specify`
- [ ] Add hook to `/speckit.plan`
- [ ] Add hook to `/speckit.tasks`
- [ ] Test automatic capture
- [ ] Verify in `memory-cli.py stats`

### Level 2: Context Injection
- [ ] Wait until 5+ features in memory
- [ ] Add context injection to `/speckit.plan`
- [ ] Test memory context retrieval
- [ ] Verify enhanced agent prompts
- [ ] Review generated plans for consistency

### Level 3: Slash Commands
- [ ] Copy `memory.recall.md` to `.claude/commands/`
- [ ] Copy `memory.reflect.md` to `.claude/commands/`
- [ ] Copy `memory.status.md` to `.claude/commands/`
- [ ] Test `/memory.recall`
- [ ] Test `/memory.reflect`
- [ ] Test `/memory.status`

### Ongoing
- [ ] Run `/memory.status` monthly
- [ ] Add 2-3 reflections per completed feature
- [ ] Backup database weekly
- [ ] Review and update patterns quarterly

---

## Troubleshooting

### Hooks Not Running

**Problem**: Post-command hooks don't execute

**Check**:
1. Are the hooks at the **end** of the command file?
2. Are the required variables defined?
3. Is the memory system installed? (`ls .agentic/scripts/bash/memory-capture.sh`)

**Test**:
```bash
# Manually test the hook
GIT_ROOT="$(git rev-parse --show-toplevel)"
FEATURE_DIR="specs/001-test"
SPEC_FILE="$FEATURE_DIR/spec.md"

.agentic/scripts/bash/memory-capture.sh \
  --feature-dir "$FEATURE_DIR" \
  --type spec \
  --file "$SPEC_FILE"
```

### Context Injection Returns Nothing

**Problem**: Memory context is empty

**Causes**:
- Not enough features in database (need 5+)
- Feature name doesn't match existing features
- No decisions in relevant categories

**Check**:
```bash
# How many features?
python3 .agentic/scripts/memory-cli.py stats

# Manual search
python3 .agentic/scripts/memory-cli.py search "your feature name"
```

### Slash Commands Not Found

**Problem**: `/memory.recall` doesn't work

**Check**:
1. Are files in `.claude/commands/`?
   ```bash
   ls .claude/commands/memory.*
   ```

2. Do they have `.md` extension?

3. Do they have frontmatter?
   ```markdown
   ---
   description: ...
   ---
   ```

---

## Best Practices

### 1. Start Simple

Begin with Level 1 (post-command hooks). Don't jump to context injection immediately.

**Week 1-2**: Manual capture or post-command hooks
**Week 3-4**: Continue hooks, accumulate knowledge
**Month 2+**: Add context injection once you have 5+ features

### 2. Verify Capture

After adding hooks, always verify:
```bash
python3 .agentic/scripts/memory-cli.py stats
```

### 3. Gradual Enhancement

Don't add all integrations at once:
1. Add post-specify hook → test → commit
2. Add post-plan hook → test → commit
3. Add post-tasks hook → test → commit
4. Add context injection → test → commit
5. Add slash commands → test → commit

### 4. Make Hooks Non-Fatal

Always use `|| true` or error handling:
```bash
capture.sh ... || {
  echo "⚠️  Capture failed (non-fatal)"
}
```

This ensures spec-kit commands succeed even if memory capture fails.

### 5. Document Variables

At the top of your spec-kit commands, document required variables:
```bash
# Required for memory integration:
# - GIT_ROOT: Git repository root
# - FEATURE_DIR: Path to feature directory
# - SPEC_FILE: Path to spec.md
```

---

## Example Integration Timeline

**Day 1**: Install memory system, add post-specify hook
**Day 2**: Add post-plan hook, capture first feature
**Day 3**: Add post-tasks hook
**Week 2**: Complete 2-3 features with automatic capture
**Week 3**: Test `/memory.recall`, search past work
**Week 4**: Add first reflections via `/memory.reflect`
**Month 2**: Add context injection after 5+ features
**Month 3+**: Patterns emerge, compound learning begins

---

## Support

**Example files**:
- `.agentic/integrations/hooks/` - Ready-to-copy hook code
- `.agentic/integrations/slash-commands/` - Slash command definitions

**Documentation**:
- `README.md` - Overview and basic usage
- `ROADMAP.md` - Integration levels and timeline
- `QUICKSTART.md` - 5-minute getting started
- `INTEGRATION_GUIDE.md` - This file

**Testing**:
```bash
# Verify memory system
python3 .agentic/scripts/memory-cli.py stats

# Test capture
.agentic/scripts/bash/memory-capture.sh --feature-dir specs/001-test --type spec --file spec.md

# Test search
.agentic/scripts/bash/memory-query.sh "test query"
```

---

**The memory system is designed to integrate gradually. Take your time, start simple, and add complexity as you see value.**
