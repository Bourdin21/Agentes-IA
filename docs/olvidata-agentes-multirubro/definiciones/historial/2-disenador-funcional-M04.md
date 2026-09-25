<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/2-disenador-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 2-disenador-funcional - M04 (2 bloques archivados)

- M4b — Agente configurador de reglas del Director
- M4 — Agentes de la organización

---

# M4b — Agente configurador de reglas del Director

Estado: **aprobado por Joaquín el 2026-09-14** con D-M4b-1..9 ("continuar"). Entrada: `1-analista-funcional.md` M4b aprobado 2026-09-14 (P1–P9). Criterio transversal: lenguaje llano, esconder complejidad (D-M3-8..12).

### M4b-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template M3b — `Tareas/_Conversacion`, `_CuadroSeguimiento`, refresco en vivo | Conversación con ajustes | **Reutilizar**: la configuración es una conversación M3b con tarjetas de propuesta embebidas. |
| Template M3 — `Reglas/_Form`, `Detalle` con historial, pestañas | ABM de reglas | **Reutilizar**: "Editar y aplicar" = formulario precargado; origen en el historial. |
| Template M4 — tarjetas del catálogo, sugerencias | Cards y activación | **Reutilizar** estilo de tarjeta y activación de sugerencias. |
| crm-olvidata (`docs/crm-olvidata/definiciones/3-arquitecto-mvc.md`) | Function calling: el modelo devuelve la acción y la ejecuta el servicio de negocio | **Reutilizar el criterio** para propuestas. |
| Catálogo y demás proyectos | Sin propuestas de cambios generadas por un agente con confirmación por tarjeta | **Diseño nuevo** → PAT-032. |

### M4b-1. Alcance funcional resumido
El Director conversa con el configurador de Olvidata dentro de Reglas; el agente consulta lo que el Director puede ver y devuelve propuestas (regla nueva, cambio, desactivación, activar sugerencia) como tarjetas; el Director aplica, edita y aplica, descarta o aplica todas; las reglas registran el origen; el costo se ve en Tareas.

### Decisiones de diseño M4b a validar en el gate
- **D-M4b-1 Entrada.** Botón secundario **"Configurar conversando"** en el encabezado de Reglas (solo Director) + invitación en la pestaña "De la empresa" cuando está vacía: "¿Preferís contarlo con tus palabras? Configurá conversando."
- **D-M4b-2 Lista de conversaciones compartida entre Directores.** Todos los Directores ven las conversaciones de configuración de la empresa; solo su autor sigue conversando (regla M3b), pero **cualquier Director puede aplicar o descartar propuestas pendientes**.
- **D-M4b-3 El configurador no recibe las reglas de la empresa como instrucciones**: las lee como datos con sus herramientas (así "Tono formal" no le cambia la forma de trabajar al configurador). En pantalla no se muestra "Lo que el agente tuvo en cuenta" en estas conversaciones.
- **D-M4b-4 Tarjeta de propuesta** con: tipo ("Nueva regla" / "Cambio en «Tono formal»" / "Desactivar «…»" / "Activar sugerencia «…»"), **Dónde aplica** en palabras, badge "Siempre" / "Salvo que se indique otra cosa", título, texto (plegado si es largo), **"Por qué"** (una línea del agente), y para cambios **Antes / Después** apilados.
- **D-M4b-5 Cambio desde la propuesta.** Si la regla cambió después de la propuesta, al aplicar se abre un modal con la versión actual y la propuesta: **Aplicar igual** · **Editar y aplicar** · Cancelar.
- **D-M4b-6 Editar y aplicar** lleva al formulario de regla precargado con un aviso arriba "Estás aplicando una propuesta del configurador"; al guardar vuelve a la conversación, a la tarjeta.
- **D-M4b-7 Arranque guiado.** El cuadro de la primera pregunta tiene chips que completan el texto: "Cómo hablamos con los clientes" · "Cosas que nunca hacemos" · "Revisá mis reglas actuales" · "Reglas para un área".
- **D-M4b-8 Tareas.** Filtro "Tipo": Tareas / Configuración de reglas (esta opción solo para Directores y staff).
- **D-M4b-9 Origen en el historial.** Badge "Propuesta del configurador" en el detalle de la regla; enlace "Ver conversación" solo para Directores y staff (el Empleado ve el badge sin enlace).

### Flujos de pantalla acordados M4b

**P-M4b-01 Reglas** (ajuste): encabezado con botón **Configurar conversando** (Director; si no hay versión publicada del configurador: deshabilitado con tooltip "Todavía no está disponible."); invitación de D-M4b-1.

