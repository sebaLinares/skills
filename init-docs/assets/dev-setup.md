# Developer setup

Local toolchain and sensors for this service. Fill in the stack-specific
commands below — the skill scaffolds this file as a skeleton, but every
project has a different stack.

> Replace each placeholder with the command or path that applies to
> this project. Delete sections that don't apply.

## Toolchain

*Fill in:* primary language + version, package manager, any other
required tools (formatter, linter, container runtime).

- Codex plugin (required for default Evaluator and adversarial review).
  Install via Claude Code marketplace. If unavailable, see
  `docs/processes/model-policy.md` § Fallback.

## Pre-commit hook

*Fill in:* what the pre-commit hook runs and how to install it.

The hook is a **sensor** in harness terms — it catches mistakes before
they reach review. At minimum it should run the project's formatter,
static analyser / linter, and tests on changed files.

Typical shape:

    <format command> && <lint command> && <test command>

Name the make / npm / task target that encapsulates this and point
`.git/hooks/pre-commit` at it. Keep the hook fast; split slow checks
into CI.

Also wire in the **plan-coverage sensor** as a final step. The sensor
reads every approved plan's `covers:` frontmatter from
`docs/exec-plans/active/` and blocks any staged source file not
covered by an approved plan. Implementation is stack-specific; see
`docs/PLANS.md` for the `covers:` contract. The sensor must support a
bypass env var (`HARNESS_BYPASS="<reason>"`) that skips *only* the
coverage check while leaving other pre-commit checks in place.

## Common commands

*Fill in the table with the commands a new developer runs day-to-day.*

| Purpose | Command |
|---|---|
| Build | `<command>` |
| Run locally | `<command>` |
| Run tests | `<command>` |
| Format code | `<command>` |
| Lint | `<command>` |
| Run all checks | `<command>` |

## Feature verification convention

*Fill in:* the exact shell command form that runs this project's test
runner with a tag filter. Example shapes:

    npm test -- --grep "@feat:<id>"
    go test -run "Feat<Id>"
    pytest -k "feat_<id>"

`docs/FEATURES.md` rows in the `verify:` column reference tags using
this convention. Until this section is filled in, `verify:` tags are
forward declarations only; they will not actually run.

`verify-cmd:` in `docs/FEATURES.md` is a literal shell string — the
escape hatch for Features the tagged-test convention does not cover
(e.g. health endpoints, smoke checks). It is fully decoupled from the
plan-coverage sensor.

## Complexity threshold

*Fill in:* the rule that classifies an ExecPlan as **complex** vs
**simple**. Phrase it in terms of modules / packages / core
infrastructure directories the plan touches, so the classification is
auditable from `module-count:` in the plan frontmatter without
re-reading the body.

Typical shapes (pick one or write your own):

    ≥2 directories under <modules-root>/, OR
    ≥2 of <core-infra-dir-1>, <core-infra-dir-2>, <core-infra-dir-3>.

High-risk or irreversible single-module plans (data migrations,
auth-path rewrites, public-API contract changes) are also complex
regardless of module count. Borderline cases default to complex.

Complex plans are drafted by the `harness-planner` subagent on Opus
4.7 xhigh and require a `codex:adversarial-review` pre-approval pass.
Simple plans stay on the orchestrator with no critic pass. See
`docs/processes/harness.md` § Phase 5 and
`docs/processes/model-policy.md` § Complex vs simple ExecPlan threshold.

## Evaluator convention

Fleet default per `docs/processes/model-policy.md`. Override only if
§ Fallback applies. Universal shape:

    <evaluator-cmd> <plan-path>

    evaluator-cmd: codex:adversarial-review --base <merge-base>
    # Focus text template: "Verify Alignment + Acceptance against
    # docs/exec-plans/active/<plan>.md. Report verdicts per ADR 003 block shape."

*Independence assertion (single line):* confirm that this command
runs in a context that does **not** share state with the worker's
session — for example a fresh subagent, a separate CLI agent, or a
human reviewer. Independence is the load-bearing property; same
agent, same session, same context does not qualify.

_________________________________________________________________

The Evaluator gates the `active/` → `completed/` transition for
every ExecPlan. It reads the plan plus the working tree it references
and writes a verdict block into the plan's `## Evaluator transcript`
section (Alignment, Acceptance, optionally Quality). The worker that
produced the plan never edits that section — independence is
structural, not convention-only. See ADR 003 and `docs/PLANS.md` →
"The `Evaluator transcript` section" for the full contract.

When the codex plugin is unavailable, fall back to a fresh Claude
subagent per `model-policy.md` § Fallback. The independence assertion
still holds — fresh subagent ≠ worker session.

## Running locally

*Fill in:* environment variables required, how to supply them (`.env`,
secret manager, direct export), and the exact command to start the
service. Include the expected startup output so a developer can
confirm the service is up.

## Troubleshooting

*Fill in over time* as recurring friction surfaces. A good entry names
the symptom, the root cause, and the fix.
