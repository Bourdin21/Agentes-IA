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
- **Reset de contexto, no compactacion (obligatorio desde 2026-09-25).** Ver seccion 4b.

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

### 4a. El estado de lo que vas a delegar se releva contra el arbol, no se arrastra del documento (agregado 2026-10-07)

**Medido en la-platense: tres briefs consecutivos arrancaron de una premisa falsa**, y las tres veces el subagente gasto trabajo en descubrirlo antes de poder empezar:

1. Un brief declaro **no construidos 6 sitios que ya estaban escritos** (el commit anterior decia lo contrario porque lo redacto el orquestador a ciegas, sin releer el arbol).
2. Un brief dio **`LP-014` por abierto en produccion, con numeros de linea** — estaba cerrado desde diez dias antes, con PASS de QA. Los numeros de linea salian del documento de arquitectura que habia relevado el defecto semanas atras, no del archivo actual.
3. Un brief pidio **corregir un XML-doc que ya estaba corregido**.

**La causa es siempre la misma:** el brief se escribe citando el documento que *descubrio* el problema, y ese documento es una foto del codigo del dia en que se escribio. **Un numero de linea, un "esta abierto" o un "falta hacer X" en un brief son afirmaciones sobre el codigo de HOY**, y el documento no las puede sostener.

**Reglas:**

- Antes de afirmar en un brief que algo esta roto, abierto o sin construir, **verificalo contra el arbol de trabajo en ese momento** — un `grep` del sintoma, un `git log` del archivo, o el estado del parte en `6-qa.md`. Cuesta segundos; el subagente lo paga en minutos y en contexto.
- Si no lo verificaste, **decilo con su fuente y su fecha** en vez de afirmarlo: *"QA midio esto en el commit `X` el dia `Y` — verificalo contra el arbol antes de tocar"*. Un brief honesto sobre lo que no sabe es util; uno que afirma de mas hace que el subagente arranque resolviendo una contradiccion.
- **Nunca cites numeros de linea de un documento de etapa previa.** Si hacen falta, sacalos del archivo en el momento de escribir el brief.
- Lo mismo vale para la **evidencia** que el brief declara como linea base. En la-platense se cito un *"153 OK / 0"* como no-regresion durante varias rondas y **no se reproducia**: el arnes necesitaba que el reloj acompaniara y que su limpieza no muriera. Una linea base se cita **con la fecha en que se midio**, y si no se midio en el arbol actual, se mide o se declara como no verificada.

**Dos formas que sobreviven a la regla de arriba, medidas en la-platense el 2026-10-07** (un brief que SI verifico contra el arbol y aun asi llevo dos premisas falsas):

- **La medicion propia mide de mas.** El brief afirmo "hay 19 migraciones" porque conto `ls Migrations/*.cs | grep -v Designer | wc -l` — y eso **incluye `AppDbContextModelSnapshot.cs`, que no es una migracion**. Son 18. Verificar contra el arbol no alcanza si el comando no mide lo que uno cree: **cuando el numero importa, mira la salida, no solo el total.** Un `wc -l` esconde exactamente el elemento que no corresponde.
- **El dato heredado de otro agente se cita como hecho propio.** El mismo brief afirmo que en dev habia "4 filas `ZZ%`, catalogo legado real, no residuo". Salia de la traza de QA del lote anterior, **marcada alli como verificacion independiente**. Al chequearlo, **no hay ninguna fila con prefijo `ZZ`**: eran coincidencias internas de `%ZZ%` en nombres de catalogo real. El reporte de un subagente es **evidencia de segunda mano**: se cita **con su fuente** ("QA reporto X en el lote N") o se vuelve a medir. Nunca se lo asciende a hecho del brief, porque el proximo agente lo va a tratar como dato duro y nadie va a saber de donde salio.

**La tercera forma, y la mas peligrosa porque no se siente como una afirmacion sobre el codigo: la premisa falsa por INFERENCIA.** Medida en la-platense el 2026-10-07. El brief decia: *"R18 dice que una nota de credito no resta del pendiente a facturar, por lo tanto `FacturacionParcialService` no cambia en este lote"*. La regla era correcta y la conclusion **exactamente al reves**: una NC es una fila mas de la misma tabla de comprobantes, con cantidades **positivas**, y los tres lectores del "ya facturado" sumaban todo comprobante vivo — asi que **dejar el codigo sin tocar no respetaba la regla, la rompia** (acreditar 2 de 5 unidades facturadas dejaba el facturado en 7 sobre una venta de 5: pendiente negativo y el tope rechazando refacturaciones legitimas). Para que una regla de negocio "no cambie nada" **hay que verificar que el codigo ya la cumpla**, no deducirlo del enunciado.

Reglas:

- **Un "por lo tanto X no cambia" es una afirmacion sobre el codigo**, con el mismo peso que "X esta roto", y se verifica igual: se abre el archivo y se mira si el invariante ya se cumple. La inferencia desde la regla de negocio **no es evidencia**.
- Cuando un brief declara que algo **queda fuera de alcance porque no hace falta tocarlo**, ese es justamente el lugar donde conviene un grep: el subagente va a confiar en esa frase y **no va a mirar**. Un alcance recortado por inferencia es la forma mas barata de dejar un defecto adentro del entregable.
- Sintoma a vigilar: el brief encadena *regla de negocio → conclusion tecnica* sin ningun archivo citado en el medio.
- **Variante medida el 2026-10-07: la regla del PROYECTO citada de memoria, con el alcance corrido.** El brief dijo *"nunca escribas `Producto.Stock` directo: el proyecto tiene un unico escritor y se respeta"*. El principio existe, pero **el unico escritor que el proyecto defiende es el de la TABLA del ledger, no el de la columna** — `IMovimientoStockService` declara explicitamente que no toca `Producto.Stock`. Obedecer el brief al pie de la letra **dejaba el stock sin mover**. Una regla propia tambien se cita abriendo el archivo: el riesgo no es inventarla, es **correrle el alcance** — y en esa forma suena igual de autorizada.

