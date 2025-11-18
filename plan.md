Agent Memory System for Spec-Kit: Implementation Plan
Executive Summary
Add a local SQLite-based memory system (.agentic/memory/memory.db) that captures design decisions, implementation reflections, and reusable patterns from spec-kit workflows. This enables agents to:
Learn from past features (avoid repeating mistakes)
Reuse proven patterns (faster implementation)
Make context-aware suggestions (token-efficient retrieval)
Track architectural evolution (decision history)
Integration Strategy: Hybrid approach with automatic capture during spec-kit commands and explicit retrieval via new commands.
1. Database Schema Design
1.1 Core Tables
-- Features: Top-level feature tracking
CREATE TABLE features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_number INTEGER NOT NULL,           -- 001, 002, 003...
    short_name TEXT NOT NULL,                  -- 'field-engineer-management'
    full_name TEXT NOT NULL,                   -- 'Field Engineer Management'
    description TEXT,                          -- From spec.md Summary
    status TEXT CHECK(status IN ('planning', 'in_progress', 'completed', 'abandoned')),
    priority TEXT CHECK(priority IN ('P1', 'P2', 'P3')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    spec_path TEXT NOT NULL,                   -- specs/003-field-engineer-management/
    UNIQUE(feature_number, short_name)
);

-- Artifacts: Spec-kit documents (spec.md, plan.md, tasks.md, etc.)
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_id INTEGER NOT NULL,
    artifact_type TEXT NOT NULL CHECK(artifact_type IN 
        ('spec', 'plan', 'tasks', 'research', 'data-model', 'quickstart', 'contract', 'checklist')),
    file_path TEXT NOT NULL,                   -- Absolute path
    content TEXT NOT NULL,                     -- Full file content
    content_hash TEXT NOT NULL,                -- SHA256 for change detection
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,                 -- Track versions
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE,
    UNIQUE(feature_id, artifact_type, file_path)
);

-- Decisions: Architectural/design choices from plan.md and research.md
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_id INTEGER NOT NULL,
    category TEXT NOT NULL CHECK(category IN 
        ('architecture', 'technology', 'data-model', 'api-design', 'security', 
         'performance', 'ux', 'testing', 'deployment', 'observability')),
    decision TEXT NOT NULL,                    -- What was decided
    rationale TEXT,                            -- Why it was chosen
    alternatives TEXT,                         -- What was considered
    constraints TEXT,                          -- Limitations/tradeoffs
    source_section TEXT,                       -- plan.md section reference
    tags TEXT,                                 -- JSON array: ["rbac", "email", "auth"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE
);

-- Reflections: Post-implementation learnings
CREATE TABLE reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_id INTEGER,                        -- NULL for global reflections
    reflection_type TEXT NOT NULL CHECK(reflection_type IN 
        ('success', 'challenge', 'lesson', 'antipattern', 'recommendation')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    impact TEXT CHECK(impact IN ('high', 'medium', 'low')),
    category TEXT,                             -- Same as decisions.category
    related_task_ids TEXT,                     -- JSON array of task IDs
    tags TEXT,                                 -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE SET NULL
);

-- Patterns: Reusable implementation patterns
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL UNIQUE,         -- 'rbac-middleware-pattern'
    pattern_type TEXT NOT NULL CHECK(pattern_type IN 
        ('code', 'architecture', 'testing', 'api', 'database', 'ui')),
    description TEXT NOT NULL,
    use_cases TEXT,                            -- When to use this pattern
    implementation_notes TEXT,                 -- How to implement
    example_code TEXT,                         -- Code snippet (if applicable)
    source_feature_ids TEXT,                   -- JSON array: [3, 7, 12]
    times_used INTEGER DEFAULT 1,
    success_rate REAL DEFAULT 1.0,             -- 0.0 to 1.0
    tags TEXT,                                 -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks: Completed task history for pattern detection
CREATE TABLE task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_id INTEGER NOT NULL,
    task_id TEXT NOT NULL,                     -- US1-T1, US2-T3, etc.
    user_story TEXT,                           -- US1, US2, etc.
    phase TEXT,                                -- 'setup', 'foundational', 'us1', 'us2'
    description TEXT NOT NULL,
    file_paths TEXT,                           -- JSON array of files touched
    test_type TEXT,                            -- 'unit', 'integration', 'e2e', 'contract'
    duration_minutes INTEGER,                  -- Time to complete
    complexity TEXT CHECK(complexity IN ('simple', 'moderate', 'complex')),
    status TEXT CHECK(status IN ('completed', 'skipped', 'blocked')),
    notes TEXT,                                -- Implementation notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE
);

