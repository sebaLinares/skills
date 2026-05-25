# Fleet Model Policy

This policy is fleet-wide and not project-configurable. It names the model
assignments for the harness so that failures and improvements can be compared
across scaffolded repos. ADR 004 records the rationale.

## Tiers

| Tier | Current model | Role |
|---|---|---|
| Orchestrator | Sonnet 4.6 high | Owns the main session loop, repo continuity, artifact routing, and ordinary edits. |
| Design subagent | Opus 4.7 xhigh | Handles synthesis-heavy design surfaces where marginal reasoning capability matters. |
| Checker / rescue | GPT-5.5 high via codex plugin | Provides structurally independent review, verification, rescue, and async result harvest. |

## Per-step assignments

| Step | Phase | Tier | Invocation | Notes |
|---|---|---|---|---|
| 1 | Session bootstrap | Orchestrator | Main session | Read `AGENTS.md` and complete the repo bootstrap. |
| 2 | Scope surface | Orchestrator | Main session | Read `docs/FEATURES.md` and map the brief to Feature IDs or a feature-less reason. |
| 3 | Catalog scan | Orchestrator | Main session | Read `docs/README.md` and select only relevant tagged docs. |
| 4 | Active-plan scan | Orchestrator | Main session | Inspect `docs/exec-plans/active/` for overlap. |
| 5 | Decision scan | Orchestrator | Main session | Inspect `docs/decisions/` for binding ADRs. |
| 6 | Model policy read | Orchestrator | Main session | Read this file before the harness-version check. |
| 7 | Harness-version check | Orchestrator | Main session | Compare `.harness-version` with the init-docs changelog head. |
| 8 | Phase 1 brief capture | Orchestrator | Main session | Restate the brief and ensure Feature coverage. |
| 9 | Phase 2 investigation | Orchestrator | Main session | Gather code and doc context for the analysis doc. |
| 10 | Phase 2 synthesis | Design subagent | Claude Task tool, Opus 4.7 xhigh | Synthesize the analysis doc from a self-contained brief. |
| 11 | Phase 3 findings review | Orchestrator | Main session | Apply lead feedback and resolve or defer open questions. |
| 12 | Phase 4 scoped decisions | Orchestrator | Main session | Record plan-local decisions inline. |
| 13 | Phase 4 broad or irreversible ADRs | Design subagent | Claude Task tool, Opus 4.7 xhigh | Draft ADRs with cross-plan or hard-to-reverse scope. |
| 14 | Phase 5 simple ExecPlan | Orchestrator | Main session | Draft single-module or straightforward plans. |
| 15 | Phase 5 complex ExecPlan | Design subagent | Claude Task tool, Opus 4.7 xhigh | Draft multi-module, high-risk, or irreversible plans. Threshold below. |
| 16 | Pre-approval critic | Checker / rescue | `codex:adversarial-review` | Review draft plans before human approval. Mandatory on complex plans; skipped on simple. |
| 17 | Phase 6 execution | Orchestrator | Main session | Execute approved plan steps and update progress. |
| 18 | Mid-execution diff sanity | Checker / rescue | `codex:review` | Request when the diff grows broad, risky, or surprising. |
| 19 | Rescue implementation | Checker / rescue | `codex:rescue` | Use when the orchestrator is stuck or needs an independent implementation attempt. |
| 20 | Async result harvest | Checker / rescue | `codex:result` | Collect codex plugin results after async checker or rescue work. |
| 21 | Completion Evaluator | Checker / rescue | `codex:adversarial-review --base <merge-base>` | Default Evaluator command before moving a plan to `completed/`. |
| 22 | Session exit and steering loop | Orchestrator | Main session | Run close-out, then route model drift through the steering loop. |

## Complex vs simple ExecPlan threshold

Binding for steps 15 and 16.

The project-specific definition of *complex* lives in
`docs/processes/dev-setup.md` § Complexity threshold. The contract
the threshold must satisfy:

- Phrased in terms of modules / packages / core infrastructure files
  the plan touches — auditable from the plan's `covers:` frontmatter
  without re-reading the body.
- High-risk or irreversible single-module plans (data migrations,
  auth-path rewrites, public-API contract changes) are also complex
  regardless of module count.
- Borderline cases default to complex — the design-subagent cost is
  bounded; a wrong-tier synthesis is not.

Plans declare the count in frontmatter as `module-count: <N>` so the
classification is auditable from `docs/exec-plans/` without re-reading
the body.

Anything below the bar is **simple**: drafted by the orchestrator on
Sonnet, no critic pass required.

## Codex commands reference

- `codex:rescue` — independent implementation attempt when the orchestrator is blocked.
- `codex:adversarial-review` — checker pass for draft plans, completion evaluation, and high-stakes review.
- `codex:review` — focused diff sanity review during execution.
- `codex:result` — harvest the result of an async codex plugin task.

## Fallback when codex plugin is absent

Use this chain when a checker command is unavailable:

1. Try the named codex command.
2. Fall back to a fresh Claude subagent via the Task tool, with no shared working context beyond a self-contained brief.
3. Fall back to a human reviewer in a separate session.

`codex:rescue` has no good fallback. Its purpose is breaking deadlock by using
a structurally independent implementation worker; when unavailable, pause and
ask for human direction rather than pretending ordinary orchestration is
equivalent.

## How to update fleet-wide

Model lineup changes land as init-docs changelog entries. Update this file, the
corresponding ADR or superseding ADR, and any scaffolded references in one
entry so audit mode can apply the change idempotently across repos.

## Drift response

When a failure involves planning, review, execution, or verification quality,
route it through `docs/processes/harness.md` § Steering loop and ask first:
was the right model used for the step above? If not, fix the policy violation
and continue steering on any residual harness gap.
