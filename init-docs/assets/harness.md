---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-harness-change
---

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
2. Read [`../FEATURES.md`](../FEATURES.md) — the scope surface. Any task that
   names or implies a behavior must map to a Feature row (existing or new)
   before phase 1 produces an analysis doc.
3. Read `docs/README.md` — the catalog, including the tag vocabulary.
4. Scan `docs/exec-plans/active/` — what is currently in flight.
5. Scan `docs/decisions/` indexes — what is already decided.
6. Identify which tags match the current task and read only the docs whose tags
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

Before drafting the analysis Problem statement, identify which existing
Feature(s) the brief touches in [`../FEATURES.md`](../FEATURES.md); if none,
draft the new Feature row(s) there and reference them by `feat-NNN` ID from
the Problem statement. Adding a Feature row is the cheapest harness artifact
— no analysis or ADR required — and it forces scope to be written down before
investigation begins.

Phase-1 gate: developer can re-state the problem in their own words, and
every behavior implied by the brief maps to a Feature ID (existing or newly
added) — or the brief is explicitly feature-less (refactor, infra, dev-ex).

### Phase 2 — Investigation

The investigation produces an analysis doc. It is split between the
orchestrator (light, on Sonnet) and the `harness-analyst` subagent
(deep, on Opus). The orchestrator does not read source files itself
in this phase — it identifies which files are relevant and hands the
list to the subagent.

| Step | Owner | Action |
|---|---|---|
| Identify candidate paths | Orchestrator | `find` / `ls` / `grep -l` for files touched by the brief. **Do not Read them.** |
| Construct typed brief | Orchestrator | Assemble `feature_id`, `slug`, `source_paths` per `harness-analyst` config. |
| Synthesis | `harness-analyst` (Opus) | Reads `docs/analysis/_template.md` + `source_paths`. Writes the analysis doc directly. |
| Catalog row | Orchestrator | Edit `docs/README.md` with the new doc's one-line entry and tags. |

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

**Pre-write gate (hard).** The orchestrator must never Write or Edit a
file under `docs/analysis/`. That path belongs to `harness-analyst`.
Any orchestrator Write to that path is a policy violation. See
`AGENTS.md` § Phase gates for the concrete `Task(subagent_type="harness-analyst", ...)`
call shape and the typed brief contract.

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

Drafting an ADR with cross-plan or irreversible scope invokes the design
subagent per the model policy.

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

Plans declare which Features they cover via the `features:` frontmatter
field (see [`../PLANS.md`](../PLANS.md) → "The `features:` field"). The
field is non-optional — every plan either lists `feat-NNN` IDs from
[`../FEATURES.md`](../FEATURES.md) or declares itself feature-less with
`feature-less-reason:`. On approval, every listed Feature transitions
from `Not started` to `Active` in `FEATURES.md`.

Drafting an ExecPlan invokes the `harness-planner` subagent. The
pre-approval critic auto-fires when the subagent returns and writes
its verdict into the plan's `## Pre-approval critic transcript`
section. See [ADR 006](../decisions/006-pre-approval-critic-gate.md).

| Step | Owner | Action |
|---|---|---|
| Scope `covers:` | Orchestrator | List the path globs the plan will authorise changes to. |
| Construct typed brief | Orchestrator | Assemble `feature_id`, `slug`, `covers`, `analysis_path` per `harness-planner` config. |
| Synthesis | `harness-planner` (Opus) | Reads `docs/PLANS.md`, `docs/exec-plans/_template.md`, the analysis doc(s). Writes the ExecPlan directly. |
| Critic pass | Hook (synchronous) | `harness-planner-critic-hook.mjs` invokes `codex-companion.mjs adversarial-review` on SubagentStop (slash command is user-only), writes verdict into `## Pre-approval critic transcript`. |
| Catalog row | Orchestrator | Edit `docs/README.md` with the new plan's one-line entry and tags. |

**Pre-write gate (hard).** The orchestrator must never Write or Edit a
file under `docs/exec-plans/active/`. That path belongs to
`harness-planner`. Any orchestrator Write to that path is a policy
violation. See `AGENTS.md` § Phase gates for the concrete
`Task(subagent_type="harness-planner", ...)` call shape and the typed
brief contract.

