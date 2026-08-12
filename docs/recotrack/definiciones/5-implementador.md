# Memoria - Implementador

## Proyecto: recotrack
## Ultima actualizacion: 2026-08-11

> Contenido migrado desde `C:\Sistemas\recotrack\docs\recotrack\definiciones\5-implementador.md` (unica copia existente hasta ahora) y ampliado con el trabajo de produccion del 2026-08-11. Esta ubicacion centralizada pasa a ser la fuente de verdad.

## Definiciones vigentes

### Archivos y capas modificadas

**Iteracion 1 — Duplicado masivo de Trabajos + Estado Empleado + Formato Legajo** (COMPLETADO — Build OK)

Input aprobados: `1-analista-funcional.md`, `2-disenador-funcional.md`, `3-arquitecto-mvc.md`, `4-presupuestador.md`.

| Etapa | Descripcion | Estado |
|-------|-------------|--------|
| E1 | Domain: enum EstadoEmpleado + propiedad + DbContext + migracion | OK |
| E2 | Application: DTOs + interfaces | OK |
| E3 | Infrastructure: EmpleadoService + TrabajoService | OK |
| E4 | Web - Empleados: ViewModels + Controller + Vistas | OK |
| E4b | Web - Trabajos: ViewModels + Controller + Index + JS | OK |
| E5 | Build + verificacion | OK |

| Capa | Archivo | Motivo |
|------|---------|--------|
| Domain | `Enums/DomainEnums.cs` | + enum EstadoEmpleado |
| Domain | `Entities/Empleado.cs` | + propiedad EstadoEmpleado |
| Infrastructure | `Data/RecoTrackDbContext.cs` | + HasDefaultValue Empleado |
| Infrastructure | Migracion EF | + columna EstadoEmpleado |
| Application | `DTOs/EmpleadoDtos.cs` | + EstadoEmpleado en 3 DTOs |
| Application | `DTOs/TrabajoDtos.cs` | + 3 DTOs de duplicacion masiva |
| Application | `Interfaces/IEmpleadoService.cs` | + GetCodigosRazonSocialAsync |
| Application | `Interfaces/ITrabajoService.cs` | + DuplicarMasivoAsync |
| Infrastructure | `Services/EmpleadoService.cs` | + mappers EstadoEmpleado + GetCodigosRazonSocialAsync |
| Infrastructure | `Services/TrabajoService.cs` | + DuplicarMasivoAsync |
| Web | `Models/EmpleadoViewModels.cs` | + CodigoRazonSocial, NumeroLegajo, EstadoEmpleado, CodigosDisponibles |
| Web | `Controllers/EmpleadosController.cs` | + GetCodigosRazonSocial; adaptar Create/Edit |
| Web | `Views/Empleados/Create.cshtml` | Rediseno legajo + dropdown Estado |
| Web | `Views/Empleados/Edit.cshtml` | Idem + descomposicion legajo |
| Web | `Views/Empleados/Index.cshtml` | + columna Estado con badge |
| Web | `Models/TrabajoViewModels.cs` | + DuplicarMasivoViewModel + ResultViewModel |
| Web | `Controllers/TrabajosController.cs` | + DuplicarMasivo + GetFilteredIds |
| Web | `Views/Trabajos/Index.cshtml` | + checkboxes + barra contextual + modal |
| Web | `wwwroot/js/trabajo-duplicar-masivo.js` | JS nuevo completo |
| Web | `appsettings.json` | + App:DuplicarMasivoMaxItems |

---

**Iteracion 2 — Separacion de vencimientos por rol (Operador/Taller/Admin)** (COMPLETADO — Build OK, 0 errores)

Input: Requerimiento funcional en conversacion — **sin docs de analisis formales** (salteo explicito de etapas 1-4 del pipeline).

| Etapa | Descripcion | Estado |
|-------|-------------|--------|
| E1 | Application/Infrastructure: extender NotificacionSettings + INotificacionVencimientoService | OK |
| E2 | Infrastructure: implementar DetectarVencimientosChoferesAsync, DetectarVencimientosCamionesAsync, EnviarNotificacionesChoferesAsync, EnviarNotificacionesCamionesAsync; refactorizar EnviarNotificacionesAsync para delegar | OK |
| E3 | Configuracion: agregar DestinatariosTaller en appsettings.json y appsettings.Production.json | OK |
| E4 | Web: agregar Taller a autorizacion, filtrado en Index por rol, ContextoRol en ViewModel, titulo dinamico en vista | OK |
| E5 | Build + verificacion | OK — 0 errores |

