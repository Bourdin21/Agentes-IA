<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/3-arquitecto-mvc.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 3-arquitecto-mvc - M03 (1 bloques archivados)

- M3b — Seguir conversando sobre una tarea

---

# M3b — Seguir conversando sobre una tarea

Estado: **aprobada por Joaquín el 2026-09-14** (puntos 1–5 del gate, incluido el proveedor simulado solo en Development). Entrada: análisis y diseño M3b aprobados 2026-09-14 (P1–P8, D-M3b-1..7). Presupuesto: omitido (proyecto personal).

### M3b-0. Escaneo de reutilizacion
| Fuente | Componente | Grado | Decisión |
|---|---|---|---|
| Template M1 — `ProcesadorTareas` (reconstrucción desde `PasoTarea`, reenvío de thinking, lease, `Version`) | Motor reanudable | **Literal (extensión)** | El seguimiento es un paso más de la conversación; el bucle no cambia de forma. |
| Template M1 — `_Progreso` + SignalR + respaldo 10 s, `TareasHub` | Progreso en vivo | **Literal** | El parcial pasa a renderizar la conversación. |
| Template M2 — `ServicioTareas.Visibles()`, `CancelarAsync` con reintento, listado con `FiltrosSesion` | Visibilidad, concurrencia, grilla | **Literal** | Base de `EnviarSeguimientoAsync` y de las columnas nuevas. |
| Template M3 — `IConstructorContexto`, `ReglasAplicadasAsync`, `ValidarAgenteAsync` | Instantánea, reglas aplicadas, suscripción | **Literal** | "Reglas cambiaron" = recalcular y comparar; preferencias ajenas ocultas en el mismo método; chequeo de suscripción reutilizado. |
| crm-olvidata | Caché de prompt en bloques | **Patrón** | Breakpoint de caché sobre el último mensaje de la conversación. |
| PAT-029 (este proyecto, diseño) | Conversación multi-turno reanudable | **Diseño nuevo** | Notas de arquitectura agregadas al catálogo. |

### M3b-1. Alcance técnico resumido
Seguimiento del autor persistido como paso de conversación con re-apertura atómica de la tarea; normalización de la conversación para la API tras turnos fallidos/cancelados; pasos por turno; cierre de turno persistido para conservar errores y cancelaciones por turno; caché de la conversación; detalle como lista de turnos; reglas cambiadas; preferencias ajenas ocultas; listado con mensajes y última actividad; atajo a nueva tarea.

### Componentes por capa M3b

**Domain**
- `EnumsAgentes.TipoPasoTarea`: + `MensajeUsuario = 3` (texto de un ajuste; `ContenidoJson` = `[BloqueTexto]`), + `CierreTurno = 4` (turno terminado como Fallida o Cancelada; `ContenidoJson` = `{estado, error, porUsuarioId?}`; nunca se envía al modelo).
- `TareaAgente`: + `CantidadSeguimientos` (int), + `UltimaActividadAt` (DateTime).

**Application**
- `Settings/MotorAgentesOptions`: + `MaxSeguimientosPorTarea` = 20, `LargoMaximoSeguimiento` = 10000. `MaxPasosPorTarea` pasa a significar **por turno** (se mantiene el nombre de configuración; doc actualizada).
- `Motor/IMotorAgentes.cs`:
  - `IServicioTareas.EnviarSeguimientoAsync(int tareaId, string texto)` → `ServiceResult` (`SinPermiso` si no es el autor; `NoEncontrado` si no es visible).
  - `TareaDetalleDto` se extiende con: `Turnos` (`TurnoDto(Numero, MensajePersona(Rotulo, Texto, Fecha), IReadOnlyList<PasoVisibleDto> Pasos, string? Respuesta, DateTime? RespuestaAt, EstadoTurno Estado, string? Error, string? CanceladoPor)`), `TurnoActivo?` (`Estado`, `PasoActual`, `MaxPasos`), `CantidadSeguimientos`, `UltimaActividadAt`, `PuedeSeguir`, `MotivoNoPuedeSeguir?` (`EnCurso`/`NoEsAutor`/`Limite`/`SinSuscripcion`), `AjustesRestantes`, `ReglasCambiaron`, `AgenteRef` (rubro, slug), `ClienteCarteraId?`, `ClienteDadoDeBaja`, `PedidaPor?`.
  - `EstadoTurno { Activo, Completado, Fallido, Cancelado }`.
  - `TareaListItemDto` + `Mensajes` + `UltimaActividad`; `TareaFiltros` + `ConAjustes?` + `UltimaActividadDesde/Hasta`.
- `Motor/IConstructorContexto.cs`: + `ReglasCambiaronAsync(InstantaneaContexto, SolicitudContexto)` → `bool` (recalcula con `CalcularAsync` y compara el conjunto ordenado de `(ReglaId, EventoId)` y de ids de reglas de plataforma).
- `DTOs/ReglasDtos.cs`: `GrupoReglasDto` + `Oculto` + `Cantidad` + `Autor?` (P6).