**P-M4b-02 Configurar reglas — conversaciones** (Director)
- Encabezado: "Configurar reglas conversando" · "Contale al configurador cómo trabaja tu empresa. Te propone reglas y vos decidís cuáles aplicar." · botón primario **Nueva conversación**.
- Grilla DataTables: Iniciada · Por · Última actividad · Pendientes (badge ámbar si > 0) · Aplicadas · Estado; filtros por columna (Por, Pendientes: Con/Sin, Estado, rangos de fecha), Session, Limpiar; acción **Abrir**.
- Vacío: "Todavía no hay conversaciones. Empezá una y contale cómo trabajan."

**P-M4b-03 Nueva conversación**
- Card "¿Qué querés configurar?": chips de D-M4b-7 · textarea (6 filas, contador 0 / 10.000) con placeholder "Contame cómo trabaja tu empresa: qué hacer siempre, qué evitar, cómo hablarle a los clientes…" · hint "El configurador no cambia nada por su cuenta: te muestra propuestas y vos las aplicás." · botón **Empezar** (Ctrl+Enter).

**P-M4b-04 Conversación de configuración** (vista de M3b con tarjetas)
- Encabezado: "Configuración de reglas · 14/09/2026" · línea: Por · costo acumulado · "3 propuestas pendientes".
- Hilo M3b; debajo de cada respuesta del agente, sus **tarjetas de propuesta** (D-M4b-4) y, si hay 2 o más pendientes, botón **Aplicar todas (N)**.
- Acciones por tarjeta: **Aplicar** (primario) · **Editar y aplicar** (secundario) · **Descartar** (outline).
- Estados en la tarjeta: Pendiente (sin badge) · **Aplicada** (verde, enlace "Ver regla") · **Descartada** (gris, acciones ocultas) · **No se pudo aplicar** (rojo, motivo + **Reintentar** + Editar y aplicar).
- "Aplicar todas": SweetAlert2 "Se van a aplicar 4 propuestas. Las que no se puedan aplicar quedan marcadas con el motivo." → resultado en toast ("3 aplicadas, 1 no se pudo aplicar") y tarjetas actualizadas sin recargar.
- Cuadro "Seguir conversando" de M3b (solo el autor) con placeholder "Pedile otra regla o que ajuste una propuesta…".
- Otro Director: lee, aplica y descarta; sin cuadro.

**P-M4b-05 Formulario de regla** (ajuste): con `propuesta` en la URL, precargado (alcance, destino, modo, tipo, título, texto, etiquetas) + `ov-alert info` "Estás aplicando una propuesta del configurador." · al guardar: "Propuesta aplicada." y vuelta a la tarjeta.

**P-M4b-06 Detalle de regla** (ajuste): badge de origen y enlace según D-M4b-9; en el historial, el evento muestra "desde el configurador".

**P-M4b-07 Tareas** (ajuste D-M4b-8).

**P-M4b-08 Núcleo IP** (staff): el configurador aparece como artefacto de la plataforma con el flujo de versiones y evaluación existente.

### ViewModels definidos M4b
| ViewModel | Campos y validaciones |
|---|---|
| `ConversacionConfiguracionListItem` (JSON) | `tareaId, iniciada, por, ultimaActividad, pendientes, aplicadas, estado` |
| `IniciarConfiguracionViewModel` | `Texto` [Required "Contame qué querés configurar."] [StringLength 10000 "El mensaje admite hasta 10.000 caracteres."] |
| `PropuestaReglaViewModel` | `Id` · `Tipo` (Nueva / Cambio / Desactivar / ActivarSugerencia) · `Estado` · `DondeAplica` (texto llano) · `Modo?` · `TipoRegla` · `Titulo` · `Texto` · `TextoAnterior?` · `PorQue?` · `MotivoFallo?` · `ReglaId?` · `CambioDesdePropuesta` · `PuedeAccionar` |
| `AplicarTodasResultadoViewModel` (JSON) | `aplicadas`, `fallidas[] {id, motivo}` |
| `TareaDetalle` (ajuste) | + `EsConfiguracion` · `PropuestasPorTurno` |

### Validaciones de UI M4b
| Caso | Mensaje |
|---|---|
| Mensaje vacío / largo | "Contame qué querés configurar." / "El mensaje admite hasta 10.000 caracteres." |
| Configurador sin publicar | "Todavía no está disponible." |
| No es Director | 403 |
| Propuesta ya aplicada o descartada | "Esta propuesta ya fue resuelta." |
| Regla cambió desde la propuesta | modal D-M4b-5: "Esta regla cambió desde la propuesta. Revisá la versión actual antes de aplicar." |
| Falla al aplicar | mensaje del servicio de reglas (límite, destino dado de baja, conflicto) |
| OK | "Propuesta aplicada." / "Propuesta descartada." / "3 aplicadas, 1 no se pudo aplicar." |
| Confirmar descartar | sin confirmación (se puede volver a pedir al agente) |

