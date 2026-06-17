---
id: pre-approval-critic-gate
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-05-27
update_trigger: on-supersession
---

# ADR pre-approval-critic-gate — Pre-approval critic gate

## Status

Accepted; supersedes the simple/complex ExecPlan threshold introduced in the
2026-05-24 changelog entry (Phase 5 split between orchestrator-written simple
plans and subagent-written complex plans, with the critic conditional on the
complex tier).

## Context

The harness applied the worker/checker split asymmetrically across the
ExecPlan lifecycle. At *completion* (active → completed), ADR evaluator-gate made the
Evaluator pass unconditional — every plan, regardless of size or risk, gets an
independent verdict before the file moves. At *approval* (draft → approved),
the pre-approval critic was conditional on a project-defined "complex"
threshold in `docs/processes/dev-setup.md`. Simple plans were drafted by the
orchestrator with no independent pre-approval check at all.

That asymmetry has three problems.

First, the threshold itself is ambiguous. Module-count is auditable, but the
"high-risk or irreversible single-module plans (data migrations, auth-path
rewrites, public-API contract changes) are also complex regardless of module
count" override is a judgment call that depends on a list the harness cannot
enumerate in advance. Borderline cases default to complex per the threshold
contract, but the borderline judgment itself is made by the same agent that
would benefit from skipping the critic. The "ambiguity could wrongly leave one
review out" failure mode is structural, not a documentation gap.

Second, the simple-tier path violates the worker/checker split named in
`docs/processes/CONTEXT.md` and reinforced by ADR evaluator-gate. When the orchestrator
drafts a plan and the orchestrator advances it to lead-approval with no
independent check in between, the orchestrator is certifying its own work.
The lead's review at approval-time is the checker — but the lead is reviewing
the *plan output*, not the *plan-construction process*; a flawed approach
embedded in a well-written draft slips through.

Third, the asymmetry between completion-side Evaluator (mandatory) and
approval-side critic (conditional) is hard to explain. Future contributors
reasonably ask "why do we always evaluate at completion but only sometimes
critique at approval?" The clean answer is that we shouldn't.

The cost lever was the original justification for the threshold — running
design-subagent synthesis plus checker-tier adversarial-review on every plan
is more expensive than the orchestrator-only path. That cost is real but
bounded: an ExecPlan is a low-frequency artifact (single-digit plans per week
in a typical repo); the marginal cost is dominated by execution and CI, not
by the planning step. Critic-skipped-when-it-was-needed is an asymmetric
failure with no upper bound on downstream impact.

## Decision

Introduce the **Pre-approval critic transcript** artifact and make the
pre-approval critic pass unconditional. The simple/complex threshold is
removed entirely from the harness vocabulary.

**Role.** The Pre-approval critic is a reading-only checker for ExecPlan
draft-quality, played by any coding agent or tool that does not share state
with the plan's worker — fresh subagent, separate session, external CLI
agent (Codex, equivalents). Independence is the load-bearing property: same
agent, same session, same context does not qualify. The role is structurally
parallel to the [Evaluator](003-evaluator-gate.md) but operates at the
draft → approved phase boundary rather than active → completed.

**Default tool.** `codex:adversarial-review`, per
[model policy](../processes/model-policy.md) row 15. The slash command
sets `disable-model-invocation: true`, so the hook invokes the underlying
`codex-companion.mjs adversarial-review` script directly via Node rather
than the slash command. Fallback chain per model policy § Fallback applies
when codex-plugin-cc is unavailable.

**Invocation contract.** The critic is auto-fired by
`.claude/hooks/harness-planner-critic-hook.mjs` on `harness-planner`
SubagentStop. The hook spawns the critic synchronously and writes its
verdict directly into the plan's `## Pre-approval critic transcript`
section. The worker (orchestrator) never edits that section — independence
is structural, not convention-only.

**Verdict shape.** A single block per run, appended to the section:

    **Run N — YYYY-MM-DD HH:MMZ — <critic-cmd>**

    <critic verdict body — challenges, hidden assumptions, sequencing
    issues, rollback concerns, alternative-approach questions>

The block is free-form prose; unlike the Evaluator's structured Alignment +
Acceptance verdicts, the critic's purpose is *challenge*, not pass/fail
adjudication. The lead reads the section and decides whether the challenges
materially affect the plan before approving.

**Failure modes.** When the hook cannot run the critic (codex-plugin-cc not
installed, codex spawn failure, codex timeout, codex non-zero exit), it
writes a `BLOCKED: <reason>` placeholder into the section *in place of* a
verdict. The empty-section gate (below) fires loudly on BLOCKED placeholders
the same way it fires on missing sections — the lead does not approve a
plan whose critic transcript is empty or BLOCKED.

    **Run N — YYYY-MM-DD HH:MMZ — codex:adversarial-review**

    BLOCKED: codex-plugin-cc not installed on this contributor's machine.
    Install per docs/processes/dev-setup.md § Toolchain, or run the critic
    out-of-band and paste the verdict here before requesting lead approval.

