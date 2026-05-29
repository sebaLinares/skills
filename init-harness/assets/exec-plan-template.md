---
status: active
id: <ticket-id-or-initiative-code>
slug: <short-slug>
covers: []  # repo-relative path prefixes this plan may touch; the coverage check reads this
verify: <shell command that proves this plan is done, e.g. go test ./... && go build ./...>
adrs: []  # repo-relative paths to ADRs this plan cites (may be empty)
---

# <Short, action-oriented title>

This ExecPlan is a living document, maintained per [`../PLANS.md`](../PLANS.md).
Keep `Plan of Work` and `Decision Log` current as work proceeds.

## Goal

What someone gains after this change and how they can see it working. State
the user-visible behaviour you will enable. Write as if the reader is new to
this repo. This is the brief, restated in your own words.

## Out of scope

What this plan deliberately will not touch. Keep it honest with `covers:`.

## Plan of Work

The ordered, concrete sequence of edits and additions. For each, name the file
and location (function, module) and what to insert or change. Minimal and
specific.

1. <step>

## Verify

How to confirm the change works. Name the `verify:` command and the behaviour
a human can observe. For tests, name the test that fails before and passes
after. Example:

    <verify command>

    before change: FAIL  <test name>
    after change:  PASS  <test name>

## Decision Log

Plan-scoped decisions with rationale and date. Architectural decisions go to
`docs/decisions/` as ADRs, not here.

- Decision: …
  Rationale: …
  Date: YYYY-MM-DD
