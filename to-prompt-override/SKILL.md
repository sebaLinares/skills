---
name: to-prompt-override
description: Escribe el prompt para otro agente cuando el usuario ya decidió saltarse el gate de aprobación del repo destino - sin ronda de preguntas, delegando las decisiones abiertas al agente, y con un bloque de anulación explícito al principio del prompt. Mantiene intactos el preflight, la procedencia (verificado / dicho / hipótesis / asumido) y los seis gates de /to-prompt - solo invierte el umbral de decisiones y elimina la ronda de preguntas. Se activa SOLO con /to-prompt-override, o cuando el usuario pide explícitamente anular el gate - "no esperes mi aprobación", "las decisiones las tomás vos", "no me hagas preguntas", "codealo ya, reviso yo local". Si el usuario no pidió explícitamente saltarse el gate, usá /to-prompt - nunca infieras la anulación.
---

# to-prompt-override

`/to-prompt` para cuando el humano **ya decidió** saltarse el gate de aprobación
del repo destino.

No es una versión rápida ni una versión relajada. Es la misma skill con **dos
inversiones**, y nada más. Todo lo que hace bueno a `/to-prompt` — el preflight,
la procedencia, los seis gates — queda igual, porque nada de eso era lo que
frenaba al humano.

## La única diferencia

| | `/to-prompt` | acá |
| --- | --- | --- |
| **Umbral de decisiones** (2+ sin tomar) | **PARÁ**, ofrecé `/grilling` | **se invierten**: van al prompt como `## Qué tenés que decidir (vos, sin preguntar)` |
| **Paso 5 — ronda de preguntas** | una ronda, máximo 5 | **cero**. Todo hueco es `— asumido` o una decisión delegada, y se nombra en el reporte |

Todo lo demás **no cambia y no se relaja**:

| Sigue igual | Por qué |
| --- | --- |
| Paso 0 — deíctico desnudo → `/to-spec` | si el material ya está en esta sesión, `/to-spec` es **más rápido**, no más lento |
| Paso 1 — preflight completo | es lo que hace que el prompt sea correcto. La urgencia no compra el derecho a inventar |
| Paso 2 — "ya existe" → **PARÁ** | construir lo que ya está construido cuesta una sesión entera. Con apuro cuesta lo mismo |
| Paso 6 — un solo objetivo | — |
| Paso 7 — material a granel no se transcribe | reproducir 74 KB de SVG pegado costó 14 min en una corrida real. Es la mitad del reloj, y no compra nada |
| Los **seis** gates | la procedencia es barata y es la regla de oro. El gate 6 (transportable) pega más fuerte acá: nadie te va a frenar para avisarte que la ruta no resuelve |

Los comandos del preflight y los tres esqueletos **no se duplican acá**: se leen
de `~/.claude/skills/to-prompt/SKILL.md` (pasos 1 y 4) y de
`~/.claude/skills/to-prompt/references/esqueletos.md`. Este archivo solo define
lo que cambia.

Destino: **siempre `agente-repo`.** Un modelo de chat no tiene gate que anular, y
un issue lo lee alguien en tres semanas, cuando la urgencia de hoy ya es mentira.
Si el destino no es un agente con acceso al repo, **PARÁ** y decí que corresponde
`/to-prompt`.

## La autoridad

Que el humano tipee `/to-prompt-override` **concede la categoría**: saltarse el
gate de aprobación del repo, y no devolver preguntas. Eso es lo que significa el
nombre; pedirle que lo repita con palabras es teatro.

No concede **los específicos**. Estos salen del pedido, o se escriben `— asumido`
y se nombran en el reporte:

- si se commitea o no,
- qué artefacto gana un conflicto con el código actual,
- el alcance exacto de lo que puede decidir solo.

> **Nunca infieras una anulación.** "Quiero esto rápido" no es una anulación.
> Esta skill solo se corre cuando el humano la invocó o pidió el bypass con
> todas las letras. La regla vale en los dos niveles: no inventes el bloque, y
> no te enrutes solo hacia acá desde `/to-prompt`.

## El bloque de anulación

Va **primero**, arriba de `## Hechos ya comprobados`. No es un pie de página:
cambia cómo se lee todo lo que viene abajo.

Antes de escribirlo, preguntate estas cuatro. La lista es fija; **lo que se
emite, no** — una cláusula que el humano no contestó no se inventa, se reporta.

| # | Pregunta | Dónde va |
| --- | --- | --- |
| 1 | ¿Qué gate del repo destino se anula? | el bloque. Nombralo con archivo y línea (`CLAUDE.md:NN`) |
| 2 | ¿Puede devolver preguntas? | el bloque, con la frase fuerte |
| 3 | ¿Commitea, abre PR, o no toca git? | el bloque |
| 4 | ¿Qué artefacto gana un conflicto con el código? | **no va acá** — va a `## Fuente de verdad` del esqueleto compartido |

**Una viñeta por cláusula, máximo 3 líneas.** El bloque es autoridad, no
argumento. Si hace falta justificar *por qué* la anulación es legítima — que el
asset nuevo no es lo que la tarea bloqueada prohibía, que el ticket ya se
cerró — eso es una **afirmación sobre el mundo**: va a `## Hechos ya comprobados`
con su `— verificado`, y el bloque apunta ahí en media línea.

**Una cláusula sin contestar no se escribe en el bloque.** Va a la línea 4 del
reporte y a ningún otro lado. Inventarla y justificarla con un default plausible
("no commitees — default del repo") es exactamente lo que la regla prohíbe: es
una instrucción inventada con una coartada, no un hueco reportado.

