---
status: draft
date: YYYY-MM-DD
topic: <short-name>
related-plan: <repo-relative path or "none yet">
related-adrs: []
---

# Analysis — <topic>

> Produced in phase 2 of the harness workflow. See
> [docs/processes/harness.md](../processes/harness.md) for what each section
> requires and when this doc is considered done.

## 1. Problem statement

Re-state the brief in technical terms. This is where verbal / Jira-originated
context enters the repo. Be precise about what is being asked for and why.

## 2. Context

What exists today that is relevant. Link to files, functions, services, other
docs. Use repository-relative paths; do not preserve local absolute paths.
Do not paraphrase when you can link.

## 3. Findings

What the investigation surfaced — especially surprises or gaps between what
the brief implied and what the code actually shows.

## 4. Options

Approaches considered. Not the plan yet.

### Option A — <name>
- Pros:
- Cons:

### Option B — <name>
- Pros:
- Cons:

## 5. Recommendation

The option you think is right, and why. Brief.

## 6. Assumptions

<!-- Agent instruction: Do NOT list unknowns here. Three rules:
     1. Assumption-based: state the assumption, its evidence, and the
        consequence if wrong. Never ask the user — just proceed.
     2. Codebase-inferable: grep/read first; report findings in §3.
        Do not surface these as questions.
     3. Cross-team blockers: go to §7 → Cross-team unknowns.
        Frame as async action items, not gates on the plan. -->

| Assumption | Evidence basis | If wrong |
|---|---|---|
| <assumption> | <grep result / file:line / convention> | <consequence and fallback> |

## 7. Risks

Known unknowns, compliance concerns, data quality, performance unknowns.

| Risk | Likelihood | Severity | Mitigation |
|---|---|---|---|
| <risk> | low / med / high | low / med / high | <mitigation> |

### Cross-team unknowns

<!-- Agent instruction: Only put items here that genuinely require a
     person on another team to answer. Each is an async action item
     (owner + question + impact), NOT a gate on the plan. State
     explicitly that the plan proceeds regardless. -->

| Owner | Question | Plan impact if unresolved |
|---|---|---|
| <team / person> | <question> | <what changes or degrades> |
