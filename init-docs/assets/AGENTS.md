# Agent Instructions

The entry point into this repository for any coding agent. Loaded
automatically by Claude Code (via the `CLAUDE.md` symlink) and by any
other agent that reads `AGENTS.md` at the repo root.

## Operating principle

**If it is not in the repo, it does not exist.** Anything the agent must
reason over must live as versioned markdown, code, or schema inside this
repo. Knowledge in Slack, meetings, Jira, Confluence, or human memory is
invisible. When a piece of context is load-bearing, capture it here first.

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

1. Read `docs/README.md` — catalog and tag vocabulary.
2. Scan `docs/exec-plans/active/` — what is in flight.
3. Scan `docs/decisions/` — what is already decided.
4. Read only the docs whose tags match the current task.
5. **Harness-version check.** Read `.harness-version` at the repo
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

## Phase gates

- No code without an approved ExecPlan in `docs/exec-plans/active/`.
- No ExecPlan without an analysis doc in `docs/analysis/`.
- No analysis without completing the session bootstrap.
- ExecPlans must satisfy every non-negotiable requirement in
  [`docs/PLANS.md`](docs/PLANS.md). Deviations from the spec are
  themselves decisions and must be logged.

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

If a user instruction conflicts with these gates, say so before
complying. Do not silently comply.

## Where to save outputs

| Output type | Folder | Naming |
|---|---|---|
| Research, gap analysis, investigations | `docs/analysis/` | `YYYY-MM-DD_<topic>.md` — template: `_template.md` |
| Architectural decisions (ADRs) | `docs/decisions/` | `NNN-<title>.md` (sequential) |
| Exec plans (active) | `docs/exec-plans/active/` | `YYYY-MM-DD_<id>_<slug>.md` — spec: [`PLANS.md`](docs/PLANS.md); template: `_template.md` |
| Exec plans (completed) | `docs/exec-plans/completed/` | same filename, moved on completion |
| Process guidelines, runbooks | `docs/processes/` | `<topic>.md` |
| Request flows, component docs, diagrams | `docs/architecture/` | `<slug>.md` or `<slug>.drawio` |
| External specs, legacy behaviour snapshots | `docs/references/` | `<name>-llms.txt` |
| Machine-generated artifacts | `docs/generated/<subfolder>/` | per-subfolder; see `docs/generated/README.md` |
| Tech debt ledger | `docs/tech-debt-tracker.md` | append-only; new rows at top of relevant section |
| AI-generated ticket drafts | `docs/tickets/` | `YYYY-MM-DD_<ID>_<slug>.md` |

After creating any doc, add a one-line entry to the relevant section of
`docs/README.md` with at least one domain tag and one type tag.

ADR format: see appendix in [`docs/processes/harness.md`](docs/processes/harness.md).

## Working relationship

- No sycophancy.
- Be direct, matter-of-fact, and concise.
- Be critical; challenge reasoning.
- Don't include timeline estimates in plans.
- Don't add yourself as a co-author to git commits.
