<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M07 (2 bloques archivados)

- M7b — Tareas asignadas a personas y asistente del Director que reparte trabajo
- M7a — Subagentes y reglas propuestas por agentes de trabajo

---

# M7b — Tareas asignadas a personas y asistente del Director que reparte trabajo

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M7 (RF-M7b-01..17, CA-M7b-01..16),
`2-disenador-funcional.md` M7 parte M7b (D-M7-12..24, P-M7b-01..09) y `3-arquitecto-mvc.md` M7 parte M7b, aprobados sin gate por
autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.
Segunda mitad de M7 (M7a ya estaba implementada, con QA y commit). Sin contenido de rubros, sin llamadas a Anthropic, sin commits.

### Escaneo de reutilizacion M7b
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M4b (`TipoTarea` + `InstantaneaConfiguracion` + render separado, `IniciarConfiguracionAsync`, `ConfiguracionReglasController`, `_TarjetasPropuesta`/`_ScriptPropuestas`, `PropuestaReglaService` con Fallida/Aplicar todas/YaResuelta, PAT-032) | El asistente ES el configurador con otro prompt: se extrajo `IniciarPlataformaAsync` y `ArmarPlataformaAsync` (formato y declaración por parámetro) y se copió el esqueleto de controller, tarjetas y script | Literal (refactor + patrón del mismo repo) |
| Template M4b (`HerramientaClientesBuscar`) | Misma clase, con la guarda ampliada por `TiposPermitidos` (virtual en la base) al asistente | Literal (extensión) |
| Template M7a (`PreparadorTareaTrabajo`, `IHerramientaDelegacion`, `ResumenHerramientasPlataforma`) | Aplicar una propuesta de tarea de agente usa el preparador tal cual (suscripción, cliente, límite M6, instantánea) | Literal |
| Template M6 (`ContadorAprobacionesViewComponent`, bandeja con pestañas y filtros por columna, SweetAlert2 con textarea y contador, `IControlGasto`) | `ContadorAsignacionesViewComponent`, pantalla Asignaciones, confirmaciones de "hecha" y "cancelar", límite al iniciar la conversación y al aplicar | Literal (patrón del mismo repo) |
| Template M2/M5 (`FiltrosSesion`, `DataTableRequestHelper`, `RespuestasServicio`, proyección anónima + nombres en memoria, tokens de color DI-M5-17) | Grilla, filtros por pestaña, respuestas AJAX, colores de estado | Literal |
| century-21 (`docs/century-21/definiciones/3-arquitecto-mvc.md`: "Tomar"/"Reasignar" con RowVersion y mensaje funcional) | Criterio del conflicto: `VersionToken` con `OriginalValue` y "Otra persona cambió esta asignación. Recargá la página." | Patrón (otro dominio) |
| yoga (`docs/yoga/definiciones/2-disenador-funcional.md`: cuota "Vencida" derivada) | "Vencida" calculada con el día argentino, nunca columna | Patrón |
| verif-m7 / verif-m6 (scratchpad) | Verificador EF → MySQL con organización de prueba y limpieza (`scratchpad/verif-m7b`) | Literal (adaptado) |
| PAT-039 / PAT-032 | PAT-039 completado con rutas reales y gotchas confirmados (`pendiente_verificar: false`); PAT-032 aplicado a un segundo tipo de propuesta | Confirmado |

### Archivos y capas modificadas M7b
**Domain** — Nuevos: `Enums/EnumsAsignaciones.cs` (`EstadoTareaAsignada`, `OrigenTareaAsignada`, `TipoPropuestaTrabajo`, `EstadoPropuestaTrabajo`),
`Entities/TareaAsignada.cs` (`TareaAsignada` + `PropuestaTrabajo`). Modificados: `Enums/EnumsAgentes.cs` (`TipoTarea.AsistenteDirector = 3`),
`Entities/Tareas.cs` (`TareaAgente.TareaAsignadaId`).

