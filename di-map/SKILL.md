---
name: di-map
description: Scan the repository for all NestJS dependency injection tokens, map each one to its interface and concrete implementation class, and write the result to `docs/architecture/di-token-map.md`. Use this skill when the user invokes /di-map, asks to "map DI tokens", "resolve injection tokens", "update the DI map", "show what's injected", or wants to regenerate or refresh the token map. Always use this skill before running /map-endpoint in a repo where di-token-map.md is missing or stale.
---

# di-map

Produce or refresh `docs/architecture/di-token-map.md` — a table mapping every DI injection token to its interface and concrete implementation.

---

## Step 1 — Collect all module files with DI providers

Glob for every `*.module.ts` in the repo:
```
src/**/*.module.ts
```

Read each file. For each file extract every `{ provide: <TOKEN>, useClass: <ConcreteClass> }` block (also catch `useFactory` and `useValue` patterns). Record:
- `token` — the constant name or string literal (e.g. `PRODUCTS_REPOSITORY`)
- `concreteClass` — the class (or `dynamic` for useFactory/useValue)
- `wiredIn` — the path of this module file (repo-relative)

Also check `src/app.module.ts` explicitly if it exists — it often registers framework-level providers (`APP_FILTER`, etc.).

## Step 2 — Locate token definitions

For each token found in Step 1, determine where it is defined:

**Check the adapters.module.ts itself first.** If it contains `export const <TOKEN> = '...'`, the token is defined inline there.

**Otherwise**, search across port files:
```
src/*/domain/ports/*.ts
```
Look for `export const <TOKEN>` in those files. The file that exports it is where the token is defined.

Record:
- `definedIn` — path of the file where `export const TOKEN` appears
- `interface` — the TypeScript interface exported from the same file (the one the concrete class implements); use the filename to infer it if needed (e.g. `products.repository.ts` → `ProductsRepository`)

## Step 3 — Collect CACHE_MANAGER usages

Search for `@Inject(CACHE_MANAGER)` across `src/`. List the files that use it — these go in the "Built-in tokens" section.

## Step 4 — Detect cross-module injection

Look for cases where a concrete repository class (found in Step 1) itself injects another token via `@Inject(TOKEN)` in its constructor. These are secondary injections — record `ConcreteClass injects TOKEN → receives ConcreteClass`.

## Step 5 — Write the document

Create or overwrite `docs/architecture/di-token-map.md` using exactly this structure:

```markdown
# DI Token Map

Maps every custom injection token to its interface and concrete implementation.

## Custom tokens

| Token | Defined in | Interface | Concrete class | Wired in |
|-------|-----------|-----------|---------------|---------|
| `TOKEN_NAME` | `src/path/to/definition.ts` | `InterfaceName` | `ConcreteClassName` | `src/path/to/adapters.module.ts` |
...

## Built-in tokens

| Token | Source | Concrete | Registered via |
|-------|--------|---------|---------------|
| `CACHE_MANAGER` | `@nestjs/cache-manager` | NestJS cache manager | `CacheModule.register()` |

Used in: `ClassA`, `ClassB`, `ClassC`.

## Cross-module injection

`ConcreteClassA` injects `TOKEN_X` and receives `ConcreteClassB` at runtime.
```

Omit any section that has no entries (e.g. omit "Cross-module injection" if there are none).

## Step 6 — Update docs/README.md

Check whether `docs/README.md` already has a link pointing to `architecture/di-token-map.md`.

- **If it does**: leave it unchanged.
- **If it doesn't**: add a one-line entry under the `## Architecture` section following the existing format:

```
- [DI Token Map](architecture/di-token-map.md) — All injection tokens mapped to their interface and concrete implementation `#<relevant domain tags>` `#diagram`
```

Use all domain tags that apply based on the modules present in the map.