-- Cross-references: Link related items
CREATE TABLE cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_type TEXT NOT NULL CHECK(from_type IN ('decision', 'reflection', 'pattern', 'task')),
    from_id INTEGER NOT NULL,
    to_type TEXT NOT NULL CHECK(to_type IN ('decision', 'reflection', 'pattern', 'task')),
    to_id INTEGER NOT NULL,
    relationship TEXT CHECK(relationship IN ('related', 'depends_on', 'supersedes', 'inspired_by')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_type, from_id, to_type, to_id)
);
1.2 Full-Text Search (FTS5)
-- FTS for fast semantic search across all text content
CREATE VIRTUAL TABLE artifacts_fts USING fts5(
    artifact_id UNINDEXED,
    feature_name,
    artifact_type,
    content,
    tokenize = 'porter unicode61'
);

CREATE VIRTUAL TABLE decisions_fts USING fts5(
    decision_id UNINDEXED,
    category,
    decision,
    rationale,
    alternatives,
    tags,
    tokenize = 'porter unicode61'
);

CREATE VIRTUAL TABLE reflections_fts USING fts5(
    reflection_id UNINDEXED,
    reflection_type,
    title,
    description,
    tags,
    tokenize = 'porter unicode61'
);

CREATE VIRTUAL TABLE patterns_fts USING fts5(
    pattern_id UNINDEXED,
    pattern_name,
    pattern_type,
    description,
    use_cases,
    tags,
    tokenize = 'porter unicode61'
);
1.3 Indexes for Performance
CREATE INDEX idx_features_status ON features(status);
CREATE INDEX idx_features_number ON features(feature_number);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX idx_artifacts_feature ON artifacts(feature_id);
CREATE INDEX idx_decisions_category ON decisions(category);
CREATE INDEX idx_decisions_feature ON decisions(feature_id);
CREATE INDEX idx_reflections_type ON reflections(reflection_type);
CREATE INDEX idx_reflections_impact ON reflections(impact);
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_tasks_feature ON task_history(feature_id);
CREATE INDEX idx_tasks_story ON task_history(user_story);
2. Memory Capture Strategy
2.1 Automatic Capture Points
| Spec-Kit Command | What to Capture | When | Tables Updated | |----------------------|---------------------|----------|-------------------| | /speckit.specify | Feature metadata, spec.md content | After spec written | features, artifacts, artifacts_fts | | /speckit.clarify | Updated spec.md (version increment) | After clarifications applied | artifacts (version++) | | /speckit.plan | plan.md, research.md, data-model.md, contracts/ | After planning complete | artifacts, decisions, decisions_fts | | /speckit.tasks | tasks.md, task breakdown | After tasks generated | artifacts, task_history (pending) | | /speckit.checklist | Checklist files | After checklist created | artifacts | | /speckit.implement | Task completion, outcomes | After each task marked [X] | task_history (status=completed) | | /speckit.analyze | Cross-artifact insights | After analysis run | reflections (if gaps found) |
2.2 Automatic Extraction Logic
From plan.md → decisions table:
Parse sections: "Tech Stack Decisions", "Architecture Decisions", "Security Model", etc.
Extract decision structure: Decision: X | Rationale: Y | Alternatives: Z
Auto-categorize based on section headers
Tag with relevant keywords (FastAPI, RBAC, PostgreSQL, etc.)
From research.md → decisions table:
Extract research conclusions as decisions
Link to specific technical choices (libraries, patterns, protocols)
From tasks.md → task_history table:
Parse task format: - [X] [US1-T1] [P] Create user model schema (backend/src/db/models/user.py)
Extract: task_id, user_story, description, file_paths, parallelizable
Track when marked complete
Pattern Detection (post-implementation):
Analyze completed tasks across features
Detect recurring task sequences (e.g., "model → schema → API → tests")
Extract reusable patterns (e.g., "CRUD endpoint pattern", "Auth middleware pattern")
3. Memory Retrieval Strategy
3.1 Smart Context Injection
Principle: Inject only relevant memory snippets based on current command context to minimize tokens.
| Command | Query | What to Retrieve | Max Items | |-------------|-----------|----------------------|---------------| | /speckit.specify | Similar feature descriptions | Top 3 similar completed features (spec summaries only) | 3 features | | /speckit.plan | Architecture decisions for similar features | Relevant decisions by category (architecture, technology, security) | 5-10 decisions | | /speckit.plan | Known patterns for tech stack | Patterns matching tech stack tags | 3-5 patterns | | /speckit.tasks | Task patterns for similar user stories | Task sequences from similar features | 3 sequences | | /speckit.implement | Reflections on current task type | Lessons/challenges for similar tasks | 3-5 reflections |
3.2 Retrieval API Functions
# Core retrieval functions (to be called by spec-kit commands)

