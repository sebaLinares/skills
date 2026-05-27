---
id: harness-design
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-05-28
update_trigger: on-supersession
---

# ADR harness-design — Harness Engineering for AI Agent Usage

## Status
Accepted

## Context

{{PROJECT_CONTEXT — one paragraph: team size, what this repo does, how AI is
being used today, and what problem that creates.}}

Three failure modes are typical when a team uses AI without an explicit
harness:

1. **Adoption.** AI is used as a model, not as an agent. Humans pre-digest
   every task into a fully specified plan; the agent just executes.
   Investigate / analyse / plan capability is not being exercised.
2. **Drift.** Plans, findings, and architectural decisions live in chats,
   meetings, and ephemeral agent sessions. Nothing compounds across sessions.
3. **Context.** Agents don't reliably know what's in the repo, what's in
   flight, or what has already been decided. Each session starts cold.

We adopt the mental model from Martin Fowler, *Harness Engineering for Coding
Agent Users*, and the OpenAI Codex team, *Harness Engineering: leveraging
Codex in an agent-first world*:

> Agent = Model + Harness.

The outer harness — the part we build around the model — exists to (a) raise
the probability the agent gets a task right on the first attempt, and
(b) provide a feedback loop that self-corrects before changes reach human
eyes.

## Decision

### Mental model

Every control in the harness is classified on Fowler's 2×2:

|  | Computational (deterministic, fast) | Inferential (LLM-judged, slower) |
|---|---|---|
| **Guides** (feedforward) | LSP, linters, formatters, codemods | `AGENTS.md` (as map; `CLAUDE.md` symlink), skills, `docs/` hierarchy, `docs/references/`, golden principles |
| **Sensors** (feedback) | tests, linters as check, coverage, pre-commit hooks, custom lints with remediation messages, structural tests | `/review`, `/security-review`, doc-gardening agent, plan-alignment judge |

**Plans are artifacts produced by guides, not a third control type.** They
live in `docs/exec-plans/`.

### Regulation categories

- **Maintainability harness** — tooling to keep the code readable and
  convention-conforming. Usually the most mature; start here.
- **Architecture fitness harness** — structural tests that enforce module /
  boundary invariants specific to this codebase.
- **Behaviour harness** — functional correctness. The field has no reliable
  automated solution yet; depend on human review and tests in v1.

### Operating principle

**If it is not in the repo, it does not exist.** Knowledge in Slack,
meetings, Jira comments, Confluence, or human memory is invisible to the
agent. Anything the agent must reason over must live as versioned markdown,
code, or schema inside this repo.

### Phase gates

No code is written without an exec-plan. No exec-plan is written without an
analysis doc. No analysis is produced without first reading `docs/README.md`
and the active-plans index. These gates are encoded in `AGENTS.md` and
enforced by convention in v1 (computational enforcement is deferred).

### Plan format

Specified in [`../PLANS.md`](../PLANS.md). Single file per initiative, living
document, with required sections: Purpose, Progress, Surprises & Discoveries,
Decision Log, Outcomes & Retrospective, Context and Orientation, Plan of
Work, Concrete Steps, Validation and Acceptance, Idempotence and Recovery,
Artifacts and Notes, Interfaces and Dependencies. Plan-scoped decisions stay
inline in the Decision Log; architectural decisions are promoted to ADRs in
`docs/decisions/`.

### Agent entry point

`AGENTS.md` at the repo root is the cross-agent entry point (loaded by any
agent that reads `AGENTS.md`). `CLAUDE.md` is a symlink to `AGENTS.md` so
Claude Code loads the same file.

### What ships in v1

{{V1_CONTENTS — project-specific list. Typical entries:}}

1. `docs/exec-plans/active/` and `docs/exec-plans/completed/` with a plan template.
2. Analysis template in `docs/analysis/`.
3. `docs/references/` for external specs the code must satisfy.
4. `docs/processes/harness.md` — operating manual.
5. `AGENTS.md` (with `CLAUDE.md` symlink) — operating principle, phase gates, session bootstrap.
6. {{language/framework-specific pre-commit hook: lint + static analysis + tests on changed files}}.
7. [`docs/PLANS.md`](../PLANS.md) — the ExecPlan specification. Load-bearing contract that every plan must satisfy.
8. [`docs/FEATURES.md`](../FEATURES.md) — the feature ledger; project-wide scope surface paired with verification and state. ExecPlans declare which Features they deliver via the `features:` frontmatter field.

### What is deferred

{{project-specific deferred list. Typical entries:}}

- PR-per-plan workflow (deferred until CI pipeline is fast enough to make one PR per plan practical).
- `/investigate` and `/plan` skills.
- Doc-gardening agent.
- `QUALITY_SCORE.md` and per-domain quality grading.
- Custom lint messages with embedded remediation instructions ("positive prompt injection").
- Plan-alignment judge (does the PR match the exec-plan?).
- Module-boundary structural tests.

### Steering loop

The harness is an ongoing practice, not a one-time build. Cadence: weekly,
~30 minutes. For every agent failure observed that week, ask:
*guide missing, or sensor missing?* Extend one. "Just prompt harder" is not
an answer.

## Consequences

**Positive.**
- A reviewable artifact exists between "brief received" and "code shipped": the
  exec-plan.
- Drift drops because analyses, decisions, and plans are versioned and
  co-located.
- Maintainability guardrails are deterministic and fast (pre-commit),
  catching a large class of issues before human review.
- Human review time shifts from code to plan — the higher-leverage stage.
- Progressive disclosure reduces prompt noise: the agent loads the map
  (`CLAUDE.md`, `docs/README.md`) and navigates from there, not one giant
  context dump.

**Negative.**
- Higher cost per task in the short term — the developer must produce an
  analysis before writing code.
- The harness itself requires ongoing maintenance via the steering loop.
  Without it, guides and sensors decay into a graveyard.
- Templates and phase-gate conventions are enforced socially in v1, not
  mechanically. Violations are possible.

**Open.**
- Behaviour harness remains unsolved. Functional correctness depends on
  human QA and tests that may themselves be agent-generated.
- If phase-gate violations happen repeatedly, v2 will need computational
  enforcement (hook that rejects edits when no active plan exists for the
  current topic).
- Harness coverage is not measured. There is no analog to code coverage for
  guides and sensors yet.
