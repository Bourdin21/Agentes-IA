---
description: Presupuesto de contexto por agente, carga por indice, techo de los archivos de memoria y hand-off comprimido entre etapas. Aplica a todo agente del estudio.
applyTo: "**"
---

# 39 - Presupuesto de contexto (obligatorio para todo agente)

## Por que existe

Medicion del 2026-09-25 (`python scripts/contexto.py presupuesto`):

- El arranque del **QA sobre marihogar**, siguiendo su lista de carga al pie de la letra, eran **2,05 MB ≈ 510k tokens** (definiciones 1+2+5, `6-qa.md` de 686 KB, `regresiones-manuales.yml` de 428 KB y 8 instructions) **antes de abrir una sola linea de codigo**.
- El arranque del **implementador sobre marihogar**: **621 KB ≈ 155k tokens**.
- El paso "escanear `docs/*/definiciones/5-implementador.md`" pedia literalmente **2,15 MB ≈ 537k tokens**.

Media ventana de contexto gastada en historia ajena a la tarea es exactamente la causa de la degradacion del razonamiento: el modelo deja de razonar sobre el problema y empieza a promediar lo que leyo. **Un agente que arranca saturado no piensa peor por el modelo, piensa peor por lo que le cargamos.**

Esta instruccion define el techo, y como respetarlo sin perder ninguna regla del estudio.

## 1. Techo de arranque por agente

El techo de cada rol sale de **cuantos documentos de etapa previa necesita para hacer su trabajo**, no de una fraccion arbitraria de la ventana:

| Agente | Techo de arranque | Razon |
|---|---|---|
| analista-funcional | **40k tokens (~160 KB)** | arranca del pedido del cliente: su memoria vigente y poco mas |
| disenador-funcional | **40k tokens** | analisis del alcance + su memoria vigente |
| documentador | **40k tokens** | la seccion del sprint en `5-implementador` y `6-qa` |
| arquitecto-mvc | **50k tokens (~200 KB)** | analisis + diseño + su memoria vigente |
| presupuesto-mvc | **60k tokens (~240 KB)** | analisis + diseño + arquitectura + dataset + su memoria |
| implementador-dotnet, implementador-astro-front | **60k tokens** | el resto de la ventana es para el codigo |
| qa-mvc | **60k tokens** | el resto de la ventana es para navegar y probar |

Reglas duras:

- El techo se mide **antes** de leer codigo o navegar. Lo que se lee despues (archivos del repo del sistema, resultados de build, snapshots de Playwright) es trabajo, no arranque.
- Si la carga declarada de un agente excede su techo, **no se carga entera**: se aplica carga por indice (seccion 2). No se elimina la regla, se posterga su cuerpo.
- Verificacion: `python scripts/contexto.py presupuesto <proyecto>` imprime el arranque real de cada agente contra su techo.
- Si en medio de una etapa el contexto se siente saturado (respuestas que repiten, reglas que se olvidan), **cerrar la etapa y arrancar de nuevo con el brief de la seccion 4** es mas barato que seguir.

## 2. Carga por indice (como leer un archivo grande)

Procedimiento, siempre en este orden:

1. **Indice primero:** `python scripts/contexto.py indice <alias>` — o, a mano, `grep -n '^## ' <archivo>`.
2. **Leer solo las secciones cuyo titulo toca lo que estas haciendo**, por rango: `sed -n '<desde>,<hasta>p' <archivo>`.
3. **Nunca** `cat` / lectura completa de un archivo de la tabla de abajo.

| Fuente grande | Que se carga en su lugar |
|---|---|
| `32-estandares-qa-implementador` (69 KB, 45 reglas) | indice de `## ` + solo las reglas que toca el cambio. Atajo: skill `estandares-qa` (las mas reincidentes ya resumidas) |
| `27-presupuesto-parametros` (69 KB) | `docs/calibracion/dataset.yml` (rangos y cierres, estructurado) + indice de `## `. La prosa solo para el contexto de un cierre puntual |
| `25-frontend-design-system` (26 KB) | indice de `## ` / skill `design-system` |
| `34-integracion-afip-arca`, `35-pantalla-control-stock`, `37-servicios-externos-fiscales` | indice de `## `, y **solo si el proyecto usa esa capacidad** |
| `26-checklists` (10 KB) | el checklist del tipo de modulo que se esta haciendo, no los 5 |
| `docs/qa/regresiones-manuales.yml` (428 KB, 107 items) | `docs/qa/cat_resumen.txt` (24 KB, 1 linea por bug). El item completo del YAML se lee **solo** cuando ese bug aplica al sistema bajo prueba |
| `docs/patrones/catalogo.yml` (184 KB, 45 patrones) | `docs/patrones/cat_resumen.txt` (1 linea por patron). La entrada completa, solo la del patron que se va a reutilizar |
| `docs/*/definiciones/*.md` de **otros** proyectos (7,5 MB en total) | nunca por cuerpo: ver seccion 3 |
| `definiciones/` del proyecto propio | bloque `## Definiciones vigentes` + el ultimo sprint/CR. Los anteriores viven en `definiciones/historial/` y se leen solo si el trabajo los toca |

Las instructions chicas (`00`, `01`, `10`, `20`–`24`, `28`, `29`, `30`, `31`, `33`, `36`, `38`, esta) se cargan completas: suman poco y son reglas base.

