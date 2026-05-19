# PLANS.md — ExecPlan specification

This file is the contract for ExecPlans in this repo.

When **writing** an ExecPlan, follow this document **to the letter**. When
**implementing** an ExecPlan, treat it as the single source of truth — do
not rely on prior conversation, chat history, or external docs that are
not explicitly referenced from within the plan.

An ExecPlan is a design document that a coding agent can follow to deliver
working, observable behaviour. Treat the reader as a complete beginner to
this repository: they have only the current working tree and this one
ExecPlan file. There is no memory of prior plans and no external context.

## How ExecPlans fit into the harness

ExecPlans are phase-5 artifacts in the harness workflow
([`processes/harness.md`](processes/harness.md)). They are written only
after an analysis doc exists in `docs/analysis/` and the lead has approved
it. No code is written before the ExecPlan is approved.

Active plans live in `docs/exec-plans/active/`. Completed plans move to
`docs/exec-plans/completed/` when all steps are done. Architectural decisions discovered
during plan execution are promoted to ADRs in `docs/decisions/`;
plan-scoped decisions stay inline in the plan's Decision Log.

## Frontmatter

Every ExecPlan begins with a YAML frontmatter block. Required fields:

- `status` — `draft`, `approved`, or `completed`.
- `date` — `YYYY-MM-DD` the plan was created.
- `id` — ticket ID or initiative code.
- `slug` — short slug used in the filename.
- `analysis` — repository-relative path to the analysis doc that produced this plan.
- `adrs` — list of repository-relative paths to ADRs cited by this plan (may be empty).
- `covers` — list of path prefixes this plan authorises changes to. **Required when `status: approved`.** See below.
- `features` — list of `feat-NNN` IDs from [`FEATURES.md`](FEATURES.md) that this plan delivers. **Non-optional:** either non-empty (every ID must resolve to a row in `FEATURES.md`) or empty paired with `feature-less-reason`. See below.
- `feature-less-reason` — one-line string declaring why this plan ships no user-observable behavior. **Required iff `features: []`.** Refactors, infra, dev-experience, and docs-only plans use this escape.

### The `covers:` field

`covers:` is a list of repository-relative **path prefixes**. A source
file is considered "covered" by this plan if any entry in `covers:` is
a prefix of the file's path. Prefix match is literal; no globbing.
Trailing `/` covers a directory and everything inside it:

    covers:
      - internal/modules/payments/
      - cmd/server/main.go

This field is consumed by the plan-coverage sensor in the pre-commit
hook. Only plans with `status: completed` in `docs/exec-plans/completed/`
grant coverage. Approved plans in `active/` do not — the sensor
enforces that execution is finished before the developer commits. For
urgent commits when no completed plan exists, set the
`HARNESS_BYPASS` environment variable:

    HARNESS_BYPASS="<reason>" git commit ...

See `docs/processes/dev-setup.md` for the full bypass policy.

### The `features:` field

`features:` is the link between an ExecPlan and the scope surface in
[`FEATURES.md`](FEATURES.md). The field is non-optional — every plan
must either list one or more `feat-NNN` IDs or declare itself
feature-less with `feature-less-reason`.

    features:
      - feat-007
      - feat-012

Or, for a plan that ships no user-observable behavior:

    features: []
    feature-less-reason: pure refactor of HTTP client; no behavioral change

State-machine consequences:

- On approval (`status: approved`), every listed Feature transitions
  from `Not started` to `Active` in `FEATURES.md`. The plan-approval
  flow owns this write.
- On completion (the plan lands in `exec-plans/completed/` with
  `status: completed`), Feature state is handed off to the verifier
  loop. The plan **does not** write `Passing` itself — that is the
  worker/checker split. A plan can be `completed` while its Features
  sit in `Failing` until the verifier loop confirms.
- A `features:` entry that does not resolve to a row in `FEATURES.md`
  makes the plan invalid. The agent must add the Feature row in
  `FEATURES.md` before approval.

The `features:` field has no interaction with the plan-coverage sensor
— that sensor reads `covers:` paths only and is unaware of
`FEATURES.md`.

### The `Evaluator transcript` section

No plan moves from `docs/exec-plans/active/` to
`docs/exec-plans/completed/` without an independent **Evaluator** pass.
The Evaluator is a coding agent or tool that does **not** share state
with the plan's worker — a fresh subagent, separate session, external
CLI agent, or human reviewer. Independence is structural: same agent,
same session, same context does not qualify. See ADR 003 for the why.

**Invocation contract.** Universal shape `<evaluator-cmd> <plan-path>`.
The consuming repo declares the concrete command in
`docs/processes/dev-setup.md` § Evaluator convention. The Evaluator
writes its output directly into the plan's `## Evaluator transcript`
section. The worker never edits that section.

**Verdicts.** Two required, one optional:

- **Alignment** (required) — the diff implements what the plan's
  Plan-of-Work and Concrete Steps said it would.
- **Acceptance** (required) — the plan's Validation & Acceptance
  criteria were actually verified, with evidence.
- **Quality** (optional) — code-quality review. A failing Quality
  verdict is *not* a completion blocker by itself; it routes to
  `docs/tech-debt-tracker.md`.

**Closure rule.** Worker moves the plan to `completed/` only if the
latest transcript block has Alignment + Acceptance both `pass`. On
fail, the plan stays in `active/`; the worker logs the failure in the
Decision Log, addresses it, and re-invokes the Evaluator. Each retry
appends a new timestamped block.

**Block shape.** Each Evaluator invocation appends a block of this
form:

    **Run N — YYYY-MM-DD HH:MMZ — <evaluator-cmd>**

    - Alignment: pass | fail — <one-line note>
    - Acceptance: pass | fail — <one-line note>
    - Quality: pass | fail | not requested — <one-line note>

    References: <commands run, files checked>