**Application** — Nuevos: `Settings/AsignacionesOptions.cs`, `DTOs/AsignacionesDtos.cs` (`MensajesAsignaciones`, `MensajesAsistente`,
`AsignacionDto`, `AsignacionListItemDto`, `PestanaAsignaciones`, `AsignacionFiltros`, `AsignacionDetalleDto`, `AsignacionRefDto`,
`PedidoDesdeAsignacionDto`, `PropuestaTrabajoDto`…), `Interfaces/ITareaAsignadaService.cs`, `Interfaces/IPropuestaTrabajoService.cs`
(+ `IAsistenteDirector`). Modificados: `Motor/NotaSubtarea.cs` (`NombresHerramientasAsistente`), `Motor/IMotorAgentes.cs`
(`CrearTareaDto.TareaAsignadaId`, `TareaDetalleDto` + `EsAsistente`/`EsDePlataforma`/`PropuestasTrabajoPorPaso`/`TareaAsignada`,
`IServicioTareas.IniciarAsistenteAsync`, `ListarConfiguracionesAsync`/`OpcionesConfiguracionAsync` con `TipoTarea`),
`Motor/IConstructorContexto.cs` (`FormatoContextoAsistente = 4`, `ArmarAsistenteAsync`), `Interfaces/IPermisosOrganizacion.cs`
(`PuedeAsignarTareas`, `PuedeUsarAsistente`), `DTOs/SubtareasDtos.cs` (QA-M7a-02: `PrefijoResultadoFallida`).

**Infrastructure** — Nuevos: `Services/Asignaciones/TareaAsignadaService.cs`, `Services/Asistente/{AsistenteDirector,
HerramientasAsistente, PropuestaTrabajoService}.cs`, `Data/Configurations/AsignacionesConfigurations.cs` (+ `ConversorDia`), migración
`Data/Migrations/20260916003219_AsignacionesAsistenteM7b.cs` (+ Designer y snapshot). Modificados: `Data/AppDbContext.cs` (DbSets),
`Data/Configurations/AgentesConfigurations.cs` (FK e índice de `TareaAsignadaId`), `Services/Motor/ConstructorContexto.cs`
(`ArmarPlataformaAsync` + `DeclaracionPrecedenciaAsistente`), `Services/Motor/ServicioTareas.cs` (`IniciarPlataformaAsync`,
`IniciarAsistenteAsync`, vínculo con la asignación en `CrearAsync`, detalle con asistente y asignación, listas por tipo),
`Services/Motor/ProcesadorTareas.cs` (guarda de plataforma generalizada, `ReconstruirPlataformaAsync`),
`Services/Motor/ProveedorModeloSimulado.cs` (`GuionAsistente`), `Services/Configurador/HerramientasConfigurador.cs` (`TiposPermitidos`
virtual; `clientes_buscar` habilitada en el asistente), `Services/Subagentes/ResumenHerramientasPlataforma.cs` (QA-M7a-02),
`Services/Organizacion/PermisosOrganizacion.cs`, `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/{AsignacionesController, AsistenteController}.cs`, `ViewComponents/ContadorAsignacionesViewComponent.cs`,
`Helpers/AsignacionesTextos.cs`, `Models/AsignacionesViewModels.cs`, vistas `Asignaciones/{Index, Form, Detalle, _ScriptAcciones}`,
`Asistente/{Index, Nueva}`, `Tareas/{_TarjetasPropuestaTrabajo, _ScriptPropuestasTrabajo}`, `Shared/Components/ContadorAsignaciones/Default`.
Modificados: `Controllers/{AgentesController (catálogo y Ejecutar con `asignacion`, POST con `TareaAsignadaId`), ConfiguracionReglasController
(tipo explícito)}.cs`, `Models/AgentesViewModels.cs` (`EjecutarAgenteViewModel` + asignación), vistas `Shared/_Layout` (ítem Asignaciones con
contador), `Agentes/{Index, _TarjetaAgente, Ejecutar}`, `Tareas/{Detalle, _Conversacion, Index}`, `wwwroot/css/site.css`,
`appsettings.json` (sección `Asignaciones`).

**Núcleo**: `nucleo/plataforma/agentes/asistente-director.md` (borrador) y entrada en `nucleo/plataforma/plataforma.yml`.
**Tests**: nuevos `AsignacionesTests.cs` (18), `AsistenteDirectorTests.cs` (18) e `Infra/EntornoM7b.cs`; ajustado `SubagentesTests.cs`
(QA-M7a-02). **Repo**: `docs/diseno-organizacion-roles-reglas.md` (M7b ✅).

