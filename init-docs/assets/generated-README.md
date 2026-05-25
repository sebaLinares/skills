---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-convention-change
---

# Generated

Machine-generated artifacts. **Do not edit by hand** — anything here is
produced by a script and will be overwritten on the next run.

## What lives here

| Subfolder | Produced by | Refresh |
|---|---|---|

*Add rows as generators are introduced.*

## Why this is tracked in git

Per the harness operating principle (*if it is not in the repo, it
does not exist* — see [AGENTS.md](../../AGENTS.md)), generated
artifacts are checked in so agents can read them without running the
generator. If the output drifts from the source, re-run the generator
and commit.

## Adding a new generated artifact

1. Create a subfolder under `docs/generated/`.
2. Point the generator script at that subfolder — **never at `docs/`
   itself**. Generators that wipe their output directory (`rm -rf`,
   `clean`, etc.) will destroy the rest of the harness if pointed at
   `docs/`. Always scope to a dedicated `docs/generated/<name>/`
   subfolder.
3. Add a row to the table above.
4. If the generator has a hazard worth flagging (destructive cleanup,
   network access, large output), note it in
   [`../tech-debt-tracker.md`](../tech-debt-tracker.md).
