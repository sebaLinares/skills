---
name: go-release
description: Set up automatic GitHub Releases for a Go project with GoReleaser + GitHub Actions — pushing a v* git tag builds binaries in CI and publishes a Release with archives + checksums. Use this skill when the user types /go-release, says "set up releases", "add automatic releases", "set up GoReleaser", "publish releases on tag", "ship binaries on tag", or "release this Go CLI/TUI/tool". Generates .goreleaser.yaml and a release.yml workflow, then verifies the two gotchas that break first-time setups: GoReleaser global before.hooks run WITHOUT a shell (no cd, no &&), and the repo's default Actions workflow permission must be Read-and-write or publishing dies with a 401. Does NOT push the git tag for you — it prepares the config and surfaces/verifies the repo setting; you cut the actual release.
---

# go-release

Set up **automatic GitHub Releases** for a Go project. End state: pushing a `v*`
git tag triggers GitHub Actions, which runs GoReleaser to build binaries and
publish a GitHub Release with `.tar.gz` archives + `checksums.txt`.

This skill **prepares config and verifies the two gotchas**. It does **not** push
the tag — you cut the release once setup is verified (scope: config + verify).

Reference implementation: `token-lens` (verified live, release v1.0.0).

---

## What this assumes

- A Go project with an entry point at `./cmd/<name>` (the `go-tui` layout).
- A GitHub remote (`origin`).
- `gh` CLI available and authenticated (for the Gotcha 2 check).

If the project embeds a frontend or other build artifact, see the **before-hook**
notes in Step 2 — that path is where Gotcha 1 bites.

---

## Step 1 — Gather context

```bash
git rev-parse --show-toplevel                      # repo root
git remote get-url origin                          # parse owner/repo
ls cmd/                                             # find the cmd/<name> entry point
```

Determine and hold:
- `BINARY` = the directory name under `cmd/` (also the binary + project name).
- `OWNER/REPO` from the origin URL.
- Whether there is a **build step before `go build`** (embedded frontend, codegen,
  `go generate`). Most TUIs have none — skip the before-hook entirely if so.

**Harness awareness:** if the repo has a harness (`docs/PLANS.md`, `AGENTS.md`
declaring an ExecPlan gate), adding `.goreleaser.yaml` + the workflow is an in-repo
change and may need an approved ExecPlan first. Check before writing files.

---

## Step 2 — Write `.goreleaser.yaml` (repo root)

GoReleaser v2. Substitute `<BINARY>`. Default matrix is **darwin amd64+arm64**
(what token-lens verified). Uncomment `linux`/`windows` if the tool runs there.

```yaml
# GoReleaser v2 — https://goreleaser.com
version: 2
project_name: <BINARY>

before:
  hooks:
    - go mod tidy
    # ─── OPTIONAL: pre-build step (embedded frontend, codegen) ───────────────
    # GOTCHA 1 — global before.hooks run WITHOUT a shell. Each entry is
    # shellword-split and the first word is exec'd directly. There is NO `cd`
    # binary and `&&` is meaningless, so `cd web && npm ci` FAILS in CI with:
    #   exec: "cd": executable file not found in $PATH
    # The { cmd:, dir: } object form is ALSO invalid for GLOBAL before.hooks
    # (only valid under per-build builds[].hooks). Fixes, pick one:
    #   - use a tool-native directory flag (preferred):
    #       - npm --prefix web ci
    #       - npm --prefix web run build
    #     (also: `make -C dir`, `go -C dir build`)
    #   - or wrap explicitly in a shell:
    #       - sh -c "cd web && npm ci && npm run build"
    # NEVER emit a bare `cd x && ...` hook string.
    # ─────────────────────────────────────────────────────────────────────────

builds:
  - id: <BINARY>
    main: ./cmd/<BINARY>
    binary: <BINARY>
    env:
      - CGO_ENABLED=0           # static binary; pure-Go deps cross-compile from Linux
    goos:
      - darwin
      # - linux
      # - windows
    goarch:
      - amd64
      - arm64
    ldflags:
      - -s -w -X main.version={{ .Version }}

archives:
  - id: <BINARY>
    formats: [tar.gz]          # v2 field (singular `format` is deprecated)
    name_template: "{{ .ProjectName }}_{{ .Os }}_{{ .Arch }}"

checksum:
  name_template: checksums.txt
```

