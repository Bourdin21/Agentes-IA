<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-10-03 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M27 (1 bloques archivados)

- M27 — Una sola puerta para armar un agente, y una tarea que no se corta

---

# M27 — Una sola puerta para armar un agente, y una tarea que no se corta

Estado: **frentes 1, 2 y 6 implementados 2026-10-01; pendiente de QA; 3 commits locales (`625b30f`, `43dce94`,
`f7103cf`), sin push y sin deploy.** Los frentes 3 (documentos) y 4 (menú) los hizo otro implementador en paralelo.
Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `0ba8ef6`. Entrada: análisis M27 (H1..H6, RF-M27-01..27,
D-M27-a..e), diseño (D-M27-1..17, P-M27-01..10) y arquitectura (A-M27-1..16, RT-M27-01..08). Gate: definiciones 1, 2 y 3
aprobadas; presupuesto omitido (proyecto personal).

### Escaneo de reutilización
`docs/patrones/cat_resumen.txt` → **PAT-030, PAT-032, PAT-029**, los tres de este mismo proyecto, como ya había
anticipado el diseñador. **Ningún patrón nuevo y nada que traer de otro repo:** ningún otro proyecto del estudio tiene
conversación con un modelo. Del propio repo se reusó todo el camino de aplicar una propuesta (M7b/M15) y el de crear un
instructivo (M14): no se escribió una sola aplicación de propuesta nueva, se le agregaron dos campos a la que existía.

### Lo que hay que saber antes de leer el resto

**El frente 2 no se arregló con código de motor: se arregló con un número, y el número se midió.** Dos corridas
controladas contra la API (2026-10-01), misma conversación de 4 turnos con dos planillas de ~470 filas leídas por
herramienta, 57.580 tokens de entrada —la misma forma que la tarea 17 de producción, que iba de 56.093 a 60.298—,
`max_tokens` 16000 y `effort` medium:

| | `task_budget` = 64.000 (producción) | `task_budget` = 400.000 |
|---|---|---|
| tokens de salida en total | **3.417** | **42.884** |
| tokens de pensamiento | 62 | 39.166 |
| las 11 partidas no conciliadas plantadas | **no encontró ninguna** | **las 11**, con fecha, comprobante e importe |
| qué dijo | «ya no tengo capacidad disponible en esta sesión» | «terminé el cruce completo de las ~470 líneas de cada lado» |
| entregable | hallazgos parciales y un pedido de cierre | conciliación completa + asientos de ajuste propuestos |

Con 64.000, en los cuatro turnos dijo textualmente *«por restricción de espacio»*, *«tokens agotados»*, *«no tengo
margen de capacidad restante en esta sesión»* y *«ya no tengo capacidad disponible»*. Es la reproducción exacta del
comportamiento de la tarea 17, con el número como única variable. **El diagnóstico de A-M27-16 es correcto.**

**El mecanismo, con la precisión que corrigió la auditoría:** el presupuesto **nunca se agotó**. `task_budget` cuenta lo
que el modelo genera más lo que lee por herramienta **en ese turno** —unos 21k en el primero y casi nada en los otros
tres—, no la historia que se reenvía. O sea que el modelo **proyectó** que no le iba a alcanzar y se negó de antemano,
desde el primer turno. Es peor que agotarse: no hace falta gastar para que frene. La frase «56-60k de entrada por
llamada contra un total de 64.000» que circuló en el brief es **falsa** y no se usó como justificación en ningún
comentario ni mensaje de commit. Lo que no cambia es la conclusión: `task_budget` es lo único que le dice al modelo
cuánto espacio tiene para esta tarea.

### Qué se construyó — frente 1 (una sola puerta)
- **Domain:** `AgenteOrganizacion.InstructivoId` + navegación (A-M27-3: en el agente, no en su versión);
  `PropuestaTrabajo.HerramientasJson` + `Pasos`.
