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

## 2026-05-21 — Fleet model policy

**What:** Encodes fleet-wide per-step model assignments as
non-negotiable contracts: Sonnet 4.6 high as default orchestrator,
Opus 4.7 xhigh as design subagent (analysis synthesis, broad/
irreversible ADRs, complex/multi-module ExecPlans), GPT-5.5 high via
the codex plugin as checker + rescue (Evaluator, adversarial review,
mid-execution diff sanity, rescue worker, async result harvest).
Breaks prior model-agnosticism deliberately so telemetry compounds
across the fleet. Ships ADR 004, a canonical
`docs/processes/model-policy.md`, an embedded summary table in the
operating manual, a session-bootstrap read step, a phase-gate bullet,
a steering-loop "model drift" triage question, and a pre-filled
default Evaluator literal (`codex:adversarial-review`) in
`dev-setup.md`. Codex plugin is a soft dependency with a documented
fresh-subagent fallback in `model-policy.md`. The contract is
enforced by reading order and the steering loop — no mechanical
sensor.

**Files touched:** `assets/model-policy.md` (new),
`assets/004-fleet-model-policy.md` (new), `assets/harness.md`,
`assets/AGENTS.md`, `assets/PLANS.md`, `assets/dev-setup.md`,
`assets/docs-README.md`, `SKILL.md`, `CONTEXT.md`.

**How to apply:**

1. If `docs/processes/model-policy.md` is absent in the target repo,
   copy it from `~/.claude/skills/init-docs/assets/model-policy.md`.
   Skip if present.

2. Check the target repo's `docs/decisions/` for any ADR titled
   "Fleet model policy" (any number). If absent, find the next
   available `NNN` — default `004` if free, otherwise the next free
   number — and copy
   `~/.claude/skills/init-docs/assets/004-fleet-model-policy.md` to
   `docs/decisions/NNN-fleet-model-policy.md`. If `NNN ≠ 004`,
   rewrite the heading `# ADR 004 — …` and any in-body `ADR 004`
   mentions to the chosen number. Record the chosen NNN for step 7.

3. In the target repo's `docs/processes/harness.md`:
   - Check for a `## Model assignments` heading. If absent, insert
     the section between `## Phase gates — quick reference` and
     `## Session exit` with the contents from
     `~/.claude/skills/init-docs/assets/harness.md`.
   - Phase 2: check for a "design subagent" reference. If absent,
     append the synthesis-invocation sentence.
   - Phase 4: check for a "design subagent" reference. If absent,
     append the ADR-drafting sentence.
   - Phase 5: check for "design subagent" and
     "codex:adversarial-review" references. If absent, append the
     plan-drafting and pre-approval critic sentences.
   - Steering loop: check for "model drift" phrasing. If absent,
     insert the triage paragraph before "Never answer 'just prompt
     harder'".
   Skip each individually if its content is already present.

4. In the target repo's `AGENTS.md`:
   - Session bootstrap: check the numbered list for a
     `model-policy.md` read step. If absent, insert it immediately
     before the harness-version check and renumber the harness-version
     step as needed.
   - Phase gates: check for a "model policy" bullet. If absent,
     insert it between the Evaluator-gate bullet and the
     plan-coverage-sensor paragraph with the contents from
     `~/.claude/skills/init-docs/assets/AGENTS.md`.

