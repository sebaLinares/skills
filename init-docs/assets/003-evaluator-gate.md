# ADR 003 — Evaluator gate at plan completion

## Status

Accepted

## Context

Phase 6 today lets one agent write the plan, execute it, declare it done, move
it to `completed/`, and commit — five worker-side steps with no independent
check between "I think I'm done" and "the repo says I'm done." That structure
is biased toward overconfidence (Guo et al. 2017): the same context that
produced the answer also grades it.

ADR 002 already partitions one slice of this — the verifier loop, not the
worker, writes FEATURES.md `Passing`. The worker/checker split named in
[`../CONTEXT.md`](../CONTEXT.md) is the umbrella principle. This ADR adds the
second concrete enforcer: a gate at the `active/` → `completed/` transition
for ExecPlans.

The lecture series this scaffold tracks
([walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering),
lectures 01, 09, 11) puts planner+generator+evaluator separation as its single
largest delta. The Anthropic data cited there is consistent with Guo et al.:
fresh context grading the work outperforms the worker grading itself.

## Decision

Introduce the **Evaluator** role and the **Evaluator transcript** artifact.

**Role.** A reading-only checker for ExecPlan completion. Played by any
coding agent or tool that does not share state with the plan's worker —
fresh subagent, separate session, external CLI agent (Codex, `claude -p
…`, equivalents), or human reviewer. Independence is the load-bearing
property: same agent, same session, same context does not qualify.

**Invocation contract.** Universal shape `<evaluator-cmd> <plan-path>`.
The consuming repo declares the concrete command in
`docs/processes/dev-setup.md` § Evaluator convention, alongside the
verifier convention. The Evaluator writes its output directly into a
dedicated `## Evaluator transcript` section in the plan file itself; the
worker never edits that section. Independence is structural — different
writer, different context — rather than convention-only.

**Verdicts.** Two required, one optional.

- **Alignment** (required) — the diff implements what the plan's
  Plan-of-Work and Concrete Steps said it would. Catches scope drift
  and silent omissions.
- **Acceptance** (required) — the plan's Validation & Acceptance
  criteria were actually verified, with evidence (test transcripts,
  observable outputs).
- **Quality** (optional) — code-quality review. A failing quality
  verdict is *not* a completion blocker by itself; it routes to
  `docs/tech-debt-tracker.md`. Folding code quality into the completion
  gate would conflate two sensors and block plan closure on style
  misses — the maintainability harness's job, not the gate's.

**Closure rule.** Worker moves the plan to `completed/` only if the
latest transcript block has Alignment + Acceptance both `pass`. On
fail, the plan stays in `active/`; the worker logs the failure in the
Decision Log, addresses it, and re-invokes the Evaluator. Each retry
appends a new timestamped block to the transcript section — history is
preserved for the steering loop.

**State machine.** No new `status:` value. The transcript section is
the state; `status` stays `draft → approved → completed` as today.

**Feature-less plans.** No exception. Refactors and infra plans are
arguably the most prone to "I think it's equivalent" overconfidence;
the Evaluator confirms the verifier was actually run and reported no
regression, not just declared green.

## Consequences

`docs/processes/harness.md` Phase 6 grows one step — Evaluator
invocation before the file move. `docs/PLANS.md` gains one required
section (`## Evaluator transcript`) and one subsection explaining the
contract. `docs/exec-plans/_template.md` ships the section as a stub.
`AGENTS.md` Phase gates lists the Evaluator gate alongside the existing
plan-coverage sensor gate. `docs/processes/dev-setup.md` adds an
Evaluator convention section the user must fill.

The pre-commit plan-coverage sensor is unchanged in v1. It already
trusts the `active/` → `completed/` boundary by reading `status:
completed` in `completed/`; the Evaluator gate sits earlier in that
boundary's workflow. A hardened sensor that also greps the transcript
for a `pass` verdict on the latest block is a v2 / stack-specific
tightening, not a v1 requirement.

A worker that moves a plan to `completed/` without a pass verdict is
violating the convention. v1 init-docs ships documentation, not
mechanical enforcement; the steering loop is the catch.
