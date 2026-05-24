---
name: changelog
description: Update a project's CHANGELOG.md with entries summarizing the current staged git diff. Use this skill whenever the user types /changelog, says "update the changelog", "add changelog entry", "log these changes", "write changelog entries for what I staged", "summarize my staged changes for the changelog", or mentions Keep a Changelog. The skill walks up from pwd to find the git root, looks for CHANGELOG.md, reads the staged diff, spawns a cheap subagent to summarize it into Keep-a-Changelog categories (Added/Changed/Deprecated/Removed/Fixed/Security), shows the proposed bullets, and prepends them under the [Unreleased] section after the user confirms. Does NOT bump versions, promote [Unreleased] to a dated section, git add, or git commit — those belong to a separate release flow. Trigger even if the user just says "changelog" with no other context.
---

# changelog

Summarize the current staged git diff into Keep-a-Changelog bullets and prepend them under `## [Unreleased]` in the repo's `CHANGELOG.md`, after the user confirms.

## Step 1 — Locate the git root and CHANGELOG.md

```bash
git rev-parse --show-toplevel 2>/dev/null
```

If this fails → report "Not in a git repository." and stop.

Look for `CHANGELOG.md` at the git root (case-insensitive: `CHANGELOG.md`, `Changelog.md`, `changelog.md` all count). If multiple exist, prefer the uppercase one.

If absent: ask the user "No CHANGELOG.md found at <repo-root>. Create one?". On yes, write the template in `assets/CHANGELOG-template.md` (see the assets folder of this skill) to `<repo-root>/CHANGELOG.md` and continue. On no, exit with "Skipped — no CHANGELOG.md created."

## Step 2 — Read the staged diff

```bash
git diff --cached --name-status      # the changed file list
git diff --cached --stat             # the stat summary
git diff --cached                    # the full patch
```

If `git diff --cached --name-status` is empty → tell the user "Nothing staged — run `git add` first, then re-run /changelog." and stop.

If the full patch is large (>2000 lines), truncate to the first 2000 lines for the subagent prompt and warn the user the summary may be lossy.

Identify and bucket the file list before summarizing:

- **Lockfiles**: `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `go.sum`, `Cargo.lock`, `poetry.lock`, `composer.lock`, `Gemfile.lock`, `*.lock`. Fold these into a single "deps" mention rather than describing them line by line.
- **Binary files**: anything `git diff --cached` reports as `Binary files … differ`. List the paths; do not try to describe contents.
- **Everything else**: pass through to the subagent for normal summarization.

## Step 3 — Generate bullets via a cheap subagent

Identify the current AI provider powering this session and spawn the equivalent fast/cheap model:

| Provider | Model to spawn |
|---|---|
| Anthropic (Claude) | `haiku` |
| OpenAI | `gpt-4o-mini` |
| Google | `gemini-2.0-flash` |
| Other | smallest/fastest available model |

Spawn the subagent with a self-contained prompt that includes:

- The bucketed file list (with `deps` + binary files already collapsed)
- The (possibly truncated) diff
- The category rules below

```
You are a changelog writer. Convert the staged git diff below into Keep-a-Changelog bullets.

Categories (use only what applies; omit empty ones):
- Added       — new features, files, endpoints, capabilities
- Changed     — modifications to existing behavior
- Deprecated  — features still present but marked for removal
- Removed     — features/files/endpoints deleted
- Fixed       — bug fixes
- Security    — vulnerability patches, auth/permission tightening

Rules:
- Feature-level abstraction, NOT file-level. Group related file edits into one bullet.
- One bullet per logical change. If a single feature touches 5 files, that's still one bullet.
- Past tense, terse imperative ("Added X", "Fixed Y when Z").
- Don't restate filenames unless they're user-facing (CLI command names, config files users edit).
- Don't invent semantics — if a change is mechanical (rename, format, comment), say so honestly under Changed.
- Skip noise: whitespace-only diffs, generated files (other than lockfiles which get one "deps" line under Changed).
- Lockfile-only changes → single bullet: "Updated dependencies." under Changed.

Return only the markdown bullets grouped under category headings, like:

### Added
- Bullet one
- Bullet two

### Fixed
- Bullet three

No preamble, no explanation, no version heading.
```

## Step 4 — Show proposal and confirm

Print the bullets exactly as the subagent returned them, prefaced with the target path:

```
Proposed entry for <repo-root>/CHANGELOG.md  → ## [Unreleased]

### Added
- ...

### Fixed
- ...
```

Then ask: "Write this to CHANGELOG.md? (yes / no / edit)"

- **yes** → go to Step 5.
- **no** → exit with "Cancelled — CHANGELOG.md unchanged."
- **edit** → ask the user what to change, regenerate (you may edit inline rather than re-spawning the subagent if the change is small), show again, re-ask.

## Step 5 — Merge into [Unreleased]

Read the existing CHANGELOG.md. Find `## [Unreleased]` (case-sensitive — that's the Keep-a-Changelog convention).

If `## [Unreleased]` is absent:

- If a versioned section exists (`## [X.Y.Z]` or `## [X.Y.Z] - YYYY-MM-DD`), ask the user "No `## [Unreleased]` section. Insert one above `## [<topmost-version>]`?". On yes, insert and proceed. On no, exit "Cancelled — no insertion point."
- If no versioned section exists either, the file is malformed for our purposes. Tell the user "CHANGELOG.md has no `## [Unreleased]` or version section — please fix the file structure first." and exit.

Merge the proposed bullets into the existing `[Unreleased]` body:

- For each category in the proposal, find the matching `### <Category>` subsection under `[Unreleased]`. If present, append the new bullets at the end of that subsection (preserve existing bullets above). If absent, create the subsection in this canonical order: Added, Changed, Deprecated, Removed, Fixed, Security.
- Skip exact-duplicate bullet text — if the user already wrote "Added foo bar" and the proposal says the same, drop the duplicate.
- Preserve every other line of the file byte-for-byte (frontmatter, intro paragraphs, all dated version sections below).

Write the file. Report: `Updated CHANGELOG.md — N bullets added under [Unreleased].`

Do **not** stage the change. Do **not** commit. Do **not** bump the version. The user will run their own commit/release flow next (in some repos `./scripts/bump-version`).

## Notes

- This skill is the *capture* half of a release flow. The *promotion* half (rename `[Unreleased]` to a dated version, bump version constants, tag) belongs to a release script the repo owns. Stay out of its lane.
- If the repo has a `bump-version` or similar script and the user asks "release a new version" — tell them this skill only writes the entry and point at the release script.
- Don't widen scope to unstaged or committed changes. Staged is the contract: the user controls what gets summarized via `git add`.
