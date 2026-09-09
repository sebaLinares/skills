---
name: pub
description: Publica un archivo HTML local en el origen tailnet del Mac Mini con `putils pub` y devuelve una sola URL pegable, para abrirla desde el iPhone u otro dispositivo del tailnet. Usá esta skill cuando el usuario escriba /pub, adjunte un `.html` y pida verlo en el teléfono, diga "publicá esto", "publicá este html", "quiero verlo en el iPhone", "pasámelo al celular", "publish this html", "put this on the tailnet", o mencione un archivo bajo `~/.claude/uploads/` o la carpeta `pub-inbox` de iCloud. También cuando pida borrar publicaciones viejas (`--gc`). NO la uses para deploys a internet, GitHub Pages, Cloudflare, Tailscale Funnel, ni para servir un directorio entero o levantar un servidor: solo publica un archivo HTML estático que ya existe.
---

# pub

Publica **un** archivo HTML que ya existe en disco al origen tailnet de la Mac
Mini, llamando a `putils pub`. Devuelve una URL y nada más.

No es un servidor, no es un deploy genérico, no es un sitio. Es un llamador del
binario.

**La skill no implementa nada.** `putils pub` ya valida el hostname, la frontera
de Tailscale Serve, la salud del `pub-server`, la materialización de
placeholders de iCloud, la colisión de slug y `--force`. No repliques ninguna de
esas validaciones ni intentes arreglarlas desde acá.

## Cuándo

El usuario adjuntó un HTML y quiere verlo en el teléfono; te pasó una ruta y
dice "publicá esto"; el archivo está bajo `~/.claude/uploads/` o en la carpeta
`pub-inbox` de iCloud Drive.

## Paso 1 — Muro de dominio (antes de tocar el binario)

La skill se instala en todas las máquinas y **las tres sesiones Brain la ven**
(Personal, Cencosud, Electromática). El binario chequea el hostname de la Mini,
pero **no distingue entre las tres**. El muro lo pone esta skill.

Aplicá la tabla de routing de vaults del **paso 1 de `wrap/SKILL.md`** (no la
copies acá: leela ahí, es la única copia). Resolvela sobre **dos** paths, y los
dos tienen que dar el mismo resultado:

1. la ruta del HTML a publicar;
2. el contexto de la sesión: `git rev-parse --show-toplevel 2>/dev/null || pwd`.

- Cualquiera de los dos resuelve a **`cencosud`** o **`electromatica`** → **PARÁ**.
  No ejecutes `putils pub`. Decí que ese material no sale por el origen tailnet
  personal y terminá ahí.
- Los dos resuelven a **`slinaresl`** → seguí. (Incluye `~/Notes/_shared`,
  `~/Documents/projects/…` que la tabla manda a `slinaresl`, `~/.claude`,
  `~/.agents` y este repo.)
- La tabla **no matchea** → preguntá de qué dominio es el archivo. No elijas.

Que el usuario haya escrito `/pub` **no saltea este paso**. La invocación
explícita dice qué hacer, no de qué dominio es el contenido.

## Paso 2 — Resolver la ruta

En este orden:

1. **Adjunto de la sesión** — `~/.claude/uploads/<sesión-actual>/`. Es donde la
   app de Claude deja los archivos adjuntos.
2. **Ruta que dio el usuario** — usala tal cual.
3. **iCloud** — `~/Library/Mobile Documents/com~apple~CloudDocs/pub-inbox/`. Es
   el camino de respaldo cuando no hay adjunto de sesión. La skill **no** vigila
   esa carpeta; solo lee de ahí si el usuario apunta ahí.

Si hay **más de un** `.html` candidato, listalos y **preguntá cuál**. No elijas
por el usuario. Si no hay ninguno, decilo y pará.

`putils pub` toma exactamente un path. Un pedido de publicar varios archivos son
varias invocaciones, cada una con su `--name`.

## Paso 3 — Resolver `--name`

**Siempre pasá `--name`** en el camino de publicar. Sin él el slug sale del
basename, y el basename de un adjunto trae el prefijo hash de la app de Claude
(`e185d75d-plan_entrenamiento_tabs.html`) — ese hash terminaría en la URL.

En este orden:

1. **El usuario nombró la cosa** ("publicá el plan de entrenamiento") →
   normalizá ese nombre a slug.
2. **No lo nombró** y el path matchea la convención de uploads de Claude —
   `~/.claude/uploads/<sesión>/<8 hex>-<resto>.html`, o sea basename que empieza
   con `^[0-9a-f]{8}-` — → `--name` = `<resto>` (sin `.html`) normalizado.
   **Esto vale solo para uploads de Claude.** Nunca le recortes un prefijo a un
   nombre que no matchee ese patrón: podría ser parte del nombre real.
3. **Ni una cosa ni la otra** → **preguntá** cómo se debería llamar. No publiques
   con un slug inventado.

Normalizar = minúsculas, sin tildes ni `ñ`, cualquier corrida de caracteres que
no sea `[a-z0-9]` se vuelve un `-`, sin `-` al principio ni al final, sin `-`
repetidos.

El resultado **tiene que** matchear `^[a-z0-9]+(?:-[a-z0-9]+)*$` — es lo que el
binario acepta en `--name`. Si después de normalizar no matchea (quedó vacío,
era solo símbolos), preguntá.

**Reservado: `index`.** Si el slug resuelto sería `index`, pedí otro nombre.

## Paso 4 — Invocar

```bash
putils pub <ruta> --name <slug>
```

Agregá `--force` **solo** si el usuario pidió explícitamente pisar una
publicación que ya existe.

Si `putils` no resuelve (`command not found`), el binario está en
`~/go/bin/putils` — usá esa ruta absoluta. No busques otro publisher.

Sale **una URL** por stdout. Reportala tal cual, pegable. Nada más: no la
adornes, no la recortes, no la reconstruyas a mano.

## Paso 5 — Errores

Código de salida ≠ 0 → **mostrá lo que imprimió el binario** y pará.

No hay plan B. No levantes un servidor, no copies el archivo a mano, no toques
Tailscale, no inventes la URL. Si el binario se plantó — máquina equivocada,
slug colisionado, `pub-server` caído — el mensaje dice qué pasa; pasáselo al
usuario y esperá instrucciones.

## `--gc`

Solo si el usuario **pide** limpiar publicaciones viejas:

```bash
putils pub --gc <días>
```

Borra las publicaciones más viejas que esa cantidad de períodos de 24 horas.
Acá **no** va `--name`. No lo ofrezcas de onda, no lo corras automáticamente, no
lo agendes.
