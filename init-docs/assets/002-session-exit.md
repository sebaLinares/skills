# ADR 002 — Session exit closes the bootstrap asymmetry

## Status

Accepted

## Context

The harness had a required session bootstrap but no matching session exit.
Phase 6 closes a plan, not a session: one agent conversation may contain zero
plans, one plan, many plans, or only investigation. That left repo state
dependent on chat memory at the point where the next agent most needs a clean
handoff.

L12 quantified the operational cost: repos without exit hygiene showed a
29-point build-pass-rate gap at week 12 compared with repos that had it. ADR
001 established the harness principle that load-bearing knowledge belongs in
the repo; session exit applies that principle to the end of each conversation.

## Decision

Add a Session exit convention to `docs/processes/harness.md` and instruct it
from `AGENTS.md`. It runs only on an explicit user signal such as "we're done",
"close out", "ttyl", "session exit", or "/quit"; there is no slash command and
no global skill.

The checklist has six dimensions: build, verifier, plan state, doc coherence,
startup viable, and chat-sweep. Its failure mode is hybrid: auto-fix mechanical
items where possible, surface judgment calls, and block-with-flag on build-red,
startup-red, or verifier regressions. The verifier dimension compares current
results against the `docs/FEATURES.md` state observed during session bootstrap;
`Passing` -> `Failing` regressions block, while pre-existing reds are reported.

## Consequences

`AGENTS.md` bootstrap now reads `docs/FEATURES.md` as a session baseline, not
only as the scope surface. The writer-partition rule for Feature state admits
session exit as a verifier-loop caller while preserving the split that ordinary
plan execution does not mark Features `Passing`.

Session exit cannot be mechanically enforced. Its leverage is discoverability:
the convention is named in the operating manual, cross-referenced from the
agent instructions, and routed into existing artifacts instead of creating a
new session log.
