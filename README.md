# Spec-Kit Memory System

An intelligent memory system for spec-kit that captures, organizes, and retrieves institutional knowledge from your feature development workflow.

## Overview

The Spec-Kit Memory System automatically learns from your development process by:

- 📝 **Capturing** design decisions, implementation patterns, and lessons learned
- 🔍 **Organizing** knowledge in a searchable SQLite database with full-text search
- 💡 **Retrieving** relevant context when planning new features
- 📊 **Analyzing** patterns across features to improve consistency
- 🚀 **Accelerating** development by reusing proven solutions

## 🎯 Zero Disruption Philosophy

**The memory system is a passive add-on that doesn't change your spec-kit workflow.**

- ✅ **No spec-kit modifications required** - Works alongside your existing commands
- ✅ **Optional usage** - Capture only when you want to
- ✅ **Manual or automatic** - You control the integration level
- ✅ **Standalone tool** - Works independently, integrates when you're ready

**Your existing workflow stays exactly the same:**
```bash
# Your normal spec-kit workflow (unchanged)
/speckit.specify "Feature X"
/speckit.plan
/speckit.tasks

# NEW: Optionally capture to memory (when you want)
.agentic/scripts/bash/memory-capture.sh --feature-dir specs/... --type spec --file spec.md
```

**Read the [ROADMAP.md](ROADMAP.md) for integration options** - from manual usage to full automation.

## 📚 Documentation Quick Reference

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[ROADMAP.md](ROADMAP.md)** - Integration levels and timeline
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Complete integration instructions
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical overview

### Integration Materials

- **`.agentic/integrations/hooks/`** - Ready-to-copy hook code for spec-kit commands
  - `post-specify-hook.sh` - Auto-capture after `/speckit.specify`
  - `post-plan-hook.sh` - Auto-capture after `/speckit.plan`
  - `post-tasks-hook.sh` - Auto-capture after `/speckit.tasks`
  - `pre-plan-context-injection.sh` - Inject memory context before planning

- **`.agentic/integrations/slash-commands/`** - Slash command definitions
  - `memory.recall.md` - Search memory (`/memory.recall`)
  - `memory.reflect.md` - Add reflections (`/memory.reflect`)
  - `memory.status.md` - View statistics (`/memory.status`)

## Features

### Automatic Capture
- **Feature metadata** from spec.md
- **Design decisions** from plan.md and research.md
- **Task history** from tasks.md
- **Implementation patterns** from completed work
- **Reflections** on successes, challenges, and lessons learned

### Smart Retrieval
- **Full-text search** across all captured knowledge
- **Similar feature detection** for quick reference
- **Pattern recommendations** based on context
- **Decision history** filtered by category and tags
- **Token-efficient summaries** to minimize context usage

### Analysis & Insights
- **Statistics dashboard** showing memory database health
- **Pattern tracking** with usage counts and success rates
- **High-impact reflections** highlighting key learnings
- **Cross-feature analysis** for architectural consistency

## Installation

### 1. Run Setup Script

```bash
./setup-memory.sh
```

This will:
- Initialize the SQLite database
- Set up the schema with FTS5 search
- Create all necessary directories
- Verify dependencies

### 2. Verify Installation

```bash
python3 .agentic/scripts/memory-cli.py stats
```

You should see the memory database statistics (initially empty).

## Usage

### Basic Commands

#### Search Memory
```bash
# Full-text search across all types
python3 .agentic/scripts/memory-cli.py search "RBAC patterns"

# Search specific types
python3 .agentic/scripts/memory-cli.py search "authentication" --type decision
python3 .agentic/scripts/memory-cli.py search "testing challenges" --type reflection

# Filter decisions by category
python3 .agentic/scripts/memory-cli.py search "FastAPI" --type decision --category technology
```

#### Add Reflections
```bash
# Interactive mode
python3 .agentic/scripts/memory-cli.py reflect

# Direct mode
python3 .agentic/scripts/memory-cli.py reflect \
  --type lesson \
  --impact high \
  --title "E2E Testing Best Practice" \
  --message "Playwright tests need explicit waits to avoid flakiness on CI" \
  --feature 3
```

#### View Features
```bash
# Quick summary
python3 .agentic/scripts/memory-cli.py feature 3 --summary

# Full details
python3 .agentic/scripts/memory-cli.py feature 3 --full
```

#### Browse Patterns
```bash
# All patterns
python3 .agentic/scripts/memory-cli.py patterns

# By type
python3 .agentic/scripts/memory-cli.py patterns --type api

# Get recommendations
python3 .agentic/scripts/memory-cli.py patterns --recommend-for "user authentication"
```

#### View Statistics
```bash
python3 .agentic/scripts/memory-cli.py stats
```

