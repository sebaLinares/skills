---
name: speckit-brief
description: Redacta el bloque de $ARGUMENTS con el que hay que acompañar un comando de spec-kit (/speckit-plan, /speckit-clarify, /speckit-implement, etc.), y decide cuál corresponde correr cuando llegó información nueva a mitad del pipeline. Úsala SIEMPRE antes de correr cualquier comando de spec-kit — nunca se corre uno pelado. Se activa con /speckit-brief, "prepara el prompt para speckit", "qué comando de speckit corro ahora", "cambió el repo de contexto", "llegó un PR nuevo y ya tengo spec/plan/tasks", o cuando el usuario está por invocar un comando speckit sin argumentos.
---

# speckit-brief

Un comando de spec-kit pelado desaprovecha la etapa. Los 10 comandos aceptan
`$ARGUMENTS` y todos dicen *"You MUST consider the user input"*. Esta skill
produce ese input — **no ejecuta el comando**.

## Regla de oro

Tu salida es **un archivo y un `pbcopy`**. Nunca invocas el comando de spec-kit.
El humano decide cuándo correrlo.

## Paso 0 — siempre

```bash
putils speckit check                    # en el repo de código
```

Eso responde, sin adivinar, dos cosas que ninguna cantidad de prompting detecta:

1. **Sobre qué feature va a operar spec-kit realmente.** Resuelve por
   `SPECIFY_FEATURE_DIRECTORY` → `.specify/feature.json`; **la rama no se usa**.
   Si hay MISMATCH, dilo primero y para: todo lo demás sería sobre la feature
   equivocada.
2. **Si llegó evidencia nueva al repo de contexto** desde que se escribieron
   spec/plan/tasks, y por qué etapa debe entrar.

Luego:

```bash
putils speckit gather --command <cmd>   # dosier con requisitos, rutas y freeze
```

Y para revisar todos los repos de una vez (features activas, mismatches, deriva
pendiente, implement a medias):

```bash
putils speckit doctor
```

El dosier trae la mitad determinista. Tú aportas la otra mitad: **el cruce**.

## Los dos modos

`gather` te dice en cuál estás.

| Modo | Cuándo | Esqueleto |
|---|---|---|
| **A · enriquecer** | primera pasada de una etapa; no hay evidencia nueva sin absorber | briefing (7 preguntas) |
| **B · reconciliar** | llegó información nueva y ya avanzaste | reconciliación (evento → cruce → freeze → prioridad) |

Los esqueletos están en `references/skeletons.md`. En modo B, el comando a correr
lo decide `references/reentry-map.md` — no lo elijas por intuición.

## Reglas de redacción

Estas cuatro deciden si el bloque sirve o estorba:

1. **Cero líneas derivables.** Si el agente lo va a leer igual en `spec.md`, la
   constitution o el propio template del comando, no lo escribas. Cada línea
   **apunta, cruza, congela o prioriza**.
2. **El cruce es el producto.** Un resumen de lo que cambió upstream no sirve
   solo: cada cambio termina en `→ contradice FR-014` / `→ reduce SC-009` /
   `→ requisito nuevo, sin cobertura`. Los IDs vienen en el dosier.
3. **Lo no verificable es pregunta, nunca supuesto.** Si no puedes confirmar
   ownership, acceso o comportamiento, va como BLOCKED con dueño. Jamás inventes
   endpoints, equipos ni contratos.
4. **Prioriza explícitamente.** `clarify` hace 5 preguntas como máximo y
   `specify` admite 3 marcadores `[NEEDS CLARIFICATION]`. Si no dices qué
   conflictos son duros, gasta el presupuesto en detalles.

La longitud la fija la evidencia, no una cuota. Un bloque de 70 líneas donde cada
una cruza algo es correcto; uno de 15 líneas de boilerplate no.

## Contrato de etapa

Cada comando tiene permisos distintos. Ver `references/stage-contracts.md`.
Emite solo las 2-4 prohibiciones que **de verdad muerden** en este caso
(típicamente: qué archivos no tocar y que no promueva nada). No copies el
contrato entero: eso es boilerplate.

## Salida

1. Escribe el bloque en la ruta que indica el dosier
   (`~/Documents/agent-scratch/<repo>/<feature>/<fecha>-<cmd>-brief.md`).
2. `pbcopy < <ruta>`.
3. Reporta en 3 líneas: comando a correr, qué conflictos duros priorizaste, y
   qué quedó como pregunta abierta para el humano.
4. Si `check` mostró MISMATCH, repite el `export` como primera línea del reporte.

Cuando el humano confirme que ya corrió el comando:

```bash
putils speckit absorb <sha>...          # deja de reportar esos commits
```

## Referencias

- `references/reentry-map.md` — qué escribe cada comando, las tres trampas, y
  qué correr según dónde estás. **Lectura obligatoria en modo B.**
- `references/skeletons.md` — los dos esqueletos, con un ejemplo real anotado.
- `references/stage-contracts.md` — qué puede y no puede decidir cada etapa.
