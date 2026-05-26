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

## 2026-05-28 — ADR identity by slug, not number

**What:** ADRs are now identified by their `id:` frontmatter slug
(kebab-case, unique within `docs/decisions/`), not by filename number.
The number prefix in the filename (`NNN-<slug>.md`) becomes a per-repo
sort key only — when the harness scaffolds into a target repo with
existing ADRs, harness ADRs are appended after the highest existing
number rather than forcing the user to renumber their own decisions
(or worse, silently colliding with them). Cross-references inside docs
use the slug form `ADR <slug>` (e.g., `ADR evaluator-gate`), which
survives any per-repo renumbering. Numeric forms (`ADR 003`,
`ADR-003`) are still legible to humans but are migration debt — the
new `sweep_adr_refs.py` tool rewrites them to slug form.

The seven harness ADRs ship with `id:` frontmatter and the optional
`legacy_numbers: []` field. When the scaffold-into-existing algorithm
(Step 13 § Assignment algorithm) lands a harness ADR at a non-canonical
number, it populates `legacy_numbers` with the canonical number so the
sweep tool can rewrite pre-existing references in the target repo's
own docs. The field is migration-only; users delete it once their
sweep is complete.

The canonical manifest (`_canonical_manifest.py`) grows
`ADR_SLUGS_REQUIRED` (the seven slugs the harness owns) and
`REQUIRED_METADATA_KEYS_ADR` (the 4-key block plus `id:`). ADR file
paths are removed from `EXISTENCE_REQUIRED` and `FRONTMATTER_REQUIRED`
— the validators resolve slugs to files by scanning
`docs/decisions/` for matching frontmatter. `check_harness_structure.py`
gains a slug-uniqueness check; `garbage_collect_docs.py` extends its
strict frontmatter pass to resolved ADR files. `REQUIRED_REFERENCES`
asserts `ADR <slug>` strings rather than canonical filename paths so
the cross-reference check survives renumbering.

All cross-references inside the harness's own assets — `AGENTS.md`,
`PLANS.md`, `harness.md`, `model-policy.md`, `dev-setup.md`,
`docs-README.md`, the seven ADRs themselves, and the two hook scripts
— have been rewritten to slug form. `harness.md` grows an "ADR identity
and format" appendix documenting the slug convention, the
`legacy_numbers:` migration field, and the updated `# ADR <slug> —
Title` header shape.

**Files touched:** `assets/001-harness-design.md` through
`assets/007-harness-validators.md` (frontmatter + header + body refs),
`assets/AGENTS.md`, `assets/PLANS.md`, `assets/harness.md`,
`assets/docs-README.md`, `assets/dev-setup.md`,
`assets/model-policy.md`, `assets/references-README.md`,
`assets/harness-planner-critic-hook.mjs`,
`assets/verify-covers-hook.sh`,
`assets/scripts/_canonical_manifest.py`,
`assets/scripts/check_harness_structure.py`,
`assets/scripts/garbage_collect_docs.py`,
`assets/scripts/sweep_adr_refs.py` (new),
`SKILL.md`, `CHANGELOG.md`.

**How to apply:**

1. **Add `id:` frontmatter to each harness ADR in the target repo.**
   The seven slugs are `harness-design`, `session-exit`,
   `evaluator-gate`, `fleet-model-policy`, `hard-constraints`,
   `pre-approval-critic-gate`, `harness-validators`. For each ADR
   file under `docs/decisions/` whose filename matches a harness ADR
   (typically `001-harness-design.md` through
   `007-harness-validators.md`), read its frontmatter. If `id:` is
   already present, skip. Otherwise insert `id: <slug>` as the first
   key inside the `---` block and `legacy_numbers: []` as the last
   key. Also update the H1 header from `# NNN — Title` to
   `# ADR <slug> — Title`. Skip a file individually if both `id:`
   and the slug-form header are already present. **Stop with conflict
   report** if any harness ADR file is missing entirely (re-run
   scaffold first) or if a file at a harness-ADR filename carries a
   different `id:` value (collision; user must resolve manually).

2. **Replace the four harness validator scripts** at
   `scripts/harness/` with the new versions from
   `~/.claude/skills/init-docs/assets/scripts/`:
   `_canonical_manifest.py`, `check_harness_structure.py`,
   `garbage_collect_docs.py`, and the new `sweep_adr_refs.py`. The
   first three are drop-in replacements (same CLI surface);
   `sweep_adr_refs.py` is new — `chmod +x` it. Skip individually if
   a file is byte-identical to the asset. **Stop with conflict
   report** if any of the three existing scripts has been locally
   modified beyond cosmetic whitespace; the changes are mechanical
   and an unexpected local edit suggests divergence the operator
   should review.

3. **Rewrite slug-form references in the harness-shipped docs**
   inside the target repo. For each of `AGENTS.md`, `docs/PLANS.md`,
   `docs/processes/harness.md`, `docs/processes/model-policy.md`,
   `docs/processes/dev-setup.md`, `docs/README.md`,
   `docs/references/README.md`, `.claude/hooks/verify-covers-hook.sh`,
   `.claude/hooks/harness-planner-critic-hook.mjs`, and the seven
   harness ADR files themselves: compare against
   `~/.claude/skills/init-docs/assets/` and apply the
   `ADR NNN` → `ADR <slug>` text rewrites that appear in the assets
   but not yet in the target. The simplest mechanical path is to run
   `python3 scripts/harness/sweep_adr_refs.py --write` once after
   step 2 — the sweep tool reads each ADR's slug + current filename
   number and rewrites all numeric refs across the repo's text scan
   set. Skip individually if the target file is byte-identical to
   the harness asset, or if the file already contains the slug form
   and no numeric form. **Stop with conflict report** if a file has
   been renamed or its `## ADR identity` / `## Hard constraints`
   sections (where applicable) restructured such that targeted
   rewrites become ambiguous.

4. **Add the "ADR identity and format" appendix to
   `docs/processes/harness.md`.** Check whether the file's final
   `## Appendix` heading is `## Appendix — ADR identity and format`.
   If so, skip. Otherwise replace the existing `## Appendix — ADR
   format` heading + body with the new appendix from
   `~/.claude/skills/init-docs/assets/harness.md` § Appendix.
   **Stop with conflict report** if the final `## Appendix` section
   has been renamed or its body locally modified beyond the harness
   default.

5. **Run the sweep tool to migrate the operator's own docs.** After
   steps 1–4 are clean, run
   `python3 scripts/harness/sweep_adr_refs.py` (dry-run) and show
   the proposed rewrites. These will cover any docs the operator
   wrote that referenced harness ADRs by number (e.g., analysis
   docs, exec-plans, tickets). On the operator's confirmation, run
   `python3 scripts/harness/sweep_adr_refs.py --write`. The tool is
   idempotent — a second `--write` is a no-op once the repo is
   clean. **Do not stop the audit if the operator declines the
   sweep** — slug refs are recommended but not required; legacy
   numeric refs continue to resolve as long as the file at that
   number exists. Surface the deferred sweep in the audit summary
   so the operator can run it later.

6. **Verify with the structure check.** Run
   `python3 scripts/harness/check_harness_structure.py --dry-run`.
   Expected: zero findings related to ADR existence, frontmatter,
   or cross-references. The dry-run flag means findings are reported
   to stderr but exit is always 0; flip to a real run (no flag) once
   the audit is clean. **Stop with conflict report** if the dry-run
   surfaces any ADR-related finding — that indicates one of steps
   1–4 did not complete idempotently and the marker must not
   advance.

**Stack-specific notes:** None. The slug convention, the manifest
structure, and the sweep tool are stack-agnostic. The Python validators
remain stdlib-only (≥ 3.9). Wiring (pre-commit / Makefile / CI) is
unchanged — the new `sweep_adr_refs.py` is a one-shot migration tool,
not a recurring gate, and does not belong in the standing CI loop.