#### Export Data
```bash
# Export specific feature as JSON
python3 .agentic/scripts/memory-cli.py export --feature 3 --format json > feature-003.json

# Export all as Markdown
python3 .agentic/scripts/memory-cli.py export --all --format markdown > memory-dump.md
```

### Bash Helpers (Shortcuts)

```bash
# Quick search
.agentic/scripts/bash/memory-query.sh "RBAC implementation"

# Backup database
.agentic/scripts/bash/memory-backup.sh

# Manual capture
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/003-feature-name \
  --type spec \
  --file specs/003-feature-name/spec.md
```

## Artifact Capture Workflow

### Current: Manual Capture (Recommended)

After running spec-kit commands, manually capture the artifacts:

```bash
# After /speckit.specify
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/003-feature-name \
  --type spec \
  --file specs/003-feature-name/spec.md

# After /speckit.plan
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/003-feature-name \
  --type plan \
  --file specs/003-feature-name/plan.md

# After /speckit.tasks
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/003-feature-name \
  --type tasks \
  --file specs/003-feature-name/tasks.md
```

### Integration with Spec-Kit Commands (Future)

You can integrate memory capture into your spec-kit slash commands by adding capture hooks at the end of each command.

Example for `/speckit.specify`:
```bash
# At the end of your specify command...

# Capture to memory
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir "$FEATURE_DIR" \
  --type spec \
  --file "$SPEC_FILE"
```

## 🗺️ Integration Roadmap

The memory system supports **multiple integration levels** - use as much or as little as you want:

### Level 0: Standalone Tool (Current - Zero Integration)
Use memory-cli.py as a standalone search tool. No spec-kit integration at all.

**Effort**: None
**Value**: Manual knowledge capture and search

### Level 1: Manual Capture (Recommended Starting Point)
After each spec-kit command, manually run capture scripts.

**Effort**: 30 seconds per artifact
**Value**: Searchable knowledge base builds over time

### Level 2: Automatic Capture (Optional Hooks)
Add capture hooks to the end of your spec-kit commands for automatic capture.

**Effort**: 5 minutes per command to add hooks
**Value**: Zero-effort knowledge capture

### Level 3: Context Injection (Advanced)
Query memory before planning to inject relevant past decisions into agent context.

**Effort**: 10-15 minutes per command to add queries
**Value**: Informed planning with architectural consistency

### Level 4: Full Learning System (Future)
Automatic pattern detection and recommendations.

**Effort**: Minimal (mostly automatic)
**Value**: Compound learning across all features

**📖 See [ROADMAP.md](ROADMAP.md) for detailed integration timeline and migration strategies.**

### Quick Start Recommendation

**Week 1-2**: Use Level 1 (manual capture) to build your knowledge base
```bash
# After each spec-kit command
.agentic/scripts/bash/memory-capture.sh --feature-dir specs/... --type spec --file spec.md

# Search when planning new features
python3 .agentic/scripts/memory-cli.py search "similar to: new feature idea"
```

**Week 3-4**: Optionally add Level 2 (automatic hooks) once you see value
```bash
# Add to end of .claude/commands/speckit.specify.md
if [[ -f ".agentic/scripts/bash/memory-capture.sh" ]]; then
  .agentic/scripts/bash/memory-capture.sh --feature-dir "$FEATURE_DIR" --type spec --file "$SPEC_FILE"
fi
```

**Month 2+**: Consider Level 3 (context injection) after accumulating 5+ features

## Database Schema

The memory system uses SQLite with FTS5 full-text search:

### Core Tables
- **features**: Top-level feature tracking
- **artifacts**: Spec-kit documents (spec.md, plan.md, etc.)
- **decisions**: Design/architecture choices with rationale
- **reflections**: Lessons learned and post-implementation insights
- **patterns**: Reusable implementation patterns
- **task_history**: Completed tasks for pattern detection
- **cross_references**: Relationships between items

### FTS5 Search Tables
- **artifacts_fts**: Full-text search on artifact content
- **decisions_fts**: Search decisions by text
- **reflections_fts**: Search reflections
- **patterns_fts**: Search patterns

## Configuration

Edit `.agentic/config/memory-config.yaml` to customize:

- Database path and backup settings
- Search result limits
- Auto-capture preferences
- Token budgets for memory injection
- Pattern recommendation thresholds

## Database Maintenance

### Backup
```bash
# Create backup
.agentic/scripts/bash/memory-backup.sh

# Backups are automatically kept in .agentic/memory/backups/
# Old backups are automatically cleaned up (keeps last 10)
```

### Database Location
```
.agentic/memory/memory.db        # Main database
.agentic/memory/backups/         # Automatic backups
.agentic/memory/schema.sql       # Schema definition
```

### Rebuild Database
If you need to rebuild the database from scratch:

```bash
# Backup first!
.agentic/scripts/bash/memory-backup.sh

# Remove database
rm .agentic/memory/memory.db

# Reinitialize
./setup-memory.sh
```

