---
id: speckit-harness-integration
owner: {{REPO_NAME}}
status: accepted
last_reviewed: {{DATE}}
update_trigger: on-harness-change
---

# ADR speckit-harness-integration — Spec-kit as artifact pipeline, harness as governance layer

## Status

Accepted. Amends [ADR harness-design](harness-design.md) on the literal
vendor-neutrality rule and on where the active plan artifact lives.

## Context

The organization mandates GitHub spec-kit across repositories to standardize
feature specification, planning, task generation, and unattended implementation
loops. This repository adds a harness that governs agent work through Brief,
Decide, Plan, and Execute phases, with two hard controls:

- `covers:` bounds the files an approved plan may touch.
- `verify:` defines the command that proves the change works.

Spec-kit contributes useful artifacts and inferential checks, but it does not
bound file scope, does not execute a feature's verification command during
convergence, and would otherwise generate a plan and authorize it in the same
act. Running both systems independently would create two plan artifacts and no
clear authority.

## Decision

Spec-kit is the artifact pipeline. The harness is the governance layer over it.

Spec-kit owns:

- `spec.md`, the feature brief.
- `/speckit-clarify` and `/speckit-analyze`, the inferential sensors that catch
  ambiguity and inconsistency before implementation.
- `/speckit-implement` and `/speckit-converge`, the unattended loop engine.

The harness owns:

- `covers:`, because spec-kit has no scope-bounding control.
- `verify:`, because converge does not run the codebase's proof command.
- The human approval gate: `/speckit-plan` emits `status: draft`, and only a
  separate human-reviewed promotion to `status: active` authorizes edits.

The single active plan artifact is `specs/<feature>/plan.md`. It carries
`ticket:`, `status:`, `covers:`, `verify:`, and `analyzed:` frontmatter, added
to `.specify/templates/plan-template.md` by the harness.

Spec-kit generated skills under `.claude/skills/speckit-*` and
`.agents/skills/speckit-*` are committed as generated integration artifacts.
They are not hand-edited. Harness-authored hook skills live once under
`.agents/skills/` and are symlinked into `.claude/skills/`.

The constitution is supreme, not owned by the harness. `.specify/memory/constitution.md`
is the highest-authority document, owned by the team via `/speckit-constitution`.
The harness governs *process* (`covers:`/`verify:`/gate/loop), which is
orthogonal to the constitution's *principles*; `AGENTS.md` defers to the
constitution and the plan Constitution Check reads from it. The harness never
authors, overwrites, or deletes it.

The harness therefore edits exactly one spec-kit file —
`.specify/templates/plan-template.md` (frontmatter + a Constitution Check that
points at the constitution). Everything else it adds lives alongside spec-kit
(`.specify/extensions.yml`, the `harness-*` skills, `scripts/harness/`,
`docs/`), connected through spec-kit's native hook mechanism.

## Consequences

- `docs/PLANS.md` is a style contract for `specs/<feature>/plan.md`.
- The pre-commit coverage sensor reads active spec-kit plans from
  `specs/*/plan.md` in the git index and rejects zero or multiple active plans
  whenever staged source files need coverage.
- Hook instructions in `.specify/extensions.yml` are soft controls: agents must
  read and obey them, but there is no runtime enforcement. The pre-commit
  coverage check remains the hard control.
- `/speckit-constitution` step 4 and `/speckit-implement` step 4 are
  neutralized by policy rather than by editing generated skills, because both
  can create drift or write outside the active plan's `covers:`.