---

## 2026-05-27 — Cold-start test and initialization checklist as scaffolded artifacts

**What:** Ships two new process documents and a closing Bootstrap-contract
verdict in `/init-docs` Step 18. `docs/processes/initialization-checklist.md`
documents the bootstrap contract — four conditions a freshly-scaffolded repo
must satisfy to be operable (can start / can test / can see progress / can
pick up next steps), each mapped to a concrete surface in the repo. Two-level
pass: *surface* (artifact exists, mechanically checkable post-scaffold) vs.
*populated* (non-placeholder content). `docs/processes/cold-start-test.md`
documents the quarterly falsifier ritual: five questions answered in a fresh
agent session using repo content only, with the transcript appended as a new
top section to a single rolling log at `docs/generated/cold-start-test.md`.
Drift across sections feeds the steering loop. Cold-start probes legibility;
bootstrap contract probes operability. Both are distinct from
`AGENTS.md` § Session bootstrap (the per-session protocol).

Step 18 grows a closing **Bootstrap contract** verdict that prints per
condition: `[✓ surface] [✓ ready]` / `[✓ surface] [⚠ placeholder]` /
`[✗ surface missing]`. A fresh scaffold satisfies all surfaces; conditions 1
and 2 routinely report `placeholder` until the user fills in `dev-setup.md`.
Surface-missing is a skill bug, surfaced loudly but non-blocking. The verdict
runs at the end of every `/init-docs` invocation — scaffold, audit, and
up-to-date no-op alike.

Files self-document; no new ADR. The CHANGELOG entry records the
introduction; the two files carry their own rationale headers.

**Files touched:** `assets/initialization-checklist.md` (new),
`assets/cold-start-test.md` (new), `assets/docs-README.md`,
`assets/harness.md`, `SKILL.md`, `CONTEXT.md`, `CHANGELOG.md`.

**How to apply:**

1. If `docs/processes/initialization-checklist.md` is absent in the
   target repo, copy it from
   `~/.claude/skills/init-docs/assets/initialization-checklist.md`.
   Skip if present.

2. If `docs/processes/cold-start-test.md` is absent in the target
   repo, copy it from
   `~/.claude/skills/init-docs/assets/cold-start-test.md`. Skip if
   present.

3. In the target repo's `docs/README.md` § Processes section, check
   for entries for the initialization checklist and the cold-start
   test. If absent, append two new bullets from
   `~/.claude/skills/init-docs/assets/docs-README.md`:
   - `- [Initialization checklist](processes/initialization-checklist.md) — the bootstrap contract; four conditions every operable repo must satisfy \`#ai-harness\` \`#guideline\``
   - `- [Cold-start test](processes/cold-start-test.md) — quarterly legibility ritual; five questions answered from repo content alone \`#ai-harness\` \`#guideline\``
   Skip each individually if already present. **Stop with conflict
   report** if `## Processes` is renamed or missing.

4. In the target repo's `docs/processes/harness.md` § Steering loop
   section, check for a "cold-start log" reference. If absent,
   insert the paragraph from
   `~/.claude/skills/init-docs/assets/harness.md` immediately after
   the `## Failing` scan paragraph and before the `---` separator
   that precedes "What the harness contains today". Skip if a
   paragraph already references the cold-start test by name.
   **Stop with conflict report** if `## Steering loop` is renamed
   or missing, or if the `## Failing` scan paragraph is not
   detectable.

5. **No mechanical change to Step 18 in target repos** — the
   Bootstrap-contract closing verdict is rendered by the agent
   running `/init-docs`, not by any file in the target repo. The
   logic lives in this skill's `SKILL.md`; consuming repos do not
   need to track it. The audit step has nothing to write here.

**Stack-specific notes:** None. Both files are stack-agnostic. The
bootstrap contract resolves to existing artifacts (`dev-setup.md`
sections, `FEATURES.md`, `exec-plans/active/`, `tech-debt-tracker.md`)
that the skill already scaffolds; the cold-start ritual is
human-initiated and document-only (no slash command, no automation).
The rolling log at `docs/generated/cold-start-test.md` is created on
first run by whoever runs the test, not pre-created by this skill —
this preserves `docs/generated/`'s "machine-generated artifacts only,
created when generated" invariant.

**Additive/replacing:** additive — two new files, two new catalog
entries, one new steering-loop paragraph, and a new closing section in
this skill's SKILL.md Step 18 (which does not propagate to target
repos).

**Conflict risk:** low. Surfaces: a target repo that has renamed
`## Processes` (docs/README.md), `## Steering loop`
(harness.md), or removed the `## Failing` scan paragraph. In any such
case the audit agent should pause and ask rather than insert blindly.

---

## 2026-05-26 — Harness structure validator and doc garbage collector

**What:** Ships two stdlib-Python validators from the init-docs skill,
installed at `scripts/harness/` in every scaffolded repo:
`check_harness_structure.py` (fast structural check — existence, 4-key
YAML frontmatter on canonical markdown, required cross-references, no
forbidden ephemera, no absolute paths), and `garbage_collect_docs.py`
(slower audit — broken-reference scan, metadata staleness, orphan and
ephemeral detection, markdown report). Both share
`_canonical_manifest.py`: the single source of truth for the canonical
file set, the frontmatter-required subset, required references,
forbidden globs, and text-scan roots. Both honour `HARNESS_BYPASS` and
accept `--dry-run`. The skill does **not** ship Makefile / pre-commit
/ CI wiring — stack-specific, mirrors the plan-coverage sensor's
posture (see 2026-04-20 entry). Example snippets ship in the ADR 007
appendix, marked example-only. Adds 4-key YAML frontmatter
(`owner: {{REPO_NAME}}`, `status`, `last_reviewed: 2026-05-26`,
`update_trigger`) to the 18 canonical markdown assets. Subagent
configs and hook scripts are existence-only — the harness 4 keys
would collide with Claude Code's subagent schema or break shebangs;
schema coexistence is tracked as tech debt. Closes ADR 003's
deferral of CI enforcement for the documentation half of the
worker/checker split.

**Files touched:** `assets/scripts/check_harness_structure.py` (new),
`assets/scripts/garbage_collect_docs.py` (new),
`assets/scripts/_canonical_manifest.py` (new),
`assets/007-harness-validators.md` (new), `assets/AGENTS.md`,
`assets/ARCHITECTURE.md`, `assets/SECURITY.md`,
`assets/docs-README.md`, `assets/PLANS.md`, `assets/FEATURES.md`,
`assets/tech-debt-tracker.md`, `assets/harness.md`,
`assets/dev-setup.md`, `assets/model-policy.md`,
`assets/001-harness-design.md`, `assets/002-session-exit.md`,
`assets/003-evaluator-gate.md`, `assets/004-fleet-model-policy.md`,
`assets/005-hard-constraints.md`,
`assets/006-pre-approval-critic-gate.md`,
`assets/references-README.md`,
`assets/generated-README.md`, `SKILL.md`, `CHANGELOG.md`.

**How to apply:**

1. If any of `scripts/harness/check_harness_structure.py`,
   `scripts/harness/garbage_collect_docs.py`, or
   `scripts/harness/_canonical_manifest.py` is absent in the target
   repo, copy all three from
   `~/.claude/skills/init-docs/assets/scripts/` to
   `scripts/harness/`. Create `scripts/harness/` if absent. `chmod +x`
   `check_harness_structure.py` and `garbage_collect_docs.py` (not
   `_canonical_manifest.py` — module). Skip if all three present.

2. Check the target repo's `docs/decisions/` for any ADR titled
   "Harness validators" (any number). If absent, find the next
   available `NNN` — default `007` if free, otherwise the next free
   number — and copy
   `~/.claude/skills/init-docs/assets/007-harness-validators.md` to
   `docs/decisions/NNN-harness-validators.md`. If `NNN ≠ 007`,
   rewrite the heading `# ADR 007 — …` and every in-body `ADR 007`
   mention to the chosen number. Record the chosen NNN for step 6.

