---
name: codebase-explainer
description: >-
  Turns a code change, investigation, or architecture into a polished,
  self-contained HTML explainer, grounded in real paths, diffs, and names —
  never generic filler. Use when the user asks to visually explain a
  refactor, migration, or change; wants an HTML walkthrough of what moved
  where; asks to document or visualize a codebase's architecture; wants a
  write-up of an investigation's findings; or says things like "make this a
  visual doc", "create an html explaining...", "show me what changed
  visually". Publishes via the Artifact tool.
---

# codebase-explainer

Every claim in the output needs a **receipt** — an exact path, a real function or type name, an actual diff hunk, a real command's output. A box, a table row, or a note with no receipt behind it doesn't ship. That's what separates this from a generic pretty page: the content is the codebase's own facts, arranged for reading.

## Step 1 — Gather receipts

Pull the concrete material before any design decision: real file paths (`old/path.go` → `new/path.go`), real function/type names, an actual `git diff` / `git log` excerpt, quotes from the relevant ADR, plan, or conversation that explain *why*, and — if the work was verified — the actual commands run and their pass/fail output.

Completion criterion: every section planned for Step 4 has at least one receipt behind it. A section that would ship on vibes ("cleaner architecture", "better separation of concerns") with no specific fact to point at gets cut or gets a fact dug up for it first.

## Step 2 — Pick the subject's shape

Three shapes, not mutually exclusive — a refactor is usually shape A carrying shape C's evidence:

| Shape | What it is | Devices from Step 4 it needs |
|---|---|---|
| **Change** | Something moved, was renamed, or was rewritten | Before/after diagram, directory trees, manifest table |
| **Investigation** | A root-cause / findings write-up, nothing shipped yet | Finding cards, evidence quotes, a timeline only if events are genuinely sequential |
| **Architecture** | Documenting current state, nothing changed | Current-state diagram, module reference table |

A verify/evidence panel applies to any shape that has a real pass/fail check to show — skip it if nothing was actually run.

## Step 3 — Design plan

Load the `artifact-design` skill for the palette/type/layout process; don't re-derive it here. This is almost always the **document** treatment in that skill's calibration, not a landing page — polished hierarchy, no oversized hero.

One addition specific to this domain: when the subject has a real semantic axis — old vs new, removed vs added, before vs after, pass vs fail — encode it as the accent pair instead of picking colors decoratively. The axis is the palette's justification, not a mood board.

If the explainer needs charts or metrics, not just structural boxes, load `dataviz` too for color/form rules.

## Step 4 — Assemble with these devices

Use only the devices Step 2's shape calls for, each backed by a Step 1 receipt:

- **Title block** — a compact header stamp (subject, status, scope, one or two key numbers) that orients the reader before they scroll, the way a drawing's title block does.
- **Before/after diagram** — hand-authored inline SVG boxes and arrows, not a generic flowchart-library render; label every box with the real package/module name.
- **Directory trees** — monospace, real paths, colour only the lines that were added/removed/shared, not every line.
- **Manifest table** — old → new mapping for the moves that carry a decision, not an exhaustive dump of every touched file.
- **Finding / decision notes** — one card per non-obvious call: the fact, the alternative considered, why this one won. Number them only if they're a genuine sequence the reader must follow in order — not by default.
- **Verify panel** — the actual commands run and their actual pass/fail, not a checklist of intentions.

## Step 5 — Build and publish

One self-contained HTML file: inline CSS, inline SVG, no external requests, light/dark theme tokens per `artifact-design`. Write it to the scratchpad directory, then publish with the `Artifact` tool.

Completion criterion: the artifact renders, every device used in Step 4 still has its receipt visible in the copy (a path, a name, a number — not a paraphrase of one), and the published URL is in hand to give the user.
