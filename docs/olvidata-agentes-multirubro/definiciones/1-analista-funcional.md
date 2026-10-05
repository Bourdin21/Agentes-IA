# Memoria - Analista funcional

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-10-02 (M29: buscar en internet desde el chat libre, y el archivo que se guarda o se descarta) | 2026-10-02 (M28: Discovery + Analisis del chat libre -- conversacion sin agente y sin cliente, cargada por menciones) | 2026-10-01 (M27: una sola puerta para armar un agente, la tarea que no se corta, todo archivo entra, el menu de menos a mas)

## Definiciones vigentes

### Modulos/features analizados

**M29 — Buscar en internet desde el chat libre, y el archivo que se guarda o se descarta** (Discovery + Análisis, 2026-10-02). Pedido de Joaquín, dos cosas, justo después de cerrar M28: *«Agregar casilla de buscar en internet»* y *«Se puede cargar un archivo a la conversación con posibilidad de que se resguarde como archivo de cliente o se descarte luego del procesamiento»*. Estado: **Análisis cerrado**; presupuesto omitido (proyecto personal).

**Lo que hay que entender antes de leer los requisitos:** el segundo pedido **es la respuesta a OLV-036**, el único defecto que M28 dejó abierto, y es una respuesta mejor que la que tenía la arquitectura. M28 cerró diciendo que *un documento de la empresa sin cliente no existe en el modelo* y que resolverlo pedía tres decisiones de producto. Joaquín las contestó de una forma que **esquiva el problema en vez de pelearlo**: el archivo no tiene que vivir sin dueño para siempre — o **se guarda en la carpeta de un cliente** (y entonces es un documento normal, con el modelo que ya existe) o **se usa y se descarta** (y entonces no hace falta decidir dónde se ve, ni si dos pueden llamarse igual, ni contra qué cuota cuentan: es transitorio). Eso convierte tres decisiones abiertas en una sola pregunta operativa —*cuándo se descarta*— que también quedó contestada.

**Ubicación en el concepto rector** (`docs/el-sistema-como-computadora.md`): las dos cosas son **periféricos**. Buscar en internet son **los ojos mirando afuera**, y ya está decidido que *la ejecuta el proveedor*, así que no entra en la lista de herramientas que corre el motor ni pasa por el guardia de destinos. El adjunto de conversación son **los ojos mirando un papel que alguien trajo**, y lo que M29 agrega es que ese papel se pueda **tirar**: hasta hoy todo lo que entraba al disco se quedaba. El archivo entra **como dato** —se lee con `adjunto_leer`, cuyo universo sigue siendo por inclusión lo adjuntado a **esa** tarea— y nunca como orden.

#### Decisiones de Joaquín (2026-10-02), que cierran el Análisis

- **D1 — El archivo «solo de esta conversación» se descarta a los N días de terminada la conversación.** Mientras el hilo vive, el archivo está: se puede seguir preguntando sobre él y se puede guardar en un cliente. Terminada la conversación arranca una **ventana de gracia configurable (7 días por defecto)** y después se borra solo. Descartado *al terminar el turno*, que era más literal y no pedía purga, porque impedía la pregunta de seguimiento — y una conversación existe para eso.
- **D2 — Cuenta contra la cuota de la organización.** Ocupa disco real, así que ocupa cuota, y así el camino transitorio no es una puerta para saltear el tope de 1 GB. Se libera al descartarse.
- **D3 — Alcance de la casilla de internet: el chat libre y nada más.** Las otras tres conversaciones de plataforma configuran el sistema; no necesitan salir a la red. El chat libre existe para *resolver cualquier consulta suelta* y es el único de los cuatro donde internet es parte del trabajo.

#### Qué de esto ya existe (relevamiento sobre el código, 2026-10-02)

- **Buscar en internet: está entero y apagado por un solo `&&`.** `ResolvedorHerramientas.cs:263` calcula `busquedaOfrecida = trabajo && (...)`, y `trabajo` es `s.Tipo == TipoTarea.Trabajo`. La columna `TareasAgente.PermiteBusquedaWeb` **ya existe para toda tarea**, la compuerta fail-closed ya está (`BusquedaWeb:Habilitada` + `PrecioPorBusquedaUsd`, y `Disponible` exige las dos), el costo por búsqueda ya se registra en `EventoUso.Busquedas`, y la casilla ya está maquetada dos veces (al crear una tarea y en el cuadro de seguimiento). **No hace falta migración.**
- **El adjunto: el pipeline de subida está entero y el agujero es el parámetro.** Un solo `SubirInternoAsync` sirve a los tres orígenes (`Estudio`, `Cliente`, `Agente`) y hace validación de formato real por firma, corte por bytes, duplicado por hash, cuota por cliente, cuota por organización, extracción por partes y nombre único con reintento. `adjunto_leer` ya resuelve el universo por inclusión contra `AdjuntosMensajeTarea`. La baja ya borra el archivo del disco y las partes de la base.
- **Lo que NO existe:** (a) un documento **sin cliente** — `DocumentoCartera.ClienteCarteraId` es `int` **NOT NULL** con FK Restrict, está en 5 índices y **el clienteId es parte de la ruta en disco** (`AlmacenDocumentosDisco.Ruta` exige `> 0`); (b) cualquier **purga automática** — lo único que hay es el comando manual `documentos-limpiar` con corte de 1 hora, y el único `AddHostedService` del sistema es el worker del motor, que no toca archivos; (c) nada **efímero** o **transitorio** en el dominio: cero ocurrencias.

#### Alcance inicial

