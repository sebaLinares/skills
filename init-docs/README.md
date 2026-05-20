# init-docs

Bootstraps an AI-harness documentation system in any project. After running, every AI agent that opens the repo gets structured context: how the project is organized, what decisions were made, what plans are in flight, and how to operate safely.

## How to trigger

Inside Claude Code, inside the project you want to set up:

```
/init-docs
```

Optionally include a domain description so tags are accurate:

```
/init-docs NestJS e-commerce backend using Stripe and PostgreSQL
```

Or say: **"set up docs"**, **"scaffold a harness"**, **"initialize documentation structure"**

## What it creates

```
AGENTS.md                          ← AI entry point (harness operating manual pointer)
CLAUDE.md → AGENTS.md             ← symlink (Claude Code reads this automatically)
ARCHITECTURE.md                    ← skeleton to fill: system shape, ADRs, constraints
SECURITY.md                        ← skeleton to fill: threat model, secrets, auth
.harness-version                   ← version marker for incremental updates

docs/
├── README.md                      ← master catalog with tag vocabulary
├── PLANS.md                       ← ExecPlan contract (what every plan must include)
├── FEATURES.md                    ← feature ledger (empty; rows added per feature)
├── tech-debt-tracker.md
├── analysis/        _template.md
├── architecture/
├── decisions/
│   ├── 001-harness-design.md      ← ADR: why this structure exists
│   ├── 002-session-exit.md        ← ADR: session exit checklist
│   ├── 003-evaluator-gate.md      ← ADR: plan validation gate
│   ├── 004-fleet-model-policy.md  ← ADR: model selection policy
│   └── 005-hard-constraints.md    ← ADR: hard constraints for agents
├── exec-plans/      active/ + completed/ + _template.md
├── generated/       README.md (convention: check in generated artifacts)
├── processes/
│   ├── harness.md                 ← day-to-day operating manual
│   ├── dev-setup.md               ← skeleton to fill: toolchain, commands, hooks
│   └── model-policy.md            ← fleet-wide model selection rules
├── references/      README.md (llms.txt convention for external specs)
└── tickets/
```

## Typical first-use flow

```bash
cd ~/my-new-project
claude

# Inside Claude Code:
/init-docs

# Fill in the skeletons Claude flags as "needs filling":
# - ARCHITECTURE.md
# - SECURITY.md
# - docs/processes/dev-setup.md
```

## Updating an existing harness

If `.harness-version` is present and older than the skill's changelog, the skill runs in **audit mode**: it reads pending changelog entries and applies them incrementally, one at a time, confirming before any destructive change.

```
/init-docs   ← detects the version marker and runs audit automatically
```

## Notes

- Never modifies source code — only documentation and root markdown files
- Safe to re-run: existing files are skipped unless you choose "overwrite"
- `ARCHITECTURE.md` and `SECURITY.md` are intentionally left as skeletons — agents can't infer why a system is shaped the way it is; only you can fill that in
