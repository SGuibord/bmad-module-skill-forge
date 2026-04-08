# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""SKF Structural Diff — Set operations on export arrays for drift detection.

Compares a baseline provenance map against a current extraction snapshot to
detect added, removed, changed, and moved exports. Used by audit-skill and
update-skill.

CLI: python3 skf-structural-diff.py <baseline-json> <current-json>
     python3 skf-structural-diff.py --baseline '<JSON>' --current '<JSON>'

Input: Two JSON objects with an "exports" array. Each export has:
  - name: string (identifier)
  - file: string (source file path)
  - line: number (line number)
  - signature: string (optional, for change detection)
  - type: string (function/class/type/const/etc.)

Output: JSON with categorized findings (added, removed, changed, moved).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def normalize_exports(exports):
    """Normalize export list into a dict keyed by name."""
    result = {}
    for exp in exports:
        name = exp.get("name", "")
        if name:
            result[name] = exp
    return result


def compute_signature_hash(export_entry):
    """Compute a hash of the export's signature for change detection."""
    sig = export_entry.get("signature", "")
    if not sig:
        # Fall back to type + name
        sig = f"{export_entry.get('type', '')}:{export_entry.get('name', '')}"
    return hashlib.sha256(sig.encode()).hexdigest()[:16]


def diff_exports(baseline_exports, current_exports):
    """Compare two export lists and produce categorized findings."""
    baseline = normalize_exports(baseline_exports)
    current = normalize_exports(current_exports)

    baseline_names = set(baseline.keys())
    current_names = set(current.keys())

    added_names = current_names - baseline_names
    removed_names = baseline_names - current_names
    common_names = baseline_names & current_names

    findings = []

    # Removed exports
    for name in sorted(removed_names):
        exp = baseline[name]
        findings.append({
            "type": "removed",
            "category": "export",
            "name": name,
            "file": exp.get("file", ""),
            "line": exp.get("line", 0),
            "export_type": exp.get("type", ""),
            "detail": f"Export '{name}' ({exp.get('type', 'unknown')}) removed from {exp.get('file', 'unknown')}",
        })

    # Added exports
    for name in sorted(added_names):
        exp = current[name]
        findings.append({
            "type": "added",
            "category": "export",
            "name": name,
            "file": exp.get("file", ""),
            "line": exp.get("line", 0),
            "export_type": exp.get("type", ""),
            "detail": f"New export '{name}' ({exp.get('type', 'unknown')}) in {exp.get('file', 'unknown')}",
        })

    # Changed exports (same name, different signature or location)
    for name in sorted(common_names):
        base_exp = baseline[name]
        curr_exp = current[name]

        changes = []

        # File moved?
        if base_exp.get("file") != curr_exp.get("file"):
            changes.append("file_moved")
            findings.append({
                "type": "moved",
                "category": "export",
                "name": name,
                "file": curr_exp.get("file", ""),
                "line": curr_exp.get("line", 0),
                "previous_file": base_exp.get("file", ""),
                "export_type": curr_exp.get("type", ""),
                "detail": f"Export '{name}' moved from {base_exp.get('file', '')} to {curr_exp.get('file', '')}",
            })

        # Signature changed?
        base_sig = base_exp.get("signature", "")
        curr_sig = curr_exp.get("signature", "")
        if base_sig and curr_sig and base_sig != curr_sig:
            findings.append({
                "type": "changed",
                "category": "signature",
                "name": name,
                "file": curr_exp.get("file", ""),
                "line": curr_exp.get("line", 0),
                "export_type": curr_exp.get("type", ""),
                "previous_signature": base_sig,
                "current_signature": curr_sig,
                "detail": f"Signature changed for '{name}' in {curr_exp.get('file', '')}",
            })

        # Type changed? (e.g., function -> class)
        if base_exp.get("type") and curr_exp.get("type") and base_exp["type"] != curr_exp["type"]:
            findings.append({
                "type": "changed",
                "category": "export",
                "name": name,
                "file": curr_exp.get("file", ""),
                "line": curr_exp.get("line", 0),
                "export_type": curr_exp.get("type", ""),
                "previous_type": base_exp.get("type", ""),
                "detail": f"Export type changed for '{name}': {base_exp['type']} -> {curr_exp['type']}",
            })

    # Summary
    by_type = {"added": 0, "removed": 0, "changed": 0, "moved": 0}
    for f in findings:
        by_type[f["type"]] = by_type.get(f["type"], 0) + 1

    return {
        "status": "ok",
        "total_findings": len(findings),
        "by_type": by_type,
        "baseline_count": len(baseline),
        "current_count": len(current),
        "findings": findings,
    }


def load_exports(source):
    """Load exports from a JSON file or string."""
    try:
        if isinstance(source, str) and source.startswith("{"):
            data = json.loads(source)
        else:
            with open(source) as f:
                data = json.load(f)
        return data.get("exports", data if isinstance(data, list) else []), None
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return None, str(e)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 skf-structural-diff.py <baseline> <current>", file=sys.stderr)
        print("       python3 skf-structural-diff.py --baseline '<JSON>' --current '<JSON>'", file=sys.stderr)
        sys.exit(1)

    if "--baseline" in sys.argv:
        idx = sys.argv.index("--baseline")
        baseline_src = sys.argv[idx + 1]
        idx = sys.argv.index("--current")
        current_src = sys.argv[idx + 1]
    else:
        baseline_src = sys.argv[1]
        current_src = sys.argv[2]

    baseline_exports, err = load_exports(baseline_src)
    if err:
        print(json.dumps({"status": "error", "error": f"Baseline: {err}"}))
        sys.exit(1)

    current_exports, err = load_exports(current_src)
    if err:
        print(json.dumps({"status": "error", "error": f"Current: {err}"}))
        sys.exit(1)

    result = diff_exports(baseline_exports, current_exports)
    print(json.dumps(result, indent=2))
    sys.exit(0)
