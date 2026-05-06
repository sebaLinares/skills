#!/bin/bash
# Symlink all skills into ~/.claude/skills/
# Run once after cloning, re-run when new skills are added.
set -e

SKILLS_REPO="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.claude/skills"
mkdir -p "$TARGET_DIR"

for skill_dir in "$SKILLS_REPO"/*/; do
  skill_name=$(basename "$skill_dir")
  [[ "$skill_name" == .* ]] && continue
  ln -sfn "$skill_dir" "$TARGET_DIR/$skill_name"
  echo "linked: $skill_name"
done
