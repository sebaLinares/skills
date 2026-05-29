---
id: harness-design
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-05-29
update_trigger: on-supersession
---

# ADR harness-design — A lightweight harness for AI agent usage

## Status

Accepted.

## Context

{{PROJECT_CONTEXT — one paragraph: what this repo/tool does, and how an AI
agent is used on it today.}}

This is a small tool. The goal is the *architecture benefits* of a harness —
plan-driven changes, recorded decisions, a guided workflow — without the
ceremony or vendor coupling a larger team needs. Three failure modes a harness
prevents:

1. **Drift.** Plans and decisions live in chats and ephemeral sessions;
   nothing compounds across sessions.
2. **Context.** The agent starts each session cold, not knowing what exists,
   what's in flight, or what's already decided.
3. **Scope creep.** Without a stated plan, changes sprawl beyond the task.

We adopt the mental model from Martin Fowler (*Harness Engineering for Coding
Agent Users*) and the OpenAI Codex team (*Harness Engineering*):

> Agent = Model + Harness.

The harness — the part we build around the model — raises the chance the agent
gets a task right the first time and gives a feedback loop that self-corrects
before changes reach human eyes.

## Decision

### Mental model

Every control is either a **guide** (feedforward — steers before acting) or a
**sensor** (feedback — catches after acting):

|  | Computational (deterministic) | Inferential (LLM/human-judged) |
|---|---|---|
| **Guides** | linters, formatters, LSP | `AGENTS.md`, `docs/` hierarchy, ADRs, plan template |
| **Sensors** | tests, pre-commit `covers:` check | code review, a manual second-pass review |

Plans are artifacts produced by guides, not a third control type. They live in
`docs/exec-plans/`.

### Vendor neutrality

The harness depends on no specific agent vendor. `AGENTS.md` is the cross-agent
entry point (`CLAUDE.md` is a symlink to it). There are no subagents, no
agent-specific hooks, and no companion review script. An independent review
(fresh agent, separate session, human, or an external CLI like Codex) is
encouraged but invoked manually, not wired as a mechanical gate.

### Operating principle

**If it is not in the repo, it does not exist.** Anything the agent must reason
over must live as versioned markdown, code, or schema inside this repo.

### Phase gates

Work moves through **Brief → Decide → Plan → Execute**. No code without an
approved ExecPlan; no edits outside the active plan's `covers:`; not done until
`verify:` is green. Encoded in `AGENTS.md`, enforced by the plan-coverage check
at pre-commit plus convention.

### Plan format

Specified in [`../PLANS.md`](../PLANS.md): one file per initiative, living
document, with `covers:` and `verify:` frontmatter and the sections Goal, Out
of scope, Plan of Work, Verify, Decision Log.

### What ships

{{V1_CONTENTS — adjust for this project. Typical:}}

1. `AGENTS.md` (+ `CLAUDE.md` symlink) — operating principle, hard
   constraints, phase gates, session bootstrap.
2. `ARCHITECTURE.md` — the repo's code map.
3. [`docs/PLANS.md`](../PLANS.md) — the ExecPlan contract.
4. `docs/exec-plans/active/` with a plan template.
5. `docs/decisions/` — ADRs (this one + adr-slug-canonical).
6. `docs/processes/harness.md` — operating manual; `dev-setup.md` — stack
   commands and the plan-coverage check wiring.
7. `scripts/harness/check_plan_coverage.py` — the one mechanical sensor.

### Steering loop

The harness is an ongoing practice. For every agent failure, ask: *guide
missing, or sensor missing?* Extend one. "Just prompt harder" is not an answer.

## Consequences

**Positive.**
- A reviewable artifact (the ExecPlan) sits between "request" and "shipped".
- Decisions and plans are versioned and co-located — drift drops.
- The `covers:` check keeps the agent inside the approved scope.
- Vendor-neutral: works under Claude, Codex, or any agent that reads
  `AGENTS.md`; nothing breaks when tooling changes.

**Negative.**
- Higher cost per task in the short term — a plan precedes code.
- Phase gates beyond `covers:` are enforced socially; violations are possible.
- The harness itself needs steering-loop maintenance or it decays.

**Open.**
- Behavioural correctness remains a human-review + tests problem.
- A heavier, mechanically-enforced review gate is deliberately deferred — add
  it (or `init-docs`) if the tool grows past the small-tool lane.
