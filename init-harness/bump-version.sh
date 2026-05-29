#!/usr/bin/env bash
#
# bump-version.sh — cut a new init-harness version.
#
# Computes the next semver from VERSION, scaffolds versions/<next>.md from a
# template, and writes the new VERSION. The pre-commit gate then refuses the
# commit until versions/<next>.md is filled in and staged alongside the asset
# edit. See SKILL.md → "How to update this skill".
#
# Usage:
#   ./bump-version.sh patch     # x.y.Z — fix to an existing harness file
#   ./bump-version.sh minor     # x.Y.0 — additive: new file/section/artifact
#   ./bump-version.sh major     # X.0.0 — breaking: file moved/renamed/removed
#
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VERSION_FILE="$SKILL_DIR/VERSION"
VERSIONS_DIR="$SKILL_DIR/versions"

LEVEL="${1:-}"
case "$LEVEL" in
  major|minor|patch) ;;
  *)
    echo "usage: $0 {major|minor|patch}" >&2
    exit 2
    ;;
esac

if [ ! -f "$VERSION_FILE" ]; then
  echo "✗ no VERSION file at $VERSION_FILE" >&2
  exit 1
fi

CURRENT=$(tr -d '[:space:]' < "$VERSION_FILE")
if ! echo "$CURRENT" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "✗ VERSION is not semver: '$CURRENT'" >&2
  exit 1
fi

IFS='.' read -r MAJ MIN PAT <<< "$CURRENT"
case "$LEVEL" in
  major) MAJ=$((MAJ + 1)); MIN=0; PAT=0 ;;
  minor) MIN=$((MIN + 1)); PAT=0 ;;
  patch) PAT=$((PAT + 1)) ;;
esac
NEXT="$MAJ.$MIN.$PAT"

NEW_FILE="$VERSIONS_DIR/$NEXT.md"
if [ -e "$NEW_FILE" ]; then
  echo "✗ $NEW_FILE already exists — refusing to overwrite" >&2
  exit 1
fi

case "$LEVEL" in
  patch) HINT="apply silently — it edits an existing file in place." ;;
  minor) HINT="fill the new file/section in if absent — additive, no confirmation needed." ;;
  major) HINT="BREAKING — show a diff and require explicit user confirmation before applying." ;;
esac

mkdir -p "$VERSIONS_DIR"
cat > "$NEW_FILE" <<EOF
# $NEXT — <one-line feature name>

## What changed

<Describe the change to the harness assets. One paragraph. A reader at the
previous version reads ONLY this file to learn what is new.>

## How to apply

<Idempotent, check-then-act migration steps. Each step reads the target file,
confirms the change is not already present, then applies it. A $LEVEL bump:
$HINT>

1. <step>
EOF

echo "$NEXT" > "$VERSION_FILE"

echo "→ bumped $CURRENT → $NEXT"
echo "  • wrote   $NEW_FILE  (fill in the two sections)"
echo "  • updated $VERSION_FILE"
echo
echo "Next: edit the asset(s), fill in $NEXT.md, then stage all three"
echo "(asset + VERSION + versions/$NEXT.md) in one commit. The pre-commit"
echo "gate refuses the commit otherwise."
