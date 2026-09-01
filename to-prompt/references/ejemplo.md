# Ejemplo anotado

Pedido real. Destino real. Muestra los cuatro conceptos de una sola pasada:
**preflight, procedencia, enrutado, gates**.

---

## El pedido crudo

Pegado tal cual, resumido a lo esencial:

> Tengo 3 vaults de Obsidian (slinaresl personal, cencosud trabajo, electromtica
> de la empresa de mi suegro). Cuando trabajo en un repo corro `/handoff` para
> que genere un documento de la sesión y lo persista en
> `/Users/sebastianlinares/Documents/agent-scratch`. Si el handoff merece
> persistirse, copio el md, abro una nota nueva en el vault que corresponde,
> pego, voy a la terminal, abro `claude` y escribo `ingest @"nombre-de-la-nota"`.
> A veces se me olvida el handoff y nunca más lo miro; en `agent-scratch/` debe
> haber handoffs que nunca usé.
>
> Busquemos la forma de eficientar esto. Creo que el intermediario
> `agent-scratch/` quizás está sobrando. Quizás no solo los handoffs, también
> las sesiones en general: a veces quedan WIP y son "pendientes" que debería
> retomar, pero viviendo en el scratch pad no tengo cómo ver qué dejé a medias.

## Paso 0 — Preflight

Lo que se comprobó, y lo que devolvió:

| Comprobación | Resultado |
| --- | --- |
| `ls -d ~/Notes/*` | 4 directorios: `_shared`, `cencosud`, `electromatica`, `slinaresl` — el pedido decía 3, y escribía mal `electromtica` |
| `ls ~/Documents/agent-scratch` | existe, **21 subdirectorios** — el "debe haber handoffs sin usar" es medible, no una sospecha |
| `sed -n 1,10p ~/.agents/skills/handoff/SKILL.md` | **"Save to the temporary directory of the user's OS — not the current workspace."** |
| `grep -ril ingest ~/Notes/slinaresl/` | `ingest` está definido **dentro del vault** (`CLAUDE.md`, `system/`), no como skill global |

**El hallazgo que justifica la skill entera:** el pedido afirma que `/handoff`
persiste en `agent-scratch`. El skill dice que guarda en el directorio temporal
del SO. La afirmación central del pedido era falsa, y sin preflight habría
llegado al prompt final más prolija, más estructurada e igual de falsa.

Segundo hallazgo, más sutil: `ingest` solo existe si el agente corre **dentro**
del vault. Eso no es un detalle de implementación — condiciona cualquier diseño
que proponga automatizarlo.

## Pasos 1 y 2 — Enrutado

**A. ¿Hace falta un prompt?** Sí. Cabía en una sesión (de hecho salió una skill
de ahí), el material no estaba en el contexto de una sesión previa, y las
decisiones abiertas eran una sola: *¿el intermediario sobra?*. Una se escribe
como pregunta dentro del prompt; dos habrían mandado esto a `/grill`.

**B. ¿Qué destino?** Un modelo de chat sin herramientas → esqueleto `chat`.
Consecuencia concreta: los cuatro hallazgos del preflight van **inline**. Si el
destino hubiera sido Claude Code, tres de ellos habrían sido punteros
(`leé handoff/SKILL.md`) en vez de contenido.

## Paso 3 — Procedencia

| Marca | Línea |
| --- | --- |
| `— verificado` | Los vaults son 4 directorios en `~/Notes/`, uno (`_shared`) es maquinaria compartida |
| `— verificado` | `handoff` guarda en el temp del SO, no en `agent-scratch` |
| `— verificado` | `agent-scratch/` tiene 21 subdirectorios hoy |
| `— dicho` | El flujo manual es copiar → pegar en el vault → `ingest` |
| `— dicho` | A veces el handoff se olvida y nunca se vuelve a mirar |
| `— hipótesis` | El intermediario `agent-scratch/` sobra en la mayoría de los casos |
| `— hipótesis` | Esto aplica a las sesiones en general, no solo a los handoffs |
| `— asumido` | Las notas WIP tienen que ser consultables desde el vault, no desde el filesystem |

Las dos `— hipótesis` cierran con la frase de desanclaje. Sin ella, el destino
diseña *asumiendo* que el intermediario sobra, que es exactamente la conclusión
que se le estaba pidiendo evaluar.

## Paso 4 — La ronda

Cinco preguntas, ninguna de las cuales el preflight ya contestaba:

1. ¿La nota WIP y el handoff cerrado son la misma cosa en dos estados, o dos
   artefactos distintos? *(recomiendo: mismo artefacto, dos estados)*
2. ¿Qué decide a qué vault va: la ruta del repo, o tu criterio en el momento?
   *(recomiendo: la ruta, tabla determinística)*
3. ¿`ingest` se dispara solo al cerrar, o sigue siendo manual?
   *(recomiendo: manual — es conversacional)*
4. ¿"Ver lo que quedó a medias" es una query del vault o un comando?
   *(recomiendo: query — ya tenés el sistema)*
5. ¿`agent-scratch/` desaparece, o se queda para el material de investigación?
   *(recomiendo: se queda, cambia de rol)*

Ninguna es sobre hechos: los hechos los resolvió el paso 0. Todas cambian el
entregable. Esa es la prueba de que una pregunta merece existir.

## Los gates

| Gate | Qué hizo |
| --- | --- |
| 1 · Procedencia | 3 líneas de relleno narrativo sin marca posible → borradas |
| 2 · Derivable | "uso Claude y Codex indistintamente" → el destino no puede hacer nada con eso → fuera |
| 3 · Comprobable | el pedido terminaba en "eficientar el proceso" → se reemplazó por las 5 preguntas que el sistema resultante debe poder contestar |
| 4 · Un objetivo | "quizás no solo los handoffs, las sesiones en general" era un segundo trabajo → al backlog |
| 5 · Capacidad | el destino no tiene herramientas → se quitó toda instrucción de inspeccionar rutas |

El gate 3 es el que más cambia el resultado. "Eficientar el proceso" no se puede
verificar. "El sistema debe poder contestar *qué quedó a medias*" sí.

## El cierre

El prompt resultante llevó a lo que hoy es la skill `wrap`: tabla de rutas a
vaults, la ubicación como estado (`workspace/sessions/` = abierta), y `ingest`
que sigue siendo conversacional.

Las tres decisiones salieron de las preguntas 2, 1 y 3. Ninguna salió de
escribir más lindo.

---

## Nota: correr este mismo pedido hoy da otra respuesta

Si hoy le pegás este pedido crudo a `to-prompt`, el preflight ya no llega a las
preguntas: encuentra que `~/sebalinares-skills/wrap` **ya hace** todo lo que el
pedido pide — tabla de rutas a vaults, la nota escrita directo en
`workspace/sessions/`, `--close` que promueve a `sources/handoffs/` — y que
`~/Notes/slinaresl/sources/handoffs/` ya está poblada.

Eso dispara la fila **"ya existe"** del paso 2, y la respuesta correcta deja de
ser un prompt: es *"ya está construido, el gap es de adopción"*.

Es el mismo pedido, el mismo preflight, y una salida distinta porque el mundo
cambió. Esa es exactamente la razón por la que el preflight corre siempre y no
se cachea.
