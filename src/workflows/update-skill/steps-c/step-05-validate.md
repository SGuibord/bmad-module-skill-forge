---
name: 'step-05-validate'
description: 'Validate updated skill against spec, verify MANUAL integrity, and check confidence tier consistency'

nextStepFile: './step-06-write.md'
---

# Step 5: Validate

## STEP GOAL:

Validate the merged skill content against the agentskills.io specification, verify all [MANUAL] sections survived the merge intact, and check confidence tier consistency across all re-extracted content. This is an advisory validation — findings are warnings, not blockers.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ⚙️ TOOL/SUBPROCESS FALLBACK: If any instruction references a subprocess, subagent, or tool you do not have access to, you MUST still achieve the outcome in your main context thread
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a precision code analyst operating in Surgeon mode
- ✅ Validation is advisory — flag issues but do not block the workflow
- ✅ Every finding must include specific file:line reference
- ✅ Zero-hallucination principle applies to validation findings too

### Step-Specific Rules:

- 🎯 Focus ONLY on validation — do not fix issues (that's the user's choice)
- 🚫 FORBIDDEN to modify merged content — validation is read-only
- 💬 Launch parallel validation checks when subprocess available (Pattern 4)
- ⚙️ If subprocess unavailable, perform checks sequentially in main thread

## EXECUTION PROTOCOLS:

- 🎯 Follow MANDATORY SEQUENCE exactly
- 💾 Compile validation findings with severity levels
- 📖 Track pass/fail for each validation category
- 🚫 Validation is ADVISORY — do not block on warnings

## CONTEXT BOUNDARIES:

- Available: merged skill content from step 04, extraction results from step 03, [MANUAL] inventory from step 01
- Focus: quality assurance — spec compliance, [MANUAL] integrity, confidence consistency
- Limits: read-only — do not modify merged content
- Dependencies: step 04 must have completed merge (with or without conflict resolution)

## MANDATORY SEQUENCE

**CRITICAL:** Follow this sequence exactly. Do not skip, reorder, or improvise unless user explicitly requests a change.

### 1. Launch Parallel Validation Checks

Launch subprocesses in parallel for each validation category, aggregating results when complete:

**Check A — Spec Compliance:**
- Validate merged SKILL.md structure against agentskills.io specification (via skills_ref if available)
- Verify required sections present: exports, usage patterns, conventions
- Verify export entries have: name, type, signature, file:line reference
- Flag missing or incomplete sections

**Check B — [MANUAL] Section Integrity:**
- Compare [MANUAL] inventory from step 01 against merged content
- Verify every [MANUAL] block from inventory exists in merged result
- Verify [MANUAL] content is byte-identical (zero modification)
- Flag any [MANUAL] blocks that were moved, truncated, or missing

**Check C — Confidence Tier Consistency:**
- Verify all re-extracted exports have confidence labels (T1/T1-low/T2)
- Verify tier labels match forge tier capabilities:
  - Quick tier: only T1-low allowed
  - Forge tier: T1 expected (T1-low for degraded operations)
  - Deep tier: T1 + T2 expected
- Flag mismatched or missing tier labels

**Check D — Provenance Completeness:**
- Verify every export in merged SKILL.md has a provenance map entry
- Verify file:line references point to actual source locations
- Verify no stale references to old file paths or line numbers
- Flag orphaned provenance entries (export removed but provenance remains)

### 2. Aggregate Validation Results

Compile results from all checks:

```
Validation Results:
  spec_compliance:
    status: PASS|WARN|FAIL
    findings: [{severity, description, location}]

  manual_integrity:
    status: PASS|WARN|FAIL
    sections_verified: [count]
    sections_intact: [count]
    findings: [{severity, description, section_name}]

  confidence_consistency:
    status: PASS|WARN|FAIL
    exports_checked: [count]
    findings: [{severity, description, export_name, expected_tier, actual_tier}]

  provenance_completeness:
    status: PASS|WARN|FAIL
    entries_checked: [count]
    findings: [{severity, description, export_name}]
```

### 3. For Stack Skills — Validate Reference Files

**ONLY if skill_type == "stack":**

Repeat checks A-D for each reference file:
- `references/{library}.md` — spec compliance and [MANUAL] integrity
- `references/integrations/{pair}.md` — spec compliance and [MANUAL] integrity

**If skill_type != "stack":** Skip with notice.

### 4. Display Validation Summary

"**Validation Results:**

| Check | Status | Findings |
|-------|--------|----------|
| Spec Compliance | {PASS/WARN/FAIL} | {count} findings |
| [MANUAL] Integrity | {PASS/WARN/FAIL} | {count} findings |
| Confidence Tiers | {PASS/WARN/FAIL} | {count} findings |
| Provenance | {PASS/WARN/FAIL} | {count} findings |

**Overall: {ALL_PASS / WARNINGS_FOUND / FAILURES_FOUND}**"

**If WARNINGS or FAILURES found:**

List each finding with severity and description:

"**Findings:**
1. [{severity}] {description} — {location}
2. [{severity}] {description} — {location}
..."

"**Note:** Validation is advisory. These findings are reported for your awareness but do not block the update. You may choose to address them after the update completes."

### 5. Present MENU OPTIONS

Display: "**Proceeding to write updated files...**"

#### Menu Handling Logic:

- After validation summary is displayed, immediately load, read entire file, then execute {nextStepFile}

#### EXECUTION RULES:

- This is an auto-proceed validation step with no user choices
- Validation is advisory — findings are informational, not blocking
- Proceed directly to next step after summary display

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN all validation checks have completed and findings are displayed will you load {nextStepFile} to write the updated files. Validation does NOT block — it informs.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All four validation checks executed (spec, [MANUAL], confidence, provenance)
- Stack skill reference files validated if applicable
- Findings reported with severity and specific locations
- [MANUAL] integrity verified with byte-level comparison
- Validation results displayed clearly
- Auto-proceeds regardless of findings (advisory mode)

### ❌ SYSTEM FAILURE:

- Skipping any of the four validation checks
- Blocking the workflow on validation warnings
- Not verifying [MANUAL] section integrity
- Hallucinating validation findings not backed by actual comparison
- Modifying merged content during validation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
