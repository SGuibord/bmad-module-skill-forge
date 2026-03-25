# Coverage Patterns

## Purpose

Rules for detecting technology/library references in architecture and PRD documents, and matching them against generated skills.

---

## Technology Detection in Documents

### Direct Name Matching

Search the architecture document for exact mentions of:
1. Library names from generated skills (case-insensitive)
2. Common aliases (e.g., "React" also matches "ReactJS", "react.js")
3. Framework names that encompass libraries (e.g., "Tauri" encompasses the Tauri ecosystem)

### Section-Based Detection

Parse document section headers for technology groupings:
- `## Desktop App` → technologies listed under this section
- `## Backend Core` → technologies in backend layer
- `## AI Layer` → AI-related technologies

### Integration Claim Detection

An "integration claim" is a statement in the architecture doc that describes two or more technologies working together. Detection patterns:

1. **Explicit connection statements**: "X connects to Y", "X feeds into Y", "X communicates with Y"
2. **Data flow descriptions**: "Data flows from X through Y to Z"
3. **Architectural layer crossing**: "The UI layer (React) communicates with the backend (Rig) via..."
4. **Dependency statements**: "X depends on Y for...", "X uses Y to..."
5. **Co-occurrence in the same paragraph**: Two or more technology names appearing in the same paragraph suggests an integration relationship

### Coverage Verdict

| Verdict | Meaning |
|---------|---------|
| **Covered** | A generated skill exists in `skills/` for this technology |
| **Missing** | Technology is referenced in architecture doc but no skill exists |
| **Extra** | A skill exists but the technology is not referenced in the architecture doc (informational, not an error) |
