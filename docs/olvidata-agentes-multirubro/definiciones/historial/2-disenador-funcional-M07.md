<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/2-disenador-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 2-disenador-funcional - M07 (1 bloques archivados)

- M7 — Subagentes, reglas propuestas por agentes y asistente del Director que reparte trabajo

---

# M7 — Subagentes, reglas propuestas por agentes y asistente del Director que reparte trabajo

Estado: **aprobado sin gate por autorización de Joaquín 2026-09-14** (decisiones D-M7-1..24 tomadas con la opción recomendada y documentadas como hipótesis). Entrada: `1-analista-funcional.md` M7 (P1–P26 tomadas sin gate). **Dos etapas: M7a (subagentes + reglas propuestas por agentes de trabajo) y M7b (asignaciones a personas + asistente del Director).** Supone M6 implementado (tarjetas de aprobación, límites, contador en el menú). Criterio transversal: lenguaje llano y esconder complejidad (D-M3-8..12); estados con ícono + texto; tema oscuro con tokens verificados (DI-M5-17, lecciones OLV-001..004, PA-11).

### M7-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template M4b — `_TarjetasPropuesta`, `_ScriptPropuestas`, `ConfiguracionReglas/{Index, Nueva}`, conversación con chips (PAT-032) | Propuestas confirmables bajo el turno, lista de conversaciones compartida, arranque guiado | **Reutilizar**: tarjetas de regla propuesta por agentes de trabajo (mismo componente con tipos nuevos) y el asistente del Director completo con la misma estructura (lista, nueva, conversación, tarjetas, aplicar todas). |
| Template M6 — tarjeta de aprobación bajo el paso, estado de la tarea en palabras, bandeja con contador (`ContadorAprobaciones`) | Elementos embebidos en la conversación y contador del menú | **Reutilizar** ubicación y estructura para la tarjeta de subtarea y el contador de Asignaciones. |
| Template M5 — "Ver pasos" llano (D-M5-12), chips de adjuntos, colores verificados (DI-M5-17) | Rótulos sin JSON, contraste | **Reutilizar** para las herramientas de delegación y tokens de estado. |
| Template M3b — `_CuadroSeguimiento` con motivos, cierre de turno, `Tareas/Index` con filtros y Session | Conversación y listado | **Extender** con los motivos "esperando a otros agentes" y "es una parte" y el filtro "Partes". |
| Template M2/M3 — DataTables con filtros por columna y Session, formularios en cards, Select2, SweetAlert2, `Reglas/{Index, _Form, Detalle}` | Grillas, formularios, confirmaciones, reglas | **Reutilizar** en Asignaciones, formulario de asignación, card de propuestas en Reglas y precarga del formulario de regla. |
| century-21 (`docs/century-21/definiciones/2-disenador-funcional.md` A-03, `3-arquitecto-mvc.md`: bandeja con "Tomar" / "Reasignar a compañero" y "ya fue tomada por un compañero") | Asignación de trabajo entre personas con concurrencia | **Reutilizar el criterio** de reasignar y del mensaje de conflicto. |
| yoga (`docs/yoga/definiciones/2-disenador-funcional.md`: cuota "Vencida" derivada de Pendiente + vencimiento) | Estado derivado | **Reutilizar**: "Vencida" calculada y filtro. |
| ganaderia / yaghan-rental (bandeja de pendientes al iniciar sesión) | Contador y lista de pendientes | **Reutilizar el criterio** de contador; sin job diario. |
| Catálogo y demás proyectos | Sin delegación entre agentes IA en un bucle reanudable ni tareas a personas propuestas por un agente | **Diseño nuevo** → PAT-038 y PAT-039 propuestos (los agrega el orquestador). |

### M7-1. Alcance funcional resumido
**M7a.** Cuando el agente de una tarea es coordinador, puede pedirles partes del trabajo a sus subagentes: en la conversación aparece una tarjeta "Le pidió a «Tasador»" por cada parte, la tarea queda "Esperando a otros agentes" y sigue sola cuando las partes terminan, con su respuesta. Cada parte es una tarea con su propio detalle (enlace a la principal, sin cuadro de ajuste), su costo y sus aprobaciones; cancelar la principal cancela sus partes. En Tareas las partes se ocultan salvo que se pidan. Además, cualquier agente de trabajo puede proponer "una preferencia tuya" o "una regla para este cliente" como tarjeta: el autor (o un Director para reglas del cliente) la aplica, la edita o la descarta, desde la conversación o desde la card "Propuestas de agentes para revisar" en Reglas.
**M7b.** El Director reparte trabajo a personas en la pantalla **Asignaciones** (título, descripción, persona, cliente, vencimiento) o conversando con el asistente "Repartir trabajo conversando", que propone asignaciones y tareas para agentes como tarjetas. Cada miembro ve "Asignadas a mí" con contador en el menú, la empieza, la marca como hecha o se la pide a un agente (Nueva tarea precargada y vinculada).