Long failure details belong in the Decision Log (worker's response to
the fail) and Surprises & Discoveries (what was uncovered), not in
this section. This section is a gate, not a log.

**Feature-less plans get the same gate.** Refactors and infra plans
are arguably the most prone to "I think it's equivalent"
overconfidence; the Evaluator confirms the verifier was actually run
and reported no regression.

## Non-negotiable requirements

- **Every ExecPlan must be fully self-contained.** A novice with only this
  file and the working tree must be able to execute it to a working
  outcome. Do not point to Slack, Confluence, prior plans, or "the team's
  shared understanding." If knowledge is required, embed it in the plan
  in your own words.
- **Every ExecPlan is a living document.** Revise it as progress is made,
  as discoveries occur, and as design decisions are finalised. After
  every revision the plan must remain fully self-contained.
- **Every ExecPlan must produce demonstrably working behaviour**, not
  merely code changes that meet a definition. State the observable
  outcome and how to verify it.
- **Every ExecPlan must define every term of art in plain language** or
  not use it. If you introduce a phrase that is not ordinary English
  ("middleware", "adapter", "projection"), define it immediately and
  name the files or commands where it appears in this repo.

## Required sections

Every ExecPlan must contain the following sections, kept current as work
proceeds. The starting skeleton is in
[`exec-plans/_template.md`](exec-plans/_template.md).

- **Purpose / Big Picture** — what someone can do after this change that
  they couldn't do before, and how to see it working.
- **Progress** — checklist of granular steps with timestamps. The only
  section where a checklist is mandatory. At every stopping point, split
  partially completed tasks into done / remaining.
- **Surprises & Discoveries** — unexpected behaviours, bugs,
  optimisations, or insights found during implementation, with concise
  evidence (test output, logs, diffs).
- **Decision Log** — every plan-scoped decision, with rationale and date.
  Architectural decisions go to `docs/decisions/` as ADRs, not here.
- **Outcomes & Retrospective** — written at major milestones and at
  completion. What was achieved, what remains, lessons. Compare the
  result against the original Purpose.
- **Context and Orientation** — current state relevant to the task, as
  if the reader knows nothing. Name key files and modules by full
  repository-relative path. Do not refer to prior plans; if prior work
  is relevant, embed the needed context here.
- **Plan of Work** — prose sequence of edits and additions. For each
  edit, name the file and location (function, module) and what to
  insert or change. Concrete and minimal.
- **Concrete Steps** — exact commands to run and where to run them
  (working directory). When a command produces output, show a short
  expected transcript so the reader can compare. Update this section
  as work proceeds.
- **Validation and Acceptance** — behaviour, not structure. For tests,
  name the test command and describe the new test that fails before the
  change and passes after.
- **Idempotence and Recovery** — whether steps are safe to repeat. For
  risky or destructive steps, specify explicit rollback.
- **Artifacts and Notes** — important transcripts, diffs, or snippets
  as indented examples. Concise, focused on proof of success.
- **Evaluator transcript** — verdicts from the independent Evaluator
  pass that gates the `active/` → `completed/` transition. Written by
  the Evaluator only; the worker never edits this section. See "The
  `Evaluator transcript` section" below for the contract.
- **Interfaces and Dependencies** — libraries, modules, and services to
  use and why. Types, interfaces, and function signatures that must
  exist at the end of the milestone. Prefer stable, repository-relative
  paths such as `<package>.<Type>`.

## Style

**Prose first.** Write in plain sentences. Avoid checklists, tables, and
long enumerations unless brevity would obscure meaning. Checklists are
permitted only in the Progress section, where they are mandatory.
Narrative sections must remain prose-first.

**Over-explain user-visible effects. Under-specify incidental
implementation details.** The reader does not need to be told how to
create a directory; they do need to be told what they should see in the
terminal or in a response body.

**Anchor with observable outcomes.** Acceptance is behaviour a human can
verify, not internal attributes. "After starting the service,
`curl localhost:8080/healthz` returns HTTP 200 with body `OK`" is
acceptable. "Added a HealthCheck struct" is not.

**Do not outsource decisions to the reader.** When ambiguity exists,
resolve it in the plan and explain why you chose that path.

## Milestones

Milestones are narrative, not bureaucracy. Introduce each with a
paragraph that describes the scope, what will exist at the end of the
milestone that did not exist before, the commands to run, and the
acceptance you expect to observe. Read as a story: goal, work, result,
proof. Each milestone must be independently verifiable and incrementally
implement the overall goal of the plan.

## Prototyping

Prototyping milestones are encouraged when they de-risk a larger change —
spikes, toy implementations, or parallel paths that prove feasibility
before full commitment. Label them clearly as prototyping, describe how
to run and observe results, and state the criteria for promoting the
prototype to production code or for discarding it. Prefer additive
changes followed by subtractions that keep tests passing.

## Living-document discipline

If you change course mid-implementation, document why in the Decision
Log and reflect the implications in Progress. Plans are guides for the
next contributor as much as checklists for the current author. Never
abbreviate a milestone merely for brevity; do not leave out details
that could be crucial to a future implementation.

At completion, write an Outcomes & Retrospective entry comparing the
result against Purpose, noting what remains (if anything), and capturing
lessons that should feed the harness steering loop
([`processes/harness.md`](processes/harness.md)).

## Formatting

The file at `docs/exec-plans/active/<name>.md` contains only the
ExecPlan. Do not wrap the whole plan in a triple-backtick fence; fence
only the internal code blocks, transcripts, or diffs. Use `#`, `##`,
`###` headings with two newlines after each. Use ordered and unordered
lists with correct syntax. Indent code blocks inside the plan with four
spaces if a fenced block would be ambiguous.
