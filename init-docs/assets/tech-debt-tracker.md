---
owner: {{REPO_NAME}}
status: living
last_reviewed: 2026-05-26
update_trigger: on-debt-added-or-resolved
---

# Tech debt tracker

Running ledger of known hazards, work-in-progress shortcuts, and
deferred improvements. Maintained per the harness steering loop
(see [`processes/harness.md`](processes/harness.md)).

## How this works

Each row is one item. New items go at the top of the relevant section.

- **Severity.** `High` (active hazard or correctness risk), `Medium`
  (hurts velocity or clarity), `Low` (cosmetic or speculative).
- **Status.** `Open`, `In progress`, `Resolved`, `Dropped`.
- **Description.** What the debt is, in one sentence.
- **Resolution.** How it was paid, when closed, with a commit or
  plan/ADR reference where useful. Empty while `Open`.

When this file exceeds ~50 rows, move the oldest resolved items to a
`tech-debt-archive.md` next to it.

## Open

| Date identified | Severity | Description |
|---|---|---|

## Resolved

| Date identified | Severity | Description | Resolution |
|---|---|---|---|