- **Application:** `AgenteFormDto.InstructivoId` (el vínculo entra en el mismo INSERT del agente);
  `AgenteDetalleDto.Pasos` + `PasosDelAgenteDto`; `PropuestaTrabajoDto.Pasos` + `Herramientas`;
  `MensajesAnalista.PasosVacios/HerramientasFueraDelBase/PasosLargos/NotaAgenteBase`;
  `MensajesInstructivos.PasosDeEsteAgente`; **`Helpers/PasosEnLineas.cs`** (nuevo, puro) — vive en Application y no en
  uno de los dos servicios que lo usan porque la tarjeta de la propuesta y el bloque «Sus pasos» tienen que mostrar la
  misma lista: si una numerara y la otra no, la persona creería que el agente quedó con otros pasos que los que aprobó.
- **Infrastructure:** `HerramientaProponerAgenteEmpresa` (esquema con `herramientas` y `pasos`, validación de
  subconjunto contra el base); `PropuestaTrabajoService.AplicarAgenteEmpresaAsync` (instructivo + agente + vínculo en
  una transacción, acción por alcance); `AgenteOrganizacionService` (bloque «Sus pasos» y guarda de transacción
  anidada); `HerramientaInstructivosListar` (la marca de A-M27-6).
- **Web:** `Agentes/Index`, `Ficha`, `Detalle`, `Crear`, `_FichaCrearVersion`, `_TarjetaAgente`,
  `PrimerosPasos/Index`, `Analista/Nueva`, `Tareas/_TarjetasPropuestaTrabajo`; `AgentesController.Crear` (la ruta
  pelada redirige al analista); `AnalistaController.Nueva/Iniciar` (agente base por `rubro`+`agente`).
- **Migración `UnificacionAgentesM27`:** exactamente lo que fijó la arquitectura y **nada más**. Verificada contra el
  MySQL de dev: `agentesorganizacion.InstructivoId int NULL MUL`, `propuestastrabajo.HerramientasJson varchar(1000)`,
  `propuestastrabajo.Pasos text`.

### Qué se construyó — frente 2 (la tarea no se corta)
- `AnthropicSettings.TaskBudgetTokens` 64.000 → **400.000**, más `TaskBudgetPorAgente` y `PresupuestoDe(rubro, agente)`.
- `SolicitudModelo.TaskBudgetTokens` y `.LimpiarResultadosViejos`: el presupuesto y la limpieza pasan a ser **por
  pedido**, no configuración global.
- `ProcesadorTareas.EnviarConEscalonamientoAsync`: limpieza del servidor → poda local con testigo → el aviso.
  **El estado final sigue siendo `Fallida`, a propósito** (ver abajo).
- `TipoPasoTarea.NotaDelMotor` (valor 5, sin migración) + su rama de omisión en `ReconstruirConversacion` y su render
  en `ServicioTareas`.
- `MotorAgentesOptions.MaxSeguimientosPorTarea` → `0 = sin tope`, default 0, con `HayTopeDeSeguimientos`.
- `nucleo/_compartido/instrucciones/10-la-tarea-se-termina-donde-empezo.md` + README.

### Qué se construyó — frente 6 (el compositor, pedido durante la implementación)
Crecer-solo sistémico en `site.js` (`textarea[data-autosize]`, una vez para todo el sistema), tres estados en
`site.css`, y `_CuadroSeguimiento.cshtml` sin nada fijo abajo. **Medido en navegador real:** 38 px de textarea en
mínimo, 158 px en el tope (y de ahí scrollea adentro), 352 px expandido; la tarjeta pasó de **221 px a 148 px** en
reposo (25 % → 16 % de un viewport de 900 px).

### Las tres cosas que sólo aparecieron en el navegador
No las habría encontrado ningún test, y las tres eran reales:
1. **En expandido, un texto largo se recortaba** en vez de scrollear: el ajuste automático dejaba un
   `overflow-y: hidden` **inline**, y un estilo inline le gana a la hoja de estilos.
2. **En un teléfono el mínimo eran dos renglones**, porque el navegador cuenta el **placeholder** en `scrollHeight` y a
   390 px el placeholder envuelve.
