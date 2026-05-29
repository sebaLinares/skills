---
owner: {{REPO_NAME}}
status: living
last_reviewed: 2026-05-29
update_trigger: on-debt-added-or-resolved
---

# Tech debt tracker

Running ledger of known hazards, work-in-progress shortcuts, and deferred
improvements. Maintained per the harness steering loop (see
[`processes/harness.md`](processes/harness.md)).

## How this works

Each row is one item. New items go at the top of the relevant section.

- **Severity.** `High` (active hazard or correctness risk), `Medium` (hurts
  velocity or clarity), `Low` (cosmetic or speculative).
- **Status.** `Open`, `In progress`, `Resolved`, `Dropped`.
- **Description.** What the debt is, in one sentence.
- **Resolution.** How it was paid, with a commit/plan/ADR reference where
  useful. Empty while `Open`.

## Open

| Date identified | Severity | Description |
|---|---|---|

## Resolved

| Date identified | Severity | Description | Resolution |
|---|---|---|---|
