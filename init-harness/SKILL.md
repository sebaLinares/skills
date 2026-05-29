---
name: init-harness
description: Initialize a lightweight, vendor-neutral documentation harness for a small tool or project. Scaffolds a minimal docs/ structure (exec-plans, decisions, processes), repo-root AGENTS.md (+ CLAUDE.md symlink) and ARCHITECTURE.md, a docs/PLANS.md ExecPlan contract, two harness ADRs, an operating manual, and one stdlib-Python plan-coverage pre-commit check. No Claude/Codex subagents, hooks, model policy, or companion scripts — enforcement is git pre-commit plus the coverage check only. Use this skill when the user invokes /init-harness, asks for a "lightweight harness", to "add a harness to a small tool/CLI/TUI", "scaffold a minimal harness", "set up a guided dev process for a tool", or wants the architecture benefits of a harness without the heavier init-docs ceremony. Versioned with semver; re-running on an existing repo applies only the version delta.
---

# init-harness

Scaffolds a **lightweight, vendor-neutral harness** for small tools: an
`AGENTS.md` entry point (with `CLAUDE.md` symlink), an `ARCHITECTURE.md` map,
a four-phase workflow (Brief → Decide → Plan → Execute), an ExecPlan contract
(`docs/PLANS.md`) with `covers:`/`verify:` frontmatter, two harness ADRs, and
**one** mechanical sensor: a stdlib-Python plan-coverage check wired into
pre-commit.

Nothing is tied to a specific agent vendor — no subagents, no `.claude/hooks`,
no codex companion script, no model policy. An independent review (fresh
agent, separate session, human, or external CLI like Codex) is encouraged but
invoked manually, never wired as a mechanical gate.

This is the lighter sibling of `init-docs`. Reach for `init-docs` when a
team/fleet needs heavyweight enforcement; reach for `init-harness` for a
solo/small tool that wants the architecture benefits without the ceremony.

Bundled seed files live in `assets/`. The skill writes them with minor
substitutions (`{{REPO_NAME}}`, project context).

## Versioning

The skill is versioned with **semver**, in `VERSION` (single line). Each
release records its changes in `versions/<X.Y.Z>.md` — a self-contained file
with **What changed** + **How to apply** (idempotent, check-then-act). There is
no monolithic changelog: a repo learns what changed by reading **only the
version files newer than its own marker**, so the read cost scales with the
delta, not the history.

Bump levels:
- **patch** (`x.y.Z`) — fix to an existing harness file. Re-run applies
  silently.
- **minor** (`x.Y.0`) — additive: a new file, section, or artifact. Re-run
  fills it in idempotently, no confirmation.
- **major** (`X.0.0`) — breaking: a file moved/renamed/removed or a contract
  changed. Re-run **shows a diff and requires explicit confirmation**.

Scaffolded repos record the applied version in `.harness-version` at their
root (e.g. `1.2.0`).

## How to update this skill

Use the bump script, then fill in the version file:

    ./bump-version.sh {major|minor|patch}

It computes the next semver, scaffolds `versions/<next>.md`, and updates
`VERSION`. Fill in the two sections of `versions/<next>.md`, edit the asset(s),
then stage **asset + VERSION + versions/<next>.md** in one commit.

The pre-commit gate (`.githooks/pre-commit`) refuses any commit touching
`assets/` or `SKILL.md` unless `VERSION` was bumped **and** a matching,
filled-in `versions/<VERSION>.md` is staged. Activate it (skill-local, mirrors
init-docs):

    git config core.hooksPath init-harness/.githooks

Bypass for typos/experiments: `INIT_HARNESS_BYPASS="<reason>" git commit ...`.

The **How to apply** block in every version file must be stack-neutral and
idempotent (check-then-act).

## Modes of operation

On invocation, read the target repo's `.harness-version` and compare it to this
skill's `VERSION`:

| Target state | Mode | Action |
|---|---|---|
| No `.harness-version`, no harness files | **Scaffold** | Steps 1–13; write `.harness-version` = `VERSION` |
| No `.harness-version`, harness files present | **Adopt + upgrade** | Assume baseline `1.0.0`; fill any missing files; then run the upgrade delta |
| `.harness-version` < `VERSION` | **Upgrade** | Skip scaffold; apply the version delta (below) |
| `.harness-version` = `VERSION` | **Up-to-date** | No-op; report "harness is current at `<VERSION>`" |
| `.harness-version` > `VERSION` | **Skill behind** | Report; do nothing (the repo is ahead of the installed skill) |

Determine mode before writing anything.

## Scaffold steps

### Step 1 — Inspect what exists

List every file/dir the skill would write (Step 3 onward). If the repo has a
custom or conflicting layout, list the conflicts and ask skip / overwrite /
abort before proceeding. A fresh repo proceeds without prompting.

