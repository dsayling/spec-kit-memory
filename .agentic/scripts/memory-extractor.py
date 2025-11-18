#!/usr/bin/env python3
"""
Spec-Kit Memory System - Artifact Extractor

Parses spec-kit artifacts (spec.md, plan.md, tasks.md, etc.)
and extracts structured data into the memory database.
"""

import re
import json
import os
import sys
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Import memory_lib
import importlib.util
spec = importlib.util.spec_from_file_location(
    "memory_lib",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory-lib.py")
)
memory_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_lib)

MemoryDB = memory_lib.MemoryDB
Feature = memory_lib.Feature
Artifact = memory_lib.Artifact
Decision = memory_lib.Decision
TaskHistory = memory_lib.TaskHistory


class SpecExtractor:
    """Extract feature metadata and description from spec.md"""

    @staticmethod
    def extract(spec_path: str, content: str) -> Tuple[Dict, Optional[str]]:
        """
        Extract feature metadata from spec.md

        Returns: (metadata_dict, description)
        """
        metadata = {}
        description = None

        # Extract feature number from path (e.g., specs/003-feature-name/)
        path_parts = Path(spec_path).parts
        for part in path_parts:
            match = re.match(r'(\d+)-(.+)', part)
            if match:
                metadata['feature_number'] = int(match.group(1))
                metadata['short_name'] = match.group(2)
                break

        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['full_name'] = title_match.group(1).strip()

        # Extract summary/overview section
        summary_section = re.search(
            r'##\s+(?:Summary|Overview)\s*\n+((?:.+\n)*?)(?:\n##|\Z)',
            content,
            re.IGNORECASE | re.MULTILINE
        )
        if summary_section:
            description = summary_section.group(1).strip()

        # Extract priority if present
        priority_match = re.search(r'\*\*Priority[:\s]+([P]\d+)', content, re.IGNORECASE)
        if priority_match:
            metadata['priority'] = priority_match.group(1)

        return metadata, description


class PlanExtractor:
    """Extract decisions from plan.md and research.md"""

    # Common section patterns that indicate decisions
    DECISION_SECTIONS = [
        r'##\s+(?:Tech(?:nology)?\s+Stack(?:\s+Decisions?)?)',
        r'##\s+(?:Architecture(?:\s+Decisions?)?)',
        r'##\s+(?:Security(?:\s+Model)?(?:\s+Decisions?)?)',
        r'##\s+(?:Data\s+Model(?:\s+Decisions?)?)',
        r'##\s+(?:API\s+Design(?:\s+Decisions?)?)',
        r'##\s+(?:Testing\s+Strategy(?:\s+Decisions?)?)',
        r'##\s+(?:Deployment(?:\s+Decisions?)?)',
        r'##\s+(?:Performance(?:\s+Considerations?)?)',
        r'##\s+(?:Observability(?:\s+Strategy)?)',
    ]

    CATEGORY_MAP = {
        'tech': 'technology',
        'architecture': 'architecture',
        'security': 'security',
        'data': 'data-model',
        'api': 'api-design',
        'test': 'testing',
        'deploy': 'deployment',
        'performance': 'performance',
        'observability': 'observability',
    }

    @staticmethod
    def extract_decisions(content: str) -> List[Dict]:
        """
        Extract decision structures from plan.md

        Expected patterns:
        - **Decision**: X
        - **Rationale**: Y
        - **Alternatives**: Z
        """
        decisions = []

        # Split content into sections
        sections = re.split(r'\n##\s+', content)

        for section in sections:
            # Determine category from section header
            category = PlanExtractor._detect_category(section)

            # Find decision blocks
            decision_blocks = re.finditer(
                r'\*\*Decision[:\s]+(.+?)\n'
                r'(?:\*\*Rationale[:\s]+(.+?)\n)?'
                r'(?:\*\*Alternatives?[:\s]+(.+?)\n)?'
                r'(?:\*\*Constraints?[:\s]+(.+?)\n)?',
                section,
                re.DOTALL | re.IGNORECASE
            )

            for match in decision_blocks:
                decision_text = match.group(1).strip()
                rationale = match.group(2).strip() if match.group(2) else None
                alternatives = match.group(3).strip() if match.group(3) else None
                constraints = match.group(4).strip() if match.group(4) else None

                # Extract tags from decision text
                tags = PlanExtractor._extract_tags(decision_text + ' ' + (rationale or ''))

                decisions.append({
                    'category': category,
                    'decision': decision_text,
                    'rationale': rationale,
                    'alternatives': alternatives,
                    'constraints': constraints,
                    'source_section': section.split('\n')[0] if section else None,
                    'tags': json.dumps(tags) if tags else None
                })

        return decisions

    @staticmethod
    def _detect_category(section_text: str) -> str:
        """Detect decision category from section header."""
        header = section_text.split('\n')[0].lower()

        for key, category in PlanExtractor.CATEGORY_MAP.items():
            if key in header:
                return category

        return 'architecture'  # Default

    @staticmethod
    def _extract_tags(text: str) -> List[str]:
        """Extract technology/concept tags from text."""
        common_tags = [
            'fastapi', 'react', 'postgresql', 'sqlite', 'docker', 'kubernetes',
            'playwright', 'pytest', 'pydantic', 'sqlalchemy', 'redis', 'celery',
            'rbac', 'auth', 'oauth', 'jwt', 'email', 'smtp', 'sendgrid',
            'api', 'rest', 'graphql', 'websocket',
            'testing', 'e2e', 'unit', 'integration', 'contract',
            'ci', 'cd', 'github-actions', 'terraform',
            'tdd', 'bdd', 'agile',
            'logging', 'metrics', 'tracing', 'prometheus', 'grafana',
        ]

        text_lower = text.lower()
        tags = [tag for tag in common_tags if tag in text_lower]

        return list(set(tags))  # Remove duplicates