def find_similar_features(description: str, limit: int = 3) -> List[Feature]:
    """FTS search on feature descriptions, return top N matches"""

def get_decisions_by_category(categories: List[str], tags: List[str] = None) -> List[Decision]:
    """Retrieve decisions filtered by category and optional tags"""

def find_patterns_by_type(pattern_type: str, tags: List[str] = None) -> List[Pattern]:
    """Get reusable patterns by type and tags"""

def get_reflections_by_category(category: str, impact: str = 'high') -> List[Reflection]:
    """Retrieve high-impact lessons learned"""

def search_all(query: str, limit: int = 10) -> SearchResults:
    """FTS search across all tables, ranked by relevance"""

def get_feature_summary(feature_id: int) -> FeatureSummary:
    """Quick summary: spec + key decisions + outcomes (token-efficient)"""
3.3 Token Efficiency Tactics
Summaries, not full content: Return 2-3 sentence summaries instead of full artifacts
Relevance scoring: Rank by FTS score + category match + tag overlap
Tiered retrieval:
Tier 1: High-relevance (top 3 results)
Tier 2: Medium-relevance (next 5-7, only if needed)
Tier 3: Full content (only on explicit request)
Lazy loading: Retrieve details only when agent requests specific item
Deduplication: Remove redundant suggestions across features
4. Integration with Spec-Kit Commands
4.1 Seamless Integration (Auto-Capture)
Modify existing commands with minimal changes by adding memory hooks:
Pattern: Add memory capture at the end of each command after artifacts are written.
# Example: /speckit.specify integration point
# After spec.md is written (existing code)...

# NEW: Auto-capture to memory
.agentic/scripts/memory-capture.py \
    --feature-dir "$FEATURE_DIR" \
    --artifact-type spec \
    --file "$SPEC_FILE"

# This script extracts metadata and inserts into memory.db
Integration Points:
| Command | Hook Location | Script Called | |-------------|-------------------|-------------------| | /speckit.specify | After spec.md written | memory-capture.py --type spec | | /speckit.plan | After plan.md/research.md written | memory-capture.py --type plan + decision extractor | | /speckit.tasks | After tasks.md written | memory-capture.py --type tasks | | /speckit.implement | After each task completion | memory-update.py --task-complete $TASK_ID |
No user-facing changes: Capture happens silently in background.
4.2 Explicit Retrieval (New Commands)
Add 3 new slash commands for explicit memory interaction:
a) /speckit.recall [query] - Search memory
# /speckit.recall "RBAC implementation patterns"

**Purpose**: Search memory for decisions, patterns, reflections, or past features.

**Usage**:
- /speckit.recall "authentication patterns"
- /speckit.recall "email integration challenges"
- /speckit.recall "FastAPI testing best practices"

**Output**:
- Top 5-10 ranked results across all memory types
- Each result: Title + 2-sentence summary + source feature
- Option to expand for full details
b) /speckit.reflect [message] - Store reflection
# /speckit.reflect "Email delivery was unreliable with Gmail SMTP; switched to SendGrid with 99.9% success"

**Purpose**: Manually record lessons learned, challenges, or recommendations.

**Usage**:
- /speckit.reflect "Auth middleware caused circular imports; fixed by lazy loading"
- /speckit.reflect "Playwright E2E tests flaky on CI; needed explicit waits"
- /speckit.reflect "PostgreSQL JSONB perfect for flexible field engineer metadata"

