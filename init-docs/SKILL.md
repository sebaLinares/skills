---
name: init-docs
description: Initialize a harness-oriented documentation system for a project. Scaffolds `docs/` subfolders (architecture, analysis, decisions, processes, exec-plans, references, generated, tickets), a master catalog at `docs/README.md`, `docs/PLANS.md` as the ExecPlan spec, templates, a seeded `docs/processes/harness.md` operating manual, eight harness ADRs identified by slug, `dev-setup.md`, `tech-debt-tracker.md`, and repo-root anchors (`AGENTS.md`, `ARCHITECTURE.md`, `SECURITY.md`) encoding the operating principle, session bootstrap, and phase gates. Use this skill when the user invokes /init-docs, asks to "set up docs", "initialize documentation structure", "scaffold docs", "set up a harness", "add a harness for AI agents", or wants to bootstrap an AI-harness documentation system for a project. Accepts an optional domain description to adapt tag vocabulary; if omitted, scans the project to infer tags automatically.
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
line changelog heading key, e.g. `2026-05-27.002`). Running the skill
on a stale repo applies pending changelog entries.

## How to update this skill

Every change to files under `assets/` or to `SKILL.md` MUST be
accompanied by a new entry in `CHANGELOG.md` with a heading key dated
today. The git pre-commit hook (`.githooks/pre-commit`) enforces this.

Ritual:

1. Edit the asset(s) or SKILL.md.
2. Add a `## YYYY-MM-DD.NNN — <feature name>` entry in `CHANGELOG.md`
   following the entry shape documented at the top of that file.
   `NNN` is the same-day sequence number; use the next unused number
   for that date.
   The "How to apply" block must be **stack-neutral** and
   **idempotent** (check-then-act). Quarantine stack-specific
   material to the optional "Stack-specific notes" block.
3. Test with a retrofitted repo: pick one scaffolded repo whose
   `.harness-version` is behind the new entry, run the skill,
   verify the entry applies idempotently and advances the marker.
4. Commit. The pre-commit hook refuses if step 2 is missing.

**Hard-constraint addition rule.** A new MUST / MUST NOT bullet in
`assets/AGENTS.md` § Hard constraints requires a backing ADR in the
*same* changelog entry. The citation in the bullet must point at that
ADR (or at an existing § in `AGENTS.md` / `docs/processes/`). A
loud-labelled bullet without a citation is malformed — audit mode
will warn about it (see "Audit mode procedure" → citation check).

Bypass for exceptional commits (typos, experiments, bootstrap):

    SKILL_CHANGELOG_BYPASS="<reason>" git commit ...

## Modes of operation

On invocation, the skill first determines mode from the target
repo's state:

| State | Mode | Action |
|---|---|---|
| No `docs/`, no `.harness-version`, no conflicts | **Scaffold** | Steps 1–16 below; final step writes `.harness-version` to the changelog head key |
| `.harness-version` present and behind changelog head | **Audit** | Skip scaffold; run the audit procedure (see "Audit mode" below) |
| `.harness-version` present and = changelog head key | **Up-to-date** | No-op; report "harness version <key> is current" |
| No `.harness-version` but `docs/` exists from a prior scaffold | **Upgrade + audit** | Run Step 1 (upgrade path, fill missing files), set `.harness-version` to the pre-changelog sentinel `2026-04-19`, then audit |
| Custom / conflicting layout | **Custom** | Step 1's "Anything else exists" branch; prompt skip/overwrite/abort |

Mode detection happens before any files are written.

## Step 1 — Check what already exists

Before creating anything, inspect the project root. List every file
and directory the skill would write:

