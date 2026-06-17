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
Point-in-time research, gap reports, investigations. **Not inlined here** — the
per-doc rows live in a generated index so this catalog stays thin at bootstrap.
Demotion is automatic from each doc's `superseded-by:` frontmatter. See
[ADR generated-catalog-subindexes](decisions/generated-catalog-subindexes.md).

- [Analysis index](analysis/README.md) — generated from `docs/analysis/*.md` frontmatter; newest first, current vs superseded `#ai-harness` `#guideline`
- [Analysis template](analysis/_template.md) — copy, fill (incl. `summary:`), commit `#ai-harness` `#guideline`

## Decisions
Architecture Decision Records (ADRs). Explain *why* the system is the way it is.

ADRs are identified by their `id:` slug. The filename is `<slug>.md`
(no numeric prefix). References inside docs use slug form: `ADR <slug>`
in prose, `decisions/<slug>.md` in markdown links. See
[ADR adr-slug-canonical](decisions/adr-slug-canonical.md) for the
convention.

- [ADR harness-design — Harness Engineering for AI Agent Usage](decisions/harness-design.md) — guides + sensors, phase gates, plans as first-class artifacts `#ai-harness` `#adr`
- [ADR session-exit — Session exit closes the bootstrap asymmetry](decisions/session-exit.md) — explicit session close-out checklist and chat-sweep routing `#ai-harness` `#adr`
- [ADR evaluator-gate — Evaluator gate at plan completion](decisions/evaluator-gate.md) — independent evaluator pass before `active/` → `completed/`; worker/checker split for plan closure `#ai-harness` `#adr`
- [ADR fleet-model-policy — Fleet model policy](decisions/fleet-model-policy.md) — named models per harness step by role (orchestrator / design subagent / checker); versions in model-policy `#ai-harness` `#adr`
- [ADR hard-constraints — Hard constraints as a separate category from phase gates](decisions/hard-constraints.md) — `## Hard constraints (MUST / MUST NOT)` section in `AGENTS.md`, distinct from phase gates `#ai-harness` `#adr`
- [ADR pre-approval-critic-gate — Pre-approval critic gate](decisions/pre-approval-critic-gate.md) — unconditional pre-approval critic pass; simple/complex threshold removed; pre-approval critic transcript artifact `#ai-harness` `#adr`
- [ADR harness-validators — Harness validators](decisions/harness-validators.md) — stdlib Python structure check + doc garbage collector at `scripts/harness/`; stack-agnostic wiring `#ai-harness` `#adr`
- [ADR adr-slug-canonical — ADR slugs as the canonical identifier](decisions/adr-slug-canonical.md) — slug-only filenames, slug-only URLs and prose refs; no numeric ADR identity anywhere `#ai-harness` `#adr`
- [ADR generated-catalog-subindexes — Churny catalog sections are generated](decisions/generated-catalog-subindexes.md) — analysis + completed-plan indexes derived from frontmatter; removes the Phase-2 catalog-row gate; `superseded-by:` drives demotion `#ai-harness` `#adr`
- [ADR post-completion-amendment — Completed plans are mutable](decisions/post-completion-amendment.md) — amend in place via `## History`, no re-entry to `active/`; per-artifact history not a central log (git is the change log) `#ai-harness` `#adr`

## Exec plans
Active and completed initiative plans. First-class artifacts — reviewed before any code is written. Plan-scoped decisions live inline; architectural decisions escalate to ADRs.

- [PLANS.md — ExecPlan specification](PLANS.md) — contract for what a plan must be, required sections, living-document discipline `#ai-harness` `#plan` `#guideline`
- `exec-plans/active/` — plans currently in flight (scanned directly at bootstrap; WIP=1)
- [Completed plans index](exec-plans/completed/README.md) — generated from `docs/exec-plans/completed/*.md` frontmatter; newest first. Plans are mutable via amendment (ADR post-completion-amendment) `#ai-harness` `#plan`
- [Plan template](exec-plans/_template.md) — copy, fill, commit to `active/` `#ai-harness` `#plan`

*(no active plans yet)*

## Processes
How-we-work: guidelines, conventions, runbooks.

- [Harness — Operating Manual](processes/harness.md) — day-to-day workflow phases, phase gates, steering loop; implements ADR harness-design `#ai-harness` `#guideline`
- [Developer setup](processes/dev-setup.md) — local toolchain, pre-commit hook, common commands — **fill in for this stack** `#ai-harness` `#guideline`
- [Model policy](processes/model-policy.md) — fleet-wide per-step model assignments and codex command reference `#ai-harness` `#guideline`
- [Initialization checklist](processes/initialization-checklist.md) — the bootstrap contract; four conditions every operable repo must satisfy `#ai-harness` `#guideline`
- [Cold-start test](processes/cold-start-test.md) — quarterly legibility ritual; five questions answered from repo content alone `#ai-harness` `#guideline`

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