- **RF-01** El chat libre ofrece la **casilla de buscar en internet** al arrancar la conversación y en cada ajuste, con la misma compuerta fail-closed y el mismo registro de costo que una tarea de trabajo.
- **RF-02** Desde **cualquier conversación** se puede **subir un archivo nuevo** sin tener que elegir un cliente primero. Esto cierra OLV-036, que afecta a las cuatro conversaciones de plataforma, no solo al chat libre.
- **RF-03** Al subirlo, la persona elige: **«usarlo solo en esta conversación»** (por defecto) o **«guardarlo en la carpeta de un cliente»**.
- **RF-04** Un archivo «solo de esta conversación» **se puede guardar después**: mientras el hilo vive, se ofrece pasarlo a un cliente sin volver a subirlo.
- **RF-05** Un archivo «solo de esta conversación» **se descarta**: a mano cuando la persona lo saca, o solo a los **N días** de terminada la conversación (D1).
- **RF-06** El archivo transitorio **cuenta contra la cuota** de la organización y se libera al descartarse (D2).
- **RF-07** El agente lo lee con `adjunto_leer` igual que a cualquier adjunto, **sin distinguir** si es transitorio o guardado: el universo sigue siendo por inclusión lo adjuntado a esa tarea.

#### Alcance no incluido

- La casilla de internet en el configurador, el asistente y el analista (D3).
- Que el **agente** decida guardar o descartar un adjunto: lo decide la persona. Guardar un archivo en la carpeta de un cliente es un acto con consecuencias y no sale de un modelo.
- Compartir un archivo transitorio entre conversaciones, o que aparezca en el listado de documentos de la organización mientras es transitorio.
- Que el cliente del portal vea un archivo transitorio, en ningún caso (ver CA-T.2, que es el riesgo que importa).

#### Supuestos y dependencias

- **S-01** Un archivo transitorio es **un `DocumentoCartera` sin cliente**, no una entidad nueva: así reutiliza extracción, partes, cuotas, duplicados, `adjunto_leer` y la baja, que es todo lo que haría falta reimplementar en una tabla paralela.
- **S-02** «Guardar en un cliente» es **asignarle el cliente**, no copiar el archivo.
- **S-03** La ventana de gracia es configuración, no código.
- **D-01** M29 depende de M28 (el chat libre y su tipo de tarea).

#### Banderas tempranas

- **Migración EF: SÍ**, y es la primera de M28/M29 — `ClienteCarteraId` pasa a nulable, con todo lo que eso arrastra (índice único, FK, ruta en disco, filtros).
- **Purga nueva: sí.** Hoy no existe ningún mecanismo de expiración al que colgarse.
- Prompt nuevo del núcleo: **no**. El agente del chat libre ya existe; a lo sumo se le menciona la casilla.
- Integración externa: **no** (la búsqueda la ejecuta el proveedor; ya estaba así).

#### Criterios de aceptación

**Buscar en internet (RF-01)**
- CA-01.1 La casilla aparece al arrancar un chat libre y en el cuadro de ajuste, **apagada por defecto**.
- CA-01.2 Con `BusquedaWeb:Habilitada` en false **o** `PrecioPorBusquedaUsd` en 0, la casilla **no se ofrece** y, forzando el POST, la tarea no permite búsqueda. Fail-closed, igual que hoy.
- CA-01.3 Marcada, el agente puede buscar; el costo de cada búsqueda queda en el paso y en `EventoUso.Busquedas`, y se suma al costo visible del hilo.
- CA-01.4 El tope `MaxBusquedasPorTarea` sigue valiendo.
- CA-01.5 La casilla **no aparece** en el configurador, el asistente ni el analista (D3), y forzar el POST ahí no habilita nada.
- CA-01.6 La búsqueda **no entra** en la lista de herramientas que corre el motor y **no** pasa por el guardia de destinos: la ejecuta el proveedor.

**Subir sin cliente (RF-02, RF-03)**
- CA-02.1 Desde las **cuatro** conversaciones de plataforma se sube un archivo nuevo sin elegir cliente, y el mensaje de error mentiroso de OLV-036 («Elegí un archivo» con el archivo adentro) **no vuelve a aparecer**.
- CA-02.2 Al subir se elige entre «solo en esta conversación» (por defecto) y «guardar en la carpeta de un cliente»; eligiendo cliente, el archivo queda como documento normal de ese cliente, con su origen y su visibilidad habituales.
- CA-02.3 Todas las validaciones del pipeline siguen valiendo para el archivo sin cliente: formato real por firma, corte por bytes, cuota de la organización, extracción por partes, y nada se sirve con su propio tipo de contenido.
- CA-02.4 Un archivo sin cliente **no aparece** en el listado de documentos de ningún cliente ni en el de la organización.

**Guardar después y descartar (RF-04, RF-05, RF-06)**
- CA-03.1 Un archivo «solo de esta conversación» se puede **pasar a un cliente** desde el hilo, sin volver a subirlo; al pasarlo se revalidan **duplicado por hash** y **cuota por cliente** contra ese cliente, y el nombre se hace único ahí.
- CA-03.2 La persona puede **sacarlo** y el archivo se borra del disco y sus partes de la base, como cualquier baja.
- CA-03.3 Terminada la conversación y pasada la ventana de gracia, el archivo transitorio **se descarta solo**. Antes de que pase, **no** se descarta.
- CA-03.4 La ventana de gracia es configurable y, puesta en 0, **no** se vuelve «descartar todo ya»: eso invertiría el comportamiento, que es el defecto que M27 encontró dos veces con los topes comparados con `>=`.
- CA-03.5 Descartar **libera la cuota** de la organización.
- CA-03.6 Un archivo ya **guardado en un cliente** no lo toca la purga, nunca, aunque su conversación haya terminado hace meses.

