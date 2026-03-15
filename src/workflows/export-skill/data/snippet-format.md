# Context Snippet Format (ADR-L v2)

## Format Rules

- Consistent multi-line format per skill — no adaptive switching
- ~50-80 tokens per skill target (description + exports + optional refs)
- T1-now content only (AST-current, no annotations)
- Description line is the WHEN-TO-USE signal — compressed from SKILL.md frontmatter
- Refs line is the WHERE-TO-LOOK signal — only when references/ exists

## Single Skill Snippet Template

```markdown
{skill-name} → skills/{skill-name}/
  {compressed-description — ~15 words from SKILL.md frontmatter description}
  exports: {export-1}, {export-2}, {export-3}, {export-4}, {export-5}
  refs: {ref-1}, {ref-2}, {ref-3}
```

- **Line 1:** Name + path pointer (always present)
- **Line 2:** Compressed description from SKILL.md frontmatter `description:` field (~15 words, trigger-optimized)
- **Line 3:** Top exports from metadata.json `exports` array (up to 10 for Deep tier, 5 otherwise)
- **Line 4:** Reference file names without extensions (only when `references/` directory exists and contains files)

## Stack Skill Snippet Template

```markdown
{project}-stack → skills/{project}-stack/
  {compressed-description}
  stack: {dep-1}@{v1}, {dep-2}@{v2}, {dep-3}@{v3}
  integrations: {pattern-1}, {pattern-2}, {pattern-3}
```

## Rules

- **description**: Compress SKILL.md frontmatter `description:` to ~15 words. Focus on WHAT it does and WHEN to use it.
- **exports**: Top exports from metadata.json `exports` array (by order as listed)
- **refs**: File names from `references/` directory, without `.md` extension, sorted. Omit line if no references/ exists.
- **stack**: Component versions from metadata.json `components` for stack skills
- **integrations**: Co-import patterns from metadata.json `integrations` for stack skills
- If fewer exports than the limit, list all available
- If no exports data available, omit the exports line
- Skill path is relative to project root
