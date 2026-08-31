---
name: wrap
description: Cierra o pausa una sesión de trabajo con un agente y deja una nota de sesión en el vault de Obsidian que corresponde, con metadata automática. Usa esta skill cuando el usuario escriba /wrap, diga "cierra la sesión", "guarda el contexto", "me tengo que ir", "dejemos esto acá", "esto queda a medias", "handoff", "pasale esto a Codex", "pasale esto a Claude", o cuando una sesión con trabajo en vuelo se interrumpe y hay contexto que se perdería. También con `--close` cuando el trabajo terminó y hay que promover la nota a fuente ingerible. NO la uses para un resumen suelto sin destino durable — para eso está /handoff.
---

# wrap

Deja el estado de una sesión de trabajo como una nota Markdown en el vault de
Obsidian correcto, con frontmatter automático, para que otro agente (o vos en
tres semanas) retome sin re-derivar nada.

**El usuario no escribe metadata.** Todos los campos se derivan.

## Qué es y qué no es

- Una **nota de sesión** es estado operativo **vivo**. Vive en
  `workspace/sessions/`. Nunca en `sources/`, nunca sellada, nunca ingerida
  mientras esté abierta.
- Cuando el trabajo cierra, `--close` la promueve por el **paso 0** del contrato
  a `sources/handoffs/`, y recién ahí es ingerible.
- **La ubicación es el estado.** No hay campo `status`.
- Esta skill **nunca** dispara un `ingest`. El ingest es conversacional y lo
  pide el humano.

## Paso 1 — Resolver el vault (determinístico, nunca por criterio propio)

Obtené el path base:

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
```

Aplicá la **primera** regla que matchee. Es una tabla, no un juicio:

| Prefijo del path | Vault |
| --- | --- |
| `~/Notes/<vault>/…` | ese mismo vault |
| `~/Notes/_shared/…` | `slinaresl` (es maquinaria compartida, no contenido de ninguna vault) |
| `~/Documents/projects/cencosud-github/…` | `cencosud` |
| `~/Documents/projects/coelpro/…` | `electromatica` |
| `~/Documents/projects/dendrita-labs/local-websites/clientes/CL-004…` | `electromatica` |
| `~/Documents/projects/dendrita-labs/local-websites/clientes/CL-005…` | `electromatica` |
| `~/Documents/projects/dendrita-labs/…` (resto, incl. `CL-001/002/003`) | `slinaresl` |
| `~/Documents/projects/…` | `slinaresl` |
| `~/Documents/.dotfiles`, `~/.claude`, `~/.agents`, `~/.codex`, `~/sebalinares-skills` | `slinaresl` |
| cualquier otro | **PARÁ Y PREGUNTÁ** |

Reglas duras:

- **Sin default.** Si ninguna regla matchea, preguntá a cuál vault va. Nunca
  elijas. Los vaults tienen un muro de privacidad duro: `cencosud` es
  confidencial de empleador y `electromatica` no tiene ningún canal de egress.
  Un routing equivocado es una fuga entre dominios, no un archivo mal puesto.
- **`--vault <nombre>` del usuario siempre gana** sobre la tabla.
- `CL-004` (`coel-pro`) y `CL-005` (`electromatica`) **son** la empresa del
  suegro. Los demás `CL-*` son clientes de Dendrita → personal.

El vault raíz es `~/Notes/<vault>/`.

## Paso 2 — Reunir los hechos (sin preguntarle nada al usuario)

```bash
git rev-parse --show-toplevel 2>/dev/null      # repo (basename)
git branch --show-current 2>/dev/null          # branch
git status --short 2>/dev/null                 # worktree limpio o sucio
git log --oneline @{u}.. 2>/dev/null           # commits sin pushear
git log --oneline -5 2>/dev/null               # qué se hizo
```

```bash
git log --merges -3 --oneline 2>/dev/null   # ¿se mergeó algo durante la sesión?
```

**Si la rama cambió durante la sesión** (mergeaste, se cerró un PR, cambiaste de
rama), `branch:` guarda **dónde se retoma**, no dónde se trabajó — y entonces
`## Artefactos` **debe** registrar el PR o el merge commit que produjo el cambio.
Sin eso, un agente frío ve una rama limpia y no puede reconstruir qué pasó.

