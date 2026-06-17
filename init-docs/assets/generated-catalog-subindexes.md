---
id: generated-catalog-subindexes
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-06-16
update_trigger: on-supersession
---

# ADR generated-catalog-subindexes — Churny catalog sections are generated, not hand-maintained

## Status

Accepted; extends ADR harness-design and ADR harness-validators.

## Context

The master catalog (`docs/README.md`) is read on every session bootstrap.
The harness made "add a one-line catalog row" a Phase-2 gate and asked the
orchestrator to hand-edit the catalog for every analysis doc and plan. In a
deployed instance (~2 months, 35 analysis docs, 42 completed plans) the
Analysis section drifted from one-liners to paragraph-length entries, was
append-only, and was never demoted — ~39 paragraph entries read at every
bootstrap, almost all describing shipped, superseded work. This is read-path
rot: not a storage problem (bootstrap does not even re-read completed plans),
but a *catalog* problem concentrated in one file plus stale tags on superseded
analysis.

The fix follows the harness's own steering-loop doctrine: a guide that
demonstrably rotted (hand-maintain a one-line row) should become a sensor. The
harness already has the structural precedent — `references/` and `generated/`
each have their own sub-index `README.md` and the master catalog only points
to them. The Analysis section is the one place that instead inlined every row.

Two symptoms must be killed at the source: paragraph bloat (an entry can be any
length) and never-demoted entries (nothing moves a superseded doc out of the
read-path).

## Decision

The churny, append-only catalog sections are **derived from artifact
frontmatter**, not hand-maintained:

- `docs/analysis/README.md` and `docs/exec-plans/completed/README.md` are
  **generated** by `scripts/harness/generate_catalog_indexes.py` from each
  artifact's frontmatter. The master `docs/README.md` carries only a pointer to
  each. ADRs, processes, architecture, and references stay hand-curated (low
  churn; their blurbs are editorial and worth keeping).
- Analysis docs gain a required one-line `summary:` frontmatter field — paragraph
  bloat is structurally impossible because the generator emits exactly that line.
- Supersession is a frontmatter pointer: `superseded-by: <repo-relative path>`.
  Stamping it moves the row into a "Superseded" group on regeneration; a
  tag-aware reader skips superseded analysis. Relevance is a relationship, not a
  date or a log scan.
- Sync is enforced by a **`--check`** mode wired into pre-commit that fails on
  drift (matching `check_harness_structure.py`'s fail-fast posture). The
  generator never mutates files mid-commit.

This is a net *reduction* in harness surface. It removes the Phase-2
"add a one-line catalog row" gate (the thing that bred the bloat) and turns
session exit's doc-coherence dimension from "manually index every artifact"
into "run the generator."

Out of scope: generating the ADR, process, architecture, or reference sections;
a central activity log (git is the authoritative change log — see
ADR post-completion-amendment).

## Consequences

The catalog can no longer rot into paragraphs or carry stale, never-demoted
entries, because it is derived rather than authored. Demotion is automatic from
a one-line `superseded-by:` stamp. The bootstrap read-path shrinks to a thin
master catalog plus on-demand sub-indexes.

The cost is one stdlib script to own and one required frontmatter field
(`summary:`) on analysis docs; `docs/analysis/README.md` and
`docs/exec-plans/completed/README.md` become generated artifacts under the
"do not hand-edit" convention. A forgotten regeneration surfaces as a
pre-commit `--check` failure rather than silent drift. Existing instances need a
one-time migration: backfill `summary:` on legacy analysis docs, stamp
`superseded-by:` where known, and run the generator.
