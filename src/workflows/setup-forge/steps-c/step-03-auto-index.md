---
name: 'step-03-auto-index'
description: 'Index current project as QMD collection (Deep tier only)'

nextStepFile: './step-04-report.md'
---

# Step 3: Auto-Index Project

## STEP GOAL:

If the detected tier is Deep, index the current project as a QMD collection for knowledge search. For Quick and Forge tiers, skip silently and proceed.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step, ensure entire file is read
- 🎯 Execute all operations autonomously — no user interaction

### Role Reinforcement:

- ✅ You are a system executor performing conditional indexing
- ✅ Graceful degradation is paramount — never fail the workflow over indexing
- ✅ No negative messaging — do not mention what non-Deep tiers are missing

### Step-Specific Rules:

- 🎯 Focus only on QMD indexing (Deep tier) or graceful skip (other tiers)
- 🚫 FORBIDDEN to display "missing" or "skipped" messages for non-Deep tiers
- 🚫 FORBIDDEN to fail the workflow if QMD indexing encounters errors
- 💬 If indexing fails: log the issue, note that index can be retried, continue

## EXECUTION PROTOCOLS:

- 🎯 Follow the MANDATORY SEQUENCE exactly
- 💾 QMD indexing operates on the project root directory
- 📖 Use {calculated_tier} from step-01 context
- 🚫 FORBIDDEN to attempt indexing for Quick or Forge tiers

## CONTEXT BOUNDARIES:

- Available: {calculated_tier} from step-01, forge-tier.yaml written in step-02
- Focus: conditional QMD indexing only
- Limits: only index if Deep tier
- Dependencies: step-02 must have completed (forge-tier.yaml exists)

## MANDATORY SEQUENCE

**CRITICAL:** Follow this sequence exactly. Do not skip, reorder, or improvise.

### 1. Check Tier

Read `{calculated_tier}` from context.

**If tier is NOT Deep:** Proceed directly to step 4 — auto-proceed with no output, no messaging.

**If tier IS Deep:** Continue to section 2.

### 2. Index Project with QMD (Deep Tier Only)

Index the current project directory as a QMD collection for knowledge search.

Use the QMD MCP server to create or update a collection for the current project:
- Collection name: derive from project directory name
- Source: project root directory
- Scope: markdown files, source code, documentation

**Timeout handling:** If indexing takes excessively long on a large project:
- Log that indexing is in progress but may need more time
- Note in context that index may be incomplete
- Do NOT halt or fail the workflow

**Error handling:** If QMD indexing fails:
- Log the specific error
- Note that indexing can be retried by re-running setup-forge
- The forge-tier.yaml already records `qmd: true` — the tool is available even if indexing failed
- Continue to step 4

### 3. Auto-Proceed

"**Proceeding to forge status report...**"

#### Menu Handling Logic:

- After indexing completes (or is skipped for non-Deep tiers), immediately load, read entire file, then execute {nextStepFile}

#### EXECUTION RULES:

- This is an auto-proceed step with no user choices
- Proceed directly to next step after indexing or skip

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN the tier check has been performed (and indexing completed or skipped accordingly) will you load and read fully `{nextStepFile}` to execute the report step.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Deep tier: QMD indexing attempted, succeeded or degraded gracefully
- Quick/Forge tier: skipped silently with no negative messaging
- Workflow continues regardless of indexing outcome
- Auto-proceeded to step-04

### ❌ SYSTEM FAILURE:

- Attempting QMD indexing for Quick or Forge tiers
- Displaying "skipped" or "missing" messages for non-Deep tiers
- Halting the workflow due to QMD indexing failure
- Not proceeding to step-04 after this step

**Master Rule:** This step must NEVER fail the workflow. Deep tier indexing is best-effort. Non-Deep tiers skip silently.