- Repo root: `AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `SECURITY.md`.
- `docs/`: `README.md`, `PLANS.md`, `FEATURES.md`, `tech-debt-tracker.md`.
- `docs/` subfolders: `analysis/`, `architecture/`, `decisions/`,
  `exec-plans/active/`, `exec-plans/completed/`, `generated/`,
  `processes/`, `references/`, `tickets/`.
- Templates: `docs/analysis/_template.md`, `docs/exec-plans/_template.md`.
- Seeded docs: `docs/processes/harness.md`, `docs/processes/dev-setup.md`,
  `docs/processes/model-policy.md`,
  `docs/processes/initialization-checklist.md`,
  `docs/processes/cold-start-test.md`,
  eight harness ADRs in `docs/decisions/` identified by slug:
  `harness-design`, `session-exit`, `evaluator-gate`, `fleet-model-policy`,
  `hard-constraints`, `pre-approval-critic-gate`, `harness-validators`,
  `adr-slug-canonical` (filenames are `<slug>.md` — see Step 13),
  `docs/references/README.md`,
  `docs/generated/README.md`.
- Subagent configs: `.claude/agents/harness-analyst.md`,
  `.claude/agents/harness-planner.md`.
- Critic hook: `.claude/hooks/harness-planner-critic-hook.mjs` (tracked
  in git) and the SubagentStop entry merged into
  `.claude/settings.local.json` (gitignored, per-contributor).
- Covers-hook reference: `.claude/hooks/verify-covers-hook.sh` (tracked
  in git; activation opt-in via `.claude/settings.local.json`).
- Harness validators: `scripts/harness/check_harness_structure.py`,
  `scripts/harness/garbage_collect_docs.py`,
  `scripts/harness/sweep_adr_refs.py`,
  `scripts/harness/_canonical_manifest.py` (tracked in git;
  stack-specific wiring deferred to `docs/processes/dev-setup.md`).

First, read `.harness-version` at the repo root if it exists. This
determines the mode (see "Modes of operation" above). If the marker
equals the changelog head key, stop and report "up to date." If the
marker is behind the head in changelog file order, skip to the "Audit
mode" section — the scaffold steps below do not apply.

If `.harness-version` is absent, proceed with the remaining cases:

- **Fresh project** — nothing conflicts: proceed without prompting to
  scaffold steps 2–16.
- **Older init-docs output** — older `docs/` layout without
  `exec-plans/`, `references/`, `generated/`, `PLANS.md`,
  `tech-debt-tracker.md`, `harness.md`, or ADR harness-design, and/or
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
    head key (the repo is now current).
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

## Step 3a — Ensure local generated artifacts are ignored

Ensure the repo-root `.gitignore` exists and contains these entries:

```
.claude/settings.local.json
.claude/worktrees/
.claude/memory/
__pycache__/
**/__pycache__/
*.py[cod]
```

Append only missing entries. Do not remove or reorder existing ignore
rules. These are local/generated artifacts; they are never harness
knowledge.

## Step 4 — Write the analysis template

Copy `assets/analysis-template.md` to `docs/analysis/_template.md`.
It references `docs/processes/harness.md` (created in Step 7).

## Step 5 — Write the exec-plan template

Copy `assets/exec-plan-template.md` to `docs/exec-plans/_template.md`.
The template has 13 required sections matching `docs/PLANS.md`
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
hook, common commands, start command). Flag it in the Step 18 report
as "needs filling".

## Step 8a — Write the model policy

Copy `assets/model-policy.md` to `docs/processes/model-policy.md`
verbatim. No substitutions — the policy is fleet-wide.

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

## Step 11a — Write the initialization checklist

Copy `assets/initialization-checklist.md` to
`docs/processes/initialization-checklist.md`. No placeholders.
Documents the bootstrap-contract property that Step 18 verifies as
its closing section.

## Step 11b — Write the cold-start test

Copy `assets/cold-start-test.md` to
`docs/processes/cold-start-test.md`. No placeholders. Documents the
quarterly legibility ritual; output lands in
`docs/generated/cold-start-test.md` (rolling log, created on first
run — not pre-created by the skill).

## Step 12 — Write the feature ledger

Copy `assets/FEATURES.md` to `docs/FEATURES.md`. Empty ledger with the
state legend, verify-convention legend, and a pointer to
`docs/PLANS.md` for the `features:` frontmatter contract that ExecPlans
must satisfy. Rows are added by the user or the agent during phase 1 of
the first relevant brief — not during scaffolding. Empty is the correct
initial state.

## Step 13 — Seed harness ADRs

The harness ships eight ADRs identified by `id:` slug. Filenames are
`<slug>.md` — no numeric prefix. See ADR adr-slug-canonical for the
convention.

| Slug | Asset filename |
|---|---|
| `harness-design` | `assets/harness-design.md` |
| `session-exit` | `assets/session-exit.md` |
| `evaluator-gate` | `assets/evaluator-gate.md` |
| `fleet-model-policy` | `assets/fleet-model-policy.md` |
| `hard-constraints` | `assets/hard-constraints.md` |
| `pre-approval-critic-gate` | `assets/pre-approval-critic-gate.md` |
| `harness-validators` | `assets/harness-validators.md` |
| `adr-slug-canonical` | `assets/adr-slug-canonical.md` |

### Idempotency rule

For each harness slug, check whether `docs/decisions/<slug>.md` exists
in the target repo:

- **Absent:** copy the asset to `docs/decisions/<slug>.md`.
- **Present with matching `id:`:** skip (idempotent).
- **Present with different `id:` or otherwise unrelated content:** halt
  with a conflict report listing the offending slug, the existing file
  path, and the harness asset that would have been written. Do not
  proceed until the user resolves the collision.

No number assignment, no URL rewriting, no `legacy_numbers:` bookkeeping
— every shipped asset already references peer ADRs by
`decisions/<slug>.md`, which is the path it lands at.

### Placeholder substitution (`harness-design` only)

Two placeholders need filling in the `harness-design` ADR:

- `{{PROJECT_CONTEXT}}` — one paragraph describing the project: team
  size, what the repo does, how AI is being used today. If this isn't
  known from the brief, leave the placeholder verbatim and flag it in
  the Step 18 report so the user can fill it in.
- `{{V1_CONTENTS}}` — project-specific list of what ships in v1. The
  template provides a generic starter list (including `docs/PLANS.md`
  as item 7 and `AGENTS.md` in item 5). Adjust the language/tooling
  entry (pre-commit hook) to match the project's stack if detectable
  from Step 2, otherwise leave the placeholder.

The Fowler/OpenAI guides-vs-sensors mental model, the phase-gate rule,
the plan-format reference to `PLANS.md`, the agent-entry-point note
about `AGENTS.md` + symlink, and the steering-loop cadence are reusable
across any project and stay verbatim.

## Step 14 — Write `docs/README.md`

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
"skip", leave it alone and emit a note in the Step 18 report pointing
out which sections (Repo-root anchors, Exec plans, Generated, Tech
debt) need to be added manually. Show the user the exact lines to
append.

## Step 15 — Write `AGENTS.md` and create the `CLAUDE.md` symlink

Copy `assets/AGENTS.md` to the project root. The file is generic and
does not require substitution.

Then create `CLAUDE.md` as a symlink to `AGENTS.md`:

```
ln -s AGENTS.md CLAUDE.md
```

On Windows / non-symlink filesystems where `ln` fails, fall back to
copying `AGENTS.md` to `CLAUDE.md` and emit a warning in the Step 18
report: "symlink not supported on this filesystem; `CLAUDE.md` copied
instead — keep the two files in sync manually, or re-run on a
Unix-like filesystem".

If either file already exists and the user chose "upgrade" or "skip",
leave it alone and emit a diff in the Step 18 report showing what the
harness expects — operating principle, session bootstrap, phase gates,
output-routing table — so the user can merge it manually.

## Step 16 — Write `ARCHITECTURE.md` and `SECURITY.md`

Copy `assets/ARCHITECTURE.md` and `assets/SECURITY.md` to the project
root. Both are language-agnostic skeletons — every section is a
prompt ("*Fill in …*") the user must resolve. Do not try to pre-fill
from code scanning; the point of these files is forcing the user to
capture context that only they know.

Flag both files in the Step 18 report as "needs filling".

## Step 16a — Write subagent configs

Copy `assets/harness-analyst.md` and `assets/harness-planner.md` to
`.claude/agents/` in the project root. Create the directory if absent.
Both files are stack-neutral; no substitution.

These configure the typed design subagents the orchestrator delegates
to in Phase 2 (analysis synthesis) and Phase 5 (all ExecPlans) per
`docs/processes/harness.md` and `AGENTS.md` § Phase gates.

## Step 16b — Wire the harness-planner critic hook

Every ExecPlan must pass through the pre-approval critic before the
lead approves it (ADR pre-approval-critic-gate). The `codex:adversarial-review` slash
command sets `disable-model-invocation: true` in the codex-plugin-cc
package, so the orchestrator **cannot** invoke it from inside a turn.
The hook is the only mechanical path to the critic. The same
restriction applies to `/codex:review` and `/codex:result`; the
Completion Evaluator (Step 20 in model-policy) and on-demand diff
sanity (Step 17) reach the underlying companion script through the
orchestrator's own Bash calls — see
`docs/processes/dev-setup.md` § Evaluator convention for the
Evaluator's resolved command shape.

1. Copy `assets/harness-planner-critic-hook.mjs` →
   `.claude/hooks/harness-planner-critic-hook.mjs` in the project
   root. Create `.claude/hooks/` if absent. `chmod +x` the file.
   **Tracked in git** — every contributor gets the script.

2. Merge the contents of `assets/claude-settings-local-fragment.json`
   into the target repo's `.claude/settings.local.json`. Read the
   existing file if present (parse JSON; `{}` if absent), then
   additively merge the `hooks.SubagentStop` entry. **Idempotent**:
   if a SubagentStop entry whose `command` references
   `harness-planner-critic-hook.mjs` is already present, skip. Write
   back with two-space indent. **`.claude/settings.local.json` is
   gitignored** — activation is per-contributor.

3. Verify `.claude/settings.local.json` is covered by the repo's
   `.gitignore` (search for `.claude/settings.local.json` or the
   `.claude/` prefix). If the entry is absent, surface in the Step 18
   report — the user must add it before committing.

Flag in the Step 18 report: "Critic hook script tracked in
`.claude/hooks/`; activation entry in gitignored
`.claude/settings.local.json`. Requires `codex-plugin-cc` installed
locally; without it the hook writes a `BLOCKED: codex-plugin-cc not
installed` placeholder into the plan's `## Pre-approval critic
transcript` section instead of a verdict. The empty-section gate
(PLANS.md) means the lead won't approve until the section contains a
non-BLOCKED verdict."

The hook fires only on `subagent_type === "harness-planner"`. It runs
`codex-companion.mjs adversarial-review` **synchronously** (no
`--background`), captures stdout, and writes the verdict directly into
the plan's `## Pre-approval critic transcript` section using
ADR pre-approval-critic-gate's run-block format. The agent's turn pauses for the duration
of the critic run (typically 30–90s, hard-capped at 10 minutes). On
any failure mode (plugin missing, codex crash, timeout, non-zero exit,
empty stdout), the hook writes a `BLOCKED: <reason>` placeholder into
the same section so the lead's approval gate fires loudly rather than
silently.