### Decisiones de diseño M7 (hipótesis tomadas sin gate, autorización 2026-09-14)
**M7a**
- **D-M7-1 Nombres en pantalla.** La subtarea se llama **"parte"** ("Parte de la tarea #123"); el estado nuevo es **"Esperando a otros agentes"**; la acción del coordinador se cuenta como **"Le pidió a «X»"**. Nunca "subagente", "delegación" ni "tarea hija" en la UI de clientes.
- **D-M7-2 Tarjeta de parte** debajo del paso del modelo que la pidió (misma ubicación que las tarjetas de M4b y M6): ícono `fa-diagram-project`; encabezado "Le pidió a «Tasador»"; pedido recortado a 200 caracteres con plegado "Ver el pedido completo"; línea de estado con ícono + texto: "En cola" (reloj, gris) · "Trabajando" (spinner, azul) · "Espera una aprobación" (mano, ámbar, enlace "Resolver") · "Terminó" (check, verde) · "No pudo terminar: <motivo>" (círculo con cruz, rojo) · "Se canceló" (prohibido, gris); costo "USD 0,04"; con Terminó, plegado **"Ver la respuesta"**; enlace **"Abrir la parte #124"**; botón **"Cancelar esta parte"** (contorno peligro) si no terminó y la persona puede cancelar.
- **D-M7-3 Estado de la principal.** Badge "Esperando a otros agentes" en listado y detalle; bajo el encabezado: "Esperando a 2 agentes: Tasador y Redactor."; cuadro de seguimiento deshabilitado con "La tarea está esperando a otros agentes. Esperá la respuesta para seguir."; el progreso en vivo (SignalR) refresca las tarjetas cuando cambia una parte.
- **D-M7-4 Costo.** En el encabezado de una principal con partes: "Costo: USD 0,12 · con sus partes: USD 0,40". Sin partes, como hoy.
- **D-M7-5 Cancelar una principal con partes sin terminar**: SweetAlert2 "¿Cancelar la tarea? También se cancelan sus 2 partes que siguen trabajando." (sin partes, la confirmación actual).
- **D-M7-6 Detalle de una parte**: `ov-alert info` arriba: "Esta tarea es una parte de la tarea #123, pedida por «Orquestador»." + enlace **"Volver a la tarea principal"**; el mensaje inicial se rotula "Pedido de «Orquestador»" (no "Pedido"); cuadro de seguimiento reemplazado por "Para seguir, escribile a la tarea principal." con el mismo enlace; sin "Nueva tarea con este agente".
- **D-M7-7 Tareas.** Filtro nuevo **"Partes"**: "Ocultar" (por defecto) / "Mostrar"; en la columna Pedido, la principal suma el chip "2 partes" y una parte muestra el chip "Parte de #123" (enlace). Persistido en Session como el resto.
- **D-M7-8 "Ver pasos" llano** para las herramientas nuevas: "Consultó a qué agentes les puede pedir ayuda" · "Le pidió a «Tasador»: …" · "Recibió la respuesta de «Tasador»" / "«Tasador» no pudo terminar: …"; sin JSON (como D-M5-12).
- **D-M7-9 Tarjeta de regla propuesta por un agente de trabajo** (componente de D-M4b-4): tipo **"Preferencia de Laura Gómez"** o **"Regla del cliente «Panadería Norte»"** (con la línea "Solo para «Asistente de ventas»" si aplica a ese agente); título; texto (plegado si es largo); "Por qué"; nota chica fija "Una regla orienta al agente; no le da permisos."; botones **Aplicar** · **Editar y aplicar** · **Descartar**; sin badge de modo (no aplica a estos alcances). Quien no puede resolverla ve la tarjeta sin botones con "Solo Laura Gómez puede aplicarla." (preferencia) o nada extra (staff). Estados como M4b.
- **D-M7-10 Card "Propuestas de agentes para revisar (N)"** arriba de las pestañas de Reglas, solo si hay pendientes que la persona puede resolver: hasta 5 tarjetas compactas (tipo, título, agente y "Ver conversación") con las mismas acciones y "Ver todas (N)" que expande el resto.
- **D-M7-11 Origen en el historial de la regla**: badge "Propuesta de «Asistente de ventas»" (el badge de M4b toma el nombre del agente según el tipo de tarea) y enlace "Ver conversación" para quien puede ver esa tarea.