**Transversal — lo que hay que probar aunque nadie lo pida**
- CA-T.1 `adjunto_leer` sigue leyendo **solo** lo adjuntado a esa tarea, sea transitorio o guardado: ni la carpeta de un cliente ni el adjunto de otra tarea.
- CA-T.2 **Ningún usuario del portal del cliente ve un archivo sin cliente, por ningún camino.** Es el riesgo central de M29: `DocumentoCartera` implementa `IClienteOwned` y el `FiltroCliente` del `AppDbContext` es lo que protege al portal; con `ClienteCarteraId` nulable hay que verificar que un `NULL` **no** se cuele por ese filtro. Es exactamente la lección de M18.
- CA-T.3 Multi-tenant: un archivo sin cliente de otra organización no se lee, no se guarda y no se descarta, y el id manipulado se rechaza con la **guarda de tenant**.
- CA-T.4 Dos archivos sin cliente de **dos organizaciones distintas** con el mismo nombre no colisionan: el índice único deja de ser global.
- CA-T.5 La ruta en disco de un archivo sin cliente **no** se arma con un valor que venga del pedido.

#### Riesgos

- **R-01 (alto) — El `NULL` que se cuela por el filtro del portal del cliente.** Volver nulable una columna que es la base de `IClienteOwned` y del `FiltroCliente` es tocar la frontera que protege a los usuarios cliente. Mitigación: CA-T.2 con **control positivo y negativo**, y revisar cada consulta que asume cliente.
- **R-02 (alto) — El índice único se vuelve global.** `(ClienteCarteraId, NombreVigente)` con `ClienteCarteraId` nulable dejaría «un nombre único entre todos los documentos sin cliente **de todas las organizaciones**». Mitigación: el índice pasa a llevar `TenantId` (CA-T.4).
- **R-03 (medio) — La ruta en disco.** `AlmacenDocumentosDisco.Ruta` exige `clienteId > 0` como **guarda de path traversal**, no por capricho. Mitigación: la carpeta del archivo sin cliente es un **nombre constante del código**, nunca un valor del pedido (CA-T.5).
- **R-04 (medio) — La purga borra algo que no debía.** Es código nuevo que borra archivos. Mitigación: solo alcanza documentos **sin cliente** cuya conversación está terminada hace más de la ventana; un documento con cliente **nunca** entra (CA-03.6); y el comando manual sigue teniendo su modo sin `--aplicar` para mirar antes.
- **R-05 (medio) — Costo de las búsquedas.** El chat libre es la conversación más abierta del producto y ahora puede salir a internet a USD 10 cada 1.000 búsquedas. Mitigación: la casilla nace **apagada**, `MaxBusquedasPorTarea` sigue valiendo, el precio se verifica contra la página oficial, y el tope de gasto de M6 **no se toca**.
- **R-06 (bajo) — La cuota se consume con basura transitoria.** Mitigación: D2 (cuenta) más la purga de D1.

**M28 — El chat libre: una conversación que arranca sin agente y sin cliente, y se carga mencionando** (Discovery, 2026-10-02). Pedido de Joaquín: una pantalla nueva donde el usuario use el chat libremente *«como si fuera Claude web»*, para resolver **cualquier consulta suelta**, pudiendo **arrobar agentes** para pedirles tareas y **crear reglas y automatizaciones haciendo menciones**, con buen diseño gráfico y **motion 3D**. Estado: **Discovery cerrado con 4 preguntas abiertas bloqueantes**; presupuesto omitido (proyecto personal).

**Ubicación en el concepto rector** (obligatoria antes de diseñar, `docs/el-sistema-como-computadora.md`): el chat libre es **la CPU sin un programa cargado**. Las cuatro conversaciones que existen hoy arrancan con la RAM ya escrita por el sistema (prompt del rubro, prompt del agente, instrucciones de la empresa, reglas). El chat libre arranca con la RAM casi vacía y **la persona decide qué cargar, mencionando**: una mención de agente carga el método de ese agente para ese pedido; una mención de configuración carga el instructivo de plataforma que corresponda. **La mención es el cargador de la RAM, no una orden nueva** — y sigue valiendo que lo mencionado entra **como datos**: una mención no crea nada, deja una tarjeta que una persona aplica. Esta es la única lectura del pedido que no rompe el concepto rector, y de ella sale el requisito RF-05.

#### Qué de esto ya existe (relevamiento sobre el código, 2026-10-02)

El pedido suena a módulo nuevo y es, en su mayor parte, **una puerta nueva a un motor que ya está entero**. Reutilización obligatoria: **PAT-029** (conversación multi-turno reanudable con contexto congelado), origen este mismo proyecto, M3b.