### Maquina de estados M4b (propuesta)
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Herramienta de propuesta del agente | Pendiente | dentro de lo que el Director puede proponer; ≤ 10 por respuesta | guarda propuesta con la versión vista de la regla | fuera de alcance → la herramienta devuelve error al agente |
| Pendiente / No se pudo aplicar | Aplicar / Reintentar | Aplicada | Director; validaciones de reglas; si la regla cambió, confirmación | crea/edita/desactiva/activa vía servicio de reglas con origen | límite / destino / conflicto → No se pudo aplicar |
| Pendiente / No se pudo aplicar | Editar y aplicar (guardar) | Aplicada | Director; validaciones | guarda lo editado | igual que el formulario |
| Pendiente / No se pudo aplicar | Descartar | Descartada | Director | — | — |

### Permisos por pantalla / accion M4b
| Acción | Director (autor) | Otro Director | Empleado | Staff |
|---|:---:|:---:|:---:|:---:|
| P-M4b-02/03 iniciar y listar | ✅ | ✅ | 403 | 👁 (lectura desde backoffice/Tareas) |
| Seguir conversando | ✅ | ❌ | — | ❌ |
| Aplicar / descartar / aplicar todas | ✅ | ✅ | 403 | ❌ |
| Ver origen en historial | ✅ con enlace | ✅ con enlace | badge sin enlace | ✅ con enlace |

### Contratos funcionales para Services M4b
| Contrato | Operaciones | Reglas |
|---|---|---|
| Configurador | disponible? · iniciar conversación · listar conversaciones de la empresa | RF-M4b-01, 11, 12; D-M4b-2 |
| Herramientas del configurador | leer reglas visibles (resumen paginado) · leer áreas, agentes de la empresa, clientes (nombres), sugerencias · proponer nueva / cambio / desactivar / activar sugerencia | RF-M4b-02, 09, 10; acotadas por permisos del Director que inició |
| Propuestas | listar por conversación y turno · aplicar (con verificación de cambio) · aplicar todas · descartar · reintentar · datos para precargar el formulario | RF-M4b-03..08 |
| Reglas (extensión) | crear/editar/desactivar/activar sugerencia con origen "Propuesta del configurador" y enlace a la propuesta | RF-M4b-04, 08 |
| Tareas (extensión) | tipo de tarea "configuración" · filtro · contexto sin reglas de la empresa | D-M4b-3, D-M4b-8 |
| Núcleo | prompt del configurador versionado y evaluado | RF-M4b-11 |

### M4b-6. Impacto funcional por capa
- **Presentación:** botón y lista de conversaciones, nueva conversación con chips, tarjetas de propuesta en la conversación, formulario precargado, origen en historial, filtro en Tareas.
- **Negocio:** herramientas de lectura/propuesta acotadas por permisos, aplicación por el servicio de reglas, verificación de cambios, aplicar todas.
- **Datos:** propuestas, origen y enlace en eventos de regla, tipo de tarea.

### M4b-7. Riesgos y supuestos
- R-M4b-01..05 heredados (propuestas equivocadas, inyección/escalamiento, costo, calidad del prompt, propuestas viejas).
- R-M4b-06 (medio, nuevo) muchas tarjetas en una respuesta pueden abrumar → límite 10 y "Aplicar todas".
- R-M4b-07 (bajo, nuevo) dos Directores accionando la misma propuesta a la vez → "Esta propuesta ya fue resuelta."
- S-M4b-01/02 heredados (confiabilidad de herramientas del modelo real; simulador con herramientas guionadas para QA).
- D-M4b-1..9 pendientes de validar.

### M4b-8. Plan funcional por etapas (para el arquitecto)
1. Tipo de conversación de configuración + contexto sin reglas de la empresa + prompt del configurador en núcleo (borrador).
2. Herramientas de lectura y de propuesta acotadas; propuestas persistidas.
3. Tarjetas, aplicar / editar y aplicar / descartar / aplicar todas, verificación de cambio.
4. Lista de conversaciones, entrada desde Reglas, origen en historial, filtro en Tareas.
5. Modelo simulado con herramientas guionadas para QA.