**Por que esto esta en la instruccion del presupuesto de contexto y no en otro lado:** es el mismo problema que el resto de este documento. Un brief con premisas falsas no es un error de prolijidad, es **contexto equivocado**, y cuesta mas caro que el contexto de mas — el subagente no solo lee algo que no servia, sino que razona sobre un mundo que no existe.


## 4b. Reset de contexto entre etapas (regla dura, no sugerencia)

Hasta el 2026-09-25 esto era una recomendacion ("si se siente saturado, conviene cerrar"). Pasa a ser mecanismo, por dos motivos medidos en sistemas de agentes largos:

1. **Comprimir el historial no alcanza.** Un resumen del contexto conserva las conclusiones y tira el detalle de dominio; el agente sigue arrastrando la etapa anterior, mas pobre.
2. **Ansiedad de contexto.** Con la ventana llenandose, el modelo **cierra el trabajo antes de tiempo**: acorta el alcance, da por probado lo que no probo, entrega "listo" a medio camino. No lo declara — se nota en el resultado. Es la falla mas cara porque se parece a terminar.

Reglas:

- **Toda etapa cierra su archivo de definicion antes de pasar a la siguiente** (ya estaba en `CLAUDE.md`) **y la siguiente arranca en un contexto nuevo**, cargado desde ese archivo + el brief de la seccion 4. No se continua una etapa nueva en el contexto de la anterior "porque ya tiene el contexto cargado" — eso es exactamente el problema, no una ventaja.
- **Prohibido compactar para seguir.** Si la ventana se llena en el medio de una etapa: se cierra lo hecho como artefacto (definicion, parte de defecto, reporte de lote), y se rearranca limpio desde ahi. El estado vive en el disco, no en la ventana.
- **Sintomas que obligan al reset inmediato**, sin esperar al cierre: respuestas que repiten lo ya dicho, una regla del arranque que se olvido, alcance que se achica solo, "para no extenderme" sin que nadie lo haya pedido.
- **El costo es real y se acepta:** rearrancar cuesta releer el artefacto y algo de latencia. Es mas barato que una etapa cerrada de mas con trabajo sin hacer.
- **QA por lotes (seccion 5) ya es esto aplicado.** La regla generaliza el mismo mecanismo al resto del flujo.

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
- El archivo vigente queda con: cabecera + `## Definiciones vigentes` (entradas con id, sin marca `superada-por`) + el ultimo sprint/CR + `## Historial de ajustes` con **una linea y un puntero por bloque archivado**.
- **El techo se sostiene archivando, no reescribiendo.** Una entrada superada se marca `superada-por: <id>` y se archiva; no se pisa su texto ni se resume para hacer lugar. Reescribir para achicar es la forma mas cara de perder memoria: el archivo queda chico y nadie sabe que se fue. Ver `29-trazabilidad-conversacion`, "Regla de edicion: entradas con id".
- Esto no es opcional ni cosmetico: es la unica razon por la que el arranque de un agente se mantiene bajo su techo con el paso de los sprints. Ver tambien la regla vigente/historial de `29-trazabilidad-conversacion`.

## 7. Higiene durante la corrida

- No re-leer un archivo ya leido en la misma sesion.
- `grep` antes de `cat`, siempre.
- La salida del agente es la salida minima de su `.agent.md`: no volcar cuerpos de archivos leidos ni citar bloques largos "para mostrar contexto".
- Al cerrar, actualizar la memoria **agregando la entrada con id** que corresponda y marcando `superada-por` la que reemplaza (nunca apilando una seccion con fecha al lado de la vieja, ni pisando el texto viejo — ver `29-trazabilidad-conversacion`).

## 8. Traza de corrida (observabilidad del *durante*)

`contexto.py presupuesto` mide lo que cargas **antes** de empezar. No habia nada que midiera lo que pasa **despues**: cuantos reintentos hubo, que criterio fallo, que regla hubo que releer porque no estaba en el arranque. Sin ese dato, cada ajuste a una instruction es intuicion: no se puede saber si mejoro o empeoro al agente.

Al cerrar su etapa, todo agente registra la traza:

```
python scripts/traza.py registrar --proyecto <proyecto> --etapa <etapa>   [--lote N] --reintentos N --criterios-fallados "ID,ID"   --reglas-releidas "32#combos,30" [--arranque-kb N] [--nota "..."]
```

El script agrega el bloque de <= 5 lineas a `docs/<proyecto>/trazabilidad.md` **y** una linea al indice consultable `docs/trazas/trazas.tsv`.

Que mirar despues (`python scripts/traza.py resumen`):

| Señal | Que significa | Que se hace |
|---|---|---|
| La misma regla releida en varias corridas | esta mal ubicada en la carga de arranque del rol | subirla al arranque, o resumirla en la skill del rol |
| El mismo criterio fallando en proyectos distintos | es un patron, no un bug del proyecto | item nuevo en `regresiones-manuales.yml` o regla en `32` |
| Reintentos altos en una etapa concreta | el brief de hand-off de esa etapa es flojo | corregir la seccion 4, no compensar cargando mas |
| Arranque real por encima del techo | la carga declarada del rol crecio de nuevo | volver a aplicar carga por indice (seccion 2) |

Una traza **no es un reporte**: son 5 lineas mecanicas. Si cuesta escribirla, esta mal usada.

Uso obligado: es la materia prima de la suite de evals (`40-evals-del-harness.instructions.md`). Los casos de eval salen de fallos reales registrados, no inventados.
