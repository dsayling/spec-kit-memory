#!/usr/bin/env python3
"""
Spec-Kit Memory System - CLI Tool

Command-line interface for searching, managing, and analyzing
the spec-kit agent memory system.
"""

import argparse
import sys
import json
import os
from datetime import datetime
from typing import Optional

# Add scripts directory to path to import memory_lib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with underscore (Python module naming)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "memory_lib",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory-lib.py")
)
memory_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_lib)

MemoryDB = memory_lib.MemoryDB
Feature = memory_lib.Feature
Decision = memory_lib.Decision
Reflection = memory_lib.Reflection
Pattern = memory_lib.Pattern
TaskHistory = memory_lib.TaskHistory


def format_feature(feature: Feature, full: bool = False) -> str:
    """Format feature for display."""
    output = [
        f"Feature {feature.feature_number:03d}: {feature.full_name}",
        f"  Status: {feature.status}",
        f"  Path: {feature.spec_path}",
    ]

    if full and feature.description:
        output.append(f"  Description: {feature.description}")

    return "\n".join(output)


def format_decision(decision: Decision, feature_name: Optional[str] = None) -> str:
    """Format decision for display."""
    tags = json.loads(decision.tags) if decision.tags else []
    output = [
        f"[{decision.category.upper()}] {decision.decision}",
    ]

    if feature_name:
        output.append(f"  From: {feature_name}")

    if decision.rationale:
        output.append(f"  Rationale: {decision.rationale[:200]}{'...' if len(decision.rationale) > 200 else ''}")

    if tags:
        output.append(f"  Tags: {', '.join(tags)}")

    return "\n".join(output)


def format_reflection(reflection: Reflection, feature_name: Optional[str] = None) -> str:
    """Format reflection for display."""
    tags = json.loads(reflection.tags) if reflection.tags else []
    impact_marker = f"[{reflection.impact.upper()}]" if reflection.impact else ""

    output = [
        f"{impact_marker} {reflection.title}",
        f"  Type: {reflection.reflection_type}",
    ]

    if feature_name:
        output.append(f"  From: {feature_name}")

    output.append(f"  {reflection.description[:200]}{'...' if len(reflection.description) > 200 else ''}")

    if tags:
        output.append(f"  Tags: {', '.join(tags)}")

    return "\n".join(output)


def format_pattern(pattern: Pattern) -> str:
    """Format pattern for display."""
    tags = json.loads(pattern.tags) if pattern.tags else []
    success_pct = pattern.success_rate * 100

    output = [
        f"{pattern.pattern_name} ({pattern.pattern_type})",
        f"  Usage: {pattern.times_used}x, {success_pct:.0f}% success rate",
        f"  {pattern.description[:200]}{'...' if len(pattern.description) > 200 else ''}",
    ]

    if tags:
        output.append(f"  Tags: {', '.join(tags)}")

    return "\n".join(output)


def cmd_search(args):
    """Search command handler."""
    db = MemoryDB(args.db_path)

    if args.type:
        # Type-specific search
        if args.type == 'decision':
            decisions = db.get_decisions_by_category(
                [args.category] if args.category else [
                    'architecture', 'technology', 'data-model', 'api-design',
                    'security', 'performance', 'ux', 'testing', 'deployment', 'observability'
                ],
                tags=[args.query] if args.query else None,
                limit=args.limit
            )
            print(f"\n📊 Found {len(decisions)} decision(s):\n")
            for decision in decisions:
                feature = db.get_feature(decision.feature_id)
                print(format_decision(decision, feature.short_name if feature else None))
                print()

        elif args.type == 'reflection':
            reflections = db.list_reflections()
            # Filter by query if provided
            if args.query:
                query_lower = args.query.lower()
                reflections = [
                    r for r in reflections
                    if query_lower in r.title.lower() or query_lower in r.description.lower()
                ]
            reflections = reflections[:args.limit]

            print(f"\n💡 Found {len(reflections)} reflection(s):\n")
            for reflection in reflections:
                feature = db.get_feature(reflection.feature_id) if reflection.feature_id else None
                print(format_reflection(reflection, feature.short_name if feature else None))
                print()

        elif args.type == 'pattern':
            patterns = db.list_patterns()
            # Filter by query if provided
            if args.query:
                query_lower = args.query.lower()
                patterns = [
                    p for p in patterns
                    if query_lower in p.pattern_name.lower() or query_lower in p.description.lower()
                ]
            patterns = patterns[:args.limit]

            print(f"\n🔧 Found {len(patterns)} pattern(s):\n")
            for pattern in patterns:
                print(format_pattern(pattern))
                print()

        elif args.type == 'feature':
            features = db.list_features()
            # Filter by query if provided
            if args.query:
                query_lower = args.query.lower()
                features = [
                    f for f in features
                    if query_lower in f.short_name.lower() or
                       query_lower in f.full_name.lower() or
                       (f.description and query_lower in f.description.lower())
                ]
            features = features[:args.limit]

            print(f"\n📋 Found {len(features)} feature(s):\n")
            for feature in features:
                print(format_feature(feature))
                print()
    else:
        # Full-text search across all types
        results = db.search_all(args.query, limit=args.limit)
        print(f"\n🔍 Search results for '{args.query}' ({len(results)} found):\n")

        for i, result in enumerate(results, 1):
            icon = {'decision': '📊', 'reflection': '💡', 'pattern': '🔧', 'feature': '📋'}.get(result.result_type, '•')
            print(f"{i}. {icon} [{result.result_type.upper()}] {result.title}")
            if result.source_feature:
                print(f"   From: {result.source_feature}")
            print(f"   {result.summary}")
            if result.tags:
                print(f"   Tags: {', '.join(result.tags)}")
            print()


