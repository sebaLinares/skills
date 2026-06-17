---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-harness-change
---

# Agent Instructions

The entry point into this repository for any coding agent. Loaded
automatically by Claude Code (via the `CLAUDE.md` symlink) and by any
other agent that reads `AGENTS.md` at the repo root.

## Operating principle

**If it is not in the repo, it does not exist.** Anything the agent must
reason over must live as versioned markdown, code, or schema inside this
repo. Knowledge in Slack, meetings, Jira, Confluence, or human memory is
invisible. When a piece of context is load-bearing, capture it here first.

## Hard constraints (MUST / MUST NOT)

These are invariants — they apply at every moment of every phase, not only
at transitions. Distinct from the phase gates below, which fire only at
phase transitions.

**Block-maintenance rule.** Each bullet MUST be loud-labelled
(**MUST** / **MUST NOT**) AND cite an ADR (`ADR <slug>`) or named section
(`§ …`). A bullet missing either is malformed — remove it or write the
ADR. A loud-labelled bullet without a citation is a soft suggestion in
hard-label clothing, which is worse than no rule at all (see
[ADR hard-constraints](docs/decisions/hard-constraints.md) § Consequences).

- **MUST NOT** create a second plan in `docs/exec-plans/active/` while one
  exists. Surface the WIP collision; on user-approved override (hotfix,
  blocked-on-external, scope split), record the pause in the displaced
  plan's Decision Log before opening the new plan.
  *(See [ADR hard-constraints](docs/decisions/hard-constraints.md).)*
- **MUST NOT** edit files outside the current plan's `covers:` during
  execution. If a needed change falls outside, stop and choose: extend
  `covers:` (re-approval required, per Phase 6), log to
  [`docs/tech-debt-tracker.md`](docs/tech-debt-tracker.md), or drop. Never
  silently widen the diff. **Before each Edit/Write tool call, verify the
  target path prefix-matches `covers:`.** The plan-coverage sensor at
  pre-commit is the last line of defence, not the first; in-execution
  self-check is the first. A PreToolUse hook MAY enforce this
  mechanically — see [`docs/processes/dev-setup.md`](docs/processes/dev-setup.md)
  § Pre-tool-use hook (covers: enforcement).
  *(See [ADR harness-design](docs/decisions/harness-design.md) and § Phase gates →
  plan-coverage sensor below.)*
- **MUST NOT** perform opportunistic refactor or cleanup outside the
  plan's stated steps until a manual run of `verify-cmd` (or `verify:`
  resolution) shows the plan's Features green. Planned refactor steps in
  Plan-of-Work or Concrete steps are exempt — those are the work.
  *(See [ADR hard-constraints](docs/decisions/hard-constraints.md).)*
- **MUST NOT** continue with load-bearing knowledge that exists only in
  chat. Capture it in the repo first.
  *(See § Operating principle above.)*
- **MUST** surface — before complying — any user instruction that
  conflicts with a hard constraint, phase gate, or documented rule.
  **MUST NOT** silently comply.
  *(See [ADR hard-constraints](docs/decisions/hard-constraints.md).)*

## Phase gates

- No code without an approved ExecPlan in `docs/exec-plans/active/`.
- No ExecPlan without an analysis doc in `docs/analysis/`.
- No analysis without completing the session bootstrap.
- ExecPlans must satisfy every non-negotiable requirement in
  [`docs/PLANS.md`](docs/PLANS.md). Deviations from the spec are
  themselves decisions and must be logged.
- No plan moves from `docs/exec-plans/active/` to `completed/` without
  an Evaluator transcript whose latest run shows Alignment + Acceptance
  both `pass`. The Evaluator is an independent agent or tool (fresh
  subagent, separate session, external CLI agent, human reviewer) — see
  [ADR evaluator-gate](docs/decisions/evaluator-gate.md) and
  [`docs/PLANS.md`](docs/PLANS.md) → "The `Evaluator transcript`
  section". This is the worker/checker split applied to plan
  completion.
- Phase 2 synthesis, phase 4 broad/irreversible ADRs, and every
  phase 5 ExecPlan invoke a typed design subagent (the **design
  subagent** tier; version per
  [model policy](docs/processes/model-policy.md) — the single source).
  Phase 2 → `harness-analyst`. Phase 5 → `harness-planner` (all
  plans; no complexity threshold — see
  [ADR pre-approval-critic-gate](docs/decisions/pre-approval-critic-gate.md)). Phase 4
  broad ADRs stay on the generic Opus Task call for now. The
  pre-approval critic is auto-fired by the
  `harness-planner-critic-hook.mjs` SubagentStop hook; the Completion
  Evaluator is orchestrator-invoked at the start of Phase 6 close-out.
  Both dispatch through `codex-companion.mjs adversarial-review` via
  Bash because the `/codex:adversarial-review` slash command is
  user-only. See `docs/processes/model-policy.md` § Codex commands
  reference.
