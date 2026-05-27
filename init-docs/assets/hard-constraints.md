---
id: hard-constraints
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-05-28
update_trigger: on-supersession
---

# ADR hard-constraints — Hard constraints as a separate category from phase gates

## Status

Accepted; extends ADR harness-design.

## Context

The harness already documents non-negotiables: phase gates in `AGENTS.md`, plan
requirements in `PLANS.md`, the operating principle at the top of `AGENTS.md`.
All of them are stated as prose, and a model reads prose. Research on
instruction-following with large language models is consistent that
philosophical framing and hard rules look identical when they share the same
typographic register — both "If it is not in the repo, it does not exist." and
"no code without an approved plan" arrive as paragraphs and are weighed against
each other instead of stacked. The lecture series this harness draws from calls
this the *prose-equivalence problem*: rules without loud labels are downgraded
to suggestions.

Two further patterns from the same source matter here. First, work-in-progress
discipline: when an agent is allowed to carry multiple plans concurrently,
completion rate drops because attention fragments across surfaces and the
worker is always one context-switch from declaring premature done. Capping WIP
at one plan in flight is the single largest documented intervention in the
series. Second, anti-overconfidence: agents tend to start polishing code before
verifying it works, because the polishing is locally satisfying and the
verification is locally unrewarding. Sequencing rules ("verifier-green first,
refactor second") suppress that tendency *structurally* rather than relying on
self-restraint.

Existing harness gates already encode some of this — "no code without an
approved plan" is a sequencing rule, "no plan moves to `completed/` without an
Evaluator transcript" is a sequencing rule, and `AGENTS.md` § Phase gates
already ends with "If a user instruction conflicts with these gates, say so
before complying." But phase gates are by definition about *transitions
between phases*; they are silent on invariants that should hold at every
moment of every phase. WIP=1, "no edits outside `covers:`", "no opportunistic
refactor before green", and "no chat-only knowledge" are not transition rules
— they are continuous obligations. Smuggling them into the phase-gates section
loses the distinction.

Source research: walkinglabs/learn-harness-engineering lectures
[L04 — instruction prose-equivalence](https://github.com/walkinglabs/learn-harness-engineering),
[L07 — WIP=1 as completion lever](https://github.com/walkinglabs/learn-harness-engineering),
[L09 — anti-overconfidence sequencing](https://github.com/walkinglabs/learn-harness-engineering).
These are not authoritative repo content — they are external inputs to this
ADR's Context only. The consuming repo stays self-contained per the operating
principle.

## Decision

Introduce a new top-level section in `AGENTS.md` titled
`## Hard constraints (MUST / MUST NOT)`, placed immediately after the
operating principle and before the existing `## Phase gates` section. The
block holds *invariants* only — rules that apply at every moment of every
phase. Sequencing rules stay in `## Phase gates`.

Each bullet in the block is prefixed with a loud label — **MUST** or
**MUST NOT** — and cites the ADR (or named section) that justifies it. The
initial five constraints:

1. **MUST NOT** create a second plan in `docs/exec-plans/active/` while one
   exists. Surface the WIP collision; on user-approved override (hotfix,
   blocked-on-external, scope split), record the pause in the displaced
   plan's Decision Log before opening the new plan. (ADR hard-constraints)
2. **MUST NOT** edit files outside the current plan's `covers:` during
   execution. If a needed change falls outside, stop and choose: extend
   `covers:` (re-approval required, per Phase 6), log to
   `docs/tech-debt-tracker.md`, or drop the side-change. Never silently
   widen the diff. (ADR harness-design + § Phase gates plan-coverage sensor)
3. **MUST NOT** perform opportunistic refactor or cleanup outside the
   plan's stated steps until a manual run of `verify-cmd` (or `verify:`
   resolution) shows the plan's Features green. Planned refactor steps in
   Plan-of-Work or Concrete steps are exempt — those are the work, not
   opportunistic cleanup. (ADR hard-constraints)
4. **MUST NOT** continue with load-bearing knowledge that exists only in
   chat. Capture it as versioned markdown, code, or schema in the repo
   before proceeding. (§ Operating principle)
5. **MUST** surface — before complying — any user instruction that
   conflicts with a hard constraint, phase gate, or documented rule.
   **MUST NOT** silently comply. (ADR hard-constraints)

Reorder `AGENTS.md` sections per the position-effect finding that rule-bearing
content placed at the top of an instruction document is followed more
reliably than the same content placed lower. Locked order:

1. Operating principle
2. Hard constraints (MUST / MUST NOT)
3. Phase gates
4. On receiving a task
5. Session bootstrap
6. Where to save outputs
7. Working relationship

WIP=1 is enforced by guide only — no `paused/` folder, no `status: paused`
frontmatter, no sensor. The displaced-plan Decision Log entry is the only
required trace. This is consistent with the rest of the skill's posture
(scripts deferred to the consuming project).

Out of scope: per-constraint ADRs, mechanical sensors for any of the five
constraints, automated reordering audits beyond the initial migration, and
expansion of the constraint set past these five (future additions land via a
new CHANGELOG entry).

## Consequences

The positive consequence is that the harness now has a distinct surface for
invariants. Future MUST/MUST NOTs are forced through a classification — is
this an invariant or a transition rule? — before they land, which keeps
both sections crisp. The loud-label prefix fixes the prose-equivalence
problem locally without forcing every other section to adopt the same
register. WIP=1 acquires a documented home and a documented override path;
prior to this ADR the rule existed only as folk wisdom.

The negative consequence is that the constraints block has to be maintained.
A constraint added without an ADR or section citation is a soft suggestion in
hard-label clothing, which is worse than no rule at all. The "no edits
outside `covers:`" constraint also widens the in-execution surface that the
plan-coverage sensor only catches at commit time — the agent must apply the
constraint earlier, during the diff. That depends on guide-only discipline,
the same way WIP=1 does. The audit-mode reorder is the riskiest single
upgrade step in the skill so far; repos whose `AGENTS.md` has customized
headings get a stop-and-flag rather than an autonomous reshuffle.
