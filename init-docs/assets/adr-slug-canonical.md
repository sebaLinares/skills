---
id: adr-slug-canonical
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-05-30
update_trigger: on-supersession
---

# ADR adr-slug-canonical — ADR slugs as the canonical identifier

## Status

Accepted. Amends ADR harness-design (naming-convention surface) and
ADR harness-validators (validator surface) by removing every load-
bearing use of the numeric ADR identifier. The harness's previous
hybrid model (slug `id:` frontmatter + `NNN-<slug>.md` filename +
`legacy_numbers:` migration field) is replaced.

## Context

A prior harness iteration introduced an `id: <slug>` frontmatter key on
every ADR and an optional `legacy_numbers:` list recording any prior
numeric identity. The existence of `legacy_numbers:` was itself the
evidence that numeric IDs are unstable: when the harness shipped an
ADR into an existing repo, scaffolded ADRs landed at non-canonical
numbers to avoid colliding with the operator's own decisions, and the
`legacy_numbers:` field existed so prose still resolving the old
numbers could be machine-rewritten.

Despite the slug `id:` and the `legacy_numbers:` map, numbers remained
load-bearing in three places:

1. Filenames — `docs/decisions/NNN-<slug>.md`.
2. URLs in prose — `[label](decisions/NNN-<slug>.md)`.
3. Numeric refs in prose — `ADR 003`, `ADR 0NN`.

An adversarial review in the ms-search reference repo surfaced concrete
instances of this fragility: an ADR body cited `ADR 003 (Evaluator
gate)` and `ADR 005 (hard constraints)`, but in that repo's namespace
those numbers had been reassigned to wholly unrelated decisions. The
numeric refs named the wrong documents; the parenthetical slugs named
the right ones. The body had been wrong since the renumber. The sweep
utility could not detect this because it excluded `docs/decisions/`
from its rewrite target set.

Slugs do not drift. They are named once at ADR authorship and survive
every subsequent reorganisation. The decision to make slugs canonical
in filenames, URLs, and prose closes the surface on which numeric
drift can manifest.

## Decision

Slugs are the canonical ADR identifier.

- ADR filenames are `docs/decisions/<slug>.md` with no leading `NNN-`
  token. The slug, taken from the file's `id:` frontmatter, is the
  filename stem.
- Prose and URL references use slug form: `ADR <slug>` in text,
  `decisions/<slug>.md` in markdown links. Numeric forms (`ADR NNN`,
  `ADR 0NN`, `decisions/NNN-<slug>.md`) do not appear in any
  text-source file.
- The `legacy_numbers:` frontmatter field is **removed**. Identity
  resolution no longer needs it (the slug is canonical), and the
  field's presence created a false sense that numeric refs were a
  legitimate alternate form. Repos migrating from the hybrid model
  drop the line during the rename pass.
- Sort order in `ls docs/decisions/` becomes alphabetical by slug.
  Chronological order is recoverable from frontmatter `last_reviewed:`
  or `git log --diff-filter=A -- docs/decisions/<slug>.md`. No
  leading-zero sort token is introduced.

## Consequences

- **MUST** name new ADRs as `docs/decisions/<slug>.md`. **MUST NOT**
  add a `NNN-` prefix. *(ADR adr-slug-canonical § Decision.)*
- **MUST** reference ADRs in prose as `ADR <slug>` and in markdown
  links as `decisions/<slug>.md`. **MUST NOT** write `ADR NNN`,
  `ADR 0NN`, or `decisions/NNN-<slug>.md`. *(ADR adr-slug-canonical
  § Decision.)*
- One-time rename of every existing ADR file drops the `NNN-` prefix
  and the `legacy_numbers:` line. External bookmarks — Jira ticket
  bodies, Slack threads, browser history, search-engine indexes —
  pointing at the numeric URL form break. This is a documented
  one-time cost; future links land at the slug URL and are durable
  across any subsequent reorganisation.
- `_canonical_manifest.py` enumerates ADRs by slug
  (`ADR_SLUGS_REQUIRED`). Validators resolve each slug to its file by
  scanning `docs/decisions/` for matching `id:` frontmatter. No
  filename-level enumeration is required.
- `sweep_adr_refs.py` becomes a one-way migration tool. It reads the
  current `NNN-<slug>.md` filenames in `docs/decisions/`, builds a
  number→slug map at migration time, and rewrites `ADR NNN` prose
  refs in non-ADR docs to `ADR <slug>`. After the migration sweep
  and the rename pass land, the tool is no-op in subsequent runs.
- The naming-convention rows in `AGENTS.md` (§ Where to save outputs)
  and `docs/processes/harness.md` (workflow table) name `<slug>.md`
  as the filename pattern. The "ADR identity and format" appendix
  in `harness.md` is removed — convention now lives in this ADR.

## Out of scope

- Renames of historical analysis docs or completed ExecPlans. Their
  bodies may reference old numeric URLs; the sweep utility rewrites
  those prose strings but does not rename the source files. Filenames
  for `docs/analysis/` and `docs/exec-plans/completed/` follow their
  own date-prefixed conventions, which are unaffected.
- A validator rule enforcing the no-numeric-ref convention. The
  convention is documented but not mechanically checked. Drift can
  creep back; that is a soft trade-off accepted at adoption time.
- Renames of any other harness asset (subagent configs, hooks,
  scripts).
- Sort-order tooling. No TUI sort-key, no leading-zero filename
  prefix, no manual sequence file. Alphabetical-by-slug is the
  steady-state shape.

## Notes

This ADR is itself the first instance of the new convention. It lives
at `docs/decisions/adr-slug-canonical.md`, not at
`008-adr-slug-canonical.md`. Every ADR authored after this one follows
the same shape; existing ADRs are renamed by the migration entry in
the harness CHANGELOG that introduces this ADR.
