#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: tasks_to_issues.sh [specs/<feature>]" >&2
}

root_dir() {
  git rev-parse --show-toplevel
}

feature_dir() {
  local root=$1
  if [ "${1:-}" != "$root" ]; then
    return 1
  fi
  if [ -n "${FEATURE_DIR:-}" ]; then
    echo "$FEATURE_DIR"
    return
  fi
  if [ -f "$root/.specify/feature.json" ]; then
    python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
data = json.loads((root / ".specify/feature.json").read_text())
feature = data.get("feature_directory")
if feature:
    path = pathlib.Path(feature)
    print(path if path.is_absolute() else root / path)
PY
    return
  fi
  local matches=()
  while IFS= read -r plan; do
    if awk 'NR == 1 && $0 == "---" { fm=1; next } fm && $0 == "---" { exit } fm && $1 == "status:" { print $2 }' "$plan" | grep -qx active; then
      matches+=("$(dirname "$plan")")
    fi
  done < <(find "$root/specs" -mindepth 2 -maxdepth 2 -name plan.md 2>/dev/null | sort)
  if [ "${#matches[@]}" -ne 1 ]; then
    echo "expected one active specs/*/plan.md, found ${#matches[@]}" >&2
    return 1
  fi
  echo "${matches[0]}"
}

github_remote_url() {
  git config --get remote.origin.url
}

ensure_github() {
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh is required" >&2
    exit 1
  fi
  gh auth status >/dev/null
  local remote
  remote=$(github_remote_url)
  if ! echo "$remote" | grep -Eq 'github\.com[:/]'; then
    echo "remote.origin.url is not a GitHub URL: $remote" >&2
    exit 1
  fi
}

task_lines() {
  local tasks=$1
  grep -E '^- \[ \] T[0-9]{3}' "$tasks" | sed -E 's/^- \[ \] //'
}

derive_titles() {
  local tasks=$1 line id description
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    id=${line%% *}
    description=${line#"$id"}
    description=$(echo "$description" | sed -E 's/\[[^]]+\][[:space:]]*//g; s/^[[:space:]]+//')
    echo "$id: $description"
  done < <(task_lines "$tasks")
}

existing_task_ids() {
  gh issue list --state all --limit 200 --json number,title \
    | python3 -c 'import json, re, sys; print("\n".join(sorted(set(re.findall(r"\bT\d{3}\b", " ".join(i["title"] for i in json.load(sys.stdin)))))))'
}

create_issues() {
  local root feature tasks existing title id
  root=$(root_dir)
  if [ "${1:-}" ]; then
    feature="$root/${1#./}"
  else
    feature=$(feature_dir "$root")
  fi
  tasks="$feature/tasks.md"
  [ -f "$tasks" ] || { echo "missing tasks.md: $tasks" >&2; exit 1; }
  ensure_github
  existing=$(existing_task_ids)
  while IFS= read -r title; do
    id=${title%%:*}
    if echo "$existing" | grep -qx "$id"; then
      echo "skip $id: issue already exists"
      continue
    fi
    gh issue create --title "$title" --body "Task from $tasks" --assignee @me
  done < <(derive_titles "$tasks")
}

selftest() {
  local dir expected actual rc=0
  dir=$(mktemp -d)
  cat >"$dir/tasks.md" <<'EOF'
## Phase 1: Core
- [ ] T001 Create project structure
- [ ] T005 [P] Implement auth middleware in internal/auth/mw.go
- [ ] T012 [P] [US1] Create User model
- [X] T002 Already done
some prose that is not a task
EOF
  expected='T001: Create project structure
T005: Implement auth middleware in internal/auth/mw.go
T012: Create User model'
  actual=$(derive_titles "$dir/tasks.md")
  if [ "$actual" = "$expected" ]; then
    echo "tasks-to-issues-titles: PASS"
  else
    echo "tasks-to-issues-titles: FAIL" >&2
    diff <(echo "$expected") <(echo "$actual") >&2 || true
    rc=1
  fi
  rm -rf "$dir"
  return $rc
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
  --selftest)
    selftest || exit 1
    exit 0
    ;;
esac

create_issues "${1:-}"
