# init-docs

Glossary for the init-docs skill — the harness-scaffolding artifact that seeds `docs/`, `AGENTS.md`, and operating manuals into a fresh repo.

## Language

**Feature**:
A coarse user-observable capability of the product, paired with a verification command that resolves to a tagged subset of tests (one feature, N tests).
_Avoid_: test, behavior, story, requirement (each names only one facet)

**Feature state**:
One of `not_started / active / blocked / failing / passing`. Writers are partitioned: humans set `not_started` (on creation) and `blocked` (with a one-line reason); plan-approval flow sets `active`; the verifier loop alone sets `passing` and `failing`. **Session exit** triggers a verifier run as part of its checklist — the verifier still writes the state, but session exit is one of its callers (alongside CI, watch mode, manual invocation). `passing → failing` is a regression; there is no transition back to `not_started`.

**Worker/checker split**:
The principle that no agent certifies its own work. A *worker* is the agent that produces an artifact (a plan, a feature state, code); a *checker* is whoever or whatever certifies it as done. The two roles must be distinguishable in the harness — either different sessions, different skills, or a deterministic tool. The harness has two concrete enforcers today: (1) the verifier loop owns FEATURES.md `passing` writes (ADR 002); (2) the **Evaluator** owns the `active/` → `completed/` transition for ExecPlans. Future enforcers must declare which side they sit on.

**Evaluator**:
The checker for ExecPlan completion. A role played by any coding agent or tool that does not share state with the plan's worker (fresh subagent, separate session, external CLI agent like Codex, human reviewer). The harness names the role and the artifact it must produce — an **Evaluator transcript** — but the consuming repo names the concrete tool in `dev-setup.md` next to the verifier convention. Independence is the load-bearing property: same agent, same session, same context does not qualify.
_Avoid_: "reviewer" (overloaded with human PR review), "judge" (overloaded with LLM-as-judge benchmarking).

**Evaluator invocation contract**:
Universal shape `<evaluator-cmd> <plan-path>`. The Evaluator reads the plan plus the working tree it references, then writes its verdicts into a dedicated **Evaluator transcript** section *inside the plan file itself*. The worker that produced the plan never edits that section — independence is structural (different writer, different context), not convention-only. The worker then reads the section it didn't write, parses verdicts, and decides whether to move the plan to `completed/`. Pattern is analogous to the existing `verify-cmd:` / `verify:` contract for Features.

**Pre-approval critic**:
The checker for ExecPlan *approval* — the worker/checker split applied at
the draft→approved phase boundary, paralleling [[evaluator]] at active→completed.
Same independence requirement as the Evaluator (different model family,
different context). Default tool is `codex:adversarial-review` (the slash
command name); the hook invokes the underlying `codex-companion.mjs
adversarial-review` script via Bash because the slash command itself sets
`disable-model-invocation: true`. Fallback chain per `model-policy.md`
§ Fallback (fresh Claude subagent, then human reviewer). Auto-fired by
`.claude/hooks/harness-planner-critic-hook.mjs` on `harness-planner`
SubagentStop. Mandatory on every ExecPlan — there is no complexity
threshold; the worker/checker split is unconditional at this gate
(ADR 006).
_Avoid_: "reviewer" (overloaded with human PR review).

**Pre-approval critic transcript**:
The artifact the [[pre-approval-critic]] writes into the plan file at a
dedicated `## Pre-approval critic transcript` section, paralleling
[[evaluator-transcript]] at completion. The worker (orchestrator) never
edits this section — independence is structural, not convention-only.
Phase 5 gate: the lead does not approve a plan whose section is empty
or BLOCKED. Hook failure modes (codex plugin missing, codex crash) write
a `BLOCKED: <reason>` placeholder into the section so the empty-section
gate fires loudly instead of silently.

**Evaluator scope**:
What the Evaluator certifies. Two required verdicts and one optional:
1. **Alignment** (required) — the diff implements what the plan's Plan-of-Work and Concrete Steps said it would. Catches scope drift and silent omissions.
2. **Acceptance** (required) — the plan's Validation & Acceptance criteria were actually verified, with evidence (test transcripts, observable outputs).
3. **Quality** (optional) — code-quality review, on by default for plans tagged `security`/`auth`/`payments`-adjacent or whenever the consuming repo configures it. A failing quality verdict is *not* a completion blocker by itself; it routes to `docs/tech-debt-tracker.md`.

Code-quality review at large is the maintainability harness's job (linters, `/review`); folding it into the completion gate would conflate two sensors and block plan closure on style misses.

