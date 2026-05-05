# Harness — Operating Manual

This is the day-to-day manual for how work gets done in this repo with an AI
coding agent. The *why* behind it lives in [ADR 001](../decisions/001-harness-design.md);
this doc tells you *how* to actually do the work.

Read this the first time you pick up a task in this repo. Re-read the phase
gates table when in doubt.

---

## Operating principle

**If it is not in the repo, it does not exist.**

Anything the agent must reason over must live as versioned markdown, code, or
schema inside this repo. Knowledge in Slack, meetings, Jira comments,
Confluence, or human memory is invisible to the agent. When a piece of context
is load-bearing, the first action is to capture it here.

Corollary: when you finish a session, ask "did I leave anything only in the
chat?" If yes, either move it into the repo or mark it explicitly as
non-authoritative.

---

## Session bootstrap

Every Claude Code session in this repo starts the same way. The agent must:

1. Read `AGENTS.md` (loaded automatically; `CLAUDE.md` is a symlink to it).
2. Read `docs/README.md` — the catalog, including the tag vocabulary.
3. Scan `docs/exec-plans/active/` — what is currently in flight.
4. Scan `docs/decisions/` indexes — what is already decided.
5. Identify which tags match the current task and read only the docs whose tags
   match. Skip the rest.

Do not start producing output before the bootstrap is done. If the user's
first message is urgent and skips this, the agent should still do the bootstrap
before generating a plan or code — just silently, without narrating it.

---

## The workflow

A task moves through six phases. Each phase produces an artifact. Phases do
not merge: do not produce two phases' output in one pass.

| # | Phase | Input | Artifact | Lives in |
|---|---|---|---|---|
| 1 | Brief | Jira ticket + verbal/written explanation from lead | Captured as the "problem statement" section of the analysis doc | — |
| 2 | Investigation | Brief + relevant docs + code scan | Analysis doc | `docs/analysis/YYYY-MM-DD_<topic>.md` |
| 3 | Findings review | Analysis doc | Analysis doc (updated, open questions resolved or deferred) | same file |
| 4 | Decisions | Points of divergence from analysis | ADR(s), or entries in the plan's decision log | `docs/decisions/NNN-<title>.md` or inline |
| 5 | Plan | Analysis + ADRs + plan-scoped decisions | Exec-plan | `docs/exec-plans/active/YYYY-MM-DD_<id>_<slug>.md` |
| 6 | Execution | Approved exec-plan | Code, tests, doc updates | the codebase |

On completion (all steps checked off, tests green), the plan moves from `active/` to `completed/`.

### Phase 1 — Brief

The brief is whatever context the lead gives the developer: a Jira ticket (often
non-technical, written by product), a Slack message, or a verbal explanation.
This is the only phase whose input lives *outside* the repo.

The developer's first job is to bring the brief into the repo. That happens as
the opening section of the analysis doc in phase 2 — the *problem statement*.
There is no separate brief artifact.

Phase-1 gate: developer can re-state the problem in their own words.

### Phase 2 — Investigation

The developer (with their agent) investigates the repo: reads relevant docs by
tag, scans related code, checks active plans and ADRs for overlap, consults
external references in `docs/references/`, and produces an analysis doc.

The analysis doc contains:

1. **Problem statement** — the brief restated in technical terms.
2. **Context** — what exists in the repo today that's relevant. Link to files
   and functions; don't paraphrase.
3. **Findings** — what the investigation surfaced, especially surprises or gaps
   between the brief and reality.
4. **Options** — approaches considered, with pros and cons. Not a plan yet.
5. **Recommendation** — the option the developer thinks is right, with reasoning.
6. **Open questions** — anything the developer cannot resolve alone.
7. **Risks** — known unknowns, dependencies on other teams, compliance, etc.

Phase-2 gate: analysis doc exists at the path above, is indexed in `docs/README.md`,
and open questions are explicit. Do not proceed to plan without this.

### Phase 3 — Findings review

The lead reads the analysis. Two outcomes:

- **Aligned:** open questions answered, recommendation approved → proceed to
  phase 4 or 5.
- **Divergent:** the lead adds comments or amends the analysis. The developer
  updates. Loop until aligned.

The analysis doc is the shared artifact; do not conduct this review in Slack
without reflecting the result back into the doc.

Phase-3 gate: all open questions are marked resolved or explicitly deferred,
and the lead has approved the recommendation.

### Phase 4 — Decisions

Not every task needs an ADR. Use this rule:

