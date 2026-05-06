# 3 - Application e Infrastructure

## VirtualWallet.Application

Capa de contratos. **No tiene logica ejecutable significativa**: solo interfaces y DTOs que `Infrastructure` implementa y `Web` consume.

### Interfaces

| Interface | Implementacion | Proposito |
|---|---|---|
| `IRepository<T>` | `Repository<T>` | Repositorio generico EF Core (CRUD + IQueryable). Se usa cuando alcanza; los controllers tambien usan `DbContext` directo. |
| `ICotizacionService` | `CotizacionService` | Obtiene cotizacion USD/ARS (cache + fallback). |
| `ICotizacionMovimientosService` | `CotizacionMovimientosService` | Recalcula `MontoUsd` masivo en movimientos. |
| `ICategorizadorMovimientos` | `Services/Importacion/CategorizadorMovimientos` | Sugiere categoria/subcategoria al importar PDF. |
| `IResumenPdfParser` | `ProvinciaVisaResumenParser`, `ProvinciaMastercardResumenParser` | Parsea PDFs de resumen segun banco/marca. |
| `IResumenTarjetaImporter` | `ResumenTarjetaImporter` | Orquesta preview y confirmacion de importacion. |
| `IExportService` | `ExportService` (QuestPDF) | Genera PDF de reportes. |
| `IEmailService` | `EmailService` (SMTP) | Envia emails. Configurado por `SmtpSettings`. |
| `IErrorNotifier` | `ErrorNotifier` | Notifica errores no controlados (email + log). |
| `INotificationService` | `NotificationService` | CRUD de `Notification` in-app. |

### DTOs

- `ServiceResult<T>`: wrapper de resultado con `Success`, `Errors`, `Value`. **Convencion**: los servicios devuelven `ServiceResult` cuando hay logica de negocio, no excepciones.
- `DataTableDtos`: contrato server-side de DataTables (`DataTablesRequest`, `DataTablesResponse<T>`).
- `NotificationDtos`: DTOs de notificaciones para JSON polling.
- `ImportacionResumenDtos`: DTOs del flujo de importacion. Incluye `ResultadoImportacionResumen` con contador `CuotasReutilizadas` (renombrado desde `CuotasActualizadas`).

## VirtualWallet.Infrastructure

### `Data/VirtualWalletDbContext`

`DbContext : IdentityDbContext<ApplicationUser>`. Define `DbSet` de cada entidad, configura:

- Global query filter `IsDeleted == false` para todas las `SoftDestroyable`.
- Indices, longitudes (`Movimiento.DescripcionOriginal` con max 500 - migracion `ConstrainDescripcionOriginalLength`).
- Relaciones explicitas con `OnDelete(Restrict)` donde corresponde.
- `OnBeforeSaveChanges`/`OnAfterSaveChanges`: rellenan `CreatedAt`, `UpdatedAt`, `Created/UpdatedBy` y generan `AuditLog`. El soft delete (state `Deleted` interceptado y convertido a `Modified` con `IsDeleted=true`) se audita como `Delete`.

### Migraciones (`Data/Migrations`)

Orden cronologico:
1. `InitialIdentity`
2. `AuditSoftDeleteNotifications`
3. `SyncModelSnapshot`
4. `AddDescripcionOriginalToMovimiento`
5. `AddEsPagoTarjetaToMovimiento` (esta en una sub-carpeta `Mig/`; revisar si conviene moverla a `Migrations/`)
6. `ConstrainDescripcionOriginalLength`

Para produccion, se generan scripts SQL idempotentes en `Data/Migrations/Scripts/*.sql`.

### Servicios de Importacion (`Services/Importacion/*` y `Services/*`)

Hay **dos copias** de `CategorizadorMovimientos`, `ProvinciaMastercardResumenParser`, `ProvinciaVisaResumenParser` y `ResumenTarjetaImporter`: una en `Services/` y otra en `Services/Importacion/`. La copia "canonica" es la de `Services/Importacion/` (es la registrada en DI). La copia plana es legado a evaluar para borrado.

Flujo de importacion:
1. **Parser** lee PDF y entrega lista de movimientos crudos + cuotas detectadas.
2. **Categorizador** asigna categoria sugerida por reglas (mapas de palabras clave).
3. **Importer.PreviewImportacionAsync**: arma DTO de preview sin persistir.
4. Usuario revisa/edita en `Views/Importacion/Preview.cshtml`.
5. **Importer.ConfirmarImportacionAsync**: persiste movimientos y reutiliza cuotas existentes (`CuotasReutilizadas`) o crea nuevas.

### Servicios transversales

- `CotizacionService`: HttpClient hacia API publica con `IMemoryCache` (TTL configurable) y fallback al ultimo valor persistido.
- `EmailService` + `SmtpSettings`: envio SMTP con plantillas simples; usado por `ErrorNotifier` y notificaciones de cuenta.
- `DatabaseHealthCheck` y `SmtpHealthCheck`: registrados en `/health` y `/health/ready`. **Requieren autorizacion** (no anonymous).
- `ExportService`: usa QuestPDF (License Community fijada en `Program.cs`).

### Repositorio generico

`Repository<T> : IRepository<T>` es un wrapper minimo (`Add`, `Update`, `Remove`, `Query()`). Para queries complejas se usa `DbContext` directo en el controller, lo cual es aceptado en este codebase.

## Configuracion

`appsettings.json` + `appsettings.Development.json` + `appsettings.Production.json`. Claves principales:

- `ConnectionStrings:DefaultConnection` (MySQL).
- `Smtp:*` (host, port, user, pass, from).
- `Cotizacion:*` (URL, cache TTL).
- `Serilog:*` (sinks, niveles).
- `ErrorNotifier:To` y `From`.

Secretos en produccion van por **variables de entorno** o User Secrets en dev. **Nunca** commitear claves reales.