3. **El chip del agente base era texto blanco sobre blanco**: `text-bg-light` no usa los tokens del theme. Ya existía
   `ov-badge-neutro` para exactamente esto.

### Verificación de A-M27-9 (compactación): **round-trippea, no era un defecto**
Los bloques que devuelve la API se serializan con el resto en el `ContenidoJson` del paso `LlamadaModelo`, se
deserializan con su discriminador `"compactacion"` y `ReconstruirConversacion` los reenvía dentro del mensaje del
asistente, que es lo que el servidor necesita de vuelta (`MapearBloque` → `BetaCompactionBlockParam`). Queda un test
que lo clava, porque es la clase de cosa que se rompe sin que nada falle.

### Lo que corrigió la auditoría sobre el código real (y qué quedó distinto del brief)
- **El analista pasa a `EtapaEntrega.PrimerosPasos` (D-M27-18).** Era el defecto más grave del frente 1 y no lo vi:
  `OpcionMenu.Automatizar` vivía en la segunda etapa, así que sacar «Crear agente» del catálogo y «Crear mi versión»
  de la ficha dejaba a **una organización nueva sin ninguna forma visible de armar un agente**, justo donde el camino
  de arranque de M26 le pide su primer agente propio.
- **El estado final ante el 400 vuelve a ser `Fallida`.** «Nunca Fallida» estaba mal planteado: una tarea `Fallida` ya
  era seguible (`Terminada()` la incluye, y hay test), así que **lo que faltaba era el mensaje**. Y `Completada` tenía
  un costo que no vi: `EjecutorProgramaciones.AvisarFinDeTareaAsync` elige el texto por `== Completada`, o sea que una
  conciliación **programada** habría avisado «terminó correctamente» sobre un trabajo que no se hizo.
- **`TaskBudgetTokens = 0` no es una opción segura y se sacó de la mesa.** La bandera `task-budgets-2026-03-13` se
  ataba a que el número llegara al mínimo de la API, pero el `output_config` existe cada vez que hay esfuerzo o
  esquema de salida y el SDK le serializa `task_budget: null` adentro: un campo sin su bandera es un 400. **Ahora la
  bandera se declara siempre**, con un `[Theory]` sobre 0 / 5.000 / 20.000 / 400.000 que lo fija.
- **El compositor se rompía en el primer refresco del hilo, sin fallar.** `#conversacion` se repinta por AJAX con
  innerHTML y el cuadro vive adentro: los listeners por elemento morían en la primera vuelta del sondeo y el textarea
  dejaba de crecer en silencio. Se pasó a un `input` **delegado en el documento** más un `MutationObserver` que repone
  alto y estado expandido (RF-M27-26).
- **Los topes del compositor dejan de ser literales y se miden contra el viewport.** Tokens
  `--ov-compositor-filas` / `--ov-compositor-vh` / `--ov-compositor-vh-abierto`, con valores propios en móvil. El
  motivo no es prolijidad: el compositor es `sticky`, y un sticky más alto que su scrollport **deja de pegarse**.
- **Supuestos del brief que el código desmintió y que NO se tocaron por eso:** `PublicarParaEmpresa` no exige Director
  en `GuardarAsync` (el gate real de una propuesta de alcance Organización es `PuedeResolverTipo`), así que no se
  agregó ningún chequeo nuevo; y el escalonamiento **no** podía ir en `RegistrarErrorAsync` (corre en un scope nuevo,
  sin conversación ni prompt), así que está dentro del bucle, donde además no consume `Intentos`.

### Decisiones de implementación que no estaban en la arquitectura
- **La guarda de transacción anidada en `AgenteOrganizacionService.GuardarAsync`.** El método abre su propia
  transacción cuando crea un agente publicado; con el aplicador de propuestas abriendo otra afuera, EF tira
  `InvalidOperationException`. Ahora usa la del llamador si existe. Es plomería, pero sin esto A-M27-4 no se podía
  escribir como está escrita.