**Pre-approval critic (hard).** Every ExecPlan passes through the
pre-approval critic before the lead approves it. The critic is
**auto-invoked** by `.claude/hooks/harness-planner-critic-hook.mjs`
on the `harness-planner` SubagentStop event. The hook runs codex
synchronously (the agent's turn pauses for the critic run, typically
30–90s) and writes the verdict directly into the plan's
`## Pre-approval critic transcript` section. When `codex-plugin-cc`
is unavailable or the critic crashes, the hook writes a
`BLOCKED: <reason>` placeholder into the same section instead of a
verdict. The lead does not approve a plan whose critic transcript is
empty or BLOCKED — install the plugin, run the critic out-of-band,
or paste a manual verdict before requesting approval. To bypass per
contributor, remove the SubagentStop entry from
`.claude/settings.local.json` (the named-section gate still
applies; manual population is required).

Phase-5 gate: the lead has read the plan, the
`## Pre-approval critic transcript` section contains a non-BLOCKED
verdict, and the plan satisfies PLANS.md. No code is written before
this.

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

Before moving the plan to `completed/`, invoke the project's
**Evaluator** with the plan path — see
[`dev-setup.md`](dev-setup.md) § Evaluator convention for the concrete
command (universal shape `<evaluator-cmd> <plan-path>`). The Evaluator
runs in a context that does not share state with this session and
writes a verdict block into the plan's `## Evaluator transcript`
section; this is the worker/checker split applied to plan completion
(see [ADR 003](../decisions/003-evaluator-gate.md)). The agent does
**not** edit that section.

Read the latest block. If Alignment and Acceptance are both `pass`,
proceed. If either is `fail`, the plan stays in `active/` — log the
failure in the Decision Log, address it, and re-invoke the Evaluator.
A failing Quality verdict is advisory only; route it to
`docs/tech-debt-tracker.md` and continue.

On a passing transcript, the **agent** moves the plan file from
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

The verifier loop owns Feature state transitions to `Passing` / `Failing`.
A plan completing is *not* the same as its Features passing — the plan can
land in `completed/` with `status: completed` while its Features sit in
`Failing` until the verifier loop runs and confirms. The agent must never
write `Passing` itself; that is the worker/checker split.

Phase-6 gate: all steps checked off, tests green, Evaluator transcript
present with latest Alignment + Acceptance both `pass`, plan in
`completed/` with `status: completed`.

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

## Model assignments

The harness uses a fleet-wide model policy, not project-local preference. The
canonical table is `docs/processes/model-policy.md`; this summary only names
the assignments most likely to affect phase gates.

| Step | Tier | Command |
|---|---|---|
| Default orchestration | Sonnet 4.6 high | Main session |
| Phase 2 analysis synthesis | Opus 4.7 xhigh | Claude Task tool |
| Phase 4 broad or irreversible ADRs | Opus 4.7 xhigh | Claude Task tool |
| Phase 5 ExecPlans (all plans) | Opus 4.7 xhigh | Claude Task tool |
| Pre-approval critic | GPT-5.5 high via codex plugin | Auto-fired by `.claude/hooks/harness-planner-critic-hook.mjs` → `codex-companion.mjs adversarial-review` |
| Mid-execution diff sanity | GPT-5.5 high via codex plugin | `Bash(node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" review)` |
| Rescue implementation | GPT-5.5 high via codex plugin | `Agent(subagent_type="codex:codex-rescue", …)` |
| Completion Evaluator | GPT-5.5 high via codex plugin | `Bash(node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" adversarial-review --base <merge-base>)` |

If the codex plugin is unavailable, follow the fallback chain in
`docs/processes/model-policy.md`; do not silently treat the main session as an
independent checker.

The codex-plugin-cc slash commands (`/codex:review`,
`/codex:adversarial-review`, `/codex:result`, etc.) set
`disable-model-invocation: true`. The orchestrator therefore invokes the
underlying `codex-companion.mjs` script via Bash for review and adversarial
review, and uses the `Agent` tool with `subagent_type="codex:codex-rescue"`
for rescue. See `docs/processes/model-policy.md` § Codex commands reference
for the full mapping.

---

## Session exit

Session exit is the clock-out half of session bootstrap. It cannot be
mechanically enforced because it depends on the user ending a conversation, but
the harness names the convention and makes it the easiest path: when a session
ends, the agent checks the repo can be picked up cleanly by the next agent.

Run session exit only on an explicit user signal, including: "session exit",
"close out", "we're done", "we are done", "that's it for today", "running
session exit", "run the exit checklist", "I'm closing the chat", "I'm out",
"ttyl", or "/quit".

The checklist has six dimensions:

1. **Build** — If code was touched, using `git status` plus working memory,
   run the build command documented in `docs/processes/dev-setup.md`.
   Auto-fix mechanical issues by re-running the documented command after
   straightforward cleanup. Red builds block with flag.
