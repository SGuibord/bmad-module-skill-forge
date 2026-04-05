# SKF Module Source

This directory contains the **Skill Forge (SKF)** BMAD module — the files that get installed into a BMAD project under `_bmad/skf/` when a user runs the installer.

For user-facing documentation (what SKF does, how to install it, how to use it), see the [repository README](../README.md) and the published docs at [armelhbobdad.github.io/bmad-module-skill-forge](https://armelhbobdad.github.io/bmad-module-skill-forge/).

## Layout

```
src/
├── module.yaml           # Module config: code, name, install prompts
├── module-help.csv       # Help registry — one row per agent command
├── agents/
│   └── forger.agent.yaml # Ferris — the single agent persona
├── workflows/            # 14 workflows (see workflows/README.md)
│   ├── setup-forge/
│   ├── analyze-source/
│   ├── brief-skill/
│   ├── create-skill/
│   ├── quick-skill/
│   ├── create-stack-skill/
│   ├── verify-stack/
│   ├── refine-architecture/
│   ├── update-skill/
│   ├── audit-skill/
│   ├── test-skill/
│   ├── export-skill/
│   ├── rename-skill/
│   └── drop-skill/
├── knowledge/            # Cross-cutting knowledge fragments (JiT loaded)
│   └── skf-knowledge-index.csv
└── forger/               # Sidecar seed files (preferences, forge tier)
```

## Components

- **Agent:** [Ferris](agents/forger.agent.yaml) — single-persona module operating in four modes (Architect / Surgeon / Audit / Delivery)
- **Workflows:** see [workflows/README.md](workflows/README.md) for the full index, typical flows, and the knowledge-vs-data distinction
- **Knowledge fragments:** cross-cutting principles Ferris consults via `knowledge/skf-knowledge-index.csv`

## Editing this module

- Agent edits — `agents/forger.agent.yaml`; validate with `bmad:bmb:agents:agent-validate`
- Workflow edits — each workflow in `workflows/{name}/`; validate with `bmad:bmb:workflows:workflow-validate`
- Module-level edits — `module.yaml` and `module-help.csv`; validate with `bmad:bmb:modules:validate-module`

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the contribution workflow.
