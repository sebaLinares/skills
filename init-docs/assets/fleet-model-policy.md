---
id: fleet-model-policy
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-06-16
update_trigger: on-supersession
---

# ADR fleet-model-policy — Fleet model policy

## Status

Accepted; extends ADR harness-design on model selection.

## Context

The harness already treats load-bearing context as repo content: if it is not
in the repo, it does not exist. Model choice is also load-bearing context. When
it lives only in chat, failures cannot be compared across repos because each
session may have used a different implicit assignment. Naming models in the
scaffold makes telemetry compound: "the design subagent drafted the ADR" or "the checker checked
the plan" means the same thing in every repo.

The assignments deliberately keep stack-agnosticism while ending
model-agnosticism. The **orchestrator** tier carries the ordinary workflow
cheaply. The **design subagent** tier is reserved for design surfaces where
synthesis quality matters: phase-2 analysis synthesis, phase-4 broad or
irreversible ADRs, and phase-5 complex or multi-module ExecPlans. The
**checker / rescue** tier satisfies structural independence for checker and
rescue work by being a different model family, not merely a new context window.
Concrete version strings for each tier live only in
`docs/processes/model-policy.md` — this ADR names roles so it does not date.

## Decision

The harness adopts a three-tier fleet — **Orchestrator**, **Design subagent**,
and **Checker / rescue** (a different model family for structural independence).

`docs/processes/model-policy.md` is the **single source of truth for both the
per-step assignment and the concrete model version string of each tier**. No
other harness doc pins a version; all refer to a tier by role. This contains
version drift to one file — the prior practice of restating versions in
harness.md, AGENTS.md, and CONTEXT.md let three copies silently age. The default Evaluator command resolves to
`codex-companion.mjs adversarial-review --base <merge-base>`, invoked by the
orchestrator via Bash — the `/codex:adversarial-review` slash command sets
`disable-model-invocation: true` and cannot be reached from inside an agent
turn. The codex plugin is a soft dependency: if unavailable, the fallback
chain is the named codex command, then a fresh Claude subagent, then a human
reviewer.

Out of scope: mechanical enforcement, per-plan model frontmatter, cost
accounting, latency budgets, and model-routing automation.

## Consequences

The positive consequence is comparable telemetry across the fleet. Model drift
is now diagnosable because the expected assignment is explicit. The policy also
contains cost by keeping expensive design work off the default path, while
preserving an independent checker tier for the worker/checker split.

The negative consequence is maintenance burden. The lineup will date as model
quality and availability change. That burden is mitigated by keeping one
canonical policy document and changing the fleet through init-docs changelog
entries. The codex plugin also becomes load-bearing for the default checker
path; the documented fresh-subagent fallback keeps repos operable when the
plugin is absent.
