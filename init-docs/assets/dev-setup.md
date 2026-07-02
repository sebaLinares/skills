---
owner: {{REPO_NAME}}
status: living
last_reviewed: 2026-07-02
update_trigger: on-toolchain-change
---

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

## Pre-tool-use hook (covers: enforcement)

The covers: hard constraint (`AGENTS.md` § Hard constraints) requires
that every Edit/Write target prefix-match an active plan's `covers:`
*at the call site* — not just at commit. The pre-commit plan-coverage
sensor is the last line of defence; this hook is the first.

The reference implementation ships at
`.claude/hooks/verify-covers-hook.sh` (bash + jq, stack-neutral). To
activate, register it in `.claude/settings.local.json`
(**per-contributor**, gitignored — not `.claude/settings.json`):

    {
      "hooks": {
        "PreToolUse": [
          {
            "matcher": "Edit|Write|MultiEdit",
            "hooks": [
              { "type": "command",
                "command": ".claude/hooks/verify-covers-hook.sh" }
            ]
          }
        ]
      }
    }

Per-contributor activation by default — see SKILL.md § Notes on
scope → Config-file precedence for the fleet rule.

Hook contract (re-implement in any language; bash is reference, not
required):

- Read PreToolUse JSON from stdin.
- If `tool_name` is not Edit/Write/MultiEdit → exit 0 (allow).
- If `tool_input.file_path` is under `docs/` or is a root anchor
  (`AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `SECURITY.md`,
  `README.md`) → exit 0 (always allowed).
- For each plan in `docs/exec-plans/active/*.md`, parse the `covers:`
  YAML list. Normalize optional leading `./`; reject absolute entries.
  If the target path prefix-matches any entry → exit 0.
- Otherwise → write a remediation message to stderr and exit non-zero
  (Claude Code reads stderr and surfaces the rejection to the agent).
- Bypass via `HARNESS_BYPASS="<reason>"` env var. Mirrors the
  pre-commit sensor's bypass shape.

Activation is opt-in. Installing the hook is a project decision —
some repos prefer the in-execution gate, some prefer to rely on the
commit-time sensor alone. The hard constraint applies either way; the
hook only enforces it mechanically.

## Harness validators

Two stdlib-Python scripts ship at `scripts/harness/`:

- `check_harness_structure.py` — fast structural check. Asserts the
  canonical files exist, carry the 4-key YAML frontmatter where
  required, and reference each other where the manifest says they
  must. No forbidden ephemera, no absolute paths in scanned text or
  path-bearing frontmatter.
- `garbage_collect_docs.py` — slower audit. Broken-reference scan,
  metadata staleness (default 90 days), orphan-doc detection,
  ephemeral-doc detection. Renders a markdown report; `--strict`
  returns non-zero on warnings too.

Requirements: `python3 ≥ 3.9` on `PATH`. Both scripts honour
`HARNESS_BYPASS="<reason>"` (same shape as the plan-coverage sensor).

Wiring contract (intentionally not shipped — fill in for this stack):

- **Pre-commit:** invoke `check_harness_structure.py`. Should be the
  *last* check after the plan-coverage sensor; cheapest first.
- **CI:** run both validators. `check_harness_structure.py` blocks
  merge; `garbage_collect_docs.py` writes its report to
  `docs/generated/harness-gc-report.md` (warn-only on PR, strict on
  the default branch is a reasonable default).
- **Nightly / weekly:** invoke `garbage_collect_docs.py --strict`.

Examples (Makefile, pre-commit, GitHub Actions) live in
[ADR harness-validators — Harness validators](../decisions/harness-validators.md)
§ Appendix — explicitly marked example-only. Stack-native
re-implementations (Node, Go, etc.) are acceptable as long as the
contract documented here is preserved.

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

## Evaluator convention

Fleet default per `docs/processes/model-policy.md`. Override only if
§ Fallback applies. Universal shape:

    <evaluator-cmd> <plan-path>

    evaluator-cmd: node "$(find ~/.claude/plugins -name codex-companion.mjs -type f 2>/dev/null | head -1)" adversarial-review --base <merge-base>
    # Focus text template:
    #   "Adversarial verification of completion. Challenge the worker's
    #   claim that the diff at docs/exec-plans/active/<plan>.md is done.
    #   Pressure-test Alignment (does the diff actually implement the
    #   Plan-of-Work and Concrete Steps, or has scope drifted / been
    #   silently omitted?) and Acceptance (are the Validation & Acceptance
    #   criteria actually verified with evidence — test transcripts,
    #   observable outputs — not just declared green?). Quality is
    #   optional; failing Quality routes to tech-debt-tracker.md, not
    #   completion blocker. Report verdicts per ADR evaluator-gate block shape."

### Tool resolution

The codex-plugin-cc slash command `/codex:adversarial-review` sets
`disable-model-invocation: true`, so the orchestrator cannot invoke it
from inside a turn. The Evaluator therefore runs through the underlying
`codex-companion.mjs` script via Bash. The script ships with the plugin
under `~/.claude/plugins/`, but `CLAUDE_PLUGIN_ROOT` is **not** set in an
ordinary orchestrator Bash tool call — Claude Code injects it only inside a
plugin's own hook or slash-command context, never in the ad-hoc Bash calls
the orchestrator uses here. The `evaluator-cmd` above therefore locates the
script with the same `find ~/.claude/plugins` discovery shim the pre-approval
critic hook uses (`harness-planner-critic-hook.mjs` → `findCompanion`), rather
than interpolating the variable. The choice of `adversarial-review` over
`review` is forced by tooling:
`adversarial-review` is the only review command that accepts focus text,
which the Evaluator needs to carry its verdict-block instructions. The
focus text above is framed as adversarial verification of conformance so
the tool's "challenge the chosen approach" framing matches the
Evaluator's "challenge the worker's claim of completion" purpose — see
ADR evaluator-gate § Tool selection.

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
structural, not convention-only. See ADR evaluator-gate and `docs/PLANS.md` →
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