## Step 16c — Ship the covers: hook reference

Copy `assets/verify-covers-hook.sh` → `.claude/hooks/verify-covers-hook.sh`
in the project root. Create `.claude/hooks/` if absent. `chmod +x` the
file. **Tracked in git** — every contributor gets the script.

Do **not** auto-register it in `.claude/settings.local.json`.
Activation is opt-in and **per-contributor** (gitignored
`.claude/settings.local.json`, not the tracked `.claude/settings.json`)
— see § Notes on scope → Config-file precedence below. The user wires
it into the PreToolUse hook list per the install snippet in
`docs/processes/dev-setup.md` § Pre-tool-use hook (covers:
enforcement).

This is the reference implementation of the in-execution half of the
covers: hard constraint (`AGENTS.md` § Hard constraints). The
pre-commit plan-coverage sensor is still the post-execution gate; this
hook only catches violations earlier, at the tool call.

The script is stack-neutral (bash + jq). Repos that prefer a
stack-native version (Node, Python, Go) may swap the script — the
contract documented in `dev-setup.md` is what matters, not the
language.

Flag in the Step 18 report: "Covers: hook script tracked in
`.claude/hooks/verify-covers-hook.sh`. Activation is opt-in — see
`docs/processes/dev-setup.md` § Pre-tool-use hook for the
`.claude/settings.json` snippet."

