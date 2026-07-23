---
owner: {{REPO_NAME}}
status: living
last_reviewed: {{DATE}}
update_trigger: on-toolchain-change
---

# Developer setup

Local toolchain, day-to-day commands, and the one mechanical harness sensor.
The harness model is described in [harness.md](harness.md).

> Fill the Toolchain and Common commands sections with this repo's real stack.
> Delete the prompts once filled.

## Toolchain

*Language/runtime versions and how to install dev tools (linters, formatters).*

## Common commands

| Purpose | Command |
|---|---|
| Build | `<build command>` |
| Run locally | `<run command>` |
| Run tests | `<test command>` |
| Format | `<format command>` |
| Lint | `<lint command>` |

## Plan-coverage check

The one mechanical sensor in this harness. It enforces the hard constraint
"no edits outside the active plan's `covers:`" (`AGENTS.md` § Hard constraints)
at commit time.

The reference implementation lives at
`scripts/harness/check_plan_coverage.py` (stdlib Python >= 3.9, no installs).
It is wired as the last step of `.githooks/pre-commit`:

    python3 "$(git rev-parse --show-toplevel)/scripts/harness/check_plan_coverage.py"

Enable the hook per clone:

    git config core.hooksPath .githooks

What the check does:

- Reads staged added, copied, modified, and deleted files from the git index.
- Always allows anything under `docs/`, `specs/`, or `scripts/harness/`, plus
  root anchors `AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `SECURITY.md`,
  `README.md`, and `.harness-version`.
- Requires every other staged file to prefix-match a `covers:` entry from the
  single active `specs/<feature>/plan.md`. A trailing `/` covers a directory.
- Fails if more than one `specs/*/plan.md` is `status: active`.
- Prints remediation and exits non-zero on uncovered files.
- Bypasses only this check with `HARNESS_BYPASS="<reason>" git commit ...`.

Verify the sensor and the loop engine after wiring:

    python3 scripts/harness/check_plan_coverage.py --selftest
    python3 scripts/harness/speckit_gate.py selftest

## Adding stack lanes to pre-commit

The shipped `.githooks/pre-commit` runs only the plan-coverage sensor, so it is
stack-neutral. Add lanes for this repo's stack (format, vet/lint, test on
affected packages) before the plan-coverage step. Keep them fast — they run on
every commit.

## Skipping checks

Skip only plan-coverage for exceptional commits:

    HARNESS_BYPASS="<reason>" git commit -m "..."

Skip the whole hook only when necessary:

    git commit --no-verify

If a check is routinely too slow or wrong, fix the check. Do not route around it
as normal workflow.
