-- Spec-Kit Memory System Database Schema
-- SQLite3 with FTS5 for full-text search

-- Features: Top-level feature tracking
CREATE TABLE IF NOT EXISTS features (
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
CREATE TABLE IF NOT EXISTS artifacts (
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
CREATE TABLE IF NOT EXISTS decisions (
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
CREATE TABLE IF NOT EXISTS reflections (
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
CREATE TABLE IF NOT EXISTS patterns (
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
CREATE TABLE IF NOT EXISTS task_history (
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
CREATE TABLE IF NOT EXISTS cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_type TEXT NOT NULL CHECK(from_type IN ('decision', 'reflection', 'pattern', 'task')),
    from_id INTEGER NOT NULL,
    to_type TEXT NOT NULL CHECK(to_type IN ('decision', 'reflection', 'pattern', 'task')),
    to_id INTEGER NOT NULL,
    relationship TEXT CHECK(relationship IN ('related', 'depends_on', 'supersedes', 'inspired_by')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_type, from_id, to_type, to_id)
);

-- FTS5 Full-Text Search Tables

-- Artifacts FTS
CREATE VIRTUAL TABLE IF NOT EXISTS artifacts_fts USING fts5(
    artifact_id UNINDEXED,
    feature_name,
    artifact_type,
    content,
    tokenize = 'porter unicode61'
);

-- Decisions FTS
CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
    decision_id UNINDEXED,
    category,
    decision,
    rationale,
    alternatives,
    tags,
    tokenize = 'porter unicode61'
);

-- Reflections FTS
CREATE VIRTUAL TABLE IF NOT EXISTS reflections_fts USING fts5(
    reflection_id UNINDEXED,
    reflection_type,
    title,
    description,
    tags,
    tokenize = 'porter unicode61'
);

-- Patterns FTS
CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
    pattern_id UNINDEXED,
    pattern_name,
    pattern_type,
    description,
    use_cases,
    tags,
    tokenize = 'porter unicode61'
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_features_status ON features(status);
CREATE INDEX IF NOT EXISTS idx_features_number ON features(feature_number);
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifacts_feature ON artifacts(feature_id);
CREATE INDEX IF NOT EXISTS idx_decisions_category ON decisions(category);
CREATE INDEX IF NOT EXISTS idx_decisions_feature ON decisions(feature_id);
CREATE INDEX IF NOT EXISTS idx_reflections_type ON reflections(reflection_type);
CREATE INDEX IF NOT EXISTS idx_reflections_impact ON reflections(impact);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_tasks_feature ON task_history(feature_id);
CREATE INDEX IF NOT EXISTS idx_tasks_story ON task_history(user_story);

-- Triggers to keep FTS tables in sync

-- Artifacts FTS triggers
CREATE TRIGGER IF NOT EXISTS artifacts_ai AFTER INSERT ON artifacts BEGIN
    INSERT INTO artifacts_fts(artifact_id, feature_name, artifact_type, content)
    SELECT NEW.id, f.short_name, NEW.artifact_type, NEW.content
    FROM features f WHERE f.id = NEW.feature_id;
END;

CREATE TRIGGER IF NOT EXISTS artifacts_ad AFTER DELETE ON artifacts BEGIN
    DELETE FROM artifacts_fts WHERE artifact_id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS artifacts_au AFTER UPDATE ON artifacts BEGIN
    DELETE FROM artifacts_fts WHERE artifact_id = OLD.id;
    INSERT INTO artifacts_fts(artifact_id, feature_name, artifact_type, content)
    SELECT NEW.id, f.short_name, NEW.artifact_type, NEW.content
    FROM features f WHERE f.id = NEW.feature_id;
END;

-- Decisions FTS triggers
CREATE TRIGGER IF NOT EXISTS decisions_ai AFTER INSERT ON decisions BEGIN
    INSERT INTO decisions_fts(decision_id, category, decision, rationale, alternatives, tags)
    VALUES (NEW.id, NEW.category, NEW.decision, NEW.rationale, NEW.alternatives, NEW.tags);
END;

CREATE TRIGGER IF NOT EXISTS decisions_ad AFTER DELETE ON decisions BEGIN
    DELETE FROM decisions_fts WHERE decision_id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS decisions_au AFTER UPDATE ON decisions BEGIN
    DELETE FROM decisions_fts WHERE decision_id = OLD.id;
    INSERT INTO decisions_fts(decision_id, category, decision, rationale, alternatives, tags)
    VALUES (NEW.id, NEW.category, NEW.decision, NEW.rationale, NEW.alternatives, NEW.tags);
END;

-- Reflections FTS triggers
CREATE TRIGGER IF NOT EXISTS reflections_ai AFTER INSERT ON reflections BEGIN
    INSERT INTO reflections_fts(reflection_id, reflection_type, title, description, tags)
    VALUES (NEW.id, NEW.reflection_type, NEW.title, NEW.description, NEW.tags);
END;

CREATE TRIGGER IF NOT EXISTS reflections_ad AFTER DELETE ON reflections BEGIN
    DELETE FROM reflections_fts WHERE reflection_id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS reflections_au AFTER UPDATE ON reflections BEGIN
    DELETE FROM reflections_fts WHERE reflection_id = OLD.id;
    INSERT INTO reflections_fts(reflection_id, reflection_type, title, description, tags)
    VALUES (NEW.id, NEW.reflection_type, NEW.title, NEW.description, NEW.tags);
END;

-- Patterns FTS triggers
CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
    INSERT INTO patterns_fts(pattern_id, pattern_name, pattern_type, description, use_cases, tags)
    VALUES (NEW.id, NEW.pattern_name, NEW.pattern_type, NEW.description, NEW.use_cases, NEW.tags);
END;

CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
    DELETE FROM patterns_fts WHERE pattern_id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON patterns BEGIN
    DELETE FROM patterns_fts WHERE pattern_id = OLD.id;
    INSERT INTO patterns_fts(pattern_id, pattern_name, pattern_type, description, use_cases, tags)
    VALUES (NEW.id, NEW.pattern_name, NEW.pattern_type, NEW.description, NEW.use_cases, NEW.tags);
END;
