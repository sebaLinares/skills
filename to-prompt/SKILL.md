---
name: to-prompt
description: Convierte un pedido crudo, narrativo o mal estructurado en un prompt preciso para otro agente o sesión. Comprueba contra el repo antes de escribir, marca la procedencia de cada línea (verificado / dicho / hipótesis / asumido) y nunca inventa contexto. Se activa con /to-prompt, "mejorá este prompt", "ayúdame a escribir el prompt", "arma el prompt para otra sesión", "pasale esto a Codex pero bien escrito", o cuando el usuario pega un texto largo pidiendo que quede prolijo para un agente. NO la uses para una idea grande y con niebla que no cabe en una sesión (eso es /wayfinder), ni para fijar lo que ya se discutió en esta sesión (/to-spec), ni para stress-testear un razonamiento (/grill), ni para el bloque de $ARGUMENTS de spec-kit (/speckit-brief).
---

# to-prompt

Un pedido crudo ya trae casi todo el conocimiento de dominio. Lo que le falta no
es prosa: son **hechos comprobados, procedencia y un criterio de término**.

Esta skill produce el prompt. **Nunca lo ejecuta, y nunca publica en un tracker**
(eso es `/to-spec` y `/to-tickets`).

## Regla de oro

**Cero invención.** Toda **afirmación sobre el mundo** que entre al prompt es
`verificado`, `dicho`, `hipótesis` o `asumido`. La que no cae en ninguna de las
cuatro, se borra.

No llevan marca — porque no afirman nada, ordenan: encabezados, instrucciones
("no modifiques nada en esta fase"), decisiones pedidas, escaleras de tradeoffs,
prohibiciones y criterios de término. Marcarlas es ruido.

## Paso 0 — ¿Hace falta un prompt? (antes de correr nada)

**No corras un solo comando todavía.** Estas cuatro filas se contestan leyendo el
pedido. Correr el preflight primero gasta llamadas y, peor, genera inercia:
después de cuatro `Bash` ya nadie para.

Tres de estas skills tienen `disable-model-invocation: true` — **no las podés
invocar vos**. La acción es parar y decirle al humano qué tipear.

| Señal en el pedido | Acción |
| --- | --- |
| **Deíctico desnudo**: "hacé **esto**", "lo que discutimos", "lo de arriba" — el pedido *apunta* al trabajo en vez de traerlo | **PARÁ.** "El material ya está en el contexto de esta sesión — tipeá `/to-spec`." |
| No entra en una sesión; ni siquiera está claro cuáles son las decisiones | **PARÁ.** "Esto es un mapa, no un prompt — tipeá `/wayfinder`." |
| Resumen suelto, sin destino durable | **PARÁ.** "Tipeá `/handoff`." |
| Bloque de `$ARGUMENTS` para spec-kit | **PARÁ.** "Tipeá `/speckit-brief`." |
| **El pedido trae el material** — enunciado inline o pegado | **seguí al paso 1** |

La regla del deíctico es mecánica a propósito. "El material ya está en contexto"
es un juicio y no se puede aplicar; "el pedido dice *esto* en vez de traer el
material" se ve.

## Paso 1 — Preflight (determinístico)