- **El instructivo se deshace explícitamente además del rollback** (`DeshacerInstructivoAsync`, marca `DeletedAt`). La
  transacción protege en MySQL, pero el proveedor en memoria de las pruebas **ignora las transacciones**, así que la
  invariante de RT-M27-05 no era verificable: el test que la arquitectura pedía no podía existir. Con la compensación
  explícita, la invariante vale en los dos proveedores y hay test.
- **El título del instructivo lo desambigua el sistema** (`Pasos de «X»`, `(2)`, `(3)`…). Lo arma el sistema, no la
  persona, así que un choque de títulos no es algo que ella pueda arreglar.
- **El presupuesto por agente quedó en configuración, no en el manifiesto.** El frontmatter pide una columna en
  `Artefactos` y la migración de M27 está cerrada. Deuda explícita, anotada en el código y en el commit.

### Cobertura
**1091 tests verdes** (eran 1067; +24). Nuevos: `PresupuestoYContextoM27Tests` (18) y seis en
`AnalistaAutomatizacionesTests`. **Cinco tests cambiaron de veredicto a propósito** y cada uno lo dice en su resumen:
`Un_agente_propuesto_nace_en_borrador_y_personal` (reemplazado: el agente ya no nace en borrador), el de conversación
demasiado larga (ahora escalona y el cartel cambió), dos del contador de ajustes (ahora `null`) y el del camino de
arranque en la primera etapa (ahora el paso «contar» SÍ se ofrece, que es por donde el camino dice que empieza).

### Verificación en navegador real (instrucción 38)
Portal de dev con el modelo simulado, 1440×900 y 390×844, tema claro y oscuro, capturas de **viewport** y scroll real
(una captura de página completa miente sobre lo que está sticky). Tres defectos aparecieron sólo acá:
**(1)** en expandido, un texto largo se recortaba en vez de scrollear, porque el ajuste dejaba un `overflow-y: hidden`
**inline** y un estilo inline le gana a la hoja; **(2)** en un teléfono el mínimo eran **dos** renglones, porque el
navegador cuenta el **placeholder** en `scrollHeight`; **(3)** el chip del agente base era **texto blanco sobre
blanco** (`text-bg-light` no usa los tokens del theme; ya existía `ov-badge-neutro`). Y un cuarto, el de los listeners
que morían en el refresco, que tampoco habría encontrado ningún test.

También se verificó contra el MySQL de dev que la migración aplica y que el detalle de tarea abre: el primer intento
dio **500 — `Unknown column 'a5.InstructivoId'`**, que es exactamente lo que va a pasar en producción si se publica
sin migrar.

### Qué se construyó — frente 3 (ningún archivo se rechaza por su formato)

Commit `8dc19cf`. **El filtro que de verdad cortaba estaba en el navegador, no en el servidor.** `AcceptExtensiones`
dejó de ser lista blanca —alimenta el `accept` de `_ZonaSubida` y el `data-extensiones` de `_ModalDocumentos`, así que
una sola fuente cerró los tres lugares— y `validar()` de `documentos.js` dejó de comparar extensiones, manteniendo los
cortes que sí sirven antes de subir 20 MB (macros, HEIC, vacío, tamaño). Se borró el mensaje duro que enumeraba los
formatos permitidos. Sin esto el `.xls` del cliente **nunca llegaba al servidor** y el frente entero no hacía nada.

El resto: `.xls` binario leído con NPOI por un extractor propio (HSSF), OLE2 detectado **después** de la tabla HTML
(PA-35, obligatorio), extensión desconocida y archivo sin extensión guardados como tipo desconocido con el motivo y la
salida en palabras, rama explícita en cada `switch` sobre `TipoDocumento` —el descarte de la extracción mandaba lo
desconocido a `ExtractorTexto`, así que un `.exe` quedaba **`Legible` con basura** que el agente iba a leer—, extensión
acotada antes de guardar (`varchar(10)`), y `octet-stream` + `attachment` donde se guarda el `TipoContenido` y no en
cada controller, con el camino *inline* por lista blanca.