3. For each path in the canonical frontmatter list — `AGENTS.md`,
   `ARCHITECTURE.md`, `SECURITY.md`, `docs/README.md`, `docs/PLANS.md`,
   `docs/FEATURES.md`, `docs/tech-debt-tracker.md`,
   `docs/processes/harness.md`, `docs/processes/dev-setup.md`,
   `docs/processes/model-policy.md`,
   `docs/decisions/00[1-6]-*.md`, the new ADR from step 2,
   `docs/references/README.md`, `docs/generated/README.md` — check
   whether the file starts with `---\n` (YAML frontmatter). If absent,
   prepend the 4-key block:

   ```yaml
   ---
   owner: <repo basename from git rev-parse --show-toplevel>
   status: <stable | living | accepted — see table in ADR 007>
   last_reviewed: 2026-05-26
   update_trigger: <on-harness-change | on-module-change | …>
   ---
   ```

   Source the `status` and `update_trigger` values from the matching
   asset under `~/.claude/skills/init-docs/assets/`. **Skip** files
   that already start with `---\n` *even if the keys differ* — flag
   as `frontmatter present but schema unverified` in the audit
   report. Subagent configs at `.claude/agents/*.md` are exempt
   (existence-only).

4. In the target repo's `docs/processes/harness.md`, check
   `## What the harness contains today` (or the equivalent harness-
   contents heading) for a `### Harness validators` subsection. If
   absent, append the subsection from
   `~/.claude/skills/init-docs/assets/harness.md`. Skip if present.
   **Stop with conflict report** if the parent heading is renamed.

5. In the target repo's `docs/processes/dev-setup.md`, check for a
   `## Harness validators` heading. If absent, insert the section
   between `## Pre-tool-use hook (covers: enforcement)` and
   `## Common commands` with the contents from
   `~/.claude/skills/init-docs/assets/dev-setup.md`. Skip if present.
   **Stop with conflict report** if either neighbouring heading is
   renamed or missing.

6. In the target repo's `docs/README.md` § Decisions, check for a
   catalog entry referencing `decisions/NNN-harness-validators.md`
   (NNN from step 2). If absent, append a one-line entry using the
   format in `~/.claude/skills/init-docs/assets/docs-README.md`.
   Skip if present.

7. **Self-verification.** Run
   `python3 scripts/harness/check_harness_structure.py --dry-run`.
   If `--dry-run` exits non-zero (the script is broken), stop and
   report; do not advance the marker. If `--dry-run` exits 0 but
   reports findings to stderr, surface them in the audit summary as
   needs-filling items (frontmatter still on `{{REPO_NAME}}`, etc.)
   and continue. Then run
   `python3 scripts/harness/check_harness_structure.py` (no flag).
   If exit 0, advance `.harness-version` to `2026-05-26`. If exit 1,
   leave the marker at the previous entry's date and report which
   check failed.

**Stack-specific notes:** No Makefile / pre-commit / CI wiring ships.
Repos translate the contract documented in `dev-setup.md` § Harness
validators into their stack of choice (Make, Task, just, npm scripts,
GitLab CI, CircleCI, etc.). The Python ≥ 3.9 requirement applies
universally; repos without Python on `PATH` install it or
re-implement the contract in their stack's native language (the
manifest is data, the checks are mechanical). Older harness repos
(`.harness-version < 2026-05-24`) won't have `.claude/agents/` or
`.claude/hooks/` populated when this entry fires — the audit
processes entries oldest-first (SKILL.md § Audit mode procedure step
2), so the 2026-05-24 and 2026-05-25 entries land first and create
those paths before this entry's manifest existence check runs them.

**Additive/replacing:** mostly additive — three new scripts, one new
ADR, two new doc sections, one new catalog entry. One additive
retrofit: 4-key YAML frontmatter prepended to 18 canonical markdown
files (prepend only; never overwrite an existing `---` block).

**Conflict risk:** medium. Surfaces: renamed
`## What the harness contains today` in `harness.md`, renamed
`## Pre-tool-use hook (covers: enforcement)` or `## Common commands`
in `dev-setup.md`, renamed `## Decisions` in `docs/README.md`,
existing-but-different frontmatter on canonical files (flagged, not
overwritten), an `ADR 007` reserved for another topic (next free
NNN + rewrite). Step 7's self-verification is the riskiest single
addition — first time the audit runs code it just installed.
Mitigation: `--dry-run` first, real run second, marker advances only
on real-run exit 0.

---

## 2026-05-25 — Codex slash commands replaced with script-invocation forms; Evaluator focus reframed

**What:** The codex-plugin-cc slash commands (`/codex:review`,
`/codex:adversarial-review`, `/codex:result`, etc.) set
`disable-model-invocation: true` — they are user-only and the orchestrator
cannot reach them from inside a turn. The harness docs previously named those
slash literals as the orchestrator's tools for Steps 17 (diff sanity), 18
(rescue), 19 (result harvest), and 20 (Completion Evaluator), which were
mechanically unactionable. The pre-approval critic hook (ADR 006) already
worked around this by spawning `codex-companion.mjs adversarial-review`
directly; this entry extends the same pattern to the orchestrator-driven
usages: Bash → `node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs"
<subcommand>` for review/adversarial-review/result, and
`Agent(subagent_type="codex:codex-rescue", …)` for rescue (the rescue
slash command forwards to that subagent, which the orchestrator *can*
invoke via the `Agent` tool).

Also reframes the Completion Evaluator's focus text in adversarial terms.
The Evaluator's job is conformance verification (Alignment + Acceptance
against the plan), but `/codex:review` accepts no focus text or plan path,
so it cannot carry the Evaluator's instruction template. The harness uses
`adversarial-review` for its steerability and reframes the prompt as
"challenge the worker's claim that the diff is done; pressure-test the
Acceptance evidence." A new `## Tool selection` section in ADR 003
records the trade-off and treats codex-plugin-cc as fixed external
tooling (no upstream feature request implied).

Renames `codex:rescue` to `codex:codex-rescue` everywhere the harness
names a tool — the slash command is user-only; the subagent is the
orchestrator-callable surface.

**Files touched:** `assets/model-policy.md`, `assets/harness.md`,
`assets/dev-setup.md`, `assets/003-evaluator-gate.md`, `assets/AGENTS.md`,
`assets/PLANS.md`, `assets/006-pre-approval-critic-gate.md`,
`assets/004-fleet-model-policy.md`, `CONTEXT.md`, `SKILL.md`,
`CHANGELOG.md`.

**How to apply:**

1. In the target repo's `docs/processes/model-policy.md` per-step
   assignments table, locate rows 17 (Mid-execution diff sanity), 18
   (Rescue implementation), 19 (Async result harvest), and 20
   (Completion Evaluator). Replace each row's Invocation column with
   the script-invocation / Agent-tool form from
   `~/.claude/skills/init-docs/assets/model-policy.md`. The substring
   to look for in the current file is the bare slash literal
   (`codex:review`, `codex:rescue`, `codex:result`,
   `codex:adversarial-review --base <merge-base>`); replace with the
   Bash / Agent invocation form. Skip each row individually if already
   updated. **Stop with conflict report** if any of rows 17–20 are
   renamed or the column layout has changed.

2. In the same file, replace the `## Codex commands reference` section
   body with the expanded version from the asset (explains slash-command
   limitation, names the two dispatch paths, lists the four roles).
   The trigger is the presence of the bare bullets
   `- `codex:rescue` — independent implementation attempt…`; the
   replacement carries the same role descriptions plus the dispatch
   explanation. Skip if the new wording (`dispatch path` or
   `Agent tool with subagent_type`) is already present.

3. In the same file, change `\`codex:rescue\` has no good fallback` to
   `\`codex:codex-rescue\` has no good fallback` in the Fallback
   subsection. Skip if already updated.

