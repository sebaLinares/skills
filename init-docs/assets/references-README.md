---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-convention-change
---

# References

Authoritative specs the code must satisfy, extracted from sources outside
this repo. Lives here because of the harness operating principle:
*if it is not in the repo, it does not exist* (see
[ADR harness-design](../decisions/001-harness-design.md)).

**Mental model:** stuff the code must conform to, that doesn't live in this
code itself.

## Reference ≠ analysis

- **Reference** = authoritative spec. No opinions, no options, no
  recommendations. Just what the thing is / does / expects.
- **Analysis** = investigation with findings and a recommendation. Has
  opinions. Goes to `docs/analysis/`, not here.

If the doc has an opinion, it's not a reference.

## Convention

- **Filename:** `<name>-llms.txt`
- **Format:** plain text optimised for LLM consumption — condensed, no
  navigation chrome, no marketing copy. Follow the `llms.txt` convention
  (see llmstxt.org).
- **One file per external system.** Do not combine.

## What belongs here

- External APIs the codebase integrates with.
- Internal services outside this repo that this service calls.
- **Legacy-system behaviour specs** — extracted contracts or behaviours from
  a predecessor system this repo replaces, treated as authoritative port
  targets. From this repo's perspective the predecessor is external; its
  behaviour is a spec the new code must honour. The `# Source` header points
  at the predecessor repo + commit.
- External libraries whose behaviour the agent needs to reason about beyond
  what the language's standard doc tooling provides.

## What does not belong here

- Standard library docs for the project's language.
- Third-party libraries that are fully documented via standard doc tooling.
- Per-deploy or environment-specific configuration.
- **Analyses, gap reports, or port recommendations** — those go to
  `docs/analysis/`.

## Required header

Every file in this folder must start with a `# Source` section:

~~~
# Source
- Upstream URL: <url>
- Retrieved: YYYY-MM-DD
- Upstream version: <version or commit>
~~~

## Maintenance

Refresh a file when the upstream changes materially. If nobody can confirm
when it was last accurate, **delete it** — a stale reference is worse than a
missing one, because the agent will trust it and act on it.

## Current files

*(none yet)*