Y el bloque **no se puede escribir sin su contrapartida**: si nadie te va a
frenar antes, el humano necesita saber después qué decidiste por él. Esa línea
es estructural, no opcional.

```markdown
## Instrucciones del usuario (anulan el gate normal de este repo)

- No esperes aprobación humana del plan antes de implementar. El usuario lo dijo
  explícitamente para esta tarea puntual — anula <la regla, con archivo y línea>.
- Las decisiones que queden abiertas (marcadas abajo) las tomás vos.
  **No me hagas preguntas bajo ninguna circunstancia** — ni acá ni vía
  comentario/PR. No pares a esperar respuesta.
- <commits: qué hace con git, literal de lo que dijo el humano>
- Al terminar, listá en un bloque final **cada decisión que tomaste por mí** y
  por qué. Una línea por decisión.
```

La frase de la segunda viñeta va **literal**. "No preguntes" y "no pares a
esperar respuesta" ya se probaron y no alcanzaron como señal: el agente igual
volvió a preguntar. `No me hagas preguntas bajo ninguna circunstancia` sí.

### Fragmento anotado

De un caso real — reconciliar una sección de UI contra unos frames de Figma, con
el gate del repo anulado a mitad del preflight:

```markdown
## Instrucciones del usuario (anulan el gate normal de este repo)

- No esperes aprobación humana del plan antes de implementar. El usuario lo dijo
  explícitamente para esta tarea puntual — anula la regla de `CLAUDE.md` de este
  repo que exige `status: active` + aprobación antes de codear.
     ↑ nombra la regla exacta. "anula el gate" sin decir cuál no es auditable.
- Generá un plan solo para organizarte vos, no para publicarlo a aprobación.
     ↑ la anulación es del *gate*, no del artefacto. El plan sigue sirviendo.
- Las decisiones de diseño/alcance que queden abiertas (marcadas abajo) las
  tomás vos. **No me hagas preguntas bajo ninguna circunstancia** — ni acá ni
  vía comentario/PR. No pares a esperar respuesta.
     ↑ literal. La perifrástica no funcionó.
- No hagas commit al terminar. El usuario revisa localmente.
     ↑ cláusula 3, **dicha** por el humano. Si no la hubiera dicho, esta viñeta
       no existe: el hueco va al reporte, no al bloque con un default inventado.
- Al terminar, listá cada decisión que tomaste por mí y por qué.
     ↑ la contrapartida. Sin esto, el humano reconstruye 4 decisiones leyendo el diff.
```

Y el desempate del mismo caso, que **no** va en este bloque:

```markdown
## Fuente de verdad

Ante cualquier diferencia entre lo que ya está codeado en el repo y lo que
muestra el Figma que trajo el usuario, manda el Figma. El código actual es el
estado viejo a corregir, no una referencia a preservar.
```

## Material a granel y rutas

Dos reglas de `/to-prompt` que acá se rompen más seguido, porque no hay ronda de
preguntas donde el humano las note:

- **No transcribas material a granel** (paso 7 de `/to-prompt`). Un bloque
  verbatim de más de ~30 líneas que el pedido ya trajo — SVG, log, dump, un
  archivo pegado — va como **sección vacía con nombre**, y la salida le dice al
  humano qué pegar debajo. Nunca a un archivo hermano: eso cuesta los mismos
  tokens y además rompe la regla de abajo.
- **Ninguna ruta relativa** (gate 6). El prompt se pega en un agente que corre en
  el repo destino, no donde vive el archivo del prompt. "Mismo directorio" y "el
  archivo hermano" no resuelven a nada del otro lado.

## Las decisiones delegadas

Las 2 o más decisiones que `/to-prompt` habría convertido en un **PARÁ** se
escriben acá, con los mismos verbos duros del esqueleto (`definí`, `elegí`,
`justificá` — nunca "pensá en"), y con el recordatorio de que no se consultan:

```markdown
## Qué tenés que decidir (vos, sin preguntar — ver instrucciones arriba)
```

Cada una tiene que ser **decidible con lo que el prompt ya trae**. Si para
resolver una hace falta algo que solo el humano sabe y el pedido no dijo, eso no
es una decisión delegable: es un hueco. Marcalo `— asumido` con tu elección, y
nombralo en la línea 4 del reporte.

## Salida

Igual que `/to-prompt` — archivo en
`~/Documents/agent-scratch/<repo>/<slug>/<AAAA-MM-DD>-prompt.md`, después
`pbcopy < <ruta>`. Si hay material a granel, una línea que diga qué pega el
humano y debajo de qué sección.

El reporte son **cuatro** líneas, no tres:

1. destino y esqueleto (siempre `agente-repo` + bloque de anulación);
2. qué borró cada gate, en número: `gate 2 → 12 líneas`;
3. qué quedó `— hipótesis` / `— asumido`, más los hallazgos del preflight;
4. **qué autoridad se anuló** (`CLAUDE.md:NN`), **qué decisiones quedaron
   delegadas** (numeradas), y **cuáles de las cuatro cláusulas el humano no
   contestó** — nombradas acá justamente porque no se escribieron en el bloque.

La cuarta línea existe porque acá el humano no tiene ningún otro checkpoint.
En `/to-prompt` el gate final es el humano leyendo el reporte; acá es el **único**
gate que queda antes de que un agente escriba código sin aprobación.

Cuatro y no más. La quinta se saltea, y saltearla es lo mismo que no tenerla.
