# Developer setup

Local toolchain and sensors for this service. Fill in the stack-specific
commands below — the skill scaffolds this file as a skeleton, but every
project has a different stack.

> Replace each placeholder with the command or path that applies to
> this project. Delete sections that don't apply.

## Toolchain

*Fill in:* primary language + version, package manager, any other
required tools (formatter, linter, container runtime).

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

## Running locally

*Fill in:* environment variables required, how to supply them (`.env`,
secret manager, direct export), and the exact command to start the
service. Include the expected startup output so a developer can
confirm the service is up.

## Troubleshooting

*Fill in over time* as recurring friction surfaces. A good entry names
the symptom, the root cause, and the fix.
