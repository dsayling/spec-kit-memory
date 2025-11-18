# Spec-Kit Memory System - Integration Roadmap

## Philosophy: Zero Disruption Add-On

The memory system is designed as a **passive observer** that sits alongside your existing spec-kit workflow. You don't need to change anything about how you use spec-kit - the memory system just makes your past work searchable and reusable.

## Current State: Manual Capture (v0.1)

**Status**: ✅ Complete - Ready to Use

The memory system is currently a **standalone tool** that you invoke manually after using spec-kit commands. No modifications to spec-kit required.

### How It Works Now

```bash
# Your existing workflow (unchanged)
/speckit.specify "Add user dashboard"
/speckit.plan
/speckit.tasks
/speckit.implement

# NEW: After each step, optionally capture to memory
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/003-user-dashboard \
  --type spec \
  --file specs/003-user-dashboard/spec.md
```

### Benefits
- ✅ **Zero disruption**: Your spec-kit workflow stays exactly the same
- ✅ **Optional**: Capture only when you want to
- ✅ **No dependencies**: Works alongside spec-kit without integration
- ✅ **Immediate value**: Search past decisions and patterns right away

## Future Roadmap

### Phase 1: Post-Command Hooks (v0.2) - Optional Integration

**Goal**: Automatically capture artifacts after spec-kit commands complete

**Approach**: Add optional hooks to your existing spec-kit commands

**Example Integration** (you control when/if to add this):

```bash
# In your /speckit.specify command file
# ... existing spec-kit logic ...

# At the very end, add:
if [[ -f "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" ]]; then
  "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" \
    --feature-dir "$FEATURE_DIR" \
    --type spec \
    --file "$SPEC_FILE" || true  # Don't fail if capture fails
fi
```

**Impact**:
- ✅ Automatic capture without manual steps
- ✅ Still zero disruption (hook only runs if memory system installed)
- ✅ Graceful degradation (command succeeds even if capture fails)

**Timeline**: Add when you're comfortable with the memory system

### Phase 2: Context Injection (v0.3) - Smart Suggestions

**Goal**: Before generating specs/plans, search memory for relevant context

**Approach**: Add memory queries at the start of spec-kit commands

**Example Integration**:

```bash
# In your /speckit.plan command
# Before generating plan.md, add:

if [[ -f "$GIT_ROOT/.agentic/scripts/bash/memory-query.sh" ]]; then
  echo "🧠 Checking memory for relevant patterns..."
  MEMORY_CONTEXT=$("$GIT_ROOT/.agentic/scripts/bash/memory-query.sh" \
    "$FEATURE_NAME" --type decision --category technology --limit 5)

  # Include in agent prompt
  AGENT_PROMPT="$AGENT_PROMPT\n\nRelevant past decisions:\n$MEMORY_CONTEXT"
fi
```