def cmd_reflect(args):
    """Reflection command handler."""
    db = MemoryDB(args.db_path)

    # Interactive prompts if not provided
    reflection_type = args.type or input("Reflection type (success/challenge/lesson/antipattern/recommendation): ")
    impact = args.impact or input("Impact level (high/medium/low): ")
    title = args.title or input("Title: ")
    message = args.message or input("Description: ")
    category = args.category or input("Category (optional, e.g., architecture, technology): ") or None

    # Auto-extract tags from message
    common_tech_terms = [
        'fastapi', 'react', 'postgresql', 'sqlite', 'docker', 'playwright',
        'pytest', 'pydantic', 'sqlalchemy', 'rbac', 'auth', 'email', 'api',
        'testing', 'e2e', 'ci', 'cd', 'tdd'
    ]
    tags = [term for term in common_tech_terms if term in message.lower()]

    # Get current feature if in a spec directory
    feature_id = None
    if args.feature:
        feature = db.get_feature_by_number(args.feature)
        if feature:
            feature_id = feature.id

    reflection = Reflection(
        id=None,
        feature_id=feature_id,
        reflection_type=reflection_type,
        title=title,
        description=message,
        impact=impact,
        category=category,
        related_task_ids=None,
        tags=json.dumps(tags) if tags else None,
        created_at=None
    )

    reflection_id = db.create_reflection(reflection)
    print(f"\n✅ Reflection saved (ID: {reflection_id})")
    print(f"   Type: {reflection_type}, Impact: {impact}")
    if tags:
        print(f"   Auto-detected tags: {', '.join(tags)}")
    print("   This will inform future tasks.\n")


def cmd_feature(args):
    """Feature command handler."""
    db = MemoryDB(args.db_path)

    feature = db.get_feature_by_number(args.feature_number)
    if not feature:
        print(f"❌ Feature {args.feature_number:03d} not found")
        return

    if args.summary:
        summary = db.get_feature_summary(feature.id)
        print(f"\n📋 Feature {feature.feature_number:03d}: {feature.full_name}\n")
        print(f"Status: {feature.status}")
        print(f"Path: {feature.spec_path}")
        if feature.description:
            print(f"Description: {feature.description[:200]}{'...' if len(feature.description) > 200 else ''}")
        print(f"\n📊 Decisions: {summary['decision_count']}")
        for d in summary['key_decisions']:
            print(f"  • [{d['category']}] {d['decision']}")
        print(f"\n💡 High-Impact Reflections: {len(summary['key_reflections'])}")
        for r in summary['key_reflections']:
            print(f"  • [{r['type']}] {r['title']}")
        print()
    elif args.full:
        print(f"\n📋 Feature {feature.feature_number:03d}: {feature.full_name}\n")
        print(format_feature(feature, full=True))

        decisions = db.list_decisions(feature_id=feature.id)
        if decisions:
            print(f"\n📊 Decisions ({len(decisions)}):\n")
            for decision in decisions:
                print(format_decision(decision))
                print()

        reflections = db.list_reflections(feature_id=feature.id)
        if reflections:
            print(f"\n💡 Reflections ({len(reflections)}):\n")
            for reflection in reflections:
                print(format_reflection(reflection))
                print()

        tasks = db.list_tasks(feature_id=feature.id, status='completed')
        if tasks:
            print(f"\n✅ Completed Tasks ({len(tasks)}):\n")
            for task in tasks[:10]:  # Show first 10
                print(f"  • [{task.task_id}] {task.description}")
            if len(tasks) > 10:
                print(f"  ... and {len(tasks) - 10} more")
            print()