- `agent`: `claude` o `codex`, según quién esté corriendo.
- `project`: proponé un slug y **validalo** contra `~/Notes/<vault>/wiki/projects/`.
  Si no existe, dejalo vacío (`project: ""`) y decilo en el reporte. **Nunca
  inventes un proyecto** — misma regla que `sources/jira/`.
- `created` / `updated`: fecha de hoy, `YYYY-MM-DD`.

## Paso 3 — ¿Nota nueva o actualización?

Buscá una nota abierta del mismo repo:

```bash
ls ~/Notes/<vault>/workspace/sessions/ 2>/dev/null | grep -i "<repo>"
```

- **Existe una del mismo repo y branch** → **actualizala**. No crees una segunda.
  Pisá `updated:` y `agent:`, appendeá a `## Estado`, reescribí `## Falta`,
  `## Bloqueadores` y `## Siguiente acción`. Este es el camino Claude ↔ Codex.
- **No existe** → creala.

Nombre del archivo:

```
YYYY-MM-DD <repo> — <slug>.md
```

Ej: `2026-09-01 ms-search — pia-rate-limit.md`

- Prefijo de fecha, igual que `sources/meetings/`.
- **Slug sin tildes ni ñ.** macOS guarda los nombres en NFD y el contenido en
  NFC, así que un nombre acentuado no matchea en búsquedas por filename. Para
  buscar por nombre siempre: `_shared/scripts/vault-find.py <vault-root> <patrón>`.

Creá el directorio si no existe: `mkdir -p ~/Notes/<vault>/workspace/sessions`

## Paso 4 — Escribir la nota

Frontmatter exacto, siete campos, todos derivados:

```yaml
---
type: session
project: "ms-search"
repo: "be-paris-backend-cl-ms-search"
branch: "STR-3102-pia-rate-limit"
agent: claude
created: 2026-09-01
updated: 2026-09-01
---
```

No agregues campos. No hay `status`, `vault`, `resume`, `ingested` ni `source`:
la ubicación ya dice todo eso, y un campo duplicado se pone rancio.

Cuerpo — **estas ocho secciones, en este orden, siempre**. Una sección sin
contenido se deja con `—`, no se omite:

```markdown
## Objetivo
Qué se quería lograr. Una o dos líneas.

## Estado
Qué quedó hecho **y verificado**. Distinguí "escrito" de "probado".
Incluí: worktree limpio/sucio, commits sin pushear, tests en verde o rojo.

## Falta
Lo que sigue, en orden de ejecución.

## Bloqueadores
Qué está esperando qué, o a quién. Vacío si no hay.

## Siguiente acción
**Una línea, imperativa, con ruta y línea si aplica.** Es lo que se lee primero
al retomar.

## Decisiones
Qué se decidió, por qué, y **qué alternativas se descartaron**. Esta sección es
la que evita el fallo más caro: un agente frío re-propone lo que ya rechazaste.

## Preguntas abiertas
Lo que hay que resolver con un humano antes de seguir.

## Artefactos
Rutas, PRs, URLs, specs, ADRs, tickets. **Referencias, nunca copias.**
```

Al final del cuerpo, una línea de trazabilidad (no va en frontmatter):

```markdown
---
`session_id: <id>` · `<agente>` · <fecha>
```

Reglas de contenido:

- **No dupliques lo que ya vive en otro artefacto.** Si hay un spec, un ADR, un
  plan o un PR, referencialo por ruta o URL. El valor de esta nota es el
  razonamiento que no quedó escrito en ningún lado.
- **Redactá secretos.** Tokens, claves, credenciales, datos personales. Si un
  secreto se imprimió en la sesión, decí *que pasó* sin reproducirlo.
- **Ninguna nota de sesión sale de su vault**, cualquiera sea. `cencosud` es
  confidencial de empleador y `electromatica` no tiene canal de egress; y una
  nota de `slinaresl` puede traer datos de salud, de familia o de terceros. No
  van a un artifact publicado, a un pastebin, a un issue ni a ningún servicio
  externo — ni siquiera "para ilustrar el formato".
