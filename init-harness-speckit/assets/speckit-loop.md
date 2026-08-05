---
owner: {{REPO_NAME}}
status: stable
last_reviewed: {{DATE}}
update_trigger: on-harness-change
---

# Spec-kit Loop Runbook

This is the operator path for one feature.

## Attended Half

1. Create the spec:

   ```bash
   /speckit-specify <feature brief>
   /speckit-clarify
   ```

2. Generate the plan and tasks:

   ```bash
   /speckit-plan
   /speckit-tasks
   /speckit-analyze
   ```

3. Read the analyze output. If it is acceptable, edit
   `specs/<feature>/plan.md`:

   ```yaml
   status: active
   analyzed: <date>
   covers:
     - <path/prefix/>
   verify: <command that proves this feature works>
   ```

The full gate requires `status: active`, a non-empty `analyzed:`, and
`tasks.md`.

## Lite Path

For a plan small enough that a task breakdown adds nothing, skip `/speckit-tasks`
and take the lite path:

```bash
/harness-implement-lite
```

Its gate (`speckit_gate.py gate-lite`) requires exactly one active plan with
`analyzed:` filled and a **real** `verify:` command — and no `tasks.md`. Do not
create `tasks.md` just to satisfy the full gate; `covers:` and `verify:` are
the controls either way. Close out the same way as the full path.

## Parallel Fan-out

For unchecked `[P]` tasks in the current phase:

```bash
scripts/harness/wt_fanout.sh start
```

Each worktree is created at `../<repo>-wt-<TASKID>` on branch
`wt/<feature-branch>/<TASKID>`.

After agents finish their task branches:

```bash
scripts/harness/wt_fanout.sh collect
```

If a conflict occurs, stop and fix `tasks.md`; a conflict means the `[P]`
marking was wrong.

Inspect live worktrees:

```bash
scripts/harness/wt_fanout.sh status
```

## Unattended Loop

Run:

```bash
/speckit-implement
/speckit-converge
```

Hooks run `verify:` after implementation and `harness-loop` after convergence.
The loop output means:

- `continue`: run another implement/converge pass.
- `stop-converged`: no unchecked tasks remain and `verify:` is green. Not
  finished yet — close the plan out (below).
- `stop-cap`: stop after five passes. Open a partial PR and paste the printed
  remaining-work block as a PR comment.

## Close Out

```bash
python3 scripts/harness/speckit_gate.py closeout
```

It re-checks that no tasks are unchecked and `verify:` is green, then sets
`plan.md` to `status: completed` and prints the remaining session-exit steps.
It refuses if either check fails. Leaving a finished plan at `status: active`
blocks the next feature's gate.

## Issues

To turn `tasks.md` into GitHub issues, use spec-kit's own command:

```bash
/speckit-taskstoissues
```

It deduplicates against existing issues via the GitHub MCP server and assigns
issues to `@me`. Requires the GitHub MCP server (see `docs/processes/dev-setup.md`
§ GitHub MCP server).
