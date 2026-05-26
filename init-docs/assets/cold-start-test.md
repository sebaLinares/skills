---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-restructure
---

# Cold-start test

The quarterly falsifier ritual. Five questions, run in a NEW agent
session with no priors and no chat context, answered from repo
content only. If the agent cannot answer, the repo is no longer the
spec for that surface — and the [bootstrap
contract](initialization-checklist.md) for that surface has regressed.

This is the legibility test. The bootstrap contract probes
*operability* (can a command run); the cold-start test probes
*legibility* (can a fresh outsider read the repo and form a coherent
picture). Both ride on the same operating principle: if it is not in
the repo, it does not exist.

## Why this exists

A repo that compiles and tests green can still be illegible. The
agent that scaffolded it carries context the next agent will not.
Operating-principle violations creep in as folk knowledge — "we all
know X is in this folder", "the deploy script is the one Sebastián
wrote", "ignore the third migration, it's stale". Periodic
re-verification in a fresh session is the only mechanism that catches
this drift, because no continuous test can probe "would a stranger
understand this?"

The lecture series this harness draws from calls the cold-start test
the *primary quality measure* of a repo built around the operating
principle. Without it, "the repo is the spec" is unfalsifiable.

## When to run

**At least quarterly.** Pick a fixed day (e.g., the 1st of every
quarter) and run it then. Soft cadence — sooner if any of:

- A major structural change (folder layout, ADR supersession, large
  refactor) lands.
- Onboarding pain is reported (a new contributor or agent gets
  stuck on something the repo should answer).
- A bootstrap-contract surface regresses (a `[⚠ placeholder]` or
  `[✗ surface missing]` shows up on an `/init-docs` re-run).

Skip if all three of these are true: no structural change since last
run, no onboarding pain, contract verdict still clean. The cadence
exists to catch drift, not to manufacture work.

## How to run

1. **Open a NEW agent session.** Fresh context, no priors, no chat
   history. This is non-negotiable — running it in the current
   session pollutes the test with shared context.
2. **Paste the five questions verbatim, one at a time.** Wait for
   each answer before asking the next.
3. **The agent answers each in ≤1 paragraph, using repo content
   only.** No chat-only knowledge, no priors, no web search. If the
   agent cannot answer from the repo, that is the answer — record
   the failure.
4. **Save the session transcript to `docs/generated/cold-start-test.md`**
   as a new top section. Heading: `## YYYY-MM-DD — Qn` (`Qn` =
   quarter and year, e.g. `Q3-2026`). Newest section at the top;
   older sections scroll down.
5. **Diff against the prior section.** What changed? Which answers
   got harder, which got easier, which broke?

## The five questions

| # | Question | Surfaces the agent should resolve via |
|---|---|---|
| 1 | What is this system? (one paragraph, no jargon) | `README.md` + `ARCHITECTURE.md` |
| 2 | How is it organised? (folder layout, bounded contexts, major moving parts) | `docs/README.md` (catalog) + `ARCHITECTURE.md` + `docs/architecture/` |
| 3 | How do I run it locally? | `docs/processes/dev-setup.md` § Running locally + § Common commands |
| 4 | How do I verify it works? | `docs/processes/dev-setup.md` § Feature verification convention + `docs/FEATURES.md` § Verify column |
| 5 | Where are we now? (in-flight work, failing features, next steps) | `docs/FEATURES.md` § Active + § Failing + `docs/exec-plans/active/` + `docs/tech-debt-tracker.md` |

Questions 3-5 overlap with the bootstrap-contract conditions; questions
1-2 are unique to this test (identity + organization, which the
contract does not probe).

## Pass criteria

A passing answer to a question:

- Is **sourced entirely from repo content.** No chat-only knowledge,
  no priors. The agent should be able to cite the file path for each
  load-bearing claim.
- Is **≤1 paragraph.** Long answers are usually a sign that the
  repo's framing is unclear — passing the answer through the agent's
  prose has compressed it.
- **Aims for ≤10 file reads** to answer all five. Soft target; if
  every answer requires opening 20 files, the legibility has
  weakened. Flag for steering loop.

A failing answer:

- "I cannot find this in the repo."
- "I need more context than the repo provides."
- An answer that contradicts what the repo says (the agent
  hallucinated from training data rather than reading).

## What to do with the result

| Outcome | Action |
|---|---|
| All five answered cleanly, no drift from prior quarter | Commit the transcript. Done. |
| Drift in any answer (new info, removed info, conflicting info) | Note in next steering loop. Was a guide missing, or a sensor missing? |
| One or more questions failed | The bootstrap contract for that surface has regressed. Re-run [Initialization checklist](initialization-checklist.md) on the affected surface and fix the placeholder/missing artifact. |
| The agent hallucinated | Treat as a failure. The repo has a load-bearing fact that exists only in training data, not in the repo. Capture it in the repo (operating principle); re-run the test. |

## Pruning

The rolling log grows ~1 section per quarter. At any point, the user
may move older sections into an archive file
(`docs/generated/cold-start-test-archive.md`) to keep the main file
short. No automation — pruning is a manual judgment call.

## Out of scope

- Slash command for `/cold-start-test` — docs-only ritual, no
  automation.
- Mechanical enforcement of the cadence — the harness names the
  ritual and makes it the cheap path; humans run it.
- Coupling to Session exit — Session exit is per-session; the
  cold-start test is per-quarter. Different surfaces, different
  cadences.
