---
name: create-view
description: Create a named view YAML file in docs/views/ that defines a subgraph selection from one or more call chain graphs. Use this skill when the user invokes /create-view, asks to "create a view", "add a view", or "define a view" over a call chain graph, or describes a focused slice of an endpoint they want to diagram or visualize (e.g. "show me just the service layer", "diagram the enrichment flow", "I want a view of the SKU hydration path").
---

# create-view

Creates `docs/views/<name>.yaml` and updates `docs/README.md`.

## Usage

```
/create-view name=<kebab-case> root=<ClassName.method> graph=<module>[,<module>] depth=<number|full> [exclude=<ClassName.method>[,<ClassName.method>]] [description=<string>]
```

Examples:
```
/create-view name=search-overview root=SearchProductsUseCase.searchProducts graph=products depth=1
/create-view name=sku-hydration root=ProductsService.getProductsBySKUList graph=products depth=full exclude=CommercetoolsProductsRepository.getProductsBySKUList description="SKU hydration via CommerceTools"
/create-view name=cross-module-detail root=ProductsController.getProductById graph=products,logistic depth=3
```

---

## Step 1 — Parse inputs

Required:
- `name` — kebab-case identifier, becomes the filename
- `root` — `ClassName.method` node where the subgraph begins
- `graph` — one or more module names (e.g. `products`, `logistic`); comma-separated if multiple
- `depth` — integer or `"full"`

Optional:
- `exclude` — comma-separated list of `ClassName.method` nodes to prune (along with their entire subtrees)
- `description` — one-line purpose statement; if omitted, derive one from the root node name and depth (e.g. `root=ProductsService.getProductsBySKUList depth=full` → `"Full call chain for ProductsService.getProductsBySKUList"`)

If any required input is missing, ask for it before proceeding.

---

## Step 2 — Resolve graph files

Map each module name to its graph file path:
```
<module> → docs/architecture/call-chains/<module>.md
```

For each resolved path, verify the file exists. If any is missing, stop and tell the user:

> `docs/architecture/call-chains/<module>.md` does not exist. Run `/map-endpoint` for that module first, or correct the module name.

---

## Step 3 — Validate root and exclude nodes

Read all resolved graph files. Node lines take two forms:

```
- ClassName.method [tag] src/relative/path.ts
- ClassName.method [tag] → see <module>.md
```

Both are valid node identifiers. When scanning for a node, match the `ClassName.method` prefix regardless of what follows.

**Root node:** search for `root` across all graph files.
- Found → proceed.
- Not found → list all available `ClassName.method` identifiers from those files, grouped by graph file, and ask the user to correct the root before proceeding.

**Exclude nodes:** for each entry in `exclude`, search the same way.
- Not found → warn the user: `"<node>" not found in the listed graph files — possible typo. Proceed anyway?`
- Don't block on this; let the user confirm or correct.

---

## Step 4 — Build the YAML

```yaml
name: <name>
description: <description>
graph:
  - docs/architecture/call-chains/<module>.md
root: <ClassName.method>
depth: <depth>
exclude:
  - <ClassName.method>
```

Omit the `exclude` key entirely if no exclusions were specified.

---

## Step 5 — Write the file

Target path: `docs/views/<name>.yaml`

Create `docs/views/` if it does not exist.

If the file already exists, ask the user whether to overwrite before writing.

---

## Step 6 — Update docs/README.md

Read `docs/README.md` first to find the section where view files are listed. Add a one-line entry there. Follow the tagging convention already in that file (at least one domain tag and one type tag). Use the view's `description` as the entry text.

---

## Step 7 — Confirm

After writing, output a brief summary:

```
Created docs/views/<name>.yaml
  root:  <ClassName.method>
  graph: <module(s)>
  depth: <depth>
  exclude: <nodes, or "none">
```

If this view is likely to be rendered as a diagram, suggest running `/drawio` next.
