---
name: commit
description: Generate and run a git commit after completing work. Use this skill whenever the user types /commit, says "commit this", "commit the changes", "make a commit", "git commit", "save my work", or wraps up a session and wants to persist their changes. The skill analyzes the diff in the current repo (pwd), spawns a fast cheap subagent to write a Conventional Commit message, and runs git commit — eliminating the friction of writing messages manually. Trigger even if the user just says "commit" with no other context.
---

# commit

Inspect the working tree in `pwd`, generate a Conventional Commit message via a cheap subagent, and run `git commit`.

## Step 1 — Check for changes in pwd

```bash
git status --short 2>/dev/null
```

If the output is empty → report "Nothing to commit, working tree clean." and stop.
If not in a git repo → report the error and stop.

## Step 2 — Stage and diff

1. Check what's already staged: `git diff --cached --name-only`
2. If nothing staged, stage everything: `git add -A`
3. Get the staged diff: `git diff --cached --stat` + `git diff --cached` (truncate body to ~200 lines if huge)
4. Get the last commit subject for context: `git log -1 --format="%s"`
5. Extract ticket ID from the current branch name:
   ```bash
   git rev-parse --abbrev-ref HEAD
   ```
   Match against `[A-Z]+-[0-9]+` (e.g. `STR-123`, `KKK-23451`). If found, store it; otherwise leave empty.

## Step 3 — Detect documentation references in staged files

Scan the staged file list for documentation artifacts (harness structure under `docs/`):

- **Analysis**: `docs/analysis/**`
- **Plan**: `docs/exec-plans/**` or any file named `*-plan.md`
- **ADRs**: `docs/decisions/**` (Architecture Decision Records)

Collect repo-relative paths of any matches. You'll use them in Step 5.

## Step 4 — Generate commit message via cheap subagent

Identify the current AI provider powering this session and spawn the equivalent fast/cheap model:

| Provider | Model to spawn |
|---|---|
| Anthropic (Claude) | `haiku` |
| OpenAI | `gpt-4o-mini` |
| Google | `gemini-2.0-flash` |
| Other | smallest/fastest available model |

Spawn the subagent with this prompt:

```
You are a git commit message writer. Write a single Conventional Commit message for the diff below.

Rules:
- Format: <type>(<optional scope>): <short description> [TICKET]
- Types allowed: feat | fix | chore | refactor | test | docs | ai | schema | security | config
- If a ticket ID is provided, append it at the end of the subject, separated by a space.
- First line ≤ 72 chars. No period at end.
- If changes span multiple concerns, pick the dominant type.
- Be specific but concise — sacrifice grammar for brevity.
- Output ONLY the commit message subject line. No body, no explanation.

Repo: <basename of pwd>
Last commit for context: <last commit subject>
Ticket ID: <ticket id or "none">

Diff stats:
<git diff --cached --stat output>

Diff:
<git diff --cached output, truncated if needed>
```

The subagent returns one line: the commit message subject.

## Step 5 — Build commit body (if docs are present)

If Step 3 found documentation files, build a body block:

```
<subject line>

Analysis: /docs/analysis/foo.md
Plan: /docs/exec-plans/active/bar-plan.md
ADRs: [/docs/decisions/001-auth.md, /docs/decisions/002-schema.md]
```

Rules:
- Omit any label (`Analysis:`, `Plan:`, `ADRs:`) if no files of that type are staged.
- `ADRs:` uses a bracketed list; `Analysis:` and `Plan:` are single paths (comma-separated if multiple).
- Use repo-relative paths starting with `/docs/`.

If no docs are staged, the commit message is just the subject line.

## Step 6 — Commit

```bash
git commit -m "<subject>

<body if present>"
```

Report the result: commit hash and message.

## Step 7 — Handle edge cases

- **Husky / pre-commit hook fails**: Show the hook output and stop. Do not retry with `--no-verify`.
- **Nothing staged after `git add -A`**: All files are gitignored. Report and stop.
- **Merge conflicts / rebase in progress**: Detect with `git status` and report; do not commit.
- **Detached HEAD**: Warn the user before committing.

## Format of final output

```
✓ abc1234 — feat(auth): add refresh token rotation
```

If failed, show the error inline.