## Examples

### Example 1: Starting a New Feature

```bash
# Search for similar features
python3 .agentic/scripts/memory-cli.py search "user dashboard"

# View a related feature in detail
python3 .agentic/scripts/memory-cli.py feature 3 --summary

# Get relevant patterns
python3 .agentic/scripts/memory-cli.py patterns --recommend-for "dashboard layout"
```

### Example 2: Capturing a Lesson Learned

```bash
# After fixing a tricky bug or discovering a best practice
python3 .agentic/scripts/memory-cli.py reflect \
  --type lesson \
  --impact high \
  --title "PostgreSQL JSONB for Flexible Schemas" \
  --message "Using JSONB columns allows schema evolution without migrations. Perfect for metadata fields that vary by entity type." \
  --category data-model \
  --feature 3
```

### Example 3: Analyzing Technology Decisions

```bash
# See all technology decisions
python3 .agentic/scripts/memory-cli.py search "" --type decision --category technology

# Export for documentation
python3 .agentic/scripts/memory-cli.py export --all --format markdown > tech-decisions.md
```

## Integration with Spec-Kit Workflow

### Recommended Workflow

1. **Specify** (`/speckit.specify`)
   - Write spec.md
   - Capture: `memory-capture.sh --type spec`

2. **Plan** (`/speckit.plan`)
   - Write plan.md and research.md
   - Capture: `memory-capture.sh --type plan`
   - System automatically extracts decisions

3. **Tasks** (`/speckit.tasks`)
   - Write tasks.md
   - Capture: `memory-capture.sh --type tasks`
   - System tracks task patterns

4. **Implement** (`/speckit.implement`)
   - Complete tasks
   - Add reflections: `memory-cli.py reflect`
   - Capture updated tasks: `memory-capture.sh --type tasks`

5. **Analyze** (`/speckit.analyze`)
   - Search for patterns: `memory-cli.py patterns`
   - View stats: `memory-cli.py stats`

## Benefits

### 🚀 Faster Development
- Reuse proven patterns instead of reinventing solutions
- Quick reference to similar features
- Avoid repeating past mistakes

### 📊 Better Decisions
- Informed by historical context
- See what worked (and didn't) in similar situations
- Maintain architectural consistency

### 💰 Token Efficiency
- Retrieve only relevant context (15-30% token reduction)
- Summaries instead of full documents
- Progressive disclosure (expand only when needed)

### 🧠 Institutional Knowledge
- Preserve team learnings across features
- Onboard new team members faster
- Create a searchable knowledge base

## Troubleshooting

### Database Not Found
```bash
# Ensure you've run setup
./setup-memory.sh
```

### Python Dependencies
The memory system uses only standard library modules:
- sqlite3 (built-in)
- json (built-in)
- re (built-in)
- hashlib (built-in)

No pip install required!

### Search Not Working
Ensure FTS5 is enabled in your Python sqlite3:
```bash
python3 -c "import sqlite3; print('fts5' in sqlite3.connect(':memory:').execute('PRAGMA compile_options').fetchall().__str__())"
```

Should output `True`.

## Advanced Usage

### Custom Patterns

You can manually add patterns to the database:

```python
from memory_lib import MemoryDB, Pattern
import json

db = MemoryDB()

pattern = Pattern(
    id=None,
    pattern_name="rbac-middleware-pattern",
    pattern_type="api",
    description="Decorator-based role checking for FastAPI endpoints",
    use_cases="Use when you need endpoint-level authorization",
    implementation_notes="Create a dependency that checks user roles",
    example_code="@require_role('admin')\nasync def endpoint()...",
    source_feature_ids=json.dumps([3, 7, 12]),
    times_used=3,
    success_rate=1.0,
    tags=json.dumps(["fastapi", "rbac", "auth", "decorator"]),
    created_at=None,
    updated_at=None
)

db.create_pattern(pattern)
```

### Batch Operations

```python
from memory_lib import MemoryDB

db = MemoryDB()

# Get all features
features = db.list_features()

# Export all decisions
for feature in features:
    decisions = db.list_decisions(feature_id=feature.id)
    print(f"\n{feature.full_name}:")
    for d in decisions:
        print(f"  - [{d.category}] {d.decision}")
```

## Contributing

The memory system is designed to be extended. Key extension points:

1. **Extractors**: Add new parsers in `memory-extractor.py`
2. **CLI Commands**: Add new commands in `memory-cli.py`
3. **Schema**: Extend database schema in `schema.sql`
4. **Analysis**: Add new analytics in `memory-lib.py`

## License

Same as your spec-kit project.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the example workflows
3. Examine the database schema
4. Check configuration in `memory-config.yaml`

---

**Built for spec-kit developers who believe knowledge should compound, not repeat.**