Resolve `{{REPO_NAME}}`: use the git repo's directory name (or remote name).
Substitute it into the `owner:` frontmatter of every written markdown file.

### Step 2 — `.gitignore`

Ensure the repo-root `.gitignore` contains (append only what's missing):

    __pycache__/
    **/__pycache__/
    *.py[cod]
    .claude/settings.local.json

### Step 3 — Folders

Create (skip existing), adding `.gitkeep` to otherwise-empty dirs:

    docs/decisions/
    docs/exec-plans/active/
    docs/processes/
    scripts/harness/

### Step 4 — Repo-root anchors

- Copy `assets/AGENTS.md` → `AGENTS.md`.
- Create `CLAUDE.md` as a symlink to `AGENTS.md` (`ln -s AGENTS.md CLAUDE.md`).
  On filesystems where `ln` fails, copy instead and flag it in the report
  ("keep the two in sync manually").
- Copy `assets/ARCHITECTURE.md` → `ARCHITECTURE.md` (skeleton — flag as
  needs-filling).

### Step 5 — ExecPlan contract + template

- Copy `assets/PLANS.md` → `docs/PLANS.md`.
- Copy `assets/exec-plan-template.md` → `docs/exec-plans/_template.md`.

### Step 6 — Operating manual + dev setup

- Copy `assets/harness.md` → `docs/processes/harness.md`.
- Copy `assets/dev-setup.md` → `docs/processes/dev-setup.md` (skeleton — flag
  as needs-filling).

### Step 7 — Tech-debt tracker

Copy `assets/tech-debt-tracker.md` → `docs/tech-debt-tracker.md`.

### Step 8 — Seed the two ADRs

| Slug | Asset |
|---|---|
| `harness-design` | `assets/harness-design.md` |
| `adr-slug-canonical` | `assets/adr-slug-canonical.md` |

For each, check `docs/decisions/<slug>.md`:
- **Absent** → copy.
- **Present with matching `id:`** → skip (idempotent).
- **Present with different `id:`** → halt with a conflict report; do not
  proceed.

In `harness-design`, leave `{{PROJECT_CONTEXT}}` and `{{V1_CONTENTS}}` as
placeholders if not known from the brief, and flag them as needs-filling.

### Step 9 — Catalog

Copy `assets/docs-README.md` → `docs/README.md`. No tag substitution — the
catalog is a plain linked list.

### Step 10 — Plan-coverage check

Copy `assets/scripts/check_plan_coverage.py` → `scripts/harness/`. `chmod +x`.
It is the one mechanical sensor; wiring it into pre-commit is the user's step
(documented in `dev-setup.md` § Plan-coverage check). Flag in the report:
"requires `python3 ≥ 3.9`; wire into pre-commit per dev-setup.md".

### Step 11 — Write `.harness-version`

Write this skill's `VERSION` value (read `init-harness/VERSION`) as a single
line to `.harness-version` at the repo root.

### Step 12 — Report

List **Created**, **Skipped (already existed)**, and **Needs filling**
(`ARCHITECTURE.md`, `docs/processes/dev-setup.md`, and any `{{PLACEHOLDER}}`
left in `harness-design`). State the `.harness-version` value written. Remind
the user to wire the plan-coverage check into pre-commit. If the `CLAUDE.md`
symlink fell back to a copy, call it out.

## Upgrade delta procedure

Runs in place of the scaffold when `.harness-version` < `VERSION`.

1. Read the target's `.harness-version` (the marker, e.g. `1.1.0`).
2. **List** `versions/*.md` filenames — do not read their contents yet.
3. Parse each filename as semver; select those **strictly greater** than the
   marker; sort ascending.
4. **Read only those files.** This is the token-efficient step — history below
   the marker is never read.
5. Apply each, oldest → newest:
   - Print the version's heading and **What changed** so the user sees what is
     being applied.
   - Execute the **How to apply** steps (idempotent check-then-act).
   - For a **major** version, show a diff and require explicit `y/n` before
     applying.
   - After each version's steps verify, advance `.harness-version` to that
     version (incremental — persisted immediately; a later failure does not
     roll back earlier successes).
6. If a step's target is locally modified such that the insertion point is
   ambiguous, **stop**, report the conflict, and leave the marker at the last
   clean version.
7. Report: which versions applied, which conflicted, the new marker.

## Notes on scope

- **The skill never modifies source code** — only docs and root-level markdown,
  plus the one Python script under `scripts/harness/`.
- **No agent-vendor coupling.** No subagents, no `.claude/hooks`, no model
  policy, no companion review script. `AGENTS.md` is the cross-agent surface.
- **One mechanical sensor.** The plan-coverage check is the only teeth shipped;
  everything else is guide (prose the agent follows) plus git pre-commit. The
  check's contract is documented for re-implementation in any language.
- **Independent review is manual.** Run a second-pass review when a change
  warrants it; it is not gated.
