# Scoring Rules

## Default Threshold

**Pass threshold:** 80%

## Category Weights

| Category | Weight | Description |
|----------|--------|-------------|
| Export Coverage | 40% | Percentage of source exports documented in SKILL.md |
| Signature Accuracy | 25% | Documented signatures match actual source signatures |
| Type Coverage | 15% | Types and interfaces referenced are complete |
| Coherence (contextual) | 20% | Cross-references valid, integration patterns complete |
| Coherence (naive) | 0% | Not applicable — weight redistributed to other categories |

## Naive Mode Weight Redistribution

When running in naive mode (no coherence category):
- Export Coverage: 50%
- Signature Accuracy: 30%
- Type Coverage: 20%

## Tier-Dependent Scoring

### Quick Tier (no tools)
- Export Coverage: file/structure existence check only
- Signature Accuracy: skipped (no AST)
- Type Coverage: skipped (no AST)
- Score based on: structural completeness only

### Forge Tier (ast-grep)
- Export Coverage: AST-backed export comparison
- Signature Accuracy: AST-verified signature matching
- Type Coverage: AST-verified type completeness
- Full scoring formula applied

### Deep Tier (ast-grep + gh + QMD)
- All Forge tier checks plus:
- Cross-repository reference verification
- QMD knowledge enrichment for coherence
- Full scoring formula with maximum depth

## Score Calculation

```
score = sum(category_weight * category_score) for each category
category_score = (items_passing / items_total) * 100
```

## Coherence Score Aggregation (Contextual Mode)

```
reference_validity = (valid_references / total_references) * 100
integration_completeness = (complete_patterns / total_patterns) * 100
combined_coherence = (reference_validity * 0.6) + (integration_completeness * 0.4)
```

If no integration patterns exist, combined coherence equals reference validity.

## Result Determination

- score >= threshold → PASS
- score < threshold → FAIL

## Gap Severity

| Severity | Criteria |
|----------|----------|
| Critical | Missing exported function/class documentation |
| High | Signature mismatch between source and SKILL.md |
| Medium | Missing type or interface documentation |
| Low | Missing optional metadata or examples |
| Info | Style suggestions, non-blocking observations |
