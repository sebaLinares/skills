#!/usr/bin/env bash
# verify-covers-hook.sh — PreToolUse hook reference implementation.
#
# Blocks Edit / Write / MultiEdit tool calls whose file_path is not
# prefix-matched by any covers: glob in an active ExecPlan
# (`docs/exec-plans/active/*.md`).
#
# Contract (ADR 005 hard constraint, covers: rule):
#   Before each Edit/Write, the target path MUST match the current plan's
#   covers:. The pre-commit plan-coverage sensor is the last line of
#   defence; this hook is the first.
#
# This is a reference implementation shipped by init-docs. Stack-neutral
# (bash + jq). Replace with a stack-native version if preferred (Node,
# Python, Go) — the contract is what matters, not the language.
#
# Install:
#   1. Place this script at .claude/hooks/verify-covers-hook.sh (chmod +x).
#   2. Register in .claude/settings.local.json (per-contributor, gitignored;
#      NOT .claude/settings.json):
#        {
#          "hooks": {
#            "PreToolUse": [
#              {
#                "matcher": "Edit|Write|MultiEdit",
#                "hooks": [
#                  { "type": "command",
#                    "command": ".claude/hooks/verify-covers-hook.sh" }
#                ]
#              }
#            ]
#          }
#        }
#
# Bypass: export HARNESS_BYPASS="<reason>" in the session env.
# Doc/config edits (docs/, AGENTS.md, root anchors) are always allowed.
#
# Requires: jq, git.

set -euo pipefail

if [[ -n "${HARNESS_BYPASS:-}" ]]; then
  exit 0
fi

input=$(cat)
tool=$(echo "$input" | jq -r '.tool_name // empty')
case "$tool" in
  Edit|Write|MultiEdit) ;;
  *) exit 0 ;;
esac

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
[[ -z "$file_path" ]] && exit 0

# Canonicalise paths to avoid macOS symlink mismatches (e.g. /var vs
# /private/var). The Write tool can target a file that does not yet
# exist, so fall back to canonicalising the parent dir + basename.
canon_path() {
  local p="$1"
  if [[ -e "$p" ]]; then
    printf '%s/%s\n' "$(cd "$(dirname "$p")" && pwd -P)" "$(basename "$p")"
  else
    local parent
    parent=$(dirname "$p")
    if [[ -d "$parent" ]]; then
      printf '%s/%s\n' "$(cd "$parent" && pwd -P)" "$(basename "$p")"
    else
      printf '%s\n' "$p"
    fi
  fi
}

repo_root=$(cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && pwd -P)
file_path_canon=$(canon_path "$file_path")
rel_path="${file_path_canon#"$repo_root"/}"

# Always-allowed paths: harness docs and root anchors. Editing the plan
# itself (e.g. checking off Concrete steps) is part of execution.
case "$rel_path" in
  docs/*|.harness-version|AGENTS.md|CLAUDE.md|ARCHITECTURE.md|SECURITY.md|README.md)
    exit 0 ;;
esac

plans_dir="$repo_root/docs/exec-plans/active"
[[ ! -d "$plans_dir" ]] && exit 0

# Collect covers: globs from every plan in active/.
globs=()
shopt -s nullglob
for plan in "$plans_dir"/*.md; do
  in_covers=false
  while IFS= read -r line; do
    if [[ "$line" =~ ^covers: ]]; then in_covers=true; continue; fi
    if $in_covers; then
      if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+(.+)$ ]]; then
        g="${BASH_REMATCH[1]}"
        g="${g%\"}"; g="${g#\"}"; g="${g%\'}"; g="${g#\'}"
        g="${g%% #*}"
        g="${g% }"
        globs+=("$g")
      else
        in_covers=false
      fi
    fi
  done < "$plan"
done

# No active plan or empty covers: → fail open. Other gates will catch
# unplanned execution; this hook only enforces the covers: contract.
[[ ${#globs[@]} -eq 0 ]] && exit 0

for glob in "${globs[@]}"; do
  # shellcheck disable=SC2254  # intentional glob expansion in case
  case "$rel_path" in
    $glob) exit 0 ;;
  esac
done

cat >&2 <<EOF
[covers:-hook] '$rel_path' is not covered by any active plan's covers:.
Active globs: ${globs[*]}

Choose:
  (a) extend covers: in the plan (re-approval required, per Phase 6),
  (b) log the side-change to docs/tech-debt-tracker.md, or
  (c) drop the change.

To bypass for this session only:
  export HARNESS_BYPASS="<reason>"
EOF
exit 2