class TaskExtractor:
    """Extract task information from tasks.md"""

    @staticmethod
    def extract_tasks(content: str) -> List[Dict]:
        """
        Extract tasks from tasks.md

        Expected format:
        - [X] [US1-T1] [P] Create user model (backend/models/user.py)
        - [ ] [US1-T2] Implement authentication (backend/auth.py)
        """
        tasks = []

        task_pattern = re.compile(
            r'-\s+\[([X\s])\]\s+\[([^\]]+)\]\s+(?:\[([PS])\]\s+)?(.+?)(?:\s+\(([^)]+)\))?$',
            re.MULTILINE
        )

        for match in task_pattern.finditer(content):
            is_completed = match.group(1) == 'X'
            task_id = match.group(2).strip()
            parallelizable = match.group(3) == 'P' if match.group(3) else False
            description = match.group(4).strip()
            file_paths_str = match.group(5).strip() if match.group(5) else None

            # Parse task_id to extract user story
            user_story = None
            phase = None
            if '-' in task_id:
                parts = task_id.split('-')
                user_story = parts[0]
                # Detect phase from user story
                if user_story.startswith('US'):
                    phase = user_story.lower()
                elif user_story.lower() in ['setup', 'foundational', 'config']:
                    phase = user_story.lower()

            # Parse file paths
            file_paths = None
            if file_paths_str:
                # Split by comma or space
                paths = re.split(r'[,\s]+', file_paths_str)
                file_paths = json.dumps([p.strip() for p in paths if p.strip()])

            # Detect test type from description
            test_type = None
            desc_lower = description.lower()
            if 'unit test' in desc_lower or 'unittest' in desc_lower:
                test_type = 'unit'
            elif 'integration test' in desc_lower:
                test_type = 'integration'
            elif 'e2e' in desc_lower or 'end-to-end' in desc_lower:
                test_type = 'e2e'
            elif 'contract test' in desc_lower:
                test_type = 'contract'

            # Estimate complexity
            complexity = 'moderate'
            if any(word in desc_lower for word in ['simple', 'basic', 'add', 'update']):
                complexity = 'simple'
            elif any(word in desc_lower for word in ['complex', 'implement', 'integrate', 'refactor']):
                complexity = 'complex'

            tasks.append({
                'task_id': task_id,
                'user_story': user_story,
                'phase': phase,
                'description': description,
                'file_paths': file_paths,
                'test_type': test_type,
                'complexity': complexity,
                'status': 'completed' if is_completed else 'pending',
            })

        return tasks


