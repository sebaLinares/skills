---
name: map-endpoint
description: >-
  Trace one HTTP endpoint's full call chain and produce a formatted entry for
  docs/architecture/call-chains/<module>.md. Use this skill when the user invokes
  /map-endpoint, asks to "map", "trace", or "document" an endpoint or controller
  method, or wants to generate or commit a call-chain-graph entry. Two modes:
  generate (default, parallelizable, no file writes) and write (persist confirmed
  entries to graph files).
---

# map-endpoint

Two modes. Default is **generate**: read source files, trace the call chain, output the formatted graph entry to the conversation — no file writes. The other is **write**: take one or more confirmed graph entries and persist them.

Determine mode from context:
- User provides an endpoint or method name → generate
- User says "write", "commit", or "save this" after reviewing output → write
- User says "write mode" or "batch write" → write

---

## Mode 1: Generate

### Step 1 — Read the DI token map

Before tracing any code, read `docs/architecture/di-token-map.md`.

If this file does not exist, stop and tell the user:

> `docs/architecture/di-token-map.md` is missing. This file maps injection tokens to their concrete implementations and is required by this skill. Please create it before running `/map-endpoint`. See `docs/processes/call-chain-graphs.md` for the expected format.

### Step 2 — Identify the target

Parse the user's input for:
- HTTP method + path: `POST /products`, `GET /products/by-sku/:sku`
- Controller method name: `searchProducts`, `getProductBySku`

If ambiguous (e.g. only a method name that could belong to multiple modules), ask which module.

### Step 3 — Find the controller method

Search in `src/<module>/infrastructure/http-server/controllers/`. Match by `@Get/@Post/@Put/@Delete/@Patch` decorator value or method name.

Note from the controller:
- Which use-case methods are called (by `this.<useCaseName>.<method>()`)
- Which `@UseInterceptors()` decorators are applied — these become `[int]` nodes

### Step 4 — Trace layer by layer

Read each file before moving to the next layer. Don't rely on imports alone — read the actual method bodies.

Tracing is fully recursive. Every time you add a node — whether `[uc]`, `[fn]`, `[repo]`, or any other tag — read its body and apply the same tracing rules to it. There is no depth limit. Stop only at the two terminal conditions: external API calls (`◈`) and built-ins/SDK internals (see Step 5).

#### Use-case layer
File: `src/<module>/application/use-cases/`

For each use-case method called by the controller:
- Private/internal methods called within the same use-case → `[uc]` child nodes; recurse into each
- Service methods called → pass to next layer

#### Service layer
File: `src/<module>/domain/services/`

For each service method:
- Standalone helper function calls (not class methods) → `[fn]` nodes; recurse into each
- Repository method calls (injected via DI token) → look up the concrete class in `docs/architecture/di-token-map.md`, then trace that class

#### Repository layer
File: concrete class from the DI token map, in `src/<module>/infrastructure/adapters/repositories/`

For each repository method:
- Private builder/helper methods called within → `[fn]` nodes; recurse into each
- Other injected class methods called (e.g. another repository injected in the constructor) → `[repo]` nodes; recurse into each
- SDK chain calls (`.withId().get().execute()`, `.send()`, HTTP requests) → stop here, emit `◈` leaf

External API leaf nodes (no class name, no tag):
```
- ◈ CommerceTools API
- ◈ Cencosud Search API (GraphQL)
- ◈ Syte API
- ◈ GIV Logistics API
```

#### Interceptor layer
For each interceptor in `@UseInterceptors()`, read its file in `src/<module>/infrastructure/http-server/interceptors/`. Find which builder/DTO functions it calls in its `map()` body → `[fn]` children.

Represent interceptors as a sibling branch at controller depth, placed after the use-case subtree.

### Step 5 — What to include / exclude

**Include**: All named class methods at every layer, private helpers and builder functions within repositories, entity transformer functions, response interceptors and their builder calls.

**Include conditional branches**: All code paths reachable in any execution — `if/else`, `try/catch`, optional chaining that leads to a function call, conditional method dispatch. The graph is a complete map of all possible paths, not a trace of a single execution. If a branch calls a function only sometimes (e.g. only for bundle products, only when a flag is set), include it. The reader needs to know it exists.

**Exclude**: Third-party SDK chain internals (`.withId().get().execute()`), `Array.map`, `Object.keys` and other JS built-ins, NestJS framework internals (pipes, guards, validation decorators), trivial one-liner getters or assignments.

Cross-module delegation: if a service delegates to another module, write:
```
- LogisticService.getServiceabilityInfo [svc] → see logistic.md
```

### Step 6 — Format and output

Node syntax (one node per line):
```
- ClassName.method [tag] src/relative/path/to/file.ts
```

- Two spaces of indentation per level
- Standalone functions (not class methods): just the function name, no class prefix, still `[fn]`
- Section header: `### METHOD /path — handlerMethodName`
- External API leaves have no tag, just `◈`

Layer tags:
| Tag | Layer |
|---|---|
| `[ctrl]` | HTTP controller |
| `[uc]` | Use-case |
| `[svc]` | Domain service |
| `[repo]` | Concrete repository implementation |
| `[fn]` | Standalone helper or builder function |
| `[int]` | Response interceptor |

Print the complete formatted graph entry to the conversation. End with:

> Write this to `docs/architecture/call-chains/<module>.md`?

---

## Mode 2: Write

Triggered when the user confirms one or more generated entries.

### For each entry:

1. **Target file**: `docs/architecture/call-chains/<module>.md`
2. **If the file doesn't exist**: create it with `# <Module> Module` as the heading
3. **If a `### METHOD /path` section already exists**: replace it with the new entry
4. **Otherwise**: append the section at the end of the file

### README update (only when a new module graph file is created)

Add a one-line entry to `docs/README.md` under the appropriate section. Follow the tagging convention already in that file (at least one domain tag and one type tag).

### Batch write

If the user confirmed multiple entries (e.g. from parallel generate runs), write all of them before reporting done. Group writes by file to minimize read/write cycles.
