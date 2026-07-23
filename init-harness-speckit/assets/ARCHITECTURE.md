---
owner: {{REPO_NAME}}
status: living
last_reviewed: 2026-05-29
update_trigger: on-module-change
---

# Architecture

Top-level map of this tool. The single source of truth for how the code is
organised; read it before writing code you might later have to unwind.

For agent guidance and the workflow, see [`AGENTS.md`](AGENTS.md) and
[`docs/processes/harness.md`](docs/processes/harness.md).

> Fill each section below. Delete the prompts once filled. Keep this file
> current — outdated architecture docs mislead agents more than missing ones.

## Overview

*What this tool does in one paragraph.* Include: the problem it solves, the
surface (CLI / TUI / library / service), and any systems it talks to.

## Top-level layout

*An ASCII tree of the repo root — top-level dirs, one line each.* For a Go
tool, typically `cmd/`, `internal/`, `pkg/`, `docs/`.

## Module pattern

*The folder shape each feature/module follows.* Name the standard subfolders
and what lives in each.

## Dependency direction

*The one-way dependency rule.* e.g. `cmd → internal/<feature> → internal/core`.
Name how it's enforced (review, tests).

## Entry point and bootstrap

*The startup sequence.* What loads config, constructs shared infrastructure,
wires things together, and how the process shuts down.

## Current hotspots

*Pointers for agents new to the code.* The 3–6 files where most non-trivial
logic lives, and why. Keep current — refactors move hotspots.

## Adding a new module

*Numbered steps to scaffold a new module that conforms to the patterns above.*
A good last step: "write an ADR if the module introduces a new cross-cutting
concern."