**Prompts**:
- Reflection type: success | challenge | lesson | antipattern | recommendation
- Impact: high | medium | low
- Category: (auto-detected or manual selection)
- Tags: (auto-extracted from message)

**Output**: Confirmation + reflection ID for future reference
c) /speckit.memory-status - View memory stats
# /speckit.memory-status

**Purpose**: Show memory database statistics and health.

**Output**:
Memory Database Status
Location: .agentic/memory/memory.db Size: 2.4 MB
Features Tracked: 12 (10 completed, 2 in-progress) Artifacts Stored: 87 (spec: 12, plan: 12, tasks: 12, ...) Decisions Recorded: 156 Reflections Captured: 43 Patterns Extracted: 18 Tasks Completed: 847
Top Categories:
Architecture: 45 decisions
Technology: 38 decisions
API Design: 27 decisions
Most Used Patterns:
rbac-middleware (used 8x, 100% success)
crud-endpoint-pattern (used 12x, 95% success)
email-service-abstraction (used 3x, 100% success)
Recent Reflections (high-impact):
"PostgreSQL JSONB perfect for flexible metadata" (003)
"Pre-commit hooks critical for code quality" (002)
5. CLI Tool Design
5.1 Python CLI (memory-cli.py)
Location: .agentic/scripts/memory-cli.py
Commands:
# Search
memory-cli search "RBAC patterns" --limit 10
memory-cli search "email integration" --type decision --category technology

# Add reflection
memory-cli reflect --type lesson --impact high --message "..."

# View feature
memory-cli feature 003 --summary          # Brief overview
memory-cli feature 003 --full             # Full details + all decisions

# Export
memory-cli export --feature 003 --format json > feature-003-memory.json
memory-cli export --all --format markdown > memory-dump.md

# Stats
memory-cli stats
memory-cli stats --category architecture

# Patterns
memory-cli patterns --type api
memory-cli patterns --recommend-for "user authentication"
5.2 Bash Helper Scripts
Location: .agentic/scripts/bash/
# memory-capture.sh - Called by spec-kit commands
memory-capture.sh --feature-dir specs/003-... --type spec --file spec.md

# memory-query.sh - Quick lookups
memory-query.sh "similar features to: field engineer dashboard"

# memory-extract-decisions.sh - Parse plan.md/research.md
memory-extract-decisions.sh specs/003-.../plan.md