4. In the target repo's `docs/processes/harness.md` § Model assignments
   table, locate the four rows (Pre-approval critic, Mid-execution diff
   sanity, Rescue implementation, Completion Evaluator) and replace
   each Command column with the dispatch form from
   `~/.claude/skills/init-docs/assets/harness.md`. Trigger: bare
   `codex:` slash literal in the Command column. Skip per-row if
   already updated.

5. In the same `harness.md`, append the "The codex-plugin-cc slash
   commands... set `disable-model-invocation: true`" paragraph
   immediately after the "If the codex plugin is unavailable, follow
   the fallback chain..." paragraph in § Model assignments. Skip if
   the paragraph is already present (search for
   `disable-model-invocation`).

6. In the same `harness.md` § Phase 5, locate the Critic-pass row of
   the step table. Replace `fires codex:adversarial-review` with
   `invokes codex-companion.mjs adversarial-review` and add the
   `(slash command is user-only)` parenthetical. Skip if already
   updated.

7. In the target repo's `docs/processes/dev-setup.md` § Evaluator
   convention, replace the `evaluator-cmd: codex:adversarial-review ...`
   line and the focus-text comment with the multi-line block from the
   asset (Bash invocation + adversarial-verification focus text). Skip
   if `codex-companion.mjs adversarial-review` is already present.

8. In the same `dev-setup.md`, check for a `### Tool resolution`
   subsection under `## Evaluator convention`. If absent, insert it
   from the asset immediately after the new focus-text block and
   before the *Independence assertion* paragraph. Skip if present.
   **Stop with conflict report** if `## Evaluator convention` has been
   renamed.

9. In the target repo's `docs/decisions/003-evaluator-gate.md`, check
   for a `## Tool selection` section between `## Decision` and
   `## Consequences`. If absent, insert the four-paragraph block from
   `~/.claude/skills/init-docs/assets/003-evaluator-gate.md`
   (explains the slash-command limitation, why `adversarial-review`
   over `review`, the focus-text reframe, and the codex-plugin-fixed
   note). Skip if present. **Stop with conflict report** if either
   neighbouring heading is renamed.

10. In the target repo's `AGENTS.md` § Phase gates, locate the
    bullet ending `Pre-approval critic and Evaluator passes invoke
    \`codex:adversarial-review\` per the same policy.` Replace the
    final sentence with the auto-fired / orchestrator-invoked
    distinction from the asset (cites
    `docs/processes/model-policy.md` § Codex commands reference).
    Skip if `auto-fired` and `slash command is user-only` are both
    present.

11. In the target repo's `docs/PLANS.md`, two phrase-level inserts:
    - In `## How ExecPlans fit into the harness`, after `The default
      critic command is \`codex:adversarial-review\`;`, insert ` the
      hook invokes the underlying \`codex-companion.mjs
      adversarial-review\` script directly because the slash command
      sets \`disable-model-invocation: true\`.` Skip if already
      present.
    - In `### The Pre-approval critic transcript section` →
      `**Invocation contract.**`, replace `The default critic is
      \`codex:adversarial-review\`, auto-fired by...` with the
      expanded version from the asset (names the
      `disable-model-invocation` flag and the Node script call).
      Skip if `disable-model-invocation` already appears in the
      paragraph.

12. In the target repo's `docs/decisions/006-pre-approval-critic-gate.md`
    § Decision → **Default tool**, replace the paragraph with the
    asset version (notes the slash-command restriction and that the
    hook invokes the underlying script). Skip if
    `disable-model-invocation` already appears in the paragraph.

13. In the target repo's `docs/decisions/004-fleet-model-policy.md`
    § Decision, replace `The default Evaluator command is
    \`codex:adversarial-review --base <merge-base>\`.` with the asset
    sentence (resolves to `codex-companion.mjs ...` via Bash;
    explains slash-command restriction). Skip if
    `codex-companion.mjs` already appears.

14. In the target repo's `docs/processes/CONTEXT.md` (or wherever the
    target keeps its glossary), update the **Pre-approval critic** and
    **Checker / rescue tier** entries to the asset versions
    (script-invocation parenthetical for the critic;
    `codex:codex-rescue` subagent name + Agent-tool dispatch note for
    the rescue tier). Skip each entry individually if already updated.

**Stack-specific notes:** None. The
`${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs` path resolves
identically on every machine with codex-plugin-cc installed; the
hook's `find ~/.claude/plugins/ -name codex-companion.mjs` discovery
fallback (used only inside the hook, where `CLAUDE_PLUGIN_ROOT` is
unpopulated) is portable across macOS and Linux.

**Additive/replacing:** mostly additive (phrase-level inserts and a
new ADR-003 § Tool selection section). Replacing: model-policy.md
rows 17–20 and the `## Codex commands reference` body; harness.md
four-row Command column and the Phase-5 Critic-pass row;
dev-setup.md `evaluator-cmd` line and focus-text comment; AGENTS.md
final sentence of the critic+Evaluator bullet; PLANS.md
**Invocation contract** paragraph; ADR-006 **Default tool**
paragraph; ADR-004 Evaluator-command sentence; CONTEXT.md two
glossary entries.

**Conflict risk:** low to medium. The Evaluator focus-text reframe in
dev-setup.md is the largest single change in spirit (not in lines)
— a project that has hand-edited the focus text will see a full
overwrite. Step 7 covers this with a skip-if-present check, but
projects with bespoke focus-text wording should review the diff
before accepting. All other edits are phrase-level and idempotent.
The ADR-003 § Tool selection insertion (step 9) hard-stops on
missing or renamed neighbouring headings.

---

## 2026-05-25 — Pre-approval critic gate (ADR 006); complexity threshold removed

**What:** Collapses the simple/complex ExecPlan threshold. Every plan now
flows through the `harness-planner` Opus 4.7 xhigh subagent and through the
pre-approval critic — no exceptions, no project-defined threshold,
no `module-count:` frontmatter. The threshold's ambiguity (single-module
high-risk surfaces, borderline-defaults-to-complex judgment calls) could
leave a high-stakes plan uncriticised; ADR 006 closes the gap by making
the worker/checker split unconditional at draft → approved, matching the
pattern ADR 003 already established at active → completed.

Introduces a new `## Pre-approval critic transcript` section in every
ExecPlan, structurally parallel to `## Evaluator transcript`. The
auto-critic hook is reshaped from background-detached to synchronous: the
agent's turn pauses for the critic run (typically 30–90s, hard-capped at
10 minutes) and the verdict is written directly into the named section
using the standard run-block format. Failure modes — codex-plugin-cc
missing, codex crash, timeout, non-zero exit, empty stdout — write a
`BLOCKED: <reason>` placeholder into the section instead of a verdict.
The lead's approval gate refuses any plan whose critic section is empty
or BLOCKED, making the gap visible at review time rather than silent.

Phase 4 ADRs are unaffected — the lead remains the canonical checker for
decision documents; extending the critic to ADRs would produce noise that
trains the lead to ignore the gate.

**Files touched:** `assets/006-pre-approval-critic-gate.md` (new),
`assets/PLANS.md`, `assets/exec-plan-template.md`, `assets/harness.md`,
`assets/AGENTS.md`, `assets/model-policy.md`, `assets/dev-setup.md`,
`assets/harness-planner-critic-hook.mjs`, `SKILL.md`, `CONTEXT.md`,
`CHANGELOG.md`.

**How to apply:**

1. Check the target repo's `docs/decisions/` for any ADR titled
   "Pre-approval critic gate" (any number). If absent, find the next
   available `NNN` — default `006` if free, otherwise the next free
   number — and copy
   `~/.claude/skills/init-docs/assets/006-pre-approval-critic-gate.md`
   to `docs/decisions/NNN-pre-approval-critic-gate.md`. If `NNN ≠ 006`,
   rewrite the heading `# ADR 006 — …` and every in-body `ADR 006`
   mention to the chosen number. Record the chosen NNN for steps 7 and 11.