## Step 16d — Ship the harness validators

Copy `assets/scripts/check_harness_structure.py`,
`assets/scripts/garbage_collect_docs.py`,
`assets/scripts/sweep_adr_refs.py`, and
`assets/scripts/_canonical_manifest.py` to `scripts/harness/` in the
project root. Create `scripts/harness/` if absent. `chmod +x` the three
CLI scripts (not `_canonical_manifest.py` — it is an importable
module, not an executable).

**Tracked in git.** Every contributor gets the validators on
checkout. The scripts are stdlib-only (Python ≥ 3.9) and self-contain
— `_canonical_manifest.py` is the single source of truth for the
canonical-file set (including `ADR_SLUGS_REQUIRED`), the frontmatter
subset, required references, and text-scan roots.

`sweep_adr_refs.py` is a one-way legacy-migration tool. It exists for
repos upgrading from the pre-slug-canonical harness (numbered
`NNN-<slug>.md` filenames with `ADR NNN` prose refs). On a fresh
slug-only scaffold it has nothing to migrate and is a no-op. Not part
of the scaffold pipeline.

Do **not** wire any of these into pre-commit / Makefile / Task / CI —
that is stack-specific and lives in `docs/processes/dev-setup.md`
§ Harness validators. Example snippets ship in
`docs/decisions/harness-validators.md` § Appendix, marked explicitly
as example-only.

