---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-fleet-policy-change
---

# Fleet Model Policy

This policy is fleet-wide and not project-configurable. It names the model
assignments for the harness so that failures and improvements can be compared
across scaffolded repos. ADR fleet-model-policy records the rationale.

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
| 14 | Phase 5 ExecPlan | Design subagent | Claude Task tool, Opus 4.7 xhigh | Draft every ExecPlan. No complexity threshold — see ADR pre-approval-critic-gate. |
| 15 | Pre-approval critic | Checker / rescue | `codex:adversarial-review` | Review every draft plan before lead approval. **Auto-invoked synchronously** by `.claude/hooks/harness-planner-critic-hook.mjs` on `harness-planner` SubagentStop; the hook writes the verdict into the plan's `## Pre-approval critic transcript` section. Failure modes (plugin missing, codex crash) write a `BLOCKED: <reason>` placeholder in the same section. See ADR pre-approval-critic-gate. |
| 16 | Phase 6 execution | Orchestrator | Main session | Execute approved plan steps and update progress. |
| 17 | Mid-execution diff sanity | Checker / rescue | `node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" review` | Request when the diff grows broad, risky, or surprising. The `/codex:review` slash command sets `disable-model-invocation: true`, so the orchestrator invokes the underlying companion script via Bash. |
| 18 | Rescue implementation | Checker / rescue | `Agent(subagent_type="codex:codex-rescue", prompt=…)` | Use when the orchestrator is stuck or needs an independent implementation attempt. The `/codex:rescue` slash command is user-only; the orchestrator routes through the `codex:codex-rescue` subagent directly via the `Agent` tool. |
| 19 | Async result harvest | Checker / rescue | `BashOutput` on the spawned shell (preferred) or `node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" result [job-id]` | Default to synchronous Bash invocation in step 17/20 — the verdict lands in stdout and needs no harvest. Only required when a checker was launched with `run_in_background: true`. The `/codex:result` slash command is user-only. |
| 20 | Completion Evaluator | Checker / rescue | `node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" adversarial-review --base <merge-base>` | Default Evaluator command before moving a plan to `completed/`. Uses `adversarial-review` for its steerability (the only review command that accepts focus text); the focus text is framed as adversarial verification of conformance — see ADR evaluator-gate § Tool selection. |
| 21 | Session exit and steering loop | Orchestrator | Main session | Run close-out, then route model drift through the steering loop. |

## Codex commands reference

The codex-plugin-cc slash commands (`/codex:review`, `/codex:adversarial-review`,
`/codex:result`, `/codex:cancel`, `/codex:status`) set
`disable-model-invocation: true` — they are user-only and the orchestrator
**cannot** invoke them from inside a turn. `/codex:rescue` is also user-only
in practice; it forwards to the `codex:codex-rescue` subagent which the
orchestrator *can* invoke via the `Agent` tool. The orchestrator therefore
calls the underlying tooling through two paths:

- Bash → `node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" <subcommand>`
  for review, adversarial-review, result, status, cancel. The
  `harness-planner-critic-hook.mjs` ships a discovery shim
  (`find ~/.claude/plugins/ -name codex-companion.mjs`) for hook contexts
  where `CLAUDE_PLUGIN_ROOT` is not populated; orchestrator Bash calls have
  the variable available.
- Agent tool with `subagent_type="codex:codex-rescue"` for rescue work.

Roles:

- `codex:codex-rescue` (Agent subagent) — independent implementation attempt
  when the orchestrator is blocked.
- `codex-companion.mjs adversarial-review` — steerable challenge review.
  Used for draft-plan critique (Step 15, hook-fired) and completion
  evaluation (Step 20, orchestrator-fired with `--base <merge-base>` plus
  focus text).
- `codex-companion.mjs review` — non-steerable defect-finding review of the
  current diff. Used for on-demand mid-execution diff sanity (Step 17).
- `codex-companion.mjs result` — fallback for harvesting a background job's
  stored output when `BashOutput` on the original shell is unavailable.

## Fallback when codex plugin is absent

Use this chain when a checker command is unavailable:

1. Try the named codex command.
2. Fall back to a fresh Claude subagent via the Task tool, with no shared working context beyond a self-contained brief.
3. Fall back to a human reviewer in a separate session.

`codex:codex-rescue` has no good fallback. Its purpose is breaking deadlock
by using a structurally independent implementation worker; when unavailable,
pause and ask for human direction rather than pretending ordinary
orchestration is equivalent.

## How to update fleet-wide

Model lineup changes land as init-docs changelog entries. Update this file, the
corresponding ADR or superseding ADR, and any scaffolded references in one
entry so audit mode can apply the change idempotently across repos.

## Drift response

When a failure involves planning, review, execution, or verification quality,
route it through `docs/processes/harness.md` § Steering loop and ask first:
was the right model used for the step above? If not, fix the policy violation
and continue steering on any residual harness gap.