- **Ya existe y no se toca:** el motor de tareas y la reanudación (`ServicioTareas`, `ProcesadorTareas`); la **tarea sin cliente** (`TareaAgente.ClienteCarteraId` es `int?`, `Tareas.cs:147`, y `adjunto_leer` ya se habilita en ese caso, `ResolvedorHerramientas.cs:108-116`); la vista de conversación **compartida por las cuatro conversaciones actuales** (`Views/Tareas/_Conversacion.cshtml`, 270 líneas, + `_CuadroSeguimiento.cshtml`); el turno en vivo por SignalR (`TareasHub`, `/hubs/tareas`) con respaldo de polling (`Progreso` devuelve el parcial); las tarjetas de propuesta de **las cuatro cosas que se cargan** (`TipoPropuestaTrabajo` = `AsignarPersona/TareaAgente/Programacion/AgenteEmpresa`, más la familia `PropuestaRegla` para regla e instructivo); el resolvedor único de herramientas por tipo de tarea (`ResolvedorHerramientas.ResolverAsync`); `TopePropuestas.PorRespuesta`; el **agente en blanco** del rubro `general`, `incluido_siempre`, con instrucciones de hasta 30.000 caracteres (M21).
- **No existe, y es el trabajo real de M28 (tres cosas):**
  1. **Menciones.** No hay nada: ni parser de `@`, ni autocomplete, ni entidad de mención. Las coincidencias de «mencion» en el repo son copy y validaciones.
  2. **Delegar en vivo a cualquier agente de la organización.** `delegar_subagente` existe (M7a) pero con dos restricciones duras que el pedido atraviesa: solo corre en `TipoTarea.Trabajo` y solo admite **hijos publicados del agente base** del coordinador (`SubtareasService.cs:68-92`). Hoy la única vía desde una conversación de plataforma es `proponer_tarea_agente`, que es una tarjeta, no una delegación en vivo.
  3. **Motion 3D.** El front es **vanilla JS + jQuery + Bootstrap 5, sin npm, sin bundler y sin ninguna librería de animación o 3D** (nada de three.js, GSAP, Lottie). Los assets son locales en `wwwroot/lib` o CDN jsdelivr desde `_Layout`. Cualquier motion 3D es una dependencia nueva, y es la primera del proyecto en su clase.

#### Alcance inicial

- **RF-01** Pantalla nueva de **chat libre**, disponible para **cualquier miembro** (no solo el Director), que se abre sin elegir agente, sin elegir cliente y sin elegir rubro.
- **RF-02** Conversación **multi-turno reanudable** sobre el motor existente, con costo visible, tope de gasto, turno en vivo y reanudación tras reinicio: por reutilización de PAT-029, no por implementación nueva.
- **RF-03** Al escribir `@`, **autocomplete** de lo mencionable, filtrado por lo que esa persona efectivamente puede usar (rol, etapa de entrega, licencia del rubro).
- **RF-04** **Mención de agente** ⇒ el pedido lo resuelve ese agente, con su prompt publicado, sus herramientas y sus reglas, y la respuesta vuelve dentro del mismo hilo.
- **RF-05** **Mención de configuración** ⇒ el chat **propone una tarjeta** de regla, instructivo, tarea programada o agente propio. **Nunca crea nada por la mención**: el rol se chequea **al aplicar**, según el alcance de cada propuesta (regla permanente del `CLAUDE.md`).
- **RF-06** Sin excepciones para el chat libre: tope de propuestas (`TopePropuestas`), tope de gasto de M6, guardia de destinos de M11, `metadata.user_id` y registro en `EventoUso`, y el recuerdo rotulado sin confirmar de M17/M25.
- **RF-07** **Diseño gráfico y motion.** Alcance a definir en P4 (ver preguntas abiertas): hay una tensión real entre «motion 3D» y la instrucción `38` del estudio, cuya regla 0 es *«lo que la persona vino a hacer entra en la primera pantalla; todo lo demás se pliega»*.
- **RF-08** **Adjuntos sin cliente**, leídos con `adjunto_leer`, cuyo universo es por inclusión lo adjuntado a **esa** conversación: nunca la carpeta de un cliente. Ya soportado.
- **RF-09** **Historial**: los chats libres se listan y se reabren como cualquier tarea.

#### Alcance no incluido (Discovery)

- Streaming token a token. Hoy el turno llega por SignalR y por el parcial que devuelve `Progreso`, y **eso no cambia en M28**: es el motor, no la pantalla.
- Mencionar **personas** para asignarles trabajo (eso es el asistente de M7/M15 y su tarjeta `AsignarPersona`).
- Mencionar **clientes** de la cartera para traer su carpeta: el chat libre es sin cliente por definición (RF-01) y abrir la carpeta de un cliente por mención contradice el universo por inclusión de `adjunto_leer` (RF-08).
- Reemplazar las cuatro conversaciones existentes ni el catálogo de Agentes. El chat libre **se suma** como puerta.
- Voz / audio (los «oídos» del concepto rector siguen pendientes de decisión).

#### Supuestos y dependencias

- **S-01** El chat libre es una `TareaAgente` como cualquier otra: hereda multi-tenant, costo, auditoría y reanudación. No es una entidad nueva de conversación.
- **S-02** Hay un prompt del núcleo que atiende el turno cuando **no** hay ninguna mención. Cuál es, es P1.
- **S-03** Toda mención resuelve contra algo **publicado** y **visible para esa persona**; una mención a algo que no puede usar no se ofrece en el autocomplete y, si se fuerza por texto, no resuelve.
- **D-01** Depende de que haya evaluación aprobada si M28 introduce un prompt nuevo: **ningún prompt se publica sin evaluación aprobada** (regla permanente).
- **D-02** Si P4 resuelve 3D, depende de incorporar la primera librería de animación del proyecto, con su peso y su política de carga.

#### Banderas tempranas

- Requiere **migración EF**: **sí, probablemente** — un valor nuevo de `TipoTarea` y, si las menciones se persisten como entidad en vez de resolverse al vuelo, una tabla. Se cierra en Arquitectura.
- Integración externa: **no**.
- Máquina de estados: **no** nueva (reutiliza `EstadoTarea`, incluido `EsperandoSubtareas` si P2 resuelve delegación en vivo).
- Prompt nuevo del núcleo: **a definir en P1** — si lo hay, arrastra evaluación y publicación.

#### Preguntas abiertas (bloqueantes: cambian el diseño, la arquitectura y el tamaño)

