---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-doc-added
---

# Docs Catalog

Entry point for AI context. Read this before any task requiring domain knowledge.

---

## Tagging system

Every catalog entry ends with a #tag list. Use them to load only what's relevant.

**Format:**
- [Title](path) — description `#tag1` `#tag2`

**When adding a doc:** append at least one domain tag and one type tag.

**When reading this catalog:** scan tags first, read only the docs whose tags
match the task at hand. Skip the rest.

**Tag vocabulary:**

| Domain | Type |
|---|---|
| DOMAIN_TAGS `#ai-harness` `#features` | `#request-flow` `#api-contract` `#data-model` `#transformation` `#diagram` |
| EXTERNAL_TAGS | `#gap-analysis` `#research` `#adr` `#guideline` `#ticket` `#plan` `#architecture` `#security` `#tech-debt` `#ledger` |

Add new tags freely — keep them lowercase, hyphenated, specific.

---

## Repo-root anchors
Top-level docs that live at the repo root, not under `docs/`. Linked here for discoverability.

- [`/AGENTS.md`](../AGENTS.md) — agent map; entry point for any coding agent. `CLAUDE.md` is a symlink to it `#ai-harness` `#guideline`
- [`/ARCHITECTURE.md`](../ARCHITECTURE.md) — code map: module shape, dependency direction, business domains, bootstrap, hotspots `#architecture` `#guideline`
- [`/SECURITY.md`](../SECURITY.md) — security posture: reporting, dependency scanning, secrets, auth, threat model `#security` `#guideline`

## Features
Repo-wide scope surface — every user-observable capability with its verification command and current state. Read before the catalog sections below when entering the repo: it tells you what the product does.

- [FEATURES.md — feature ledger](FEATURES.md) — what this product is supposed to do, with verification and state `#ai-harness` `#features` `#ledger`

## Architecture
System internals: request flows, data transformations, API contracts, diagrams. For the repo-wide map, see [`/ARCHITECTURE.md`](../ARCHITECTURE.md).

*(none yet)*

## Analysis
Point-in-time research, gap reports, investigations. Dated — may be superseded by newer entries.

- [Analysis template](analysis/_template.md) — copy, fill, commit `#ai-harness` `#guideline`

## Decisions
Architecture Decision Records (ADRs). Explain *why* the system is the way it is.

- [001 — Harness Engineering for AI Agent Usage](decisions/001-harness-design.md) — guides + sensors, phase gates, plans as first-class artifacts `#ai-harness` `#adr`
- [002 — Session exit closes the bootstrap asymmetry](decisions/002-session-exit.md) — explicit session close-out checklist and chat-sweep routing `#ai-harness` `#adr`
- [003 — Evaluator gate at plan completion](decisions/003-evaluator-gate.md) — independent evaluator pass before `active/` → `completed/`; worker/checker split for plan closure `#ai-harness` `#adr`
- [004 — Fleet model policy](decisions/004-fleet-model-policy.md) — named models per harness step; Sonnet orchestrator, Opus design subagent, GPT-5.5 checker via codex plugin `#ai-harness` `#adr`
- [005 — Hard constraints as a separate category from phase gates](decisions/005-hard-constraints.md) — `## Hard constraints (MUST / MUST NOT)` section in `AGENTS.md`, distinct from phase gates `#ai-harness` `#adr`
- [006 — Pre-approval critic gate](decisions/006-pre-approval-critic-gate.md) — unconditional pre-approval critic pass; simple/complex threshold removed; pre-approval critic transcript artifact `#ai-harness` `#adr`
- [007 — Harness validators](decisions/007-harness-validators.md) — stdlib Python structure check + doc garbage collector at `scripts/harness/`; stack-agnostic wiring `#ai-harness` `#adr`

## Exec plans
Active and completed initiative plans. First-class artifacts — reviewed before any code is written. Plan-scoped decisions live inline; architectural decisions escalate to ADRs.

- [PLANS.md — ExecPlan specification](PLANS.md) — contract for what a plan must be, required sections, living-document discipline `#ai-harness` `#plan` `#guideline`
- `exec-plans/active/` — plans currently in flight
- `exec-plans/completed/` — done, retained for historical context
- [Plan template](exec-plans/_template.md) — copy, fill, commit to `active/` `#ai-harness` `#plan`

*(no active or completed plans yet)*

## Processes
How-we-work: guidelines, conventions, runbooks.

- [Harness — Operating Manual](processes/harness.md) — day-to-day workflow phases, phase gates, steering loop; implements ADR 001 `#ai-harness` `#guideline`
- [Developer setup](processes/dev-setup.md) — local toolchain, pre-commit hook, common commands — **fill in for this stack** `#ai-harness` `#guideline`
- [Model policy](processes/model-policy.md) — fleet-wide per-step model assignments and codex command reference `#ai-harness` `#guideline`

## References
External / legacy specs the code must conform to. See [references/README.md](references/README.md) for convention and the reference-vs-analysis distinction.

- [References — convention](references/README.md) — `#ai-harness` `#guideline`

*(no reference pulls yet)*

## Generated
Machine-generated artifacts. Not hand-edited.

- [Generated — convention](generated/README.md) — what lives here and how it's refreshed `#ai-harness` `#guideline`

## Tech debt
Running ledger of known hazards, shortcuts, and deferred improvements.

- [Tech debt tracker](tech-debt-tracker.md) — severity + status legend; open and resolved items `#tech-debt` `#ai-harness` `#ledger`

## Tickets
AI-generated ticket drafts.

*(none yet)*