### Qué se construyó — frente 4 (el menú de menos a más)

Commit `8e15ab4`. Las **25** opciones (no 20: el conteo del análisis estaba mal y lo corrigió QA al armar el plan) pasan
de tres secciones a cuatro, declaradas una vez en `MenuOrganizacion` — el layout dejó de decidir y son **219 líneas
menos de vista**. Ninguna opción se saca ni se esconde.

**Lo más importante del frente no es el orden: es lo que el reordenamiento iba a tapar.** `VeEnMenu` miraba solo la
etapa, y el rol lo decía el layout con un `@if (Permisos.EsDirector)` que envolvía a cuatro ítems. De ahí salían dos
defectos que estaban a la vista y que nadie había mirado:

- **«Configurar conversando» y «Repartir trabajo conversando» se le ofrecían a un Empleado** aunque sus controllers son
  `RequireDirector`: el enlace estaba y daba **403**. `EtapasEntrega.SoloDirector` ya tenía la respuesta escrita; el
  layout no la consultaba.
- **`Miembros` era el único ítem sin `VeEnMenu`:** su condición efectiva era el `@if` externo. Re-anidar ese bloque para
  reordenar es justo donde se escapa un permiso, así que la condición se completó **antes** de mover nada.

Ahora hay **una sola condición por opción** (etapa **y** rol) y `OpcionesVisibles` —que es lo que afirman los tests—
describe de verdad lo que se ve. Y un encabezado de sección no se dibuja si no tiene ningún ítem visible: en etapa
`PrimerosPasos` los ocho ítems de «Tu forma de trabajar» quedan detrás de la etapa y el título se habría dibujado solo.

Sigue valiendo que **esto oculta, no bloquea**: el menú deja de ofrecerle `Pruebas` a un Empleado porque correrlas gasta
del tope de la empresa, pero su controller sigue siendo `RequireMiembro` a propósito y puede leer la lista.

### Qué se construyó — el núcleo (la instrucción transversal y el contrato de la herramienta)

Commit `364c4a5`. Dos cosas que M27 dejó escritas y sin enganchar, más lo que la decisión de Joaquín del 2026-10-01
definió:

- **La instrucción transversal enganchada en los cuatro rubros** (`contable`, `inmobiliario`, `estudio-software`,
  `general`) con una línea `archivo:`, que se resuelve con `GetFullPath` sobre la raíz y por eso puede apuntar a este
  repo desde los repos de contenido: **una sola copia, no cuatro**. Dato que explica por qué la regla no llegaba a
  ningún lado: **el rubro `contable` no tenía bloque `instrucciones:` en absoluto** — el agente que falló en la demo
  nunca tuvo instrucciones a nivel rubro.
- **El contrato de `proponer_agente_empresa`, una vez y no tres.** La herramienta la ofrecen el analista, el asistente y
  el configurador. En vez de reescribir tres prompts —y arriesgar que uno quede distinto—, lo que comparten los tres va
  en `nucleo/plataforma/instrucciones/`, que es el mecanismo que el sistema ya tiene para eso (regla del proyecto,
  2026-09-25). Solo el prompt del analista necesitó edición propia, porque su sección de agente propio hablaba
  únicamente de las instrucciones y ahora tiene que hablar de los pasos.
- **Cuatro casos de evaluación nuevos**, donde no había ninguno para la herramienta que M27 convirtió en el único camino
  para armar un agente: que el agente se proponga **con** sus pasos y **no además** como instructivo, que sin pasos los
  pregunte en vez de inventarlos, que lleve el orden que dijo la persona, y que una preferencia sobre un agente que ya
  sirve siga siendo una regla y no un agente nuevo.