- **P1 — ¿Quién atiende el chat cuando no hay ninguna mención?** Tres caminos con consecuencias muy distintas: (a) el **agente en blanco** del rubro `general`, que ya existe, ya es `incluido_siempre` y ya delega el método a las instrucciones de la empresa — sin prompt nuevo, sin evaluación, sin publicar; (b) un **cuarto agente de plataforma** en `nucleo/plataforma`, con prompt propio orientado a consulta general y derivación — es el más parecido a Claude web, y arrastra prompt nuevo más evaluación más publicación; (c) **ningún agente**: el chat exige mención para hacer cualquier cosa, y sin mención solo conversa y orienta.
- **P2 — Una mención de agente: ¿delegación en vivo o tarea aparte?** (a) **En vivo**, ampliando `delegar_subagente` a cualquier agente que esa persona pueda usar: es lo que más se parece a lo pedido, y es un cambio de alcance de M7a con riesgo de costo (un hilo libre podría disparar varios agentes). (b) **Tarea aparte**, donde la mención abre una tarea del agente mencionado y el hilo libre queda esperándola con su tarjeta de parte: más barato, ya existe el estado `EsperandoSubtareas`, y la respuesta del agente sigue entrando al hilo.
- **P3 — «Crear reglas y automatizaciones haciendo menciones»: ¿qué hace exactamente la mención?** La lectura que respeta el concepto rector es que la mención **carga el instructivo** del configurador o del analista y el turno **propone una tarjeta** (RF-05). La otra lectura —que la mención cree la regla directamente— está descartada de entrada por la regla permanente de que **una preferencia la aplica una persona**. Confirmar que P3 es la primera lectura.
- **P4 — Alcance del «motion 3D».** Hoy no hay ninguna librería 3D ni de animación y la instrucción `38` del estudio es explícita en que el adorno que compite con el contenido se pliega. Tres niveles: (a) **motion sin 3D**: transiciones, estado del agente pensando, aparición de tarjetas y del autocomplete, con CSS y el design system — cero dependencias; (b) **3D acotado**: una pieza sola (por ejemplo el indicador del agente trabajando, o el estado vacío de arranque), con carga diferida y apagado por `prefers-reduced-motion`; (c) **3D de ambiente**: fondo animado en toda la pantalla — es el que más choca con la instrucción `38` y el que pesa.

#### Respuestas de Joaquín a las preguntas abiertas (2026-10-02) — cierran el Análisis

- **P1 → (b) un cuarto agente de plataforma.** El chat libre tiene **prompt propio** en `nucleo/plataforma/agentes/`, orientado a la consulta general y a derivar. Consecuencia aceptada: arrastra **prompt nuevo + evaluación aprobada + publicación**, y mientras no haya versión publicada **la pantalla no está disponible** (mismo criterio que los otros tres). Descartado el agente en blanco de `general`: ese es el agente que **el cliente** escribe entero, y el chat libre tiene que saber de la plataforma para poder derivar.
- **P2 → (b) tarea aparte, el hilo espera.** La mención de un agente **abre una tarea de ese agente** y el hilo libre queda en `EstadoTarea.EsperandoSubtareas` con su tarjeta de parte; la respuesta vuelve al hilo. Se reutiliza M7a casi tal cual. Motivo de la elección: el costo queda acotado y visible **por tarea**, y la delegación en vivo habría dejado al tope de gasto como único freno de un hilo que puede disparar varios agentes.
- **P3 → confirmado: propone, no crea.** La mención de configuración **carga el instructivo** y el turno deja **tarjetas**. El rol se chequea **al aplicar**, según el alcance de cada propuesta.
- **P4 → (b) 3D acotado a una pieza.** Una sola pieza en 3D, con **carga diferida** y **apagada por `prefers-reduced-motion`**. El resto del movimiento es CSS y design system. Descartado el fondo de ambiente por la regla 0 de la instrucción `38` y por su peso.

#### Problema de negocio

El sistema tiene cinco puertas y **todas piden que la persona ya sepa qué quiere**: elegir un agente del catálogo, elegir un cliente, o entrar a una de las tres conversaciones de configuración, cada una con su tema fijo. No hay ningún lugar donde alguien escriba *una pregunta cualquiera* y el sistema le sirva — y eso es justamente el gesto con el que la gente ya sabe tratar a una IA. La consecuencia medida en la primera demo (M27) fue que la funcionalidad existía y no se encontraba. El chat libre es la puerta que **no exige haber decidido nada antes de escribir**, y desde la cual se llega a todo lo demás mencionando.

#### Casos de uso

- **CU-01 — Consulta suelta.** Un miembro abre el chat libre, escribe una pregunta sin mencionar a nadie y recibe respuesta del agente de chat libre, con costo registrado y el hilo reanudable.
- **CU-02 — Pedirle trabajo a un agente mencionándolo.** Escribe `@` y el autocomplete le ofrece los agentes que **esa persona** puede usar; elige uno, describe el pedido, y el chat abre una tarea de ese agente. El hilo queda esperando y la respuesta entra al hilo.
- **CU-03 — Configurar mencionando.** Menciona la configuración (regla, instructivo, tarea programada o agente propio) y el turno deja **tarjetas**, que una persona aplica con un botón si su rol alcanza para ese alcance.
- **CU-04 — Adjuntar un documento al chat.** Adjunta un archivo **sin cliente** y el agente lo lee con `adjunto_leer`, cuyo universo es lo adjuntado a **esa** conversación.
- **CU-05 — Volver a un chat libre.** Encuentra sus chats libres en el historial y los reabre; sigue valiendo que **solo el autor continúa** y que los roles superiores leen.
- **CU-06 — Derivación.** Pide algo que corresponde a una de las tres conversaciones de plataforma y el chat lo **deriva** nombrando dónde se hace, en vez de intentar hacerlo él.