**Verification (`verify:` / `verify-cmd:`)**:
Every **Feature** declares how it is checked at creation time. `verify:` holds a tag selector (e.g. `feat:checkout`) interpreted by a stack-specific convention documented in `dev-setup.md` ("how this repo runs its test command with a tag filter"). `verify-cmd:` is the escape hatch — a literal shell string — used only when the tagged-test convention does not apply. Exactly one of the two is required; presence is non-negotiable even for `not_started` features.

**Feature provenance (`source:`)**:
Every **Feature** row records where it came from — `brief`, `prd:<path>`, `analysis:<path>`, or `inferred`. Defuses free-form bloat without imposing a phase gate on Feature creation itself.

**Orchestrator**:
The agent owning the main session loop and continuity across phases. Default
model: Sonnet 4.6 high. Delegates synthesis-heavy work to the design subagent
and verification to checker commands.

**Design subagent**:
Opus 4.7 xhigh invoked from the orchestrator for the harness's design surfaces:
analysis-doc synthesis (phase 2), broad/irreversible ADRs (phase 4),
ExecPlans (phase 5 — all plans, no complexity threshold). Receives a
self-contained brief from the orchestrator; writes the artifact in place;
returns a one-paragraph summary. Reasoning is opaque to the orchestrator by
design.

**Checker / rescue tier**:
GPT-5.5 high invoked via the codex plugin. Two roles share the tier because
both require structural independence from the orchestrator: *checker*
(Evaluator, pre-approval critic, diff sanity) reads and verdicts without
writing code; *rescue* (`codex:codex-rescue` subagent) implements when the
orchestrator is stuck. Independence is achieved by being a different model
family, not just a different context window. The codex-plugin-cc slash
commands set `disable-model-invocation: true`, so the orchestrator reaches
the checker side through `codex-companion.mjs` via Bash and the rescue side
through the `Agent` tool with `subagent_type="codex:codex-rescue"`. See
`model-policy.md` § Codex commands reference.

**Model policy**:
Fleet-wide per-step model assignments at `docs/processes/model-policy.md`.
Breaks the harness's prior model-agnosticism deliberately so that telemetry
compounds across scaffolded repos. Enforced by reading order + steering loop,
not by mechanical sensor.

**Hard constraint**:
A repo-wide invariant that applies at every moment of every phase, distinct from a [[phase-gate]] (sequencing rule, fires only at transitions). Hard constraints sit in a `## Hard constraints (MUST / MUST NOT)` block immediately below `## Operating principle` in AGENTS.md, loud-labelled per item, each citing an ADR. Initial set (ADR 005): [[wip]]=1 on ExecPlans, no edits outside `covers:` during execution, no opportunistic refactor before verifier-green, no chat-only knowledge, no silent compliance with rule violations. The load-bearing motivation is the prose-equivalence problem — philosophical text and MUST NOTs look identical to a model without the loud label.
_Avoid_: "guideline" (soft, no label), "phase gate" (different category, see below).

**Phase gate**:
A sequencing rule that fires at the transition between phases — "X must precede Y". Distinguishable from a [[hard-constraint]] (invariant, at all times). Examples: no code without an approved ExecPlan (phase 5→6), no plan moves to `completed/` without an Evaluator transcript (phase 6 → close). Lives in `## Phase gates` in AGENTS.md, below the hard constraints block.
_Avoid_: "hard constraint" (invariants, not transitions); "checkpoint" (overloaded with CI usage).

**WIP**:
Work-in-progress counter, applied at the ExecPlan level. At most one plan in `docs/exec-plans/active/` at a time (a [[hard-constraint]], ADR 005). Features inherit the bound — a Feature is in scope of zero or one active ExecPlan. Analyses are not counted; parallel investigation is cheap and encouraged. Override is guide-only: the agent surfaces the WIP collision; on user approval (hotfix, blocked-on-external, scope split), the displaced plan gets a one-line Decision Log entry recording the pause and reason before the new plan opens. No `paused/` folder, no `status: paused` frontmatter — the harness avoids new state where conversational discipline suffices.

**Session bootstrap**:
The protocol an agent runs at the start of every session: read FEATURES.md, the catalog, active plans, decisions, model policy, harness-version marker, and only the docs whose tags match the current task. Documented in `AGENTS.md` § Session bootstrap. Distinct from [[bootstrap-contract]] (the *property* "this repo can be operated") and from [[session-exit]] (the clock-out half of the same symmetry). Bootstrap is per-session; the contract is per-scaffold/audit; cold-start test is per-quarter.
_Avoid_: conflating with "initialization" (per-repo, one-time-or-audit) or "onboarding" (per-human, one-time).

