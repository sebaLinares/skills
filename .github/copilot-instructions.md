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

## Cross-agent constraints

Skills are shared between Claude Code, OpenAI Codex, and GitHub Copilot. The `description` frontmatter field is the compatibility surface — it is passed verbatim to each agent's tool registry.

| Field | Rule | Reason |
|---|---|---|
| `name` | kebab-case, `[a-z0-9-]`, ≤50 chars | Codex/Copilot reject names with dots or spaces; 50 < 64 hard limit everywhere |
| `description` | plain text, ≤1,000 chars | Codex hard-limits at 1,024; use 1,000 as safe target |

**Description writing rules:**
- Put the core capability in the first sentence (some agents truncate at ~500 chars)
- List trigger phrases ("when the user says X") after the capability summary
- No markdown inside the description value — backticks are OK, headers/bullets are not
- Long implementation details belong in the SKILL.md body, not the frontmatter description

**Verify before committing a new or updated skill:**
```bash
echo -n "your description here" | wc -c   # must be ≤ 1000
```
