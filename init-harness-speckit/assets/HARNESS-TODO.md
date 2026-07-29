---
owner: {{REPO_NAME}}
status: living
last_reviewed: {{DATE}}
update_trigger: on-skeleton-filled
---

# Harness onboarding — skeletons to fill

`init-harness-speckit` scaffolds this repo's harness with a few **skeleton**
files that only the team can fill with repo-specific content. This is a
**non-blocking** checklist: you can spec, plan, and ship features before any of
these are filled. Nothing here gates commits or CI. Fill each as you touch the
relevant area, tick its box, and delete this file once every box is checked.

They exist so a coding agent (or a new dev) starting cold has real repo context
instead of placeholders.

## Checklist

- [ ] **`ARCHITECTURE.md`** — the code map: overview, top-level layout, module
  pattern, dependency direction, entry point/bootstrap, hotspots.
  *Done when:* no `> Fill each section` prompts remain.
- [ ] **`SECURITY.md`** — security posture: reporting, secrets, dependency
  scanning, auth/trust boundaries.
  *Done when:* no `> Fill each section` prompts remain.
- [ ] **`docs/processes/dev-setup.md`** — Toolchain + Common commands for this
  repo's stack (build / run / test / format / lint).
  *Done when:* the command table has real commands, not `<placeholders>`.
- [ ] **`docs/decisions/harness-design.md`** — replace `{{PROJECT_CONTEXT}}`
  with one paragraph: what this service is and what it talks to.
  *Done when:* the `{{PROJECT_CONTEXT}}` marker is gone.
- [ ] **`.specify/memory/constitution.md`** — the project constitution (the
  supreme document). Author it via `/speckit-constitution`.
  *Done when:* it no longer contains `[PROJECT_NAME]` / `[PRINCIPLE_1_NAME]`.

## Conditional items

The scaffold appends these only when it actually hit the condition — they
won't appear in every repo.

- [ ] **Wire the plan-coverage sensor by hand** — Step 10 found a YAML/JSON
  hook manager (`lefthook.yml`, `.pre-commit-config.yaml`, a
  `simple-git-hooks` config) and will not auto-edit it. Add this line to the
  manager's plan-coverage entry:
  `python3 "$(git rev-parse --show-toplevel)/scripts/harness/check_plan_coverage.py"`.
  *Done when:* `python3 scripts/harness/check_plan_coverage.py --doctor`
  prints `WIRED`.
- [ ] **Install Docker** — the GitHub MCP server (needed by
  `/speckit-taskstoissues`) runs as a container; Step 5b found no `docker` on
  `PATH` and skipped writing `.mcp.json`. Install Docker, then re-run
  `/init-harness-speckit` so it can write the config.
  *Done when:* `docker --version` succeeds and `.mcp.json` has a `github` entry.
- [ ] **Authorize the GitHub PAT** — create a personal access token (scope
  `repo`), authorize it for SSO against the org if required, and export it as
  `GITHUB_PERSONAL_ACCESS_TOKEN` in your shell profile. See
  `docs/processes/dev-setup.md` § GitHub MCP server.
  *Done when:* `/speckit-taskstoissues` runs without an auth error.
- [ ] **Codex: add the GitHub MCP server to `~/.codex/config.toml`** — this is
  a user-global file outside the repo, so the harness doesn't write it. Copy
  the `[mcp_servers.github]` snippet from `docs/processes/dev-setup.md` §
  GitHub MCP server.
  *Done when:* Codex can list/create issues via `/speckit-taskstoissues`.

## When you fill one

Edit the file, delete its prompts/markers, tick its box here. When all boxes are
ticked, delete this file — its job is done.