**Bootstrap contract**:
The property "this repo can be operated by a fresh agent." Four conditions, each mapped to a concrete surface: *can start* → `dev-setup.md` § Common commands + § Running locally; *can test* → `dev-setup.md` § Common commands (Run tests) + § Feature verification convention; *can see progress* → `FEATURES.md` + `exec-plans/active/` + `docs/README.md`; *can pick up next steps* → `FEATURES.md` § Active|Failing + `exec-plans/active/` + `tech-debt-tracker.md`. Verified at the end of every `/init-docs` run (Step 18 closing section). Two-level pass: a *surface* is the artifact's existence (mechanically checkable post-scaffold); *populated* is the artifact carrying non-placeholder content. A fresh scaffold satisfies all surfaces; populated status reflects whether the user has filled in dev-setup.md yet. Distinct from [[session-bootstrap]] (insider protocol — what an agent reads at session start) and [[cold-start-test]] (quarterly legibility ritual).
_Avoid_: "initialization checklist" as the verdict name — the checklist is the documentation file; the contract is the property being verified.

**Cold-start test**:
A quarterly falsifier ritual that probes [[bootstrap-contract]] *legibility* (qualitative), not just operability (binary). Five questions — what is the system / how organised / how to run / how to verify / where are we now — answered in a NEW agent session using repo content only (Operating principle). Output is appended as a new top section to a single rolling log at `docs/generated/cold-start-test.md`, newest-first, one section per run with heading `## YYYY-MM-DD — Qn`. Drift across sections is a steering-loop input; a question the agent cannot answer means the repo is no longer the spec for that surface. Soft cadence: at least quarterly; sooner on major restructure, onboarding pain, or ADR supersession. Human-initiated, document-only ritual — no slash command, no automation, no mechanical coupling to other rituals (matches the same docs-only posture as Session exit).

## Relationships

- A **Feature** is verified by one or more tests, addressed via a single tagged subset command (`#suite-tag` / `--grep feat:<id>` / equivalent).
- A **Feature** is *in scope* of zero or one active **ExecPlan**; once delivered, its passing state is owned by the verifier loop, not by the plan.
- **Feature state** ownership reflects the worker/checker split: the agent writing or executing a plan never writes `passing` itself.
- An **ExecPlan** carries a `features:` frontmatter list. It is non-optional: either non-empty (every ID must resolve to a row in FEATURES.md) or empty + `feature-less-reason: <one line>` declaring the plan ships no user-observable behavior. Approving the plan sets each referenced Feature to `active`; landing in `completed/` hands state back to the verifier loop.
- Creating a Feature is not harness-gated — no analysis required. Features are the *input* to the analysis/plan flow, not the output.

**FEATURES.md**:
The repo-wide ledger of **Features**, stored as `docs/FEATURES.md`. Markdown sections (one per non-passing state, plus a single `Passing` bulk section) over markdown tables with fixed columns `ID | Behavior | Verify | State | Source | Notes`. No JSON schema, no parser, no verifier script — guides-only, consistent with the rest of the skill's "scripts deferred to the project" posture.

**Session**:
One agent conversation, bounded by the user opening and closing the chat (or compaction). May contain zero, one, or many **ExecPlans**, or pure investigation with none. Distinct from a plan: Phase 6 closes a plan; **Session exit** closes a session. The two concepts overlap only when the session contains exactly one plan that finishes inside it.
_Avoid_: "run", "task" (each names a sub-unit, not the conversation envelope).

**Session exit**:
The clock-out half of the harness's symmetry with **Session bootstrap**. A six-dimension checklist run on explicit user signal ("we're done", "ttyl", "/session-exit"): build / verifier / plan state / doc coherence / startup viable / chat-knowledge sweep. Auto-fixes the mechanical, surfaces judgment items, blocks-with-flag on build-red or verifier regression. Output lands in existing artifacts (Progress sections, `docs/README.md` index, FEATURES.md, tech-debt-tracker, ADR drafts) — no dedicated session log. Triggers a verifier run; pre-existing failures are reported but not blocking, regressions are blocking. Cannot be mechanically enforced — the harness names the convention and makes it the easiest path.

## Flagged ambiguities

- "feature" was briefly conflated with "acceptance test" — resolved: a feature is the user-visible capability; acceptance tests are its evidence. Multiple tests per feature is normal.
