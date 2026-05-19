# Feature ledger

Repo-wide ledger of every user-observable capability this product is
supposed to deliver, paired with how each is verified and what state it
is in today. The scope surface that briefs, plans, and the verifier
loop all converge on.

Read this before the catalog when entering the repo: it tells you what
the product does. See [`processes/harness.md`](processes/harness.md)
for how Features move through phases, and [`PLANS.md`](PLANS.md) for
the `features:` frontmatter ExecPlans must declare.

## How this works

Each row is one Feature.

- **ID.** `feat-NNN`, sequential, never reused. Next available integer
  when adding a row.
- **Behavior.** One sentence, user-observable. Not implementation. A
  Feature describes what the product does, not how.
- **Verify.** Either `verify: <tag>` (the project's test runner is
  invoked with this tag filter — see
  [`processes/dev-setup.md`](processes/dev-setup.md) for the exact
  command form) or `verify-cmd: <shell>` (escape hatch for Features
  the tagged-test convention does not cover, e.g. health endpoints).
  Exactly one is required; presence is non-negotiable even for
  `not_started`.
- **State.** The section heading under which the row lives — one of
  `Not started`, `Active`, `Blocked`, `Failing`, `Passing`. Writers
  are partitioned (worker/checker split):
    - **Humans** set `Not started` (on row creation) and `Blocked`
      (with a one-line reason in Notes).
    - **Plan-approval flow** moves a row from `Not started` to
      `Active` when an ExecPlan referencing the Feature's ID is
      approved (`status: approved` in `exec-plans/active/`).
    - **The verifier loop alone** sets `Passing` and `Failing`. The
      agent executing a plan never writes `Passing` itself.
- **Source.** Where the Feature came from: `brief`, `prd:<path>`,
  `analysis:<path>`, or `inferred`. Required. Defuses free-form bloat
  without imposing a phase gate on Feature creation.
- **Notes.** Free text. Use for `Blocked` reasons, regression dates,
  cross-references to ADRs or plans. Keep short.

A Feature row is the *cheapest* harness artifact — anyone can add one
without analysis or ADR. The act of adding it forces scope to be
written down. That is the leverage.

Transitions worth noting:

- `Not started → Active` is set by plan approval, not by hand.
- `Active → Passing` happens only after the plan lands in
  `exec-plans/completed/` *and* the verifier loop confirms.
- `Passing → Failing` is a regression. Only the verifier loop writes
  this; surface every entry in `## Failing` to the next steering loop.
- There is no transition back to `Not started`.

## Verify convention

`verify:` references the project's tag-filter convention for its test
runner. The exact shell invocation is recorded in
[`processes/dev-setup.md`](processes/dev-setup.md) under "Feature
verification convention". Until that section is filled in, `verify:`
tags are forward declarations only; they will not actually run.

`verify-cmd:` is a literal shell string. Use only when no test exists
yet (e.g. early scaffolding) or when the Feature is verified by
something other than a test (e.g. a health endpoint).

## Not started

| ID | Behavior | Verify | Source | Notes |
|---|---|---|---|---|

## Active

| ID | Behavior | Verify | Source | Notes |
|---|---|---|---|---|

## Blocked

| ID | Behavior | Verify | Source | Notes |
|---|---|---|---|---|

## Failing

| ID | Behavior | Verify | Source | Notes |
|---|---|---|---|---|

## Passing

| ID | Behavior | Verify | Source | Notes |
|---|---|---|---|---|
