---
name: 'step-06-validate'
description: 'Validate compiled skill content against agentskills.io spec via skill-check'
nextStepFile: './step-07-generate-artifacts.md'
---

# Step 6: Validate

## STEP GOAL:

To validate the compiled SKILL.md content against the agentskills.io specification using skill-check, auto-fix any validation failures, and confirm spec compliance before artifact generation.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 📖 CRITICAL: Read the complete step file before taking any action
- 🎯 ALWAYS follow the exact instructions in the step file
- ⚙️ TOOL/SUBPROCESS FALLBACK: If any instruction references a tool you do not have access to, you MUST still achieve the outcome in your main context thread
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a skill compilation engine performing quality assurance
- ✅ Validation ensures spec compliance — it does not modify content semantics
- ✅ Tool unavailability means skip validation, not halt workflow

### Step-Specific Rules:

- 🎯 Focus ONLY on validating compiled content against spec
- 🚫 FORBIDDEN to add new content — only fix spec compliance issues
- 💾 Validation and auto-fix modify files in the staging directory (`_bmad-output/{name}/`)
- 💬 If auto-fix fails, report issues clearly but proceed (warn, don't halt)
- ⚙️ If skill-check unavailable: skip validation, add warning to evidence report
- ⚠️ Ignore non-zero exit codes from `skill-check` if the JSON output shows 0 errors — parse JSON output, not exit codes

## EXECUTION PROTOCOLS:

- 🎯 Follow MANDATORY SEQUENCE exactly
- 💾 Validation results are added to evidence-report content in context
- 📖 Auto-fix pattern: validate → fix → re-validate (once)
- 🚫 Maximum one auto-fix attempt per validation failure

## CONTEXT BOUNDARIES:

- Available: All compiled content from step-05 (SKILL.md, metadata.json, etc.)
- Focus: Spec compliance validation and auto-fix
- Limits: Do NOT add new content or modify extraction data
- Dependencies: Compiled content must exist from step-05

## MANDATORY SEQUENCE

**CRITICAL:** Follow this sequence exactly. Do not skip, reorder, or improvise.

### 1. Check Tool Availability

Run: `npx skill-check -h`

- If succeeds (returns usage information): Continue to automated validation (section 2)
- If fails (command not found or error): Perform manual fallback (section 3)
  - Add note to evidence-report content: "Spec validation performed manually — skill-check tool unavailable"

**Important:** Use the verification command. Do not assume availability — empirical check required.

### 2. Validate & Auto-Fix (skill-check check --fix)

Run the external skill-check tool against the compiled skill staging directory:

```bash
npx skill-check check <staging-skill-dir> --fix --format json --no-security-scan
```

This single command performs:
- Frontmatter validation (required fields, naming, ordering, unknown fields)
- Description quality checks (length, "Use when" phrasing)
- Body limit enforcement (line count, token count)
- Local link resolution
- File formatting (trailing newlines)
- **Auto-fix** of all deterministic issues (frontmatter ordering, slug format, required fields, description phrasing, trailing newlines)
- **Quality score** (0-100) across five weighted categories

**Parse the JSON output** to extract:
- `qualityScore` — overall score (0-100)
- `diagnostics[]` — remaining issues after auto-fix
- `fixed[]` — issues that were automatically corrected

**Note:** `skill-check` may return a non-zero exit code even when `errorCount` is 0 (e.g., security advisories or package warnings). Always rely on the parsed JSON `errorCount` and `warningCount`, not the shell exit code.

**If quality score ≥ 70:** Record "Schema: PASS (score: {score}/100)" in evidence-report content.

**If quality score < 70:**
1. Log remaining diagnostics as warnings
2. Record "Schema: WARN — score {score}/100, {count} remaining issues" in evidence-report
3. Proceed (do not halt)

**If skill-check returns errors that --fix could not resolve:**
- Record specific rule IDs and suggestions in evidence-report
- Proceed with warnings

### 3. Validate Frontmatter (Fallback)

**If skill-check was available:** Skip — already validated in step 2.

**If skill-check NOT available (fallback):** Perform manual frontmatter compliance check.

**Check (agentskills.io specification):**

- [ ] Frontmatter present — file starts with `---` and has closing `---`
- [ ] `name` field — present, non-empty, lowercase alphanumeric + hyphens only, 1-64 chars
- [ ] `name` matches skill output directory name
- [ ] `description` field — present, non-empty, 1-1024 characters
- [ ] No unknown fields — only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` are permitted
- [ ] `version` and `author` are NOT in frontmatter (they belong in metadata.json)

**If validation passes:** Record "Frontmatter: PASS" in evidence-report content.

**If validation fails:**
1. Auto-fix frontmatter (these are deterministic fixes — remove disallowed fields, add missing required fields)
2. Re-validate once
3. Record result in evidence-report

### 4. Split Oversized Body (if needed)

**If step 2 reported `body.max_lines` failure:**

Run split-body to extract oversized sections into reference files:

```bash
npx skill-check split-body <staging-skill-dir> --write
```

Then re-validate to confirm the fix:

```bash
npx skill-check check <staging-skill-dir> --format json --no-security-scan
```

**If skill-check unavailable or no body size issue:** Skip this step.

### 5. Security Scan

**If skill-check is available**, run security scan on the compiled skill:

```bash
npx skill-check check <staging-skill-dir> --format json
```

(Security scan is enabled by default when `--no-security-scan` is omitted.)

**Parse security findings** from the JSON output:
- Record any security warnings (prompt injection risks, unsafe patterns) in evidence-report
- Security findings are advisory — they do not block artifact generation

**If skill-check unavailable:** Skip with note: "Security scan skipped — skill-check tool unavailable"

### 6. Content Quality Review (tessl)

**If tessl is available**, run a content quality review on the compiled skill:

```bash
npx -y tessl skill review <staging-skill-dir>
```

**Parse the output** to extract:
- `description_score` — percentage
- `content_score` — percentage
- `average_score` — percentage
- `validation_result` — PASSED/FAILED
- `judge_suggestions[]` — list of improvement suggestions

**If tessl content score < 70%:** Record a warning in the evidence report:

"Content quality warning: tessl scored content at {score}%. This often indicates SKILL.md lacks inline actionable content after split-body. Consider inlining Quick Start and common workflows directly in SKILL.md."

**If tessl unavailable:** Skip with note: "Content quality review skipped — tessl tool unavailable"

**Note:** tessl installs automatically via `npx`. A missing tool is not an error — graceful skip.

### 7. Validate metadata.json

Cross-check metadata.json content against extraction inventory:
- `stats.exports_documented` matches actual documented exports
- `stats.exports_total` matches total extracted exports
- `stats.coverage` is accurate (documented / total)
- `confidence_t1`, `confidence_t2`, `confidence_t3` match actual counts
- `spec_version` is "1.3"

Auto-fix any discrepancies (these are computed values).

### 8. Update Evidence Report

Add validation results to the evidence-report content in context:

```markdown
## Validation Results
- Schema: {pass/fail} (quality score: {score}/100)
- Frontmatter: {pass/fail}
- Body: {pass/fail} {split-body applied if applicable}
- Security: {pass/warn/skipped}
- Content Quality (tessl): {pass/warn/skipped} (score: {score}%)
- Metadata: {pass/fail}

## Quality Score Breakdown
- Frontmatter (30%): {score}
- Description (30%): {score}
- Body (20%): {score}
- Links (10%): {score}
- File (10%): {score}

## Auto-Fixed Issues
- {list of issues automatically corrected by --fix}

## Remaining Warnings
- {any warnings from validation}

## Security Findings
- {any security scan results}

## Content Quality (tessl)
- {tessl average score, description score, content score, or "skipped"}
- {judge suggestions if available}
```

### 9. Menu Handling Logic

**Auto-proceed step — no user interaction.**

After validation is complete (or skipped if tools unavailable), immediately load, read entire file, then execute `{nextStepFile}`.

#### EXECUTION RULES:

- This is an auto-proceed validation step with no user choices
- Tool unavailability is a skip, not a halt
- Validation failures are warnings — proceed to artifact generation
- Proceed directly to next step after validation completes

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN validation is complete (or skipped) and evidence-report content is updated will you proceed to load `{nextStepFile}` for artifact generation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- `npx skill-check check --fix --format json` executed (or skipped with warning if unavailable)
- Quality score (0-100) captured and recorded in evidence report
- Auto-fix applied via `--fix` for deterministic issues
- Security scan executed as separate pass (or skipped with warning)
- Split-body applied if `body.max_lines` failed
- `npx -y tessl skill review` executed (or skipped with warning if unavailable)
- Content quality warning raised if tessl content score < 70%
- Metadata cross-check performed
- Evidence report updated with structured validation results (including tessl scores)
- Auto-proceeded to step-07

### ❌ SYSTEM FAILURE:

- Halting the workflow on validation failure (should warn and proceed)
- Halting on skill-check unavailability (should skip with warning)
- Adding new content during validation (only structural fixes allowed)
- Not recording quality score in evidence report
- Skipping security scan without recording the skip
- Attempting more than one auto-fix cycle per failure

**Master Rule:** Validation informs, it does not block. Record results, fix what's deterministic, scan for security issues, warn about the rest, and proceed.
