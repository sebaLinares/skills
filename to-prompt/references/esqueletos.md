# Esqueletos

Tres, uno por destino. **No son formularios.** Una sección sin contenido con
procedencia se borra — no se deja vacía ni se rellena.

---

## `agente-repo`

Destino: Claude Code, Codex u otro agente **con acceso al repositorio**.

Lo que lo distingue: el agente puede ir a buscar. Entonces no le pegues el
contexto — **apuntale dónde está** y decile qué comprobar. Y no le repitas nada
de `CLAUDE.md` / `AGENTS.md`: ya lo cargó.

```markdown
# <objetivo, una línea, en imperativo>

## Hechos ya comprobados

<lo que el preflight resolvió, con el comando que lo produjo entre paréntesis.
Esto le ahorra al destino la mitad de su exploración.>

- `~/Notes/` contiene 4 directorios: … (`ls -d ~/Notes/*`) — verificado

## Cómo funciona hoy

<flujo, con flechas. Una línea por paso.>

A
→ B
→ C

## Qué está fallando

<problemas, separados de las soluciones propuestas. Uno por bloque.>

## Hipótesis mías

- …— hipótesis

Esto es hipótesis mía, no requisito. No asumas que es correcta.

## Antes de proponer nada, inspeccioná

1. …
2. …

No modifiques ningún archivo en esta fase.

## Qué tenés que decidir

<verbos duros: definí, elegí, compará, justificá. Nunca "pensá en" ni "explorá".>

1. …
2. …

## Cómo resolver los tradeoffs

<orden de prioridad explícito cuando exista>

extender lo que ya existe > componente local chico > app nueva > servicio

## No hagas

- …

## Entregable

<estructura que espeja el razonamiento pedido, no headings decorativos>

## Terminaste cuando

<criterio comprobable. Si no se puede verificar, no es criterio.>
```

---

## `chat`

Destino: modelo de chat **sin herramientas** (ChatGPT, Claude en la web).

Lo que lo distingue: **no puede ir a buscar nada**. Todo lo que necesite va
inline, y las rutas absolutas son ruido salvo que también sean el tema.
Sin fase de inspección — no tiene con qué.

```markdown
# Rol

<el rol solo si cambia la respuesta. Si no, borralo.>

# Contexto

<todo inline. Lo que en `agente-repo` sería un puntero, acá es el contenido.>

# Cómo funciona hoy

A
→ B
→ C

# Qué está fallando

# Hipótesis mías

- …— hipótesis

Esto es hipótesis mía, no requisito. No asumas que es correcta.

# Qué quiero que resuelvas

1. …

# Cómo resolver los tradeoffs

# Restricciones

- No …

# Entregable

<qué forma tiene la respuesta>

# No termines con una lista de opciones equivalentes

Elegí una y explicá por qué.
```

---

## `issue`

Destino: cuerpo de un issue (`/to-tickets`, `vikunja`, GitHub).

Lo que lo distingue: lo lee un humano *y* un agente, semanas después, sin el
contexto de hoy. **Nada de proceso** — el proceso lo pone el que lo tome.

```markdown
## Problema

<desde la perspectiva de quien lo sufre, no de la solución>

## Criterios de aceptación

- [ ] <comprobable, uno por línea>

## Contexto verificado

- … — verificado

## Bloqueado por

- <ticket o condición>

## Fuera de alcance

- …
```
