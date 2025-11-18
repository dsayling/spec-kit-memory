#!/usr/bin/env python3
"""
Spec-Kit Memory System - Core Library

Provides database access, search functionality, and memory operations
for the spec-kit agent memory system.
"""

import sqlite3
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager


# Data Models
@dataclass
class Feature:
    id: Optional[int]
    feature_number: int
    short_name: str
    full_name: str
    description: Optional[str]
    status: str
    priority: Optional[str]
    created_at: Optional[str]
    completed_at: Optional[str]
    spec_path: str


@dataclass
class Artifact:
    id: Optional[int]
    feature_id: int
    artifact_type: str
    file_path: str
    content: str
    content_hash: str
    created_at: Optional[str]
    updated_at: Optional[str]
    version: int


@dataclass
class Decision:
    id: Optional[int]
    feature_id: int
    category: str
    decision: str
    rationale: Optional[str]
    alternatives: Optional[str]
    constraints: Optional[str]
    source_section: Optional[str]
    tags: Optional[str]  # JSON array as string
    created_at: Optional[str]


@dataclass
class Reflection:
    id: Optional[int]
    feature_id: Optional[int]
    reflection_type: str
    title: str
    description: str
    impact: Optional[str]
    category: Optional[str]
    related_task_ids: Optional[str]  # JSON array as string
    tags: Optional[str]  # JSON array as string
    created_at: Optional[str]


@dataclass
class Pattern:
    id: Optional[int]
    pattern_name: str
    pattern_type: str
    description: str
    use_cases: Optional[str]
    implementation_notes: Optional[str]
    example_code: Optional[str]
    source_feature_ids: Optional[str]  # JSON array as string
    times_used: int
    success_rate: float
    tags: Optional[str]  # JSON array as string
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class TaskHistory:
    id: Optional[int]
    feature_id: int
    task_id: str
    user_story: Optional[str]
    phase: Optional[str]
    description: str
    file_paths: Optional[str]  # JSON array as string
    test_type: Optional[str]
    duration_minutes: Optional[int]
    complexity: Optional[str]
    status: str
    notes: Optional[str]
    created_at: Optional[str]
    completed_at: Optional[str]


@dataclass
class SearchResult:
    result_type: str  # 'feature', 'decision', 'reflection', 'pattern'
    id: int
    title: str
    summary: str
    relevance_score: float
    source_feature: Optional[str]
    tags: List[str]


