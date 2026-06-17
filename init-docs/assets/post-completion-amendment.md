---
id: post-completion-amendment
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-06-16
update_trigger: on-supersession
---

# ADR post-completion-amendment — Completed plans are mutable; per-artifact history, not a central log

## Status

Accepted; extends ADR harness-design and ADR evaluator-gate.

## Context

The harness lifecycle has one transition: `active/ → completed/`. Practice
revealed a recurring workflow it did not name: after a plan ships, the author
sometimes discovers the plan was *wrong about something* a few commits later and
wants to **amend the original plan** rather than spawn a new one. The user had
to issue this instruction manually each time — by the steering-loop's own rule,
a recurring manual instruction is a missing guide.

This punctures an implicit assumption: that `completed/` is frozen. It is not —
relevance can return to a shipped plan. The pre-write gate only protects
`active/`, so the orchestrator can already edit a completed plan; what was
missing was *how* the correction is recorded and whether it re-triggers the gate
chain.

Separately, a question arose: should the harness carry a history/activity log?
A central markdown ledger was rejected — the harness already has a central,
append-only, timestamped, authored change log: `git`. A hand-maintained ledger
would be a guide that rots (the exact disease being treated), a multi-session
write-hotspot, and an unbounded new pile. But git does not cheaply give an
in-context reader the *semantic event sequence* of one artifact, and frontmatter
props capture current state, not ordered events.

## Decision

**Amendment.** A correction to an already-completed ExecPlan is recorded in
place. The plan stays in `completed/`; it does **not** move back to `active/` and
does not re-run the planner → pre-approval critic → Evaluator chain. The
correction is added as a dated row in the plan's `## History` section. Re-running
the Evaluator is required only when the amendment changes shipped behavior
(code), not for a doc-only correction.

**Per-artifact history.** ExecPlans (and optionally analysis docs) carry a
`## History` table recording the ordered semantic events of the artifact's life
(shipped → found-wrong-about-X → amended → superseded). It is bounded by
construction and read in-context when the artifact is already loaded.

**No central log.** Git is the authoritative byte-level change record.
Current-state facts live in frontmatter (`status`, `superseded-by:`) where a
sensor reads them in O(1); ordered events live in the per-artifact `## History`
table where a reader consumes them as narrative. The two are complementary, not
rivals.

## Consequences

The "amend, don't spawn a new plan" workflow is now a harness guide instead of a
manual instruction repeated each time. Provenance for *why* a plan was corrected
lives where a future reader looks. The "re-evaluate only on behavior change"
clause keeps the checker honest without taxing doc-only fixes — at the cost that
an amendment which *should* have been re-reviewed could slip through as a "doc
fix"; the guide names the behavior/doc distinction explicitly to mitigate this.

Rejecting the central ledger keeps git as the single change-log authority and
avoids adding a write-hotspot rot-pile. The per-artifact `## History` table adds
a small, bounded section to the plan template.
