# Extraction Patterns by Tier

## Quick Tier (No AST)

Source reading via gh_bridge — infer exports from file structure and content.

### Strategy
1. `gh_bridge.list_tree(owner, repo, branch)` — map source structure
2. Identify entry points: index files, main exports, public modules
3. `gh_bridge.read_file(owner, repo, path)` — read each entry point
4. Extract: exported function names, parameter lists, return types (from signatures)
5. Infer types from JSDoc, docstrings, type annotations in source

### Confidence
- All results: T1-low (source reading without structural verification)
- No co-import detection available
- No AST-backed line numbers

### Supported Patterns
- `export function name(...)` / `export const name = ...` (JS/TS)
- `pub fn name(...)` (Rust)
- `def name(...)` with `__all__` (Python)
- `func Name(...)` (Go, capitalized = exported)

---

## Forge Tier (AST Available)

Structural extraction via ast_bridge — verified exports with line-level citations.

### Strategy
1. Detect language from brief or file extensions
2. `ast_bridge.scan_definitions(path, language)` — extract all exports
3. For each export: function name, full signature, parameter types, return type, line number
4. `ast_bridge.detect_co_imports(path, libraries[])` — find integration points
5. Build extraction rules YAML for reproducibility

### Confidence
- Exported functions with full signatures: T1 (AST-verified)
- Type definitions and interfaces: T1
- Co-import patterns: T1
- Internal/private functions: excluded (not part of public API)

### ast-grep Patterns
- JS/TS: `export function $NAME($$$PARAMS): $RET` / `export const $NAME`
- Rust: `pub fn $NAME($$$PARAMS) -> $RET`
- Python: function definitions within `__all__` list
- Go: capitalized function definitions

---

## Deep Tier (AST + QMD)

Same extraction as Forge tier. Deep tier adds enrichment in step-04, not extraction.

### Strategy
- Identical to Forge tier extraction
- QMD enrichment happens in the next step (step-04-enrich)
- Extraction results carry forward unchanged

### Confidence
- Extraction: same as Forge (T1)
- Enrichment annotations added in step-04: T2

---

## Tier Degradation Rules

### Remote Source at Forge/Deep Tier

When `source_repo` is a remote URL (GitHub URL or owner/repo format) and the tier is Forge or Deep:

- **ast-grep requires local files** — it cannot operate on remote URLs

**Ephemeral clone strategy (preferred):**

1. Check `git` availability (`git --version`). `git` is effectively guaranteed at Deep tier (via `gh` dependency) but NOT guaranteed at Forge tier.
2. If `git` is available: perform an ephemeral shallow clone to a system temp path (`{system_temp}/skf-ephemeral-{skill-name}-{timestamp}/`).
3. For create-skill: use `--depth 1 --single-branch --filter=blob:none`; apply sparse-checkout if `include_patterns` are specified.
4. For update-skill: use sparse-checkout scoped to the changed files from the change manifest only. No `--branch` flag — uses the remote default branch (must match the branch used during original create-skill run).
5. If clone succeeds: use the local clone path for AST extraction. All results are T1 with `[AST:...]` citations.
6. Cleanup: delete the temp directory after extraction inventory is built and all data is in context. The clone never persists beyond the extraction step.

**Fallback (clone fails or `git` unavailable):**

- The extraction step MUST warn the user explicitly before degrading
- **create-skill:** Warning must include actionable guidance — clone locally and update `source_repo` in the brief to the local path
- **update-skill:** Warning must include actionable guidance — clone locally, re-run [CS] Create Skill with the local path to regenerate provenance data, then re-run the update
- Extraction proceeds using Quick tier strategy (source reading via gh_bridge)
- All results labeled T1-low with `[SRC:...]` citations
- The degradation reason is recorded in the evidence report

Silent degradation is **forbidden**. The user must always know when AST extraction was skipped and why.

### AST Tool Unavailable at Forge/Deep Tier

When the tier is Forge or Deep but ast-grep is not functional:

- The extraction step MUST warn the user explicitly before degrading
- Warning must include actionable guidance: run [SF] Setup Forge to detect tools
- Extraction proceeds using Quick tier strategy
- All results labeled T1-low
- The degradation reason is recorded in the evidence report

### Per-File AST Failure

When ast-grep fails on an individual file (parse error, unsupported syntax):

- Fall back to source reading for **that file only**
- Other files continue with AST extraction
- The affected file's results are labeled T1-low; unaffected files retain T1
- Log a warning noting which file degraded and why
