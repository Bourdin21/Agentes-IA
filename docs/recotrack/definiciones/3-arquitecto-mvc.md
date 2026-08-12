# Memoria - Arquitecto MVC

## Proyecto: recotrack
## Ultima actualizacion: 2026-08-11

> Contenido migrado desde `C:\Sistemas\recotrack\docs\recotrack\definiciones\3-arquitecto-mvc.md` (unica copia existente hasta ahora) y ampliado con decisiones tomadas fuera de pipeline formal (fix de produccion 2026-08-11). Esta ubicacion centralizada pasa a ser la fuente de verdad.

## Definiciones vigentes

### Componentes por capa

Arquitectura en 4 capas (Clean Architecture), consistente con el baseline BlankProject:

- `RecoTrack.Domain` — Entidades (`EntityBase`: `Id`, `CreatedAt`, `CreatedByUserId`, `UpdatedAt`, `UpdatedByUserId`; **sin soft delete**, a diferencia del baseline `SoftDestroyable`) + Enums.
- `RecoTrack.Application` — Interfaces (`IRepository<T>`, `IEmailService`, `IChoferRegistrosService`, etc.) + DTOs (`ServiceResult`, `DataTableRequest/Response`).
- `RecoTrack.Infrastructure` — `RecoTrackDbContext`, repositorios genericos, servicios concretos, `SeedData`, `VencimientoCronJob` (BackgroundService).
- `RecoTrack.Web` — Controllers, ViewModels, Views, Middleware (`ErrorEmailNotifierMiddleware`).
- `RecoTrack.Tools.ImportPadron` — proyecto de consola separado para importacion de padron de empleados (no forma parte de la app web).

### Entidades y configuraciones EF

- `MultaChofer` y `AccidenteChofer` tienen columna `Hora` mapeada como `TimeOnly?` en el dominio, con conversion explicita EF Core `HasConversion` a `TimeSpan?` (ver A-09).
- `EstadoEmpleado` se mapea como columna `int NOT NULL DEFAULT 1` en MySQL 8. No se usa `HasConversion` para el enum; EF Core lo mapea directamente (A-07, iteracion 1).

### Migraciones requeridas

- `FixHoraTimeOnlyMapping` (2026-08-11): `ALTER COLUMN Hora time -> time(6)` en `MultasChofer` y `AccidentesChofer`, consecuencia de A-09. Generada localmente, **pendiente de aplicar en produccion** (deploy manual, sin `Migrate()` automatico en `Program.cs`).

### Riesgos tecnicos activos

- **R-01**: no hay `Migrate()` automatico al iniciar la app (`Program.cs`). El deploy (FTP, `DeleteExistingFiles=false`) y las migraciones EF son pasos manuales separados — riesgo de drift entre schema de produccion y modelo de codigo si se olvida el paso de `dotnet ef database update`. Causa raiz confirmada del incidente A-09/A-10.
- **R-02**: el email de notificacion de errores (`ErrorEmailNotifierMiddleware`) dependia de una clave de configuracion (`Notificaciones:ErrorEmail:Destinatarios`) que nunca existio en `appsettings.Production.json` (la real es `Olvidata_ErrorEmail:Destinatarios`). Corregido 2026-08-11 (A-10) — antes de este fix, ninguna excepcion no manejada en produccion generaba alerta por mail.
- **R-03**: `ConnectionStrings` usa la clave `RecoTrackMySql` en vez de `DefaultConnection` (clave esperada por `24-config-paquetes.instructions.md`). No es un bug funcional, pero diverge del estandar documentado para proyectos nuevos; no se recomienda renombrar sin necesidad (tocaria `appsettings.Production.json` en un host compartido).

## Decisiones arquitectonicas tomadas

