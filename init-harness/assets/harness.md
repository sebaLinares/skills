---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-29
update_trigger: on-harness-change
---

# Harness — Operating Manual

The day-to-day manual for how work gets done in this repo with a coding agent.
The *why* lives in [ADR harness-design](../decisions/harness-design.md); this
doc tells you *how*. It is vendor-neutral: no part depends on a specific
agent's subagents, hooks, or companion tooling.

Read this the first time you pick up a task here. Re-read the phase gates when
in doubt.

---

## Operating principle

**If it is not in the repo, it does not exist.**

Anything the agent must reason over must live as versioned markdown, code, or
schema inside this repo. When a piece of context is load-bearing, capture it
here first. When you finish a session, ask "did I leave anything only in the
chat?" — if yes, move it into the repo or mark it non-authoritative.

---

## Session bootstrap

Every session starts the same way:

1. Read `AGENTS.md` (`CLAUDE.md` is a symlink to it).
2. Read `docs/README.md` — the catalog.
3. Scan `docs/exec-plans/active/` — what is in flight. If a plan is present,
   hold its `covers:` prefixes in working context.
4. Scan `docs/decisions/` — what is already decided.
5. Read `ARCHITECTURE.md` before touching code.

Do not produce output before the bootstrap is done. If the user's first
message is urgent, do the bootstrap silently, then proceed.

---

## The workflow

A task moves through four phases. Each produces an artifact; phases do not
merge.

| # | Phase | Input | Artifact | Lives in |
|---|---|---|---|---|
| 1 | Brief | the user's request | Goal section of the plan (or a quick note) | — |
| 2 | Decide | a hard-to-reverse choice | ADR (only when warranted) | `docs/decisions/<slug>.md` |
| 3 | Plan | brief + decisions | ExecPlan | `docs/exec-plans/active/<id>_<slug>.md` |
| 4 | Execute | approved ExecPlan | code, tests, doc updates | the codebase |

### Phase 1 — Brief

Bring the request into the repo. The brief becomes the **Goal** of the
ExecPlan — restate the problem in your own words and name the observable
outcome. There is no separate brief artifact.

Gate: you can re-state the problem in your own words.

### Phase 2 — Decide

Not every task needs an ADR. Write one only when **all three** hold:

1. **Hard to reverse** — changing your mind later is costly.
2. **Surprising without context** — a future reader will ask "why this way?"
3. **A real trade-off** — there were genuine alternatives.

If any is missing, keep the decision inline in the plan's Decision Log. ADR
identity and format: [ADR adr-slug-canonical](../decisions/adr-slug-canonical.md).

Gate: every decision the plan needs is recorded — ADR or inline — with
reasoning, not just outcome.

### Phase 3 — Plan

Write an ExecPlan following [`../PLANS.md`](../PLANS.md) — the contract. Start
from [`../exec-plans/_template.md`](../exec-plans/_template.md). One file per
initiative, in `docs/exec-plans/active/`. The two load-bearing frontmatter
keys are `covers:` (the path prefixes this plan may touch — the plan-coverage
check reads it) and `verify:` (the command that proves "done").

**Only one plan in `active/` at a time** (AGENTS.md § Hard constraints).

Gate: the plan satisfies `PLANS.md`, `covers:` and `verify:` are set, and the
user has approved it. No code before this.

> An independent review of the plan (a fresh agent, a separate session, a
> human, or an external CLI like Codex) is *encouraged* but not a mechanical
> gate in this harness. Invoke it manually when the change warrants a second
> pair of eyes.

### Phase 4 — Execute

Execute the plan step by step:

- Update the Progress log after each step.
- If a step reveals information that changes the plan, **stop**, update the
  plan, get re-approval. Do not improvise.
- Stay inside `covers:`. The plan-coverage check at pre-commit
  (`docs/processes/dev-setup.md` § Plan-coverage check) is the last line of
  defence; in-execution self-check is the first.
- Run `verify:` until green.

On green: move the plan file out of `docs/exec-plans/active/` to
`docs/exec-plans/` and set `status: completed`, then commit.

Gate: all steps done, `verify:` green, plan moved out of `active/`.

---

## Phase gates — quick reference

| To enter | Required |
|---|---|
| Decide | The brief is understood and restated |
| Plan | Required decisions are recorded |
| Execute | The plan is approved and has `covers:` + `verify:` |
| Done | All steps done, `verify:` green, plan moved out of `active/` |

**Do not skip gates under time pressure.** If a gate genuinely does not apply
(e.g. a trivial fix with no design impact), say so explicitly in the plan's
Decision Log.

---

## Session exit

When the user signals "we're done" / "close out" / "ttyl", before responding:

1. **Build/verify** — if code was touched, run the plan's `verify:` (or the
   build command in `dev-setup.md`). A regression blocks; report it.
2. **Plan state** — the active plan's Progress reflects reality. Split any
   partially-done step into done / remaining.
3. **Doc coherence** — every new/edited doc is indexed in `docs/README.md`.
4. **Chat-sweep** — move any load-bearing knowledge still living only in the
   chat into the repo: rejected options → Decision Log; surprises or follow-up
   work → `docs/tech-debt-tracker.md`; a cross-plan principle → a new ADR.

---

## Steering loop

The harness is maintained, not built once. Whenever the agent gets something
wrong — bad plan, wrong code, skipped phase, reinvented an existing helper —
ask one question: **guide missing, or sensor missing?**

- **Missing guide** — the agent didn't know the right thing to do. Fix:
  extend `AGENTS.md`, an ADR, `ARCHITECTURE.md`, or the plan template.
- **Missing sensor** — the agent did the wrong thing and nothing caught it.
  Fix: add a test, a lint rule, or a pre-commit check.

**Never answer "just prompt harder."** A repeat failure is a harness bug.
Every steering pass lands either a guide update or a sensor addition.

---

## What the harness contains

See [ADR harness-design](../decisions/harness-design.md) for the inventory and
the guides-vs-sensors mental model. When the inventory changes, update the ADR.

ADR identity and format: [ADR adr-slug-canonical](../decisions/adr-slug-canonical.md).