Flag in the Step 18 report: "Harness validators installed at
`scripts/harness/`. Requires `python3 ≥ 3.9` on `PATH`. Wiring
(pre-commit / CI / Makefile) is stack-specific — see
`docs/processes/dev-setup.md` § Harness validators."

## Step 17 — Write `.harness-version`

Write a single line to `.harness-version` at the repo root. The value
is the heading key of the first entry in this skill's `CHANGELOG.md`
(the "changelog head key", e.g. `2026-05-27.002`). Do **not** use
today's date by itself — a date-only marker cannot distinguish
multiple same-day entries.

For upgrade-mode runs (the "Older init-docs output" branch of Step 1),
write the pre-changelog sentinel `2026-04-19` instead, so the
subsequent audit picks up every changelog entry.

## Audit mode procedure

This runs in place of the scaffold when `.harness-version` is present
and behind the changelog head.

1. Read `.harness-version` (the repo marker).
2. Read this skill's `CHANGELOG.md`. Entries are ordered newest-first
   by file position. If the marker is a legacy date-only value
   (`YYYY-MM-DD`), resolve it to the last entry that old date-only
   version could have meant. For the migration date specifically,
   `2026-05-27` resolves to `2026-05-27.001`, so the
   `2026-05-27.002` cursor-migration entry remains pending. For other
   dates, resolve to the newest entry in the historical same-date block
   (for example, `2026-05-25` resolves to `2026-05-25.004`). If no
   entry matches, treat the marker as older than all entries. Enumerate
   entries above the resolved marker. Process them oldest-first
   (bottom-up in the pending slice).
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
      `.harness-version` to that entry's heading key. This is incremental —
      one entry at a time, persisted immediately. A later failure
      does not roll back earlier successes.
4. When all pending entries are applied, report: "harness version
   advanced from <old> to <new>; N entries applied." If any entry
   failed or conflicted, report which one and leave the marker at
   the last successful entry's heading key.

