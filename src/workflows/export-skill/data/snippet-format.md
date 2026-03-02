# Context Snippet Format (ADR-L)

## Format Rules

- One format always — two-line per skill
- No adaptive format switching (consistent for agent parsing)
- ~30 tokens per skill target
- T1-now content only (AST-current, no annotations)

## Single Skill Snippet Template

```markdown
{skill-name} → skills/{skill-name}/
  exports: {export-1}, {export-2}, {export-3}, {export-4}, {export-5}
```

## Stack Skill Snippet Template

```markdown
{project}-stack → skills/{project}-stack/
  stack: {dep-1}@{v1}, {dep-2}@{v2}, {dep-3}@{v3}
  integrations: {pattern-1}, {pattern-2}, {pattern-3}
```

## Rules

- **exports**: Top 5 most-used exports from metadata.json `exports` array
- **stack**: Component versions from metadata.json `components` for stack skills
- **integrations**: Co-import patterns from metadata.json `integrations` for stack skills
- If fewer than 5 exports exist, list all available
- If no exports data available, omit the exports line (name + path only)
- Skill path is relative to project root