### Historias de usuario M4b
- **HU-M4b-01** Como Director, quiero contarle al configurador cómo trabaja mi empresa y recibir propuestas de reglas, para no tener que aprender alcances y modos. *CA:* CA-M4b-01; chips de arranque (D-M4b-7).
- **HU-M4b-02** Como Director, quiero aplicar una propuesta con un click. *CA:* CA-M4b-02.
- **HU-M4b-03** Como Director, quiero corregir una propuesta antes de aplicarla. *CA:* CA-M4b-03; D-M4b-6.
- **HU-M4b-04** Como Director, quiero descartar propuestas que no me sirven. *CA:* CA-M4b-04.
- **HU-M4b-05** Como Director, quiero aplicar varias propuestas juntas y saber cuáles fallaron. *CA:* CA-M4b-05, CA-M4b-10.
- **HU-M4b-06** Como Director, quiero que me avise si una regla cambió desde que se propuso el cambio. *CA:* CA-M4b-06; D-M4b-5.
- **HU-M4b-07** Como Director, quiero la tranquilidad de que nada se aplica sin mi confirmación. *CA:* CA-M4b-07.
- **HU-M4b-08** Como Director, quiero retomar una conversación de configuración y ver las de otros Directores. *CA:* CA-M4b-12; D-M4b-2.
- **HU-M4b-09** Como miembro o staff, quiero saber que una regla vino del configurador. *CA:* CA-M4b-13; D-M4b-9.
- **HU-M4b-10** Como Director, quiero ver cuánto cuestan las conversaciones de configuración. *CA:* CA-M4b-14; D-M4b-8.
- **Transversal** CA-M4b-08 (lectura acotada), CA-M4b-09 (Empleado 403), CA-M4b-11 (no disponible) y CA-M4b-15 (404 entre organizaciones) aplican a HU-M4b-01..08.

---
# M4 — Agentes de la organización

Estado: **aprobado por Joaquín el 2026-09-14** con D-M4-1..3 y D-M4-6..10, y el ajuste siguiente (prevalece sobre lo escrito abajo).

### Ajuste aprobado en el gate (2026-09-14): sin revisión del Director por ahora
- Se elimina el estado **"En revisión del Director"** y todo el flujo de propuesta: **P-M4-04 Propuestas y P-M4-05 Revisar propuesta quedan fuera de M4** (pospuestos); **D-M4-4 y D-M4-5 no aplican**.
- **Cualquier miembro publica directo** un agente para toda la empresa. D-M4-3 queda: "Solo yo" → **Guardar y usar** / Guardar borrador; "Toda la empresa" → **Publicar para la empresa** / Guardar borrador (mismo botón para Director y Empleado; se quita el hint "lo revisa el Director").
- **Edición de agentes de la empresa:** su creador y el Director. **Archivar/reactivar:** el Director cualquiera de la empresa; cada miembro los suyos (personales o de la empresa que creó).
- **D-M4-7 Notificaciones (adaptada):** cuando un miembro publica o actualiza un agente para toda la empresa, se avisa a los Directores ("Laura publicó «CM del estudio» para toda la empresa."), para que puedan revisarlo o archivarlo.
- **Máquina de estados de versión:** Borrador → Publicada → Reemplazada (sin En revisión ni Rechazada). Estados visibles (D-M4-2): Borrador · Publicado · Archivado · No disponible.
- Validación "Solo el Director puede publicar agentes para toda la empresa" se elimina.

Entrada: `1-analista-funcional.md` M4 aprobado 2026-09-14 (P1–P11 con las hipótesis). Criterio transversal vigente: UI en lenguaje llano, esconder la complejidad interna (D-M3-8..12).

### M4-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template M3 — `Reglas/*` (listado con pestañas, formulario con contador y opciones plegadas, detalle con historial, `_CardReglasDestino`) | ABM con versiones e historial | **Reutilizar** estructura para crear/editar/detalle de agentes y la card "Reglas de este agente". |
| Template M3 — `Agentes/Ejecutar` + `_VistaPreviaReglas`, `Tareas/_ReglasAplicadas` | Vista previa y reglas usadas | **Reutilizar** sumando el grupo "Instrucciones de <agente>". |
| Template núcleo — `Nucleo/Version` (estados Borrador/Evaluada/Publicada) | Ciclo de versiones | **Reutilizar** criterio visual de estados e historial. |
| Template — `NotificationService` + campana del topbar | Notificaciones in-app | **Reutilizar** para propuestas aprobadas/rechazadas y nuevas propuestas. |
| Template M2/M3 — listados DataTables con filtros, Session, acciones AJAX | Grillas | **Reutilizar** en Propuestas y en la vista de staff. |
| Catálogo y demás proyectos | Sin prompts derivados configurables por el cliente con aprobación | **Diseño nuevo** → PAT-030. |

### M4-1. Alcance funcional resumido
Catálogo unificado de agentes; crear, editar, duplicar, archivar y reactivar agentes derivados de un agente base; publicar (personal o para la empresa) con propuesta y revisión del Director; versiones e historial; uso en tareas con sus instrucciones en la vista previa; reglas por agente de la empresa; sugerencias de reglas de Olvidata activables por el Director; rubro incluido en todas las suscripciones (mecanismo); lectura para staff.

