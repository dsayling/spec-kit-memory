# Spec-Kit Memory - Integration Examples

This directory contains ready-to-use integration code for connecting the memory system with your spec-kit workflow.

## Directory Structure

```
.agentic/integrations/
├── hooks/              # Post-command and pre-command hooks
└── slash-commands/     # Slash command definitions
```

## Hooks

Copy-paste ready code for automatic memory capture and context injection.

### Post-Command Hooks (Automatic Capture)

**What**: Capture artifacts automatically after spec-kit commands complete
**When**: After implementing Level 1 (Manual Capture) and seeing value
**Effort**: 2-5 minutes per command

#### Files:
- **`post-specify-hook.sh`** - Add to end of `/speckit.specify` to auto-capture specs
- **`post-plan-hook.sh`** - Add to end of `/speckit.plan` to auto-capture plans and extract decisions
- **`post-tasks-hook.sh`** - Add to end of `/speckit.tasks` to auto-capture task completion

#### Usage:
1. Open your spec-kit command file (e.g., `.claude/commands/speckit.specify.md`)
2. Scroll to the **end** of the file
3. Copy the code from the appropriate hook file
4. Paste at the end
5. Test with your next spec-kit command

#### Example:
```bash
# Your existing /speckit.specify command
# ... spec-kit logic ...

# === Paste hook code here ===
if [[ -f "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" ]]; then
  echo "📝 Capturing spec to memory system..."
  "$GIT_ROOT/.agentic/scripts/bash/memory-capture.sh" \
    --feature-dir "$FEATURE_DIR" \
    --type spec \
    --file "$SPEC_FILE" || {
    echo "⚠️  Memory capture failed (non-fatal)"
  }
fi
```

### Pre-Command Hooks (Context Injection)

**What**: Query memory before planning to inject relevant context
**When**: After accumulating 5+ features in memory
**Effort**: 10-15 minutes per command

#### Files:
- **`pre-plan-context-injection.sh`** - Add to beginning of `/speckit.plan` to query memory

#### Usage:
1. Open your `/speckit.plan` command file
2. Find where you call the agent to generate the plan
3. **Before** that call, paste the context injection code
4. Update your agent call to use the enhanced `$AGENT_PROMPT`

#### Example:
```bash
# Your /speckit.plan command

# === Paste context injection here (BEFORE agent call) ===
if [[ -f "$GIT_ROOT/.agentic/scripts/memory-cli.py" ]]; then
  echo "🧠 Querying memory for relevant context..."
  # ... context injection code ...
  AGENT_PROMPT="... enhanced with memory context ..."
fi

# Now call agent with enhanced prompt
agent_call "$AGENT_PROMPT"
```

## Slash Commands

Slash command definitions for explicit memory operations.

### Files:
- **`memory.recall.md`** - Search memory for decisions, patterns, reflections
- **`memory.reflect.md`** - Add reflections about successes, challenges, lessons
- **`memory.status.md`** - View memory database statistics

### Installation:

Copy to your `.claude/commands/` directory:

```bash
# From spec-kit-memory root directory
cp .agentic/integrations/slash-commands/memory.*.md .claude/commands/

# Or copy individually
cp .agentic/integrations/slash-commands/memory.recall.md .claude/commands/
cp .agentic/integrations/slash-commands/memory.reflect.md .claude/commands/
cp .agentic/integrations/slash-commands/memory.status.md .claude/commands/
```

### Usage:

Once installed, use these commands in your Claude conversations:

```
/memory.recall RBAC implementation patterns
/memory.reflect
/memory.status
```

#### `/memory.recall <query>`
Search memory for relevant information.

**Examples**:
- `/memory.recall authentication patterns`
- `/memory.recall similar to: user dashboard`
- `/memory.recall FastAPI decisions`

**Output**: Ranked results grouped by type (decisions, patterns, reflections, features)

#### `/memory.reflect`
Capture a lesson, success, challenge, or recommendation.

**Examples**:
- `/memory.reflect` (interactive mode)
- `/memory.reflect I learned that using JSONB in PostgreSQL works great for flexible metadata`

**Output**: Prompts for details, then captures to memory

#### `/memory.status`
View memory database health and statistics.

**Output**:
- Feature counts
- Decision/reflection/pattern counts
- Top patterns
- Knowledge gaps
- Recommendations

## Integration Levels

These files support different integration levels from the ROADMAP:

| Level | What | Files Needed |
|-------|------|--------------|
| **Level 0** | Manual capture | None (use CLI directly) |
| **Level 1** | Manual capture (recommended) | None (use bash helpers) |
| **Level 2** | Auto-capture hooks | `post-*-hook.sh` files |
| **Level 3** | Context injection | `pre-plan-context-injection.sh` |
| **Level 3** | Slash commands | `memory.*.md` files |
| **Level 4** | Pattern detection | Automatic (future) |

## Complete Integration Guide

For detailed instructions, see **[INTEGRATION_GUIDE.md](../../INTEGRATION_GUIDE.md)** in the root directory.

## Quick Start

**1. Add automatic capture** (Level 2):
```bash
# Copy post-command hook code into your spec-kit commands
# See hooks/*.sh files
```

**2. Add slash commands** (Level 3):
```bash
# Copy to .claude/commands/
cp .agentic/integrations/slash-commands/memory.*.md .claude/commands/
```

**3. Add context injection** (Level 3, after 5+ features):
```bash
# Copy pre-command hook code into /speckit.plan
# See hooks/pre-plan-context-injection.sh
```

## Troubleshooting

### Hooks don't run
- Check that variables like `$GIT_ROOT`, `$FEATURE_DIR`, `$SPEC_FILE` are defined
- Ensure memory system is installed (`ls .agentic/scripts/bash/memory-capture.sh`)
- Test manually: `.agentic/scripts/bash/memory-capture.sh --feature-dir specs/001-test --type spec --file spec.md`

### Slash commands not found
- Ensure files are in `.claude/commands/` directory
- Check that files have `.md` extension
- Verify frontmatter exists (`---\ndescription: ...\n---`)

### Context injection returns nothing
- Check feature count: `python3 .agentic/scripts/memory-cli.py stats`
- Need 5+ features for meaningful context
- Try manual search: `python3 .agentic/scripts/memory-cli.py search "your query"`

## Support

See main documentation:
- [INTEGRATION_GUIDE.md](../../INTEGRATION_GUIDE.md) - Complete integration instructions
- [ROADMAP.md](../../ROADMAP.md) - Integration timeline
- [README.md](../../README.md) - Overview

## License

Same as spec-kit-memory project.
