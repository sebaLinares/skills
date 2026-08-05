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
Wiring it into pre-commit is a **convention this harness sets up where it
can, not a guarantee** — a repo's existing hook manager (husky, lefthook,
`.pre-commit-config.yaml`, plain `.githooks/`) always takes precedence over
the harness owning `core.hooksPath`. Check whether it's actually wired in
*this* clone:

    python3 scripts/harness/check_plan_coverage.py --doctor

`WIRED` means the line below is already called from your active pre-commit
hook. `UNWIRED` means it isn't — see `docs/HARNESS-TODO.md` for the fix that
applies to this repo's hook manager. The line itself, if you're wiring it by
hand:

    python3 "$(git rev-parse --show-toplevel)/scripts/harness/check_plan_coverage.py"

If this repo has no hook manager of its own, the harness set one up at
`.githooks/pre-commit` and ran `git config core.hooksPath .githooks` for you;
that only needs re-running per clone if `core.hooksPath` doesn't persist in
your git config location of choice:

    git config core.hooksPath .githooks

What the check does:

- Reads staged added, copied, modified, and deleted files from the git index.
- Always allows anything under `docs/` or `specs/`, plus root anchors
  `AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `SECURITY.md`, `README.md`, and
  `.harness-version`. **`scripts/harness/` is not on that list**: the sensors
  are the strongest mechanical guard here, so changing them needs an active
  plan covering them, like any other code.
- Requires every other staged file to prefix-match a `covers:` entry from the
  single active `specs/<feature>/plan.md`. A trailing `/` covers a directory.
- Fails if more than one `specs/*/plan.md` is `status: active`.
- Prints remediation and exits non-zero on uncovered files.
- Bypasses only this check with `HARNESS_BYPASS="<reason>" git commit ...`.

Verify the sensor and the loop engine after wiring:

    python3 scripts/harness/check_plan_coverage.py --selftest
    python3 scripts/harness/speckit_gate.py selftest
    bash scripts/harness/wt_fanout.sh --selftest

Check that this repo's harness itself is intact (ignore entries, hooks,
plan-template edits, skills, retired files, feature hint, sensor wiring):

    python3 scripts/harness/speckit_gate.py doctor

## Adding stack lanes to pre-commit

The plan-coverage step is stack-neutral by design — it's a single line, not a
config format, so it drops into any hook manager. Add lanes for this repo's
stack (format, vet/lint, test on affected packages) before the plan-coverage
line, in whichever file is your active pre-commit hook (`--doctor` above
tells you which one). Keep them fast — they run on every commit.

## GitHub MCP server

`/speckit-taskstoissues` (converts `tasks.md` into GitHub issues) needs the
GitHub MCP server configured — it has no `gh` CLI fallback. If the harness
scaffold wrote `.mcp.json` for you (Docker-based, official GitHub MCP server
image), you still need to:

1. Create a personal access token with `repo` scope. If the org requires SSO,
   authorize the token for it (github.com → Settings → Developer settings →
   Personal access tokens → Configure SSO).
2. Export it in your shell profile — never commit it, never put it in
   `.mcp.json` itself:

       export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...

3. Using Codex instead of / in addition to Claude Code? Codex reads MCP
   servers from `~/.codex/config.toml` (user-global, not part of this repo —
   the harness doesn't write it). Add:

       [mcp_servers.github]
       command = "docker"
       args = ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"]

       [mcp_servers.github.env]
       GITHUB_PERSONAL_ACCESS_TOKEN = "${GITHUB_PERSONAL_ACCESS_TOKEN}"

If `docs/HARNESS-TODO.md` flags Docker as missing, install it first — the
server runs as a container, not a native binary.

## Skipping checks

Skip only plan-coverage for exceptional commits:

    HARNESS_BYPASS="<reason>" git commit -m "..."

Skip the whole hook only when necessary:

    git commit --no-verify

If a check is routinely too slow or wrong, fix the check. Do not route around it
as normal workflow.
