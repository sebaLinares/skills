---
owner: {{REPO_NAME}}
status: living
last_reviewed: 2026-05-29
update_trigger: on-toolchain-change
---

# Developer setup

Local toolchain and the one mechanical sensor for this tool. The skill
scaffolds this as a skeleton — fill in the stack-specific commands.

> Replace each placeholder with the command or path that applies. Delete
> sections that don't apply.

## Toolchain

*Fill in:* primary language + version, package manager, and any other required
tools (formatter, linter).

## Common commands

*Fill in the table with the commands a developer runs day-to-day.*

| Purpose | Command |
|---|---|
| Build | `<command>` |
| Run locally | `<command>` |
| Run tests | `<command>` |
| Format | `<command>` |
| Lint | `<command>` |

## Plan-coverage check

The one mechanical sensor in this harness. It enforces the hard constraint
"no edits outside the active plan's `covers:`" (`AGENTS.md` § Hard constraints)
at commit time.

The reference implementation ships at
`scripts/harness/check_plan_coverage.py` (stdlib Python ≥ 3.9, no installs).
Wire it as the **last** step of your pre-commit hook:

    python3 scripts/harness/check_plan_coverage.py

What it does (the contract — re-implement in Go/Node if you prefer no Python
in this repo):

- Reads staged added/modified/**deleted** files (`git diff --cached`) — a
  staged delete is an edit outside `covers:` too.
- Always allowed: anything under `docs/` or `scripts/harness/`, the root
  anchors (`AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `SECURITY.md`,
  `README.md`), and `.harness-version` — these are docs and harness infra, not
  application source under a plan.
- Every other staged file must be prefix-matched by a `covers:` entry of a
  plan, read from the git **index**: the active plan in
  `docs/exec-plans/active/` or a completed plan at the `docs/exec-plans/` root.
  A trailing `/` covers a directory.
- On an uncovered file: prints remediation and exits non-zero.
- Bypass (skips only this check): `HARNESS_BYPASS="<reason>" git commit ...`

Installing the hook is a project decision; the script ships, the wiring is
yours. A minimal `.git/hooks/pre-commit`:

    #!/usr/bin/env bash
    set -e
    <your format/lint/test commands>
    python3 scripts/harness/check_plan_coverage.py

## Running locally

*Fill in:* required environment variables and how to supply them, plus the
exact command to start the tool and the expected startup output.

## Troubleshooting

*Fill in over time* as recurring friction surfaces — symptom, root cause, fix.
