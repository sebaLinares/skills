#!/usr/bin/env bash
# Symlink all skills into agent skill directories.
# Run once after cloning, re-run when new skills are added.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.agents/skills"
)

for target in "${TARGETS[@]}"; do
  mkdir -p "$target"
  for dir in "$SCRIPT_DIR"/*/; do
    name="$(basename "$dir")"
    [[ "$name" == .* ]] && continue
    ln -sfn "$dir" "$target/$name"
    echo "  → $target/$name"
  done
done

echo "Done."