def capture_artifact(db: MemoryDB, feature_dir: str, artifact_type: str,
                     file_path: str) -> bool:
    """
    Capture an artifact and extract structured data.

    Args:
        db: MemoryDB instance
        feature_dir: Path to feature directory (e.g., specs/003-feature-name/)
        artifact_type: Type of artifact (spec, plan, tasks, etc.)
        file_path: Path to artifact file

    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}", file=sys.stderr)
        return False

    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract feature metadata from path or database
    feature_number = None
    path_parts = Path(feature_dir).parts
    for part in path_parts:
        match = re.match(r'(\d+)-(.+)', part)
        if match:
            feature_number = int(match.group(1))
            short_name = match.group(2)
            break

    if not feature_number:
        print(f"❌ Could not extract feature number from path: {feature_dir}", file=sys.stderr)
        return False

    # Get or create feature
    feature = db.get_feature_by_number(feature_number)
    if not feature:
        # Extract from spec if this is the spec artifact
        if artifact_type == 'spec':
            metadata, description = SpecExtractor.extract(feature_dir, content)
            feature = Feature(
                id=None,
                feature_number=metadata.get('feature_number', feature_number),
                short_name=metadata.get('short_name', short_name),
                full_name=metadata.get('full_name', short_name.replace('-', ' ').title()),
                description=description,
                status='planning',
                priority=metadata.get('priority'),
                created_at=None,
                completed_at=None,
                spec_path=feature_dir
            )
            feature.id = db.create_feature(feature)
            print(f"✅ Created feature {feature_number:03d}: {feature.full_name}")
        else:
            print(f"❌ Feature {feature_number:03d} not found in database. Capture spec.md first.", file=sys.stderr)
            return False

    # Save artifact
    artifact = Artifact(
        id=None,
        feature_id=feature.id,
        artifact_type=artifact_type,
        file_path=os.path.abspath(file_path),
        content=content,
        content_hash="",  # Will be computed by save_artifact
        created_at=None,
        updated_at=None,
        version=1
    )
    artifact_id = db.save_artifact(artifact)
    print(f"✅ Saved artifact: {artifact_type} (ID: {artifact_id})")

    # Extract structured data based on type
    if artifact_type == 'plan':
        decisions = PlanExtractor.extract_decisions(content)
        for decision_data in decisions:
            decision = Decision(
                id=None,
                feature_id=feature.id,
                category=decision_data['category'],
                decision=decision_data['decision'],
                rationale=decision_data['rationale'],
                alternatives=decision_data['alternatives'],
                constraints=decision_data['constraints'],
                source_section=decision_data['source_section'],
                tags=decision_data['tags'],
                created_at=None
            )
            decision_id = db.create_decision(decision)
        print(f"✅ Extracted {len(decisions)} decision(s) from plan")

    elif artifact_type == 'tasks':
        tasks = TaskExtractor.extract_tasks(content)
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        for task_data in completed_tasks:
            task = TaskHistory(
                id=None,
                feature_id=feature.id,
                task_id=task_data['task_id'],
                user_story=task_data['user_story'],
                phase=task_data['phase'],
                description=task_data['description'],
                file_paths=task_data['file_paths'],
                test_type=task_data['test_type'],
                duration_minutes=None,
                complexity=task_data['complexity'],
                status=task_data['status'],
                notes=None,
                created_at=None,
                completed_at=None
            )
            task_id = db.create_task(task)
        print(f"✅ Extracted {len(completed_tasks)} completed task(s) from tasks.md")

    return True


def main():
    """Main entry point for memory extractor."""
    import argparse

    parser = argparse.ArgumentParser(description='Extract structured data from spec-kit artifacts')
    parser.add_argument('--feature-dir', required=True, help='Feature directory path')
    parser.add_argument('--type', required=True, choices=[
        'spec', 'plan', 'tasks', 'research', 'data-model', 'quickstart', 'contract', 'checklist'
    ], help='Artifact type')
    parser.add_argument('--file', required=True, help='Path to artifact file')
    parser.add_argument('--db-path', help='Path to memory database')

    args = parser.parse_args()

    try:
        db = MemoryDB(args.db_path)
        success = capture_artifact(db, args.feature_dir, args.type, args.file)
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