2. **Verifier** — Run the project's verifier, resolved from `verify-cmd:` or
   `verify:` via `docs/processes/dev-setup.md`. Compare against the
   `docs/FEATURES.md` state observed during session bootstrap. A
   `Passing` -> `Failing` regression blocks with flag; pre-existing reds are
   reported without blocking.
3. **Plan state** — Every active plan touched this session has Progress
   reflecting reality. If a step is partially done, split it into done and
   remaining items. Auto-fix by editing the plan. Ambiguous progress is
   surfaced.
4. **Doc coherence** — Every new or edited artifact is indexed in
   `docs/README.md` with tags, and no docs are orphaned. Auto-fix missing
   catalog entries. Ambiguous tag choices are surfaced.
5. **Startup viable** — If startup-affecting code was touched, confirm the
   startup commands described in `docs/processes/dev-setup.md` still bring the
   project up. Auto-fix stale command text when the correct command is known.
   Red startup blocks with flag.
6. **Chat-sweep** — Sweep the conversation for knowledge that exists only in
   chat and route it into existing artifacts using the questionnaire below.

Chat-sweep questionnaire:

| Question | Destination |
|---|---|
| Were any options rejected that future work should not reopen? | Decision Log in the active plan, or a new `docs/analysis/` doc if no plan exists |
| Were there surprises, insights, or discoveries? | Surprises & Discoveries in the active plan, or `docs/tech-debt-tracker.md` |
| Is there followup work outside the current plan? | `docs/tech-debt-tracker.md` |
| Did a cross-plan principle emerge? | ADR draft in `docs/decisions/_drafts/` |
| Is there an external person, deadline, or commitment to track? | `docs/tech-debt-tracker.md`, or plan Context if plan-scoped |

Block with this exact prompt when build, verifier regression, or startup cannot
be made green before exit:

    BLOCKED on <dim>. Continue anyway? [y/N]

Example transcript:

    Session exit
    - Build: passed (`npm test`)
    - Verifier: no regression; pre-existing `feat-004` remains Failing
    - Plan state: updated `docs/exec-plans/active/2026-05-19_ABC_widget.md`
    - Doc coherence: indexed 2 edited docs in `docs/README.md`
    - Startup viable: not applicable; no startup-affecting code touched
    - Chat-sweep:
      - Rejected options: recorded in plan Decision Log
      - Surprises: none
      - Followups: added TD-018
      - Cross-plan principles: none
      - External commitments: none

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

For failures involving planning, synthesis, review, or rescue, first ask:
*was the right model used per `model-policy.md`?* If no, the failure is model
drift — a policy violation — not a harness gap. Correct the assignment and then
continue steering on any residual guide or sensor gap.

**Never answer "just prompt harder."** If the same failure shows up a second
time, it is a harness bug.

**Record the change.** Every steering-loop session produces either a guide
update (commit) or a sensor addition (commit). If neither, the session didn't
land.

**Scan the `## Failing` section of [`../FEATURES.md`](../FEATURES.md).** Every
entry is either a steering-loop input (a regression where a sensor is missing
or a guide is wrong) or a tech-debt row (an acknowledged hazard). Empty
`## Failing` is the target state.

---

## What the harness contains today

See [ADR 001 — Harness Engineering for AI Agent Usage](../decisions/001-harness-design.md)
for the current inventory (guides, sensors, what's deferred) and the regulation
categories in scope.

When the inventory changes, update the ADR — either by amending the "what
ships in v1" list or by writing a superseding ADR.

### Harness validators

Two stdlib-Python scripts ship at `scripts/harness/` to mechanically
enforce the documentation contract:

- `check_harness_structure.py` — existence of canonical files, 4-key
  YAML frontmatter on the markdown subset, required cross-references,
  no forbidden ephemera under `docs/`, no absolute paths in scanned
  text. Fail-fast, suitable for pre-commit.
- `garbage_collect_docs.py` — broken-reference scan, stale-review
  flag, orphan-doc detection. Slower; suitable for nightly or weekly
  runs. Renders a markdown report.

Both honour `HARNESS_BYPASS="<reason>"`. The shared manifest lives at
`scripts/harness/_canonical_manifest.py` — every CHANGELOG entry that
touches the canonical set updates the manifest in the same entry. See
[ADR 007 — Harness validators](../decisions/007-harness-validators.md)
for the design and the explicit non-shipping of Makefile / pre-commit
/ CI wiring (stack-specific; the contract lives in `dev-setup.md`
§ Harness validators).

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
