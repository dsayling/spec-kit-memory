---
description: View spec-kit memory database statistics and health metrics
---

You are a memory system monitoring assistant. The user wants to see the current state and health of their knowledge base.

**Your task**: Display memory database statistics and provide insights about the knowledge base.

## Instructions

1. **Get database statistics**:
   ```bash
   python3 .agentic/scripts/memory-cli.py stats
   ```

2. **Parse and present** the statistics in a user-friendly format

3. **Provide insights** based on the stats:
   - Is the knowledge base growing?
   - Are there knowledge gaps?
   - What are the most-used patterns?
   - What are the high-impact reflections?

4. **Suggest actions** based on current state

## Statistics Available

The stats command returns:
- Database size and location
- Feature counts by status
- Artifact counts by type
- Decision counts by category
- Total reflections and patterns
- Task completion stats
- Top patterns (by usage)
- Recent high-impact reflections

## Output Format

```markdown
# 📊 Spec-Kit Memory System Status

## Database Health
- 📁 Location: `.agentic/memory/memory.db`
- 💾 Size: 2.5 MB
- 📅 Last backup: 2 days ago

## Knowledge Base Overview

### Features Tracked: 12
- ✅ Completed: 8
- 🚧 In Progress: 3
- 📋 Planning: 1

### Knowledge Captured
- 📄 **Artifacts**: 48 documents
  - spec: 12
  - plan: 12
  - tasks: 12
  - research: 8
  - contracts: 4

- 📊 **Decisions**: 156 recorded
  - Top categories:
    - technology: 42
    - architecture: 38
    - api-design: 24
    - security: 18
    - testing: 16

- 💡 **Reflections**: 24 captured
  - High impact: 8
  - Medium impact: 12
  - Low impact: 4

- 🔧 **Patterns**: 15 identified
  - Most successful:
    - rbac-middleware-pattern (8x, 100% success)
    - crud-api-pattern (12x, 100% success)
    - e2e-test-pattern (10x, 90% success)

- ✅ **Tasks**: 342 completed

## Recent Activity

### High-Impact Reflections (Last 5)
1. "E2E Testing Best Practice" (Feature 012)
2. "PostgreSQL JSONB for Flexibility" (Feature 010)
3. "FastAPI Dependency Injection" (Feature 003)

### Most Referenced Features
1. Feature 003: User Authentication (15 references)
2. Feature 007: Email Integration (12 references)
3. Feature 010: Dashboard (8 references)

## Health Indicators

✅ **Healthy**: Active knowledge capture
✅ **Diverse**: Good coverage across categories
⚠️  **Suggestion**: More reflections needed (aim for 2-3 per feature)

## Recommendations

Based on your knowledge base stats:

1. **Knowledge Gaps Detected**:
   - Few security decisions (only 18) - consider documenting security choices more
   - Low pattern count in UI category - capture frontend patterns

2. **Strong Areas**:
   - Excellent technology decision documentation (42 decisions)
   - High pattern success rates - keep reusing proven approaches

3. **Suggested Actions**:
   - Add reflections for Features 1, 2, 4 (no reflections captured yet)
   - Run backup: `.agentic/scripts/bash/memory-backup.sh`
   - Capture remaining research.md files (4 features missing)

## Growth Metrics

**Compared to last month**:
- Features: +5 (71% growth)
- Decisions: +38 (32% growth)
- Reflections: +8 (50% growth)
- Patterns: +3 (25% growth)

**Knowledge Velocity**: 2.3 decisions per feature (healthy)

## Next Steps

1. **Maintain**: Keep capturing artifacts after each spec-kit command
2. **Reflect**: Add 2-3 reflections per completed feature
3. **Backup**: Run backup weekly
4. **Clean**: Consider archiving abandoned features
```

## Advanced Views

Offer these additional views:

```bash
# View all patterns
python3 .agentic/scripts/memory-cli.py patterns

# View patterns by type
python3 .agentic/scripts/memory-cli.py patterns --type api
python3 .agentic/scripts/memory-cli.py patterns --type testing

# List features
python3 .agentic/scripts/memory-cli.py search "" --type feature

# Export for analysis
python3 .agentic/scripts/memory-cli.py export --all --format json > memory-dump.json
python3 .agentic/scripts/memory-cli.py export --all --format markdown > memory-dump.md
```

## Health Thresholds

Use these thresholds to assess health:

**Excellent** (🟢):
- 10+ features tracked
- 100+ decisions
- 20+ reflections
- 2+ reflections per completed feature
- 10+ patterns identified

**Good** (🟡):
- 5+ features tracked
- 50+ decisions
- 10+ reflections
- 1+ reflection per completed feature
- 5+ patterns identified

**Needs Attention** (🟠):
- 3+ features tracked
- 20+ decisions
- 5+ reflections
- Some patterns identified

**Getting Started** (⚪):
- <3 features tracked
- <20 decisions
- <5 reflections

## Visualization Ideas

Suggest these visualizations if the user wants deeper analysis:

```bash
# Export to JSON for custom analysis
python3 .agentic/scripts/memory-cli.py export --all --format json > stats.json

# Then analyze with tools:
# - Plot decision growth over time
# - Show pattern success rates
# - Map knowledge coverage by category
# - Identify most influential features
```

## Error Handling

```bash
# Check if memory system exists
if [[ ! -f .agentic/memory/memory.db ]]; then
  echo "⚠️  Memory system not initialized"
  echo ""
  echo "To set up the memory system:"
  echo "  ./setup-memory.sh"
  echo ""
  echo "This will create the database and enable knowledge capture."
  exit 1
fi
```

## Interpretation Guide

Help users understand what the stats mean:

**Feature Count**:
- More features = more institutional knowledge
- Aim for at least 5 before enabling context injection

**Decision Count**:
- Should grow with features (avg 10-15 per feature)
- Low count suggests incomplete plan capture

**Reflection Count**:
- Critical for learning
- Should be 2-3 per completed feature
- High-impact reflections are most valuable

**Pattern Count**:
- Emerges after 5-10 features
- High success rate = proven approaches
- Low success rate = need refinement

**Pattern Usage**:
- Patterns with 3+ uses are "proven"
- 100% success rate = very reliable
- <80% success rate = needs investigation
