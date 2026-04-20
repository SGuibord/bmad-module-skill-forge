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

| Rule                     | Effect                                                                                                                     |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------|
| `deletion`               | Branch cannot be deleted.                                                                                                  |
| `non_fast_forward`       | Force-push blocked.                                                                                                        |
| `pull_request`           | Requires ≥ 1 approving review; `require_code_owner_review: true` (see CODEOWNERS note below); merge/squash/rebase allowed. |
| `code_quality`           | Blocks merge on `severity: errors` from GitHub code-quality checks.                                                        |
| `required_status_checks` | Merge blocked until all seven `quality.yaml` checks pass (names below).                                                    |

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

**CODEOWNERS note:** the `pull_request` rule has `require_code_owner_review: true`, but no `.github/CODEOWNERS` file exists in the repo today. GitHub treats the code-owner requirement as vacuously satisfied when the file is absent, so this setting is currently a no-op — the only active review gate is `required_approving_review_count: 1`. If a CODEOWNERS file is added later, make sure the listed owners can actually approve PRs from other authors (GitHub disallows self-review as a code owner, which would deadlock solo-maintainer PRs).

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

## Release Environment

The publish job is gated by a **GitHub [deployment environment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) with a required-reviewer rule** (not by workflow logic). A job declaring `environment: release` pauses until a listed reviewer clicks "Approve and deploy" in the Actions UI.

**Environment:** `release` — id `14347249917` — created 2026-04-20.

| Setting                      | Value                                               |
|------------------------------|-----------------------------------------------------|
| `wait_timer`                 | `0` (no artificial delay; approval is the only gate) |
| `prevent_self_review`        | `false` — see rationale below                       |
| `reviewers`                  | `armelhbobdad` (user id `132626034`), 1 approver    |
| `deployment_branch_policy`   | `custom_branch_policies: true`, list: `main` only   |
| Environment-scoped secrets   | `0` (invariant — see `NPM_TOKEN` note below)        |
| Cost                         | `$0` on public-repo tier (environments, required reviewers, and branch policies are [free for public repositories](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#about-environments)) |

**`prevent_self_review: false` — correctness constraint, not a loosened control.** Solo-maintainer setups cannot self-approve when this is `true`, so the gate would deadlock on any maintainer-triggered publish. The value flips to `true` the moment a second reviewer joins — do not leave it loose by inertia.

**`NPM_TOKEN` is NOT scoped to this environment.** It remains at repo-level secrets during the OIDC transition and is removed entirely post-v1.0.0 (see Story 6.3). The invariant: the `release` env must have zero secrets. If a future change scopes any secret here, re-audit whether the OIDC trusted-publisher path is still in force.

**Coupling with npm trusted publishing (Story 1.3).** The npm trusted publisher binds on four fields — `organization=armelhbobdad`, `repository=bmad-module-skill-forge`, `workflow filename=release.yaml`, `environment=release`. The environment name above is load-bearing: any rename here must be accompanied by a matching npm-side update in the same change, or the next publish returns 404.

### Inspect current state

```bash
# Environment itself (reviewers, branch-policy shape, prevent_self_review)
gh api repos/armelhbobdad/bmad-module-skill-forge/environments/release

# Allowed deployment branches (expect: one entry, name "main")
gh api repos/armelhbobdad/bmad-module-skill-forge/environments/release/deployment-branch-policies

# Environment-scoped secrets (expect: zero)
gh api repos/armelhbobdad/bmad-module-skill-forge/environments/release/secrets
```

### Restore / re-apply

Two-call pattern — the environment and its branch-policy list are separate resources. Creating the environment alone with `custom_branch_policies: true` leaves the allow-list empty, which rejects every dispatch; the second call is mandatory.

```bash
# (1) Create or update the environment with the required-reviewer gate
gh api --method PUT repos/armelhbobdad/bmad-module-skill-forge/environments/release --input - <<'JSON'
{
  "wait_timer": 0,
  "prevent_self_review": false,
  "reviewers": [{ "type": "User", "id": 132626034 }],
  "deployment_branch_policy": {
    "protected_branches": false,
    "custom_branch_policies": true
  }
}
JSON

# (2) Add main to the allowed deployment branches
gh api --method POST repos/armelhbobdad/bmad-module-skill-forge/environments/release/deployment-branch-policies --input - <<'JSON'
{ "name": "main" }
JSON
```

### Temporarily allowing a feature branch

A release workflow that declares `environment: release` will be rejected from any branch not on the allow-list. For legitimate validation cuts from a feature branch (Story 3.2's alpha cut is the canonical case), widen the allow-list for the duration of the test and tighten it back immediately:

```bash
# Allow the feature branch (capture the returned policy id)
gh api --method POST \
  repos/armelhbobdad/bmad-module-skill-forge/environments/release/deployment-branch-policies \
  --input - <<'JSON'
{ "name": "feat/my-validation-branch" }
JSON
# → { "id": <POLICY_ID>, "name": "feat/my-validation-branch", ... }

# ... run the validation cut, approve via the reviewer UI, confirm publish ...

# Revoke immediately — the allow-list must return to { main } before leaving the session
gh api --method DELETE \
  repos/armelhbobdad/bmad-module-skill-forge/environments/release/deployment-branch-policies/<POLICY_ID>
```

Leaving a feature branch on the allow-list is an unguarded hole — any later `workflow_dispatch` from that branch would be able to reach the publish path. Treat the revoke as the last step of the validation, not a follow-up.

<!-- Rollback Playbook — added in Story 4.1 -->

## Rollback Playbook

_To be authored in Story 4.1 — rollback playbook covering scenarios such as failed publish, tag mismatch, bad `latest` dist-tag, OIDC auth failure, and post-publish security issue._