- **El tope de instrucciones de la herramienta, de 8.000 a 30.000.** El esquema le declaraba al modelo 8.000 caracteres
  y el servidor valida contra `MaxInstrucciones = 30.000`: **el esquema mentía**. Con el analista como única puerta eso
  recortaba justo al **agente en blanco** del rubro `general`, donde las instrucciones no son un ajuste de tono sino el
  método entero. El número va al esquema y el criterio de cuánto escribir va a la descripción, que es donde el modelo lo
  puede usar: pocas líneas si el base es un agente de rubro, el método completo si el base es el agente en blanco.

### Dos trampas de YAML que se pagaron en el camino

Las dos son del mismo tipo y conviene que queden escritas, porque el repo ya las documenta en el importador y se
volvieron a pisar:

1. **Un valor sin comillas con `: ` adentro** no es texto para YAML. `texto: Los pasos del agente YA son el instructivo
   de esa tarea: proponer los dos es duplicar` no parsea.
2. **Peor: un ítem de lista con `: ` adentro parsea bien y significa otra cosa.** `- No dice que no se puede armar un
   agente propio: dice que para esto no hace falta.` se lee como un **mapa**, no como un texto. PyYAML lo acepta sin
   chistar y devuelve un diccionario; **YamlDotNet revienta al deserializarlo en un `string`**, y el error que sale es
   «Exception during deserialization» sobre el archivo entero, sin número de línea.

**La lección operativa:** validar la **sintaxis** del YAML no alcanza —el archivo parseaba— y validar con PyYAML tampoco
—el archivo pasaba—. Hay que validar la **forma**: que lo que tiene que ser texto sea texto. Es lo que encontró el test
`FichaImportadaTests.Los_agentes_del_nucleo_traen_su_ficha`, que importa los manifiestos de verdad, y es la razón por la
que ese test vale más de lo que parece.

### Cobertura y estado

`dotnet build` limpio y **1120 tests verdes** (eran 1091 al cerrar los frentes 1/2/6: el menú trajo 29 nuevos en
`MenuLateralTests`, que es la prueba automática que la arquitectura había dado por imposible).

**Siete commits locales, sin push:** `625b30f` (frente 1) · `43dce94` (frente 2) · `f7103cf` (frente 6) · `28b929c` (el
analista en la primera etapa y tres correcciones) · `8dc19cf` (frente 3) · `8e15ab4` (frente 4) · `364c4a5` (el núcleo).

### Lo que queda fuera de este trabajo

- **Importar, evaluar y publicar las tres suites de plataforma.** Decisión de Joaquín (2026-10-01): se hace, con la
  corrida de aprobación. Ninguna versión se publica sin evaluación aprobada y las suites de plataforma corren con
  Opus 5, así que es trabajo con costo, no un ajuste de texto.
- **Enganchar la instrucción transversal en producción** exige reimportar y publicar cada rubro: las tareas ya abiertas
  **no cambian de hash** porque su contexto está congelado en la instantánea, pero las nuevas sí la traen.
- **El despliegue a producción**, que es lo que habilita la prueba de la tarea 17: migración + editar
  `appsettings.Production.json`, que no está versionado y **gana** sobre el default de C#.
- Los cuatro pendientes de decisión que quedaron anotados y sin resolver: el texto del paso de M26 que sigue diciendo
  «Crear mi agente», agente + programación en la misma vuelta, y si el orden «de menos a más» se replica en
  `Primeros pasos` (decidido que **no**, a propósito).

#### Lo que decía el cierre de los frentes 1/2/6 (se conserva)

##### Pendientes anotados al cerrar los frentes 1, 2 y 6
- **La regla de prompt no está enganchada en ningún rubro.** Las instrucciones de `plataforma` solo entran en los
  formatos de contexto 3, 4 y 5: a una conciliación (formato 1) no llegan. Para que alcance tiene que ser instrucción
  **del rubro**, y el contenido de los rubros vive en otros repos (`Agente Contable-IA`, `Agente Inmobil-IA`,
  `Agentes-IA`). Es además un cambio de prompt: importar → evaluar → publicar. El README de `nucleo/_compartido/`
  tiene la línea exacta de manifiesto.
- **La prueba final de CA-M27-04 la hace Joaquín** sobre la tarea 17 de producción.
