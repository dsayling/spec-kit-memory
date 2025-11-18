# Spec-Kit Memory - Quick Start Guide

Get up and running with the Spec-Kit Memory System in 5 minutes.

## Installation (30 seconds)

```bash
# Clone or download the spec-kit-memory tool
git clone <repo-url> spec-kit-memory

# Run installation in your spec-kit repository
cd /path/to/your/spec-kit-repo
/path/to/spec-kit-memory/setup-memory.sh

# Or install directly in the spec-kit-memory directory
cd spec-kit-memory
./setup-memory.sh
```

The installer will:
- ✅ Create `.agentic/memory/` directory structure
- ✅ Install all scripts and tools
- ✅ Initialize SQLite database with FTS5 search
- ✅ Update .gitignore

## Basic Commands (2 minutes)

### 1. Check Status
```bash
python3 .agentic/scripts/memory-cli.py stats
```

### 2. Capture a Spec File
```bash
# After creating a spec with /speckit.specify
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/001-my-feature \
  --type spec \
  --file specs/001-my-feature/spec.md
```

### 3. Search Memory
```bash
# Search everything
.agentic/scripts/bash/memory-query.sh "authentication"

# Search decisions only
python3 .agentic/scripts/memory-cli.py search "RBAC" --type decision

# Search by category
python3 .agentic/scripts/memory-cli.py search "FastAPI" --type decision --category technology
```

### 4. Add a Reflection
```bash
python3 .agentic/scripts/memory-cli.py reflect \
  --type lesson \
  --impact high \
  --title "E2E Testing Best Practice" \
  --message "Always use explicit waits in Playwright to avoid CI flakiness"
```

### 5. View a Feature
```bash
# Quick summary
python3 .agentic/scripts/memory-cli.py feature 1 --summary

# Full details
python3 .agentic/scripts/memory-cli.py feature 1 --full
```

## Typical Workflow (2 minutes)

### Step 1: Create a Feature Spec
```bash
# Use your normal spec-kit workflow
/speckit.specify "Add user authentication system"

# Capture to memory
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/001-user-authentication \
  --type spec \
  --file specs/001-user-authentication/spec.md
```

### Step 2: Create a Plan
```bash
# Use spec-kit
/speckit.plan

# Capture to memory (automatically extracts decisions!)
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/001-user-authentication \
  --type plan \
  --file specs/001-user-authentication/plan.md
```

### Step 3: Create Tasks
```bash
# Use spec-kit
/speckit.tasks

# Capture to memory
.agentic/scripts/bash/memory-capture.sh \
  --feature-dir specs/001-user-authentication \
  --type tasks \
  --file specs/001-user-authentication/tasks.md
```

### Step 4: Implement & Reflect
```bash
# After completing implementation
python3 .agentic/scripts/memory-cli.py reflect \
  --type success \
  --impact high \
  --title "OAuth2 Integration Smooth" \
  --message "Using FastAPI's built-in OAuth2 dependencies made implementation straightforward" \
  --feature 1
```

### Step 5: Use Memory for Next Feature
```bash
# Find similar features
python3 .agentic/scripts/memory-cli.py search "authentication"

# Get patterns
python3 .agentic/scripts/memory-cli.py patterns --recommend-for "user login"

# View past decisions
python3 .agentic/scripts/memory-cli.py search "" --type decision --category security
```

## Aliases (Optional)

Add these to your `~/.bashrc` or `~/.zshrc` for faster access:

```bash
# Memory aliases
alias mem='python3 .agentic/scripts/memory-cli.py'
alias mem-search='.agentic/scripts/bash/memory-query.sh'
alias mem-capture='.agentic/scripts/bash/memory-capture.sh'
alias mem-stats='python3 .agentic/scripts/memory-cli.py stats'
alias mem-backup='.agentic/scripts/bash/memory-backup.sh'

# Usage:
# mem stats
# mem search "RBAC"
# mem-capture --feature-dir specs/001-... --type spec --file specs/001-.../spec.md
```

## Common Use Cases

### Find Similar Work
```bash
# Before starting a new feature
mem search "user dashboard"
mem feature 3 --summary  # View similar feature
```

### Learn from Past
```bash
# What did we learn about testing?
mem search "testing" --type reflection

# What technology decisions have we made?
mem search "" --type decision --category technology
```

### Maintain Consistency
```bash
# What patterns do we use?
mem patterns

# What API patterns?
mem patterns --type api

# Get recommendations
mem patterns --recommend-for "REST API endpoint"
```

### Export Knowledge
```bash
# Export a feature
mem export --feature 3 --format json > feature-003.json

# Export all as markdown
mem export --all --format markdown > knowledge-base.md
```

## Tips

1. **Capture Regularly**: Capture artifacts right after creating them while context is fresh

2. **Add Reflections**: After completing features, add high-impact reflections about what worked and what didn't

3. **Search Before Planning**: Before planning a new feature, search for similar work

4. **Review Patterns**: Periodically review patterns to see what's working well

5. **Backup Monthly**: Run `.agentic/scripts/bash/memory-backup.sh` monthly (automatic cleanup keeps last 10)

## Troubleshooting

### "Database not found"
```bash
# Reinitialize
./setup-memory.sh
```

### "Python module not found"
```bash
# Ensure you're using Python 3
python3 --version

# The system uses only standard library modules
```

### "Search not working"
```bash
# Check FTS5 support
python3 -c "import sqlite3; print('fts5' in str(sqlite3.connect(':memory:').execute('PRAGMA compile_options').fetchall()))"
# Should print: True
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review the [plan.md](plan.md) to understand the architecture
- Explore the database schema at `.agentic/memory/schema.sql`
- Customize settings in `.agentic/config/memory-config.yaml`

## Support

The memory system is designed to be self-explanatory, but if you need help:
1. Check `python3 .agentic/scripts/memory-cli.py --help`
2. Review examples in README.md
3. Examine the database: `sqlite3 .agentic/memory/memory.db`

---

**Start building institutional knowledge today! 🧠**