# memory-backup.sh - Periodic backups
memory-backup.sh  # Creates .agentic/memory/backups/memory-YYYYMMDD.db
6. Token Efficiency Strategy
6.1 Context Budget Allocation
Allocate max 10-15% of context window to memory retrieval:
| Command | Context Budget | Retrieval Strategy | |-------------|-------------------|------------------------| | /speckit.specify | 2-3K tokens | Top 3 similar feature summaries (300 tokens each) | | /speckit.plan | 5-7K tokens | 5-10 relevant decisions (500-700 tokens each) | | /speckit.tasks | 3-5K tokens | 3 task pattern sequences (1K tokens each) | | /speckit.implement | 2-4K tokens | 3-5 reflections on current task type (500-800 tokens each) |
6.2 Progressive Disclosure
Tier 1 (Always Shown): Ultra-compact summaries
Feature: 003: Field Engineer Management - RBAC + email integration, 5 user stories
Decision: Tech: FastAPI + SQLAlchemy (robust async ORM, team familiarity)
Pattern: RBAC middleware: Decorator-based role checking, reusable across endpoints
Tier 2 (On Demand): Medium detail (agent requests "expand item 3")
Full decision rationale (200-300 tokens)
Pattern implementation notes (300-500 tokens)
Tier 3 (Explicit): Full content (agent requests "show full plan.md from feature 003")
Complete artifact content (2K-10K tokens)
6.3 Smart Caching
Session-level cache: Once retrieved, keep in conversation context (don't re-query)
Deduplication: If decision appears in multiple features, show once with "also used in: 003, 007, 012"
7. Workflow Examples
Example 1: Starting a New Feature
# User: /speckit.specify "Add reporting dashboard for business owners"

# Agent internally:
1. Runs /speckit.specify logic (existing)
2. Before writing spec.md:
   - Queries memory: find_similar_features("reporting dashboard business owners")
   - Retrieves: Feature 003 (Field Engineer Dashboard), Feature 002 (Business Owner Onboarding)
   - Injects context: "FYI: Similar dashboards in 003 (used React Query + TailwindCSS)"
3. Writes spec.md (existing)
4. Auto-captures to memory:
   - memory-capture.sh --type spec --feature 004-reporting-dashboard

# Output to user: (no mention of memory system - seamless)
Example 2: Planning Architecture
# User: /speckit.plan

# Agent internally:
1. Loads spec.md (existing)
2. Before generating plan:
   - Queries memory: get_decisions_by_category(['architecture', 'technology'])
   - Retrieves: "Past features used FastAPI + PostgreSQL + React"
   - Retrieves: "RBAC pattern successful in 003, 007, 012"
   - Injects context: "Recommended patterns based on past success..."
3. Generates plan.md (existing)
4. Auto-captures:
   - memory-capture.sh --type plan
   - memory-extract-decisions.sh plan.md  # Extracts decisions into DB

# Output to user: Plan includes "Tech Stack (informed by past features: 003, 007)"
Example 3: Explicit Reflection
# User: /speckit.reflect "Playwright E2E tests were flaky on CI due to race conditions. 
#       Fixed by adding explicit waitForSelector() before assertions. Critical for frontend testing."

# Agent:
1. Parses message
2. Prompts:
   - "Type: challenge | lesson | recommendation?" → User: "lesson"
   - "Impact: high | medium | low?" → User: "high"
   - "Category?" → Auto-detected: "testing"
   - "Tags?" → Auto-extracted: ["playwright", "e2e", "ci", "flaky-tests"]
3. Inserts into reflections table
4. Confirms: "Reflection saved (ID: 127). This will inform future frontend testing tasks."
Example 4: Searching Memory
# User: /speckit.recall "RBAC implementation"

# Agent:
1. FTS search across decisions_fts, patterns_fts, reflections_fts
2. Ranks by relevance
3. Returns:

**Search Results for "RBAC implementation"**

**Patterns** (2 found):
1. **rbac-middleware-pattern** (used 8x, 100% success)
   - Decorator-based role checking, reusable across FastAPI endpoints
   - Source: Features 003, 007, 012
   - [Expand for implementation notes]

**Decisions** (5 found):
1. **Feature 003: Security Model - Role-Based Access Control**
   - Decision: FastAPI dependencies + custom decorators
   - Rationale: Type-safe, testable, integrates with Pydantic schemas
   - [Expand for details]

2. **Feature 007: Admin Panel - Permission System**
   - Decision: PostgreSQL JSONB for flexible permissions
   - Rationale: Schema evolution without migrations
   - [Expand for details]

**Reflections** (1 found):
1. **Lesson: RBAC middleware must handle async context** (Feature 003)
   - Impact: High
   - FastAPI dependencies require async-aware role checking
   - [Expand for full reflection]
8. Implementation Phases
Phase 1: Foundation (Week 1)

Create database schema ([object Object])

Implement core SQLite + FTS5 setup

Write Python CLI ([object Object]) with basic CRUD

Create bash helper scripts (capture, query)

Unit tests for database layer
Phase 2: Auto-Capture (Week 2)

Integrate capture hooks into [object Object]

Integrate capture hooks into [object Object]

Implement decision extraction from [object Object]

Integrate capture hooks into [object Object]

Integrate capture hooks into [object Object]

Implement task completion tracking
Phase 3: Retrieval Commands (Week 3)

Implement [object Object] command

Implement [object Object] command

Implement [object Object] command

Add context injection to planning phase

Add context injection to specification phase
Phase 4: Pattern Detection (Week 4)

Analyze completed tasks across features

Implement pattern extraction algorithm

Auto-populate [object Object] table from historical data

Implement pattern recommendation engine

Add pattern suggestions to [object Object]
Phase 5: Polish & Optimization (Week 5)

Add caching layer for frequent queries

Implement backup/restore functionality

Add export capabilities (JSON, Markdown)

Performance tuning (query optimization)

Documentation and examples

E2E test suite for memory system
9. Success Metrics
Quantitative Metrics
Token Reduction: 15-30% reduction in context usage during planning/implementation
Reuse Rate: 40%+ of decisions/patterns reused across features
Search Performance: <100ms for FTS queries on 1000+ artifacts
Capture Coverage: 100% of spec-kit artifacts auto-captured
Qualitative Metrics
Consistency: Architectural decisions align across features (measurable via /speckit.analyze)
Learning Curve: New features leverage past lessons (fewer repeated mistakes)
Agent Effectiveness: Agents make better-informed suggestions during planning
Developer Satisfaction: Faster feature development with pattern reuse
10. File Structure
.agentic/
├── memory/
│   ├── memory.db                    # SQLite database
│   ├── backups/                     # Automated backups
│   │   └── memory-20251118.db
│   └── schema.sql                   # Schema definition
├── scripts/
│   ├── memory-cli.py                # Main CLI tool
│   ├── memory-lib.py                # Core library (DB access, search)
│   ├── memory-extractor.py          # Parse artifacts → structured data
│   └── bash/
│       ├── memory-capture.sh        # Auto-capture hook
│       ├── memory-query.sh          # Quick search
│       ├── memory-extract-decisions.sh
│       └── memory-backup.sh
└── config/
    └── memory-config.yaml           # Configuration (retention, backup schedule)
11. Constitutional Compliance
Alignment with Constitution Principles
| Principle | How Memory System Supports It | |---------------|-----------------------------------| | TDD | Tracks test task patterns; reminds agents of test-first approach from past features | | API-First | Stores API contract decisions; surfaces contract patterns during planning | | Observability | Captures logging/metrics decisions; ensures consistency across features | | Simplicity | Warns when complexity patterns emerge; recommends simpler alternatives from past | | Pre-Commit Gates | Stores quality gate outcomes; learns from past gate failures | | E2E Verification | Tracks E2E test patterns; surfaces common E2E challenges |
New Constitutional Gate Candidate:
IX. Institutional Memory: All architectural decisions, lessons learned, and reusable patterns MUST be captured in the agent memory system. Features cannot be marked complete without memory capture verification.
12. Token Efficiency Example
Before Memory System:
/speckit.plan for Feature 004: Reporting Dashboard

Agent reads:
- spec.md (full: 8K tokens)
- constitution.md (full: 3K tokens)
- plan-template.md (full: 2K tokens)
Total: 13K tokens

Generates plan from scratch without context of past features.
After Memory System:
/speckit.plan for Feature 004: Reporting Dashboard

Agent reads:
- spec.md (full: 8K tokens)
- constitution.md (full: 3K tokens)
- plan-template.md (full: 2K tokens)
- Memory injection (summaries): 1.5K tokens
  - "Feature 003 used React Query for data fetching (500 tokens)"
  - "RBAC pattern successful across 3 features (400 tokens)"
  - "PostgreSQL JSONB for flexible schemas (300 tokens)"
  - "TailwindCSS + glassmorphic design (300 tokens)"
Total: 14.5K tokens

BUT: Generates plan 3x faster with informed decisions, avoiding blind exploration.
NET EFFECT: Saves 5-10K tokens in iterative clarifications and research.
ROI: Upfront cost of 1.5K tokens → Saves 5-10K tokens in downstream conversation.
13. Future Enhancements (Beyond MVP)
Semantic Search: Replace FTS5 with vector embeddings (Sentence-BERT) for deeper semantic matching
Trend Analysis: Detect architectural drift over time ("we're moving away from X toward Y")
Multi-Project Support: Track memory across multiple repositories
Visual Memory Map: Graph visualization of decision relationships
AI-Suggested Reflections: Auto-prompt agents to reflect after task completion
Memory Pruning: Archive or summarize old/irrelevant memories
Integration with Git: Link commits to decisions/reflections
Collaboration: Multi-agent memory sharing (team-wide knowledge base)
Conclusion
This memory system transforms spec-kit from a process framework into a learning system. By capturing institutional knowledge, it enables:
✅ Faster development (reuse proven patterns)
✅ Better decisions (informed by past outcomes)
✅ Consistency (architectural alignment across features)
✅ Token efficiency (targeted context injection vs. full artifact reads)
✅ Continuous improvement (learn from reflections)
Integration Philosophy: "Memory should be invisible until needed."
Auto-capture: Silent, seamless
Retrieval: Explicit when desired, injected when beneficial
Commands: Minimal additions (/recall, /reflect, /memory-status)