def cmd_patterns(args):
    """Patterns command handler."""
    db = MemoryDB(args.db_path)

    if args.recommend_for:
        # Search for relevant patterns
        results = db.search_all(args.recommend_for, limit=5)
        pattern_results = [r for r in results if r.result_type == 'pattern']

        print(f"\n🔧 Recommended patterns for '{args.recommend_for}':\n")
        for result in pattern_results:
            pattern = db.get_pattern(result.id) if hasattr(db, 'get_pattern') else None
            if pattern:
                print(format_pattern(pattern))
            else:
                print(f"  • {result.title}")
                print(f"    {result.summary}")
            print()

    elif args.type:
        patterns = db.find_patterns_by_type(args.type, limit=20)
        print(f"\n🔧 {args.type.title()} Patterns ({len(patterns)}):\n")
        for pattern in patterns:
            print(format_pattern(pattern))
            print()
    else:
        patterns = db.list_patterns()
        print(f"\n🔧 All Patterns ({len(patterns)}):\n")
        for pattern in patterns:
            print(format_pattern(pattern))
            print()


def cmd_stats(args):
    """Stats command handler."""
    db = MemoryDB(args.db_path)
    stats = db.get_stats()

    print("\n" + "="*60)
    print("📊 MEMORY DATABASE STATISTICS")
    print("="*60)

    print(f"\n📁 Location: {stats['db_path']}")
    print(f"💾 Size: {stats['db_size_mb']:.2f} MB")

    print(f"\n📋 Features Tracked: {stats['total_features']}")
    if stats['features']:
        for status, count in stats['features'].items():
            print(f"  • {status}: {count}")

    print(f"\n📄 Artifacts Stored: {stats['total_artifacts']}")
    if stats['artifacts']:
        for artifact_type, count in stats['artifacts'].items():
            print(f"  • {artifact_type}: {count}")

    print(f"\n📊 Decisions Recorded: {stats['total_decisions']}")
    if stats['decisions_by_category']:
        print("  Top Categories:")
        for category, count in list(stats['decisions_by_category'].items())[:5]:
            print(f"  • {category}: {count}")

    print(f"\n💡 Reflections Captured: {stats['total_reflections']}")
    print(f"🔧 Patterns Extracted: {stats['total_patterns']}")
    print(f"✅ Tasks Completed: {stats['total_tasks']}")

    if stats['top_patterns']:
        print("\n🏆 Most Used Patterns:")
        for pattern in stats['top_patterns']:
            print(f"  • {pattern['name']} (used {pattern['used']}x, {pattern['success_rate']*100:.0f}% success)")

    if stats['recent_high_impact_reflections']:
        print("\n⭐ Recent High-Impact Reflections:")
        for reflection in stats['recent_high_impact_reflections']:
            print(f"  • \"{reflection['title']}\" ({reflection['feature']})")

    print("\n" + "="*60 + "\n")