**Infrastructure**
- `Services/Motor/ServicioTareas.cs`:
  - `EnviarSeguimientoAsync`: `Visibles()` → autor (`tarea.UsuarioId == contexto.UsuarioId`, staff nunca) → estado ∈ {Completada, Fallida, Cancelada} → largo → `CantidadSeguimientos < Max` → suscripción vigente al rubro del agente de la tarea (misma consulta que `ValidarAgenteAsync`, sin exigir versión publicada: la tarea está anclada) → **un solo `SaveChanges`**: `PasoTarea(MensajeUsuario, Numero = max + 1)` + `Estado = Pendiente`, `Resultado/Error/FinalizadaAt/WorkerId/LeaseHasta = null`, `Intentos = 0`, `CantidadSeguimientos++`, `UltimaActividadAt`, `Version++`. `DbUpdateConcurrencyException` → relee y re-evalúa una vez (si otro envío ganó, responde "La tarea todavía está trabajando…"). Telemetría `seguimiento_enviado`; notificación `EstadoCambiado`.
  - `CancelarAsync`: además agrega `PasoTarea(CierreTurno, Cancelada, porUsuarioId)` en el mismo guardado (el token `Version` evita chocar con el `Numero` de un paso del worker; ante conflicto, reintento existente).
  - `ObtenerDetalleAsync`: arma turnos cortando la secuencia de pasos en cada `MensajeUsuario`; respuesta del turno = textos del último `LlamadaModelo` con `end_turn` del turno (D-M3b-3); estado del turno = `CierreTurno` si existe, si no Completado, y el último turno toma `tarea.Estado`; `ReglasCambiaron` solo se calcula si quien mira es el autor y la tarea tiene instantánea; `PuedeSeguir`/motivo con las mismas guardas que el envío.
  - `ReglasAplicadasAsync`: grupo `Usuario` oculto (solo cantidad y nombre del autor) si quien mira no es el autor ni staff (P6).
  - `ListarAsync`: columnas y filtros nuevos; orden por defecto `UltimaActividadAt` desc (D-M3b-4).
- `Services/Motor/ProcesadorTareas.cs`:
  - `ReconstruirConversacion` **normaliza** para cumplir las reglas de alternancia de la API: (1) omite `CierreTurno`; (2) si un `LlamadaModelo` con `tool_use` quedó sin `ResultadosHerramientas` (turno cortado), inserta resultados sintéticos `EsError = true` "La ejecución se interrumpió antes de terminar." para esos `tool_use_id` (no se persisten); (3) mensajes de usuario consecutivos (pedido/ajuste sin respuesta, o resultados de herramientas seguidos de un ajuste) se fusionan en un solo mensaje de usuario conservando el orden de bloques (resultados de herramientas primero). Los bloques de thinking se reenvían sin tocar.
  - Pasos del modelo contados **desde el último `MensajeUsuario`** para el máximo por turno.
  - `MarcarFin(Fallida)` (todos los caminos: máximo de pasos, rechazo, max_tokens, contexto no reconstruible, reintentos agotados en `ReclamarSiguienteAsync`/`RegistrarErrorAsync`) agrega `CierreTurno` en el mismo guardado.
  - `UltimaActividadAt` se actualiza en cada guardado de paso y al finalizar.
  - Tareas sin instantánea (M1/M2): mismo armado anterior de sistema; el seguimiento funciona igual (CA-M3b-12).
- `Services/Motor/ProveedorModeloAnthropic.cs`: breakpoint de caché (`CacheControlEphemeral`) en el **último bloque de texto o resultado de herramienta del último mensaje** (tercer breakpoint, además de B1 y B2): reutiliza el historial entre turnos y entre vueltas del bucle de herramientas. Bloques de thinking nunca llevan `cache_control`.
- `Services/Motor/ConstructorContexto.cs`: `ReglasCambiaronAsync`.
- Migración `ConversacionM3b`: columnas `CantidadSeguimientos` (int, default 0) y `UltimaActividadAt` (datetime, backfill `COALESCE(FinalizadaAt, IniciadaAt, CreatedAt)`), índice `(TenantId, UltimaActividadAt)`. Los tipos de paso nuevos son valores de enum int (sin cambio de esquema).

**Web**
- `TareasController`: + `EnviarSeguimiento` POST JSON (`ValidateAntiForgeryToken`; 403/404 vía `TipoError`); `Detalle` y `Progreso` renderizan `_Conversacion`; `Listar` con filtros nuevos.
- Vistas: `Tareas/Detalle` (encabezado, línea de totales, reglas plegadas + aviso, hilo, cuadro), `Tareas/_Conversacion` (reemplaza `_Progreso`: turnos, turno activo, `data-final`), `Tareas/_CuadroSeguimiento`, `Tareas/Index` (columnas y filtros), `Tareas/_ReglasAplicadas` (grupo oculto). JS: envío AJAX con Ctrl+Enter, contador, deshabilitado mientras hay turno activo, reinicio del canal SignalR/respaldo tras enviar (hoy solo arranca si la tarea estaba activa al cargar), scroll al último mensaje, copiar con `navigator.clipboard` y toast.
- `AgentesController.Ejecutar`: acepta `clienteCarteraId` en query para precargar (D-M3b-5; se valida igual al enviar).

