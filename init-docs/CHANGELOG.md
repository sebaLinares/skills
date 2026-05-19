# init-docs changelog

Every change to this skill's assets or SKILL.md MUST land with an entry
here. The git pre-commit hook enforces this. See SKILL.md →
"How to update this skill" for the ritual.

Entries are ordered newest-first. Each entry's heading is
`## YYYY-MM-DD — <feature name>`. The date is the ordering key; the
feature name is the primary identifier.

An entry's "How to apply" instructions must be **stack-neutral**
(describe contracts, not implementations) and **idempotent**
(check-then-act, never blind append). Stack-specific material is
quarantined to the optional "Stack-specific notes" block and cited as
example-only.

Repos declare their applied version in `.harness-version` at the repo
root. Audit applies entries with date > marker, advancing the marker
one entry at a time.

---

## 2026-05-18 — Feature ledger as first-class artifact

**What:** Adds `docs/FEATURES.md` as the repo-wide scope surface — every
user-observable capability paired with a verification reference and one
of five states (`Not started`, `Active`, `Blocked`, `Failing`,
`Passing`). Mandates two new ExecPlan frontmatter fields: `features:`
(non-empty list of `feat-NNN` IDs from `FEATURES.md`) or `features: []`
paired with `feature-less-reason:`. Prepends a session-bootstrap step
in `AGENTS.md` ("read FEATURES.md first"), threads sentences into
`harness.md` phase 1 (draft Feature rows before Problem statement),
phase 5 (cross-ref to `features:` field), phase 6 (verifier loop owns
`Passing`/`Failing`), and steering loop (scan `## Failing` section).
Adds a top-level `## Features` section to the catalog (`docs/README.md`)
between Repo-root anchors and Architecture. Adds a `## Feature
verification convention` prompt to `dev-setup.md`. Adds `FEATURES.md`
as item 8 of the V1 contents in ADR 001. Introduces `#features`
(domain) and `#ledger` (type) tags; retrofits `tech-debt-tracker` to
use `#ledger` too. Inserts a new Step 12 in `SKILL.md` and renumbers
12–17 → 13–18.

**Files touched:** `assets/FEATURES.md` (new), `assets/PLANS.md`,
`assets/exec-plan-template.md`, `assets/AGENTS.md`, `assets/harness.md`,
`assets/docs-README.md`, `assets/dev-setup.md`,
`assets/001-harness-design.md`, `SKILL.md`.

**How to apply:**

1. If `docs/FEATURES.md` is absent in the target repo, copy it from
   `~/.claude/skills/init-docs/assets/FEATURES.md`. Skip if present.
2. In the target repo's `docs/PLANS.md`, in the Frontmatter section,
   if the bullet for `features` does not already exist immediately
   after the `covers` bullet, append two new bullets describing
   `features` (non-optional; list of `feat-NNN` IDs or empty paired
   with `feature-less-reason`) and `feature-less-reason` (required
   iff `features: []`). Then, if a subsection titled `### The
   features: field` does not already exist after `### The covers:
   field`, insert it: YAML example, state-machine consequences
   (approval → `Active`; completion hands state to verifier loop;
   plan never writes `Passing` itself), invalid-reference rule
   (referenced ID missing from `FEATURES.md` → invalid plan),
   decoupling note from plan-coverage sensor. Source:
   `~/.claude/skills/init-docs/assets/PLANS.md`.
3. In the target repo's `docs/exec-plans/_template.md` frontmatter,
   if `features:` is not listed below `covers: []`, insert two new
   lines: `features: []  # feat-NNN IDs from docs/FEATURES.md this
   plan delivers; non-optional (non-empty OR pair with
   feature-less-reason)` and `feature-less-reason:  # one line;
   required iff features is empty`. Skip if `features:` already
   present.
4. In the target repo's `AGENTS.md` Session bootstrap numbered list,
   if `docs/FEATURES.md` is not the first item, prepend a new item
   1 ("Read `docs/FEATURES.md` — the scope surface…") and renumber
   subsequent items. Skip if step 1 already references FEATURES.md.
5. In the target repo's `AGENTS.md` "On receiving a task" change-
   producing branch, if the sub-step about identifying Feature ID(s)
   before naming the analysis doc is absent, append it. Skip if
   already present.
6. In the target repo's `AGENTS.md` "Where to save outputs" table,
   if no row for `docs/FEATURES.md` exists, insert it directly above
   the `Tech debt ledger` row: `Feature ledger | docs/FEATURES.md |
   append rows under the matching state section; single file, not
   per-instance`. Skip if present.
