---
status: draft
date: YYYY-MM-DD
id: <jira-id-or-initiative-code>
slug: <short-slug>
analysis: <link to the analysis doc that produced this plan>
adrs: []
covers: []  # path prefixes this plan authorises changes to; required when status: approved
features: []  # feat-NNN IDs from docs/FEATURES.md this plan delivers; non-optional (non-empty OR pair with feature-less-reason)
feature-less-reason:  # one line; required iff features is empty (e.g. "pure refactor; no user-observable change")
---

# <Short, action-oriented title>

This ExecPlan is a living document. The sections `Progress`,
`Surprises & Discoveries`, `Decision Log`, and
`Outcomes & Retrospective` must be kept current as work proceeds. This
plan must be maintained in accordance with [`../PLANS.md`](../PLANS.md).

## Purpose / Big Picture

Explain in a few sentences what someone gains after this change and how
they can see it working. State the user-visible behaviour you will enable.
Avoid internal jargon; write as if the reader is new to this repo.

## Progress

The only section where a checklist is mandatory. Use timestamps so rates
of progress are visible. At every stopping point, update this list; if a
task is partially done, split it into done / remaining.
On session exit, this section must reflect reality.

- [ ] (YYYY-MM-DD HH:MMZ) <granular step>

## Surprises & Discoveries

Unexpected behaviours, bugs, optimisations, or insights found during
implementation. Include concise evidence — test output, logs, diffs.

- Observation: …
  Evidence:

      <paste snippet here, indented>

## Decision Log

Plan-scoped decisions with rationale and date. Architectural decisions
go to `docs/decisions/` as ADRs, not here.

- Decision: …
  Rationale: …
  Date / Author: YYYY-MM-DD / <name>

## Outcomes & Retrospective

Written at major milestones and at completion. What was achieved, what
remains, lessons learned. Compare the result against Purpose. Capture any
lesson that should feed the harness steering loop.

## Context and Orientation

Describe the current state relevant to this task as if the reader knows
nothing about this repo. Name key files and modules by full
repository-relative path. Define any non-obvious term you use. Do not
point to prior plans; if prior work is relevant, incorporate the needed
context here.

## Plan of Work

Prose description of the sequence of edits and additions. For each edit,
name the file and location (function, module) and what to insert or
change. Keep it concrete and minimal. Prefer sentences over bullets.

## Concrete Steps

Exact commands to run and where to run them. When a command produces
output, show a short expected transcript so the reader can compare.
Update this section as work proceeds. Example:

    cd <repo-root>
    <build or check command>

    → expected output

## Validation and Acceptance

Behavioural, not structural. Name the acceptance criteria as things a
human can observe. For tests, name the test command and state the test
that fails before the change and passes after. Example:

    <test command>

    before change: FAIL  <test name>
    after change:  PASS  <test name>

## Idempotence and Recovery

Whether the steps are safe to repeat. For risky or destructive operations
(migrations, infra changes), include explicit rollback. Keep the
environment clean after completion.

## Artifacts and Notes

Important transcripts, diffs, or snippets as indented examples. Keep
them concise and focused on what proves success.

## Evaluator transcript

Written by the Evaluator only; the worker does not edit this section.
The Evaluator is invoked at the end of Phase 6 before the plan moves
to `completed/` — see [`../PLANS.md`](../PLANS.md) → "The
`Evaluator transcript` section" for the contract and block shape.

_No runs yet._

## Interfaces and Dependencies

Libraries, modules, and services to use and why. Types, interfaces, and
function signatures that must exist at the end of this milestone. Prefer
stable, repository-relative paths. Example:

In `<package-path>`, this plan must produce:

    <signature or type declaration>