### Decisiones de implementacion M7b (ambigüedades resueltas)
- **DI-M7b-1 Un solo camino para las conversaciones de plataforma:** en vez de duplicar `IniciarConfiguracionAsync` y
  `ArmarConfiguracionAsync`, se extrajeron `IniciarPlataformaAsync` y `ArmarPlataformaAsync` con el formato, el tipo y la declaración por
  parámetro. El formato 3 queda byte a byte igual (su golden sigue verde) y el 4 tiene el suyo. La guarda del procesador y la reconstrucción
  pasaron de `== ConfiguracionReglas` a `!= Trabajo`: todo tipo nuevo de plataforma hereda el comportamiento.
- **DI-M7b-2 `clientes_buscar` compartida:** `HerramientaConfiguradorBase` expone `TiposPermitidos` virtual (por defecto solo
  configuración) y `HerramientaClientesBuscar` lo amplía al asistente. Una sola clase, una sola lectura acotada, sin copiar código.
- **DI-M7b-3 El vencimiento mínimo se exige SOLO cuando cambia:** si no, una asignación vieja (ya vencida) dejaría de poder editarse para
  cambiarle el título o reasignarla. `ValidarAsync` recibe el vencimiento anterior y compara.
- **DI-M7b-4 "Pedírsela a un agente" pasa por el catálogo:** `Ejecutar` necesita un agente, así que el botón del detalle lleva a
  `Agentes/Index?asignacion=N` (con `ov-alert` "Elegí el agente") y cada "Usar" arrastra la asignación hasta `Agentes/Ejecutar?asignacion=N`.
  Las dos pantallas validan con `DatosParaPedirAAgenteAsync` (403 si no es la persona asignada, 404 si no la ve).
- **DI-M7b-5 El vínculo lo prepara el servicio de asignaciones:** `PrepararVinculoAsync` no guarda: setea `TareaAsignadaId` y pasa la
  asignación a En curso, y `ServicioTareas.CrearAsync` guarda todo junto. Un conflicto de token deja la tarea sin crear (`ChangeTracker.Clear`).
- **DI-M7b-6 La propuesta aplicada se marca en el mismo `SaveChanges` que su resultado:** la asignación por `CrearAsync(dto, propuestaId)` y
  la tarea por la navegación `ResultadoTareaAgente` (EF completa la FK sin un segundo guardado).
- **DI-M7b-7 Permisos, nunca visibilidad (OLV-010):** `VisibleAsync` solo habilita LECTURA; cada acción pasa por `ParaAccionarAsync`
  (asignado o Director, o solo Director en cancelar) y `PropuestaTrabajoService.ParaResolverAsync` (Director activo de esa organización).
  `PuedeAccionar` de las tarjetas es cosmético: el servidor vuelve a decidir.
- **DI-M7b-8 Contador del menú para todo miembro:** el ítem "Asignaciones" está en el bloque `Permisos.EsMiembro` del layout, junto a
  Aprobaciones; "Del equipo" se esconde y, por URL, cae a "Asignadas a mí" (no 403: la pestaña no es un recurso).
- **DI-M7b-9 Filtro Estado múltiple:** la grilla arranca con Pendiente + En curso preseleccionados (D-M7-13) y se persiste como lista
  separada por comas en Session; "Solo vencidas" es una casilla aparte. Sin `data-select2` propio (OLV-007): el `<select multiple>` lo toma
  `ovAplicarSelect2` como todos los demás.
- **DI-M7b-10 El simulador propone a la primera persona del equipo:** el diseño pedía "la primera que no sea el autor", pero el simulador no
  puede saber quién es (el `metadata.user_id` es opaco por el plan §5). Propone a `equipo_listar[0]` (orden alfabético) y a
  `agentes_disponibles[0]`. Para QA es equivalente y no expone identidades.
- **DI-M7b-11 `DateOnly` con conversor (RT-M7-13):** la columna sigue siendo `date`, pero se registró un `ValueConverter<DateOnly, DateTime>`
  porque `MySql.EntityFrameworkCore` devuelve `DateTime` y una proyección anónima a `DateOnly` revienta con `InvalidCastException`. Lo
  encontró el verificador contra MySQL real, no InMemory.
