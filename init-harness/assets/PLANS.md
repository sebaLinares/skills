---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-29
update_trigger: on-execplan-spec-change
---

# PLANS.md — ExecPlan specification

The contract for ExecPlans in this repo.

When **writing** a plan, follow this to the letter. When **implementing** one,
treat it as the single source of truth — do not rely on prior conversation or
external docs that the plan does not explicitly reference.

An ExecPlan is a design document a coding agent can follow to deliver working,
observable behaviour. Treat the reader as a complete beginner to this repo:
they have only the current working tree and this one file.

## How ExecPlans fit the harness

ExecPlans are the Phase-3 artifact of the workflow
([`processes/harness.md`](processes/harness.md)). Active plans live in
`docs/exec-plans/active/`; on completion they move to `docs/exec-plans/` with
`status: completed`. Plan-scoped decisions stay inline in the Decision Log;
architectural decisions are promoted to ADRs in `docs/decisions/`.

Only one plan lives in `active/` at a time.

## Frontmatter

Every ExecPlan begins with a YAML frontmatter block. Required fields:

- `status` — `active` or `completed`.
- `covers` — list of repository-relative path prefixes this plan authorises
  changes to. **Load-bearing**: the plan-coverage check reads it. See below.
- `verify` — a literal shell command that proves the plan is done (tests,
  build, smoke check). Run it until green before completing the plan.

Optional: `id`, `slug` (used in the filename), `adrs` (paths to ADRs this plan
cites).

### The `covers:` field

`covers:` is a list of repository-relative **path prefixes**. Optional leading
`./` is accepted. Absolute paths are invalid. A file is "covered" if any entry
is a prefix of its path. Prefix match is literal; a trailing `/` covers a
directory and everything inside it:

    covers:
      - internal/widget/
      - cmd/foo/main.go

This field is consumed by the plan-coverage check at pre-commit
(`scripts/harness/check_plan_coverage.py`), which reads plan content from the
git **index** (the staged version). Coverage is granted by the active plan
(`docs/exec-plans/active/`) *and* by completed plans at the `docs/exec-plans/`
root — so the "move the plan out of `active/`, then commit" completion flow is
committable (the just-moved completed plan still grants coverage). Always
allowed without coverage: anything under `docs/` or `scripts/harness/`, the
root anchors (`AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `SECURITY.md`,
`README.md`), and `.harness-version`. Staged deletes count as edits and need
coverage too. For urgent commits, bypass with:

    HARNESS_BYPASS="<reason>" git commit ...

See `docs/processes/dev-setup.md` § Plan-coverage check.

### The `verify:` field

`verify:` is the command a human (or the agent) runs to confirm the plan
delivered working behaviour. It is the completion gate: the plan is not done
until `verify:` is green. Examples:

    verify: go test ./... && go build ./...
    verify: npm test && npm run build

## Required sections

Every ExecPlan contains exactly these sections, kept current as work proceeds.
The skeleton is [`exec-plans/_template.md`](exec-plans/_template.md).

- **Goal** — what someone can do after this change that they couldn't before,
  and how to see it working. The brief, restated in plain terms.
- **Out of scope** — what this plan deliberately will not touch. Prevents
  scope creep; keeps `covers:` honest.
- **Plan of Work** — the ordered, concrete sequence of edits. For each, name
  the file and what to insert or change. Minimal and specific.
- **Verify** — how to confirm green: the `verify:` command plus any manual
  checks. State the behaviour a human can observe, not internal structure.
- **Decision Log** — every plan-scoped decision, with rationale and date.
  Architectural decisions go to `docs/decisions/` as ADRs instead.

## Non-negotiable requirements

- **Self-contained.** A novice with only this file and the working tree can
  execute it to a working outcome. Embed required knowledge in your own words.
- **Living document.** Revise it as work proceeds and discoveries occur; after
  every revision it must remain self-contained.
- **Demonstrably working.** State the observable outcome and how to verify it,
  not merely "code that meets a definition."
- **Define terms of art.** If you use a non-ordinary phrase ("adapter",
  "projection"), define it immediately and name where it appears in the repo.

## Style

**Prose first.** Plain sentences over checklists and tables, except in the
Plan of Work where an ordered list is natural. **Anchor on observable
outcomes** — "after `go run ./cmd/foo`, the TUI shows the new pane" is
acceptable; "added a Model struct" is not. **Resolve ambiguity in the plan**;
don't outsource decisions to the reader.

## Formatting

The plan file contains only the ExecPlan. Do not wrap the whole plan in a
fence; fence only internal code blocks or transcripts. Use `#`/`##`/`###`
headings.
