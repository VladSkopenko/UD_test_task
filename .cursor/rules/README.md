# Cursor Rules Configuration

This directory contains modular rules for the Cursor AI assistant in `.mdc` format (Markdown + YAML frontmatter).

## 📁 Available Rules

### Always Active

- **`index.mdc`** - Core project rules and coding standards
  - Code style, safety rules, core principles (DRY, KISS, SOLID)

### Auto-Applied (by file pattern)

- **`database.mdc`** - SQLAlchemy models, queries, transactions
  - Auto-applies to: `src/app/**/models/**/*.py`, `migrations/**/*.py`, `src/app/**/repositories/**/*.py`
  - JSONB with lambda structure, N+1 prevention, indexes

- **`schemas.mdc`** - Pydantic schemas, validation, API stability
  - Auto-applies to: `src/app/**/schemas/**/*.py`, `src/app/**/endpoints/**/*.py`
  - Never delete fields (deprecate!), camelCase aliases, type safety

### Manual Reference (use with @)

- **`code-review.mdc`** - Security, performance, race conditions
  - Use when reviewing code or checking for bugs
  - Reference: `@code-review.mdc review this code`

- **`new-feature.mdc`** - Feature development guide
  - Use when implementing new features
  - Reference: `@new-feature.mdc create payment feature`

## 🎯 How to Use

### Automatic Rules
Rules with `globs` or `alwaysApply: true` are automatically activated when working on matching files.

### Manual Reference
Use `@` to reference specific rules when needed:

```
@code-review.mdc check this service for N+1 queries
@new-feature.mdc help me structure a new shipping feature
@database.mdc add indexes to this model
```

## 📚 Migration from Old Setup

This replaces:
- ✅ `.cursorrules` → migrated to `index.mdc`
- ✅ `.claude/contexts/` → migrated to individual `.mdc` files
- ✅ `CLAUDE.md` → migrated to `index.mdc`

The old files can be safely removed after verifying this setup works.

## 🔄 Maintenance

When updating rules:
1. Edit the appropriate `.mdc` file
2. Commit changes to git
3. Rules are automatically picked up by Cursor
4. Team members get updated rules on git pull