**M7b**
- **D-M7-12 Menú.** En "Principal", ítem **"Asignaciones"** (`fa-clipboard-list`) para todo miembro, con contador de Pendientes + En curso asignadas a mí (sin contador si es 0). Se usa "Asignaciones" en el menú y "tarea asignada" en los textos, para no confundir con "Tareas" (de agentes).
- **D-M7-13 Pantalla Asignaciones** con pestañas **"Asignadas a mí"** (por defecto) y **"Del equipo"** (solo Director). Encabezado del Director: **Nueva asignación** (primario) y **Repartir trabajo conversando** (secundario; deshabilitado con tooltip "Todavía no está disponible." sin versión publicada).
- **D-M7-14 Estados en palabras con ícono**: "Pendiente" (`fa-circle`, gris) · "En curso" (`fa-play`, azul) · "Hecha" (`fa-check`, verde) · "Cancelada" (`fa-ban`, gris); **"Vencida"** es un segundo badge rojo con `fa-triangle-exclamation` junto al estado ("Pendiente · Vencida").
- **D-M7-15 Formulario** en dos cards: **"¿Qué hay que hacer?"** (Título, Descripción con contador 0/4.000) y **"¿Quién y para cuándo?"** (Persona con Select2 "Nombre · Área", Cliente con Select2 opcional, Vence con fecha y chips "Hoy" · "Mañana" · "En una semana" · "Sin fecha"). Hint al pie: "La persona recibe un aviso. Lo que escribas es una indicación: no le da permisos nuevos a nadie."
- **D-M7-16 Detalle de asignación** en dos columnas (desktop) / apilado (mobile): izquierda título, estado, descripción y card **"Pedidos a agentes"** (tareas vinculadas: #, agente, estado, fecha, enlace); derecha card **"Datos"** (Persona, Asignada por, Cliente, Vence, Creada, Empezada, Hecha por/nota o Cancelada por/motivo, origen "Propuesta del asistente" con "Ver conversación" para Directores) y **acciones** según estado y rol.
- **D-M7-17 Confirmaciones.** "Marcar como hecha": SweetAlert2 con textarea "Nota (opcional)" 0/500. "Cancelar asignación": SweetAlert2 peligro con "Motivo (opcional)" 0/500. Empezar y Reabrir sin confirmación (toast).
- **D-M7-18 "Pedírsela a un agente"** (primario para la persona asignada) abre Agentes → Ejecutar con `asignacion={id}`: `ov-alert info` "Estás resolviendo la tarea asignada «Revisar balance». Podés cambiar el pedido antes de enviarlo."; pedido precargado "<título>\n\n<descripción>" y cliente; al crear, toast "Tarea creada. La asignación quedó En curso." y se abre el detalle de la tarea (con enlace "Asignación: «…»").
- **D-M7-19 Reasignar** es cambiar la Persona en Editar (sin botón aparte); si la persona actual ya no está activa, el detalle muestra `ov-alert warning` "La persona ya no está activa. Reasignala." con enlace a Editar (Director).
- **D-M7-20 Asistente** con la estructura de M4b: lista **"Repartir trabajo conversando"**, nueva conversación con chips "Repartí el trabajo de esta semana" · "¿Quién tiene más pendientes?" · "Pedile a un agente que…" · "Reasigná lo vencido", placeholder "Contame qué hay que hacer y quién está disponible…" y hint "El asistente no asigna nada por su cuenta: te muestra propuestas y vos las aplicás."
- **D-M7-21 Tarjeta de propuesta de trabajo**: tipo con ícono **"Asignar a Laura Gómez"** (`fa-user`) o **"Pedir a «CM del estudio»"** (`fa-robot`); título (asignación) o pedido (tarea de agente, plegado); Cliente; "Vence el 20/09" / "Sin fecha" (solo asignación); "Por qué"; acciones Aplicar · Editar y aplicar · Descartar; Aplicada: "Asignada · Ver asignación" o "Tarea #456 creada · Ver tarea"; No se pudo aplicar: motivo + Reintentar + Editar y aplicar.
- **D-M7-22 Tareas → filtro Tipo**: "Tareas" · "Configuración de reglas" · "Reparto de trabajo" (las dos últimas solo Director y staff).
- **D-M7-23 Colores** con los tokens de DI-M5-17 (verde #15803d / #86efac, ámbar #92400e / #fcd34d, rojo #b91c1c / #fca5a5, gris `--ov-gray-600` / `--ov-text-muted`, azul de acción #1a78b8 / marca en oscuro); badge "Esperando a otros agentes" y "En curso" con fondo suave y texto azul verificado (nunca `bg-info` con texto blanco); texto siempre presente.
- **D-M7-24 Guiones del simulador** (solo Development): "deleg" → una parte; "dos partes" → dos; "de ahora en más" o "prefer" → preferencia; "cliente" en ese mismo pedido → además regla del cliente; "repart" en el asistente → una asignación y una tarea de agente.

### Flujos de pantalla acordados M7

**M7a**

**P-M7a-01 Detalle de tarea principal** (ajuste de `Tareas/Detalle`, `_Conversacion`, `_CuadroSeguimiento`): tarjetas de parte bajo su paso (D-M7-2) en el orden en que se pidieron, después de las tarjetas de aprobación (M6) y antes de las de propuesta; estado y encabezado (D-M7-3, D-M7-4); cancelar (D-M7-5); tarjetas de regla propuesta en tareas de trabajo (D-M7-9); "Ver pasos" llano (D-M7-8). Staff: tarjetas sin botones.

**P-M7a-02 Detalle de una parte** (`Tareas/Detalle/{id}` de una subtarea): D-M7-6; tarjetas de aprobación (M6) iguales; "Lo que el agente tuvo en cuenta" como toda tarea.

**P-M7a-03 Tareas** (ajuste de `Tareas/Index`): D-M7-7.

**P-M7a-04 Reglas** (ajuste de `Reglas/Index`): D-M7-10. Vacío: la card no se muestra.

**P-M7a-05 Formulario de regla** (ajuste de `Reglas/Create` con `propuesta`): para miembros (no solo Director) cuando la propuesta es de una tarea de trabajo; precargado (alcance, cliente, agente, tipo, título, texto, etiquetas) + `ov-alert info` "Estás aplicando una regla que propuso «Asistente de ventas»."; al guardar "Propuesta aplicada." y vuelta a la tarjeta (o a Reglas si se abrió desde la card).

**P-M7a-06 Detalle de regla** (ajuste): D-M7-11.

**M7b**

**P-M7b-01 Asignaciones** (`Asignaciones/Index?pestana=mias|equipo`)
- Encabezado: "Asignaciones" · descripción "Tareas que el equipo tiene que hacer. Podés resolverlas vos o pedírselas a un agente." · botones del Director (D-M7-13).
- Grilla DataTables: Título (enlace) · Cliente · Persona (solo "Del equipo") · Asignada por · Vence ("20/09/2026", badge Vencida) · Estado (D-M7-14) · Actualizada · acción **Ver**. Filtros por columna: Título (texto), Cliente (Select2 con "Sin cliente"), Persona (Select2, equipo), Asignada por (Select2), Vence (rango + casilla "Solo vencidas"), Estado (Select2; por defecto "Pendiente y En curso"), Actualizada (rango); Session por pestaña; **Limpiar filtros**. Búsqueda global sobre título, descripción, cliente, persona, fechas visibles y estado. Orden inicial: Vence asc (sin fecha al final).
- Vacío "Asignadas a mí": "No tenés tareas asignadas." · "Del equipo": "Todavía no hay tareas asignadas. Creá una o repartí el trabajo conversando."
- Mobile: Título + Vence + Estado; resto en detalle expandible.

**P-M7b-02 Nueva / Editar asignación** (`Asignaciones/Nueva`, `Asignaciones/Editar/{id}`; Director): D-M7-15. Editar solo en Pendiente o En curso. Con `propuesta` en la URL: precargado + `ov-alert info` "Estás aplicando una propuesta del asistente." y al guardar vuelve a la tarjeta. Guardar → detalle con toast "Asignación creada." / "Asignación actualizada.".

**P-M7b-03 Detalle de asignación** (`Asignaciones/Detalle/{id}`): D-M7-16, D-M7-17, D-M7-19. Acciones visibles según la máquina de estados:
| Estado | Persona asignada | Director |
|---|---|---|
| Pendiente | Empezar · Pedírsela a un agente · Marcar como hecha | Editar · Cancelar (+ las de la persona si es él) |
| En curso | Pedírsela a un agente · Marcar como hecha | Editar · Cancelar · Marcar como hecha |
| Hecha | Reabrir | Reabrir |
| Cancelada | — | — |

**P-M7b-04 Nueva tarea desde una asignación** (ajuste de `Agentes/Ejecutar`): D-M7-18. Si el cliente de la asignación está dado de baja: se precarga sin cliente con `ov-alert warning` "El cliente «X» se dio de baja: la tarea va sin cliente.".

**P-M7b-05 Repartir trabajo conversando — conversaciones** (Director; estructura de P-M4b-02): "Repartir trabajo conversando" · "Contale al asistente qué hay que hacer. Te propone a quién asignarlo o qué pedirle a un agente, y vos decidís." · **Nueva conversación**; grilla Iniciada · Por · Última actividad · Pendientes · Aplicadas · Estado, filtros y Session. Vacío: "Todavía no hay conversaciones. Empezá una y contale qué hay que hacer."

**P-M7b-06 Nueva conversación** (estructura de P-M4b-03): D-M7-20; mensaje hasta 10.000 caracteres; **Empezar** (Ctrl+Enter).

**P-M7b-07 Conversación del asistente** (estructura de P-M4b-04): encabezado "Reparto de trabajo · 15/09/2026" · Por · costo · "N propuestas pendientes"; tarjetas (D-M7-21) bajo cada respuesta y **Aplicar todas (N)** con 2 o más; "Aplicar todas": SweetAlert2 "Se van a aplicar 4 propuestas. Las que no se puedan aplicar quedan marcadas con el motivo." → toast "3 aplicadas, 1 no se pudo aplicar". Cuadro de seguimiento solo para el autor, placeholder "Pedile otro reparto o que ajuste una propuesta…". Sin "Lo que el agente tuvo en cuenta".

**P-M7b-08 Tareas** (ajuste): D-M7-22.

**P-M7b-09 Núcleo IP** (staff): el asistente aparece como artefacto de la plataforma con el flujo de versiones y evaluación existente.

**Notificaciones** (campana del template, con enlace):
| Evento | Destinatario | Título | Mensaje |
|---|---|---|---|
| Asignación creada | Persona | "Te asignaron una tarea" | "Martín Pérez te asignó «Revisar balance» (Panadería Norte), vence el 20/09." |
| Reasignada | Nueva persona / anterior | "Te asignaron una tarea" / "Ya no tenés asignada una tarea" | "…«Revisar balance»." / "«Revisar balance» ahora la tiene Martín Gómez." |
| Cambió el vencimiento | Persona | "Cambió el vencimiento de una tarea" | "«Revisar balance» ahora vence el 22/09." |
| Cancelada | Persona | "Se canceló una tarea asignada" | "Martín Pérez canceló «Revisar balance»[: motivo]." |
| Hecha | Quien la creó (si no fue él) | "Terminaron una tarea asignada" | "Laura Gómez marcó como hecha «Revisar balance»[: nota]." |

### ViewModels definidos M7
| ViewModel | Campos y validaciones |
|---|---|
| `ParteTarjetaViewModel` | `TareaId, Agente, Pedido, PedidoRecortado, Estado, EstadoTexto, Motivo?, CostoUsd, Respuesta?, EsperaAprobacion, PuedeCancelar, Version` |
| `TareaDetalleViewModel` (ajuste) | + `PartesPorPaso`, `TareaPrincipal?` (`Id`, `Agente`), `EsParte`, `CostoConPartesUsd?`, `EsperandoAgentesTexto?`, `PropuestasPorPaso` también en tareas de trabajo; `MotivoNoPuedeSeguir` + `EsperandoOtrosAgentes`, `EsParte` |
| `TareaListItem` (ajuste JSON) | + `tareaPrincipalId?`, `partes` |
| `TareaFiltrosViewModel` (ajuste) | + `Partes` ("ocultar" por defecto / "mostrar"); `Tipo` + "reparto" |
| `PropuestaReglaViewModel` (ajuste) | + `TipoTexto` ("Preferencia de …" / "Regla del cliente «…»"), `SoloParaAgente?`, `AgenteOrigen`, `NoPuedeAccionarTexto?` |
| `PropuestasAgentesReglasViewModel` | `Total`, `Items[]` (`PropuestaReglaViewModel` + `TareaId`) |
| `AsignacionListItem` (JSON) | `id, titulo, cliente, persona, personaActiva, asignadaPor, vence, vencida, estado, estadoTexto, actualizada` |
| `AsignacionFiltrosViewModel` | `Pestana` (mias/equipo) · `Titulo` · `ClienteId` (id o "sin") · `PersonaId` (solo equipo) · `AsignadaPorId` · `Estados[]` · `SoloVencidas` · `VenceDesde/Hasta` · `ActualizadaDesde/Hasta` |
| `AsignacionFormViewModel` | `Id?` · `Titulo` [Required "Escribí qué hay que hacer."] [StringLength 150 "El título admite hasta 150 caracteres."] · `Descripcion?` [StringLength 4000 "La descripción admite hasta 4.000 caracteres."] · `AsignadaAUsuarioId` [Required "Elegí a quién se la asignás."] · `ClienteCarteraId?` · `VenceEl?` (fecha; servidor: ≥ hoy AR "La fecha tiene que ser hoy o más adelante.") · `PropuestaId?` · `Version?` |
| `AsignacionDetalleViewModel` | `Id, Titulo, Descripcion, Estado, EstadoTexto, Vencida, Persona, PersonaActiva, AsignadaPor, Cliente?, ClienteId?, VenceEl?, CreadaAt, IniciadaAt?, HechaAt?, HechaPor?, NotaCierre?, CanceladaAt?, CanceladaPor?, MotivoCancelacion?, ConversacionOrigenId?, TareasVinculadas[] {Id, Agente, EstadoTexto, Creada}, PuedeEditar, PuedeCancelar, PuedeEmpezar, PuedeMarcarHecha, PuedeReabrir, PuedePedirAAgente, Version` |
| `MarcarHechaViewModel` | `Id` · `Version` · `Nota?` [StringLength 500 "La nota admite hasta 500 caracteres."] |
| `CancelarAsignacionViewModel` | `Id` · `Version` · `Motivo?` [StringLength 500 "El motivo admite hasta 500 caracteres."] |
| `EjecutarAgenteViewModel` (ajuste) | + `TareaAsignadaId?`, `AsignacionTitulo?`, `AvisoClienteDadoDeBaja?` |
| `IniciarAsistenteViewModel` | `Texto` [Required "Contame cómo querés repartir el trabajo."] [StringLength 10000 "El mensaje admite hasta 10.000 caracteres."] |
| `ConversacionAsistenteListItem` (JSON) | igual a `ConversacionConfiguracionListItem` |
| `PropuestaTrabajoViewModel` | `Id, Tipo (AsignarPersona/TareaAgente), Estado, Persona?, PersonaActiva, Agente?, Titulo?, Texto, Cliente?, VenceEl?, PorQue?, MotivoFallo?, ResultadoAsignacionId?, ResultadoTareaId?, PuedeAccionar, Version` |
| `AplicarTodasResultadoViewModel` (JSON) | reuso M4b: `aplicadas`, `fallidas[] {id, motivo}` |

### Validaciones de UI M7
| Caso | Mensaje |
|---|---|
| Ajuste a una principal esperando partes | "La tarea está esperando a otros agentes. Esperá la respuesta para seguir." |
| Ajuste a una parte | "Esta tarea es una parte de la tarea #123. Para seguir, escribile a la tarea principal." |
| Cancelar una parte ya terminada | "Esta parte ya terminó." |
| Preferencia propuesta resuelta por otra persona que no es el autor (JSON 403) | "Solo Laura Gómez puede aplicar esta preferencia." |
| Regla del cliente sin permiso (JSON 403) | "Solo quien pidió la tarea o un Director puede aplicar esta regla." |
| Propuesta ya resuelta / falla al aplicar / OK | reuso M4b: "Esta propuesta ya fue resuelta." · mensaje del servicio de reglas · "Propuesta aplicada." / "Propuesta descartada." |
| Título vacío / largo | "Escribí qué hay que hacer." · "El título admite hasta 150 caracteres." |
| Descripción larga | "La descripción admite hasta 4.000 caracteres." |
| Persona vacía / no activa / de otra organización | "Elegí a quién se la asignás." · "Esa persona ya no está activa en la empresa." · 404 |
| Cliente dado de baja o de otra organización | "El cliente elegido no existe." |
| Vencimiento en el pasado | "La fecha tiene que ser hoy o más adelante." |
| Editar una asignación Hecha o Cancelada | "Esta asignación ya está hecha o cancelada: no se puede editar." |
| Transición no válida (ej. marcar hecha una Cancelada) | "Esta asignación ya no admite esa acción. Recargá la página." |
| Conflicto de versión | "Otra persona cambió esta asignación. Recargá la página." |
| Asignación ajena (Empleado) | 404 |
| Empleado en Nueva/Editar/Cancelar o asistente | 403 |
| Pedírsela a un agente sin ser la persona asignada | "Solo la persona asignada puede pedírsela a un agente." |
| OK asignaciones | "Asignación creada." · "Asignación actualizada." · "Empezaste la tarea." · "Marcaste la tarea como hecha." · "Reabriste la tarea." · "Asignación cancelada." · "Tarea creada. La asignación quedó En curso." |
| Asistente sin publicar / mensaje vacío o largo | "Todavía no está disponible." · "Contame cómo querés repartir el trabajo." · "El mensaje admite hasta 10.000 caracteres." |
| Propuesta del asistente que falla al aplicar | mensaje del servicio (persona no activa, agente no disponible, límite de gasto, suscripción, cliente) |

### Maquina de estados M7

**Tarea del motor (transiciones nuevas)**
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| En curso | Terminó el recorrido del paso con partes sin terminar y sin aprobaciones pendientes | Esperando a otros agentes | partes creadas y guardadas | suelta el motor (sin lease) | carrera perdida → otro proceso sigue |
| Esperando a otros agentes | Terminó la última parte del paso (aviso o barrido) | En cola | versión de la tarea; sin aprobaciones pendientes del paso | reinicia intentos | conflicto → reintento del aviso o del barrido |
| Esperando a otros agentes | Cancelar | Cancelada | permiso de cancelar (M2) | partes no terminadas → Cancelada (con sus aprobaciones pendientes) en el mismo guardado; cierre de turno en cada una | — |
| Esperando a otros agentes | Ajuste | sin cambio | — | — | "La tarea está esperando a otros agentes…" |
| Espera aprobación (M6) | Se resuelve la última aprobación y quedan partes sin terminar | En cola → (al retomar) Esperando a otros agentes | — | no llama al modelo | — |

**Parte (subtarea)**
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | El coordinador pide ayuda a un subagente | En cola | tarea principal de trabajo; subagente permitido; topes; límite M6; cliente y documentos válidos; sin parte previa para ese pedido | crea la parte (autor, cliente, instantánea, nota del coordinador) | motivo devuelto al coordinador, sin parte |
| En cola / Trabajando / Espera aprobación | Termina, falla o se cancela | Completada / Fallida / Cancelada | — | avisa a la principal | — |
| cualquiera | Ajuste | sin cambio | — | — | "Esta tarea es una parte…" |

**Propuesta de regla de un agente de trabajo** (máquina de M4b con guardas nuevas)
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Herramienta del agente | Pendiente | tarea principal de trabajo; autor activo; alcance preferencia o cliente (con cliente vigente); ≤ 3 por paso; largos | guarda propuesta | motivo al agente |
| Pendiente / No se pudo aplicar | Aplicar / Editar y aplicar / Reintentar | Aplicada | preferencia: autor; cliente: autor o Director; validaciones de Reglas | crea la regla con origen | límite / cliente dado de baja → No se pudo aplicar |
| Pendiente / No se pudo aplicar | Descartar | Descartada | mismas guardas de permiso | — | 403 |

**Asignación**
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Crear (formulario o propuesta aplicada) | Pendiente | Director; persona activa; cliente vigente; vence ≥ hoy | notifica a la persona | validaciones |
| Pendiente | Empezar | En curso | persona asignada o Director; versión | registra inicio | 403 / conflicto |
| Pendiente | Pedírsela a un agente (tarea creada) | En curso | persona asignada; tarea válida | vincula la tarea en el mismo guardado | errores de Nueva tarea |
| En curso | Pedírsela a un agente | En curso | persona asignada | vincula otra tarea | ídem |
| Pendiente / En curso | Marcar como hecha | Hecha | persona asignada o Director; versión | registra quién, cuándo y nota; notifica a quien la creó | 403 / conflicto |
| Hecha | Reabrir | En curso | persona asignada o Director | limpia hecha | 403 |
| Pendiente / En curso | Editar (incluye reasignar) | igual | Director; validaciones | notifica según cambio | "ya está hecha o cancelada" |
| Pendiente / En curso | Cancelar | Cancelada | Director | registra motivo; notifica | 403 |
| Hecha / Cancelada | Editar / Cancelar / Empezar | — | — | — | "ya no admite esa acción" |

**Propuesta del asistente**
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Herramienta del asistente | Pendiente | conversación del asistente; autor Director activo; ≤ 10 por paso; persona activa / agente disponible / cliente vigente / vence ≥ hoy | guarda propuesta | motivo al asistente |
| Pendiente / No se pudo aplicar | Aplicar / Editar y aplicar / Reintentar | Aplicada | Director; validaciones del servicio de asignaciones o de tareas (suscripción, límite M6) | crea la asignación o la tarea con origen en el mismo guardado | → No se pudo aplicar con motivo |
| Pendiente / No se pudo aplicar | Descartar | Descartada | Director | — | — |

### Permisos por pantalla / accion M7
| Acción | Director | Empleado (autor / asignado) | Empleado (otro) | Staff |
|---|:---:|:---:|:---:|:---:|
| P-M7a-01/02 Ver partes y tarjetas | ✅ | ✅ | 404 | ✅ lectura |
| Cancelar principal o parte | ✅ | ✅ | 404 | ❌ |
| Aplicar/descartar preferencia propuesta | ❌ 403 (sin botones) | ✅ autor | 404 | ❌ |
| Aplicar/descartar regla del cliente propuesta | ✅ | ✅ autor | 404 | ❌ |
| P-M7a-04 Card de propuestas en Reglas | ✅ las que puede resolver | ✅ las suyas | — | ❌ |
| P-M7b-01 "Asignadas a mí" | ✅ | ✅ | ✅ | ❌ (portal: 403) |
| P-M7b-01 "Del equipo" | ✅ | ❌ | ❌ | ❌ |
| P-M7b-02 Nueva / Editar | ✅ | 403 | 403 | ❌ |
| P-M7b-03 Detalle | ✅ | ✅ asignado | 404 | ❌ |
| Empezar / Marcar como hecha / Reabrir | ✅ | ✅ asignado | 404 | ❌ |
| Cancelar asignación | ✅ | 403 | 404 | ❌ |
| P-M7b-04 Pedírsela a un agente | ✅ si es el asignado | ✅ asignado | 404 | ❌ |
| P-M7b-05/06 Asistente: listar e iniciar | ✅ | 403 | 403 | 👁 conversaciones desde Tareas |
| Seguir conversando con el asistente | ✅ autor | — | — | ❌ |
| Aplicar / descartar / aplicar todas (asistente) | ✅ | 403 | 403 | ❌ |

### Contratos funcionales para Services M7
| Contrato | Operaciones | Reglas |
|---|---|---|
| Partes (subtareas) | subagentes permitidos para una tarea · preparar una parte desde el pedido del coordinador · resultado para el coordinador · avisar a la principal cuando termina una parte · barrido de principales en espera · tarjetas por paso · cancelar en cascada | RF-M7a-01..14 |
| Motor (extensión) | ofrecer herramientas de ayuda solo a principales con coordinador · recorrido del paso con partes y aprobaciones · espera y retorno · nota del coordinador en la conversación de la parte | RF-M7a-02, 03, 06, 07, 12 |
| Tareas (extensión) | filtro Partes y contador · detalle con partes, principal, costo total y motivos nuevos · ajuste bloqueado · cancelar en cascada · crear tarea vinculada a una asignación · tipo "Reparto de trabajo" | RF-M7a-08..11, 14; RF-M7b-06, 17 |
| Propuestas de reglas (extensión) | herramienta de propuesta para agentes de trabajo · permisos por tipo (autor / Director) · pendientes que puedo resolver · aplicar con origen del agente | RF-M7a-15..21 |
| Asignaciones | listar (mías / equipo) · contar mías abiertas · detalle · crear · editar/reasignar · empezar · marcar hecha · reabrir · cancelar · datos para pedírsela a un agente · notificaciones | RF-M7b-01..10 |
| Asistente | disponible? · iniciar · listar conversaciones · herramientas de lectura acotadas · proponer asignación / tarea de agente | RF-M7b-11..13, 16, 17 |
| Propuestas del asistente | listar por conversación · aplicar (asignación o tarea) · aplicar todas · descartar · datos para precargar | RF-M7b-13..15 |
| Núcleo | prompt del asistente versionado y evaluado | RF-M7b-16 |

### M7-6. Impacto funcional por capa
- **Presentación:** tarjetas de parte, estado "Esperando a otros agentes", detalle de parte, filtro Partes, Ver pasos llano, tarjetas de regla propuesta en tareas de trabajo, card en Reglas, precarga del formulario para miembros; pantalla Asignaciones con pestañas, formulario, detalle con acciones, contador en el menú, Nueva tarea desde una asignación; asistente (lista, nueva, conversación con tarjetas), filtro Tipo.
- **Negocio:** subagentes permitidos, creación de partes con contexto del autor, topes, límites, espera y retorno, cancelación en cascada; propuestas de reglas con permisos por tipo; asignaciones con estados, permisos, vencida calculada, reasignación, notificaciones, vínculo con tareas; asistente con lectura acotada y propuestas aplicadas por los servicios.
- **Datos:** datos de parte en la tarea (principal, pedido de origen, profundidad), estado nuevo de tarea, asignaciones, propuestas del asistente, vínculo tarea ↔ asignación.

### M7-7. Riesgos y supuestos
- R-M7-01..10 heredados (costo por delegaciones, escalamiento o inyección vía texto, principal trabada, parte duplicada, ruido en Tareas, reglas propuestas equivocadas, asignaciones olvidadas, calidad de prompts, partes en serie, confusión Tareas/Asignaciones).
- R-M7-11 (medio, nuevo) **Muchas tarjetas en una respuesta** (aprobaciones + partes + propuestas) → orden fijo (aprobaciones, partes, propuestas), tarjetas compactas y plegados.
- R-M7-12 (bajo, nuevo) Asignación con cliente dado de baja al pedírsela a un agente → tarea sin cliente con aviso (P-M7b-04).
- R-M7-13 (bajo, nuevo) El estado nuevo de la tarea no contemplado en algún badge, filtro o búsqueda existente → lista de lugares en la arquitectura y QA recorre Tareas, Configuraciones y Aprobaciones.
- **Hipótesis heredadas del análisis que este diseño asume:** P1 (dos etapas), P2 (jerarquía del núcleo), P3 (profundidad 1), P4 (5/10), P5 (estado nuevo), P6 (sin ajustes en partes), P7 (costo propio + total), P8 (partes ocultas), P9 (respuesta recortada), P10 (cascada y cancelación individual), P11 (preferencia y cliente, solo nuevas), P12 (autor / Director), P13 (tarjeta + card en Reglas), P14 (3 por respuesta), P15 (solo Director asigna), P16 (estados con Reabrir), P17 (sin cierre automático), P18 (sin recordatorios), P19 (asistente sin reglas de la empresa), P20 (tarea a nombre del Director que aplica), P21 (asistente propone a coordinadores), P22 (staff sin asignaciones), P23 (prompt borrador), P24 (guiones del simulador), P25 (Empleado no ve asignaciones ajenas), P26 (QA con rubro ya importado). Supuestos S-M7-01..06 (en especial S-M7-01: M6 implementado).
- D-M7-1..24 tomadas sin gate.

### M7-8. Plan funcional por etapas (para el arquitecto)
**M7a**
1. Datos de parte en la tarea y estado "Esperando a otros agentes"; subagentes permitidos y creación de partes con contexto del autor.
2. Motor: herramientas de ayuda, recorrido del paso con partes y aprobaciones, espera, aviso y barrido, resultado al coordinador, nota del coordinador.
3. Tareas: tarjetas de parte, detalle de parte, costo total, cancelación en cascada, filtro Partes, Ver pasos llano.
4. Reglas propuestas por agentes de trabajo: herramienta, permisos por tipo, tarjetas en la conversación, card en Reglas, precarga para miembros, origen en historial.
5. Simulador con guiones de delegación y propuesta; QA.

**M7b**
6. Asignaciones: datos, servicio con estados, permisos y notificaciones; pantalla, formulario, detalle, contador.
7. Pedírsela a un agente: Nueva tarea precargada y vínculo.
8. Asistente: tipo de conversación y contexto propio, prompt borrador, herramientas de lectura y propuesta.
9. Propuestas del asistente: tarjetas, aplicar / editar y aplicar / descartar / aplicar todas, lista de conversaciones, filtro Tipo.
10. Simulador con guion del asistente; QA.

### Historias de usuario M7
**M7a**
- **HU-M7a-01** Como miembro, quiero que un agente coordinador reparta mi pedido entre agentes especializados, para no tener que pedirle a cada uno por separado. *CA:* CA-M7a-01, CA-M7a-04, CA-M7a-07; D-M7-2, D-M7-3.
- **HU-M7a-02** Como miembro, quiero ver qué le pidió el coordinador a cada agente, cómo va y qué respondió. *CA:* CA-M7a-01, CA-M7a-10; D-M7-2, D-M7-6, D-M7-8.
- **HU-M7a-03** Como responsable de Olvidata, quiero que la delegación tenga topes y respete los límites de gasto. *CA:* CA-M7a-05, CA-M7a-06, CA-M7a-13; D-M7-4.
- **HU-M7a-04** Como miembro, quiero cancelar una tarea con todas sus partes, o solo una parte. *CA:* CA-M7a-09; D-M7-5.
- **HU-M7a-05** Como responsable de Olvidata, quiero que ningún texto le dé a un agente acceso a otros agentes, clientes o permisos. *CA:* CA-M7a-02, CA-M7a-03, CA-M7a-18.
- **HU-M7a-06** Como miembro, quiero que una tarea que espera a otros agentes no quede trabada si algo se corta. *CA:* CA-M7a-08, CA-M7a-14.
- **HU-M7a-07** Como miembro, quiero que Tareas no se llene de partes, pero poder verlas si las busco. *CA:* CA-M7a-11, CA-M7a-12; D-M7-7.
- **HU-M7a-08** Como miembro, quiero que lo que le enseño a un agente conversando me lo proponga como preferencia, para no repetirlo en cada tarea. *CA:* CA-M7a-15, CA-M7a-16, CA-M7a-19; D-M7-9.
- **HU-M7a-09** Como miembro o Director, quiero confirmar las reglas de un cliente que propone un agente, sin que se apliquen solas. *CA:* CA-M7a-17, CA-M7a-20; D-M7-9.
- **HU-M7a-10** Como miembro, quiero ver en Reglas las propuestas pendientes aunque no abra la tarea. *CA:* CA-M7a-21; D-M7-10, D-M7-11.
- **Transversal** CA-M7a-22 (tema oscuro y mobile) aplica a HU-M7a-01..10.

**M7b**
- **HU-M7b-01** Como Director, quiero asignar tareas a las personas de mi equipo con fecha y cliente, para saber quién hace qué. *CA:* CA-M7b-01, CA-M7b-02; D-M7-13, D-M7-15.
- **HU-M7b-02** Como miembro, quiero ver lo que me asignaron y marcar lo que voy haciendo. *CA:* CA-M7b-03, CA-M7b-06; D-M7-12, D-M7-14, D-M7-16, D-M7-17.
- **HU-M7b-03** Como miembro, quiero pedirle a un agente que resuelva una tarea que me asignaron, sin volver a escribirla. *CA:* CA-M7b-04; D-M7-18.
- **HU-M7b-04** Como Director, quiero reasignar o cancelar tareas y enterarme cuando se terminan. *CA:* CA-M7b-07, CA-M7b-08; D-M7-19.
- **HU-M7b-05** Como miembro, quiero la tranquilidad de que nadie más ve lo que me asignaron salvo los Directores. *CA:* CA-M7b-05.
- **HU-M7b-06** Como Director, quiero contarle al asistente qué hay que hacer y recibir propuestas de a quién asignarlo o qué pedirle a un agente. *CA:* CA-M7b-09, CA-M7b-10; D-M7-20, D-M7-21.
- **HU-M7b-07** Como Director, quiero aplicar, corregir o descartar lo que propone el asistente, y que nada se cree sin mi confirmación. *CA:* CA-M7b-11, CA-M7b-12.
- **HU-M7b-08** Como responsable de Olvidata, quiero que el asistente solo lea lo necesario de la organización y que solo lo usen los Directores. *CA:* CA-M7b-13, CA-M7b-14.
- **Transversal** CA-M7b-15 (hash) y CA-M7b-16 (tema oscuro y mobile) aplican a HU-M7b-01..08.

---