2. In the target repo's `docs/exec-plans/_template.md` frontmatter,
   check for a `module-count:` line. If present, delete it. Skip if
   absent. **Stop with conflict report** if the line has been reworded
   beyond the original template shape.

3. In the same `_template.md`, check the section list for
   `## Pre-approval critic transcript`. If absent, insert the section
   (with the "Written by the Pre-approval critic only…" stub and
   `_No runs yet._` placeholder) immediately before
   `## Evaluator transcript`. Source:
   `~/.claude/skills/init-docs/assets/exec-plan-template.md`. Skip if
   present.

4. In the target repo's `docs/PLANS.md`:
   - In `## How ExecPlans fit into the harness`, replace the
     "multi-module or irreversible plans are drafted by the design
     subagent" sentence with the unconditional version from the asset
     (every plan goes through `harness-planner` + critic; default
     critic command; pointer to ADR 006). Skip if the sentence already
     references ADR 006.
   - Check for a `### The Pre-approval critic transcript section`
     subsection. If absent, insert it immediately before
     `### The Evaluator transcript section` with the contents from
     the asset (role definition, invocation contract, verdict shape,
     block shape, approval rule, feature-less plan handling).
   - In `## Required sections`, check for a `Pre-approval critic
     transcript` bullet. If absent, insert it immediately before the
     `Evaluator transcript` bullet with the contents from the asset.
   Skip each individually if its content is already present. **Stop
   with conflict report** if `## How ExecPlans fit into the harness`,
   `### The Evaluator transcript section`, or `## Required sections`
   has been renamed.

5. In the target repo's `docs/processes/harness.md` § Phase 5:
   - Locate the `Drafting a multi-module ExecPlan invokes the
     harness-planner subagent.` sentence. Replace it with the
     unconditional version from the asset (every plan; auto-critic;
     section pointer; ADR 006 link). Skip if the new wording is
     already present.
   - Locate the `**Complexity threshold (binding).**` paragraph. If
     present, delete it entirely. Skip if absent.
   - Locate the `**Pre-write gate (hard).**` paragraph and drop the
     "for a complex plan" / "under the complex threshold" / "Simple
     plans remain orchestrator-written." qualifiers. Match the wording
     in the asset. Skip if already universal.
   - Locate the `**Pre-approval critic (hard, complex plans only).**`
     paragraph. Replace it with the synchronous-hook version from the
     asset (drops "complex plans only", names the section, documents
     BLOCKED placeholders, removes the `/codex:status` + `/codex:result`
     harvest language). Skip if the new wording is already present.
   - Update the Phase-5 gate sentence to mention the
     `## Pre-approval critic transcript` section requirement.
   - In the Phase 5 step table, replace the `Critic pass | Orchestrator
     | …` row with `Critic pass | Hook (synchronous) | …` per the
     asset. Skip if already updated.
   - In § Model assignments, change `Phase 5 complex or multi-module
     ExecPlans` to `Phase 5 ExecPlans (all plans)`. Skip if already
     updated.

6. In the target repo's `AGENTS.md` § Phase gates:
   - Locate the `Phase 2 synthesis, phase 4 broad/irreversible ADRs,
     and phase 5 multi-module ExecPlans invoke…` bullet. Replace
     `phase 5 multi-module ExecPlans` with `every phase 5 ExecPlan`
     and `Phase 5 → harness-planner.` with `Phase 5 → harness-planner
     (all plans; no complexity threshold — see [ADR 006](docs/decisions/NNN-pre-approval-critic-gate.md)).`
     Match NNN from step 1.
   - Locate the `"Multi-module" / complex is defined per project in
     docs/processes/dev-setup.md § Complexity threshold` bullet. If
     present, delete it entirely. Skip if absent.
   - In the "Concrete delegation" subsection, locate the
     `**Phase 5 — ExecPlan (complex only).**` header. Replace with
     `**Phase 5 — ExecPlan.**`. Skip if already updated.
   - Check for a phase-gate bullet describing the
     `## Pre-approval critic transcript` section as a draft → approved
     gate. If absent, insert it from the asset (one bullet, paralleling
     the existing Evaluator-transcript gate, citing ADR NNN from
     step 1).
   Skip each individually if its content is already present.

7. In the target repo's `docs/processes/model-policy.md`
   "Per-step assignments" table:
   - Find rows for `Phase 5 simple ExecPlan` and `Phase 5 complex
     ExecPlan`. If both exist, replace them with a single
     `Phase 5 ExecPlan` row from the asset, and renumber subsequent
     rows down by 1 (step 17 → 16, 18 → 17, …, 22 → 21). Skip if
     already a single row.
   - Find the `Pre-approval critic` row (originally step 16). Replace
     its Notes column with the synchronous-hook + BLOCKED-placeholder
     version from the asset. Skip if already updated.
   - Delete the `## Complex vs simple ExecPlan threshold` section if
     present. Skip if absent. **Stop with conflict report** if the
     section has been reworded beyond recognition.

8. In the target repo's `docs/processes/dev-setup.md`, delete the
   `## Complexity threshold` section if present (heading plus body up
   to the next `## ` heading). Skip if absent.

9. In the target repo's `.claude/hooks/harness-planner-critic-hook.mjs`,
   replace the file with the synchronous version from
   `~/.claude/skills/init-docs/assets/harness-planner-critic-hook.mjs`.
   This is a **replacing** edit — the hook's behaviour changes from
   background-detached to synchronous and from silent-skip-on-failure
   to BLOCKED-placeholder-on-failure. Show the diff and require
   explicit user `y/n` before overwriting. On `n`, leave the file and
   emit it as a "Needs manual merge" item in the audit summary; still
   advance the marker.

10. In the target repo's `SKILL.md`:
    - Step 1 file list: ensure `docs/decisions/006-pre-approval-critic-gate.md`
      is present in the seeded-docs enumeration. Insert if absent.
    - Add a `## Step 13e — Seed ADR 006` step (or `NNN` if step 1
      chose differently) between Step 13d and Step 14, with the
      contents from the asset.
    - Step 16b: replace the "spawns codex-companion.mjs adversarial-review
      --background detached" language with the synchronous-hook
      description from the asset (no --background, writes verdict into
      named section, BLOCKED placeholders on failure). Skip if the new
      wording is already present.
    - Step 18 needs-filling list: ensure ADR 006 (`NNN-pre-approval-critic-gate.md`)
      is listed alongside the other ADRs.

11. In the target repo's `docs/README.md` § Decisions: check for the
    new ADR catalog entry. If absent, append a one-line entry for the
    NNN chosen in step 1, e.g.
    `- [ADR NNN — Pre-approval critic gate](decisions/NNN-pre-approval-critic-gate.md) — #ai-harness #plan`
    Skip if present.

**Stack-specific notes:** The hook is Node + Bash + jq-free (uses
spawnSync from `node:child_process`); no stack-specific dependencies
beyond Node on PATH. The 10-minute timeout is a fleet default; repos
on very large plans may need to extend it locally — edit the
`TIMEOUT_MS` constant at the top of the hook script. The hook script
is tracked in git; activation entry stays per-contributor in
`.claude/settings.local.json` per CHANGELOG 2026-05-25
"Block-maintenance" entry (the per-contributor rule is intentionally
preserved — contributors without codex-plugin-cc get BLOCKED
placeholders rather than silent skips, and the empty-section gate
makes manual remediation visible at review time).