5. In the target repo's `docs/PLANS.md`, check `## How ExecPlans fit
   into the harness` for a "model policy" reference. If absent,
   append the paragraph from
   `~/.claude/skills/init-docs/assets/PLANS.md`.

6. In the target repo's `docs/processes/dev-setup.md`:
   - § Toolchain: check for a "codex plugin" bullet. If absent,
     append it.
   - § Evaluator convention: read the current value of
     `evaluator-cmd:`. If the line still contains only the literal
     placeholder underscores or is blank, replace with
     `codex:adversarial-review --base <merge-base>` plus the
     focus-text template comment from
     `~/.claude/skills/init-docs/assets/dev-setup.md`. If the line
     already contains a non-placeholder value, leave it alone and
     flag in the audit report: "evaluator-cmd has a project-local
     value; review against the fleet default in `model-policy.md`".
   - Replace the "Until this section is filled in..." paragraph with
     the codex-fallback paragraph from the asset. Skip if the new
     paragraph is already present.

7. In the target repo's `docs/README.md`:
   - § Decisions: check for the new ADR catalog entry. If absent,
     append it with the contents from
     `~/.claude/skills/init-docs/assets/docs-README.md`, rewriting
     the number and link if step 2 chose `NNN ≠ 004`.
   - § Processes: check for a `model-policy.md` entry. If absent,
     append the entry from the asset.

**Stack-specific notes:** None. The policy is intentionally
stack-agnostic — it constrains the agent fleet, not the project's
language or toolchain. The codex-plugin requirement is the only tool
dependency; its fallback is named in `model-policy.md` so repos
without the plugin still operate.

**Additive/replacing:** mostly additive — one new ADR, one new
process doc, several new sections and bullets. Two replacing edits:
the `evaluator-cmd:` literal in `dev-setup.md` (placeholder → fleet
default; skipped if the user has already filled it with a
non-placeholder value), and the "Until this section is filled in..."
paragraph that follows it.

**Conflict risk:** medium. Surfaces: renamed `## Phase gates — quick
reference`, `## Session exit`, `## How ExecPlans fit into the
harness`, `## Evaluator convention`, `## Toolchain`, `## Decisions`,
`### Steering loop`. The ADR-numbering branch in step 2 is a real
surface — repos that already have an ADR 004 reserved for a different
topic get the next free number and a rewrite pass. The
`evaluator-cmd:` replacement is the highest-risk single edit; the
placeholder-vs-filled detection must be conservative — if in doubt,
skip and flag.

---

## 2026-05-20 — Evaluator gate at plan completion

**What:** Adds an independent **Evaluator** pass as the gate between
`docs/exec-plans/active/` and `docs/exec-plans/completed/`. The
Evaluator is a coding agent or tool that does not share state with the
plan's worker — fresh subagent, separate session, external CLI agent,
or human reviewer. Universal invocation contract `<evaluator-cmd>
<plan-path>`; the consuming repo declares the concrete command in
`docs/processes/dev-setup.md` § Evaluator convention. The Evaluator
writes verdicts (Alignment + Acceptance required, Quality optional)
into a new `## Evaluator transcript` section in the plan file itself;
the worker never edits that section. Retries append new timestamped
blocks. Closes the worker/checker split named in CONTEXT.md by adding
its second concrete enforcer (the first being the verifier loop from
ADR 002).

**Files touched:** `assets/PLANS.md`, `assets/harness.md`,
`assets/exec-plan-template.md`, `assets/AGENTS.md`,
`assets/dev-setup.md`, `assets/docs-README.md`,
`assets/003-evaluator-gate.md` (new), `SKILL.md`, `CONTEXT.md`.

**How to apply:**

1. In the target repo's `docs/PLANS.md`, check the Required sections
   list for an "Evaluator transcript" entry. If absent, insert the
   bullet between "Artifacts and Notes" and "Interfaces and
   Dependencies", and append the new "The `Evaluator transcript`
   section" subsection at the end of the `features:` block (above
   "Non-negotiable requirements"), using the contents from
   `~/.claude/skills/init-docs/assets/PLANS.md`.
2. In the target repo's `docs/processes/harness.md`, check Phase 6
   for an "Evaluator" reference. If absent, insert the new pre-move
   paragraph immediately before "On completion, the **agent** moves
   the plan file…" with the contents from
   `~/.claude/skills/init-docs/assets/harness.md`. Update the Phase-6
   gate line to require an Evaluator transcript with latest Alignment
   + Acceptance both `pass`.
3. In the target repo's `docs/exec-plans/_template.md`, check for a
   `## Evaluator transcript` section. If absent, insert it between
   "Artifacts and Notes" and "Interfaces and Dependencies" with the
   stub from `~/.claude/skills/init-docs/assets/exec-plan-template.md`.
4. In the target repo's `AGENTS.md`, check the Phase gates list for
   the Evaluator bullet. If absent, append it with the contents from
   `~/.claude/skills/init-docs/assets/AGENTS.md`.
5. In the target repo's `docs/processes/dev-setup.md`, check for an
   "Evaluator convention" heading. If absent, insert the section
   between "Feature verification convention" and "Running locally"
   with the contents from `~/.claude/skills/init-docs/assets/dev-setup.md`.
   Flag the section for filling.
