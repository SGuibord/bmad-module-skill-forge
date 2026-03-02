---
name: 'step-07-generate-artifacts'
description: 'Write all output files — 4 deliverables to skills/ and 3 workspace artifacts to forge-data/'
nextStepFile: './step-08-report.md'
---

# Step 7: Generate Artifacts

## STEP GOAL:

To write all compiled content to disk — 4 deliverable files to `skills/{name}/` and 3 workspace artifacts to `forge-data/{name}/`, creating directories as needed.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 📖 CRITICAL: Read the complete step file before taking any action
- 🎯 ALWAYS follow the exact instructions in the step file
- ⚙️ TOOL/SUBPROCESS FALLBACK: If any instruction references a tool you do not have access to, you MUST still achieve the outcome in your main context thread
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a skill compilation engine performing artifact generation
- ✅ All content was assembled in step-05 and validated in step-06
- ✅ This step ONLY writes — it does not modify, compile, or validate content

### Step-Specific Rules:

- 🎯 Focus ONLY on writing files from the compiled content in context
- 🚫 FORBIDDEN to modify content during writing — write exactly what was compiled
- 🚫 FORBIDDEN to skip any artifact — all 7 files must be written
- 💬 Report each file written with its path
- 📁 Create directories before writing files

## EXECUTION PROTOCOLS:

- 🎯 Follow MANDATORY SEQUENCE exactly
- 💾 Write files using the compiled content from context
- 📖 Create directory structure first, then write files
- 🚫 Halt with error if a file write fails — do not continue with partial output

## CONTEXT BOUNDARIES:

- Available: All compiled content from step-05, validation results from step-06
- Focus: File system operations — create directories, write files
- Limits: Do NOT modify content during writing
- Dependencies: All content must be compiled and validated in context

## MANDATORY SEQUENCE

**CRITICAL:** Follow this sequence exactly. Do not skip, reorder, or improvise.

### 1. Create Directory Structure

Create the following directories at `{project-root}/`:

```
skills/{name}/
skills/{name}/references/
forge-data/{name}/
```

Where `{name}` is the skill name from the brief (kebab-case).

If directories already exist, do not error — proceed with file writing (overwrites existing files).

### 2. Write Deliverables to skills/{name}/

Write these 4 files from the compiled content:

**File 1:** `skills/{name}/SKILL.md`
- The complete compiled skill document
- agentskills.io-compliant format with all sections
- [MANUAL] markers seeded

**File 2:** `skills/{name}/context-snippet.md`
- Compressed 2-line format for CLAUDE.md integration

**File 3:** `skills/{name}/metadata.json`
- Machine-readable birth certificate with stats and provenance

**File 4:** `skills/{name}/references/*.md`
- One file per function group or type
- Progressive disclosure detail files

### 3. Write Workspace Artifacts to forge-data/{name}/

Write these 3 files from the compiled content:

**File 5:** `forge-data/{name}/provenance-map.json`
- Per-claim source map with AST bindings and confidence tiers

**File 6:** `forge-data/{name}/evidence-report.md`
- Build artifact with extraction summary, validation results, warnings

**File 7:** `forge-data/{name}/extraction-rules.yaml`
- Language and ast-grep schema used for this extraction (for reproducibility)

### 4. Verify Write Completion

After all files are written, verify:
- All 7 files exist at their expected paths
- List each file with its path and size

**If any write failed:**
Halt with: "Artifact generation failed: could not write `{file_path}`. Check permissions and disk space."

**If all writes succeeded:**
Display brief confirmation:

"**Artifacts generated.**

**Deliverables (skills/{name}/):**
- SKILL.md
- context-snippet.md
- metadata.json
- references/ ({reference_count} files)

**Workspace (forge-data/{name}/):**
- provenance-map.json
- evidence-report.md
- extraction-rules.yaml

Proceeding to compilation report..."

### 5. Menu Handling Logic

**Auto-proceed step — no user interaction.**

After all artifacts are written and verified, immediately load, read entire file, then execute `{nextStepFile}`.

#### EXECUTION RULES:

- This is an auto-proceed file writing step with no user choices
- All 7 files must be written before proceeding
- File write failures are real errors — halt, do not proceed with partial output
- Proceed directly to next step after successful generation

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN all 7 artifact files are written and verified will you proceed to load `{nextStepFile}` for the compilation report.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Directory structure created (skills/{name}/, forge-data/{name}/)
- All 4 deliverable files written to skills/{name}/
- All 3 workspace artifact files written to forge-data/{name}/
- Write completion verified — all 7 files exist
- Brief confirmation displayed with file list
- Auto-proceeded to step-08

### ❌ SYSTEM FAILURE:

- Modifying content during the write step
- Skipping any of the 7 required files
- Proceeding with partial output if a write fails
- Not creating directories before writing
- Not verifying all files were written

**Master Rule:** This step ONLY writes. All content was compiled and validated in previous steps. Write faithfully, verify completely.