## 3. Escaneo de reutilizacion cross-proyecto (reemplaza el "escanear docs/*/definiciones/")

La regla de reutilizacion **no cambia**: sigue siendo obligatoria en Diseno, Arquitectura e Implementacion. Lo que cambia es el costo. El escaneo literal vale 2,1 MB; esta secuencia vale menos de 30 KB:

1. **`docs/patrones/cat_resumen.txt`** — una linea por patron (id, nombre, categoria, proyecto de origen). Es el primer y obligatorio lookup.
2. **Si hay match:** leer esa entrada completa en `catalogo.yml` (solo esa) y despues el codigo real en `ruta_repositorio` del `metadata.md` del proyecto de origen. Si la entrada tenia `pendiente_verificar: true`, confirmar la ruta y sacar el flag.
3. **Si no hay match:** grep dirigido por el sustantivo del dominio sobre el historial, sin abrir nada todavia:
   `grep -ril "<entidad o flujo>" docs/*/definiciones/`
   y leer **solo** el archivo que matchea, **solo** la seccion del match (`grep -n` para ubicarla, `sed -n` para leerla).
4. **Recien si eso falla:** declarar "sin antecedente en el historial" en la salida y construir nuevo — y agregar el patron al catalogo antes de cerrar la etapa.

Prohibido leer archivos enteros del historial "por si acaso". Un archivo del historial sin match en el paso 3 no se abre.

## 4. Hand-off comprimido entre etapas

El orquestador (y cualquier agente que delegue) **no** dice "lee las definiciones del proyecto". Pasa en el prompt del subagente un **brief de a lo sumo 2 paginas** con:

1. Proyecto, repo del sistema (`ruta_repositorio`) y rama.
2. Que se aprobo: el CR/feature en 3-10 lineas, no el documento entero.
3. Criterios de aceptacion, textuales, solo los de este alcance.
4. Decisiones ya tomadas que el subagente no debe re-litigar (entidades, estados, permisos, patron reutilizado con su id `PAT-xxx`).
5. Archivos/modulos que se espera tocar, si ya se sabe.
6. Punteros a lo que queda por demanda: `definiciones/<archivo>.md` + numero de linea de la seccion, no el archivo.

El subagente **puede** ampliar leyendo esos punteros, pero arranca del brief. Si el brief no alcanza, el problema es el brief: se corrige y se vuelve a delegar, no se compensa cargando todo.

## 5. QA por lotes

Una corrida de QA sobre un sistema con muchos modulos **no se hace en un solo contexto**:

- Lotes de **a lo sumo 3 modulos** (o 1 modulo si es financiero/integracion), cada lote en **su propio subagente**, con su propio brief.
- Cada lote devuelve un reporte compacto (**<= 40 lineas**): PASS/FAIL/BLOCKED por criterio, defectos con id, auto-fixes aplicados.
- El orquestador consolida los reportes de lote en `6-qa.md`. Nadie mantiene los N lotes en un mismo contexto.
- El chequeo de reglas nuevas (`33-verificacion-automatizada-qa`) se hace **una vez**, en el lote 1, y su resultado se pasa como dato a los lotes siguientes.

Motivo: un lote con contexto limpio encuentra bugs que el lote 12 de una corrida monolitica ya no ve.

## 6. Techo de los archivos de memoria

- Ningun archivo de `docs/<proyecto>/definiciones/` ni `docs/<proyecto>/trazabilidad.md` supera **150 KB**. `doctor.py` lo reporta como **ERROR**, no como aviso.
- Al cerrar una etapa, los sprints/CR ya cerrados se mueven a `docs/<proyecto>/definiciones/historial/` (o `docs/<proyecto>/historial/` para trazabilidad) con:
  `python scripts/archivar_memoria.py <archivo>` (dry-run; `--aplicar` para hacerlo)
- El script agrupa lo archivado por **mes** o por **modulo** (`M08`), segun como el archivo identifique su unidad de trabajo, y nunca pisa un archivo de historial existente. `--techo 70` poda mas agresivo: sirve cuando el bloque vigente acumulo modulos ya entregados de sprints viejos.
- Si el script avisa **PARCIAL**, archivo lo que podia y el resto del peso esta en secciones que no declaran sprint/CR/modulo: ahi hace falta curaduria a mano (decidir que del bloque vigente ya es historia). Ningun script puede tomar esa decision por nosotros.
- El archivo vigente queda con: cabecera + `## Definiciones vigentes` + el ultimo sprint/CR + `## Historial de ajustes` con **una linea y un puntero por bloque archivado**.
- Esto no es opcional ni cosmetico: es la unica razon por la que el arranque de un agente se mantiene bajo su techo con el paso de los sprints. Ver tambien la regla vigente/historial de `29-trazabilidad-conversacion`.

## 7. Higiene durante la corrida

- No re-leer un archivo ya leido en la misma sesion.
- `grep` antes de `cat`, siempre.
- La salida del agente es la salida minima de su `.agent.md`: no volcar cuerpos de archivos leidos ni citar bloques largos "para mostrar contexto".
- Al cerrar, actualizar la memoria **editando** el bloque vigente (nunca apilando una seccion nueva al lado de la vieja).