#### Criterios de aceptación

**CU-01**
- CA-01.1 Cualquier **miembro activo** (no solo el Director) abre la pantalla de chat libre, sin elegir agente, sin elegir cliente y sin elegir rubro.
- CA-01.2 Sin versión publicada del agente de chat libre, la opción **no se ofrece en el menú ni en el catálogo**, y entrar por URL devuelve el mismo trato que las otras tres conversaciones sin publicar («Todavía no está disponible.»).
- CA-01.3 El turno llega en vivo por SignalR y, cortando el websocket, el respaldo de polling lo trae igual.
- CA-01.4 La tarea se reanuda tras reiniciar el proceso, con el **mismo contexto congelado**, y el costo acumulado se ve en la barra.
- CA-01.5 Con el tope de gasto de M6 alcanzado, el chat libre **no arranca** y dice por qué. Ningún valor de M6 se toca.
- CA-01.6 Toda llamada lleva `metadata.user_id` opaco y deja su `EventoUso`.

**CU-02**
- CA-02.1 Al escribir `@` aparece el autocomplete; se navega con flechas, se elige con Enter o Tab y se cierra con Escape.
- CA-02.2 El autocomplete ofrece **solo** lo que esa persona puede usar: filtrado por rol, por etapa de entrega y por licencia del rubro. Un agente sin versión publicada no aparece.
- CA-02.3 Mencionar por texto un agente que no se ofrecería (id o slug manipulado, agente de otra organización) **no resuelve** y el turno lo dice: no abre tarea y no filtra que exista.
- CA-02.4 La mención abre una tarea del agente mencionado; el hilo libre pasa a `EsperandoSubtareas` y muestra la tarjeta de parte con su estado.
- CA-02.5 Al terminar la tarea del agente, el hilo libre **se despierta solo** y su resultado entra al hilo. Si la tarea del agente falla, el hilo se despierta igual y lo informa: no queda esperando para siempre.
- CA-02.6 La profundidad máxima de subagentes sigue valiendo: un agente alcanzado por mención no puede usar el chat libre para volver a entrar.
- CA-02.7 El agente mencionado corre con **su** prompt publicado, **sus** herramientas y **las reglas de la empresa** que le corresponden — no con el contexto del chat libre.

**CU-03**
- CA-03.1 Una mención de configuración deja **tarjetas** y **no crea, modifica ni activa nada** por sí sola. Verificable en base: después del turno, cero filas nuevas de regla, instructivo, programación o agente.
- CA-03.2 El rol se chequea **al aplicar**: un Empleado ve la tarjeta de una propuesta cuyo alcance es de la empresa y, al aplicarla, recibe 403 y nada se guarda.
- CA-03.3 `TopePropuestas` vale sin excepción. El chat libre **no es una tarea de trabajo**, así que su tope es **10**, igual que las otras conversaciones de plataforma.
- CA-03.4 Las cuatro cosas que se cargan quedan cubiertas: regla, instructivo, tarea programada y agente propio.
- CA-03.5 Un hecho que el agente aprenda se anota como **recuerdo rotulado sin confirmar**, por `IEscritorRecuerdos`, y **nunca** se convierte una instrucción en memoria.

**CU-04**
- CA-04.1 Se adjunta un documento al chat libre **sin cliente** y el agente lo lee con `adjunto_leer`.
- CA-04.2 `adjunto_leer` en el chat libre **solo** alcanza lo adjuntado a esa conversación: pedir la carpeta de un cliente, o el adjunto de otra tarea, no devuelve nada.
- CA-04.3 Ningún archivo se rechaza por su formato (M27), y lo guardado nunca se sirve con su propio tipo de contenido.

**CU-05**
- CA-05.1 Los chats libres aparecen en el historial del miembro y se reabren.
- CA-05.2 **Solo el autor continúa** un chat libre; un Director de la misma organización lo lee pero no puede enviar seguimiento; un miembro de **otra** organización recibe 404.

**CU-06**
- CA-06.1 Pedirle al chat libre algo que es de las tres conversaciones de plataforma produce una **derivación nombrada** (dónde se hace), no un intento de hacerlo.

**Diseño y motion (RF-07)**
- CA-07.1 La pantalla cumple la instrucción `38`: el compositor acoplado abajo, medida de lectura acotada, lo que no cambia nunca en el rótulo y no en el cuerpo, y la trazabilidad («ver pasos») visible como pastilla.
- CA-07.2 La pieza 3D **carga diferida**: no bloquea el primer render ni entra en la carga inicial de la pantalla.
- CA-07.3 Con `prefers-reduced-motion: reduce`, la pieza 3D y todas las transiciones se apagan y la pantalla **sigue completa y usable**.
- CA-07.4 Solo tokens `--ov-*`: la pantalla se ve bien a **1440 y a 390 px, en tema claro y oscuro**, verificada en navegador real con datos de verdad.
- CA-07.5 Si la pieza 3D no puede inicializarse (sin WebGL, o el script no cargó), **degrada en silencio** a su equivalente plano. Nunca deja un hueco ni un error visible.

**Transversal**
- CA-T.1 Multi-tenant: manipular ids en la mención, en el adjunto o en la URL del chat libre no muestra ni toca datos de otra organización.
- CA-T.2 **Ningún prompt se publica sin evaluación aprobada**, y el agente de chat libre entra en **Borrador** como todo artefacto. La suite común de seguridad (`00-suite-seguridad-agentes.yml`) corre con él también.
- CA-T.3 Agregar el formato de contexto nuevo **no cambia el hash de ninguna tarea vieja**: verificable porque la instantánea guarda qué versiones y qué formato vio cada tarea.
- CA-T.4 Nada sale hacia afuera sin el guardia de destinos de M11.