| # | Decision |
|---|----------|
| A-01 | `DuplicarMasivoAsync` procesa cada trabajo con su propia transaccion EF (`BeginTransactionAsync` + `CommitAsync`/`RollbackAsync`) para garantizar que un fallo individual no contamine el contexto ni revierta los demas. |
| A-02 | El endpoint `DuplicarMasivo` retorna `ServiceResult<DuplicarMasivoResultDto>` y el controller lo serializa como JSON (respuesta AJAX), coherente con el patron `GetData` existente. |
| A-03 | `GetCodigosRazonSocialAsync` extrae prefijos con una unica consulta LINQ proyectada (sin cargar entidades completas) y aplica `Distinct().OrderBy()` en memoria. |
| A-04 | No se introduce indice compuesto nuevo en `Trabajos` en esta iteracion; el volumen esperado no lo justifica. Se deja como mejora futura documentada. |
| A-05 | No se agregan Authorization Policies nuevas; se mantiene el patron `[Authorize(Roles = SeedData.RolX)]` del proyecto (no usa el esquema de Policies `RequireAdministracion`/`RequireSuperUsuario` del baseline BlankProject — ver roles reales en seccion siguiente). |
| A-06 | El limite de trabajos por operacion de duplicado masivo se lee desde `appsettings.json` (`App:DuplicarMasivoMaxItems`, default 200), reutilizando el patron de `UmbralAviso` ya existente. |
| A-07 | `EstadoEmpleado` se mapea como columna `int NOT NULL DEFAULT 1` en MySQL 8. No se usa `HasConversion`; EF Core mapea el enum directamente. |
| A-08 | El archivo JS de duplicacion masiva se agrega como `wwwroot/js/trabajo-duplicar-masivo.js` y se referencia desde la seccion `Scripts` de `Index.cshtml`, coherente con `trabajo-empleados.js` existente. |
| A-09 | **(2026-08-11)** `MultaChofer.Hora` y `AccidenteChofer.Hora` (`TimeOnly?`) reciben un `HasConversion` explicito a `TimeSpan?` en `RecoTrackDbContext`. Motivo: `MySql.EntityFrameworkCore` 10.0.1 devuelve `TimeSpan` desde el driver para columnas `TIME`, pero el mapeo nativo a `TimeOnly` intenta un cast directo que revienta en runtime (`InvalidCastException`) al traer filas con `Hora` no nula — reproducible solo contra el MySQL de produccion (site4now.net), no en el entorno de desarrollo. El tipo CLR de la entidad (`TimeOnly?`) no cambia; solo cambia el mapeo a nivel de proveedor. Efecto colateral: el store type default pasa de `time` a `time(6)` (mas precision, sin perdida de datos). |
| A-10 | **(2026-08-11)** `ErrorEmailNotifierMiddleware` corrige la clave de configuracion leida, de `Notificaciones:ErrorEmail:Destinatarios` (inexistente) a `Olvidata_ErrorEmail:Destinatarios` (la real, poblada en `appsettings.Production.json` con `olvidatasoft@gmail.com`), alineando con el estandar documentado en `24-config-paquetes.instructions.md`. |

## Convenciones reales del proyecto (relevado 2026-08-11, para uso de `documentador`/`implementador`)

- **Roles**: `SeedData.RolAdmin` ("Administrador"), `RolSupervisor` ("Supervisor"), `RolOperador` ("Operador"), `RolTaller` ("Taller"). Autorizacion via `[Authorize(Roles = SeedData.RolX + "," + SeedData.RolY)]`, **no** via `AddPolicy`/`RequireAdministracion` como en el baseline BlankProject.
- **Exportacion a Excel**: `ExcelReporteHelper` (helper estatico) + `ClosedXML` directo en los servicios (ej. `ChoferRegistrosService.ExportarMultasExcelAsync`). No hay abstraccion `IExportService`.
- **Notificaciones**: solo por email (`IEmailService` + `INotificacionVencimientoService`), sin sistema de notificaciones in-app.
- **Manejo de errores**: `UseExceptionHandler("/Home/Error")` + `ErrorEmailNotifierMiddleware` propio (no existe una clase `GlobalExceptionHandler` ni interfaz `IErrorNotifier` como en el baseline).
- **Cron jobs**: `VencimientoCronJob` como `IHostedService`, corre 1° de cada mes 10:00 AM Buenos Aires.
- **Logging**: Serilog a archivo (`Logs/recotrack-{prod|dev}-*.log` y `Logs/recotrack-errors-*.log`), sin sink a base de datos ni a servicio externo.

## Historial de ajustes
- 2025-07: Iteracion 1 (Duplicado masivo + Estado Empleado + Formato Legajo) — arquitectura completada, decisiones A-01 a A-08.
- 2026-08-11: migrado el contenido desde el repo local a esta ubicacion centralizada. Agregadas A-09 y A-10 (fix de produccion: cast TimeOnly/MySQL + clave de config del email de errores). Agregados riesgos R-01/R-02/R-03 y seccion de convenciones reales relevadas del codigo. **Pendiente**: no existe arquitectura formal documentada para las iteraciones de vencimientos por rol / estado de camiones / rol Taller / tipo de camion / reporte de disponibilidad (jun-2026) — ver nota en `5-implementador.md`.