**Additive/replacing:** mixed. Additive: ADR 006, PLANS.md section +
required bullet, exec-plan-template.md section stub, harness.md Phase
5 table row update, AGENTS.md critic-transcript gate bullet, SKILL.md
Step 13e. Replacing: dev-setup.md § Complexity threshold deletion,
model-policy.md row collapse + threshold section deletion, harness.md
Phase 5 Complexity-threshold paragraph deletion + Pre-write/Pre-approval
paragraph rewrites + Model assignments row, AGENTS.md "Multi-module
defined per project" bullet deletion + design-subagent bullet rewrite
+ "complex only" qualifier drop, exec-plan-template.md `module-count:`
frontmatter deletion, harness-planner-critic-hook.mjs full rewrite,
SKILL.md Step 16b rewrite.

**Conflict risk:** high. The hook rewrite is the riskiest single
change in the skill to date — it changes runtime behaviour from
non-blocking to blocking and from silent-skip to BLOCKED-placeholder.
Step 9 requires explicit user `y/n` for the overwrite. The
model-policy row renumbering (step 17–22 → 16–21) and the
harness.md Phase 5 paragraph deletions/rewrites are also high-touch
edits — every "Stop with conflict report" branch must halt the audit
rather than guess. The Phase 4 ADR exemption is documented in ADR 006
to forestall the natural follow-up question; do not extend the gate
to ADRs without a superseding ADR.

---

## 2026-05-25 — Covers: in-execution gate, citation discipline, reorder safety

**What:** Addresses the three negative consequences ADR 005 names —
constraints-block maintenance rot, the in-execution `covers:` gap, and
the AGENTS.md reorder risk. Three independent moves bundled into one
entry because they share a single rationale (close ADR 005's documented
weak points without changing its decision).

1. **Block-maintenance meta-rule.** Adds a `**Block-maintenance rule.**`
   paragraph at the top of `AGENTS.md` § Hard constraints requiring
   every loud-labelled bullet to cite an ADR (`ADR NNN`) or named
   section (`§ …`). Cites ADR 005 § Consequences for the rationale.
2. **In-execution covers: check.** Tightens the existing covers:
   bullet to require a per-tool-call self-check ("Before each
   Edit/Write tool call, verify the target path prefix-matches
   `covers:`"). Adds a session-bootstrap step (item 3) instructing the
   agent to load the active plan's `covers:` glob list into working
   context. Ships a stack-neutral PreToolUse hook reference at
   `assets/verify-covers-hook.sh` (bash + jq) and documents the
   contract in a new `## Pre-tool-use hook (covers: enforcement)`
   section in `dev-setup.md`. The hook breaks the prior
   "sensor scripts not shipped" posture — deliberately, with
   activation kept opt-in. Repos can swap for a stack-native
   implementation; the contract is what matters.
3. **Audit-mode safety rails.** Adds two new steps (5 and 6) to the
   audit procedure: (5) a warn-only citation check on Hard
   constraints bullets after marker advance; (6) an explicit
   side-by-side preview + `AGENTS.md.bak` backup + `y/n` gate before
   any heading reorder. Citation drift never blocks marker advance;
   reorder refusal still advances the marker but emits the reorder as
   a "Needs manual merge" item.

Also adds a "Hard-constraint addition rule" paragraph to SKILL.md §
"How to update this skill" tying new MUST/MUST NOT bullets to
same-changelog-entry ADRs, and a "Config-file precedence" bullet to
SKILL.md § Notes on scope declaring that hook activation entries
land in `.claude/settings.local.json` (per-contributor, gitignored),
never in tracked `.claude/settings.json`. Tie-breaker rule for any
future config-file decision: per-contributor wins. Hook *scripts*
remain tracked in git; only the activation entry is per-contributor.

**Files touched:** `assets/AGENTS.md`, `assets/dev-setup.md`,
`assets/verify-covers-hook.sh` (new), `SKILL.md`, `CHANGELOG.md`.

**How to apply:**

1. If `.claude/hooks/verify-covers-hook.sh` is absent in the target
   repo, copy it from
   `~/.claude/skills/init-docs/assets/verify-covers-hook.sh` and
   `chmod +x` it. Create `.claude/hooks/` if absent. Skip if present.
   Do **not** modify `.claude/settings.local.json` — activation is
   opt-in per project.

2. In the target repo's `AGENTS.md` § Hard constraints (MUST / MUST
   NOT), check for a paragraph beginning `**Block-maintenance rule.**`.
   If absent, replace the existing intro paragraph (currently begins
   "These are invariants" and ends "phase transitions.") with the
   two-paragraph block from
   `~/.claude/skills/init-docs/assets/AGENTS.md`: the unchanged
   "These are invariants…" sentence plus the new "Block-maintenance
   rule" paragraph. Skip if already present. **Stop with conflict
   report** if the § Hard constraints heading is missing — the
   harness predates ADR 005 and must run that entry's audit first.

3. In the same `## Hard constraints` block, locate the **MUST NOT**
   bullet about editing outside `covers:`. Check for the sentence
   "Before each Edit/Write tool call, verify the target path
   prefix-matches `covers:`." If absent, replace the bullet body with
   the updated version from
   `~/.claude/skills/init-docs/assets/AGENTS.md` (adds the
   pre-call-check sentence and the pointer to `dev-setup.md`
   § Pre-tool-use hook). Skip if the new sentence is already present.
   **Stop with conflict report** if the bullet has been reworded
   beyond recognition.

4. In the target repo's `AGENTS.md` § Session bootstrap, locate item 3
   ("Scan `docs/exec-plans/active/` — what is in flight."). If it
   does not already mention loading `covers:` into working context,
   replace it with the expanded version from
   `~/.claude/skills/init-docs/assets/AGENTS.md`. Skip if the
   `covers:` glob-load sentence is already present.

5. In the target repo's `docs/processes/dev-setup.md`, check for a
   `## Pre-tool-use hook (covers: enforcement)` heading. If absent,
   insert the section between `## Pre-commit hook` and
   `## Common commands` with the contents from
   `~/.claude/skills/init-docs/assets/dev-setup.md`. Skip if present.
   **Stop with conflict report** if either neighbouring heading is
   renamed or missing.

**Stack-specific notes:** The reference hook is bash + jq. Repos
without jq, or that prefer a stack-native implementation (Node hook,
Python hook, Go hook), may swap the script entirely — the contract
documented in `dev-setup.md` § Pre-tool-use hook is what the harness
relies on, not the language. The `.claude/hooks/` placement follows
the Claude Code project-local convention; agents that use a different
hook directory should adjust the path in both the script and the
install snippet. The activation entry lands in
`.claude/settings.local.json` (per-contributor, gitignored) — never
in tracked `.claude/settings.json` — per the new SKILL.md § Notes on
scope → Config-file precedence rule. Entry is deliberately not
auto-merged either way: contributors opt in explicitly.

**Additive/replacing:** mixed. Additive: one new script, one new
`dev-setup.md` section, one new SKILL.md scaffold step (16c), two new
SKILL.md audit-mode steps (5 and 6), one new SKILL.md "How to update"
paragraph. Replacing: the Hard constraints intro paragraph, the
covers: bullet body, the bootstrap item 3.

**Conflict risk:** medium. Surfaces: a target repo whose ADR 005 hard
constraints block has been edited (reworded covers: bullet, removed
intro paragraph), or whose `dev-setup.md` has reorganised the
`## Pre-commit hook` / `## Common commands` boundary. The three
replacing edits are all phrase-level and idempotent (check for the
new sentence before writing). The biggest single edit is the
`dev-setup.md` insertion (new section). All conflicts halt the audit
and leave the marker at the previous entry; the citation check (audit
step 5) and reorder gate (audit step 6) only fire on subsequent
audits after this entry applies.

---

## 2026-05-25 — Auto-critic SubagentStop hook for harness-planner

