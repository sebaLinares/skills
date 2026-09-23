# drawio

Vendored from [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp) (Apache-2.0). Keep both files identical to upstream except for `local.patch`.

| Local | Upstream |
|---|---|
| `SKILL.md` | `plugins/claude-code/skills/drawio/SKILL.md` + `local.patch` |
| `references/xml-reference.md` | `shared/xml-reference.md` |

Last synced: `c094dff` (2026-09-22).

`local.patch` holds the only local changes: `/drawio` instead of the plugin name `/drawio:drawio` in the examples, and § XML reference reads the local copy instead of fetching the URL.

## Sync

```bash
cd ~/sebalinares-skills
SHA=$(gh api repos/jgraph/drawio-mcp/commits/main --jq .sha)
raw() { gh api "repos/jgraph/drawio-mcp/contents/$1?ref=$SHA" -H 'Accept: application/vnd.github.raw'; }
raw plugins/claude-code/skills/drawio/SKILL.md > drawio/SKILL.md
raw shared/xml-reference.md > drawio/references/xml-reference.md
git apply drawio/local.patch
```

If `git apply` fails, upstream changed the patched lines: redo the edits by hand, then regenerate `local.patch` from a diff against the pristine upstream file. Update "Last synced" above.
