---
title: Releasing SKF
description: Maintainer reference for the release pipeline — branch protection, release workflow, and rollback procedures.
---

This document records the configuration that gates releases of `bmad-module-skill-forge`. It exists so a future maintainer (including future-you) can audit, restore, or extend the pipeline without reverse-engineering GitHub settings.

For background on GitHub rulesets vs legacy branch protection, see the [GitHub ruleset docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets).

## Branch Protection on `main`

`main` is gated by a **GitHub repository ruleset** (not legacy branch protection). The legacy "Settings → Branches → Branch protection rules" surface returns 404 for this repo.

**Ruleset:** `Default` — id `13855503` — applies to `~DEFAULT_BRANCH` (currently `main`) — enforcement `active`.

**Active rules (5):**

| Rule                     | Effect                                                                                 |
|--------------------------|----------------------------------------------------------------------------------------|
| `deletion`               | Branch cannot be deleted.                                                              |
| `non_fast_forward`       | Force-push blocked.                                                                    |
| `pull_request`           | Requires ≥ 1 approving review; requires CODEOWNERS review; merge/squash/rebase allowed. |
| `code_quality`           | Blocks merge on `severity: errors` from GitHub code-quality checks.                    |
| `required_status_checks` | Merge blocked until all seven `quality.yaml` checks pass (names below).                |

**Required status checks (7):** sourced from `.github/workflows/quality.yaml` job keys. Matrix jobs expand to `jobname (matrix-value)`:

- `prettier`
- `eslint`
- `markdownlint`
- `validate (ubuntu-latest)`
- `validate (windows-latest)`
- `python (ubuntu-latest)`
- `python (windows-latest)`

**Coupling with `quality.yaml`:** if that workflow renames a job or changes the `strategy.matrix.os` for `validate` or `python`, the ruleset's `required_status_checks` list must be updated in lock-step — otherwise merges to `main` will either block on a check name that no longer reports, or silently pass without the renamed check. Update both in the same PR.

**`strict_required_status_checks_policy: false`** — PR branches are not forced to be up-to-date with `main` before merging. This avoids constant rebases on a low-traffic repo. Flip to `true` if concurrent merges start producing logical conflicts the checks can't catch.

**Bypass actors:** `RepositoryRole` actor_id=5 (Admin), `bypass_mode: pull_request`. Admins can bypass the ruleset **only via a pull request**, never via direct push. This preserves `non_fast_forward` and the required-checks gate for the `github-actions[bot]` account that the future `release.yaml` workflow (Story 3.1) will use to push tags and commits to `main`. **Do not add a bot-specific bypass**; it would defeat the whole purpose of this ruleset.

### Inspect current state

```bash
gh api repos/armelhbobdad/bmad-module-skill-forge/rulesets/13855503
```

### Restore from a saved baseline

A JSON baseline captured before any change can be replayed via:

```bash
# Extract rules + bypass_actors from a saved baseline.json
jq '{rules, bypass_actors}' baseline.json > /tmp/restore.json

gh api --method PUT \
  repos/armelhbobdad/bmad-module-skill-forge/rulesets/13855503 \
  --input /tmp/restore.json
```

The GitHub ruleset API uses `PUT` (not `PATCH`) for updates, and the `rules` array is replaced wholesale — it is not merged server-side. Always fetch current state, modify the in-memory copy, and `PUT` the complete list.

<!-- Rollback Playbook — added in Story 4.1 -->

## Rollback Playbook

*To be authored in Story 4.1 — six scenario playbook covering failed publish, tag mismatch, bad `latest` dist-tag, OIDC auth failure, and post-publish security issue.*