**Impact**:
- ✅ Agents see relevant past decisions during planning
- ✅ Architectural consistency across features
- ✅ Faster planning (no need to research what you've already done)

**Timeline**: Add after accumulating 5-10 features in memory

### Phase 3: New Slash Commands (v0.4) - Explicit Retrieval

**Goal**: Add memory-specific commands for explicit knowledge retrieval

**New Commands**:
- `/speckit.recall <query>` - Search memory
- `/speckit.reflect <message>` - Add reflection
- `/speckit.memory-status` - View statistics

**Example**:

```bash
# .claude/commands/speckit.recall.md
Search the spec-kit memory database for relevant decisions, patterns, and reflections.

Usage: /speckit.recall "RBAC implementation"

The agent will search memory and present ranked results.
```

**Impact**:
- ✅ Explicit knowledge retrieval when needed
- ✅ Ad-hoc reflection capture
- ✅ Memory health monitoring

**Timeline**: Add when memory database has meaningful content

### Phase 4: Pattern Detection (v0.5) - Learning System

**Goal**: Automatically detect recurring patterns across features

**Approach**: Analyze completed tasks to identify reusable patterns

**What Gets Detected**:
- Code patterns (RBAC middleware, CRUD endpoints, etc.)
- Architecture patterns (layered architecture, event-driven, etc.)
- Testing patterns (E2E test structures, mocking strategies, etc.)
- Workflow patterns (model→schema→API→tests sequences)

**Impact**:
- ✅ Automatic pattern library building
- ✅ Pattern recommendations during planning
- ✅ Best practices emerge organically

**Timeline**: After 10+ completed features

## Migration Path: Zero to Full Integration

### Week 1: Manual Use (No spec-kit changes)
```bash
# Install
./setup-memory.sh

# Use spec-kit normally
/speckit.specify "Feature X"
/speckit.plan

# Manually capture
.agentic/scripts/bash/memory-capture.sh --feature-dir specs/001-... --type spec --file spec.md
.agentic/scripts/bash/memory-capture.sh --feature-dir specs/001-... --type plan --file plan.md

# Search when needed
python3 .agentic/scripts/memory-cli.py search "authentication"
```

**Effort**: 30 seconds per artifact to capture
**Value**: Searchable knowledge base

### Week 2-4: Build Memory Database (Still manual)
```bash
# Continue spec-kit workflow unchanged
# Capture artifacts after each feature
# Search before planning new features

python3 .agentic/scripts/memory-cli.py search "similar to: $NEW_FEATURE"
```

**Effort**: Same as Week 1
**Value**: Growing knowledge base, patterns emerging

### Month 2: Add Post-Command Hooks (Optional)
```bash
# Modify your spec-kit commands to auto-capture
# Edit .claude/commands/speckit.specify.md
# Add memory-capture.sh call at the end
```

**Effort**: 5 minutes per command to add hook
**Value**: Zero-effort capture, full automation

### Month 3+: Context Injection (Optional)
```bash
# Add memory queries before planning
# Inject relevant decisions into agent prompts
```

**Effort**: 10-15 minutes per command to add queries
**Value**: Informed planning, architectural consistency

## Key Principle: Gradual Adoption

```
┌─────────────────────────────────────────────────────────┐
│ Spec-Kit Workflow (Unchanged)                           │
│                                                          │
│  /speckit.specify → /speckit.plan → /speckit.tasks     │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │
                         │ Optional capture
                         │
┌─────────────────────────────────────────────────────────┐
│ Memory System (Passive Observer)                        │
│                                                          │
│  .agentic/memory/memory.db  ← Captures knowledge        │
│  memory-cli.py              ← Search when needed        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**You control the integration level:**
- Level 0: No integration (memory-cli.py as standalone tool)
- Level 1: Manual capture after commands
- Level 2: Automatic capture via hooks
- Level 3: Context injection before commands
- Level 4: Full learning system with patterns

## Recommended Adoption Strategy

### For New Projects (Starting Fresh)
1. Install memory system during project setup
2. Use manual capture for first 2-3 features
3. Add post-command hooks once comfortable
4. Enable context injection after 5+ features

### For Existing Projects (Retrofitting)
1. Install memory system
2. Capture existing specs/plans for 1-2 completed features
3. Use manual capture for new features
4. Add hooks when you see value in automation

### For Experimentation (Trying It Out)
1. Install in a test repository
2. Capture 1-2 dummy features
3. Test search functionality
4. Decide if valuable enough to integrate

## What Stays The Same

**No changes required to:**
- Spec-kit commands (they work exactly as before)
- Spec-kit templates
- Your development workflow
- Your team's processes
- Constitutional compliance (still enforced by spec-kit)

**Memory system is purely additive:**
- Adds `.agentic/memory/` directory
- Adds CLI tools in `.agentic/scripts/`
- Optionally captures artifacts (you control when)
- Optionally provides context (you control what)

## What Changes (Only If You Want)

**Optional changes you can make:**
- Add capture hooks to spec-kit commands (automation)
- Add memory queries before planning (context injection)
- Add new slash commands for recall/reflect (explicit retrieval)
- Configure capture preferences in `memory-config.yaml`

## Success Criteria

You'll know the memory system is valuable when:

1. **You search before planning**: "What did we do for authentication in feature 003?"
2. **You reference past decisions**: "We chose FastAPI because of X (feature 003, decision #42)"
3. **You reuse patterns**: "Use the RBAC pattern from feature 003"
4. **You avoid mistakes**: "Feature 007 had flaky E2E tests - use explicit waits"
5. **You capture reflections**: "This worked well / This was a mistake - let's remember it"

## Measuring Impact

**Before Memory System:**
```
/speckit.plan
↓
Agent researches from scratch
↓
Generates plan (may repeat past mistakes)
↓
8-10K tokens of conversation
```

**After Memory System:**
```
/speckit.plan
↓
Agent checks memory for similar features
↓
"Feature 003 used FastAPI + PostgreSQL successfully"
↓
Generates informed plan
↓
5-7K tokens of conversation (30% reduction)
```

**ROI**:
- 30 seconds to capture artifact
- 2-5 minutes saved per planning session
- Fewer architectural inconsistencies
- Faster onboarding for new features

## Timeline Summary

| Phase | What | Integration Level | Timeline |
|-------|------|-------------------|----------|
| **v0.1** (Current) | Manual capture & search | Level 1 - Manual | ✅ Ready now |
| **v0.2** | Auto-capture hooks | Level 2 - Hooks | When comfortable (Week 2-4) |
| **v0.3** | Context injection | Level 3 - Context | After 5+ features (Month 2) |
| **v0.4** | Slash commands | Level 3 - Context | After meaningful content (Month 2) |
| **v0.5** | Pattern detection | Level 4 - Learning | After 10+ features (Month 3+) |

## Getting Started Today

**Minimal path to value** (10 minutes):

```bash
# 1. Install (2 minutes)
./setup-memory.sh

# 2. Capture one existing spec (30 seconds)
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/001-existing-feature \
  --type spec \
  --file specs/001-existing-feature/spec.md

# 3. Search it (30 seconds)
python3 .agentic/scripts/memory-cli.py search "your feature name"

# 4. View stats (30 seconds)
python3 .agentic/scripts/memory-cli.py stats
```

That's it! You now have institutional memory. Everything else is optional.

---

**Bottom Line**: The memory system is designed to be **invisible until useful**. Use as much or as little as you want. Your spec-kit workflow stays exactly the same.
