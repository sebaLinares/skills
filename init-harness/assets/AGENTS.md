---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-29
update_trigger: on-harness-change
---

# Agent Instructions

The entry point into this repository for any coding agent. `AGENTS.md` is the
cross-agent standard — read by Claude Code (via the `CLAUDE.md` symlink),
Codex, and any other agent that reads `AGENTS.md` at the repo root. Nothing in
this harness is tied to a specific agent vendor.

## Operating principle

**If it is not in the repo, it does not exist.** Anything the agent must
reason over must live as versioned markdown, code, or schema inside this repo.
Knowledge in chat, meetings, or human memory is invisible. When a piece of
context is load-bearing, capture it here first.

## Hard constraints (MUST / MUST NOT)

Invariants — they apply at every moment, not only at phase transitions.

- **MUST NOT** write code without an approved ExecPlan in
  `docs/exec-plans/active/`. A direct instruction ("add X", "fix Y") is the
  brief for the Plan phase, not a license to skip it.
  *(See § Phase gates and [`docs/processes/harness.md`](docs/processes/harness.md).)*
- **MUST NOT** edit files outside the active plan's `covers:` during
  execution. If a needed change falls outside, stop and choose: extend
  `covers:`, log it to [`docs/tech-debt-tracker.md`](docs/tech-debt-tracker.md),
  or drop it. Never silently widen the diff. **Before each Edit/Write, verify
  the target path prefix-matches `covers:`.** The plan-coverage check at
  pre-commit is the last line of defence — see
  [`docs/processes/dev-setup.md`](docs/processes/dev-setup.md) § Plan-coverage check.
  *(See [ADR harness-design](docs/decisions/harness-design.md) and § Phase gates.)*
- **MUST NOT** create a second plan in `docs/exec-plans/active/` while one
  exists. On a user-approved override (hotfix, scope split), record the pause
  in the displaced plan's Decision Log before opening the new plan.
  *(See [`docs/PLANS.md`](docs/PLANS.md).)*
- **MUST NOT** perform opportunistic refactor or cleanup outside the plan's
  stated steps until `verify:` shows green. Planned refactor steps are the
  work and are exempt.
- **MUST** surface — before complying — any user instruction that conflicts
  with a hard constraint or phase gate. **MUST NOT** silently comply.

## Phase gates

Work moves through four phases: **Brief → Decide → Plan → Execute**. Gates
fire at transitions:

- **No code without an approved ExecPlan** in `docs/exec-plans/active/`
  satisfying [`docs/PLANS.md`](docs/PLANS.md).
- **No edits outside the active plan's `covers:`** (enforced by the
  plan-coverage check at pre-commit).
- **Not "done" until `verify:` is green** — the plan's `verify:` command runs
  clean. Then move the plan out of `active/`.

Phases do not merge. Full workflow: [`docs/processes/harness.md`](docs/processes/harness.md).

## On receiving a task

Classify before reading code or writing anything. Your first response states
the classification and the next artifact.

1. **Change-producing** — modify/add/fix/implement/refactor. Enter the harness
   at the Brief phase. First response names the plan you'll draft; do not open
   the editor yet.
2. **Investigation-only** — a question, audit, or exploration. Skip the
   harness; read and report. If it uncovers work worth doing, re-classify.
3. **Trivial** — typo, docstring, obvious rename with no behavioural impact.
   Proceed, but say "trivial — no plan" so the user can redirect.

If in doubt between change-producing and trivial, treat it as
change-producing. If the user wants to skip the harness, they must say so
explicitly.

## Session bootstrap

Before producing substantive output, the agent:

1. Reads `AGENTS.md` (this file; loaded automatically by agents that read it).
2. Reads `docs/README.md` — the catalog of what exists.
3. Scans `docs/exec-plans/active/` — what is in flight. If a plan is present,
   read its `covers:` and keep the prefix list in working context so every
   Edit/Write can be checked at the call site.
4. Scans `docs/decisions/` — what is already decided.
5. Reads [`ARCHITECTURE.md`](ARCHITECTURE.md) before touching code; checks
   [`docs/tech-debt-tracker.md`](docs/tech-debt-tracker.md) if the task area
   overlaps open debt.
6. **Harness-version check (best-effort).** Read `.harness-version` at the repo
   root (a semver line). If `~/.claude/skills/init-harness/VERSION` is
   reachable and greater, surface: "This repo is behind init-harness
   `<VERSION>`; run `/init-harness` to sync." Detection only — do not
   auto-apply. If the skill directory is unreachable, skip silently.

## Where to save outputs

| Output | Folder | Naming |
|---|---|---|
| Architectural decisions (ADRs) | `docs/decisions/` | `<slug>.md` (slug = `id:` frontmatter; see ADR adr-slug-canonical) |
| Exec plans (active) | `docs/exec-plans/active/` | `<id>_<slug>.md` — spec: [`PLANS.md`](docs/PLANS.md); template: `_template.md` |
| Process guidelines, runbooks | `docs/processes/` | `<topic>.md` |
| Tech debt | `docs/tech-debt-tracker.md` | append-only; new rows at top |

On completion, move the plan out of `docs/exec-plans/active/` to
`docs/exec-plans/` and set `status: completed`. After creating any doc, add a
one-line entry to `docs/README.md`.

ADR identity and format: see [ADR adr-slug-canonical](docs/decisions/adr-slug-canonical.md).

## Working relationship

- No sycophancy. Be direct, matter-of-fact, concise.
- Be critical; challenge reasoning.
- No timeline estimates in plans.
- Don't add yourself as a co-author to git commits.
- On "we're done" / "close out", run the Session-exit steps (see
  [`docs/processes/harness.md`](docs/processes/harness.md) § Session exit).