### Decisiones de diseño M4 a validar en el gate
- **D-M4-1 Formulario único, no asistente por pasos.** Cards en orden: agente base → datos → instrucciones → herramientas → quién lo usa.
- **D-M4-2 Estados en palabras.** "Borrador", "En revisión del Director", "Publicado", "Rechazado", "Archivado", "No disponible".
- **D-M4-3 Botones según el caso.** Personal: **Guardar y usar** / Guardar borrador. Para la empresa: Director **Publicar** / Guardar borrador; Empleado **Proponer a la empresa** / Guardar borrador.
- **D-M4-4 Bandeja de propuestas.** "Mi organización → Propuestas de agentes" con contador en el menú (solo Director).
- **D-M4-5 Revisión lado a lado.** El Director ve la versión publicada y la propuesta en dos columnas (texto completo, sin marcado de diferencias).
- **D-M4-6 Catálogo por secciones.** "De tu área" (destacados) · "De la empresa" · "Mis agentes" · "De Olvidata" (por rubro), con buscador.
- **D-M4-7 Notificaciones.** Nueva propuesta → Directores; aprobada/rechazada → creador (campana existente).
- **D-M4-8 Reglas "Por agente".** El combo incluye agentes de Olvidata y agentes publicados para la empresa; los agentes personales no reciben reglas (sus instrucciones ya son personales).
- **D-M4-9 Sugerencias de Olvidata** como pestaña de Reglas, solo para el Director.
- **D-M4-10 Rubro incluido siempre** visible como marca en Núcleo IP y como casilla tildada y bloqueada en el alta de licencias; se configura desde el manifiesto del núcleo, no desde el portal.

### Flujos de pantalla acordados M4

**P-M4-01 Agentes — catálogo** (rediseño de `Agentes/Index`, miembros)
- Encabezado: "Agentes" · "Elegí un agente para pedirle una tarea, o creá tu propia versión de uno de Olvidata." · botón primario **Crear agente**.
- Buscador por nombre/descripción (filtra en la página).
- Secciones (ocultas si vacías): **De tu área «Marketing»** · **De la empresa** · **Mis agentes** · **De Olvidata** (subtítulo por rubro).
- Card: nombre · descripción · badges (Personal / De la empresa / De Olvidata; área destacada; "Basado en <agente base>") · para el creador, estado si no está publicado (Borrador, En revisión del Director, Rechazado) · acciones: **Usar** (primario) · menú: Crear mi versión (agentes de Olvidata y de la empresa) · Ver · Editar · Duplicar · Archivar.
- "No disponible": card atenuada con "No disponible: la suscripción a <rubro> no está vigente." y sin "Usar".
- Estado vacío de "Mis agentes": "Todavía no creaste agentes. Elegí uno de Olvidata y tocá «Crear mi versión»."

**P-M4-02 Crear / editar agente**
- Encabezado: "Nuevo agente" / "Editar <nombre>" · "Partís de un agente de Olvidata y le sumás cómo trabaja tu empresa." · Volver.
- Card "Agente base": Select2 agrupado por rubro con la descripción del base (precargado si se entró con "Crear mi versión"); en edición solo lectura con hint "Para cambiar de agente base, duplicá este agente."
- Card "Datos": Nombre* (`col-md-6`) · Descripción (`col-12`, hint "La ven quienes lo eligen en el catálogo.").
- Card "Instrucciones": textarea 14 filas, contador "0 / 8.000", hint "Contale qué tiene que hacer distinto: tono, formato, pasos de tu empresa. No hace falta repetir las reglas de la empresa." · aviso "No cargues contraseñas ni datos bancarios."
- Card "Herramientas": casillas con nombre llano y descripción de cada herramienta del base; sin herramientas: "Este agente de Olvidata no usa herramientas."
- Card "Quién lo usa": radio **Solo yo** / **Toda la empresa** (para el Empleado: "Toda la empresa — lo revisa el Director antes de publicarlo") · Área destacada (Select2 opcional, visible con "Toda la empresa").
- Barra sticky según D-M4-3 · Cancelar · en edición: espaciador + Archivar. Hint en edición: "Guardar crea la versión 3. Las tareas anteriores no cambian."
- Si hay una versión en revisión: `ov-alert info` "Hay una versión esperando la revisión del Director. Si guardás, reemplaza a esa propuesta."

