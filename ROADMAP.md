# Roadmap

Future work planned for Skill Forge. Items here are directional, not scheduled. Layered items ship when their trigger conditions are met, not on a timeline.

**North-star principle for workspace/infrastructure work:** *The workspace is an optimization, never a gate.* Every failure path degrades gracefully to the existing ephemeral behavior.

---

## Persistent Workspace (`~/.skf/workspace/`)

A shared, system-level cache of git clones and their tool indexes, replacing per-forge ephemeral cloning. Designed as four layers that ship independently when real usage proves the need.

### Layer 0 — Core Workspace *(current)*

Persistent clones + CCC indexes preserved across forges, projects, and sessions. Zero new dependencies. Lazy creation on first remote forge. Always falls back to ephemeral on any failure.

### Layer 1 — Registry Intelligence *(triggered)*

Ship when real users cache 5+ repos, disk complaints arrive, concurrent forge failures surface, or users start asking "what's in my workspace?"

**Registry:** `registry.json` with `schema_version`, staleness thresholds, disk budget + LRU eviction, and PID-based locking. **CLI:** `skf workspace list/remove/clean/migrate`. **Cross-platform hardening:** Windows long paths, case-sensitivity detection, file-lock retry. **Recovery paths:** self-healing registry, git health check, auth-failure degradation.

### Layer 2 — Tool Tenants *(triggered)*

Ship when Layer 1 is stable and a target tool meets the **Tool Maturity Gate**: versioned schema, 6+ months of releases, no critical security fixes in the last 3 months, deletion handling in incremental updates, and Linux/macOS/Windows support. Tools persist outputs inside repo checkouts (`.cocoindex_code/`, `graphify-out/`, etc.); the registry's extensible `tools` section tracks per-tool state without tool-specific code.

### Layer 3 — Cross-Repo Intelligence *(triggered)*

Ship when Layer 2 graphify (or alternative) integration is proven AND a graph-merging API exists. Scope: merge per-repo graphs into a unified stack graph, Leiden community detection across repos for architectural layers, forge intelligence prompts ("you've forged N skills from this repo, here are unexplored communities"), stack-skill drift detection at the relationship level, and workspace-level QMD collections.

### Architectural decision: two-tier vs collapsed-tier

Layer 2/3 as written assumes tenants produce per-repo outputs that Layer 3 merges later — matching graphify-shaped tools. A credible alternative (CodeGraphContext-shaped) indexes all repos into a single embedded graph backend (KùzuDB) with queries scoped by `repo_path`, collapsing Layer 2 and Layer 3 into one tier.

**Both shapes remain open.** Path A preserves tenant modularity and matches the current roadmap; Path B reaches Layer 3 primitives sooner at the cost of letting one tool own more of the surface. The choice will be made when a candidate tool first meets the Tool Maturity Gate; this decision is recorded here so integration work stays coherent with whichever path we commit to.

---

## Layer 2 Tenant Candidates

SKF contributes upstream rather than forking. Three OSS candidates are tracked as parallel options; none currently clears the Tool Maturity Gate (the 6-months-of-releases criterion in particular). The first to clear becomes the Layer 2 anchor; the others remain referenced.

Layer 3 decomposes into two primitives — cross-repo graph merge and community detection. No single candidate ships both today, which is load-bearing context for the path chosen.

**Candidates (as of 2026-04-19):**

- **[safishamsi/graphify](https://github.com/safishamsi/graphify)** — MIT, ~30k stars. Tree-sitter + NetworkX + **Leiden clustering** (the algorithm named in Layer 3 above; other candidates do not ship it). Narrowest surface to audit; parallel version branches in CI signal healthier release-engineering than a single-branch pre-1.0 project.
  - Open P0s: versioned `graph.json` schema; Windows CI coverage (CI is currently `ubuntu-latest` only).
  - Open P1s: cross-repo graph-merge API; stable, documented Python API; shallow-clone validation.

- **[CodeGraphContext/CodeGraphContext](https://github.com/CodeGraphContext/CodeGraphContext)** — MIT, ~3k stars, 14 languages. **Native multi-repo unified graph** via KùzuDB (embedded, Windows-supported) scoped by `repo_path`; "Bundles" ship pre-indexed library graphs. Would require committing to the collapsed-tier architectural path.
  - Open P0s: **no community detection implemented** — a direct Layer 3 primitive SKF would need to add upstream or delegate; one-pass security review (a hardened fork exists with claimed path-traversal and Cypher-injection patches — upstream status unverified).
  - Open P1s: stable programmatic API; shallow-clone validation.

- **[repowise-dev/repowise](https://github.com/repowise-dev/repowise)** — **AGPL-3.0**, ~1.2k stars. Full codebase-intelligence platform (dependency graph, git intelligence, dead code, decision extraction, MCP + REST + dashboard). `--index-only` zero-LLM mode covers the parts SKF cares about without forcing API keys on users.
  - License note: AGPL-3.0 permits subprocess/CLI use from MIT code (SKF invokes the `repowise` binary). Importing repowise as a library would trigger AGPL contagion — not permitted. Network §13 would constrain any future hosted-SKF offering.
  - Open P0s: reach 6+ months of releases (currently <1 month old); Louvain → Leiden swap if Layer 3 is to match the algorithm named above; cross-repo support in OSS (currently hosted-only); Windows CI coverage (`ubuntu-latest` only).

**Non-candidates (documented so they are not re-discovered):**

- **[abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus)** — PolyForm Noncommercial 1.0.0. Source-available, not OSI-open. Disqualified for SKF integration irrespective of technical fit (which is strong: multi-repo groups, CLI + MCP + browser).
- **github/stack-graphs** — archived 2025-09-09. Referenced only as a cautionary data point against per-language graph-construction DSLs.
- **CodeGraph-Rust** — no canonical repository located; removed from tracking pending a verified URL.

---

## Spec Sync Mechanism

Pending an upstream agentskills.io spec endpoint. SKF currently version-pins to an agentskills.io spec at release time; once upstream publishes a canonical endpoint, SKF will add a sync path — likely a maintainer-side release script, not a runtime CLI flag.
