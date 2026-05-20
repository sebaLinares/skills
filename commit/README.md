# commit

Generates a Conventional Commit message from the current diff and runs `git commit` — no message writing required.

## How to trigger

Inside Claude Code, in any git repo:

```
/commit
```

Or just say: **"commit this"**, **"make a commit"**, **"save my work"**

## What happens

1. Checks `git status` — stops if nothing to commit
2. Stages unstaged changes (`git add -A`) if nothing is staged yet
3. Reads the diff and last commit for context
4. Spawns a fast/cheap model (Haiku, gpt-4o-mini, etc.) to write the message
5. Runs `git commit -m "<generated message>"`
6. Reports the commit hash

## Output format

```
✓ abc1234 — feat(auth): add refresh token rotation
```

## Notes

- Follows [Conventional Commits](https://www.conventionalcommits.org/): `feat`, `fix`, `chore`, `refactor`, `test`, `docs`, `ai`, `schema`, `security`, `config`
- If the branch name contains a ticket ID (`ABC-123`), it's appended to the subject
- If docs files (`docs/analysis/`, `docs/exec-plans/`, `docs/decisions/`) are staged, a body block is added with paths
- Never skips pre-commit hooks (`--no-verify`)
