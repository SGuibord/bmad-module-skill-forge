---
name: 'step-01-select'
description: 'Select skill, version(s), and drop mode (deprecate/purge)'
nextStepFile: './step-02-execute.md'
versionPathsKnowledge: '../../../knowledge/version-paths.md'
---

# Step 1: Select Drop Target

## STEP GOAL:

Identify exactly what the user wants to drop — which skill, which version(s), and whether the drop is a soft deprecation (manifest-only) or a hard purge (files deleted). Enforce the active version guard, gather the list of affected directories, and obtain explicit user confirmation before any write or delete operation is scheduled.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER schedule a destructive operation without explicit user confirmation
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ⚙️ TOOL/SUBPROCESS FALLBACK: If any instruction references a subprocess, subagent, or tool you do not have access to, you MUST still achieve the outcome in your main context thread
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are Ferris in Management mode — a destructive operation specialist
- ✅ Safety first, confirmation required
- ✅ You protect the active version and enforce the active version guard
- ✅ You treat every drop as potentially irreversible — soft drops are recoverable, hard drops are not

### Step-Specific Rules:

- 🎯 Focus only on selection, validation, and confirmation
- 🚫 FORBIDDEN to proceed without explicit user confirmation at the final gate
- 🚫 FORBIDDEN to modify the manifest or delete any files in this step — execution happens in step-02
- 🚫 FORBIDDEN to drop an active version when other non-deprecated versions exist
- 💬 Present selections clearly so the user can verify scope, mode, and blast radius before committing

## EXECUTION PROTOCOLS:

- 🎯 Load version-paths knowledge and the export manifest as the sole source of truth
- 💾 Gather all selection decisions into context for step-02
- 📖 Show version lists, statuses, and directory paths clearly so the user understands what will be affected
- 🚫 Do not proceed if the manifest is empty or missing — halt gracefully

## CONTEXT BOUNDARIES:

- Available: Export manifest v2, SKF module config variables, on-disk skill directory listing
- Focus: Selection, validation, and user confirmation
- Limits: Do not write to the manifest, do not delete any files — execution is deferred to step-02
- Dependencies: At least one skill must exist in the export manifest; otherwise the workflow halts

## MANDATORY SEQUENCE

**CRITICAL:** Follow this sequence exactly. Do not skip, reorder, or improvise unless user explicitly requests a change.

### 1. Load Knowledge

Read `{versionPathsKnowledge}` completely and extract:

- Path templates: `{skill_package}`, `{skill_group}`, `{forge_version}`, `{forge_group}`
- Export manifest v2 schema (`schema_version`, `exports`, `active_version`, `versions` map, `status` field values)
- Skill management operations (Drop section — soft vs hard, active version guard, skill-level drop)

You will use these templates and rules to build directory paths and enforce safety guards in the following sections.

### 2. Read Export Manifest

Load `{skills_output_folder}/.export-manifest.json`.

**If the file is missing, empty, or contains no `exports` entries:**

"**Drop Skill — nothing to drop.** The export manifest at `{skills_output_folder}/.export-manifest.json` is empty or missing. There are no exported skills on record. Run `[EX] Export Skill` first, then return here when you need to drop a version."

HALT the workflow. Do not proceed to section 3.

**If the file exists:** Parse JSON and verify `schema_version` is `"2"`. If the manifest is v1 (no `schema_version` field), note this but continue — treat every entry as having a single active version derived from its current state.

### 3. List Available Skills

Build and display a summary of every skill in the manifest. For each skill:

1. Read `active_version` from the manifest entry
2. List every entry in the skill's `versions` map with its `status` field
3. Mark the active version with a trailing `*`
4. Sort versions in descending order (newest first) where possible

Also scan `{skills_output_folder}/` for any top-level directories that are NOT present in the manifest's `exports` object. Record these as "(not in manifest)" — they represent draft or orphaned skills that the drop workflow can still purge from disk.

Display the combined list:

```
**Drop Skill — select target**

Available skills:
1. cognee
   - 0.1.0 (deprecated)
   - 0.5.0 (archived)
   - 0.6.0 (active) *
2. express
   - 4.18.0 (active) *
3. legacy-helper (not in manifest)
```

### 4. Ask Which Skill

"**Which skill would you like to drop?**
Enter the skill name or its number from the list above."

Wait for user input. Accept either the numeric index or the skill name (exact match).

**If the user's input does not match any listed skill:** Re-display the list and ask again.

Store the selection as `target_skill`.

### 5. Display Version Details

For the selected skill, display every version with its full metadata from the manifest:

```
**{target_skill} — versions:**

| Version | Status     | Last Exported | Platforms              |
|---------|------------|---------------|------------------------|
| 0.1.0   | deprecated | 2026-01-15    | claude                 |
| 0.5.0   | archived   | 2026-03-15    | claude                 |
| 0.6.0   | active *   | 2026-04-04    | claude, copilot        |
```

If the selected skill was flagged "(not in manifest)", note that no versions are tracked and only a skill-level purge is meaningful.

### 6. Ask Scope

"**Drop which version(s)?**

- **[N]** Specific version — soft deprecate or hard purge a single version
- **[A]** All versions — drops the entire skill (skill-level operation)"

