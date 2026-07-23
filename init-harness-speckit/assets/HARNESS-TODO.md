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

## When you fill one

Edit the file, delete its prompts/markers, tick its box here. When all boxes are
ticked, delete this file — its job is done.