> `CGO_ENABLED=0` is what lets a Linux CI runner cross-compile darwin binaries.
> If the project needs cgo (a C dependency), this matrix won't cross-compile and
> you need per-OS runners — out of scope here; flag it to the user.

---

## Step 3 — Write `.github/workflows/release.yml`

```yaml
name: release

on:
  push:
    tags: ['v*']

permissions:
  contents: write             # required — but NOT sufficient (see Gotcha 2)

jobs:
  goreleaser:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0       # GoReleaser needs full history + tags
      - uses: actions/setup-go@v5
        with:
          go-version: stable
      # ─── OPTIONAL: only if .goreleaser.yaml has a frontend before-hook ───
      # - uses: actions/setup-node@v4
      #   with:
      #     node-version: lts/*
      # ─────────────────────────────────────────────────────────────────────
      - uses: goreleaser/goreleaser-action@v6
        with:
          version: '~> v2'     # latest GoReleaser v2; pin exact (e.g. v2.16.0) if you want reproducible CI
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Step 4 — Verify Gotcha 2 (the most-overlooked step)

Even with `permissions: contents: write` in the workflow, the **repo-level
default** Actions permission can be read-only, which blocks release creation:

```
scm releases: ... POST /repos/.../releases: 401 Requires authentication
```

Check it:

```bash
gh api repos/<OWNER>/<REPO>/actions/permissions/workflow --jq .default_workflow_permissions
```

- `write` → good, nothing to do.
- `read` → must be fixed or the first release fails at the publish step.

**Fix — requires repo admin. Only with the user's explicit consent.** Either:

- UI: Settings → Actions → General → **Workflow permissions → "Read and write
  permissions"**. Leave "Allow GitHub Actions to create and approve pull requests"
  **unchecked** — releases don't need it.
- API:
  ```bash
  gh api repos/<OWNER>/<REPO>/actions/permissions/workflow -X PUT -f default_workflow_permissions=write
  ```

Do **not** bundle the PR-approval grant. **Detect + instruct by default; only flip
it with consent.** If a permission classifier denies the automated PUT, hand the
command to the user to run themselves.

---

## Step 5 — Hand off the release (you do NOT run this)

Tell the user how to cut the first release:

```bash
git tag v1.0.0
git push origin v1.0.0
gh run watch          # or watch the Actions tab
```

Then verify: the Release page shows the archives + `checksums.txt`, and the run
is green. If the run failed only on the publish step due to Gotcha 2, no re-tag
is needed — fix the setting and `gh run rerun <run-id>`.

**Versioning rule:** never reuse a version that has already published a Release.
(Reusing an unpublished/broken tag by deleting + re-pointing it is fine.)

---

## The two gotchas (the whole reason this skill exists)

1. **Shell-less `before.hooks`.** Global GoReleaser `before.hooks` are exec'd
   directly, no shell. `cd x && ...` and the `{ cmd:, dir: }` object form both
   fail. Use tool-native dir flags (`npm --prefix`, `make -C`, `go -C`) or
   `sh -c "..."`.
2. **Read-only Actions token → 401 on publish.** A workflow `permissions:` block
   is not enough; the repo's default Workflow permission must be Read-and-write.
   This is a repo setting, not code. Always verify it.

---

## Out of scope (documented, not built)

- **Homebrew tap, Linux/Windows packages (`nfpms`), Docker images.** GoReleaser
  supports all of these; add them when a project actually needs them.
- **Signing / notarization** of macOS binaries.
- **Driving the tag/verify end-to-end** — this skill stops at config + the repo
  setting; the user cuts the release.