#### Alcance incluido / no incluido (Análisis)

**Incluido:** pantalla nueva de chat libre; cuarto agente de plataforma con su prompt, su suite de evaluación y su formato de contexto; resolución de menciones de agente y de configuración con autocomplete; apertura de tarea por mención con espera y despertar; adjuntos sin cliente; historial; motion con una pieza 3D acotada y diferida.

**No incluido:** streaming token a token; mencionar personas; mencionar clientes para traer su carpeta; reemplazar las cuatro conversaciones ni el catálogo; voz/audio; delegación en vivo dentro del mismo turno (descartada en P2).

#### Riesgos

- **R-01 (alto) — El chat libre se vuelve la única puerta y su prompt pasa a ser camino crítico.** Mitigación: las cinco puertas actuales **siguen existiendo y alcanzables**; una falla del chat libre degrada a «hay que entrar por el catálogo», no a «no se puede trabajar». Mismo criterio que M27 usó con `Agentes/Crear`.
- **R-02 (alto) — Costo.** Un hilo libre que menciona varios agentes multiplica tareas, y cada turno reenvía la conversación completa (riesgo conocido de PAT-029). Mitigación: tope de gasto de M6 sin tocar, costo visible por tarea y por hilo, cache de prompt sobre el historial, tope de seguimientos, y la elección de P2 que hace **visible y contable** cada delegación en vez de esconderla dentro de un turno.
- **R-03 (medio) — La mención se convierte en un canal de escalada de privilegios.** Una mención es texto que escribe la persona, y el modelo no puede ser el que decida si corresponde. Mitigación: la mención **solo resuelve** contra lo que esa persona ya podía usar (CA-02.2/02.3), y el rol se chequea **al aplicar** (CA-03.2). La mención entra **como dato**, nunca como orden.
- **R-04 (medio) — El hilo que queda esperando para siempre.** Si la tarea del agente mencionado falla o se cancela, el hilo libre podría quedar colgado en `EsperandoSubtareas`. Mitigación: CA-02.5 exige el despertar **en todo fin**, no solo en el feliz — es exactamente el defecto que M27 encontró con `CierreTurno`.
- **R-05 (medio) — El 3D se come la pantalla o el dispositivo.** Mitigación: una sola pieza, diferida, apagada por `prefers-reduced-motion`, con degradación silenciosa sin WebGL (CA-07.2/07.3/07.5).
- **R-06 (bajo) — El formato de contexto nuevo cambia hashes viejos.** Mitigación: CA-T.3, verificable por la instantánea.

#### Banderas tempranas (cerradas en Análisis)

- **Migración EF: sí.** Valor nuevo de `TipoTarea` y, según cómo se resuelvan las menciones, nada más. Se cierra en Arquitectura.
- **Prompt nuevo del núcleo: sí** (decisión P1), con suite de evaluación propia y la suite común de seguridad.
- **Formato de contexto nuevo: sí** (el 6), reutilizando el armado de plataforma.
- Integración externa: no. Máquina de estados nueva: no.

#### Clasificación de perfil de cliente

Producto **propio de Olvidata Soft**. Aprobador: Joaquín. **No corresponde precio al cliente ni descuentos**; la etapa 4 se omite (proyecto personal), igual que en los módulos anteriores.


## Historial de ajustes

- **M20 + M21 + M27** — 3 bloques (2026-09-24 a 2026-10-01) → [`1-analista-funcional-M20-M27.md`](historial/1-analista-funcional-M20-M27.md). Curaduria a mano: el archivo declara sus modulos en negrita, no en encabezados.


### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M08** — 9 bloques (2026-09-14 a 2026-09-15) → [`1-analista-funcional-M08.md`](historial/1-analista-funcional-M08.md)
- **M07** — 8 bloques → [`1-analista-funcional-M07-2.md`](historial/1-analista-funcional-M07-2.md)
- **M06** — 4 bloques → [`1-analista-funcional-M06-2.md`](historial/1-analista-funcional-M06-2.md)
- **M03** — 1 bloques → [`1-analista-funcional-M03-2.md`](historial/1-analista-funcional-M03-2.md)


### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M07** — 2 bloques (2026-09-14 a 2026-09-15) → [`1-analista-funcional-M07.md`](historial/1-analista-funcional-M07.md)
- **M06** — 6 bloques (2026-09-14 a 2026-09-15) → [`1-analista-funcional-M06.md`](historial/1-analista-funcional-M06.md)
- **M05** — 10 bloques (2026-09-14 a 2026-09-14) → [`1-analista-funcional-M05.md`](historial/1-analista-funcional-M05.md)
- **M04** — 21 bloques (2026-09-14 a 2026-09-14) → [`1-analista-funcional-M04.md`](historial/1-analista-funcional-M04.md)
- **M03** — 19 bloques (2026-09-14 a 2026-09-14) → [`1-analista-funcional-M03.md`](historial/1-analista-funcional-M03.md)

