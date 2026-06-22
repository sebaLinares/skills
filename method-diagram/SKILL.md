---
name: method-diagram
description: >-
  Use when the user invokes /method-diagram, asks to "diagram", "draw a
  flowchart for", or "document" a method or set of methods in the codebase,
  provides a view YAML path (e.g. docs/views/*.yaml), or references a
  ClassName.method. Generates a native draw.io flowchart showing internal logic
  and control flow. Two modes - view-driven: reads a view YAML to scope which
  methods to include and produces an inline-expansion swimlane flowchart;
  method-driven: reads one method directly from source and produces a
  single-method flowchart. Output is a .drawio file saved to docs/architecture/.
---

# method-diagram

Generates draw.io flowcharts documenting method logic. The user provides a view YAML or a method name — the skill handles reading source, parsing call chains, and producing the diagram.

## Step 1 — Detect mode

**Mode 1 (view-driven):** input contains a `.yaml` or `.yml` path (e.g. `docs/views/main-attributes-creation.yaml`)

**Mode 2 (method-driven):** input contains a `ClassName.method` reference or a method name and optionally a file path

---

## Step 2A — Mode 1: resolve the method set

1. Read the view YAML. Extract: `name`, `graph` (list of call-chain files), `root` (`ClassName.method`), `depth` (integer or `"full"`), `exclude` (list of `ClassName.method` strings).

2. Read each file listed in `graph`. Call-chain format:
   ```
   - ClassName.method [tag] src/relative/path.ts
     - ClassName.method [tag] src/relative/path.ts
       - ClassName.method [tag] src/relative/path.ts
       - ◈ ExternalServiceName
   ```
   Each level of indentation (2 spaces per level) represents a call dependency.

3. Traverse the tree from `root`:
   - Find the line whose `ClassName.method` matches `root`
   - Its indentation level is the baseline (level 0)
   - Collect all subsequent lines more indented than the root line
   - Stop collecting when a line with indentation ≤ root's level is reached (sibling or ancestor)
   - If `depth` is an integer N, only collect descendants up to N indentation levels below root
   - **Excluded nodes:** if a line's `ClassName.method` is in the `exclude` list, skip that line **and its entire subtree**
   - Lines starting with `◈` are external boundaries — keep as opaque boxes (no source file to read)

4. The result is an ordered list of included nodes. Each has: `ClassName.method`, `[tag]`, `src/path.ts` (or `◈ Name`).

5. For each non-`◈` node, read its source file and extract the method body.

6. For each method, follow **1 level** of direct type imports to understand input/output shapes — read the imported interface/type file, do not recurse further.

---

## Step 2B — Mode 2: resolve the method

1. If a file path is given, read it. Otherwise, grep the codebase for the method name and locate the file.
2. Read the file, extract the target method body.
3. Follow 1 level of direct type imports to understand input/output shapes.

---

## Step 3 — Generate IR JSON and run the generator

Instead of producing draw.io XML directly, produce a compact JSON IR and let the generator script handle all XML, layout, and styling.

### IR JSON schema

```json
{
  "title": "view-name",
  "swimlanes": [
    {
      "id": "sw1",
      "label": "ClassName.method [tag]",
      "nodes": [
        { "id": "start", "type": "start", "label": "START", "col": 0, "row": 0 },
        { "id": "step1", "type": "process", "label": "Do something", "col": 0, "row": 1, "color": "blue" },
        { "id": "dec1", "type": "decision", "label": "condition?", "col": 0, "row": 2 },
        { "id": "yes_path", "type": "process", "label": "Yes result", "col": 1, "row": 2, "color": "green" },
        { "id": "no_path", "type": "process", "label": "No result", "col": 0, "row": 3, "color": "orange" },
        { "id": "end", "type": "end", "label": "END", "col": 0, "row": 4 }
      ],
      "edges": [
        { "from": "start", "to": "step1" },
        { "from": "step1", "to": "dec1" },
        { "from": "dec1", "to": "yes_path", "label": "Yes", "direction": "right" },
        { "from": "dec1", "to": "no_path", "label": "No" },
        { "from": "yes_path", "to": "end", "merge": "right" },
        { "from": "no_path", "to": "end" }
      ]
    }
  ],
  "crossEdges": [
    { "from": { "swimlane": "sw1", "node": "step1" }, "to": { "swimlane": "sw2", "node": "start" }, "label": "calls" },
    { "from": { "swimlane": "sw2", "node": "end" }, "to": { "swimlane": "sw1", "node": "step2" }, "label": "returns", "returnEdge": true }
  ],
  "notes": [
    { "id": "note1", "text": "Warning text", "attachTo": { "swimlane": "sw1", "node": "step1" }, "position": "left" }
  ]
}
```

### Field reference

**Node:** `{ id, type, label, col, row, color?, height? }`
- `type`: `start` | `end` | `process` | `decision` | `opaque` | `note`
- `col`: `0` = main column, `1` = right branch, `-1` = left branch
- `row`: 0-based integer, sequential within swimlane
- `color` (optional): `green` | `blue` | `orange` | `red` | `yellow`
  - `green` = START/END/positive, `blue` = process/loop, `orange` = edge case/null, `red` = mutation/side-effect, `yellow` = warning
  - start/end default to green; others default to no fill
- Use `\n` for line breaks in labels

**Edge:** `{ from, to, label?, direction?, merge? }`
- `direction`: `"right"` for decision Yes branches going to col 1; `"left"` for going to col -1; omit for downward flow
- `merge`: `"right"` routes the edge back from col 1 to col 0 via a right-side trunk; `"left"` via left-side trunk

**CrossEdge:** `{ from: {swimlane, node}, to: {swimlane, node}, label?, returnEdge? }`
- `returnEdge: true` routes the edge upward along the left perimeter (for return-from-child-swimlane edges)

**Note:** `{ id, text, attachTo: {swimlane?, node}, position? }` — position defaults to `"left"`

**Single-method mode:** Omit `swimlanes`, use top-level `nodes` and `edges` instead.

### Swimlane layout rules

- **Mode 1 (view-driven):** Each included method gets its own swimlane. Order: document order from the call-chain file (depth-first traversal).
- Inside each swimlane, model the full control flow. At call sites:
  - **Included method** → add a cross-swimlane edge to the child's START, and a `returnEdge` cross-edge from child's END back to the next step in the parent
  - **Excluded method** → opaque node (`type: "opaque"`) inside the current swimlane
  - **`◈` external boundary** → opaque node labeled `◈ ExternalName`

### Execution

1. Write the IR JSON to `/tmp/<title>.diagram.json`
2. Run: `node ~/.claude/skills/method-diagram/tools/generate-drawio.mjs /tmp/<title>.diagram.json <output-path>.drawio`
3. Delete the temp file: `rm /tmp/<title>.diagram.json`

Output path:

| Mode | Output path |
|---|---|
| Mode 1 (view) | `docs/architecture/<view-name>.drawio` |
| Mode 2 (method) | `docs/architecture/<kebab-case-method-name>.drawio` |

4. Open on macOS: `open <output-path>`

If the `open` command fails or the draw.io app is not found, print the absolute file path so the user can open it manually.
