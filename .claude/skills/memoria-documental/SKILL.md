---
name: memoria-documental
description: Como escribir la memoria del estudio (definiciones por agente, trazabilidad, indice, catalogo de patrones) sin duplicar ni desincronizar datos. Usar al cerrar cualquier etapa del flujo Discovery -> Cierre, o al tocar docs/.
paths:
  - "docs/**/*.md"
  - "docs/**/*.yml"
---

# Memoria documental: donde va cada cosa

Fuentes: `.github/instructions/29-trazabilidad-conversacion.instructions.md`, `39-presupuesto-contexto.instructions.md` (seccion 6) y `00-operativa-global.instructions.md`.

## Un dato, un lugar

| Dato | Unico lugar |
|---|---|
| Estado del proyecto (activo/cerrado/produccion, repo) | `docs/indice.md` |
| Owner, hosting, `ruta_repositorio` | `docs/<proyecto>/metadata.md` |
| Estado vigente de cada etapa | `docs/<proyecto>/definiciones/<n>-<agente>.md`, seccion "Definiciones vigentes" |
| Historial de decisiones | `docs/<proyecto>/trazabilidad.md` |
| Patron reutilizable | `docs/patrones/catalogo.yml` |
| Numeros de estimacion | `docs/calibracion/dataset.yml` |
| Regla preventiva cross-proyecto | `.github/instructions/32-estandares-qa-implementador.instructions.md` |
| Sprint / CR / modulo ya cerrado | `docs/<proyecto>/definiciones/historial/` (puntero de 1 linea en el archivo vigente) |
| Indice plano de un catalogo (entrada de los agentes) | `docs/qa/cat_resumen.txt`, `docs/patrones/cat_resumen.txt` — generados: `python scripts/contexto.py resumenes` |
| Clientes, su plan y su recurrente | `docs/olvidata/clientes.md` — **generado** del CRM (`scripts/olvidata_datos.py`) |
| Leads abiertos y el embudo | `docs/olvidata/pipeline.md` — **generado** |
| Recurrente real por mes y el umbral del Ministerio | `docs/olvidata/metricas.md` — **generado** |
| Precio de catalogo o de un plan | `docs/olvidata/precios.md` (deja linea en `docs/olvidata/trazabilidad.md`) |
| Regla comercial vigente | `docs/olvidata/reglas-comerciales.md` (ID `COM-NNN`, 3 digitos) |
| Que se puede afirmar de un cliente | `docs/olvidata/casos.md` |
| Costos de hosting, IA y herramientas | `docs/olvidata/costos.md` |
| Pregunta abierta esperando a Joaquin | `docs/olvidata/decisiones.md` (ID `DEC-NNN`) |
| Reglas de marca y lenguaje | `docs/olvidata/marca/MARCA.md` (movido de BotPublicitario el 2026-10-15) |

Si un dato ya existe en otro archivo, **referencialo, no lo copies**. Toda copia se desincroniza: la auditoria del 2026-09-15 encontro el factor de Build desactualizado en 4 archivos a la vez.

## Regla de edicion (vigente vs. historial)

- `definiciones/*.md` tiene **2 zonas**: "Definiciones vigentes" (se edita in-place, reemplazando el dato viejo) e "Historial de ajustes" (unica zona que crece por append, una linea por cambio).
- Nunca agregar una seccion fechada nueva al lado de la vieja, ni dejar una nota tipo "correccion: en realidad es X" junto al dato viejo.
- `trazabilidad.md` es log, no estado: una entrada por decision, formato `### <fecha> - <agente>` con Etapa / Cambio / Motivo / Impacto en capas / Riesgos. Si algo describe el estado actual, va a `definiciones/` o `metadata.md`.
- **Techo de 150 KB por archivo** (`definiciones/*.md` y `trazabilidad.md`): al cerrar la etapa, los sprints/CR/modulos cerrados se archivan con `python scripts/archivar_memoria.py <archivo> --aplicar`, que los mueve agrupados (por mes o por modulo) a `historial/` y deja un puntero de una linea por grupo. `doctor.py` lo vigila.
- El motivo del techo no es prolijidad: cada KB de memoria vieja es contexto que el agente gasta al arrancar en vez de usarlo para pensar el trabajo. `6-qa.md` de marihogar llego a 686 KB (~170k tokens de arranque).
- Lo archivado **no se toca ni se reedita**: es historia cerrada. El estado vigente vive siempre en el archivo de origen.

## Antes de cerrar una etapa

Correr `python scripts/doctor.py`. Si aparece un ERROR, es una contradiccion real entre archivos (un precio, un estado, un ID duplicado) y se arregla antes de cerrar. Los avisos son deuda: se atienden cuando se pueda, no bloquean.

## Memoria de negocio (`docs/olvidata/`)

Los tres primeros de la tabla son **snapshots generados**: se regeneran con
`python scripts/olvidata_datos.py todo`, que lee el CRM productivo. Editarlos a mano es tirar el
cambio a la basura en la proxima corrida — lo que el CRM no sabe va en `docs/olvidata/datos-manuales.yml`.

El resto se edita a mano, con dos reglas que `doctor.py` controla: todo `COM-NNN` citado existe en el
catalogo, y todo cambio de `precios.md` deja linea en `docs/olvidata/trazabilidad.md`.
