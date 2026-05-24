# changelog

Skill for updating a project's `CHANGELOG.md` from the current staged git diff.

Trigger: `/changelog` (or any phrasing like "update the changelog", "add a changelog entry for what I staged").

## Flow

1. Walks up from `pwd` to find the git root.
2. Locates `CHANGELOG.md` (offers to create one from `assets/CHANGELOG-template.md` if missing).
3. Reads `git diff --cached`.
4. Spawns a cheap subagent to summarize the diff into Keep-a-Changelog categories (Added/Changed/Deprecated/Removed/Fixed/Security).
5. Shows the proposed bullets, waits for `yes` / `no` / `edit`.
6. On confirm, prepends bullets under `## [Unreleased]` — merging into existing category subsections rather than duplicating.

## Out of scope

- Bumping versions
- Promoting `[Unreleased]` to a dated section
- `git add` / `git commit`

Those belong to whatever release script the target repo owns (e.g. `./scripts/bump-version`).

## Files

```
changelog/
├── SKILL.md
├── README.md
├── assets/
│   └── CHANGELOG-template.md
└── evals/
    └── evals.json
```
