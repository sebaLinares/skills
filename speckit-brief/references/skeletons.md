# Los dos esqueletos

Rellénalos con evidencia. Si una sección no tiene contenido **no derivable**,
bórrala — una sección vacía o genérica resta atención a las que sí importan.

---

## Modo A · enriquecer

Primera pasada de una etapa. Las 7 preguntas; **emite solo las que tengan
respuesta no obvia**.

```markdown
/speckit-<cmd>

Baseline:      desde qué rama/SHA se razona; qué snapshot es el válido.
Fuentes:       qué documentos y qué código son autoritativos, en orden.
Antes de decidir:  qué hay que verificar en código real; qué NO se puede inventar
               (contratos, ownership, comportamiento) y qué se marca BLOCKED.
Ya decidido:   constraints cerrados que esta corrida no reabre.
Debe cubrir:   las dimensiones que harían que el resultado parezca correcto pero
               esté incompleto (failure modes, timeouts/retries, idempotencia,
               privacidad, observabilidad, rollout/rollback, pruebas).
No hagas:      límites de alcance y de escritura para esta etapa.
Al terminar:   decisiones · supuestos · blockers con dueño · preguntas abiertas.
```

Para una feature chica dentro de un solo repo, esto cabe en 8 líneas. Para una
integración entre equipos, no.

---

## Modo B · reconciliar

Llegó evidencia nueva y ya avanzaste. Seis bloques, en este orden:

```markdown
/speckit-<cmd>

1. EVENTO Y PROCEDENCIA
   Qué cambió, en qué repo, qué PR/SHA, qué fecha, y que es POSTERIOR a
   spec/plan/tasks. Una frase sobre qué premisa invierte.
   Cierra con el alcance: "esta corrida solo reconcilia la spec".

2. FUENTES AUTORITATIVAS
   Rutas absolutas a leer ANTES de preguntar. Del dosier, tal cual.

3. EL CRUCE  ← el producto
   Por cada cambio: qué es, y a qué requisito de ESTE repo le pega.
     N. <cambio concreto, con el dato verificable>
        → contradice FR-0xx / reduce SC-0xx / requisito nuevo, sin cobertura

4. CONGELADO
   Lo que no se reabre, aunque la evidencia lo roce.

5. TAREA Y PRIORIDAD
   Qué hacer, y **qué conflictos van primero**. Con tope de 5 preguntas, esta
   línea decide si la corrida sirve.
   Dónde registrar el resultado (sesión fechada, citando evidencia por archivo).
   Distinguir lo decidido upstream de lo que sigue siendo decisión de este repo.

6. LÍMITES DE ESCRITURA
   Qué archivos no tocar en esta corrida. "No promuevas nada."
```

---

## Espécimen anotado

Caso real: `006-pia-chat-sse-proxy` en ms-search, tras el merge de un PR en el
repo de contexto que invirtió la premisa de passthrough 1:1.

```markdown
/speckit-clarify

⟨1 EVENTO⟩
Contexto: el repo de contexto `be-paris-pia-context` mergeó el PR #11
(commit d4d9811, 2026-08-26) DESPUÉS de que se generaron spec/plan/tasks.
Ese PR invierte la premisa de passthrough 1:1 sobre la que está escrita
spec.md. No implementes nada: esta corrida solo reconcilia la spec.

⟨2 FUENTES⟩
Fuentes autoritativas a leer antes de preguntar:
- .../001-pia-chat-sse-integration/contracts/pia-ms-search-proxy.md
- .../001-pia-chat-sse-integration/data-model.md
- .../context/notas/2026-08-26-cliente-referencia-y-slice.md

⟨3 CRUCE⟩            ← cada punto termina apuntando a un ID
1. Passthrough 1:1 → fachada. Los frontends consumen un contrato Paris
   estable; ms-search adapta al GET real de Search.
   → contradice FR-001 y FR-014.
3. clientId/sessionId/userId NO viajan en el body; se derivan server-side.
   → contradice FR-002 y la clave de rate limiting de FR-009.
4. El parser debe leer el nombre desde la línea `event:`; follow_up_questions
   e item_results son opcionales y order-independent.
   → contradice FR-003 (orden fijo) y SC-009.
5. El upstream no respeta num_results=1; la fachada aplica el tope de salida.
   → requisito nuevo, sin cobertura hoy.

⟨4 CONGELADO⟩
Lo que NO cambia y no debe reabrirse: la topología aprobada, que ningún
frontend llame a Search/Constructor directamente, la política de precio de
la Historia 2 (FR-012/FR-013).

⟨5 TAREA Y PRIORIDAD⟩
- Recorre spec.md y marca cada requisito que la nueva evidencia invalida,
  reduce o amplía.
- Prioriza las preguntas sobre los conflictos duros (FR-001/002/003/009/014
  y SC-009) por encima de los detalles nuevos.
- Registra las respuestas en una sesión nueva de Clarifications fechada
  2026-08-27, citando la evidencia por archivo, no por memoria.
- Distingue lo decidido upstream de lo que sigue siendo decisión de este repo.

⟨6 LÍMITES⟩
- No toques plan.md, tasks.md, contracts/ ni código en esta corrida.
- No promuevas nada: el plan queda como está hasta aprobación humana.
```

### Por qué funciona

- **Cada punto del cruce muere en un ID.** Sin eso es un resumen del PR, y el
  resumen ya está en el repo de contexto.
- **La prioridad es explícita.** Seis conflictos duros nombrados para un
  presupuesto de cinco preguntas.
- **El congelado es corto y concreto.** No es una lista de principios: son las
  tres cosas que la evidencia nueva podría hacer tambalear sin deber hacerlo.
- **Los límites de escritura son dos líneas**, no el contrato de etapa completo.
- **Nada inventado.** Donde no hay certeza (semántica de `thread_id`, ownership
  del prefijo `/pia/v1`), queda como pregunta con dueño, no como supuesto.