- 2026-09-14: Discovery + Análisis de M2 Organización (roles Director/Empleado, ABM de Áreas, miembros, cartera de clientes, permisos, visibilidad de tareas). 12 reglas, 17 criterios de aceptación, 4 riesgos, 5 preguntas con hipótesis.
- 2026-09-14: Gate aprobado por Joaquín con respuestas P1–P5. Cambios: alta de miembros pasa al SuperUsuario (RF-06, CU-06 ampliado, CU-03 sin alta); cliente de cartera con todos los datos y sin estado Activo/Inactivo; área opcional también para el Director; se elimina migración de usuarios existentes (R-04 descartado).
- 2026-09-14: Discovery + Análisis de M3 Reglas por alcance (constructor de contexto, vista previa, instantánea, versiones, límites). 10 CU, 12 RF, 15 CA, 5 riesgos, 9 preguntas con hipótesis. Pendiente gate de Joaquín.
- 2026-09-14: Gate M3 aprobado. P1 solo Director; P2 cualquier miembro; P3 al crear; P4 sí; P5 archivo del núcleo con evaluación; P6 en M3; P7 confirmados; P8 sí; P9 staff ve el texto de reglas de las organizaciones. Pedidos nuevos N-01 (agente configurador de reglas del Director, etapa propia después de M4) y N-02 (asistente que reparte tareas a empleados/subagentes, junto a M7 + tareas asignadas a personas).
- 2026-09-14: Discovery + Análisis de M3b Seguir conversando sobre una tarea. 5 CU, 10 RF, 14 CA, 4 riesgos, 8 preguntas con hipótesis (P6 retoma OBS-M3-1). Pendiente gate de Joaquín.
- 2026-09-14: Gate M3b aprobado con todas las hipótesis. Ajustes derivados: RF-M3b-01 incluye `Cancelada` (P3); RF-M3b-09 → tras cancelar se puede seguir; P6 suma al alcance ocultar el texto de preferencias personales ajenas en "Lo que el agente tuvo en cuenta" (el staff sigue viéndolo, P9 de M3).
- 2026-09-14: Discovery + Análisis de M4 Agentes de la organización (pendientes PA-01..07 abiertos por decisión de Joaquín). 11 CU, 15 RF, 15 CA, 4 riesgos, 11 preguntas con hipótesis. Pendiente gate de Joaquín.
- 2026-09-14: Gate M4 aprobado con todas las hipótesis. Ajuste derivado: RF-M4-10 → un agente archivado no admite tareas nuevas pero sí ajustes (M3b) en sus tareas existentes (P11-B).
- 2026-09-14: Discovery + Análisis de M4b Agente configurador de reglas del Director (N-01). 7 CU, 12 RF, 15 CA, 5 riesgos, 9 preguntas con hipótesis. Pendiente gate de Joaquín.
- 2026-09-15: Discovery + Análisis de M5 Workspace por cliente de cartera, **aprobado sin gate por autorización de Joaquín 2026-09-14**. 11 CU, 18 RF, 19 CA, 7 riesgos, 14 preguntas con la opción recomendada tomada (reemplazar `DocumentoCliente`, texto extraído sin visión, 20 MB / 1 GB / 200 / 1.000.000 / 10, baja por Director o autor, herramientas automáticas en tareas con cliente, adjuntar = referencia + lectura por herramientas, staff solo metadatos, baja con borrado físico, duplicados, extracción al subir, sin escritura del agente, sin documentos de empresa, simulador con guion, sin versiones).
- 2026-09-15: Discovery + Análisis de M6 Aprobaciones de acciones y límites de gasto, **aprobado sin gate por autorización de Joaquín 2026-09-14**. 14 CU, 25 RF, 22 CA, 8 riesgos, 16 preguntas con la opción recomendada (costo a precio de lista, USD 100 por defecto, límite de miembro ≤ organización, sin límites con API key propia, turno Fallida al llegar y seguir con ajuste, área actual, avisos in-app 80/100, nivel de aprobación en código, pedidos del paso a la vez, vencimiento 72 h, motivo opcional, bandeja + tarjeta, herramientas de demostración solo en Development). Facturación fuera (PLAN §8.1).
- 2026-09-15: Discovery + Análisis de M7 Subagentes, reglas propuestas por agentes y asistente del Director, **aprobado sin gate por autorización de Joaquín 2026-09-14**, dividido en M7a (subagentes + reglas propuestas) y M7b (asignaciones a personas + asistente). 17 CU, 38 RF, 38 CA, 10 riesgos, 26 preguntas con la opción recomendada (jerarquía del núcleo, profundidad 1, 5/10, estado "Esperando a otros agentes", sin ajustes en subtareas, costo propio + total, preferencias del autor y reglas del cliente con confirmación, asignaciones solo del Director con Vencida calculada, sin cierre automático ni recordatorios, asistente sin reglas de la empresa y tareas a nombre del Director que aplica). Depende de M6.
- 2026-09-16: Revisión y cierre del Análisis de M8 Evaluación automática de prompts (núcleo y agentes de la organización), **aprobado sin gate por autorización de Joaquín 2026-09-14**. Actualizado el estado: M1–M7 ya implementadas (244 tests), el asistente del Director (PA-14) entra como artefacto evaluable desde el día uno, los cuatro formatos de contexto tienen golden y los patrones nuevos son PAT-040/041 (PAT-038/039 quedaron tomados por M7). 11 CU, 25 RF, 24 CA, 8 riesgos, 20 preguntas con la opción recomendada (casos en el repositorio importados con el manifiesto, gate solo en Agente y Regla de plataforma, simulado que no publica, suite de seguridad común, revisor `claude-sonnet-5` distinto del evaluado, 1/2 repeticiones, seguridad y críticos al 100 % y generales al 90 %, reuso de la corrida de la publicada, control del revisor, tope USD 5 por corrida y USD 30 por mes, solo SuperUsuario gasta, sin Batches, la corrida aprueba sola, casos cambiados invalidan la aprobación, excepción manual auditada, uso a nombre de una organización técnica interna, casos iniciales redactados como borrador, herramientas nunca ejecutadas). Agentes de la organización fuera del alcance ejecutable (M8b).