def cmd_export(args):
    """Export command handler."""
    db = MemoryDB(args.db_path)

    if args.feature:
        feature = db.get_feature_by_number(args.feature)
        if not feature:
            print(f"❌ Feature {args.feature:03d} not found")
            return

        data = {
            'feature': feature.__dict__,
            'decisions': [d.__dict__ for d in db.list_decisions(feature_id=feature.id)],
            'reflections': [r.__dict__ for r in db.list_reflections(feature_id=feature.id)],
            'tasks': [t.__dict__ for t in db.list_tasks(feature_id=feature.id)],
        }

        if args.format == 'json':
            print(json.dumps(data, indent=2, default=str))
        elif args.format == 'markdown':
            print(f"# Feature {feature.feature_number:03d}: {feature.full_name}\n")
            print(f"**Status:** {feature.status}\n")
            if feature.description:
                print(f"## Description\n{feature.description}\n")
            if data['decisions']:
                print(f"## Decisions ({len(data['decisions'])})\n")
                for d in data['decisions']:
                    print(f"### [{d['category']}] {d['decision']}\n")
                    if d['rationale']:
                        print(f"{d['rationale']}\n")
            if data['reflections']:
                print(f"## Reflections ({len(data['reflections'])})\n")
                for r in data['reflections']:
                    print(f"### {r['title']}\n")
                    print(f"**Type:** {r['reflection_type']} | **Impact:** {r['impact']}\n")
                    print(f"{r['description']}\n")

    elif args.all:
        features = db.list_features()
        data = {
            'features': [f.__dict__ for f in features],
            'stats': db.get_stats()
        }

        if args.format == 'json':
            print(json.dumps(data, indent=2, default=str))
        elif args.format == 'markdown':
            print("# Spec-Kit Memory Export\n")
            print(f"**Generated:** {datetime.now().isoformat()}\n")
            print(f"## Summary\n")
            print(f"- Features: {len(features)}")
            print(f"- Decisions: {data['stats']['total_decisions']}")
            print(f"- Reflections: {data['stats']['total_reflections']}")
            print(f"- Patterns: {data['stats']['total_patterns']}\n")
            print("## Features\n")
            for feature in features:
                print(f"### {feature.feature_number:03d}: {feature.full_name}")
                print(f"**Status:** {feature.status}\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Spec-Kit Memory System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search
  memory-cli search "RBAC patterns"
  memory-cli search "email integration" --type decision --category technology

  # Add reflection
  memory-cli reflect --type lesson --impact high --title "E2E testing" --message "..."

  # View feature
  memory-cli feature 3 --summary
  memory-cli feature 3 --full

  # Patterns
  memory-cli patterns --type api
  memory-cli patterns --recommend-for "user authentication"

  # Stats
  memory-cli stats

  # Export
  memory-cli export --feature 3 --format json
  memory-cli export --all --format markdown
        """
    )

    parser.add_argument('--db-path', help='Path to memory database (default: .agentic/memory/memory.db)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search memory database')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', choices=['decision', 'reflection', 'pattern', 'feature'],
                              help='Search specific type')
    search_parser.add_argument('--category', help='Filter by category (for decisions)')
    search_parser.add_argument('--limit', type=int, default=10, help='Max results')
    search_parser.set_defaults(func=cmd_search)

    # Reflect command
    reflect_parser = subparsers.add_parser('reflect', help='Add a reflection')
    reflect_parser.add_argument('--type', choices=['success', 'challenge', 'lesson', 'antipattern', 'recommendation'],
                               help='Reflection type')
    reflect_parser.add_argument('--impact', choices=['high', 'medium', 'low'], help='Impact level')
    reflect_parser.add_argument('--title', help='Reflection title')
    reflect_parser.add_argument('--message', help='Reflection description')
    reflect_parser.add_argument('--category', help='Category')
    reflect_parser.add_argument('--feature', type=int, help='Associate with feature number')
    reflect_parser.set_defaults(func=cmd_reflect)

    # Feature command
    feature_parser = subparsers.add_parser('feature', help='View feature details')
    feature_parser.add_argument('feature_number', type=int, help='Feature number')
    feature_parser.add_argument('--summary', action='store_true', help='Show brief summary')
    feature_parser.add_argument('--full', action='store_true', help='Show full details')
    feature_parser.set_defaults(func=cmd_feature)

    # Patterns command
    patterns_parser = subparsers.add_parser('patterns', help='View patterns')
    patterns_parser.add_argument('--type', choices=['code', 'architecture', 'testing', 'api', 'database', 'ui'],
                                help='Pattern type')
    patterns_parser.add_argument('--recommend-for', help='Get pattern recommendations for query')
    patterns_parser.set_defaults(func=cmd_patterns)

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    stats_parser.set_defaults(func=cmd_stats)

    # Export command
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('--feature', type=int, help='Export specific feature')
    export_parser.add_argument('--all', action='store_true', help='Export all data')
    export_parser.add_argument('--format', choices=['json', 'markdown'], default='json',
                              help='Output format')
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