### Modelo de permisos M3b
Sin policies nuevas. `EnviarSeguimientoAsync` decide: autor → sí; Director/Empleado no autor → `SinPermiso` (el Empleado ni la ve: `NoEncontrado`); staff → `SinPermiso`. Cancelar mantiene M2. Preferencias ajenas ocultas en el service (no en la vista).

### Migraciones requeridas M3b
**Sí**, leve: `ConversacionM3b` (2 columnas + backfill + índice).

### Estrategia de pruebas M3b
**xUnit (InMemory + `ModeloGuionado`, sin costo)** — `ConversacionTests.cs`:
- Seguimiento sobre Completada: el modelo recibe pedido → respuesta → ajuste; la tarea vuelve a Completada con la nueva respuesta; `CantidadSeguimientos`, tokens y costo acumulados.
- Normalización: (a) tras turno cancelado con `tool_use` sin resultados → resultados sintéticos antes del ajuste; (b) tras turno cancelado antes de cualquier respuesta → pedido y ajuste fusionados en un mensaje de usuario; (c) tras `max_tokens` → alternancia correcta; (d) `CierreTurno` nunca llega al modelo; (e) thinking reenviado intacto.
- Pasos por turno: un turno de seguimiento dispone de `MaxPasos` completo aunque el anterior usó varios.
- Guardas: Pendiente/EnCurso rechazado; no autor (Director) → `SinPermiso`; Empleado ajeno → `NoEncontrado`; staff → `SinPermiso`; límite 20; largo; suscripción vencida; doble envío concurrente (dos scopes con la misma `Version`) → uno solo prospera.
- Reanudación: reinicio con el `MensajeUsuario` ya persistido y tarea Pendiente → el worker la toma sin duplicar el ajuste (CA-M3b-13).
- Cierre de turno: Fallida por máximo de pasos y Cancelada registran `CierreTurno`; el detalle muestra error/cancelación en su turno.
- Caché: `SolicitudModelo` lleva la marca de caché en el último bloque elegible (verificado en `ModeloGuionado`/proveedor).
- Reglas cambiaron: editar/desactivar una regla o sumar una aplicable → `true`; sin cambios → `false`; el contexto del seguimiento sigue siendo el de la instantánea (hash igual).
- P6: Director ve el grupo de preferencias oculto con cantidad; autor y staff ven el texto.
- Tarea M1/M2 sin instantánea admite seguimiento.
- Listado: mensajes, última actividad, filtros y orden por defecto.
- Los 61 tests actuales siguen verdes.

**MySQL real (implementador):** migración con backfill e índice. **QA navegador (sin costo):** con el motor apagado los turnos quedan en cola; para ver respuestas sin gastar, QA puede usar tareas con pasos insertados en la base de desarrollo o un modelo simulado solo en entorno de desarrollo si el implementador lo deja disponible detrás de configuración (ver RT-M3b-06). Validación real de calidad y caché: corrida con OK de costo de Joaquín.

### Riesgos tecnicos M3b
- **RT-M3b-01 (alto) Reglas de la API sobre la conversación** (alternancia usuario/asistente, `tool_result` para cada `tool_use`, thinking intacto): cubierto por la normalización y sus tests; es la parte más delicada.
- **RT-M3b-02 (medio) Costo creciente por turno:** límite de 20, caché del historial, costo visible. Medir `cache_read` en la corrida real.
- **RT-M3b-03 (medio) Ventana de contexto:** 21 turnos con resultados largos de herramientas pueden acercarse al límite del modelo; si la API rechaza por tamaño, el turno falla con mensaje "La conversación es demasiado larga. Empezá una tarea nueva." (sin compactación, P7).
- **RT-M3b-04 (bajo) Choque de `Numero` de paso entre cancelar y el worker:** resuelto con el token `Version` + reintento.
- **RT-M3b-05 (bajo) `ReglasCambiaron` recalcula en cada vista del autor:** una consulta del constructor; aceptable.
- **RT-M3b-06 (medio) QA sin costo no ve respuestas nuevas** con el motor apagado. Propuesta: proveedor de modelo simulado (`Anthropic:Simulado = true`, solo se registra en Development, responde "Respuesta simulada al turno N") para validar la UI de punta a punta sin llamar a la API. Requiere aprobación.

### Gate M3b
Arquitectura lista para Implementación. Requiere aprobación de: paso `CierreTurno` para conservar el resultado de cada turno, normalización de la conversación con resultados sintéticos, breakpoint de caché sobre el último mensaje, `MaxPasosPorTarea` reinterpretado como por turno, y el **proveedor simulado solo en Development** para QA sin costo (RT-M3b-06).

---

## Historial de ajustes

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 5 bloques (2026-09-14 a 2026-09-14) → [`3-arquitecto-mvc-2026-09.md`](historial/3-arquitecto-mvc-2026-09.md)
- **historico** — 1 bloques → [`3-arquitecto-mvc-historico.md`](historial/3-arquitecto-mvc-historico.md)