6. Check the target repo's `docs/decisions/` for any ADR titled
   "Evaluator gate at plan completion" (any number). If absent, find
   the next available `NNN` — default `003` if free, otherwise the
   next free number — and copy
   `~/.claude/skills/init-docs/assets/003-evaluator-gate.md` to
   `docs/decisions/NNN-evaluator-gate.md`. If `NNN ≠ 003`, also
   rewrite the cross-references inside the copied file (the heading
   `# ADR 003 — …` and any in-body `ADR 003` mentions) to the chosen
   number.
7. In the target repo's `docs/README.md`, check the Decisions section
   for the new ADR. If absent, append the catalog entry from
   `~/.claude/skills/init-docs/assets/docs-README.md`, rewriting the
   number and link if step 6 chose `NNN ≠ 003`.

**Stack-specific notes:** None. The Evaluator command itself is
stack-specific and is captured in each repo's
`docs/processes/dev-setup.md` § Evaluator convention; the skill does
not impose a default. Until the section is filled, the convention is
"a human reviewer in a separate session writes the transcript."

**Additive/replacing:** additive — one new ADR, one new PLANS.md
required section + subsection, one new harness.md Phase-6 paragraph,
one new exec-plan-template stub, one new AGENTS.md phase-gate bullet,
one new dev-setup.md section, and one new catalog entry.

**Conflict risk:** medium. Surfaces: a target repo that has renamed
`## Required sections`, `## Phase gates`, the Phase 6 "On completion"
sentence, `## Artifacts and Notes`, `## Feature verification
convention`, or `## Decisions` (catalog). The ADR-numbering branch in
step 6 is also a real surface — repos that already have an ADR 003
(e.g. plan-coverage sensor reference implementations) get the next
free number and a rewrite pass. In any conflict, the audit agent
should pause and ask rather than insert blindly.

---

## 2026-05-19 — Session exit checklist

**What:** Adds Session exit as the explicit clock-out half of session
bootstrap. The new checklist has six dimensions: build, verifier, plan
state, doc coherence, startup viable, and chat-sweep. It runs only on
explicit user signals such as "we're done", "ttyl", "close out",
"session exit", or "/quit"; it routes orphan chat knowledge into
existing artifacts instead of creating a session log. Adds ADR 002,
threads a FEATURES.md baseline read into `AGENTS.md` bootstrap, adds a
Working relationship trigger bullet, and marks ExecPlan Progress as the
place that must reflect reality on exit.

**Files touched:** `assets/harness.md`, `assets/AGENTS.md`,
`assets/exec-plan-template.md`, `assets/docs-README.md`,
`assets/002-session-exit.md` (new), `SKILL.md`.

**How to apply:**

1. In the target repo's `docs/processes/harness.md`, check for a
   `## Session exit` heading. If absent, insert the section between
   `## Phase gates — quick reference` and `## Where artifacts live`
   with the contents from
   `~/.claude/skills/init-docs/assets/harness.md`.
2. In the target repo's `AGENTS.md`, check for the trigger-recognition
   bullet under "Working relationship". If absent, append it. Check
   for the `docs/FEATURES.md` read step in Session bootstrap that
   records the `Passing` baseline for session exit. If absent, insert
   it.
3. In the target repo's `docs/exec-plans/_template.md`, check the
   Progress section for the session-exit cross-reference. If absent,
   append it.
4. Check for `docs/decisions/002-session-exit.md`. If absent, copy it
   from `~/.claude/skills/init-docs/assets/002-session-exit.md`.
5. In the target repo's `docs/README.md`, check the Decisions section
   for `002-session-exit.md`. If absent, append the ADR 002 catalog
   entry from `~/.claude/skills/init-docs/assets/docs-README.md`.

**Stack-specific notes:** None. The checklist resolves build, startup,
and verifier commands through each repo's `docs/processes/dev-setup.md`
and existing `verify-cmd:` / `verify:` convention.

**Additive/replacing:** additive — one new ADR, one new operating-manual
section, one new bootstrap baseline step, one Working relationship
bullet, one ExecPlan Progress sentence, and one catalog entry.

**Conflict risk:** low. Surfaces: a target repo that has renamed
`## Phase gates — quick reference`, `## Where artifacts live`,
`## Session bootstrap`, `## Working relationship`, `## Progress`, or
`## Decisions`. In any such case the audit agent should pause and ask
rather than insert blindly.

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