- No plan moves from `status: draft` to `status: approved` without a
  `## Pre-approval critic transcript` section containing a non-BLOCKED
  verdict. The critic is auto-fired by
  `.claude/hooks/harness-planner-critic-hook.mjs` on `harness-planner`
  SubagentStop and writes its verdict into the section synchronously.
  This is the worker/checker split applied to plan approval — see
  [ADR pre-approval-critic-gate](docs/decisions/pre-approval-critic-gate.md) and
  [`docs/PLANS.md`](docs/PLANS.md) → "The `Pre-approval critic
  transcript` section".
- The subagents own the Write to `docs/analysis/...` and
  `docs/exec-plans/active/...`. The orchestrator never writes to those
  paths. Any `Write`/`Edit` whose `file_path` matches
  `^docs/(analysis|exec-plans/active)/` while the orchestrator tier
  is active is a policy violation: stop, delegate. The orchestrator's
  role on those paths is limited to (a) constructing the typed brief,
  (b) editing `docs/README.md` after the subagent returns to add the
  catalog row.
- Concrete delegation, copy-pasteable.

  **Phase 2 — analysis doc.** After bootstrap and after identifying
  the source files relevant to the brief (via `find` / `ls` /
  `grep -l`, *not* by reading them):

  ```
  Task(
    subagent_type="harness-analyst",
    model="opus",
    description="Phase 2 — <slug>",
    prompt="""
      feature_id: <feat-NNN or feature-less-reason: <one-line>>
      slug: <kebab-case topic>
      source_paths:
        - <repo-relative-path-1>
        - <repo-relative-path-2>
    """
  )
  ```

  **Phase 5 — ExecPlan.** After the analysis is approved and you
  have scoped the `covers:` path prefixes:

  ```
  Task(
    subagent_type="harness-planner",
    model="opus",
    description="Phase 5 — <slug>",
    prompt="""
      feature_id: <feat-NNN or feature-less-reason: <one-line>>
      slug: <kebab-case>
      covers:
        - <path-prefix-1>
        - <path-prefix-2>
      analysis_path: docs/analysis/YYYY-MM-DD_<slug>.md
    """
  )
  ```

  **You must pass `model: "opus"` explicitly in the Task call**, even
  though each subagent config declares `model: opus` in its
  frontmatter. The explicit override is belt-and-suspenders:
  (a) it removes any ambiguity about which model actually runs,
  (b) the harness-log tail will render the launch as
  `harness-analyst[opus]` / `harness-planner[opus]` instead of
  `[default]`, making policy compliance auditable from the log.
  A launch line showing `[default]` is a policy violation regardless
  of whether Opus actually ran — fix the Task call.

  Both subagents enforce a typed brief. If any required field is
  missing, they reply `MISSING_FIELDS: [...]` and refuse to write.
  Treat that reply as a contract violation on your side: fix the
  brief and re-invoke. Do not synthesize the missing field from memory.
  All path fields in those briefs (`source_paths`, `covers`,
  `analysis_path`) must be repository-relative. Optional leading `./`
  is fine. If a search tool returns an absolute path under this repo,
  strip the repo root before invoking the subagent. If a subagent
  replies `INVALID_PATHS: [...]`, re-invoke with relative paths.

  Caveat on hook tags: every tool event fired from inside the
  subagent (its own Reads, Writes, Greps) will still render with the
  orchestrator's `session_model` as the line prefix. That prefix
  reflects the parent session's transcript, not the subagent's. The
  subagent's model is only authoritatively visible in the `SUBAGENT`
  launch line. Do not interpret in-subagent orchestrator-tier tags as
  a model violation.

The phase-6 gate is enforced mechanically by a plan-coverage sensor
wired into the pre-commit hook. The sensor checks that every staged
source file is covered by the `covers:` frontmatter of a plan in
`docs/exec-plans/completed/` with `status: completed`. An approved
plan still in `active/` does not satisfy the sensor — the agent must move the plan to `completed/` and then commit
automatically (via `/commit` if available, otherwise directly via
`git commit` with a Conventional Commit message). See
`docs/PLANS.md` for the `covers:` spec. The sensor is the *last* line
of defence — analysis, plan, and full execution should exist long
before the commit is attempted.

Phases do not merge. Do not produce two phases' output in one pass. Full
workflow and phase definitions: [`docs/processes/harness.md`](docs/processes/harness.md).

## On receiving a task

When the user sends a new unit of work, **classify it before reading
code or writing anything**. Your first response must state the
classification and the next artifact you will produce. Do not produce
code in that first response. Three categories:

1. **Change-producing** — any request to modify, add, fix, implement,
   refactor, build, or otherwise change code or docs that ship.
   Imperative phrasing ("add X", "implement Y", "fix Z", "make it do W")
   is almost always this category. Enter the harness at phase 1. Your
   first response must name the analysis doc you will draft under
   `docs/analysis/` before touching source. Do not read code beyond
   what is needed to draft the analysis. Do not open the editor.
   Before naming the analysis doc, identify the affected Feature
   ID(s) in [`docs/FEATURES.md`](docs/FEATURES.md) — or declare the
   work feature-less with a one-line reason (`feature-less-reason:`
   in the eventual plan's frontmatter).
2. **Investigation-only** — the user is asking a question, requesting
   an audit, or exploring a decision. No code changes expected. Skip
   the harness; read and report. If the investigation uncovers work
   worth doing, stop and re-classify.
3. **Trivial and self-evident** — typo, docstring wording, obvious
   rename with no behavioural impact. You may proceed directly, but
   your first response must say "trivial — no analysis" so the user
   can redirect if they disagree.

**Imperative phrasing is not a license to skip the harness.** A direct
instruction is the brief for phase 1, not a bypass of it. If the user
wants to skip, they must say so explicitly ("skip the harness", "no
plan needed", "just code it"). You do not self-grant the exemption.

If in doubt between change-producing and trivial, treat it as
change-producing. If in doubt between change-producing and
investigation-only, ask.

## Session bootstrap

For change-producing and investigation-only tasks, before producing any
substantive output:

1. Read [`docs/FEATURES.md`](docs/FEATURES.md) — the scope surface. Any
   task that names or implies a behavior must map to a Feature row
   (existing or new) before phase 1 can produce an analysis doc.
2. Read `docs/README.md` — catalog and tag vocabulary.
3. Scan `docs/exec-plans/active/` — what is in flight. If a plan is
   present, read its `covers:` frontmatter and keep the path-prefix
   list in working context so every subsequent Edit/Write can be
   checked at the call site (per Hard constraints).
4. Scan `docs/decisions/` — what is already decided.
5. Note which Features in `docs/FEATURES.md` are `Passing` as the
   baseline for the session-exit verifier dimension.
6. Read only the docs whose tags match the current task.
7. Read `docs/processes/model-policy.md` — the fleet model assignments
   for harness steps.
8. **Harness-version check.** Read `.harness-version` at the repo
   root (single-line ISO date). If the file is present, compare its
   value to the most recent `## YYYY-MM-DD` heading in
   `~/.claude/skills/init-docs/CHANGELOG.md`. If the marker is
   older, surface to the user: "This repo is N harness entries
   behind; run `/init-docs` to sync." If the marker is absent but
   `docs/` exists, surface: "No `.harness-version` found; run
   `/init-docs` to establish the baseline." Do **not** auto-apply
   changes — detection only. If the skill directory is unreachable
   (different machine, non-Claude agent), skip the check gracefully.