5. **Hard-constraint citation check (warn-only).** After step 4,
   re-read the target repo's `AGENTS.md` § Hard constraints (MUST /
   MUST NOT) block, if present. For each bullet that begins with
   `**MUST**` or `**MUST NOT**`, verify the bullet body contains
   either an `ADR NNN` reference or a `§ <section name>` reference.
   For each bullet missing both, emit a one-line warning in the audit
   report: `WARN: malformed hard-constraint bullet — "<first 60 chars
   of bullet>" lacks ADR/§ citation`. **Do not** halt the audit or
   roll back the marker — citation drift is documentation hygiene,
   not a contract violation. If the Hard constraints block is absent
   entirely (older harness without ADR hard-constraints applied), skip silently —
   the citation check is conditional on the block existing.

6. **Section-order check for AGENTS.md reorders.** When a changelog
   entry includes an AGENTS.md heading reorder step (e.g. ADR hard-constraints'
   step 4), do the following *before* writing:
   a. Parse the current top-level heading order in the target
      repo's `AGENTS.md`.
   b. Compare against the locked order declared in the entry's
      "How to apply".
   c. If they already match, skip the reorder silently (idempotent).
   d. If they differ, print both orders side-by-side, write
      `AGENTS.md.bak` as a safety copy, and require explicit user
      `y/n` before applying. On `n`, skip the reorder and emit it
      as a "Needs manual merge" item in the audit summary — but
      still advance the marker (the reorder is the only step
      pending; the rest of the entry already applied).

**Never** auto-apply "replacing" entries, never merge conflicts
autonomously, never silently skip steps.

## Step 18 — Report what was created

List every file and directory created or skipped. Use four sections,
plus a closing **Bootstrap contract** verdict:

- **Created** — new files, with paths. Include `.harness-version`
  with its value. Note `docs/FEATURES.md` as an empty ledger by design
  (rows are added during phase 1 of the first brief — *not* a
  needs-filling file). List each harness ADR by `id:` slug with its
  filename (e.g., `ADR session-exit → docs/decisions/session-exit.md`),
  the fleet model policy at `docs/processes/model-policy.md`, the
  initialization checklist at
  `docs/processes/initialization-checklist.md`, the cold-start test at
  `docs/processes/cold-start-test.md`, and the four harness validators
  at `scripts/harness/`.