- **Promote to ADR** when the decision has cross-plan scope, architectural
  implications, or will constrain future work (e.g., "all persistence goes
  through repository X," "we don't use ORMs").
- **Keep inline** when the decision is scoped to this plan only (e.g., "we'll
  paginate this endpoint by cursor because we expect <10k items per query").

Inline decisions go in the plan's *decision log* (see phase 5 template).

Phase-4 gate: every decision required by the plan is recorded somewhere — ADR
or inline — with the reasoning, not just the outcome.

### Phase 5 — Plan

The developer (with their agent) produces an ExecPlan following
[`../PLANS.md`](../PLANS.md). PLANS.md is the specification — every
non-negotiable requirement (self-containment, living-document discipline,
demonstrably working outcome, defining every term of art) applies. The
starting skeleton is [`../exec-plans/_template.md`](../exec-plans/_template.md).

Single file per initiative, under `docs/exec-plans/active/`. Plan-scoped
decisions stay in the plan's Decision Log; architectural decisions are
promoted to ADRs in `docs/decisions/`.

Phase-5 gate: the lead has read the plan and approved it, and the plan
satisfies PLANS.md. No code is written before this.

The pre-commit hook contains a plan-coverage sensor. The sensor reads
each completed plan's `covers:` frontmatter (see `docs/PLANS.md`) and
refuses to commit any source file whose path is not covered by a plan
in `docs/exec-plans/completed/` with `status: completed`. The sensor
is the *last* line of defence; analysis, plan, and full execution
should exist long before the commit is attempted.

For exceptional commits when the gate should not apply, the sensor
should support an explicit bypass environment variable
(e.g. `HARNESS_BYPASS="<reason>" git commit ...`). The reason is
logged; all other pre-commit checks still run. The implementation is
stack-specific — see `docs/processes/dev-setup.md` for setup.

### Phase 6 — Execution

The developer executes the plan step by step. Rules:

- Progress log is updated after each step completes.
- If a step reveals new information that would change the plan, **stop**,
  update the plan, get re-approval. Do not improvise.
- Any decision made during execution is recorded in the decision log with
  timestamp and reasoning.

On completion, the **agent** moves the plan file from
`docs/exec-plans/active/` to `docs/exec-plans/completed/` and sets
`status: completed` in the frontmatter. The agent then commits automatically — no prompt required. If the
`/commit` skill is available, invoke it; otherwise stage all changes,
write a Conventional Commit message, and run `git commit` directly.
The agent owns closing the plan and the commit; the developer owns
reviewing the result.

The pre-commit hook validates this: it will reject any commit that
touches source files unless a plan in `completed/` with
`status: completed` covers those paths. This is what makes the
move-then-commit order enforceable.

Phase-6 gate: all steps checked off, tests green, plan in `completed/`
with `status: completed`.

> **Note:** PR-per-plan is deferred to the backlog pending CI pipeline
> improvements. Plans are closed on step completion, not on merge.

---

## Phase gates — quick reference

| To enter | Required |
|---|---|
| Investigation | Developer understands the brief |
| Findings review | Analysis doc exists and is indexed |
| Decisions | Analysis is approved by the lead |
| Plan | All required decisions are recorded |
| Execution | Plan is approved by the lead |
| Completion | All steps done, plan moved to `completed/` |

**Do not skip gates under time pressure.** Skipping is the single fastest way to
burn the harness. If a gate genuinely does not apply (e.g., a trivial bug fix
with no architectural implication), say so explicitly in the analysis doc
("decisions phase skipped — no architectural impact").

---

## Where artifacts live

| Artifact | Path | Naming |
|---|---|---|
| Analysis | `docs/analysis/` | `YYYY-MM-DD_<topic>.md` |
| ADR | `docs/decisions/` | `NNN-<title>.md` (sequential) |
| Plan (active) | `docs/exec-plans/active/` | `YYYY-MM-DD_<id>_<slug>.md` |
| Plan (completed) | `docs/exec-plans/completed/` | same filename |
| Process / runbook | `docs/processes/` | `<topic>.md` |
| Architecture / diagrams | `docs/architecture/` | `<slug>.md` or `<slug>.drawio` |
| External references | `docs/references/` | `<name>-llms.txt` |
| AI-generated ticket drafts | `docs/tickets/` | `YYYY-MM-DD_<ID>_<slug>.md` |

After creating any doc, add a one-line entry to the relevant section of
`docs/README.md` with at least one domain tag and one type tag.

Templates for analysis and plan files live next to where they belong:
`docs/analysis/_template.md` and `docs/exec-plans/_template.md`. Copy and fill.

---

## Steering loop

The harness is not built once. It is maintained.

**Cadence:** weekly, 30 minutes, between lead and developer.

**Input:** everything the agent got wrong that week — bad plans, wrong code,
skipped phases, drifted from the plan, used the wrong abstraction, wrote a
helper that already exists, etc.

**For each failure, ask one question:** *guide missing, or sensor missing?*

- **Missing guide** — the agent didn't know to do the right thing. Fix:
  extend `CLAUDE.md`, add a skill, write a golden principle, add a reference
  doc, update the plan template.
- **Missing sensor** — the agent did the wrong thing and nothing caught it.
  Fix: add a lint rule, a pre-commit check, a test, a review-skill rule, or a
  custom linter message with remediation instructions.

**Never answer "just prompt harder."** If the same failure shows up a second
time, it is a harness bug.

**Record the change.** Every steering-loop session produces either a guide
update (commit) or a sensor addition (commit). If neither, the session didn't
land.

---

## What the harness contains today

See [ADR 001 — Harness Engineering for AI Agent Usage](../decisions/001-harness-design.md)
for the current inventory (guides, sensors, what's deferred) and the regulation
categories in scope.

When the inventory changes, update the ADR — either by amending the "what
ships in v1" list or by writing a superseding ADR.

---

## Appendix — ADR format

Every ADR in `docs/decisions/` follows this four-section template:

~~~
# NNN — Title

## Status
Accepted | Superseded by NNN

## Context
Why this decision needed to be made.

## Decision
What was decided.

## Consequences
What changes as a result.
~~~