class MemoryDB:
    """Core database access layer for the spec-kit memory system."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        if db_path is None:
            # Default to .agentic/memory/memory.db relative to git root
            git_root = self._find_git_root()
            db_path = os.path.join(git_root, '.agentic', 'memory', 'memory.db')

        self.db_path = db_path
        self.schema_path = os.path.join(
            os.path.dirname(db_path), 'schema.sql'
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database if it doesn't exist
        if not os.path.exists(db_path):
            self.initialize_db()

    @staticmethod
    def _find_git_root() -> str:
        """Find the git repository root directory."""
        current = os.getcwd()
        while current != '/':
            if os.path.exists(os.path.join(current, '.git')):
                return current
            current = os.path.dirname(current)
        return os.getcwd()  # Fallback to current directory

    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_db(self):
        """Initialize the database from schema.sql."""
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_sql)

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    # Feature operations
    def create_feature(self, feature: Feature) -> int:
        """Create a new feature record."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO features (
                    feature_number, short_name, full_name, description,
                    status, priority, spec_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                feature.feature_number, feature.short_name, feature.full_name,
                feature.description, feature.status, feature.priority,
                feature.spec_path
            ))
            return cursor.lastrowid

    def get_feature(self, feature_id: int) -> Optional[Feature]:
        """Get feature by ID."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM features WHERE id = ?", (feature_id,)
            ).fetchone()
            if row:
                return Feature(**dict(row))
            return None

    def get_feature_by_number(self, feature_number: int) -> Optional[Feature]:
        """Get feature by feature number."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM features WHERE feature_number = ?", (feature_number,)
            ).fetchone()
            if row:
                return Feature(**dict(row))
            return None

    def update_feature_status(self, feature_id: int, status: str,
                             completed_at: Optional[str] = None):
        """Update feature status."""
        with self.get_connection() as conn:
            if status == 'completed' and completed_at is None:
                completed_at = datetime.now().isoformat()
            conn.execute("""
                UPDATE features SET status = ?, completed_at = ?
                WHERE id = ?
            """, (status, completed_at, feature_id))

    def list_features(self, status: Optional[str] = None) -> List[Feature]:
        """List all features, optionally filtered by status."""
        with self.get_connection() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM features WHERE status = ? ORDER BY feature_number DESC",
                    (status,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM features ORDER BY feature_number DESC"
                ).fetchall()
            return [Feature(**dict(row)) for row in rows]

    # Artifact operations
    def save_artifact(self, artifact: Artifact) -> int:
        """Save or update an artifact."""
        content_hash = self._compute_hash(artifact.content)

        with self.get_connection() as conn:
            # Check if artifact exists
            existing = conn.execute("""
                SELECT id, content_hash, version FROM artifacts
                WHERE feature_id = ? AND artifact_type = ? AND file_path = ?
            """, (artifact.feature_id, artifact.artifact_type, artifact.file_path)).fetchone()

            if existing:
                # Update if content changed
                if existing['content_hash'] != content_hash:
                    new_version = existing['version'] + 1
                    conn.execute("""
                        UPDATE artifacts
                        SET content = ?, content_hash = ?,
                            updated_at = CURRENT_TIMESTAMP, version = ?
                        WHERE id = ?
                    """, (artifact.content, content_hash, new_version, existing['id']))
                    return existing['id']
                return existing['id']
            else:
                # Insert new
                cursor = conn.execute("""
                    INSERT INTO artifacts (
                        feature_id, artifact_type, file_path, content, content_hash
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    artifact.feature_id, artifact.artifact_type,
                    artifact.file_path, artifact.content, content_hash
                ))
                return cursor.lastrowid

    def get_artifact(self, artifact_id: int) -> Optional[Artifact]:
        """Get artifact by ID."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM artifacts WHERE id = ?", (artifact_id,)
            ).fetchone()
            if row:
                return Artifact(**dict(row))
            return None

    def list_artifacts(self, feature_id: Optional[int] = None,
                      artifact_type: Optional[str] = None) -> List[Artifact]:
        """List artifacts with optional filters."""
        with self.get_connection() as conn:
            query = "SELECT * FROM artifacts WHERE 1=1"
            params = []

            if feature_id is not None:
                query += " AND feature_id = ?"
                params.append(feature_id)
            if artifact_type is not None:
                query += " AND artifact_type = ?"
                params.append(artifact_type)

            query += " ORDER BY updated_at DESC"
            rows = conn.execute(query, params).fetchall()
            return [Artifact(**dict(row)) for row in rows]

    # Decision operations
    def create_decision(self, decision: Decision) -> int:
        """Create a new decision record."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO decisions (
                    feature_id, category, decision, rationale, alternatives,
                    constraints, source_section, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision.feature_id, decision.category, decision.decision,
                decision.rationale, decision.alternatives, decision.constraints,
                decision.source_section, decision.tags
            ))
            return cursor.lastrowid

    def get_decisions_by_category(self, categories: List[str],
                                  tags: Optional[List[str]] = None,
                                  limit: int = 10) -> List[Decision]:
        """Get decisions filtered by category and optional tags."""
        with self.get_connection() as conn:
            placeholders = ','.join('?' * len(categories))
            query = f"""
                SELECT * FROM decisions
                WHERE category IN ({placeholders})
            """
            params = categories.copy()

            if tags:
                # Simple tag matching (contains any of the tags)
                tag_conditions = ' OR '.join(['tags LIKE ?' for _ in tags])
                query += f" AND ({tag_conditions})"
                params.extend([f'%"{tag}"%' for tag in tags])

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [Decision(**dict(row)) for row in rows]

    def list_decisions(self, feature_id: Optional[int] = None) -> List[Decision]:
        """List all decisions, optionally for a specific feature."""
        with self.get_connection() as conn:
            if feature_id is not None:
                rows = conn.execute(
                    "SELECT * FROM decisions WHERE feature_id = ? ORDER BY created_at",
                    (feature_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM decisions ORDER BY created_at DESC"
                ).fetchall()
            return [Decision(**dict(row)) for row in rows]

    # Reflection operations
    def create_reflection(self, reflection: Reflection) -> int:
        """Create a new reflection record."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO reflections (
                    feature_id, reflection_type, title, description, impact,
                    category, related_task_ids, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reflection.feature_id, reflection.reflection_type,
                reflection.title, reflection.description, reflection.impact,
                reflection.category, reflection.related_task_ids, reflection.tags
            ))
            return cursor.lastrowid

    def get_reflections_by_category(self, category: str,
                                    impact: Optional[str] = None,
                                    limit: int = 10) -> List[Reflection]:
        """Get reflections by category and optional impact level."""
        with self.get_connection() as conn:
            query = "SELECT * FROM reflections WHERE category = ?"
            params = [category]

            if impact:
                query += " AND impact = ?"
                params.append(impact)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [Reflection(**dict(row)) for row in rows]

    def list_reflections(self, feature_id: Optional[int] = None,
                        reflection_type: Optional[str] = None) -> List[Reflection]:
        """List reflections with optional filters."""
        with self.get_connection() as conn:
            query = "SELECT * FROM reflections WHERE 1=1"
            params = []

            if feature_id is not None:
                query += " AND feature_id = ?"
                params.append(feature_id)
            if reflection_type is not None:
                query += " AND reflection_type = ?"
                params.append(reflection_type)

            query += " ORDER BY created_at DESC"
            rows = conn.execute(query, params).fetchall()
            return [Reflection(**dict(row)) for row in rows]

    # Pattern operations
    def create_pattern(self, pattern: Pattern) -> int:
        """Create a new pattern record."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO patterns (
                    pattern_name, pattern_type, description, use_cases,
                    implementation_notes, example_code, source_feature_ids,
                    times_used, success_rate, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_name, pattern.pattern_type, pattern.description,
                pattern.use_cases, pattern.implementation_notes, pattern.example_code,
                pattern.source_feature_ids, pattern.times_used, pattern.success_rate,
                pattern.tags
            ))
            return cursor.lastrowid

    def find_patterns_by_type(self, pattern_type: str,
                             tags: Optional[List[str]] = None,
                             limit: int = 5) -> List[Pattern]:
        """Get patterns by type and optional tags."""
        with self.get_connection() as conn:
            query = "SELECT * FROM patterns WHERE pattern_type = ?"
            params = [pattern_type]

            if tags:
                tag_conditions = ' OR '.join(['tags LIKE ?' for _ in tags])
                query += f" AND ({tag_conditions})"
                params.extend([f'%"{tag}"%' for tag in tags])

            query += " ORDER BY success_rate DESC, times_used DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [Pattern(**dict(row)) for row in rows]

    def update_pattern_usage(self, pattern_id: int, success: bool = True):
        """Update pattern usage statistics."""
        with self.get_connection() as conn:
            pattern = conn.execute(
                "SELECT times_used, success_rate FROM patterns WHERE id = ?",
                (pattern_id,)
            ).fetchone()

            if pattern:
                new_times_used = pattern['times_used'] + 1
                # Update success rate: (old_rate * old_count + new_success) / new_count
                old_successes = pattern['success_rate'] * pattern['times_used']
                new_successes = old_successes + (1.0 if success else 0.0)
                new_success_rate = new_successes / new_times_used

                conn.execute("""
                    UPDATE patterns
                    SET times_used = ?, success_rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_times_used, new_success_rate, pattern_id))

    def list_patterns(self, pattern_type: Optional[str] = None) -> List[Pattern]:
        """List all patterns, optionally filtered by type."""
        with self.get_connection() as conn:
            if pattern_type:
                rows = conn.execute(
                    "SELECT * FROM patterns WHERE pattern_type = ? ORDER BY success_rate DESC, times_used DESC",
                    (pattern_type,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM patterns ORDER BY success_rate DESC, times_used DESC"
                ).fetchall()
            return [Pattern(**dict(row)) for row in rows]

    # Task history operations
    def create_task(self, task: TaskHistory) -> int:
        """Create a new task history record."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO task_history (
                    feature_id, task_id, user_story, phase, description,
                    file_paths, test_type, duration_minutes, complexity,
                    status, notes, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.feature_id, task.task_id, task.user_story, task.phase,
                task.description, task.file_paths, task.test_type,
                task.duration_minutes, task.complexity, task.status,
                task.notes, task.completed_at
            ))
            return cursor.lastrowid

    def list_tasks(self, feature_id: Optional[int] = None,
                  status: Optional[str] = None) -> List[TaskHistory]:
        """List task history with optional filters."""
        with self.get_connection() as conn:
            query = "SELECT * FROM task_history WHERE 1=1"
            params = []

            if feature_id is not None:
                query += " AND feature_id = ?"
                params.append(feature_id)
            if status is not None:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC"
            rows = conn.execute(query, params).fetchall()
            return [TaskHistory(**dict(row)) for row in rows]

    # Full-text search operations
    def search_all(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Full-text search across all memory types."""
        results = []

        with self.get_connection() as conn:
            # Search decisions
            decision_rows = conn.execute("""
                SELECT d.id, d.category, d.decision, d.rationale, d.tags,
                       f.short_name as feature_name,
                       decisions_fts.rank as relevance
                FROM decisions_fts
                JOIN decisions d ON decisions_fts.decision_id = d.id
                JOIN features f ON d.feature_id = f.id
                WHERE decisions_fts MATCH ?
                ORDER BY relevance
                LIMIT ?
            """, (query, limit)).fetchall()

            for row in decision_rows:
                tags = json.loads(row['tags']) if row['tags'] else []
                results.append(SearchResult(
                    result_type='decision',
                    id=row['id'],
                    title=f"{row['category']}: {row['decision'][:100]}",
                    summary=row['rationale'][:200] if row['rationale'] else "",
                    relevance_score=abs(row['relevance']),
                    source_feature=row['feature_name'],
                    tags=tags
                ))

            # Search reflections
            reflection_rows = conn.execute("""
                SELECT r.id, r.title, r.description, r.reflection_type, r.impact, r.tags,
                       f.short_name as feature_name,
                       reflections_fts.rank as relevance
                FROM reflections_fts
                JOIN reflections r ON reflections_fts.reflection_id = r.id
                LEFT JOIN features f ON r.feature_id = f.id
                WHERE reflections_fts MATCH ?
                ORDER BY relevance
                LIMIT ?
            """, (query, limit)).fetchall()

            for row in reflection_rows:
                tags = json.loads(row['tags']) if row['tags'] else []
                results.append(SearchResult(
                    result_type='reflection',
                    id=row['id'],
                    title=row['title'],
                    summary=f"[{row['impact'] or 'N/A'}] {row['description'][:200]}",
                    relevance_score=abs(row['relevance']),
                    source_feature=row['feature_name'],
                    tags=tags
                ))

            # Search patterns
            pattern_rows = conn.execute("""
                SELECT p.id, p.pattern_name, p.description, p.pattern_type,
                       p.times_used, p.success_rate, p.tags,
                       patterns_fts.rank as relevance
                FROM patterns_fts
                JOIN patterns p ON patterns_fts.pattern_id = p.id
                WHERE patterns_fts MATCH ?
                ORDER BY relevance
                LIMIT ?
            """, (query, limit)).fetchall()

            for row in pattern_rows:
                tags = json.loads(row['tags']) if row['tags'] else []
                results.append(SearchResult(
                    result_type='pattern',
                    id=row['id'],
                    title=row['pattern_name'],
                    summary=f"{row['description'][:200]} (used {row['times_used']}x, {row['success_rate']*100:.0f}% success)",
                    relevance_score=abs(row['relevance']),
                    source_feature=None,
                    tags=tags
                ))

        # Sort by relevance and return top results
        results.sort(key=lambda x: x.relevance_score)
        return results[:limit]

    def find_similar_features(self, description: str, limit: int = 3) -> List[Feature]:
        """Find features with similar descriptions using FTS."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT f.*, artifacts_fts.rank as relevance
                FROM artifacts_fts
                JOIN artifacts a ON artifacts_fts.artifact_id = a.id
                JOIN features f ON a.feature_id = f.id
                WHERE artifacts_fts MATCH ? AND a.artifact_type = 'spec'
                GROUP BY f.id
                ORDER BY relevance
                LIMIT ?
            """, (description, limit)).fetchall()

            return [Feature(**{k: row[k] for k in row.keys() if k != 'relevance'})
                   for row in rows]

    def get_feature_summary(self, feature_id: int) -> Dict[str, Any]:
        """Get a token-efficient summary of a feature."""
        feature = self.get_feature(feature_id)
        if not feature:
            return {}

        decisions = self.list_decisions(feature_id=feature_id)
        reflections = self.list_reflections(feature_id=feature_id)

        return {
            'feature': asdict(feature),
            'decision_count': len(decisions),
            'key_decisions': [
                {
                    'category': d.category,
                    'decision': d.decision,
                    'rationale': d.rationale[:100] if d.rationale else ""
                }
                for d in decisions[:5]
            ],
            'reflection_count': len(reflections),
            'key_reflections': [
                {
                    'type': r.reflection_type,
                    'title': r.title,
                    'impact': r.impact
                }
                for r in reflections if r.impact == 'high'
            ][:3]
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get memory database statistics."""
        with self.get_connection() as conn:
            stats = {
                'db_path': self.db_path,
                'db_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0,
            }

            # Feature counts
            feature_rows = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM features
                GROUP BY status
            """).fetchall()
            stats['features'] = {row['status']: row['count'] for row in feature_rows}
            stats['total_features'] = sum(stats['features'].values())

            # Artifact counts
            artifact_rows = conn.execute("""
                SELECT artifact_type, COUNT(*) as count
                FROM artifacts
                GROUP BY artifact_type
            """).fetchall()
            stats['artifacts'] = {row['artifact_type']: row['count'] for row in artifact_rows}
            stats['total_artifacts'] = sum(stats['artifacts'].values())

            # Decision counts
            decision_rows = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM decisions
                GROUP BY category
                ORDER BY count DESC
            """).fetchall()
            stats['decisions_by_category'] = {row['category']: row['count'] for row in decision_rows}
            stats['total_decisions'] = sum(stats['decisions_by_category'].values())

            # Reflection counts
            stats['total_reflections'] = conn.execute(
                "SELECT COUNT(*) as count FROM reflections"
            ).fetchone()['count']

            # Pattern counts
            stats['total_patterns'] = conn.execute(
                "SELECT COUNT(*) as count FROM patterns"
            ).fetchone()['count']

            # Task counts
            stats['total_tasks'] = conn.execute(
                "SELECT COUNT(*) as count FROM task_history"
            ).fetchone()['count']

            # Top patterns
            pattern_rows = conn.execute("""
                SELECT pattern_name, times_used, success_rate
                FROM patterns
                ORDER BY times_used DESC, success_rate DESC
                LIMIT 5
            """).fetchall()
            stats['top_patterns'] = [
                {
                    'name': row['pattern_name'],
                    'used': row['times_used'],
                    'success_rate': row['success_rate']
                }
                for row in pattern_rows
            ]

            # Recent high-impact reflections
            reflection_rows = conn.execute("""
                SELECT r.title, f.feature_number, f.short_name
                FROM reflections r
                LEFT JOIN features f ON r.feature_id = f.id
                WHERE r.impact = 'high'
                ORDER BY r.created_at DESC
                LIMIT 5
            """).fetchall()
            stats['recent_high_impact_reflections'] = [
                {
                    'title': row['title'],
                    'feature': f"{row['feature_number']:03d}" if row['feature_number'] else "global"
                }
                for row in reflection_rows
            ]

            return stats
