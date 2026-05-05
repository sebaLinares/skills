---
name: init-docs
description: Initialize a harness-oriented documentation system for a project. Creates `docs/` subfolders (architecture, analysis, decisions, processes, exec-plans/{active,completed}, references, generated, tickets), a master catalog at `docs/README.md` with tag-based navigation, `docs/PLANS.md` as the ExecPlan specification, analysis + exec-plan templates, a seeded operating manual at `docs/processes/harness.md`, ADR 001 — Harness Engineering, a language-agnostic `dev-setup.md`, `docs/tech-debt-tracker.md`, `docs/generated/README.md`, and repo-root anchors (`AGENTS.md` with `CLAUDE.md` symlink, `ARCHITECTURE.md`, `SECURITY.md`) that encode the operating principle, session bootstrap, and phase gates. Use this skill when the user invokes /init-docs, asks to "set up docs", "initialize documentation structure", "scaffold docs", "set up a harness", "add a harness for AI agents", or wants to bootstrap an AI-harness documentation system for a project. Accepts an optional domain description to adapt tag vocabulary; if omitted, scans the project to infer tags automatically.
---

# init-docs

Scaffolds a harness-oriented documentation system: guides
(`AGENTS.md` + symlink, `docs/` hierarchy, templates, references),
sensors pointer (`dev-setup.md` for the pre-commit hook), and a
published operating manual (`docs/processes/harness.md`) with phase
gates from brief → analysis → decisions → plan → execution. The
ExecPlan contract lives in `docs/PLANS.md`. Repo-root anchors
(`ARCHITECTURE.md`, `SECURITY.md`, `tech-debt-tracker.md`) hold
load-bearing context that agents read before touching code.

Bundled seed files live in `assets/`. The skill writes them with
minor substitutions (tag vocabulary, project context). Every file
is language-agnostic; stack-specific content stays as prompts or
placeholders that the user fills after scaffolding.

The skill is versioned: `CHANGELOG.md` in this directory is the source
of truth for changes to assets and SKILL.md. Each scaffolded repo
records the applied version in `.harness-version` at its root (single-
line ISO date). Running the skill on a stale repo applies pending
changelog entries.

## How to update this skill

Every change to files under `assets/` or to `SKILL.md` MUST be
accompanied by a new entry in `CHANGELOG.md` dated today. The
git pre-commit hook (`.githooks/pre-commit`) enforces this.

Ritual:

1. Edit the asset(s) or SKILL.md.
2. Add a `## YYYY-MM-DD — <feature name>` entry in `CHANGELOG.md`
   following the entry shape documented at the top of that file.
   The "How to apply" block must be **stack-neutral** and
   **idempotent** (check-then-act). Quarantine stack-specific
   material to the optional "Stack-specific notes" block.
3. Test with a retrofitted repo: pick one scaffolded repo whose
   `.harness-version` is older than the new entry, run the skill,
   verify the entry applies idempotently and advances the marker.
4. Commit. The pre-commit hook refuses if step 2 is missing.

Bypass for exceptional commits (typos, experiments, bootstrap):

    SKILL_CHANGELOG_BYPASS="<reason>" git commit ...

## Modes of operation

On invocation, the skill first determines mode from the target
repo's state:

| State | Mode | Action |
|---|---|---|
| No `docs/`, no `.harness-version`, no conflicts | **Scaffold** | Steps 1–16 below; final step writes `.harness-version` to changelog head date |
| `.harness-version` present and < changelog head | **Audit** | Skip scaffold; run the audit procedure (see "Audit mode" below) |
| `.harness-version` present and = changelog head | **Up-to-date** | No-op; report "harness version <date> is current" |
| No `.harness-version` but `docs/` exists from a prior scaffold | **Upgrade + audit** | Run Step 1 (upgrade path, fill missing files), set `.harness-version` to the pre-changelog sentinel `2026-04-19`, then audit |
| Custom / conflicting layout | **Custom** | Step 1's "Anything else exists" branch; prompt skip/overwrite/abort |

Mode detection happens before any files are written.

## Step 1 — Check what already exists

Before creating anything, inspect the project root. List every file
and directory the skill would write:

- Repo root: `AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `SECURITY.md`.
- `docs/`: `README.md`, `PLANS.md`, `tech-debt-tracker.md`.
- `docs/` subfolders: `analysis/`, `architecture/`, `decisions/`,
  `exec-plans/active/`, `exec-plans/completed/`, `generated/`,
  `processes/`, `references/`, `tickets/`.
- Templates: `docs/analysis/_template.md`, `docs/exec-plans/_template.md`.
- Seeded docs: `docs/processes/harness.md`, `docs/processes/dev-setup.md`,
  `docs/decisions/001-harness-design.md`, `docs/references/README.md`,
  `docs/generated/README.md`.

First, read `.harness-version` at the repo root if it exists. This
determines the mode (see "Modes of operation" above). If the marker
equals the changelog head date, stop and report "up to date." If the
marker is older, skip to the "Audit mode" section — the scaffold
steps below do not apply.

If `.harness-version` is absent, proceed with the remaining cases:

- **Fresh project** — nothing conflicts: proceed without prompting to
  scaffold steps 2–16.
- **Older init-docs output** — older `docs/` layout without
  `exec-plans/`, `references/`, `generated/`, `PLANS.md`,
  `tech-debt-tracker.md`, `harness.md`, or ADR 001, and/or
  pre-existing `CLAUDE.md` without the symlink: treat as an upgrade.
  List what's present, what's missing, and offer:
  - **Upgrade** (default) — add only missing artifacts; do not touch
    existing files. After the upgrade, write `.harness-version` =
    `2026-04-19` (the pre-changelog sentinel) so that the subsequent
    audit picks up every changelog entry. When `CLAUDE.md` exists as
    a regular file, leave it and skip the symlink (note in the Step
    16 report that the user can migrate manually).
  - **Overwrite** — replace everything (destructive — confirm
    explicitly). After overwrite, write `.harness-version` = changelog
    head date (the repo is now current).
  - **Abort**.
- **Anything else exists** — custom layout: list conflicts and ask
  skip / overwrite / abort.

Do not proceed until the user responds in the non-fresh cases.

## Step 2 — Derive domain tags

The goal is a tag vocabulary that reflects the real domain language of
*this* project. `#ai-harness` (domain) and the type tags `#plan`,
`#architecture`, `#security`, `#tech-debt` are added unconditionally
because they are harness-intrinsic.

**If the user provided a domain description** (e.g. `/init-docs NestJS
e-commerce product microservice`):
- Extract the nouns that represent bounded domains: modules, services,
  entities.
- Also extract external systems/dependencies mentioned.
- Examples: "product microservice" → `#products`, `#pricing`,
  `#inventory`; "uses Stripe and PostgreSQL" → `#stripe`,
  `#postgresql`.

**If no description was provided**, scan the project to infer tags:

1. Read `package.json` / `go.mod` / `pyproject.toml` / `Cargo.toml` —
   check name and description for domain hints.
2. List top-level source subdirectories (`src/`, `lib/`, `internal/`,
   `app/`, `cmd/`) — each top-level folder is typically a module;
   derive a tag from its name.
3. Check dependency declarations to identify external systems the
   code integrates with. Common patterns:
   - `@commercetools/*` → `#commercetools`
   - `stripe` → `#stripe`
   - `ioredis` / `redis` → `#redis`
   - `pg` / `typeorm` → `#postgresql`
   - `mongoose` → `#mongodb`
   - `aws-sdk` / `@aws-sdk/*` → `#aws`
   - `gin-gonic/gin` → `#gin`
   - `fastapi` → `#fastapi`
   - `@nestjs/*` → `#nestjs`

Aim for 4–8 domain tags and 2–5 external dependency tags. Keep all
tags lowercase and hyphenated.

## Step 3 — Create the folder structure

Create these directories (skip any that already exist):

```
docs/
├── analysis/
├── architecture/
├── decisions/
├── exec-plans/
│   ├── active/
│   └── completed/
├── generated/
├── processes/
├── references/
└── tickets/
```

Add a `.gitkeep` to every otherwise-empty directory so they are
tracked by git. `exec-plans/active/`, `exec-plans/completed/`, and
`generated/` especially matter — these are first-class artifact
locations and must exist even when empty.

## Step 4 — Write the analysis template

Copy `assets/analysis-template.md` to `docs/analysis/_template.md`.
It references `docs/processes/harness.md` (created in Step 7).

## Step 5 — Write the exec-plan template

Copy `assets/exec-plan-template.md` to `docs/exec-plans/_template.md`.
The template has 12 required sections matching `docs/PLANS.md`
(created in Step 6).

## Step 6 — Write `docs/PLANS.md`

