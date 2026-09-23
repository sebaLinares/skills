---
name: harness-implement-lite
description: "Lite Execute path of the spec-kit harness: runs speckit_gate.py gate-lite and, only if it passes, executes the active specs/<feature>/plan.md directly without tasks.md, inside the plan's covers:, until its verify: is green. Use when the before_implement hook or the user picks the lite path for a small analyzed plan. Not for plans that have tasks.md (that is /speckit-implement)."
---

Run:

```bash
python3 scripts/harness/speckit_gate.py gate-lite
```

If the command fails, report the output and stop.

If it passes, the gate is the authorization to execute the active plan directly.
Do not reject execution because `tasks.md` is missing, and do not run
`/speckit-implement` or create `tasks.md`.

Then:

1. Read the active `specs/<feature>/plan.md`.
2. Execute the plan's listed steps with normal Edit/Bash tools.
3. Before every edit, confirm the path prefix-matches the plan's `covers:`.
4. Run the plan's `verify:` command until it is green, or report the failure
   without forcing it.
5. After green verification, set the plan to `status: completed` and add
   `docs/README.md` entries only when the plan requires new catalog entries and
   covers that file.
