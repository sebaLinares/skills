# init-docs

Glossary for the init-docs skill — the harness-scaffolding artifact that seeds `docs/`, `AGENTS.md`, and operating manuals into a fresh repo.

## Language

**Feature**:
A coarse user-observable capability of the product, paired with a verification command that resolves to a tagged subset of tests (one feature, N tests).
_Avoid_: test, behavior, story, requirement (each names only one facet)

**Feature state**:
One of `not_started / active / blocked / failing / passing`. Writers are partitioned: humans set `not_started` (on creation) and `blocked` (with a one-line reason); plan-approval flow sets `active`; the verifier loop alone sets `passing` and `failing`. `passing → failing` is a regression; there is no transition back to `not_started`.

**Verification (`verify:` / `verify-cmd:`)**:
Every **Feature** declares how it is checked at creation time. `verify:` holds a tag selector (e.g. `feat:checkout`) interpreted by a stack-specific convention documented in `dev-setup.md` ("how this repo runs its test command with a tag filter"). `verify-cmd:` is the escape hatch — a literal shell string — used only when the tagged-test convention does not apply. Exactly one of the two is required; presence is non-negotiable even for `not_started` features.

**Feature provenance (`source:`)**:
Every **Feature** row records where it came from — `brief`, `prd:<path>`, `analysis:<path>`, or `inferred`. Defuses free-form bloat without imposing a phase gate on Feature creation itself.

## Relationships

- A **Feature** is verified by one or more tests, addressed via a single tagged subset command (`#suite-tag` / `--grep feat:<id>` / equivalent).
- A **Feature** is *in scope* of zero or one active **ExecPlan**; once delivered, its passing state is owned by the verifier loop, not by the plan.
- **Feature state** ownership reflects the worker/checker split: the agent writing or executing a plan never writes `passing` itself.
- An **ExecPlan** carries a `features:` frontmatter list. It is non-optional: either non-empty (every ID must resolve to a row in FEATURES.md) or empty + `feature-less-reason: <one line>` declaring the plan ships no user-observable behavior. Approving the plan sets each referenced Feature to `active`; landing in `completed/` hands state back to the verifier loop.
- Creating a Feature is not harness-gated — no analysis required. Features are the *input* to the analysis/plan flow, not the output.

**FEATURES.md**:
The repo-wide ledger of **Features**, stored as `docs/FEATURES.md`. Markdown sections (one per non-passing state, plus a single `Passing` bulk section) over markdown tables with fixed columns `ID | Behavior | Verify | State | Source | Notes`. No JSON schema, no parser, no verifier script — guides-only, consistent with the rest of the skill's "scripts deferred to the project" posture.

**Session**:
One agent conversation, bounded by the user opening and closing the chat (or compaction). May contain zero, one, or many **ExecPlans**, or pure investigation with none. Distinct from a plan: Phase 6 closes a plan; **Session exit** closes a session. The two concepts overlap only when the session contains exactly one plan that finishes inside it.
_Avoid_: "run", "task" (each names a sub-unit, not the conversation envelope).

## Flagged ambiguities

- "feature" was briefly conflated with "acceptance test" — resolved: a feature is the user-visible capability; acceptance tests are its evidence. Multiple tests per feature is normal.