Copy `assets/PLANS.md` to `docs/PLANS.md`. This is the ExecPlan
specification — the contract every plan in `docs/exec-plans/active/`
must satisfy. It is load-bearing; do not skip.

## Step 7 — Write the operating manual

Copy `assets/harness.md` to `docs/processes/harness.md`. This is the
day-to-day manual: operating principle, session bootstrap (referencing
`AGENTS.md` via the `CLAUDE.md` symlink), six-phase workflow with
phase-5 delegating to `PLANS.md`, phase-gate table, artifact paths,
steering loop, and an ADR format appendix that `AGENTS.md` points at.

## Step 8 — Write the developer setup skeleton

Copy `assets/dev-setup.md` to `docs/processes/dev-setup.md`. This file
is a language-agnostic skeleton — every section is a placeholder the
user must fill in with stack-specific commands (toolchain, pre-commit
hook, common commands, start command). Flag it in the Step 16 report
as "needs filling".

## Step 9 — Write the references convention

Copy `assets/references-README.md` to `docs/references/README.md`. The
convention is **llms.txt only**: authoritative specs the code must
satisfy, one file per external system, required `# Source` header, no
opinions.

## Step 10 — Write the generated convention

Copy `assets/generated-README.md` to `docs/generated/README.md`. The
convention: machine-generated artifacts are checked in so agents can
read them without running the generator. The "never point generators
at `docs/` itself" rule is load-bearing — stale generators that wipe
their output directory will destroy the rest of the harness.

## Step 11 — Write the tech-debt tracker

Copy `assets/tech-debt-tracker.md` to `docs/tech-debt-tracker.md`.
Empty ledger with the severity + status legend. New entries go at the
top of the relevant section.

## Step 12 — Seed ADR 001

Copy `assets/001-harness-design.md` to
`docs/decisions/001-harness-design.md`. Two placeholders need filling:

- `{{PROJECT_CONTEXT}}` — one paragraph describing the project: team
  size, what the repo does, how AI is being used today. If this isn't
  known from the brief, leave the placeholder verbatim and flag it in
  the Step 16 report so the user can fill it in.
- `{{V1_CONTENTS}}` — project-specific list of what ships in v1. The
  template provides a generic starter list (including `docs/PLANS.md`
  as item 7 and `AGENTS.md` in item 5). Adjust the language/tooling
  entry (pre-commit hook) to match the project's stack if detectable
  from Step 2, otherwise leave the placeholder.

The Fowler/OpenAI guides-vs-sensors mental model, the phase-gate rule,
the plan-format reference to `PLANS.md`, the agent-entry-point note
about `AGENTS.md` + symlink, and the steering-loop cadence are reusable
across any project and stay verbatim.

## Step 13 — Write `docs/README.md`

Copy `assets/docs-README.md` to `docs/README.md`. Two substitutions:

- Replace `DOMAIN_TAGS` with the domain tags derived in Step 2, space-
  separated with backticks: `` `#products` `#pricing` `#inventory` ``.
- Replace `EXTERNAL_TAGS` with the external dependency tags:
  `` `#stripe` `#postgresql` ``.

`#ai-harness` (domain) and `#plan` / `#architecture` / `#security` /
`#tech-debt` (type) are already in the template — do not remove them.
The catalog already has sections for Repo-root anchors, Generated, and
Tech debt populated with links to the files written in earlier steps.

If `docs/README.md` already exists and the user chose "upgrade" or
"skip", leave it alone and emit a note in the Step 16 report pointing
out which sections (Repo-root anchors, Exec plans, Generated, Tech
debt) need to be added manually. Show the user the exact lines to
append.

## Step 14 — Write `AGENTS.md` and create the `CLAUDE.md` symlink

Copy `assets/AGENTS.md` to the project root. The file is generic and
does not require substitution.

Then create `CLAUDE.md` as a symlink to `AGENTS.md`:

```
ln -s AGENTS.md CLAUDE.md
```

On Windows / non-symlink filesystems where `ln` fails, fall back to
copying `AGENTS.md` to `CLAUDE.md` and emit a warning in the Step 16
report: "symlink not supported on this filesystem; `CLAUDE.md` copied
instead — keep the two files in sync manually, or re-run on a
Unix-like filesystem".

If either file already exists and the user chose "upgrade" or "skip",
leave it alone and emit a diff in the Step 16 report showing what the
harness expects — operating principle, session bootstrap, phase gates,
output-routing table — so the user can merge it manually.