**P-M4-03 Detalle de agente**
- Encabezado: nombre · badge de estado · acciones: Usar · Editar · Duplicar · Archivar/Reactivar (según permisos).
- `ov-detail-grid`: Basado en (agente y rubro) · Quién lo usa · Área destacada · Creado por · Versión publicada · Herramientas.
- Card "Instrucciones" (versión publicada).
- Card "Borrador" o "En revisión del Director" (si existe) con su texto; si fue rechazada: `ov-alert warning` con el motivo del Director.
- Card "Historial de versiones": Versión · Estado · Fecha · Autor · Motivo (si rechazada) · "Ver instrucciones".
- Card "Reglas de este agente" (D-M4-8, reutiliza la card de M3) con "Nueva regla para este agente" (Director, solo agentes de la empresa).

**P-M4-04 Propuestas de agentes** (`Mi organización`, Director)
- Encabezado: "Propuestas de agentes" · "Agentes que tu equipo quiere compartir con toda la empresa."
- Grilla DataTables: Agente · Propuesto por · Tipo (Nuevo / Cambio) · Área destacada · Fecha; filtros por columna; Session; Limpiar filtros; acción **Revisar**.
- Vacío: "No hay propuestas pendientes."

**P-M4-05 Revisar propuesta** (Director)
- Encabezado: "Revisar «CM del estudio»" · "Propuesto por Laura el 14/09/2026."
- Dos columnas (una sola en mobile, propuesta primero): **Publicada hoy** / **Propuesta** — instrucciones, herramientas, quién lo usa, área destacada. Para "Nuevo", solo la propuesta.
- Barra: **Aprobar y publicar** (primario) · **Rechazar** (outline rojo → SweetAlert2 con textarea obligatoria "Contale a Laura qué cambiar") · Volver.

**P-M4-06 Nueva tarea** (ajuste): encabezado "CM del estudio · basado en Community manager"; en "Esto es lo que el agente va a tener en cuenta" aparece el grupo **"Instrucciones de CM del estudio"** en su lugar de prioridad.

**P-M4-07 Reglas** (ajuste D-M4-8): el combo Agente se agrupa en "De Olvidata" y "De la empresa"; en la pestaña "Por agente" la columna muestra el nombre del agente.

**P-M4-08 Reglas → Sugerencias de Olvidata** (pestaña, solo Director)
- Descripción: "Reglas que Olvidata recomienda para tus rubros. Activalas en un click y después editalas como quieras."
- Cards agrupadas por rubro: título · texto · etiquetas · acciones **Activar en la empresa** / **Activar en un área** (modal: Área*, "Siempre" / "Salvo que se indique otra cosa" — por defecto la segunda).
- Ya activada: badge "Ya activada" con enlace a la regla.
- Vacío: "Todavía no hay sugerencias de Olvidata para tus rubros."

**P-M4-09 Backoffice y núcleo** (staff)
- Organizaciones → detalle → **Agentes**: grilla de solo lectura (Agente, Basado en, Quién lo usa, Estado, Creado por) y detalle P-M4-03 sin acciones, con instrucciones visibles.
- Núcleo IP → rubro: badge "Incluido en todas las suscripciones"; sugerencias de reglas como artefactos con el flujo de evaluación existente.
- Alta de licencia: el rubro incluido aparece tildado y bloqueado con hint "Se incluye en todas las suscripciones."

**P-M4-10 Detalle de tarea** (ajuste): encabezado "CM del estudio (versión 3)"; si el agente está archivado, badge "Agente archivado" (los ajustes siguen permitidos, P11).

### ViewModels definidos M4
| ViewModel | Campos y validaciones |
|---|---|
| `AgentesCatalogoViewModel` | `Secciones[]` (`Titulo`, `Items[]`) · `AreaUsuario?` · `PuedeCrear` |
| `AgenteCardItem` | `Tipo` (Olvidata / Empresa / Personal) · `Id/Ref` · `Nombre` · `Descripcion` · `BaseNombre` · `AreaDestacada?` · `Estado` · `Disponible` · `MotivoNoDisponible?` · acciones permitidas |
| `AgenteFormViewModel` | `Id?` · `BaseRef` [Required "Elegí el agente de Olvidata en el que se basa."] · `Nombre` [Required "Ingresá un nombre."] [StringLength 100] · `Descripcion?` [StringLength 500] · `Instrucciones` [Required "Escribí las instrucciones."] [StringLength 8000 "Las instrucciones admiten hasta 8.000 caracteres."] · `Herramientas[]` · `Visibilidad` [Required "Elegí quién lo usa."] · `AreaDestacadaId?` · `Accion` (GuardarBorrador / GuardarYUsar / Publicar / Proponer) · `VersionToken` · opciones (bases, herramientas del base, áreas) · `HayPropuestaPendiente` |
| `AgenteDetalleViewModel` | datos · `Publicada?` · `Pendiente?` (borrador o en revisión, con motivo de rechazo) · `Historial[]` · `ReglasDelAgente` · permisos |
| `PropuestaListItem` (JSON) | `id, agente, propuestoPor, tipo, areaDestacada, fecha` |
| `RevisarPropuestaViewModel` | `Publicada?` · `Propuesta` · `Autor` · `Fecha` · `MotivoRechazo` [Required al rechazar "Contale qué cambiar."] [StringLength 1000] |
| `SugerenciaReglaItem` | `Id` · `Rubro` · `Titulo` · `Texto` · `Etiquetas` · `YaActivadaReglaId?` |
| `ActivarSugerenciaViewModel` | `SugerenciaId` · `Destino` (Empresa / Área) · `AreaId?` (requerido si Área: "Elegí el área.") · `Modo` |