- **Datos de salud y de terceros**: si la nota los toca (peso, medicación,
  diagnóstico, un menor, alguien que no es el usuario), decilo en el reporte
  final para que quede consciente de qué guardó y dónde.
- **No cruces vaults.** Una nota puede nombrar la *maquinaria* de otra vault
  (que existe, cómo sincroniza), nunca su *contenido*. El muro es duro.
- Los pendientes de **conocimiento** (no de la sesión) van como `- [ ]` en la
  página del wiki que corresponde, no acá. Esta nota es ejecución, no wiki.

## Paso 5 — Commitear el vault

**Hacelo vos. No lo hace nadie más.** El hook `Stop` de los vaults resuelve el
repo desde el `cwd`, y `/wrap` casi siempre corre desde un repo de código, no
desde el vault — así que la nota queda untracked si no la commiteás acá.

**Solo el archivo de la nota.** Nunca `git add -A`: el vault suele tener
material del humano sin trackear (reuniones, capturas) que no es tuyo y que no
va en este commit.

```bash
git -C ~/Notes/<vault> add "workspace/sessions/<archivo>"
git -C ~/Notes/<vault> commit -q -m "docs(session): <repo> — <slug>"
```

Mensaje según el caso:

- nota nueva → `docs(session): <repo> — <slug>`
- actualización → `docs(session): actualiza <repo> — <slug>`
- `--close` → `docs(session): promueve <repo> — <slug> a sources/handoffs/`

Si el commit falla, **no lo escondas**: reportá que el archivo quedó escrito
pero sin commitear, y seguí. El archivo en disco es lo que importa; el commit
es durabilidad, no corrección.

## Paso 6 — Reportar

Imprimí la ruta absoluta del archivo, el vault elegido y **por qué regla**, si
`project` quedó vacío, y si el commit salió.

## Modo `--close`

Cuando el trabajo terminó y la nota tiene conocimiento durable:

1. **Confirmá con el humano en una palabra.** El paso 0 del contrato dice que
   *ingestible ⟺ congelable*: promover significa que la nota deja de editarse.
   "Todavía no" es una respuesta válida y termina acá.
2. Actualizá la nota por última vez (`updated:`, `## Estado` final).
3. Promové con `git mv`, renombrando:
   ```bash
   mkdir -p ~/Notes/<vault>/sources/handoffs
   git -C ~/Notes/<vault> mv \
     "workspace/sessions/YYYY-MM-DD <repo> — <slug>.md" \
     "sources/handoffs/YYYY-MM-DD Handoff <repo> — <slug>.md"
   ```
4. Commiteá el movimiento (`docs(session): promueve <repo> — <slug> a
   sources/handoffs/`).
5. **Pará ahí.** No ingieras, no sellés, no toques el wiki ni `system/log.md`.
   Decile al humano que la fuente quedó lista y que el siguiente paso es
   `ingest @"<nombre>"` cuando quiera.

Si el trabajo no dejó nada durable, la respuesta correcta es **borrar la nota**,
no promoverla. Proponelo.

## Errores a no cometer

- Escribir en `sources/` fuera de `--close`. `sources/` es inmutable y su único
  cambio permitido es el sello, que lo pone el ingest.
- Escribir en `inbox/`. Es zona de tránsito que se vacía en la misma sesión;
  usarla como buzón la convierte en la pila que el contrato prohíbe.
- Agregar una línea a `system/log.md`. Ese log es para ops del vault
  (`ingest|query|lint|migrate`), se lee entero para saber qué falta ingerir, y
  ya está rotando por tamaño. Una sesión no es una op del vault.
- Crear una segunda nota para un repo que ya tiene una abierta.
- Elegir vault por criterio propio cuando la tabla no matchea.
- Disparar un `ingest` automático.
- `git add -A` en el vault. Barre material del humano que no es tuyo.
- Dar por hecho que algo commitea la nota por vos.