## Step 15 — Write `ARCHITECTURE.md` and `SECURITY.md`

Copy `assets/ARCHITECTURE.md` and `assets/SECURITY.md` to the project
root. Both are language-agnostic skeletons — every section is a
prompt ("*Fill in …*") the user must resolve. Do not try to pre-fill
from code scanning; the point of these files is forcing the user to
capture context that only they know.

Flag both files in the Step 16 report as "needs filling".

## Step 16 — Write `.harness-version`

Write a single line to `.harness-version` at the repo root. The value
is the date of the most recent entry in this skill's `CHANGELOG.md`
(the "changelog head date"). Do **not** use today's date — a scaffold
done after the changelog head would otherwise claim to be newer than
any entry and mask pending work if new entries are added later.

For upgrade-mode runs (the "Older init-docs output" branch of Step 1),
write the pre-changelog sentinel `2026-04-19` instead, so the
subsequent audit picks up every changelog entry.

## Audit mode procedure

This runs in place of the scaffold when `.harness-version` is present
and older than the changelog head.

1. Read `.harness-version` (the repo marker).
2. Read this skill's `CHANGELOG.md`. Enumerate entries whose heading
   date is strictly greater than the marker. Process them oldest-
   first (bottom-up in the file).
3. For each pending entry, in order:
   a. Print the entry's heading and the "What" summary so the user
      sees what is about to be applied.
   b. Execute each numbered step in the "How to apply" block. Every
      step is written as check-then-act — read the target file,
      confirm the change is not already present, then apply.
   c. If a step's target file has been locally modified such that
      the insertion point is ambiguous (renamed heading, reordered
      structure, missing expected section), **stop the audit**,
      report the specific conflict to the user, and do not advance
      the marker.
   d. If the entry is marked "replacing" (not additive), show the
      diff and require explicit user confirmation before applying.
   e. After each step completes, re-read the target file and verify
      the expected content is present. If verification fails, stop;
      do not advance the marker.
   f. Once *all* steps for an entry pass verification, update
      `.harness-version` to that entry's date. This is incremental —
      one entry at a time, persisted immediately. A later failure
      does not roll back earlier successes.
4. When all pending entries are applied, report: "harness version
   advanced from <old> to <new>; N entries applied." If any entry
   failed or conflicted, report which one and leave the marker at
   the last successful entry's date.

**Never** auto-apply "replacing" entries, never merge conflicts
autonomously, never silently skip steps.

## Step 17 — Report what was created

List every file and directory created or skipped. Use four sections:

- **Created** — new files, with paths. Include `.harness-version`
  with its value.
- **Skipped (already existed)** — existing files not touched.
- **Needs filling** — files written with placeholder content the user
  must resolve. At minimum: `ARCHITECTURE.md`, `SECURITY.md`,
  `docs/processes/dev-setup.md`, and any `{{PLACEHOLDER}}` remaining
  in ADR 001.
- **Needs manual merge** — only if the user chose "upgrade" or "skip"
  and a pre-existing file would have been updated. Show the exact
  content to merge.

For audit-mode runs, replace the four sections with a single summary:
which entries applied, which conflicted (if any), and the new marker
value.

If tags were inferred from the project (Step 2), briefly explain the
signals used so the user can correct wrong inferences.

If the `CLAUDE.md` symlink fell back to a copy (Step 14), call it out.

## Notes on scope

- **No pre-commit hooks are installed.** Hooks are language-specific
  and belong in a separate skill. The user fills in `dev-setup.md`
  with their stack's hook entrypoint; installing it is a manual or
  separate-skill step.
- **Sensor documentation is included; sensor scripts are not.**
  `AGENTS.md`, `PLANS.md`, `harness.md`, and `dev-setup.md` all
  describe the plan-coverage sensor pattern: a pre-commit check that
  reads each approved plan's `covers:` frontmatter and blocks any
  staged source file not covered. The actual script
  (`scripts/verify-plan-coverage.sh` or equivalent) is
  stack-specific and must be implemented after scaffolding. The Go
  reference implementation lives in the ms-search repo at ADR 003.
- **`ARCHITECTURE.md` and `SECURITY.md` are not pre-filled from code
  scanning.** They intentionally force the user to capture project
  context that scanning can't infer (why the system is shaped this
  way, what the threat model actually is).
- **The skill never modifies source code** — only documentation and
  root-level markdown files.
