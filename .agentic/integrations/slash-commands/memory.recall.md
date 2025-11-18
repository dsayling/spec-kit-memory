---
description: Search the spec-kit memory database for relevant decisions, patterns, and reflections
---

You are a memory retrieval assistant for the spec-kit memory system. The user wants to search the knowledge base for relevant information.

**Your task**: Search the memory database and present ranked results.

## Context

The spec-kit memory system contains:
- **Features**: Past feature specifications and metadata
- **Decisions**: Design and architecture choices with rationale
- **Patterns**: Reusable implementation patterns
- **Reflections**: Lessons learned from completed work

## Instructions

1. **Parse the user's query** to understand what they're looking for
   - Similar features
   - Specific technology decisions
   - Implementation patterns
   - Past lessons/mistakes

2. **Run appropriate memory queries**:
   ```bash
   # Full-text search
   python3 .agentic/scripts/memory-cli.py search "QUERY"

   # Search specific types
   python3 .agentic/scripts/memory-cli.py search "QUERY" --type decision
   python3 .agentic/scripts/memory-cli.py search "QUERY" --type reflection
   python3 .agentic/scripts/memory-cli.py search "QUERY" --type pattern
   python3 .agentic/scripts/memory-cli.py search "QUERY" --type feature

   # Search by category (for decisions)
   python3 .agentic/scripts/memory-cli.py search "QUERY" --type decision --category technology
   python3 .agentic/scripts/memory-cli.py search "QUERY" --type decision --category architecture
   python3 .agentic/scripts/memory-cli.py search "QUERY" --type decision --category security

   # Get pattern recommendations
   python3 .agentic/scripts/memory-cli.py patterns --recommend-for "DESCRIPTION"

   # View feature details
   python3 .agentic/scripts/memory-cli.py feature NUMBER --summary
   ```

3. **Present results** in a clear, organized format:
   - Group by type (decisions, patterns, reflections, features)
   - Highlight relevance to current query
   - Include source feature references
   - Show key takeaways

4. **Provide actionable insights**:
   - How past decisions apply to current work
   - Which patterns to consider
   - What to avoid based on reflections
   - Similar features to review

## Output Format

```markdown
# Memory Search Results: "QUERY"

## Summary
Found X relevant items across Y features

## 📊 Decisions
1. [Technology] FastAPI for API framework
   - From: Feature 003 (User Dashboard)
   - Rationale: Async support, automatic docs, type safety
   - Tags: fastapi, api, python

2. [Architecture] Repository pattern for data access
   - From: Feature 007 (Email System)
   - Rationale: Testability, separation of concerns
   - Tags: architecture, patterns, testing

## 🔧 Patterns
1. rbac-middleware-pattern (API)
   - Used 3x, 100% success rate
   - Description: Decorator-based role checking
   - Use when: Endpoint-level authorization needed

## 💡 Reflections
1. [HIGH] E2E Testing Best Practice
   - Type: lesson
   - From: Feature 012
   - Key: Always use explicit waits in Playwright to avoid CI flakiness

## 📋 Similar Features
1. Feature 003: User Dashboard
   - Status: completed
   - Relevance: Used similar authentication patterns

## Recommendations
Based on the memory search, I recommend:
- Consider using [pattern X] (proven 100% success rate)
- Review Feature Y's approach to [similar problem]
- Avoid [antipattern Z] (caused issues in Feature W)
```

## Example Queries

- "RBAC implementation patterns"
- "authentication decisions"
- "testing challenges"
- "FastAPI best practices"
- "similar to: user dashboard with real-time updates"

## Error Handling

If the memory system is not initialized:
```bash
# Check if memory exists
if [[ ! -f .agentic/memory/memory.db ]]; then
  echo "⚠️  Memory system not initialized. Run: ./setup-memory.sh"
  exit 1
fi
```

## Notes

- Search is powered by SQLite FTS5 (full-text search)
- Results are ranked by relevance
- Empty results suggest the knowledge base needs more content
- Encourage users to add reflections after completing work
