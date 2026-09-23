---
name: harness-loop
description: "Loop-termination check for the spec-kit harness: runs speckit_gate.py loop after /speckit-converge and, on stop-converged, closeout, which sets the plan to status: completed. Use when the after_converge hook fires or the user asks whether the unattended loop should continue."
---

Run:

```bash
python3 scripts/harness/speckit_gate.py loop
```

Report the command output verbatim. A non-zero exit halts the calling spec-kit
command; do not proceed past a failed loop check.

On `stop-converged`, the loop is green but the plan is not closed. Run:

```bash
python3 scripts/harness/speckit_gate.py closeout
```

It re-checks convergence and sets the plan to `status: completed`. Report its
output verbatim too; if it refuses, do not complete the plan by hand.
