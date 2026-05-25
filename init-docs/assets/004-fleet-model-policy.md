# ADR 004 — Fleet model policy

## Status

Accepted; extends ADR 001 on model selection.

## Context

The harness already treats load-bearing context as repo content: if it is not
in the repo, it does not exist. Model choice is also load-bearing context. When
it lives only in chat, failures cannot be compared across repos because each
session may have used a different implicit assignment. Naming models in the
scaffold makes telemetry compound: "Opus drafted the ADR" or "GPT-5.5 checked
the plan" means the same thing in every repo.

The assignments deliberately keep stack-agnosticism while ending
model-agnosticism. Sonnet 4.6 high carries the ordinary workflow cheaply as the
orchestrator. Opus 4.7 xhigh is reserved for design surfaces where synthesis
quality matters: phase-2 analysis synthesis, phase-4 broad or irreversible
ADRs, and phase-5 complex or multi-module ExecPlans. GPT-5.5 high via the
codex plugin satisfies structural independence for checker and rescue work by
being a different model family, not merely a new context window.

## Decision

The harness adopts a three-tier fleet:

- Orchestrator: Sonnet 4.6 high.
- Design subagent: Opus 4.7 xhigh.
- Checker / rescue: GPT-5.5 high via the codex plugin.

The single source of truth for per-step assignment is
`docs/processes/model-policy.md`. The default Evaluator command resolves to
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
