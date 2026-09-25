<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M03 (1 bloques archivados)

- M3b — Seguir conversando sobre una tarea

---

# M3b — Seguir conversando sobre una tarea

Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` (P1–P8), `2-disenador-funcional.md` (D-M3b-1..7) y `3-arquitecto-mvc.md` M3b aprobados (incluido el proveedor simulado solo en Development); `4-presupuestador.md` omitido por decisión de Joaquín (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.

### Escaneo de reutilizacion M3b
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 (`ProcesadorTareas`, `_Progreso` + SignalR + respaldo 10 s, `TareasHub`) | Bucle reanudable extendido a multi-turno; el refresco en vivo pasa a `_Conversacion` y se reinicia tras enviar | Literal (extensión) |
| Template M2 (`Visibles()`, reintento de `CancelarAsync`, `FiltrosSesion`/`DataTableRequestHelper`, `RespuestasServicio.Json`, `ovPostAjax`/`ovToast`) | Visibilidad, concurrencia con `Version`, columnas y filtros nuevos, POST AJAX con 403/404 | Literal |
| Template M3 (`IConstructorContexto.CalcularAsync`, `ReglasAplicadasAsync`, consulta de licencias de `ValidarAgenteAsync`, `EntornoReglas`/`ModeloGuionado`) | "Reglas cambiaron", preferencias ajenas ocultas, suscripción vigente, entorno de tests | Literal |
| crm-olvidata | Caché de prompt por bloques → breakpoint en el último mensaje | Patrón |
| Catálogo / otros `5-implementador.md` | Sin conversación multi-turno persistida contra un modelo (los "conversación" de crm-olvidata son bots de WhatsApp) | Diseño nuevo → PAT-029 completado con rutas reales, `pendiente_verificar: false` |

### Archivos y capas modificadas M3b
**Domain**
- `Enums/EnumsAgentes.cs`: `TipoPasoTarea.MensajeUsuario = 3`, `CierreTurno = 4`.
- `Entities/Tareas.cs`: `TareaAgente.CantidadSeguimientos`, `UltimaActividadAt`.

**Application**
- `Motor/IMotorAgentes.cs`: `IServicioTareas.EnviarSeguimientoAsync`; `EstadoTurno`, `MotivoNoPuedeSeguir`, `MensajePersonaDto`, `TurnoDto`, `TurnoActivoDto`, `AgenteRefDto`; `TareaDetalleDto` + propiedades `init` (Turnos, TurnoActivo, CantidadSeguimientos, UltimaActividadAt, PuedeSeguir, Motivo, AjustesRestantes, MaxSeguimientos, LargoMaximoSeguimiento, ReglasCambiaron, AgenteRef, ClienteCarteraId, ClienteDadoDeBaja, AutorNombre, EsAutor, CantidadMensajes); `TareaListItemDto` + `Mensajes`, `UltimaActividad`; `TareaFiltros` + `ConAjustes`, `UltimaActividadDesde/Hasta`; `FiltroTareas.SoloPedido/ConAjustes`.
- `Motor/ModeloConversacion.cs`: `ContenidoCierreTurno` (JSON tipado) y `CacheConversacion.IndiceBloque`.
- `Motor/IConstructorContexto.cs`: `ReglasCambiaronAsync`.
- `DTOs/ReglasDtos.cs`: `GrupoReglasDto` + `Oculto`, `CantidadOculta`, `Autor`, `Cantidad`; `ReglasAplicadasDto.CantidadReglas` suma `Cantidad`.
- `Settings/MotorAgentesOptions.cs`: `MaxSeguimientosPorTarea = 20`, `LargoMaximoSeguimiento = 10000`; `MaxPasosPorTarea` documentado como por turno. `Settings/AgentesSettings.cs`: `AnthropicSettings.Simulado`.

**Infrastructure**
- `Services/Motor/ServicioTareas.cs`: `EnviarSeguimientoAsync` (guardas en el orden de la arquitectura, un solo `SaveChanges` mensaje + re-apertura, 2 pasadas ante `DbUpdateException`, telemetría `seguimiento_enviado`); `ObtenerDetalleAsync` por turnos (respuesta = texto del paso `end_turn`, estado por `CierreTurno` o por la tarea en el último turno, nombres por id sin `List<string>.Contains`), puede seguir/motivo, `ReglasCambiaron` solo para el autor; `ReglasAplicadasAsync` con grupo de preferencias oculto; `CancelarAsync` agrega `CierreTurno` (porUsuarioId) y reintenta ante `DbUpdateException`; `ListarAsync` con Mensajes, Última actividad, filtros, búsqueda global y orden por defecto; `CrearAsync` fija `UltimaActividadAt`.
- `Services/Motor/ProcesadorTareas.cs`: `ReconstruirConversacion` normalizada (público, estático); `LlamadasDelTurno`; `MarcarFinAsync` con `CierreTurno` en todo fin Fallida (máximo de pasos, rechazo, max_tokens, fin inesperado, contexto no reconstruible, reintentos agotados al reclamar, `RegistrarErrorAsync`); `UltimaActividadAt` en cada paso y al finalizar; conversación demasiado larga → Fallida sin reintento; `GuardarAsync` distingue carrera del índice `(TareaAgenteId, Numero)`.
- `Services/Motor/ProveedorModeloAnthropic.cs`: `MapearMensajes` (público) con `CacheControlEphemeral` en el último texto/resultado del último mensaje.
- `Services/Motor/ProveedorModeloSimulado.cs` (nuevo) y `DependencyInjection.UsarModeloSimuladoSiCorresponde`.
- `Services/Motor/ConstructorContexto.cs`: `ReglasCambiaronAsync`.
- `Data/Configurations/AgentesConfigurations.cs`: default de `CantidadSeguimientos`, índice `(TenantId, UltimaActividadAt)`.
- Migración `Data/Migrations/20260914201323_ConversacionM3b.cs` (+ Designer y snapshot).

**Web**
- `Controllers/TareasController.cs`: `EnviarSeguimiento` POST JSON (`ValidateAntiForgeryToken`, 403/404 vía `RespuestasServicio`), `Progreso` → `_Conversacion`, `Listar` con Mensajes y Última actividad.
- `Models/TareasViewModels.cs` (nuevo): `SeguimientoViewModel`. `Models/ReglasViewModels.cs`: `CantidadReglas` suma `Cantidad`.
- Vistas: `Tareas/Detalle` (reescrita: encabezado, reglas plegadas + aviso de reglas cambiadas, script de envío/copiar/refresco), `Tareas/_Conversacion`, `Tareas/_PasosTurno`, `Tareas/_CuadroSeguimiento` (nuevas), `Tareas/Index` (columnas y filtros), `Shared/_ReglasEfectivas` (grupo oculto); **eliminada** `Tareas/_Progreso`.
- `Program.cs`: registro del modelo simulado + advertencias de log. `wwwroot/css/site.css`: `.ov-chat*`, cuadro sticky en mobile. `appsettings.json` (`MaxSeguimientosPorTarea`, `LargoMaximoSeguimiento`), `appsettings.Development.json` (`Anthropic:Simulado: false` documentado).
- `AgentesController.Ejecutar`: sin cambios; ya aceptaba `clienteCarteraId` por query y el `<option>` con `asp-for` lo preselecciona (D-M3b-5).

**Tests**: nuevo `ConversacionTests.cs` (22: 16 `Fact` + `Theory` de 6 casos).

**Docs del repo**: `docs/diseno-organizacion-roles-reglas.md` (M3b ✅), `docs/diseno-motor-agentes.md` §4 (multi-turno y modelo simulado).

### Decisiones de implementacion M3b (ambigüedades resueltas)
- **DI-M3b-1 Mensajes:** mensajes de la persona = pedido + ajustes (`1 + CantidadSeguimientos`), igual en el detalle ("N mensajes") y en la columna del listado; "Solo el pedido" = 0 ajustes.
- **DI-M3b-2 Cierres heredados:** una tarea Fallida o Cancelada anterior a M3b (sin `CierreTurno`) recibe el cierre en el mismo guardado del primer ajuste, así su error sigue visible en su turno. Cierre sin usuario → "Se canceló esta respuesta."
- **DI-M3b-3 Autor:** miembro de la organización de la tarea con su `UsuarioId`; staff y procesos sin usuario nunca. Las preferencias se ocultan a todo el que no sea autor ni staff (incluidos scopes sin usuario) y muestran el nombre completo del autor.
- **DI-M3b-4 Largo:** como DI-M3-7, el service normaliza `\r\n` → `\n` y recorta; el ViewModel solo tiene `[Required]` (con `StringLength` el navegador contaría doble los saltos). 10.000 exactos se aceptan.
- **DI-M3b-5 Carreras de `Numero`:** en el service, `DbUpdateException` (versión o índice único) → se descartan los pendientes y se reintenta (ajuste 2 pasadas, cancelar 3). En el procesador, solo se trata como carrera si la `Version` en la base ya no es la leída; si no, se relanza.
- **DI-M3b-6 Normalización extra:** un paso del modelo sin bloques se omite; un `tool_use` pendiente al final de la secuencia también recibe resultado sintético.
- **DI-M3b-7 Conversación demasiado larga (RT-M3b-03):** `RegistrarErrorAsync` detecta por texto del error ("prompt is too long", "request_too_large", "exceeds the context window") y deja el turno Fallido sin reintentos con "La conversación es demasiado larga. Empezá una tarea nueva."
- **DI-M3b-8 Pantalla:** "Cancelar" vive en la línea de estado dentro del parcial refrescable (aparece y desaparece en vivo) en lugar del encabezado; "Nueva tarea con este agente" en el encabezado solo para miembros, con cliente precargado salvo dado de baja. El cuadro se re-renderiza en cada refresco: mientras hay turno activo el textarea está deshabilitado, así que no se pisa texto escrito (REG-008). JS con delegación.
- **DI-M3b-9 Modelo:** la vista usa `TareaDetalleDto` (propiedades `init`) en vez de un `TareaConversacionViewModel` espejo; `Pasos`, `Resultado` y `Error` planos se conservan por compatibilidad (tests M1).
- **DI-M3b-10 Búsqueda global:** también matchea la cantidad de mensajes y la fecha de última actividad (regla 25).
- **DI-M3b-11 Modelo simulado:** extensión de Infrastructure que exige `IsDevelopment()` + `Anthropic:Simulado`; el proveedor además se niega fuera de Development. Demora 1,5 s (para ver "Trabajando"), 0 tokens, texto "Respuesta simulada al turno N. Recibí: «…»". El portal loguea advertencia si está activo o si se pidió fuera de Development.
- **DI-M3b-12 Costo:** "USD 0,12" con hasta 4 decimales (tareas baratas no quedan en 0,00).
- **DI-M3b-13 Texto de cancelación:** "Respuesta cancelada. Si el agente estaba en medio de un paso, se detiene al terminarlo."

### Migraciones EF generadas M3b
- `20260914201323_ConversacionM3b` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14** con `dotnet ef database update`. Columnas `CantidadSeguimientos int NOT NULL DEFAULT 0` y `UltimaActividadAt datetime(6) NOT NULL` + `migrationBuilder.Sql` de backfill `COALESCE(FinalizadaAt, IniciadaAt, CreatedAt)` + índice `IX_TareasAgente_TenantId_UltimaActividadAt`. Los tipos de paso nuevos son valores int (sin esquema).
- Verificado por SQL (`scratchpad/verif-conversacionm3b.sql`): tipos y default correctos; índice de 2 columnas; backfill 7/7 (0 sin fecha); `EXPLAIN` del listado por organización usa el índice nuevo con *Backward index scan*; pasos tipo 3 y 4 con JSON válido y tildes en transacción revertida; `Numero` repetido → 1062; 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m3b`, modelo simulado, 37 pasos OK): crear, turno, detalle autor/Directora, ajuste 403, ajuste persistido y re-apertura, conversación alternada, **doble envío concurrente con reversión real del paso perdedor**, cancelar con cierre, ajuste fusionado sin cierre al modelo, 4 turnos en el detalle, listado (orden, filtros, búsqueda por fecha y por mensajes, orden por columnas), reintentos agotados y "prompt demasiado largo" con cierre (MAX de `Numero`), ajuste sobre Fallida. Sin errores de type mapping (MH-001). Limpieza de 3 tareas, 11 pasos y 11 eventos; 0 restos.
- Impacto: 2 columnas en `TareasAgente` con backfill; datos existentes intactos.