| Capa | Archivo | Motivo |
|------|---------|--------|
| Infrastructure | `Services/NotificacionSettings.cs` | + DestinatariosTaller |
| Application | `Interfaces/INotificacionVencimientoService.cs` | + 4 metodos filtrados por tipo |
| Infrastructure | `Services/NotificacionVencimientoService.cs` | Implementar Detectar/Enviar por tipo; refactorizar EnviarNotificacionesAsync |
| Web | `appsettings.json` | + DestinatariosTaller:[] |
| Web | `appsettings.Production.json` | + DestinatariosTaller:[""] (placeholder a completar) |
| Web | `Controllers/NotificacionesController.cs` | + using Domain.Entities; + Taller en [Authorize]; filtrado de vencimientos por rol en Index(); ContextoRol en ViewModel |
| Web | `Models/NotificacionesViewModels.cs` | + propiedad ContextoRol |
| Web | `Views/Notificaciones/Index.cshtml` | Titulo dinamico segun ContextoRol; boton Enviar solo visible a Admin/Supervisor |

Notas: `VencimientoCronJob` no requirio cambios (llama a `EnviarNotificacionesAsync()`, que ahora delega internamente). `appsettings.Production.json`: `DestinatariosTaller` quedo con placeholder `""`, pendiente que el cliente confirme el email del area Taller.

---

**Ajuste de produccion 2026-08-11 — Fix cast TimeOnly/MySQL + email de errores** (COMPLETADO — build OK, sin QA formal, sin analisis/diseno previos — incidente reactivo)

Input: reporte del cliente ("DataTables warning ... Ajax error" en `tblMultas`) — diagnosticado por log de produccion (`Logs/recotrack-errors-20260811.log`, descargado por FTP), sin pasar por analisis/diseno/arquitectura formales (incidente productivo, resolucion directa). Decisiones tecnicas registradas retroactivamente en `3-arquitecto-mvc.md` (A-09, A-10).

| Capa | Archivo | Motivo |
|------|---------|--------|
| Web | `Middleware/ErrorEmailNotifierMiddleware.cs` | Corrige clave de config leida: `Notificaciones:ErrorEmail:Destinatarios` -> `Olvidata_ErrorEmail:Destinatarios` (la real). Antes del fix, ninguna excepcion no manejada en produccion generaba email de alerta. |
| Infrastructure | `Data/RecoTrackDbContext.cs` | `HasConversion` explicito `TimeOnly? <-> TimeSpan?` para `MultaChofer.Hora` y `AccidenteChofer.Hora` — evita `InvalidCastException` al leer columnas `TIME` desde MySQL en produccion (`GetMultas`/`GetAccidentes` devolvian 500). |
| Infrastructure | Migracion EF `20260811202007_FixHoraTimeOnlyMapping` | `ALTER COLUMN Hora time -> time(6)` en `MultasChofer` y `AccidentesChofer`. Generada y verificada localmente (build OK). **No aplicada aun en produccion.** |

### Migraciones EF generadas

- `FixHoraTimeOnlyMapping` (2026-08-11) — pendiente de aplicar contra la base de produccion (`dotnet ef database update`, o via el flujo de deploy habitual del cliente).

### Riesgos residuales

- El fix de codigo (HasConversion) ya resuelve el `InvalidCastException` en cuanto se redeploye, independientemente de si la migracion se aplico o no — pero el modelo queda "pending changes" hasta aplicarla, lo que puede confundir a un `dotnet ef migrations add` futuro si no se corre antes.
- Cambios locales sin commitear al cierre de esta sesion (`git status`): `RecoTrackDbContextModelSnapshot.cs`, `RecoTrackDbContext.cs`, `ErrorEmailNotifierMiddleware.cs` modificados + migracion nueva sin trackear.
- No hubo QA funcional formal de este fix mas alla de `dotnet build` — no se corrio contra una base de datos real con datos de `Hora` poblados.

### Proximos pasos pendientes

- Commitear y deployar el fix (codigo + migracion) a produccion.
- Aplicar `dotnet ef database update` contra la base de site4now.net.
- Confirmar que las alertas de error por mail llegan correctamente tras el fix de config (probar con una excepcion controlada, o esperar la proxima real).
- Completar `DestinatariosTaller` en `appsettings.Production.json` (placeholder pendiente desde iteracion 2).
- Evaluar si conviene agregar `Migrate()` automatico al arranque para evitar drift schema/codigo (ver R-01 en `3-arquitecto-mvc.md`) — no implementado, requiere decision del cliente/arquitecto por el riesgo en hosting compartido.

## Historial de ajustes
- 2025-07: Iteracion 1 completada — build OK.
- 2026-06 (fecha exacta no registrada): Iteracion 2 completada — build OK, 0 errores. Salteo explicito de etapas de analisis/diseno formales.
- 2026-08-11: migrado el contenido desde el repo local a esta ubicacion centralizada. Agregado el ajuste de produccion del mismo dia (fix TimeOnly/MySQL + email de errores).
