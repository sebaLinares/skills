# Contratos de etapa

Qué puede decidir cada comando de spec-kit, qué no, y con qué tope.
Emite en el bloque solo las prohibiciones que muerden en el caso concreto.

| Comando | Puede decidir | NO puede | Tope / nota |
|---|---|---|---|
| `constitution` | invariantes de ingeniería del repo, MUST vs SHOULD | nada específico de una feature | sobrescribe `constitution.md` |
| `specify` | necesidades, actores, alcance, fuera de alcance | arquitectura, tecnología, protocolos | **3** `[NEEDS CLARIFICATION]`; crea feature **nueva** |
| `clarify` | resolver ambigüedad de requisitos; escribe en `spec.md` | decisiones técnicas (son de `plan`) | **5** preguntas |
| `checklist` | si los requisitos están bien escritos | casos de prueba de implementación | append; no es un test plan |
| `plan` | decisiones técnicas, contratos, estructura | cambiar requisitos para acomodar el diseño | termina en Phase 1; no genera tasks |
| `tasks` | descomponer en trabajo ejecutable y ordenarlo | inventar arquitectura ausente del plan | decisión faltante → blocker, no la decide |
| `analyze` | señalar inconsistencias entre spec/plan/tasks/constitution | modificar cualquier archivo | read-only estricto |
| `implement` | escribir código conforme a `tasks.md` | reinterpretar intent, ampliar alcance, refactors no pedidos | marca `[X]` en tasks.md |
| `converge` | detectar trabajo declarado y no construido | reescribir tasks previas, borrar código, sugerir mejoras nice-to-have | append-only |
| `taskstoissues` | convertir tasks ejecutables en issues | crear issues de headings, notas o blockers sin trabajo | dedup por task ID |

## Las prohibiciones que suelen faltar

Por etapa, lo que en la práctica se escapa si no lo escribes:

- **`specify`** — "no definas arquitectura ni protocolos todavía; separa
  requirements / assumptions / open questions / out of scope".
- **`clarify`** — "no preguntes decisiones técnicas que le corresponden a
  `plan`"; y en modo reconciliación: "no toques `plan.md`, `tasks.md`,
  `contracts/` ni código en esta corrida".
- **`plan`** — "no modifiques la spec para acomodar el diseño"; si es un
  re-plan, **di qué secciones de `plan.md` quedaron invalidadas** (el archivo se
  preserva, las secciones viejas sobreviven en silencio).
- **`tasks`** — "si `tasks.md` requiere una decisión ausente del plan, repórtala
  como blocker en vez de decidirla".
- **`implement`** — presupuesto de cambio: cambios mínimos y localizados, sin
  refactors, sin tocar dependencias ni infraestructura ajena, sin cambiar APIs
  públicas fuera de `contracts/`; ante contradicción material entre código, task
  y plan: **STOP y reporta**.
- **`converge`** — "solo gaps respecto del intent ya documentado; nada de
  mejoras".

## Definition of Done del bloque

Pide siempre que el comando cierre separando estas cuatro cosas, que los agentes
mezclan si no se las delimitas:

```
decisiones confirmadas · supuestos · blockers con dueño · preguntas abiertas
```

Y en cualquier etapa que escriba artefactos: **"no promuevas nada"** — el humano
aprueba antes de pasar a la etapa siguiente.