Wait for user selection.

**If [N] Specific version:**

"**Which version?** Enter the version string (e.g. `0.5.0`)."

Wait for user input. Validate that the version exists in the manifest's `versions` map for `target_skill`. If not, repeat the prompt.

Set `target_versions = [<selected version>]` and `is_skill_level = false`.

**If [A] All versions:**

Set `target_versions = "all"` and `is_skill_level = true`.

### 7. Active Version Guard

**Applies only when `is_skill_level = false` (specific version selected):**

1. Read the selected version's `status` field from the manifest
2. If `status != "active"` → skip this guard, the version is safe to drop
3. If `status == "active"`:
   a. Count the number of OTHER versions in the `versions` map with `status != "deprecated"` (i.e., `active`, `archived`, or `draft`)
   b. If that count is `> 0` → REFUSE the drop:

      "**Cannot drop the active version `{version}`.**
      Other non-deprecated versions of `{target_skill}` still exist. To proceed, either:

      **(a)** Switch the active version to another version first by re-running `[EX] Export Skill` with a different version selected, then return here to drop `{version}`, OR

      **(b)** Use the `[A] All versions` option to drop every version of `{target_skill}` at once."

      HALT the workflow. Do not proceed.

   c. If the count is `0` → the active version is the ONLY version; allow the drop to continue (it is functionally equivalent to a skill-level drop on a single-version skill)

### 8. Ask Mode

"**How should this be dropped?**

- **[D]** Deprecate (soft) — Mark the version as `deprecated` in the manifest. Files remain on disk. Export-skill will exclude it from all platform context files. Reversible by editing the manifest.
- **[P]** Purge (hard) — Deprecate AND delete files from disk (`{skill_package}` and `{forge_version}`, or full `{skill_group}` and `{forge_group}` for a skill-level drop). **Irreversible.**"

Wait for user selection.

Set `drop_mode` to `"deprecate"` (on D) or `"purge"` (on P).

### 9. Compute Affected Directories

Using the templates from `{versionPathsKnowledge}`, resolve the list of directories that would be affected:

**If `is_skill_level = false` (version-level drop):**

- `{skill_package}` = `{skills_output_folder}/{target_skill}/{version}/{target_skill}/`
- The enclosing version directory = `{skills_output_folder}/{target_skill}/{version}/`
- `{forge_version}` = `{forge_data_folder}/{target_skill}/{version}/`

**If `is_skill_level = true` (skill-level drop):**

- `{skill_group}` = `{skills_output_folder}/{target_skill}/`
- `{forge_group}` = `{forge_data_folder}/{target_skill}/`

Store the list as `affected_directories`.

If `drop_mode == "deprecate"`, record the list but present it as "retained" in the confirmation output — no deletion will occur.

### 10. Confirmation Gate

Display the full operation summary:

```
**About to drop:**

  Skill:   {target_skill}
  Version: {version or "ALL versions"}
  Mode:    {Deprecate (soft) | Purge (hard)}
  Files:
    {for each path in affected_directories, list one per line}
    {or "(retained on disk — soft drop)" if drop_mode == "deprecate"}

{if drop_mode == "purge":}
  ⚠️  This operation cannot be undone. Files will be permanently deleted.
{else:}
  Files remain on disk. Reversible by manually editing the manifest.

Proceed? [Y/N]
```

Wait for explicit user response.

- **If `Y`** → proceed to section 11
- **If `N`** → "**Cancelled.** No changes were made." HALT the workflow
- **Any other input** → re-display the confirmation and ask again

### 11. Store Decisions in Context

Store the following decisions in workflow context for step-02:

- `target_skill` — the skill name
- `target_versions` — list of version strings (`[<version>]`) or the literal string `"all"`
- `drop_mode` — `"deprecate"` or `"purge"`
- `is_skill_level` — boolean (true if all versions)
- `affected_directories` — list of absolute directory paths that step-02 will delete in purge mode (or retain in deprecate mode)

### 12. Load Next Step

Load, read the full file, and then execute `{nextStepFile}`.

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN the user has confirmed with `Y` at the confirmation gate AND all selection decisions have been stored in context, will you then load and read fully `{nextStepFile}` to execute the drop.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Version-paths knowledge loaded and applied via templates (no hardcoded paths)
- Export manifest read and validated (halt if empty/missing)
- Complete skill and version list displayed with statuses and active marker
- Skill, version(s), and mode selected by explicit user input
- Active version guard enforced — refused to drop an active version with surviving non-deprecated peers
- Affected directories computed from templates
- Explicit user confirmation (`Y`) received at the confirmation gate
- All selection decisions stored in context for step-02

### ❌ SYSTEM FAILURE:

- Proceeding without reading version-paths knowledge
- Proceeding when the manifest is empty or missing
- Hardcoding directory paths instead of using `{skill_package}`, `{skill_group}`, `{forge_version}`, `{forge_group}` templates
- Allowing a drop of the active version when other non-deprecated versions exist
- Modifying the manifest or deleting files in this step (execution belongs to step-02)
- Skipping the confirmation gate or proceeding on any response other than `Y`
- Not storing decisions in context for step-02

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE. No destructive action proceeds without explicit user confirmation.
