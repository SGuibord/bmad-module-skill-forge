# Skill Brief Schema

## Required Fields

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| name | string | Kebab-case skill name | Must match `[a-z0-9-]+` |
| version | string | Semantic version | Must match `X.Y.Z` pattern, default "1.0.0" |
| source_repo | string | GitHub URL or local path | Must be accessible |
| language | string | Primary programming language | Must be detected or user-specified |
| scope | object | Inclusion/exclusion boundaries | Must have type + at least one pattern |
| description | string | What this skill covers | 1-3 sentences |
| forge_tier | string | Compilation tier | One of: quick, forge, deep |
| created | string | Creation date | ISO date format |
| created_by | string | User who created the brief | From config user_name |

## Scope Object Structure

```yaml
scope:
  type: full-library | specific-modules | public-api
  include:
    - "src/**/*.ts"           # Glob patterns for included files/directories
  exclude:
    - "**/*.test.*"           # Glob patterns for excluded files
    - "**/node_modules/**"
  notes: "Optional notes about scope decisions"
```

## YAML Template

```yaml
---
name: "{skill-name}"
version: "1.0.0"
source_repo: "{github-url-or-local-path}"
language: "{detected-language}"
description: "{brief-description}"
forge_tier: "{quick|forge|deep}"
created: "{date}"
created_by: "{user_name}"
scope:
  type: "{full-library|specific-modules|public-api}"
  include:
    - "{pattern}"
  exclude:
    - "{pattern}"
  notes: "{optional-scope-notes}"
---
```

## Human-Readable Presentation Format

When presenting the brief for confirmation (step 04), display as:

```
Skill Brief: {name}
====================

Target:      {source_repo}
Language:    {language}
Forge Tier:  {forge_tier}
Description: {description}

Scope: {scope.type}
  Include: {scope.include patterns, one per line}
  Exclude: {scope.exclude patterns, one per line}
  Notes:   {scope.notes}

Version:    {version}
Created:    {created}
Created by: {created_by}
```

## Validation Rules

1. `name` must be unique within {forge_data_folder}
2. `source_repo` must be accessible (gh api for GitHub, path exists for local)
3. `language` must be a recognized programming language
4. `scope.type` must be one of the three defined types
5. `scope.include` must have at least one pattern
6. `forge_tier` must match the tier from forge-tier.yaml (or default to quick)
