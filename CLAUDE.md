# Skills Repo

Each skill lives in its own subdirectory. The git repo root is `~/sebalinares-skills/`.

## Publishing a skill

`.gitignore` uses a whitelist pattern — everything is ignored by default, only explicitly listed skills are tracked. To publish a new skill, add two lines to `.gitignore`:

```
!my-skill/
!my-skill/**
```

Then stage and commit:

```bash
git add .gitignore my-skill/
git commit -m "feat: add my-skill"
git push origin main
```

After adding a new skill, re-run `install.sh` to create symlinks in all agent skill directories.

## Skill structure

Each skill directory contains at minimum:

```
my-skill/
  SKILL.md      # skill definition loaded by Claude Code
  evals/        # optional: evaluation cases
  assets/       # optional: files the skill copies/references
  resources/    # optional: reference material loaded into context
```

## What stays local (never committed)

- `*-workspace/` — eval iteration dirs
- `**/.claude/` — local agent permission files (settings.local.json)
- `.DS_Store`
- `grill-with-docs` — symlink to external agent

## Symlink targets

`install.sh` creates symlinks in:
- `~/.claude/skills/` — Claude Code
- `~/.agents/skills/` — OpenAI / Codex agents
