---
title: SKF Stability & Public API Contract
description: What SemVer covers at v1.0.0 — the surfaces downstream consumers may pin against, and the surfaces explicitly excluded.
---

> **Status:** DRAFT — locks at v1.0.0 cut (Story 5.1 pre-flight audit). Review-window open until then.

This document is the public API contract for `bmad-module-skill-forge` at v1.0.0. It enumerates exactly which SKF surfaces [Semantic Versioning 2.0.0](https://semver.org/) covers and which are explicitly `@internal`. The goal is that a downstream consumer pinning `"bmad-module-skill-forge": "^1.0.0"` can identify — unambiguously — whether a given SKF change is breaking, additive, or internal. Breaking changes to covered surfaces require a major-version bump; additive changes to covered surfaces are minor bumps; changes to `@internal` surfaces are free to land in any release.

## Covered Surfaces

The five buckets below are the entirety of the v1.0.0 public surface. Anything not explicitly listed here is `@internal` (see [§ @internal — Not Covered by SemVer](#internal--not-covered-by-semver)).

### CLI Command Surface

The CLI is invoked via `npx bmad-module-skill-forge <subcommand>` (one-shot) or `npm run skf:<subcommand>` (post-install). Covered:

- **Subcommands**: `install`, `update`, `status`, `uninstall`. Renaming, removing, or changing the semantics of any subcommand is breaking.
- **Top-level options**: `-V, --version` (prints the installed package version) and `-h, --help` (prints command help). Provided by commander as part of the entrypoint at `tools/cli/skf-cli.js`.
- **Per-subcommand flags**: none are currently part of the v1.0.0 surface. Each subcommand today accepts no flags. Adding a new flag is additive (minor); removing or renaming a flag once added would be breaking.
- **Exit codes**: `0` on success (including user-cancel on `install` and "nothing to do" paths on `uninstall`); `1` on unhandled failure. Intermediate exit codes are not part of the contract.
- **`npm run skf:*` script aliases**: `skf:install`, `skf:update`, `skf:status`, `skf:uninstall` in `package.json` are the post-install convenience entry points. Renaming or removing any `skf:*` script is breaking. (Note: `release:*` scripts are NOT part of this contract — they are internal-to-maintainers and are being retired across Epic 4 and Epic 6.)

### Programmatic API of `tools/cli/skf-cli.js`

`tools/cli/skf-cli.js` is the CLI entrypoint for `npx bmad-module-skill-forge` and for `npm run skf:<subcommand>`. Though `package.json`'s `main` field points at this file (standard npm resolution for bin-like packages), it has **no programmatic export surface**. The file runs commander setup and calls `program.parse(process.argv)` as top-level side effects; it has no `module.exports` block. A `require('bmad-module-skill-forge')` from Node runs the CLI parser against the caller's `process.argv` — not a supported usage.

Programmatic embedding of SKF is explicitly `@internal` at v1.0.0. If a programmatic API is ever added, it will be introduced via an explicit `module.exports` block and a minor version bump (additive).

### Skill Manifest & Frontmatter Contract

**`SKILL.md` frontmatter.** SKF-shipped `SKILL.md` files conform to the [agentskills.io minimal frontmatter spec](https://github.com/agentskills/agentskills). Required fields are `name` (kebab-case) and `description` (one-line natural-language summary that terminates with an explicit trigger phrase — see the `src/skf-*/SKILL.md` files in this repo for live examples). SKF does NOT extend the agentskills.io spec; there are no SKF-specific frontmatter fields. If the agentskills.io spec evolves, SKF tracks upstream rather than forking.

**`bmad-skill-manifest.yaml` schema.** The agent-type skill manifest shape SKF uses is validated by the zod schema at `test/schema/agent.js`:

```js
const manifestSchema = z
  .object({
    type: z.enum(['agent', 'workflow', 'tool']),   // required
    name: createNonEmptyString('name'),            // required
    displayName: createNonEmptyString('displayName').optional(),
    title: createNonEmptyString('title').optional(),
    icon: z.string().optional(),
    capabilities: z.string().optional(),
    role: createNonEmptyString('role').optional(),
    identity: createNonEmptyString('identity').optional(),
    communicationStyle: createNonEmptyString('communicationStyle').optional(),
    principles: createNonEmptyString('principles').optional(),
    module: createNonEmptyString('module'),        // required
  })
  .strict();
```

The schema is strict — unknown keys are rejected. Renaming or removing a required field, changing an enum value, or tightening an optional field into required is breaking. Adding a new optional field is additive. The `module` field is always `skf` for SKF-authored manifests.

### Installation Layout

When a consumer runs `skf install` in a project, SKF creates or modifies exactly the following on-disk paths. Paths outside this list are not touched (no surprise edits to project root). Renaming any path, changing a path's semantics, or removing a path from this list is breaking.

- `_bmad/skf/` — SKF module files.
- `_bmad/_config/skf-manifest.yaml` — install manifest. Format per `tools/cli/lib/manifest.js`; covered top-level keys: `version`, `installed_at`, `action`, `module`, `skf_folder`, `ides`, `skills_output_folder`, `forge_data_folder`, `directories[]`, `files.{skf,sidecar,ide_skills,learning,output}`. Downstream tooling that introspects an SKF install (e.g. to detect installed IDEs or list installed skills) reads this file; its top-level shape is the v1.0.0 contract.
- `_bmad/_memory/forger-sidecar/` — Ferris agent runtime state directory. The directory's existence and location are covered; the internal file structure and schemas inside are `@internal` (stable as a runtime contract between SKF versions during the life of one install, but not a downstream-consumable API).
- `_skf-learn/` — optional learning material; created only when the user opts into learning at install time.
- `{skills_output_folder}/` — default `skills/`, configurable via install prompt and persisted to `skf-manifest.yaml`.
- `{forge_data_folder}/` — default `forge-data/`, configurable via install prompt and persisted to `skf-manifest.yaml`.
- **Per-IDE skill directories.** SKF installs skills to each configured IDE's conventional skills directory. The IDE → directory mapping is enumerated in `tools/cli/lib/platform-codes.yaml` under `platforms.<ide>.installer.target_dir`; that file is the source of truth and is itself part of the v1.0.0 contract. Specifically: renaming `platforms.*` or `installer.target_dir` is breaking; removing a platform's `target_dir` is breaking for consumers of that IDE; adding a new platform entry is additive (minor).

### User-Facing Command Output Formats

The v1.0.0 contract commits to the **information each command outputs** and to **exit-code semantics**, not to exact human-readable wording, ANSI color choices, or console layout. Downstream tooling that needs structured introspection of an install should read `_bmad/_config/skf-manifest.yaml` directly (see [§ Installation Layout](#installation-layout)), which IS committed verbatim.

- **`skf status`** SHALL convey: installation-present boolean, installed version string, forge-tier name (or a "not detected" equivalent), configured IDE list, workflow-skill count, sidecar state, and output-folder paths. Exit `0` on success; `1` on unhandled failure.
- **`skf install`** SHALL exit `0` on successful install and on user-cancel, `1` on unhandled failure. The success path SHALL emit a message referencing the SKF folder path created in the project.
- **`skf update`** SHALL exit `0` on successful update; `1` on unhandled failure. Update preserves existing config and sidecar state.
- **`skf uninstall`** SHALL exit `0` on successful removal, on "nothing to do" (no prior install detected), and on user-declined confirmation. Exit `1` on unhandled failure.

Explicit non-commitments: ANSI color choices, exact prose wording, precise layout of tables or lists, and i18n prose variations are `@internal` and may change in minor releases.

## @internal — Not Covered by SemVer

The following surfaces are explicitly excluded from the v1.0.0 contract. Changes to any of these may land in any release — patch, minor, or major — without constituting a "breaking change" from a SemVer perspective. Downstream consumers SHOULD NOT pin against these surfaces.

- **`tools/cli/lib/*` internal helper modules** — implementation detail of the CLI; not a library. Any refactor that preserves the observable CLI surface and install layout above is allowed.
- **Internal structure of workflow step files under `src/skf-*/steps-c/`** — the workflow authoring format is an SKF-internal authoring surface; step numbering, file names, and prose can change.
- **`_bmad/_memory/forger-sidecar/*.yaml` file schemas** — Ferris sidecar state. Stable as a runtime contract between SKF versions during one install's lifetime (so `skf update` works), but not a downstream-consumable schema.
- **Ferris agent persona prose and menu wording** — the in-product agent persona can be rephrased or restructured at any time.
- **Exact chalk styling / ANSI color choices in command output** — stylistic; see the output-format bucket above for what IS committed.
- **Internal logic of the `Installer` class in `tools/cli/lib/installer.js`** — private implementation; what's covered is the observable install layout, not how the files get there.
- **Workflow `{communication_language}` / `{document_output_language}` template substitution** — an authoring convenience for workflow prose; the mechanism is internal.
- **Knowledge-base contents under `src/knowledge/` and `src/skf-*/references/`** — evolving reference material, not a schema.
- **Test fixtures and test file layout under `test/`** — test organization is internal.
- **Build and docs tooling (`tools/build-docs.js`, `website/`)** — internal build pipeline for the Starlight docs site; not a consumer surface.
- **`_bmad-output/` planning-artifact layout** — gitignored and never distributed; not shipped in the npm package.

## How to Use This Contract

Pin SKF as a dependency with caret-range major-version pinning to get minor and patch updates automatically:

```json
"bmad-module-skill-forge": "^1.0.0"
```

The caret range covers additive changes and internal refactors on covered surfaces, and any change on `@internal` surfaces. If you find that an SKF release broke a covered surface listed in this document, please open an issue at the SKF issue tracker citing the relevant section — it is either a bug in SKF that needs reverting or a missed major-version bump.

If a surface you depend on is NOT explicitly enumerated in [§ Covered Surfaces](#covered-surfaces), treat it as `@internal` — if in doubt, it is `@internal`. If you believe a surface should be promoted from `@internal` to covered, open an issue with a use-case description; promotion is additive and can land in a minor release.

## Changes to This Contract

Shrinking the covered surface (removing a commitment) is a breaking change and requires a major-version bump. Expanding the covered surface (promoting an `@internal` surface to covered, or adding a new commitment) is additive and ships in a minor release. This document is versioned alongside the package; historical versions are visible via `git log docs/STABILITY.md`.

## References

- [agentskills.io spec](https://github.com/agentskills/agentskills) — external canonical source for the `SKILL.md` frontmatter grammar.
- [Semantic Versioning 2.0.0](https://semver.org/) — the SemVer semantics this contract commits to.
- [CHANGELOG.md](../CHANGELOG.md) — release-by-release history; breaking changes are called out there.
- [docs/RELEASING.md](RELEASING.md) — maintainer reference for the release pipeline (companion document: this file is about what ships, `RELEASING.md` is about how).
- `tools/cli/lib/platform-codes.yaml` — source of truth for the IDE → skills-directory mapping covered under [§ Installation Layout](#installation-layout).
- `test/schema/agent.js` — zod schema definitions for `bmad-skill-manifest.yaml` covered under [§ Skill Manifest & Frontmatter Contract](#skill-manifest--frontmatter-contract).
