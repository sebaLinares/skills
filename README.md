# sebalinares-skills

Reusable skills for Claude Code. A skill is a slash command (`/skill-name`) you can invoke inside any Claude Code session — Claude reads the skill's instructions and executes them in your current project.

## Install

```bash
git clone https://github.com/sebalinares/sebalinares-skills.git ~/sebalinares-skills
cd ~/sebalinares-skills
./install.sh
```

`install.sh` symlinks every skill into `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex / Copilot). Run it once after cloning, and again whenever a new skill is added.

## Usage

1. Open Claude Code in **any project**: `claude` (or via the IDE extension)
2. Type `/` — skills appear in autocomplete
3. Invoke a skill by name, e.g. `/init-docs`

That's it. Skills run in the context of your current working directory.

## Available skills

| Skill | What it does | How to trigger |
|-------|-------------|----------------|
| [`/init-docs`](init-docs/README.md) | Bootstraps an AI-harness docs structure (`docs/`, ADRs, `AGENTS.md`, `CLAUDE.md` symlink, templates) so agents have structured project context | `/init-docs` or "set up docs" or "scaffold a harness" |
| [`/commit`](commit/README.md) | Analyzes the git diff, generates a Conventional Commit message via a fast model, and runs `git commit` | `/commit` or "commit this" or "make a commit" |

## Typical first-use flow

```
# 1. Install skills (once)
cd ~/sebalinares-skills && ./install.sh

# 2. Go to a project you want to set up
cd ~/my-project
claude

# 3. Inside Claude Code, bootstrap the docs harness
/init-docs

# 4. When you're ready to commit work
/commit
```

## Adding a new skill

1. Create `my-skill/SKILL.md` with YAML frontmatter (`name`, `description`) and step-by-step instructions
2. Whitelist it in `.gitignore`:
   ```
   !my-skill/
   !my-skill/**
   ```
3. Run `./install.sh` to symlink it
4. Commit and push

See `CLAUDE.md` for frontmatter rules and cross-agent compatibility constraints.
