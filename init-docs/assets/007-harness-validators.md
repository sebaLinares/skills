---
owner: {{REPO_NAME}}
status: accepted
last_reviewed: 2026-05-26
update_trigger: on-supersession
---

# ADR 007 — Harness validators (structure check + doc garbage collector)

## Status

Accepted; extends ADR 001 (harness design), ADR 003 (Evaluator gate), and
ADR 005 (hard constraints) by adding mechanical sensors for the
documentation contract those ADRs establish.

## Context

The harness ships a growing set of canonical files — repo-root anchors,
catalog and ledgers, processes, decisions, subagent configs, hooks — that
agents and humans must agree exist, carry consistent metadata, and
reference each other in known ways. Each individual file is enforced by
review; the *set* is not. Drift surfaces incrementally: a renamed
section breaks an inbound reference, a forgotten `last_reviewed` date
leaves a doc invisibly stale, a dashboard file lands under `docs/` when
it should have lived in `docs/generated/`.

ADR 003 names the worker/checker split that closes one half of this
problem (the Evaluator gates plan completion). The other half — *is the
documentation contract intact?* — has no mechanical enforcer in the
scaffolded harness. ms-search (this skill's reference user) ships two
Python scripts that do the job for that repo; they are project-specific
in their hardcoded paths and required-reference table, but the *shape*
of the checks generalises cleanly.

## Decision

Ship two stdlib-only Python validators from the init-docs skill,
installed at `scripts/harness/` in every scaffolded repo:

1. **`check_harness_structure.py`** — fail-fast pre-commit-friendly
   check. Verifies existence of every canonical file, presence of the
   4-key YAML frontmatter on the markdown subset, presence of required
   cross-references, absence of forbidden ephemera under `docs/`, and
   absence of absolute paths or generated/-as-canonical phrasing in any
   scanned text. Exit non-zero on any finding.

2. **`garbage_collect_docs.py`** — slower, broader audit suitable for
   nightly or weekly runs. Broken-reference scan, two-pass metadata
   check (strict on canonical, lenient elsewhere), stale-review flag
   (default 90 days), orphan-doc detection, ephemeral-doc detection.
   Renders a markdown report; `--strict` returns non-zero on warnings
   too.

Both scripts read a shared `_canonical_manifest.py` module — the single
source of truth for the list of canonical files, the frontmatter
subset, required references, forbidden globs, and scan roots. Every
future init-docs CHANGELOG entry that adds, renames, or removes a
canonical file MUST update this manifest in the same entry.

Both scripts honour `HARNESS_BYPASS="<reason>"` (same convention as the
plan-coverage sensor — see ADR 003) and accept `--dry-run` for skill
self-verification (reports findings to stderr, always exits 0).

## Frontmatter scope

The 4-key block (`owner`, `status`, `last_reviewed`, `update_trigger`)
is required on the 18 canonical *markdown* files: the three repo-root
guides, the catalog, the ledgers, the three processes, the six ADRs,
and the two convention READMEs.

Excluded from the frontmatter check (existence-only):

- `CLAUDE.md` — symlink to `AGENTS.md`; would double-count.
- `.claude/agents/*.md` — already carry Claude Code's subagent
  frontmatter schema (`name`, `description`, `model`, `effort`,
  `tools`). Coexistence with the harness 4 keys is a separate question
  pending Claude Code parser-tolerance verification; tracked as a
  follow-up in `docs/tech-debt-tracker.md`.
- `.claude/hooks/*.{sh,mjs,js,py}` — executables; YAML in a shebang
  line breaks them.
- `scripts/harness/*.py` — Python modules; metadata lives in this
  manifest.
- `.harness-version` — one-line ISO date marker.

## Wiring posture (intentionally not shipped)

The skill does **not** install:

- A Makefile target that runs the validators.
- A pre-commit hook that calls them.
- A GitHub Actions workflow that runs them on PRs.

This mirrors the posture established by the plan-coverage sensor in the
2026-04-20 CHANGELOG entry (ADR 003 in the ms-search reference repo).
Wiring is stack-specific; the skill ships the contract in
`docs/processes/dev-setup.md § Harness validators`, and the repo's
owners translate it into Makefile / pre-commit / Task / just / CI as
their stack prefers.

## Self-verification

Step 7 of the 2026-05-26 CHANGELOG entry that introduces these
validators runs `check_harness_structure.py --dry-run` as the last step
of an audit applying that entry, then flips to a real run only if
dry-run passes. The marker advances only on a passing real run. This is
the first init-docs entry whose application is verified by the artifact
it installs.

## Consequences

### Positive

- Documentation drift becomes detectable at commit time, not at PR
  review or in the next agent session.
- Adding a canonical file becomes a single coordinated edit (manifest
  + asset + CHANGELOG entry) rather than a scattered patch across the
  skill.
- The manifest is also a deployment receipt — its presence and
  validity *is* the proof that the harness scaffold completed.

### Negative

- Every future CHANGELOG entry touching the canonical set pays a
  manifest tax. Acceptable; the cost is one list edit.
- Subagent configs are exempt for v1 — the harness 4 keys can drift
  on those files. Mitigated by their small count (currently 2) and by
  the tech-debt tracker entry that follows up on schema coexistence.
- Self-verification (step 7) means a bug in the validators can block
  every audit applying entries dated 2026-05-26 or later. Mitigated by
  the `--dry-run` first-pass.
- The validators are Python (≥ 3.9). Repos without Python on `PATH`
  must install it or substitute. The contract is in the manifest
  module; a stack-native re-implementation is acceptable.

## Appendix — example wiring (example only, NOT shipped)

These snippets illustrate how a stack might wire the validators. They
are deliberately not part of the scaffold.

### Example Makefile target

```makefile
.PHONY: verify-docs
verify-docs:
	@python3 scripts/harness/check_harness_structure.py

.PHONY: gc-docs
gc-docs:
	@python3 scripts/harness/garbage_collect_docs.py \
	    --report docs/generated/harness-gc-report.md
```

### Example pre-commit hook gating

```bash
#!/usr/bin/env bash
set -euo pipefail
if [ -n "${HARNESS_BYPASS:-}" ]; then
    exit 0
fi
python3 scripts/harness/check_harness_structure.py
```

### Example GitHub Actions step

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- name: Harness structure check
  run: python3 scripts/harness/check_harness_structure.py
- name: Doc garbage collection (warn-only on PR)
  run: python3 scripts/harness/garbage_collect_docs.py
```

Treat each as a starting point; the contract — exit-zero on success,
`HARNESS_BYPASS` honoured, stdlib-only — is what the harness relies on.