**What:** Closes the model-policy step 16 hole. The codex plugin's
`/codex:adversarial-review` slash command sets
`disable-model-invocation: true`, so the orchestrator structurally
cannot trigger it from inside a turn — every Phase 5 plan was
silently skipping the critic. Ships a SubagentStop hook
(`.claude/hooks/harness-planner-critic-hook.mjs`) that fires only
when `subagent_type === "harness-planner"`, discovers
`codex-companion.mjs` under `~/.claude/plugins/`, and Bash-spawns
`adversarial-review --background` against the newest file in
`docs/exec-plans/active/`. Detached + unref()'d — the hook returns
in <100ms; the agent turn is never blocked. Per-contributor
activation: hook script is tracked in git; the SubagentStop entry
lives in gitignored `.claude/settings.local.json` so contributors
without `codex-plugin-cc` installed don't trip a dead reference.
Updates `assets/model-policy.md` step 16 row and the
`Pre-approval critic` paragraph in `assets/harness.md` to name the
hook as the auto-invoker and document the bypass procedure.

**Files touched:** `assets/harness-planner-critic-hook.mjs` (new),
`assets/claude-settings-local-fragment.json` (new),
`assets/model-policy.md`, `assets/harness.md`, `SKILL.md`,
`CHANGELOG.md`.

**How to apply:**

1. If `.claude/hooks/` is absent in the target repo, create it. If
   `.claude/hooks/harness-planner-critic-hook.mjs` is absent, copy
   it from
   `~/.claude/skills/init-docs/assets/harness-planner-critic-hook.mjs`
   and `chmod +x` the destination. Skip if present.
   **Do not overwrite** an existing file — flag for user review if
   the contents differ from the asset.

2. Read the target repo's `.claude/settings.local.json` (parse as
   JSON; treat absent file as `{}`). Check for a `hooks.SubagentStop`
   entry whose `command` field contains
   `harness-planner-critic-hook.mjs`. If absent, additively merge the
   fragment from
   `~/.claude/skills/init-docs/assets/claude-settings-local-fragment.json`
   into the parsed object and write back with two-space indent.
   Skip if present. Create the file if absent. **Do not touch other
   keys.** `.claude/settings.local.json` must be gitignored.

3. Check `.gitignore` for a `.claude/settings.local.json` entry (any
   form). If absent, append it. **Stop with conflict report** if
   `.gitignore` is missing entirely (the scaffold should already have
   ensured this elsewhere).

4. In the target repo's `docs/processes/model-policy.md`, locate the
   step 16 row in the "Per-step assignments" table. Check the Notes
   column for the substring `auto-invoked`. If absent, replace the
   row with the version from
   `~/.claude/skills/init-docs/assets/model-policy.md`. **Stop with
   conflict report** if the step 16 row is renamed or the column
   layout changed. Skip if already present.

5. In the target repo's `docs/processes/harness.md`, locate the
   paragraph beginning `**Pre-approval critic (hard, complex plans
   only).**` Check for the substring `auto-invoked` in the same
   paragraph. If absent, append the auto-fire sentence and bypass
   note from
   `~/.claude/skills/init-docs/assets/harness.md` to the end of that
   paragraph. **Stop with conflict report** if the anchor heading or
   paragraph is renamed. Skip if already present.

**Stack-specific notes:** Hook requires Node on `PATH` (shebang is
`#!/usr/bin/env node`). Hook requires `codex-plugin-cc` installed
locally — install with `/plugin marketplace add openai/codex-plugin-cc`
and the plugin's subsequent install step. The hook fails silently
(one stderr line, exit 0) when codex isn't present. To bypass per-
session: temporarily remove or rename
`.claude/hooks/harness-planner-critic-hook.mjs`; to bypass per-
contributor: remove the SubagentStop entry from
`.claude/settings.local.json`.

**Additive/replacing:** additive — one new script, one new fragment
asset, one step 16 row replacement (semantically the same), one
appended sentence to the critic paragraph, one `.gitignore` line.

**Conflict risk:** low. Surfaces: a target repo that has already
defined `hooks.SubagentStop` in `.claude/settings.local.json` for
something else (step 2 handles via additive array push — but if the
file's shape is malformed, abort and ask). Step 4 hard-stops on
renamed/reordered model-policy table; step 5 hard-stops on renamed
critic paragraph. No edit outside `.claude/`, `docs/processes/`, and
`.gitignore`.

---

## 2026-05-24 — Typed design subagents (harness-analyst, harness-planner) with pre-write gates

**What:** Ships two project-level subagent configs under `.claude/agents/`
— `harness-analyst` (Phase 2 analysis synthesis) and `harness-planner`
(Phase 5 complex ExecPlan drafting). Both enforce a typed brief
contract: missing any required field → subagent replies
`MISSING_FIELDS: [...]` and refuses to write. The orchestrator owns
candidate-path identification and brief construction; the subagent owns
the synthesis Write to `docs/analysis/...` and
`docs/exec-plans/active/...`. Adds a hard pre-write gate: the
orchestrator may never Write/Edit those paths (under the complex
threshold for plans). Pre-approval critic on complex plans becomes
mandatory. Encodes the binding complexity threshold in
`docs/processes/dev-setup.md` § Complexity threshold (project-specific
definition) and audits it via a new `module-count:` ExecPlan frontmatter
field. Adds copy-pasteable `Task(...)` call shapes to `AGENTS.md` for
both subagents, including the explicit `model: "opus"` override (so
harness-log lines render `[opus]` instead of `[default]` and the policy
is auditable from the log). Documents the hook-tag caveat: in-subagent
tool events render with the orchestrator's `session_model` prefix; only
the `SUBAGENT` launch line authoritatively reflects the subagent's
model.

**Files touched:** `assets/harness-analyst.md` (new),
`assets/harness-planner.md` (new), `assets/AGENTS.md`,
`assets/harness.md`, `assets/model-policy.md`,
`assets/exec-plan-template.md`, `assets/dev-setup.md`, `SKILL.md`,
`CHANGELOG.md`.

**How to apply:**

1. If `.claude/agents/` is absent in the target repo, create it. If
   `.claude/agents/harness-analyst.md` is absent, copy it from
   `~/.claude/skills/init-docs/assets/harness-analyst.md`. Skip if
   present. Same for `.claude/agents/harness-planner.md`.

2. In the target repo's `AGENTS.md` `## Phase gates` section, locate
   the bullet starting "Phase 2 synthesis, phase 4 broad/irreversible
   ADRs, and phase 5 multi-module ExecPlans invoke the design
   subagent". If it still reads "the design subagent" (singular,
   untyped), replace it and append the follow-on bullets and the
   "Concrete delegation, copy-pasteable" subsection with the contents
   from `~/.claude/skills/init-docs/assets/AGENTS.md`. The new content
   covers: typed subagent names (`harness-analyst`, `harness-planner`);
   threshold pointer to `dev-setup.md`; pre-write gate; copy-pasteable
   `Task(...)` call shapes with the explicit `model: "opus"` override;
   MISSING_FIELDS contract; hook-tag caveat. Skip if the bullet already
   reads "a typed design subagent" and the `Task(...)` shapes are
   already present. **Stop with conflict report** if the bullet has
   been reworded beyond recognition.

3. In the target repo's `docs/processes/harness.md` § Phase 2, check
   for the orchestrator/subagent split table immediately after "The
   investigation produces an analysis doc." If absent, replace the
   opening paragraph and insert the four-row table (Identify candidate
   paths / Construct typed brief / Synthesis / Catalog row) with the
   contents from `~/.claude/skills/init-docs/assets/harness.md`. Then
   replace the "Synthesis of the analysis doc invokes the design
   subagent..." paragraph (if still present) with the "Pre-write gate
   (hard)" paragraph. Skip each individually if already present.

4. In the target repo's `docs/processes/harness.md` § Phase 5, check
   for the "Complexity threshold (binding)" paragraph and the
   orchestrator/subagent split table. If absent, replace the "Drafting
   a multi-module ExecPlan invokes the design subagent" sentence with
   the `harness-planner` version, then insert the threshold paragraph,
   the five-row table, the "Pre-write gate (hard)" paragraph, and the
   "Pre-approval critic (hard, complex plans only)" paragraph from
   `~/.claude/skills/init-docs/assets/harness.md`. Skip each
   individually if already present.