### Evidencia de build y tests M3b
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **83 OK / 0 fallidos** (61 existentes + 22 de `ConversacionTests`).
- Lecciones: (1) EF InMemory no es transaccional: un `SaveChanges` que falla por concurrencia deja aplicado el INSERT previo; la atomicidad se prueba en MySQL. (2) `SerializacionBloques` (JsonSerializerDefaults.Web) escapa no ASCII en el JSON guardado: comparar el texto deserializado. (3) C# no admite `await` en filtros `catch … when`.

### Riesgos residuales M3b
- RT-M3b-02 costo creciente y caché: el tercer breakpoint no se midió con la API real (medir `cache_read` en la corrida con OK de costo de Joaquín).
- RT-M3b-03: la detección de "conversación demasiado larga" depende del texto del error del SDK; confirmar en corrida real.
- La carrera del índice `(TareaAgenteId, Numero)` en el procesador se cubrió por revisión de código y SQL (1062), no reproducida contra MySQL.
- `UltimaActividadAt` no cambia al reclamar ni al renovar el lease (solo mensajes, pasos y cierres, según la arquitectura).
- Verificación visual pendiente (QA): burbujas y alertas en tema oscuro, cuadro sticky en mobile, Select2 del filtro Mensajes, reinicio del canal SignalR tras enviar, portapapeles (HTTPS).
- Deuda preexistente vista, fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; `Admin licencia-crear` con `slugs.Contains` (MH-001).

### Proximos pasos pendientes M3b
- QA etapa 6 (guía en `trazabilidad.md`, entrada del implementador M3b), con el modelo simulado activo.
- Corrida real con costo (OK de Joaquín): calidad de ajustes, `cache_read` en el segundo turno, error de prompt largo.

---

## Historial de ajustes

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 15 bloques (2026-09-14 a 2026-09-25) → [`5-implementador-2026-09.md`](historial/5-implementador-2026-09.md)
