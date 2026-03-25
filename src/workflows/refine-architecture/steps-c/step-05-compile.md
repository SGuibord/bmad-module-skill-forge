---
name: 'step-05-compile'
description: 'Produce the refined architecture document by annotating the original with gaps, issues, and improvements'

nextStepFile: './step-06-report.md'
outputFile: '{output_folder}/refined-architecture-{project_name}.md'
---

# Step 5: Compile Refined Architecture

## STEP GOAL:

Produce the refined architecture document by starting with the original as a base, adding gap-fill subsections, issue callout blocks, and improvement suggestions. Append a Refinement Summary. Present for user review before finalizing.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- CRITICAL: Read the complete step file before taking any action
- TOOL/SUBPROCESS FALLBACK: If any instruction references a subprocess, subagent, or tool you do not have access to, you MUST still achieve the outcome in your main context thread
- YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- You are an architecture refinement analyst compiling the final refined document
- Additive, not destructive — preserve every word of the original, only add refinements
- The document must be in `{document_output_language}`

### Step-Specific Rules:

- FORBIDDEN to discover new gaps, issues, or improvements — use only what Steps 02-04 produced
- FORBIDDEN to delete, reword, or rearrange original architecture content
- Present compiled document for user review (Gate checkpoint)

## EXECUTION PROTOCOLS:

- Compile refined architecture from original + findings from Steps 02-04
- Write output to {outputFile}, wait for user approval before proceeding

## CONTEXT BOUNDARIES:

- From Steps 01-04: Architecture document, skill inventory, gap/issue/improvement findings
- This step produces: The refined architecture document at {outputFile}

## MANDATORY SEQUENCE

**CRITICAL:** Follow this sequence exactly. Do not skip, reorder, or improvise.

### 1. Prepare the Original as Base

Load the complete original architecture document.

This is the base. Every line of the original MUST appear in the refined document, unmodified.

### 2. Insert Gap-Fill Subsections

For each gap finding from Step 02:

**Locate the most relevant section** in the original architecture where this integration would logically belong.

**Insert a gap-fill subsection** one heading level deeper than the parent section:

```markdown
#### RA: {Library A} <-> {Library B} Integration Path

> [!NOTE] **Gap Identified by Refine Architecture**
> This integration path was not documented in the original architecture but is supported by skill API evidence.

{Gap description with full evidence citation from Step 02}

**Proposed Integration:**
{Suggested architecture content describing how the libraries connect}
```

If no clear parent section exists, collect orphan gaps into a new section: "## RA: Additional Integration Paths"

### 3. Insert Issue Annotations

For each issue finding from Step 03:

**Locate the section** containing the contradicted claim.

**Insert an issue callout block** immediately after the contradicted text:

```markdown
> [!WARNING] **Issue Detected by Refine Architecture** ({severity})
> Architecture states: "{quoted claim}"
> Skill reality: {contradicting evidence from skill}
> {IF VS report}: VS verdict: {verdict} for {pair}
>
> **Suggested Correction:** {specific correction with API evidence}
```

**Order by severity:** Critical issues first, then Major, then Minor.

### 4. Insert Improvement Suggestions

For each improvement finding from Step 04:

**Locate the section** where the library is discussed.

**Insert an improvement subsection** one heading level deeper:

```markdown
#### RA: Enhancement — {Improvement Title}

> [!TIP] **Improvement Suggested by Refine Architecture** ({value} value)
> {skill_name} provides `{api}` which is not currently leveraged.

{Full improvement description with evidence citation from Step 04}

**How to Incorporate:**
{Specific suggestion for updating the architecture}
```

**Order by value:** High value improvements first, then Medium, then Low.

### 5. Add Refinement Summary Section

Append a `## Refinement Summary` section containing:

- **Header:** "Produced by: Refine Architecture workflow using {skill_count} skills" and date
- **Changes Made table:** Gaps Filled ({gap_count}), Issues Flagged ({issue_count} with severity breakdown), Improvements Suggested ({improvement_count} with value breakdown)
- **Evidence Sources table:** Each skill name and how many refinements cite it
- **Next Steps:** Review `[!WARNING]` issues, `[!NOTE]` gaps, `[!TIP]` improvements; then run **[SS] compose-mode**

### 6. Write the Refined Document

Write the complete refined architecture to `{outputFile}`.

### 7. Present Compiled Document for Review

"**Refined architecture compiled. Please review:**

---

{Display the Refinement Summary section only — not the full document}

---

**The full refined document has been written to:** `{outputFile}`

Please review the refinements:
- {gap_count} gap-fill subsections added
- {issue_count} issue annotations inserted
- {improvement_count} improvement suggestions included
- Original architecture content preserved in full

**Does the refinement look correct?**"

### 8. Present MENU OPTIONS

Display: **Select:** [C] Continue to Final Report

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting compilation
- ONLY proceed to next step when user approves and selects 'C'

#### Menu Handling Logic:

- IF C: Load, read entire file, then execute {nextStepFile}
- IF Any other: Process as feedback, adjust specific refinements in the document, rewrite {outputFile}, redisplay preview, then [Redisplay Menu Options](#8-present-menu-options)

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

- Original architecture document preserved in full without modifications
- Gap-fill subsections inserted at logical locations with evidence citations
- Issue callout blocks inserted adjacent to contradicted claims with severity
- Improvement suggestions inserted with value ratings and evidence
- Refinement Summary section appended with accurate counts
- Refined document written to {outputFile}
- User reviewed and approved compilation
- Proceeded to step 06 only after user selected C

### SYSTEM FAILURE:

- Deleting, rewording, or rearranging original architecture content
- Discovering new findings not from Steps 02-04
- Inserting refinements without evidence citations
- Proceeding without user review (Gate checkpoint)
- Not writing the document to {outputFile} before presenting for review
- Hardcoded paths instead of frontmatter variables

**Master Rule:** Additive only. Preserve the original. Get user approval before proceeding.