- **Skipped (already existed)** — existing files not touched.
- **Needs filling** — files written with placeholder content the user
  must resolve. At minimum: `ARCHITECTURE.md`, `SECURITY.md`,
  `docs/processes/dev-setup.md` (including its "Feature verification
  convention" section, the independence assertion under "Evaluator
  convention", and the wiring contract under "Harness validators"),
  and any `{{PLACEHOLDER}}` remaining in ADR harness-design. Repos may also want
  to substitute `{{REPO_NAME}}` in the `owner:` frontmatter field of
  every canonical markdown file — left as a literal placeholder by
  design so the choice is explicit.
- **Needs manual merge** — only if the user chose "upgrade" or "skip"
  and a pre-existing file would have been updated. Show the exact
  content to merge.

### Bootstrap contract (closing verdict)

After the four sections above, print a Bootstrap-contract verdict
per [`docs/processes/initialization-checklist.md`](this file's
runtime path in the target repo). Verify each of the four conditions
and emit one line per condition. Two-level pass:

- **`[✓ surface] [✓ ready]`** — artifact exists and carries
  non-placeholder content.
- **`[✓ surface] [⚠ placeholder]`** — artifact exists but contains
  scaffold-default markers (`*Fill in:*`, `<command>`,
  `{{PLACEHOLDER}}`). Not a skill bug; the user has not yet filled
  in stack-specific commands.
- **`[✗ surface missing]`** — artifact does not exist where the
  contract says it should. *This is a skill bug.* Print loudly. Do
  NOT block exit; the user has on-disk files worth keeping.

Verification rules per condition:

| # | Condition | Surface check | Populated check |
|---|---|---|---|
| 1 | Can start | `docs/processes/dev-setup.md` exists; `## Common commands` and `## Running locally` headings exist | The Build and Run-locally table cells are not `<command>`; the § Running locally body contains no `*Fill in:*` |
| 2 | Can test | `docs/processes/dev-setup.md` exists; `## Common commands` and `## Feature verification convention` headings exist | The Run-tests table cell is not `<command>`; § Feature verification convention body contains no `*Fill in:*` |
| 3 | Can see progress | `docs/FEATURES.md` + `docs/exec-plans/active/` (folder) + `docs/README.md` exist; `FEATURES.md` carries `## Not started`, `## Active`, `## Blocked`, `## Failing`, `## Passing` headings | n/a — empty is legitimate; no placeholder state |
| 4 | Can pick up next steps | `docs/FEATURES.md`, `docs/exec-plans/active/`, `docs/tech-debt-tracker.md` exist and are readable | n/a — empty is legitimate; no placeholder state |

Example output (fresh scaffold):

    Bootstrap contract:
      [✓ surface] [⚠ placeholder] can start         → dev-setup.md § Common commands (Build, Run locally)
      [✓ surface] [⚠ placeholder] can test          → dev-setup.md § Common commands (Run tests) + Feature verification convention
      [✓ surface] [✓ ready]       can see progress  → FEATURES.md + exec-plans/active/ + docs/README.md
      [✓ surface] [✓ ready]       can pick up next  → FEATURES.md § Active|Failing + exec-plans/active/ + tech-debt-tracker.md

    Initialization complete. 2 placeholders to fill before this repo is operable:
      - dev-setup.md § Common commands
      - dev-setup.md § Feature verification convention

The verdict runs at the end of fresh scaffold, audit-mode runs
(after the marker advances), and up-to-date no-op runs. It is the
point — the verdict tells the agent whether the bootstrap contract is
satisfied right now, not whether anything changed.

For audit-mode runs, replace the four sections above with a single
summary (which entries applied, which conflicted, the new marker
value), then print the Bootstrap-contract verdict.

If tags were inferred from the project (Step 2), briefly explain the
signals used so the user can correct wrong inferences.

If the `CLAUDE.md` symlink fell back to a copy (Step 15), call it out.

## Notes on scope

- **No pre-commit hooks are installed.** Hooks are language-specific
  and belong in a separate skill. The user fills in `dev-setup.md`
  with their stack's hook entrypoint; installing it is a manual or
  separate-skill step.
- **Sensor documentation is included; pre-commit sensor scripts are
  not.** `AGENTS.md`, `PLANS.md`, `harness.md`, and `dev-setup.md` all
  describe the plan-coverage sensor pattern: a pre-commit check that
  reads each approved plan's `covers:` frontmatter and blocks any
  staged source file not covered. The actual pre-commit script
  (`scripts/verify-plan-coverage.sh` or equivalent) is stack-specific
  and must be implemented after scaffolding. The Go reference
  implementation lives in the ms-search repo at ADR evaluator-gate.
- **The PreToolUse covers: hook IS shipped** as a reference (Step
  16c). It is the in-execution counterpart to the pre-commit sensor —
  earlier feedback loop, same `covers:` contract. Activation is
  opt-in; the script is stack-neutral bash + jq and may be swapped.
- **`ARCHITECTURE.md` and `SECURITY.md` are not pre-filled from code
  scanning.** They intentionally force the user to capture project
  context that scanning can't infer (why the system is shaped this
  way, what the threat model actually is).
- **The skill never modifies source code** — only documentation and
  root-level markdown files.
- **Config-file precedence: per-contributor by default.** When a
  decision arises between `.claude/settings.json` (per-repo, tracked
  in git) and `.claude/settings.local.json` (per-contributor,
  gitignored), the latter is chosen. Activation entries for harness
  hooks (auto-critic SubagentStop, covers: PreToolUse, and any future
  hooks) land in `.claude/settings.local.json` so each contributor
  opts in explicitly. The hook *scripts* themselves are tracked in
  git under `.claude/hooks/`; only the activation entry is
  per-contributor. Reason: shared tracked activation forces hook
  behaviour on every contributor (and CI), which is a
  blast-radius decision the harness should not make autonomously.