- **DI-M7b-12 QA-M7a-02:** el resultado de una parte fallida ya no dice "subagente" (`MensajesSubtareas.PrefijoResultadoFallida` = "El otro
  agente no pudo terminar: ") y "La subtarea se canceló" pasó a "La parte se canceló". `ResumenHerramientasPlataforma.SinPrefijo` usa la
  constante y el test de `SubagentesTests` afirma además que el texto NO contiene "subagente".

### Migraciones EF generadas M7b
- `20260916003219_AsignacionesAsistenteM7b` — `CreateTable TareasAsignadas` (título 150, descripción 4000, nota y motivo 500, `VenceEl` **date**,
  enums int, `VersionToken` como token, FKs Restrict a Tenant, ClienteCartera y 4 usuarios) y `PropuestasTrabajo` (texto `text`, `VenceEl` date,
  único `(TareaAgenteId, ToolUseId)`, índices `(TareaAgenteId, PasoNumero)` y `(ResultadoTareaAsignadaId)`, token); `AddColumn
  TareasAgente.TareaAsignadaId` + FK Restrict + índice. Índices de negocio: `(TenantId, AsignadaAUsuarioId, Estado)` y `(TenantId, Estado, VenceEl)`.
  Sin transformación de datos (las dos tablas nacen vacías y la columna nueva queda NULL en todas las tareas existentes). `Down` en orden inverso.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, luego `database update SubagentesReglasPropuestasM7a` (Down OK) y
  `database update` otra vez; `has-pending-model-changes` limpio también después de agregar el conversor de `DateOnly`.
- Verificado por SQL (`scratchpad/verificar-m7b.sql`, transacción revertida): `VenceEl` es `date` en las dos tablas y `DATE(VenceEl) = VenceEl`;
  único `(TareaAgenteId, ToolUseId)` con `NON_UNIQUE = 0` y **1062 real** al repetirlo; FK `FK_TareasAgente_TareasAsignadas_TareaAsignadaId`;
  "Vencida" calculada con `CONVERT_TZ(...,'-03:00')`; `EXPLAIN`: el contador usa un índice (`ref`), el listado del equipo usa
  `IX_TareasAsignadas_TenantId_AsignadaAUsuarioId_Estado` (`Using index condition`) y las tareas vinculadas usan
  `IX_TareasAgente_TareaAsignadaId` (`Using index`); 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m7b`, sin Anthropic): **67 pasos OK, 0 fallas, 0 restos**. Alta con cliente y vencimiento,
  vencimiento pasado rechazado, listado del equipo con proyección anónima, 9 filtros, 6 búsquedas globales (texto, persona, cliente, estado en
  palabras, "vencida", fecha) y 4 órdenes; visibilidad, detalle y contador; transiciones y **`DbUpdateConcurrencyException` real**;
  "Pedírsela a un agente" con vínculo y En curso en un guardado, y rechazo a quien no es la persona asignada; conversación del asistente
  (formato 4), las 4 herramientas de lectura y las 2 de propuesta con sus validaciones; aplicar asignación y tarea de agente por los servicios
  reales (origen, autor = Director que aplica), "ya fue resuelta" con token real, Empleado sin tarjetas; lista de conversaciones con
  "con pendientes" y búsqueda por cantidad, y filtro Tipo en Tareas.
- Impacto: 2 tablas nuevas vacías, 1 columna nueva (NULL) con FK e índice en `TareasAgente`.

### Evidencia de build y tests M7b
- `dotnet build OlvidataAgentes.slnx`: **0 errores** (queda la advertencia preexistente CS0114 de `HomeController`).
- `dotnet test tests/OlvidataAgentes.Tests`: **244 OK / 0 fallidos** (208 previos + 36 nuevos: 18 de asignaciones y 18 del asistente);
  golden de hash de los formatos 1, 2 y 3 verdes sin cambios y **golden nuevo del formato 4**
  (`039c7e7b606bde6c09003d40fd9c0e70a06991f1a8395178952a820518bbbbea`).
- Lecciones: (1) **MySQL no materializa `DateOnly` desde una columna `date` en una proyección** — hace falta un `ValueConverter` (InMemory no lo
  detecta, el verificador sí); (2) reusar el mismo scope de servicios entre dos operaciones de un test hace que la entidad quede cacheada:
  una edición que compara contra el valor anterior necesita un scope nuevo (como una request nueva); (3) `IReadOnlySet<T>.Contains` dentro de
  una consulta EF no es el `Contains` de LINQ: hay que materializar a `List<T>` antes.

### Riesgos residuales M7b
- El asistente está **importado en dev como borrador, sin publicar** (PA-14): hasta evaluarlo y publicarlo, "Repartir trabajo conversando"
  aparece deshabilitado. Los pasos para habilitarlo y revertirlo están en la guía de QA de `trazabilidad.md`.
- El prompt es un **borrador sin evaluar**: su calidad (a quién propone, cómo redacta el pedido) todavía no se midió; M8 es el camino previsto.
- El contador del menú hace un `COUNT` por request con menú, como el de M6 (RT-M6-12).
- Una notificación que falla después del commit queda sin reintento (se loguea), igual que en M6 (RT-M6-06).
- "Vencida" depende del reloj del servidor convertido a hora argentina: una asignación que vence hoy pasa a vencida a la medianoche AR.
- El simulador propone a la primera persona del equipo (DI-M7b-10): con un solo miembro, el Director se autoasigna.
- Verificación visual pendiente (QA): pestañas y filtros de Asignaciones, formulario con chips de vencimiento, detalle en dos columnas,
  confirmaciones con textarea, tarjetas del asistente, contador del menú, mobile 390 y ambos temas.

### Proximos pasos pendientes M7b
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M7b).
- PA-14: evaluar y publicar el prompt `asistente-director` (hoy en borrador).
- Deuda fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; advertencia CS0114 de `HomeController` (template).

---
# M7a — Subagentes y reglas propuestas por agentes de trabajo

Estado: **implementada 2026-09-15, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M7 (P1–P26, alcance M7a),
`2-disenador-funcional.md` M7 (D-M7-1..11, D-M7-23/24) y `3-arquitecto-mvc.md` M7 (parte M7a), aprobados sin gate por autorización
de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.
**M7b (asignaciones y asistente del Director) queda para otra corrida.** Sin contenido de rubros, sin llamadas a Anthropic, sin commits.

### Escaneo de reutilizacion M7a
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 (`TareaPadreId` sin uso, `EjecucionHerramienta` único por `ToolUseId`, `GuardarAsync` con `Version`, `ReclamarSiguienteAsync`) | La parte es una `TareaAgente` hija; su resultado vuelve como ejecución de herramienta; el estado nuevo no se reclama | Literal (extensión) |
| Template núcleo (`Artefacto.ArtefactoPadreId` que completa `ImportadorRubro` desde `coordinador`) | Subagentes = hijos publicados del artefacto base, sin tocar el importador | Literal |
| Template M3/M4 (`ServicioTareas.CrearAsync`, `ValidarAgenteOrganizacionAsync`, instantánea y hash) | Extraídos a `PreparadorTareaTrabajo` sin cambiar comportamiento ni mensajes | Literal (refactor) |
| Template M3b (`ReconstruirConversacion`, `MarcarFinAsync`, `MotivoNoPuedeSeguir`, simulador con guion) | Nota del coordinador en los mensajes, motivos nuevos, guiones nuevos | Literal (extensión) |
| Template M4b (`PropuestaRegla`, `PropuestaReglaService`, `ReglaService(OrigenAplicacion)`, `_TarjetasPropuesta`/`_ScriptPropuestas`, PAT-032) | Reglas propuestas por agentes de trabajo sobre la MISMA entidad, servicio y tarjetas, con permisos por tipo de tarea | Literal (patrón del mismo repo) |
| Template M5 (`NotaAdjuntos`, `ValidarAdjuntosAsync`, `HerramientasDocumentos.Resumir`, JSON con `JavaScriptEncoder`) | Nota de formato fijo, adjuntos de la parte, "Ver pasos" llano, resultado escapado | Literal |
| Template M6 (`IControlGasto`, `AprobacionAccion`, recorrido del paso, barrido del worker, PAT-034/035) | Límite al delegar, aprobaciones que bloquean el recorrido, segundo barrido en el worker | Literal (extensión) |
| verif-m6 (scratchpad) | Verificador EF → MySQL con organización de prueba y limpieza (`scratchpad/verif-m7`) | Literal (adaptado) |
| PAT-038 / PAT-032 | PAT-038 completado con rutas reales y gotchas confirmados; PAT-032 ampliado a agentes de trabajo | Confirmado |

### Archivos y capas modificadas M7a
**Domain** — Modificados: `Enums/EnumsAgentes.cs` (`EstadoTarea.EsperandoSubtareas = 7`), `Entities/Tareas.cs` (`TareaAgente.Profundidad`,
`PasoPadreNumero`, `ToolUseIdPadre`), `Entities/PropuestaRegla.cs` (comentario del uso M7a).

**Application** — Nuevos: `Settings/SubagentesOptions.cs`, `Motor/NotaSubtarea.cs` (+ `NombresHerramientasPlataforma`),
`Motor/IPreparadorTareaTrabajo.cs`, `Interfaces/ISubtareasService.cs` (+ `SubagenteDto`), `DTOs/SubtareasDtos.cs` (`MensajesSubtareas`).
Modificados: `Motor/IMotorAgentes.cs` (`ContextoHerramienta` + profundidad/base/versión, `IHerramientaDelegacion`, `TareaFiltros.IncluirSubtareas`,
`TareaListItemDto` + padre y cantidad, `PasoVisibleDto.PedidosLegibles`, `SubtareaDto`, `TareaRefDto`, `MotivoNoPuedeSeguir` 7 y 8,
`TareaDetalleDto` con partes/principal/costo total/agentes esperados, `FiltroTareas.Ocultar/MostrarPartes`),
`Interfaces/IPropuestaReglaService.cs` (`ListarPendientesParaMiAsync`), `DTOs/ConfiguradorDtos.cs` (`PropuestaReglaDto` + `EsDeTrabajo`,
`AutorNombre`, `AgenteOrigen`, `NoPuedeAccionarTexto`; `PropuestaFormularioDto.AgenteOrigen`), `DTOs/ReglasDtos.cs` (`OrigenAgenteTexto`),
`Helpers/BusquedaHelper.cs` (QA-M6-03: fecha corta "15/09").

**Infrastructure** — Nuevos: `Services/Motor/PreparadorTareaTrabajo.cs`, `Services/Subagentes/{SubtareasService, HerramientasSubagentes,
ResumenHerramientasPlataforma}.cs`, `Services/Reglas/HerramientaProponerRegla.cs`, migración
`Data/Migrations/20260915230800_SubagentesReglasPropuestasM7a.cs` (+ Designer y snapshot). Modificados:
`Services/Motor/ProcesadorTareas.cs` (herramientas de plataforma, nota del coordinador, recorrido del paso con partes, espera +
re-chequeo, `TrasFinAsync`/`GuardarYAvisarAsync`, `ReconstruirConversacion` con nota), `Services/Motor/ServicioTareas.cs` (crear por el
preparador, filtro Partes y chips, búsqueda por estado en palabras, detalle con partes/principal/costo total, ajuste bloqueado,
cancelación en cascada), `Services/Motor/ProveedorModeloSimulado.cs` (nombres exactos + guiones de delegación y de propuesta + parte que
falla), `Services/Motor/MotorAgentesWorker.cs` (barrido de partes), `Services/Configurador/{PropuestaReglaService,
HerramientasConfigurador}.cs` (permisos por tipo, pendientes para mí, `NombresPropuesta`), `Services/Reglas/ReglaService.cs` (aplicar
propuestas de trabajo, origen con nombre del agente), `Data/Configurations/AgentesConfigurations.cs`, `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/PropuestasReglaController.cs`, `Helpers/SubtareasTextos.cs`, vistas `Tareas/_TarjetaParte.cshtml`,
`Reglas/{_PropuestasAgentes, _PropuestaAgenteFila}.cshtml`. Modificados: `Controllers/{TareasController (filtro Partes, cancelar con
`volver`), ReglasController (card y agente de la propuesta)}.cs`, `Models/{ConfiguradorViewModels (TarjetasParte, PropuestasAgentes),
ReglasViewModels}.cs`, vistas `Tareas/{Detalle, _Conversacion, _CuadroSeguimiento, _EstadoTarea, _PasosTurno, _TarjetasPropuesta,
_ScriptPropuestas, Index}`, `Reglas/{Index, Detalle, _Form}`, `Consumo/_TablasConsumo` (CS8321), `wwwroot/css/site.css`, `appsettings.json`
(sección `Subagentes`).

**Tests**: nuevos `SubagentesTests.cs` (15), `ReglasPropuestasAgentesTests.cs` (6), `BusquedaFechaCortaTests.cs` (2) e `Infra/EntornoM7.cs`;
ajustados `AgentesOrganizacionTests` y `HerramientasDocumentosTests` (listas exactas de herramientas) y `ConfiguradorReglasTests` (nombres
exactos). **Repo**: `docs/diseno-organizacion-roles-reglas.md` (M7a ✅, M7b pendiente).

### Decisiones de implementacion M7a (ambigüedades resueltas)
- **DI-M7a-1 Sin endpoint propio de partes:** como en DI-M6-2, las tarjetas de parte se refrescan con `Tareas/Progreso` (el fragmento de
  la conversación); el procesador avisa por SignalR al padre cuando una parte arranca, espera aprobación o termina, y el respaldo de 10 s
  de la página cubre el resto. No se agregó `Tareas/Partes`.
- **DI-M7a-2 Preparador con las validaciones de agente:** `IPreparadorTareaTrabajo` expone también `ValidarAgenteAsync`,
  `ValidarAgenteOrganizacionAsync` y `SuscripcionVigenteAsync` para que `ServicioTareas` (vista previa, detalle, ajustes) no duplique
  consultas. Direcciones de dependencia: `ServicioTareas` → preparador + partes + propuestas; `SubtareasService` → preparador; ninguno al revés.
- **DI-M7a-3 Aviso al padre sin limpiar el ChangeTracker:** ante `DbUpdateConcurrencyException`, `AvisarFinAsync` desasocia solo la tarea
  principal y la relee (limpiar todo el tracker rompería la unidad de trabajo del procesador que lo llama).
- **DI-M7a-4 Cancelar una parte vuelve a la principal:** `Tareas/Cancelar` acepta `volver` (id de la principal) para el botón de la tarjeta;
  la visibilidad la sigue decidiendo el servicio.
- **DI-M7a-5 Prioridad del simulador:** con `delegar_subagente` ofrecida y "deleg" en el pedido, el guion de delegación gana sobre los de
  documentos y aprobaciones. Así la PARTE (que no delega) dispara esos guiones con el mismo texto y QA puede probar una aprobación o una
  lectura de documentos dentro de una parte. Además, una parte cuyo pedido dice "falle" termina Fallida (QA del resultado de fallo).
- **DI-M7a-6 "Ver pasos" llano centralizado:** `ResumenHerramientasPlataforma` arma los rótulos de delegación, consulta de subagentes,
  propuesta de regla **y de las acciones de demostración de M6** (QA-M6-04); `PasoVisibleDto.PedidosLegibles` los lleva alineados por índice.
- **DI-M7a-7 Orden de validación al aplicar una propuesta:** el mensaje "el configurador no crea preferencias" se responde antes que el
  estado y los permisos (comportamiento de M4b intacto); solo si la propuesta viene de una tarea de trabajo se admite el alcance Usuario.
- **DI-M7a-8 "Aplicar todas" en tareas de trabajo:** un Director que no es el autor aplica en masa solo las reglas de cliente; las
  preferencias ajenas quedan fuera de la selección (sin marcarlas fallidas).
- **DI-M7a-9 Card de propuestas en Reglas:** reusa `_ScriptPropuestas` con un contenedor alternativo (`#propuestasAgentes`); hasta 5
  tarjetas compactas y el resto en "Ver todas (N)".
- **DI-M7a-10 Tests con listas de herramientas:** ofrecer `proponer_regla` en toda tarea de trabajo cambia la lista que ven dos tests de
  M4/M5; se filtran las herramientas de plataforma en esas aserciones (el cambio es esperado, RT-M7-05).

### Migraciones EF generadas M7a
- `20260915230800_SubagentesReglasPropuestasM7a` — `AddColumn TareasAgente.Profundidad` (int, default 0), `PasoPadreNumero` (int null),
  `ToolUseIdPadre` (varchar(100) null) y único `(TareaPadreId, ToolUseIdPadre)`. **Corrección a mano:** MySQL no deja soltar
  `IX_TareasAgente_TareaPadreId` porque lo usa la FK; la migración saca la FK, cambia el índice y la repone (la FK se apoya en el prefijo
  del único). Sin transformación de datos: todas las tareas existentes quedan principales. El índice `(TenantId, Estado)` de
  `PropuestasRegla` ya existía desde M4b.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-15**, luego `database update AprobacionesYGastoM6` (Down OK) y `database update`
  otra vez; `has-pending-model-changes` limpio.
- Verificado EF → MySQL real (`scratchpad/verif-m7`, sin Anthropic): **31 pasos OK, 0 fallas, 0 restos**. Estructura (columnas, único con
  `NON_UNIQUE = 0`, FK repuesta, índice de propuestas); dos principales con `(NULL, NULL)` conviven y **1062 real** al repetir
  `(TareaPadreId, ToolUseIdPadre)`; subagentes permitidos por jerarquía + licencia (y `subagentes_listar`); preparar y guardar una parte con
  autor, cliente, profundidad y hash propios; espera que no despierta con partes sin terminar, aviso que la devuelve con `Intentos = 0` y
  barrido; listado sin/con partes con la subconsulta `CantidadSubtareas`, búsqueda por estado en palabras y por fecha corta (QA-M6-03),
  detalle con tarjetas y costo total y detalle de parte con principal; cancelación en cascada con cierre de turno; propuestas de agente de
  trabajo (tarjetas, card, aplicar como autor, Director sin permiso sobre la preferencia, reglas con `OrigenRegla.PropuestaAgente` y origen
  "Propuesta de «…»"). `EXPLAIN`: el conteo de partes usa el único nuevo (`ref`), el barrido usa `IX_TareasAgente_Estado_LeaseHasta` y la
  card usa `IX_PropuestasRegla_TenantId_Estado`.
- Impacto: 3 columnas nuevas en `TareasAgente` (todas las filas existentes quedan principales), un índice único nuevo y la FK recreada.

### Evidencia de build y tests M7a
- `dotnet build OlvidataAgentes.slnx`: **0 errores** (queda la advertencia preexistente CS0114 de `HomeController`; la CS8321 de
  `_TablasConsumo` que reportó QA quedó resuelta).
- `dotnet test tests/OlvidataAgentes.Tests`: **208 OK / 0 fallidos** (185 previos + 23 nuevos); golden de hash de formatos 1, 2 y 3 verdes
  sin cambios y la instantánea de una parte es idéntica a la de una tarea equivalente sin principal.
- Lecciones: (1) MySQL bloquea el cambio de índice que usa una FK (ver migración); (2) llamar al aviso del padre desde la unidad de trabajo
  del hijo obliga a desasociar en vez de limpiar el tracker; (3) el guion del simulador por prefijo era una bomba de tiempo: los nombres
  exactos tienen test de regresión; (4) el límite de gasto al delegar se prueba mejor contra el servicio (el motor frena antes el turno).
- Observación: `LectorDocumentosTests.Extraccion_que_supera_el_tiempo_queda_como_no_se_pudo_leer` (M5, por tiempos) falló una vez con la
  máquina cargada y pasó al repetirlo; es inestable por diseño, no por M7a.

### Riesgos residuales M7a
- Sin contenido real de coordinadores: en dev el rubro `inmobiliario` ya tiene `inmo-orquestador` publicado con todos sus agentes como
  hijos, que alcanza para QA.
- Con `MaxTareasPorCliente = 1` las partes corren en serie (aceptado, RT-M7-08): una tarea con 5 partes tarda 5 vueltas del worker.
- El re-chequeo inmediato y el barrido cubren la carrera de RT-M7-01; el test cubre el camino del barrido y el del aviso, no una carrera
  real de dos procesos (InMemory).
- `CostoConSubtareasUsd` suma solo un nivel (profundidad 1 hoy); si sube la profundidad hay que sumar recursivamente (la cancelación ya recorre).
- La cancelación en cascada reintenta hasta 3 veces si el worker toca una parte a la vez; con muchas partes en curso podría devolver
  "no se pudo cancelar" y hay que reintentar desde la pantalla.
- Verificación visual pendiente (QA): tarjetas de parte y su refresco en vivo, detalle de parte, filtro Partes y chips, tarjetas de regla
  propuesta y card en Reglas, mobile 390 y ambos temas.

### Proximos pasos pendientes M7a
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M7a).
- M7b (asignaciones a personas y asistente del Director) con la migración `AsignacionesAsistenteM7b`.
- Deuda fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; advertencia CS0114 de `HomeController` (template).

---
