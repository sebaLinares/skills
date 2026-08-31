# Mapa de re-entrada de spec-kit

Qué correr cuando llega información nueva y ya avanzaste en el pipeline.

Todo lo de aquí está verificado contra los templates de `github/spec-kit`
(`templates/commands/*.md`, `scripts/bash/*.sh`). Las referencias `archivo:línea`
son a ese repo.

---

## 0. Preflight: ¿sobre qué feature va a operar el comando?

**Esta es la primera comprobación, siempre.** `get_feature_paths`
(`common.sh:163-207`) resuelve la feature en este orden:

1. variable de entorno `SPECIFY_FEATURE_DIRECTORY`
2. `.specify/feature.json` → clave `feature_directory`
3. error

**La rama de git no se usa nunca.** `feature.json` lo escribe el último
`specify` que corriste, así que apunta a la última feature *creada*, no a la que
estás trabajando. Si trabajas en una rama con nombre de ticket
(`STR-3062-PiaChatSseProxy`) sobre una feature que no fue la última creada, todos
los comandos operan sobre la feature equivocada y no avisan.

```bash
bash .specify/scripts/bash/check-prerequisites.sh --paths-only   # qué resolvería
export SPECIFY_FEATURE_DIRECTORY=specs/006-mi-feature            # corregir
```

---

## 1. Qué escribe cada comando

| Comando | Escribe | Semántica | Re-correr |
|---|---|---|---|
| `specify` | `specs/NNN-<slug>/` **nuevo** + `.specify/feature.json` | crea una feature nueva por invocación (`specify.md:82-110`) | 🔴 bifurca |
| `clarify` | `spec.md` | append a Clarifications; reemplaza texto contradictorio (`clarify.md:195-196`) | ✅ seguro |
| `plan` | `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` | plan.md se **preserva** si existe (`setup-plan.sh:38-40`); el resto se regenera | ⚠️ mixto |
| `tasks` | `tasks.md` | regeneración total desde template, **sin guarda de existencia** (`setup-tasks.sh`) | 🔴 destructivo |
| `analyze` | nada | read-only estricto (`analyze.md:58,247`) | ✅ gratis |
| `implement` | código + marca `[X]` en tasks.md (`implement.md:169`) | avanza el estado | — |
| `converge` | `tasks.md` | **APPEND-ONLY, NEVER REWRITE** (`converge.md:73-79`) | ✅ seguro |
| `checklist` | `checklists/<nombre>.md` | append; nunca borra (`checklist.md:146-147`) | ✅ seguro |
| `constitution` | `.specify/memory/constitution.md` | overwrite (`constitution.md:125`) | ⚠️ |
| `taskstoissues` | GitHub issues | dedup por task ID (`taskstoissues.md:67-69`) | ✅ idempotente |

### Las tres trampas

**1. `specify` no edita: bifurca.**
Crea `specs/NNN-...` nueva y reescribe `.specify/feature.json`, que es de donde
`plan`/`tasks` sacan la ruta. Re-correrlo para "arreglar la spec" redirige el
pipeline entero a otra carpeta y deja la anterior huérfana.
**Para corregir una spec existente: `clarify`.**

**2. `plan` es mitad y mitad.**
`setup-plan.sh` salta la copia del template si `plan.md` existe, así que el
agente edita el archivo viejo y las secciones obsoletas sobreviven en silencio.
Pero `research.md` / `data-model.md` / `contracts/` sí se regeneran.
**Al re-planificar hay que decirle explícitamente qué secciones de `plan.md`
quedaron invalidadas** — no lo detecta solo.

**3. `tasks` destruye el progreso.**
A diferencia de `setup-plan.sh`, `setup-tasks.sh` no tiene guarda: regenera
`tasks.md` desde el template. Como `implement` guarda el avance marcando `[X]`
ahí mismo, re-correr `tasks` después de un implement parcial **borra el registro
de qué ya está hecho.**

> **`converge` es el reemplazo append-only de re-correr `tasks`.**
> No es un comando de pulido final: es la puerta de vuelta segura una vez que
> cruzaste la línea de `implement`.

---

## 2. Mapa de re-entrada

| Estás en… | El cambio toca… | Corre | No corras |
|---|---|---|---|
| spec escrita, sin plan | requisitos / alcance | `clarify` | `specify` (bifurca) |
| plan hecho, sin tasks | requisitos | `clarify` → `plan` | — |
| plan hecho, sin tasks | solo decisión técnica | `plan` (dile qué secciones invalidar) | — |
| tasks hecho, **sin implement** | lo que sea | `clarify`/`plan` → `tasks` | — |
| **implement parcial** | requisitos | `clarify` → `plan` → **`converge`** | 🔴 `tasks` |
| implement parcial | nada del intent; el código se desvió | `converge` | — |
| no sabes qué está inconsistente | — | `analyze` primero (read-only) | — |

**Regla:** el delta entra por la **capa más alta que toca**; todo lo de abajo
queda invalidado hasta que apruebes. Cruzar la línea de `implement` cambia la
herramienta de propagación de `tasks` a `converge`.

### Límite de `converge`

Solo **agrega** trabajo faltante; nunca borra código (`converge.md:156`). Si el
cambio *invierte* una premisa, hay código ya escrito que ahora está **mal**, no
**incompleto**. Converge lo reporta para tu conocimiento, pero necesitas tasks de
remoción explícitas. En ese caso congela `plan.md`/`tasks.md` y reconcilia la
spec primero.

---

## 3. Presupuestos que hacen que priorizar importe

Estos comandos tienen tope interno. Decirles qué conflictos son duros no es
adorno: es asignar un recurso escaso.

| Comando | Tope | Consecuencia |
|---|---|---|
| `clarify` | **5 preguntas** máximo (`clarify.md:129`) | sin prioridad, gasta 2 en trivialidades |
| `specify` | **3 marcadores** `[NEEDS CLARIFICATION]` (`specify.md:128`) | los ambiguos sobrantes se resuelven por supuesto |

---

## 4. Gates que ya tienes (harness)

Si el repo tiene `.specify/extensions.yml` del harness, ya hay orden forzado:

| Hook | Efecto |
|---|---|
| `before_plan` → `speckit-clarify` | no se planifica sin clarificar |
| `after_tasks` → `speckit-analyze` | no se promueve con inconsistencias CRITICAL |
| `before_implement` → `harness-gate` | exige plan `active` + `analyzed` |
| `after_implement` → `harness-verify` | corre el `verify:` del plan |

Esos hooks controlan el **orden entre etapas**. No detectan **deriva del repo de
contexto** — eso es lo que hace `putils speckit check`.
