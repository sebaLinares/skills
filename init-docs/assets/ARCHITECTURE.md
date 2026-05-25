---
owner: {{REPO_NAME}}
status: living
last_reviewed: 2026-05-26
update_trigger: on-module-change
---

# Architecture

Top-level map of this service. This file is the single source of truth
for how the code is organised; read it before writing code you might
later have to unwind.

For agent-specific guidance and the workflow harness, see
[`AGENTS.md`](AGENTS.md) and
[`docs/processes/harness.md`](docs/processes/harness.md).

> Fill each section below for this project. Delete the prompts once
> filled. Keep this file current — outdated architecture docs mislead
> agents more than missing ones.

## Overview

*Describe what this service does in one paragraph.* Include: the
problem it solves, the public surface (HTTP / gRPC / queue consumer /
etc.), the transport and port, and the upstream / downstream systems
it talks to.

## Top-level layout

*Paste an ASCII tree of the repo root. Include only top-level dirs and
a one-line comment per entry.* Typical shapes:

- Go service: `cmd/`, `internal/`, `pkg/`, `scripts/`, `docs/`, `k8s/`.
- Node / TypeScript service: `src/`, `dist/`, `tests/`, `scripts/`,
  `docs/`.
- Mixed: whatever the actual layout is — document it as-is.

## Module pattern

*Describe the folder shape every feature module follows.* Name the
standard subfolders (handlers, services, mappers, routes, models — or
the equivalents in your stack) and what lives in each.

## Dependency direction

*State the one-way dependency rule inside a module.* Typical examples:

- Go / Gin-style: `handler → service → (mapper →) model`.
- NestJS-style: `controller → service → repository → entity`.
- Clean / hexagonal: `adapter → use-case → entity`.

Name how the rule is enforced (review, pre-commit, structural tests).

## Business domains

*List the current modules. Keep it short; link to deeper docs rather
than duplicating them here.*

| Module | Path | Notes |
|---|---|---|
| <name> | `<path>` | <one-line purpose> |

## Entry point and bootstrap

*Describe the startup sequence.* What loads config, what constructs
shared infrastructure (logger, clients, DB pool), what wires modules
into the router, how the process shuts down.

## Shared utilities

*List reusable helpers (`pkg/utils/`, `src/common/`, or equivalent) and
any shared internal library this service depends on.* Note what lives
in the shared library and should not be duplicated here.

## Current hotspots

*Pointers for agents new to the code.* List the 3–6 files where most
of the non-trivial logic lives, and why. Keep this section current —
refactors change hotspots, and stale entries mislead agents.

## Adding a new module

*Numbered steps for scaffolding a new feature module that conforms to
the patterns above.* A good last step is "write an ADR if the module
introduces a new cross-cutting concern."