Ahora sí, junta hechos. Nada de esto es opinable.

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
git rev-parse --abbrev-ref HEAD 2>/dev/null
git log --oneline -10 2>/dev/null
ls -1 AGENTS.md CLAUDE.md README.md 2>/dev/null
find . -maxdepth 2 -type d -not -path '*/.*' | head -40
ls -1 ~/.claude/skills/ 2>/dev/null
```

Y después, lo que de verdad paga:

> **Toda ruta, repo, CLI, archivo o skill que el pedido nombre se comprueba.**
> Si no existe, o existe distinto de como lo describe el pedido, eso es un
> **hallazgo del preflight**: se reporta antes de escribir nada. No se corrige
> en silencio ni se copia tal cual al prompt.

```bash
ls -d <cada ruta nombrada> 2>&1
<cada CLI nombrado> --help 2>&1 | head -20
sed -n '1,20p' ~/.claude/skills/<cada skill nombrada>/SKILL.md 2>/dev/null
```

**Higiene.** Nunca `find ~`. Buscá en las raíces que el pedido nombra, y excluí
`Library/`, `.Trash`, `node_modules`, `.git`. Un preflight que devuelve 80 líneas
de ruido no es evidencia, es distracción.

Sin repo detectable: todo el material queda `dicho` o `hipótesis`, y se dice en
el reporte. **No se inventa un repo.**

## Paso 2 — Enrutado caro (solo el preflight lo puede contestar)

| Hallazgo | Acción |
| --- | --- |
| **Ya existe.** El preflight muestra que lo pedido está construido, o resuelto por otra skill/herramienta | **PARÁ.** Decí qué existe, con evidencia, y que el gap es de adopción y no de tooling. Ofrecé las alternativas concretas que sí quedan. |
| **2 o más decisiones sin tomar** que el prompt estaría delegando | **PARÁ.** Ver *Umbral de decisiones*. |
| Ninguno de los dos | seguí al paso 3 |

Parar por "ya existe" es el mejor resultado que esta skill puede dar. Un prompt
para construir algo que ya está construido cuesta una sesión entera.

### Umbral de decisiones

Una decisión abierta se puede escribir como pregunta explícita *dentro* del
prompt. **Dos o más, no**: eso ya es un prompt que decide por el humano sin
avisarle, disfrazando decisiones de contexto.

Con 2 o más: **preguntá en una línea** si quiere correr `/grilling` ahora
(`grilling` sí es invocable), y disparala solo con un sí. Nunca la dispares de
sorpresa: es larga.

## Paso 3 — Destino

El destino cambia la **forma** del prompt, no su largo.

| Destino | Qué cambia | Esqueleto |
| --- | --- | --- |
| Agente con acceso al repo (Claude Code, Codex) | rutas y comandos reales; prohibiciones de archivos; **nada** que ya lea de `CLAUDE.md`/`AGENTS.md` | `agente-repo` |
| Modelo de chat sin herramientas | todo el contexto va inline: no puede ir a buscar nada | `chat` |
| Cuerpo de issue (`to-tickets`, `vikunja`, GitHub) | criterios de aceptación y blocked-by, no proceso | `issue` |
| Agente en repo ajeno o del trabajo | fase read-only explícita y qué no tocar | `agente-repo` + cláusula read-only |
| Cualquier otro | **PARÁ Y PREGUNTÁ** | — |

Esqueletos en `references/esqueletos.md`.

## Paso 4 — Procedencia

**4a. Comprobar.** Todo lo del pedido que el preflight pueda confirmar, se
confirma. Un hecho comprobado vale más que tres párrafos de estructura.

**4b. Marcar.** Sufijo al final de cada línea. Por línea, no por sección —
agrupar por sección invita a acomodar.

| Marca | Significa |
| --- | --- |
| `— verificado` | lo corrí o lo leí ahora, en este preflight |
| `— dicho` | el humano lo afirmó; no lo pude comprobar |
| `— hipótesis` | sospecha del humano, sin confirmar |
| `— asumido` | hueco que llenaste vos porque no cambiaba el entregable |

Todo bloque con líneas `— hipótesis` cierra, una sola vez, con:

```
Esto es hipótesis mía, no requisito. No asumas que es correcta.
```

## Paso 5 — Una ronda de preguntas (máximo 5)

- **Nunca** preguntes lo que el preflight contestó.
- Preguntá **solo lo que cambia el entregable**. Si las dos respuestas posibles
  producen el mismo prompt, asumí y marcá `— asumido`.
- Numeradas, cada una con tu recomendación, para que se pueda contestar
  "sí a todo".
- **Una sola ronda.**

Al cerrar la ronda, el enrutado se dispara **otra vez**:

| Lo que sigue faltando | Acción |
| --- | --- |
| **Hechos** | buscalos, o dejalos `— asumido`. Seguí. |
| **Decisiones** (2 o más) | **PARÁ.** Volvé al *Umbral de decisiones*. |

Una decisión sin tomar no se arregla escribiendo mejor. Se arregla decidiendo.

## Paso 6 — Un solo objetivo

Si el material trae más de un trabajo (criterios de éxito distintos), el default
es **principal + backlog**:

1. Escribí completo **el principal**.
2. Los otros van al final, numerados, bajo
   `## Fuera de alcance — próximos prompts`.

Nunca los mezcles en un prompt. **Nunca bloquees pidiendo que elija.**

## Paso 7 — Redactar

Esqueleto según destino. Y la regla que fija el largo:

> **Cero líneas derivables.** Si el agente destino lo va a leer igual de
> `CLAUDE.md`, `AGENTS.md`, el README o el repo mismo, no lo escribas.
> Cada línea **apunta, comprueba, decide o acota**.

El largo lo fija la evidencia, no una cuota. Un prompt de 70 líneas donde cada
una aporta está bien; uno de 15 de relleno, no.

## Los cinco gates

Bloquean la salida. No son checklist: si uno falla, **no se emite**.

| # | Gate | Falla | Acción |
| --- | --- | --- | --- |
| 1 | Procedencia | hay una **afirmación** sin marca | comprobala o borrala |
| 2 | Derivable | el destino lo lee igual del repo o de `CLAUDE.md` | fuera |
| 3 | Comprobable | no hay criterio de término verificable | escribilo, o preguntalo |
| 4 | Un objetivo | hay dos trabajos mezclados | paso 6 |
| 5 | Capacidad | le pedís algo que el destino no puede hacer | reformulá o cambiá de destino |

## Salida

**Llegar hasta acá es el camino feliz. Si llegaste, se escribe el archivo — no
se termina con el prompt en el chat.**

1. Escribí el prompt en
   `~/Documents/agent-scratch/<repo>/<slug>/<AAAA-MM-DD>-prompt.md`.
   `<repo>`: nombre del directorio del repo, o `_sin-repo`.
   `<slug>`: kebab-case corto del pedido.
2. `pbcopy < <ruta>`.
3. Reportá en **3 líneas**:
   - destino elegido y esqueleto usado;
   - qué borró cada gate, **en número**: `gate 2 → 12 líneas`, o `gate 2 → 0`.
     Nunca en prosa: "no borró nada grande" no se puede auditar;
   - qué quedó `— hipótesis` / `— asumido`, más los hallazgos del preflight.

La tercera línea es la que importa: **el gate final es el humano**, y ese renglón
le dice dónde mirar en vez de obligarlo a releer todo.

## Referencias

- `references/esqueletos.md` — los tres esqueletos por destino.
- `references/ejemplo.md` — un pedido crudo real, anotado de punta a punta.