### Validaciones de UI M4
| Caso | Mensaje |
|---|---|
| Nombre repetido entre agentes activos | "Ya hay un agente activo con ese nombre en tu empresa." |
| Herramienta fuera del agente base | "Esa herramienta no está disponible en el agente de Olvidata elegido." |
| Agente base no habilitado | "Ese agente de Olvidata no está incluido en la suscripción de tu empresa." |
| Límite de agentes activos | "Tu empresa llegó al máximo de 50 agentes activos. Archivá alguno para crear otro." |
| Límite personales | "Llegaste al máximo de 10 agentes personales. Archivá alguno para crear otro." |
| Empleado intenta publicar directo / aprobar | "Solo el Director puede publicar agentes para toda la empresa." (403) |
| Agente no disponible | "Este agente no está disponible: la suscripción a <rubro> no está vigente." |
| Editar mientras otro guardó | "Otra persona modificó este agente mientras lo editabas. Revisá la versión actual y volvé a guardar." |
| OK | "Agente guardado como borrador." / "Agente listo para usar." / "Agente publicado para toda la empresa." / "Propuesta enviada al Director." / "Propuesta aprobada y publicada." / "Propuesta rechazada. Le avisamos a Laura." / "Agente archivado." / "Agente reactivado." / "Copia creada como borrador." / "Regla activada." |
| Confirmación archivar | "¿Archivar «CM del estudio»? Deja de aparecer para pedir tareas nuevas; las tareas y conversaciones existentes siguen disponibles." |

### Maquina de estados M4 (versión del agente)
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Guardar borrador | Borrador | permisos; límites; validaciones | nueva versión | límite / validación |
| Borrador | Guardar y usar (personal) | Publicada | creador; visibilidad Solo yo | publicada anterior → Reemplazada | — |
| Borrador | Publicar (empresa) | Publicada | Director | anterior → Reemplazada; notifica si había propuesta | sin permiso |
| Borrador | Proponer | En revisión | Empleado; visibilidad Toda la empresa | notifica Directores; reemplaza propuesta previa del mismo agente | — |
| En revisión | Aprobar | Publicada | Director; misma organización | anterior → Reemplazada; notifica creador | sin permiso |
| En revisión | Rechazar | Rechazada | Director; motivo | notifica creador con motivo | motivo vacío |
| Publicada / Rechazada | Editar | Borrador (N+1) | permisos | — | conflicto de edición |
| Agente Activo | Archivar | Archivado | Director o creador (personal) | sale del catálogo | — |
| Archivado | Reactivar | Activo | permisos; límite de activos | vuelve con su última publicada | límite |

### Permisos por pantalla / accion M4
| Pantalla / acción | Director | Empleado | Staff |
|---|:---:|:---:|:---:|
| P-M4-01 catálogo | ✅ (sin personales ajenos) | ✅ (sin personales ajenos) | — |
| P-M4-02 crear / editar | personales propios y de la empresa | personales propios; de la empresa que creó (vuelve a revisión) | ❌ |
| P-M4-03 detalle | empresa + propios | empresa + propios | ✅ todos (P-M4-09) |
| P-M4-04/05 propuestas | ✅ | ❌ 403 | ❌ |
| P-M4-08 sugerencias | ✅ | ❌ (pestaña oculta) | — |
| Archivar / reactivar | cualquiera de la empresa + propios | sus personales | ❌ |

### Contratos funcionales para Services M4
| Contrato | Operaciones | Reglas |
|---|---|---|
| Agentes de la organización | catálogo por usuario · obtener detalle con historial · crear/editar con acción · duplicar · archivar/reactivar · opciones del formulario (bases habilitadas, herramientas del base, áreas) | RF-M4-01..11, 14, 15; D-M4-1..3, 6 |
| Propuestas | listar pendientes · obtener para revisar · aprobar · rechazar con motivo | RF-M4-06, 07; D-M4-4, 5, 7 |
| Constructor de contexto (extensión) | resolver agente (base o de la empresa) → versión del base vigente + versión del derivado + herramientas efectivas · nivel 6 · reglas por agente de la empresa y del base | RF-M4-02, 03, 09 |
| Tareas (extensión) | crear con agente de la empresa · detalle con nombre y versión · ajustes permitidos con agente archivado | RF-M4-10 (P11) |
| Reglas (extensión) | combo de agentes · sugerencias visibles por rubro · activar sugerencia | D-M4-8, 9; RF-M4-13 |
| Licencias / núcleo (extensión) | rubro incluido siempre al crear y renovar · sincronizar vigentes · importar y publicar sugerencias | RF-M4-12, 13; D-M4-10 |
| Notificaciones | propuesta nueva · aprobada · rechazada | D-M4-7 |