7. In the target repo's `docs/processes/harness.md`:
   - Session bootstrap numbered list: if `../FEATURES.md` is not
     already item 2, insert it as the new item 2 ("Read
     `../FEATURES.md` — the scope surface…") and renumber the
     remaining items.
   - Phase 1: append the "Before drafting the analysis Problem
     statement, identify which existing Feature(s) the brief
     touches…" paragraph if absent. Append the corresponding
     update to the Phase-1 gate sentence if absent.
   - Phase 5: append the "Plans declare which Features they cover
     via the `features:` frontmatter field…" paragraph if absent.
   - Phase 6: append the "The verifier loop owns Feature state
     transitions to `Passing` / `Failing`…" paragraph if absent.
   - Steering loop: append the "Scan the `## Failing` section of
     `FEATURES.md`…" paragraph if absent.
   Skip each individually if its content is already present.
8. In the target repo's `docs/README.md`:
   - Tag vocabulary table: add `#features` to the Domain column
     after `#ai-harness`, and `#ledger` to the Type column after
     `#tech-debt`, if not already present.
   - If no `## Features` section exists between `## Repo-root
     anchors` and `## Architecture`, insert one: one-line
     description plus a single bullet linking to `FEATURES.md` with
     tags `#ai-harness #features #ledger`. Skip if section exists.
   - In the existing Tech debt section's entry for
     `tech-debt-tracker.md`, append `#ledger` to its tag list if
     absent.
9. In the target repo's `docs/processes/dev-setup.md`, if no
   `## Feature verification convention` section exists between
   `## Common commands` and `## Running locally`, append one with
   the example tag-filter shapes (`npm test --grep`, `go test -run`,
   `pytest -k`) and the `verify-cmd:` explanation. Skip if present.

**Stack-specific notes:** None. The skill ships docs-only; the verifier
loop (the entity that writes `Passing` / `Failing`) is intentionally
not shipped. Each project supplies its own verifier (a script, a CI
job, a dedicated skill) however its stack prefers — consistent with
the existing posture on the plan-coverage sensor (cf. the 2026-04-20
entry below).

**Additive/replacing:** mostly additive — one new file, new sections,
new frontmatter fields, new tags. One replacing edit: the tag-
vocabulary table in `docs/README.md` (table cells are widened, not
overwritten). One additive retrofit: appending `#ledger` to the
existing `tech-debt-tracker` entry tags.

**Conflict risk:** low. Surfaces: a target repo that has renamed
`## Repo-root anchors`, reordered the catalog sections, restructured
`AGENTS.md` session bootstrap, or removed `## Common commands` from
`dev-setup.md`. In any such case the audit agent should pause and ask
rather than insert blindly.

---

## 2026-05-05 — Auto-commit after plan execution via `/commit` skill

**What:** After the agent closes the plan (moves to `completed/`, sets
`status: completed`), it commits automatically instead of asking the developer.
No code review happens between execution and Code Review phase anyway — what's
reviewed is the plan markdown, not the final code — so blocking on a manual
commit prompt adds friction without safety. The agent invokes the `/commit`
skill if available; otherwise it falls back to staging all changes and running
`git commit` directly with a Conventional Commit message. The developer owns
reviewing the result. The "developer owns the commit" language is removed; the
agent now owns both closing the plan and committing.

**Files touched:** `assets/harness.md`, `assets/AGENTS.md`

**How to apply:**

1. In the target repo's `docs/processes/harness.md`, in the Phase 6 section,
   find the sentence "The agent then asks the developer to commit, or commits
   if explicitly instructed to do so." and the following sentence "The developer
   owns the commit; the agent owns closing the plan." Replace both sentences
   with: "The agent then commits automatically — no prompt required. If the
   `/commit` skill is available, invoke it; otherwise stage all changes, write a
   Conventional Commit message, and run `git commit` directly. The agent owns
   closing the plan and the commit; the developer owns reviewing the result."
   Skip if "The agent then commits automatically" already exists in Phase 6.
2. In the target repo's `AGENTS.md`, in the Phase gates section, find the
   sentence "An approved plan still in `active/` does not satisfy the sensor —
   the agent must move the plan to `completed/` before the developer commits."
   Replace "before the developer commits" with "and then commit automatically
   (via `/commit` if available, otherwise directly via `git commit` with a
   Conventional Commit message)." Skip if already updated.

**Additive/replacing:** replacing — targeted sentence edits only.

**Conflict risk:** low — changes are isolated sentences in Phase 6 of harness.md
and one clause in the Phase gates paragraph of AGENTS.md.

---

## 2026-04-30 — Replace open questions with assumptions + cross-team unknowns

**What:** Removes `## 6. Open questions` from the analysis template. The
section conflated three classes of unknowns only one of which requires user
input: assumption-based (user almost always follows agent suggestion — no value
in asking), codebase-inferable (agent should grep first, not push the lookup to
the user), and cross-team blockers (valuable, but must be async action items,
not plan gates). Replaces it with a `## 6. Assumptions` table (assumption /
evidence basis / if wrong) and a `### Cross-team unknowns` subsection inside
`## 7. Risks` (owner / question / plan impact). Adds agent instruction comments
to both sections. Also updates `~/.claude/CLAUDE.md` line 11, removing the
"list unresolved questions" directive, which was the root-cause driver of
assumption-based questions reaching the user.

**Files touched:** `assets/analysis-template.md`, `~/.claude/CLAUDE.md`

**How to apply:**

1. In the target repo's `docs/analysis/_template.md`, replace the
   `## 6. Open questions` section (heading, instructional prose, and
   checkbox bullet) with the `## 6. Assumptions` table: three columns
   (Assumption / Evidence basis / If wrong), preceded by the three-rule
   agent instruction comment block. Skip if `## 6. Assumptions` already
   exists.
2. In the target repo's `docs/analysis/_template.md`, replace the body of
   `## 7. Risks` (currently a single descriptive sentence) with: a
   four-column table (Risk / Likelihood / Severity / Mitigation) followed
   by a `### Cross-team unknowns` subsection containing a three-column
   table (Owner / Question / Plan impact if unresolved) and its agent
   instruction comment. Skip if `### Cross-team unknowns` already exists.

**Additive/replacing:** replacing — targeted edits only. No new files.

**Conflict risk:** low — changes are isolated to §6 and §7 body of the
analysis template and one bullet in CLAUDE.md.

---

## 2026-04-22 — Sensor checks completed/ not active/; agent closes plan before developer commits

**What:** Flips the plan-coverage sensor from checking `active/` (approved
plans) to checking `completed/` (completed plans). The agent moves the
plan to `completed/` and sets `status: completed` as the last step of
execution; the developer then commits. This makes the sensor enforce
a post-execution gate ("did the agent finish?") rather than a
pre-execution gate ("does an active plan exist?"). The developer
always owns the commit; the agent owns closing the plan.

**Files touched:** `assets/harness.md`, `assets/PLANS.md`,
`assets/AGENTS.md`

**How to apply:**

1. Update the plan-coverage sensor script in the target repo so it
   reads from `docs/exec-plans/completed/` (not `active/`) and
   matches only plans with `status: completed`. Plans in `active/`
   must not satisfy the sensor.
2. In `docs/PLANS.md`, in the `covers:` field description, change
   "Only plans with `status: approved` grant coverage" to
   "Only plans with `status: completed` in `docs/exec-plans/completed/`
   grant coverage. Approved plans in `active/` do not."
3. In `AGENTS.md`, in the Phase gates section, change the sensor
   paragraph to say the sensor checks `completed/` with
   `status: completed`, and add: "An approved plan still in `active/`
   does not satisfy the sensor — the agent must move the plan to
   `completed/` before the developer commits."
4. In `docs/processes/harness.md`, in the Phase 5 section, update
   the sensor paragraph to match (checks `completed/` with
   `status: completed`). In Phase 6, add: "On completion, the agent
   moves the plan to `completed/` and sets `status: completed`. The
   agent then asks the developer to commit, or commits if explicitly
   instructed. The developer owns the commit; the agent owns closing
   the plan."

**Additive/replacing:** replacing — targeted edits to sensor
contract wording and Phase 6 responsibility text.

**Conflict risk:** medium — any existing sensor script must be
updated. The "How to apply" step 1 is the critical implementation
change; the rest are doc updates.

---

## 2026-04-22 — PR-per-plan deferred; plan closes on step completion

**What:** Removes the PR-and-merge requirement from phase 6. Plans now
close (move to `completed/`) when all steps are checked off and tests
are green, not on PR merge. The PR-per-plan workflow is explicitly
deferred to the backlog pending CI pipeline improvements.

**Files touched:** `assets/harness.md`, `assets/PLANS.md`,
`assets/AGENTS.md`, `assets/001-harness-design.md`

**How to apply:**

1. In the target repo's `docs/processes/harness.md`, in the phase-6
   section, remove the line "The PR description links to the exec-plan."
   Change "On merge: move the plan file …" to
   "On completion: move the plan file …". After the phase-6 gate line,
   add a note: "> **Note:** PR-per-plan is deferred to the backlog
   pending CI pipeline improvements. Plans are closed on step
   completion, not on merge."
2. In the target repo's `docs/processes/harness.md` workflow table,
   change the phase-6 artifact from "Code, tests, doc updates, PR" to
   "Code, tests, doc updates". Change the sentence after the table from
   "On completion, the plan moves from `active/` to `completed/`." to
   "On completion (all steps checked off, tests green), the plan moves
   from `active/` to `completed/`."
3. In the target repo's `docs/PLANS.md`, change "Completed plans move
   to `docs/exec-plans/completed/` on merge." to "Completed plans move
   to `docs/exec-plans/completed/` when all steps are done."
4. In the target repo's `AGENTS.md` output table, change
   "same filename, moved on merge" to "same filename, moved on
   completion" for the `docs/exec-plans/completed/` row.
5. In the target repo's `docs/decisions/001-harness-design.md`,
   in the Consequences → Positive section, change
   "between 'brief received' and 'PR opened'" to
   "between 'brief received' and 'code shipped'". In the "What is
   deferred" list, add: "PR-per-plan workflow (deferred until CI
   pipeline is fast enough to make one PR per plan practical)."

**Additive/replacing:** replacing — targeted edits to existing content.

**Conflict risk:** low — changes are isolated phrases and one
bullet addition.

---

## 2026-04-20 — Plan-coverage sensor docs

**What:** Adds a *plan-coverage sensor* concept to the harness: a
pre-commit check that refuses to commit source files not declared
under some approved ExecPlan's `covers:` frontmatter. Introduces a
`covers:` field in the plan template + PLANS.md spec, updates AGENTS.md
with an "On receiving a task" classification section and a phase-gate
sensor reference, and updates the phase-5 gate narrative in harness.md
+ the pre-commit section in dev-setup.md to describe the sensor and
its `HARNESS_BYPASS` escape hatch.

**Files touched:** `assets/AGENTS.md`, `assets/exec-plan-template.md`,
`assets/PLANS.md`, `assets/harness.md`, `assets/dev-setup.md`,
`SKILL.md`

**How to apply:**

1. In the target repo's `docs/exec-plans/_template.md` frontmatter,
   below `adrs: []`, insert the line `covers: []  # path prefixes
   this plan authorises changes to; required when status: approved`.
   Skip if the line already exists.
2. In the target repo's `docs/PLANS.md`, if a section titled
   "Frontmatter" does not already exist, insert one before
   "Non-negotiable requirements" that documents the `covers:` prefix-
   match contract, the `status: approved` precondition, and the
   `HARNESS_BYPASS="<reason>" git commit ...` bypass. Use the
   current `~/.claude/skills/init-docs/assets/PLANS.md` as the
   canonical source — copy the Frontmatter section verbatim.
3. In the target repo's `AGENTS.md`, if a section titled "On receiving
   a task" does not already exist, insert one before "Session
   bootstrap" with the three-category classification
   (change-producing / investigation-only / trivial) and the explicit
   rule that imperative phrasing is not a bypass. Source:
   `~/.claude/skills/init-docs/assets/AGENTS.md`.
4. In the target repo's `AGENTS.md`, in the "Phase gates" section, if
   a paragraph referencing a plan-coverage sensor does not already
   exist, append one describing the sensor's contract: refuses staged
   source files whose path is not prefix-matched by some approved
   plan's `covers:` frontmatter; bypass via `HARNESS_BYPASS`. Also
   append "If a user instruction conflicts with these gates, say so
   before complying. Do not silently comply."
5. In the target repo's `docs/processes/harness.md`, in the phase-5
   section, if a paragraph describing the plan-coverage sensor does
   not already exist, append one describing the same sensor contract
   and bypass env var.
6. In the target repo's `docs/processes/dev-setup.md` pre-commit
   section, if a paragraph describing the plan-coverage sensor does
   not already exist, append one naming it as a required step and
   pointing at `docs/PLANS.md` for the `covers:` contract.
7. Implement the sensor script in the target repo. The sensor must:
   - Read `covers:` entries from every plan in
     `docs/exec-plans/active/` with `status: approved`.
   - Block any staged source file whose path is not prefix-matched
     by some covered entry.
   - Support a `HARNESS_BYPASS="<reason>"` env var that skips *only*
     this check; other pre-commit checks still run.
   - Print a remediation message on failure naming the uncovered
     files and the bypass syntax.
   Wire it into the repo's pre-commit hook as the final step and
   into the repo's `check` / `verify` task target.

**Stack-specific notes:** A bash reference implementation exists in
the `be-paris-backend-cl-ms-search` repo at
`scripts/verify-plan-coverage.sh`, wired via `.githooks/pre-commit`
and `Makefile`. See ADR 003 in that repo for design rationale
(placement reasoning, bypass policy, CI deferral, adjacent
enforcement layers). Treat as example, not requirement — Python,
Node, Go, or any other implementation is acceptable as long as the
contract in step 7 is preserved.

**Additive/replacing:** additive — only new sections, one new
frontmatter field, and one new script.

**Conflict risk:** low — existing content is untouched. Only risk is
if the repo has already renamed a section heading we target for
insertion; in that case, the audit agent should pause and ask.