For tasks that touch code, also read [`ARCHITECTURE.md`](ARCHITECTURE.md)
before phase 2 investigation. Check
[`docs/tech-debt-tracker.md`](docs/tech-debt-tracker.md) if the task
area overlaps with any open debt items.

## Where to save outputs

| Output type | Folder | Naming |
|---|---|---|
| Research, gap analysis, investigations | `docs/analysis/` | `YYYY-MM-DD_<topic>.md` — template: `_template.md` |
| Architectural decisions (ADRs) | `docs/decisions/` | `<slug>.md` (slug = `id:` frontmatter; see ADR adr-slug-canonical) |
| Exec plans (active) | `docs/exec-plans/active/` | `YYYY-MM-DD_<id>_<slug>.md` — spec: [`PLANS.md`](docs/PLANS.md); template: `_template.md` |
| Exec plans (completed) | `docs/exec-plans/completed/` | same filename, moved on completion |
| Process guidelines, runbooks | `docs/processes/` | `<topic>.md` |
| Request flows, component docs, diagrams | `docs/architecture/` | `<slug>.md` or `<slug>.drawio` |
| External specs, legacy behaviour snapshots | `docs/references/` | `<name>-llms.txt` |
| Machine-generated artifacts | `docs/generated/<subfolder>/` | per-subfolder; see `docs/generated/README.md` |
| Feature ledger | `docs/FEATURES.md` | append rows under the matching state section; single file, not per-instance |
| Tech debt ledger | `docs/tech-debt-tracker.md` | append-only; new rows at top of relevant section |
| AI-generated ticket drafts | `docs/tickets/` | `YYYY-MM-DD_<ID>_<slug>.md` |

After creating any doc, add a one-line entry to the relevant section of
`docs/README.md` with at least one domain tag and one type tag.

ADR identity and format: see [ADR adr-slug-canonical](docs/decisions/adr-slug-canonical.md).

## Working relationship

- No sycophancy.
- Be direct, matter-of-fact, and concise.
- Be critical; challenge reasoning.
- Don't include timeline estimates in plans.
- Don't add yourself as a co-author to git commits.
- On user signals "we're done", "ttyl", "close out", or similar, run
  the Session-exit checklist (see `docs/processes/harness.md` §
  Session exit) before responding.