### M4-6. Impacto funcional por capa
- **Presentación:** catálogo rediseñado, formulario y detalle de agentes, propuestas y revisión, pestaña de sugerencias, ajustes en nueva tarea, reglas, detalle de tarea, backoffice, núcleo y licencias.
- **Negocio:** versiones con aprobación, permisos por visibilidad y rol, límites, herramientas efectivas, nivel 6 del contexto, activación de sugerencias, rubro incluido.
- **Datos:** agentes de la organización y versiones, referencia en tareas y reglas, sugerencias del núcleo, marca de rubro incluido.

### M4-7. Riesgos y supuestos
- R-M4-01..04 heredados (inyección por instrucciones, cambios del base, complejidad de estados, proliferación).
- R-M4-05 (medio, nuevo) mostrar estados de versión sin abrumar: solo el creador y el Director ven borradores/revisión; el resto ve el agente publicado.
- R-M4-06 (bajo, nuevo) propuestas abandonadas: sin vencimiento en M4.
- S-M4-01/02 heredados (pocas herramientas hoy; contenido de "negocio" y sugerencias lo define Joaquín).
- D-M4-1..10 pendientes de validar.

### M4-8. Plan funcional por etapas (para el arquitecto)
1. Datos y servicio de agentes de la organización (versiones, permisos, límites, archivar, duplicar).
2. Catálogo, formulario y detalle.
3. Propuestas, revisión y notificaciones.
4. Constructor de contexto (nivel 6, herramientas efectivas), tareas y reglas por agente de la empresa.
5. Rubro incluido siempre y sugerencias de reglas (núcleo, licencias, pestaña del Director).
6. Vistas de staff.

### Historias de usuario M4
- **HU-M4-01** Como miembro, quiero crear mi propia versión de un agente de Olvidata para que trabaje como yo necesito. *CA:* CA-M4-01, CA-M4-04, CA-M4-06.
- **HU-M4-02** Como Director, quiero publicar un agente para toda la empresa y destacarlo para un área. *CA:* CA-M4-02.
- **HU-M4-03** Como Empleado, quiero proponer un agente a la empresa y saber si fue aprobado o por qué se rechazó. *CA:* CA-M4-03; notificación y motivo visibles.
- **HU-M4-04** Como Director, quiero revisar propuestas comparando con lo publicado. *CA:* CA-M4-03; D-M4-5; rechazar exige motivo.
- **HU-M4-05** Como creador, quiero editar un agente sin afectar las tareas ya hechas. *CA:* CA-M4-05; edición de Empleado sobre agente de la empresa vuelve a revisión (P5).
- **HU-M4-06** Como miembro, quiero encontrar rápido el agente que necesito. *CA:* D-M4-6; buscador; destacados de mi área.
- **HU-M4-07** Como miembro, quiero ver en la vista previa las instrucciones del agente de la empresa. *CA:* CA-M4-01 (grupo "Instrucciones de…").
- **HU-M4-08** Como Director, quiero reglas para un agente de la empresa. *CA:* CA-M4-07; D-M4-8.
- **HU-M4-09** Como Director o creador, quiero archivar y reactivar agentes. *CA:* CA-M4-08; ajustes en tareas existentes permitidos (P11).
- **HU-M4-10** Como miembro, quiero duplicar un agente como punto de partida. *CA:* CA-M4-11.
- **HU-M4-11** Como miembro, quiero saber cuándo un agente no está disponible y por qué. *CA:* CA-M4-09.
- **HU-M4-12** Como Director, quiero activar reglas sugeridas por Olvidata. *CA:* CA-M4-13; D-M4-9.
- **HU-M4-13** Como staff de Olvidata, quiero que un rubro quede incluido en todas las suscripciones. *CA:* CA-M4-12; D-M4-10.
- **HU-M4-14** Como staff de Olvidata, quiero ver los agentes que crean las organizaciones. *CA:* CA-M4-14.
- **Transversal** CA-M4-10 (límites) y CA-M4-15 (ids de otra organización → 404) aplican a HU-M4-01..12.

---