**Approval gate.** The lead does not move a plan from `status: draft` to
`status: approved` while the `## Pre-approval critic transcript` section is
empty or contains only BLOCKED placeholders. This is a guide-level gate
enforced by lead discipline, parallel to the Evaluator's completion gate.
The pre-commit plan-coverage sensor is unchanged; this gate sits earlier in
the lifecycle.

**Iteration cap.** The pre-approval critic runs at most twice on the
same plan. After Run 2, the hook refuses to spawn codex and writes a
`CAP_REACHED:` block into the transcript naming the three exit paths
the lead must choose between:

1. *Ship with residuals.* Append unresolved findings to the Decision
   Log as accepted residuals, with rationale.
2. *Scope-split.* Create a new ExecPlan for the shipping slice; the
   deferred work returns to Phase 2 for a fresh analysis. The new
   plan starts a fresh critic counter.
3. *Escalate to re-analysis.* The critic surfaced an unresolved
   design question. Halt Phase 5, amend the analysis doc, then
   re-dispatch harness-planner under reset scope.

The cap exists because a critic that keeps finding *new* defect
categories on each pass is signalling a scope problem, not a
convergence opportunity. Each Run+revision pair costs one Opus
synthesis plus one checker-tier adversarial-review plus the
orchestrator's token spend reading both; three rounds is roughly the
same cost as planning three independent plans. Past two rounds the
loop is anti-convergent on average.

Override: re-dispatch harness-planner with
`HARNESS_CRITIC_FORCE="<reason>"` in the env. Use only when the
re-dispatch carries genuinely new scope (e.g. after a scope-split
landed and a sibling plan opens), not when the iteration is the same
scope under a different prompt. The reason is logged in the
`CAP_REACHED` block for review.

**No simple-tier exception.** Every ExecPlan flows through `harness-planner`
on design-subagent and through the critic on checker-tier via the codex
plugin (or the fallback chain). The `simple` and `complex` terms are
removed from the harness vocabulary; the `module-count:` frontmatter field
is dropped (it existed to make the threshold auditable; with no threshold,
nothing audits it).

**Phase 4 ADRs are not affected.** The same reasoning does *not* extend to
Phase 4 decision documents. Decisions are judgment calls; the lead is the
canonical checker for judgment. A critic pass on every inline decision
would produce noise that trains the lead to ignore critic output, defeating
the gate's purpose. Inline decisions are covered indirectly by sitting
inside the plan that the critic reads; broad/irreversible ADRs continue to
go through the design subagent without a separate critic pass. This
asymmetry is principled, not lazy.

## Consequences

The positive consequence is structural symmetry of the worker/checker split
across both ExecPlan phase boundaries. The harness now applies the same
doctrine — "no agent certifies its own work" — at draft → approved and at
active → completed. The Evaluator transcript and Pre-approval critic
transcript share a section-as-gate pattern that future contributors learn
once and apply twice. The threshold ambiguity is gone; no plan can slip
past the critic by being judged "simple."

The cost consequence is one design-subagent synthesis plus one checker-tier
critic pass per ExecPlan, with no opt-out. ExecPlans are low-frequency, so
the absolute cost is bounded, but the change is monotonic — there is no
fallback to "skip the expensive path." Cost telemetry feeds the steering
loop; if a project finds the marginal cost unjustified, the steering-loop
response is to reduce ExecPlan frequency (e.g. fold related work into
fewer plans), not to reintroduce a skip path.

The hook becomes load-bearing in a way it wasn't before. Yesterday's design
treated the auto-critic hook as a convenience layered on top of the
"orchestrator must invoke" guide; the hook's failure mode was silent skip.
Under this ADR, hook failure writes a visible BLOCKED placeholder that the
lead must address before approval. The hook is still per-contributor
opt-in (activation in `.claude/settings.local.json`, gitignored); a
contributor without the hook installed gets a plan whose critic section
needs to be populated manually before approval. This is intentional: the
fleet rule that hook activation is per-contributor (CHANGELOG 2026-05-25
"Block-maintenance" entry) is not overridden by this ADR. The named-section
gate makes the manual-vs-auto distinction visible at review time, which is
where it matters.

The hook implementation changes from background-detached to synchronous.
The agent's turn pauses for the duration of the critic run (typically
30–90s on a non-trivial plan). The pause is at the draft → approval
transition where nothing else is happening; the trade is visible latency
for a populated verdict on first read.