5. In the target repo's `docs/processes/model-policy.md`:
   - Steps 15 and 16 of the per-step table: append "Threshold below."
     to step 15's Notes column and "Mandatory on complex plans;
     skipped on simple." to step 16's Notes column if not already
     present.
   - Check for a `## Complex vs simple ExecPlan threshold` section
     between the per-step table and `## Codex commands reference`. If
     absent, insert it with the contents from
     `~/.claude/skills/init-docs/assets/model-policy.md`. The section
     points to `dev-setup.md` for the project-specific definition and
     names the contract the definition must satisfy.

6. In the target repo's `docs/exec-plans/_template.md` frontmatter,
   check for a `module-count:` line. If absent, insert it immediately
   below `covers:` with the comment from
   `~/.claude/skills/init-docs/assets/exec-plan-template.md`. Skip if
   present.

7. In the target repo's `docs/processes/dev-setup.md`, check for a
   `## Complexity threshold` section. If absent, insert it immediately
   before `## Evaluator convention` with the placeholder contents from
   `~/.claude/skills/init-docs/assets/dev-setup.md`. Flag it as
   "needs filling" in the audit report. The section is a placeholder
   by design — each project supplies its own threshold (typical shapes
   provided as examples).

**Stack-specific notes:** The complexity-threshold definition is
intentionally placed in `dev-setup.md` rather than the universal docs
because the right rule depends on the project's directory layout. The
ms-search reference implementation uses: "≥2 directories under
`internal/modules/`, OR ≥2 of `internal/router`, `internal/app`,
`internal/container`, `internal/config`." Treat as example only —
NestJS, Python, Rust, or any other layout supplies its own rule
following the contract in `model-policy.md` § Complex vs simple
ExecPlan threshold. The `module-count:` frontmatter field is universal;
only the threshold definition is stack-specific.

**Additive/replacing:** mixed. Additive: two new subagent files, the
`module-count:` frontmatter field, the `Complex vs simple ExecPlan
threshold` section in `model-policy.md`, the `Complexity threshold`
section in `dev-setup.md`, the orchestrator/subagent split tables in
`harness.md` Phase 2 and Phase 5, the pre-write gate paragraphs, the
pre-approval critic paragraph, the `Concrete delegation` subsection in
`AGENTS.md`. Replacing: the "design subagent" wording in `AGENTS.md`
and `harness.md` Phase 2 and Phase 5 (singular/untyped → typed
subagent names); two Notes-column cells in `model-policy.md` per-step
table.

**Conflict risk:** medium. Surfaces: a target repo that has reworded
the "Phase 2 synthesis, phase 4 broad/irreversible ADRs..." bullet,
the "Synthesis of the analysis doc invokes the design subagent..."
sentence, the "Drafting a multi-module ExecPlan invokes the design
subagent" sentence, or restructured sections in `model-policy.md` /
`dev-setup.md`. The `AGENTS.md` `Task(...)` insertion is the largest
single edit; verify the post-insertion structure with a re-read before
advancing the marker. The `dev-setup.md` insertion point is between
two named sections — stop and ask if either heading is missing or
renamed.

---

## 2026-05-22 — Hard constraints (MUST / MUST NOT) block in AGENTS.md

**What:** Introduces a new top-level section in `AGENTS.md` titled
`## Hard constraints (MUST / MUST NOT)`, placed immediately after
`## Operating principle` and before `## Phase gates`. The block holds
*invariants* — rules that apply at every moment of every phase — as
distinct from phase gates, which fire only at transitions. Each bullet
is prefixed with the loud label **MUST** or **MUST NOT** and cites
the ADR or section that justifies it. Initial five constraints: WIP=1
on ExecPlans (at most one plan in `active/`, guide-only override via
displaced plan's Decision Log), no edits outside the current plan's
`covers:` during execution, no opportunistic refactor before the
plan's `verify-cmd` shows green, no chat-only load-bearing knowledge,
and an explicit MUST to surface — not silently comply with —
instructions that conflict with a rule. Reorders `AGENTS.md`
sections per the position-effect finding: principle → constraints →
gates → on-receiving-task → bootstrap → output-routing → tone. Removes
the trailing silent-compliance sentence from `## Phase gates`
(subsumed by the broader constraint). Ships ADR 005 recording the new
category, the initial five constraints, and the locked section order.

**Files touched:** `assets/AGENTS.md`,
`assets/005-hard-constraints.md` (new), `SKILL.md`, `CONTEXT.md`,
`CHANGELOG.md`.

**How to apply:**

1. Check the target repo's `docs/decisions/` for any ADR titled
   "Hard constraints" (any number). If absent, find the next
   available `NNN` — default `005` if free, otherwise the next free
   number — and copy
   `~/.claude/skills/init-docs/assets/005-hard-constraints.md` to
   `docs/decisions/NNN-hard-constraints.md`. If `NNN ≠ 005`, rewrite
   the heading `# ADR 005 — …` and every in-body `ADR 005` mention
   to the chosen number. Record the chosen NNN for steps 2 and 5.

2. In the target repo's `AGENTS.md`, check for a
   `## Hard constraints (MUST / MUST NOT)` heading. If absent,
   insert the entire block from
   `~/.claude/skills/init-docs/assets/AGENTS.md` (the five
   loud-labelled bullets plus the intro paragraph) between
   `## Operating principle` and `## Phase gates`. Rewrite the four
   in-block `ADR 005` citation links to the NNN chosen in step 1 if
   different. Skip the entire step if the heading is already
   present. **Stop with conflict report** if `## Operating principle`
   or `## Phase gates` is renamed, missing, or non-detectable.

3. In the target repo's `AGENTS.md` `## Phase gates` section, check
   for the standalone sentence: "If a user instruction conflicts
   with these gates, say so before complying. Do not silently
   comply." If present as its own paragraph or trailing line in
   the section, remove it (subsumed by hard constraint #5). Skip
   if absent. **Do not** delete the sentence if it has been
   reworded or moved — surface a conflict and stop.

4. In the target repo's `AGENTS.md`, reorder the top-level sections
   to: `## Operating principle`, `## Hard constraints (MUST / MUST
   NOT)`, `## Phase gates`, `## On receiving a task`,
   `## Session bootstrap`, `## Where to save outputs`,
   `## Working relationship`. **Stop with conflict report** if any
   of these seven headings is renamed, missing, or duplicated.
   Skip if the order already matches.

5. In the target repo's `docs/README.md` § Decisions, check for the
   new ADR catalog entry. If absent, append a one-line entry for
   the NNN chosen in step 1, e.g.:
   `- [ADR NNN — Hard constraints](decisions/NNN-hard-constraints.md) — #ai-harness #plan`
   Skip if present.

**Stack-specific notes:** None. The block is stack-agnostic — it
constrains agent behaviour, not the project's language or toolchain.
WIP=1 is enforced by guide-only discipline; no folder reorganisation
(no `paused/`) or frontmatter additions (no `status: paused`) are
introduced. The displaced-plan Decision Log entry is the only
required trace on a WIP override.

**Additive/replacing:** mixed. Additive: one new ADR, one new
`AGENTS.md` section, one new catalog entry. Replacing: a section
reorder in `AGENTS.md` (step 4) and a one-sentence removal from
`## Phase gates` (step 3).

**Conflict risk:** high. Step 4 (the reorder) is the riskiest single
upgrade step in the skill to date — any rename, reorder, or
restructure of the seven top-level sections in `AGENTS.md` aborts
the audit and leaves the marker untouched. Step 3 (sentence
removal) is also a surface — if the sentence has been reworded the
audit must stop rather than guess. The ADR-numbering branch in step
1 follows the same convention as ADR 003 and ADR 004 entries: pick
the next free number and rewrite cross-references.

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
