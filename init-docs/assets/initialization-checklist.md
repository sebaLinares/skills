---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-bootstrap-contract-change
---

# Initialization checklist — the bootstrap contract

The contract every freshly-scaffolded repo must satisfy before it is
operable by an agent that has never seen it. Four conditions, each
mapped to a concrete surface in this repo. Verified mechanically at the
end of every `/init-docs` run (Step 18 closing section); also
re-verified by the quarterly [Cold-start
test](cold-start-test.md).

Distinct from `AGENTS.md` § Session bootstrap (the *protocol* an agent
runs every session). This file documents the *property* — whether the
repo can be picked up at all.

## Why this exists

A scaffold without an explicit "initialization complete" gate is
documentation, not initialization. The repo could look complete
(folders present, AGENTS.md written, ADRs seeded) while still being
unoperable (no run command, no test command, empty FEATURES). The
bootstrap contract is the falsifier: it names the four properties
that make the difference between *a scaffold* and *an operable repo*.

## The four conditions

| # | Condition | Surface | Pass test |
|---|---|---|---|
| 1 | **Can start** | [`processes/dev-setup.md`](processes/dev-setup.md) § Common commands → Build, Run locally; § Running locally | Sections exist; Build and Run-locally commands are non-placeholder (no `<command>`, no `*Fill in:*`) |
| 2 | **Can test** | [`processes/dev-setup.md`](processes/dev-setup.md) § Common commands → Run tests; § Feature verification convention | Sections exist; commands and convention are non-placeholder |
| 3 | **Can see progress** | [`FEATURES.md`](FEATURES.md) + `exec-plans/active/` + [`README.md`](README.md) | Files/folders exist; FEATURES.md carries the 5 state sections; catalog has Features + Exec plans + Tech debt rows |
| 4 | **Can pick up next steps** | [`FEATURES.md`](FEATURES.md) § Active + § Failing + `exec-plans/active/` + [`tech-debt-tracker.md`](tech-debt-tracker.md) | Files exist and are readable; empty is legitimate |

## Two-level pass

Each condition resolves to one of three states:

- **surface present, populated.** The artifact exists and carries
  non-placeholder content. The condition is satisfied.
- **surface present, placeholder.** The artifact exists with
  scaffold-default placeholder text (`*Fill in:*`, `<command>`,
  `{{PLACEHOLDER}}`). Not a skill bug — the user has not yet filled
  in the stack-specific commands. Reported as `[⚠ placeholder]`.
- **surface missing.** The artifact does not exist where the
  contract says it should. This is a *skill bug* (the scaffold did
  not write the file). Reported as `[✗ surface missing]`; the user
  should re-run `/init-docs` or file an issue.

Empty is not placeholder. `FEATURES.md` § Active being empty after a
fresh scaffold is the correct state — the harness has not yet been
exercised. The placeholder check looks for *unresolved scaffold
markers*, not for blank tables.

## How to fix a failing condition

| Condition | If `[⚠ placeholder]` | If `[✗ surface missing]` |
|---|---|---|
| Can start | Edit `dev-setup.md` § Common commands → Build, Run locally with this stack's commands. Fill in § Running locally with env vars and startup command. | Re-run `/init-docs`. If missing again, file an issue against the skill. |
| Can test | Edit `dev-setup.md` § Common commands → Run tests. Fill in § Feature verification convention with this stack's tag-filter shape. | Re-run `/init-docs`. |
| Can see progress | (No placeholder state — empty FEATURES + empty active/ is the correct fresh state.) | Re-run `/init-docs`. If `FEATURES.md` is the missing surface, see the 2026-05-18 CHANGELOG entry for the migration. |
| Can pick up next steps | (No placeholder state.) | Re-run `/init-docs`. |

## When this is verified

Every `/init-docs` invocation re-verifies the contract as the closing
section of its Step 18 report — both for fresh scaffolds and for
audit-mode runs on existing repos. A re-run on a fully-up-to-date
repo still prints the verdict because the verdict is the point — it
tells the agent whether the bootstrap contract is satisfied right now,
not whether anything changed.

The quarterly [Cold-start test](cold-start-test.md) re-verifies the
*legibility* side of the same property (can a fresh agent answer five
questions from repo content alone). Failing a cold-start question
typically means the bootstrap contract for that surface has regressed
— re-run this checklist on the affected surface.

## Out of scope

- Per-condition automated remediation (the skill ships docs-only;
  fixing placeholders is the user's job).
- Mechanical enforcement at session bootstrap (the contract is a
  scaffold/audit-time property; runtime checks are session bootstrap's
  job).
- Coupling to Session exit (per-session checklist) or to the
  harness-version check (skill-version drift detection). Each has its
  own purpose and cadence.
