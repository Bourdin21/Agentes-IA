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

### Servicios de Importacion (`Services/*`)

Los servicios de importacion viven **todos en `Services/`** (plano): `CategorizadorMovimientos`,
`ProvinciaMastercardResumenParser`, `ProvinciaVisaResumenParser`, `ResumenTarjetaImporter`. La
carpeta `Services/Importacion/` existio como resto de una migracion vieja con 4 archivos `.cs` de
0 bytes y fue **eliminada** (2026-08-31); no hay copias duplicadas de estas clases.

Flujo de importacion (unico flujo vivo):
1. **Parser** lee PDF y entrega lista de movimientos crudos + cuotas detectadas.
2. **Categorizador** asigna categoria sugerida por reglas (mapas de palabras clave).
3. **Importer.PreviewImportacionAsync**: arma DTO de preview sin persistir.
4. Usuario revisa/edita en `Views/Importacion/Preview.cshtml`.
5. **Importer.ConfirmarImportacionAsync**: persiste movimientos y reutiliza cuotas existentes (`CuotasReutilizadas`) o crea nuevas.

> `ImportarResumenAsync` (un segundo camino PDF -> persistencia directa, sin preview) fue
> **eliminado** del importer y de `IResumenTarjetaImporter` el 2026-08-31: no tenia ningun caller
> en el repo y habia divergido del flujo real, lo que lo volvia una fuente de confusion.

#### Clave de deduplicacion (idempotencia del import)

La clave es **`UsuarioId + CuentaId + Fecha.Date + DescripcionOriginal`**.

- **`Monto` NO forma parte de la clave.** En lineas en dolares el monto en pesos es un valor
  *derivado* (`MontoUsd x cotizacion del momento del import`) que puede variar levemente entre
  dos importaciones del mismo PDF; incluirlo hacia que el duplicado no se detectara.
- `DescripcionOriginal` es la **linea cruda del PDF** (`DescripcionRaw`), que incluye el numero de
  cupon y por lo tanto distingue dos consumos distintos del mismo comercio, el mismo dia, por el
  mismo importe. Si el parser no la pobla, se cae a la descripcion limpia.
- Caso especial — **fila sintetica de impuestos** (`IMPUESTO CREDITO MASTERCARD`): totaliza varias
  lineas y no tiene cupon. Su `DescripcionRaw` se compone como
  `IMPUESTO CREDITO MASTERCARD {fecha:yyyy-MM-dd} {totalPesos:F2} {totalDolares:F2}` para que un
  resumen reemitido del mismo periodo **con impuestos corregidos** genere una clave distinta y el
  importe nuevo entre, en vez de descartarse en silencio contra la fila vieja.
- La deduplicacion se evalua **dos veces**: en `PreviewImportacionAsync` (para marcar
  `EsDuplicado`/`Excluir`) y **de nuevo en `ConfirmarImportacionAsync` contra la base**. La
  segunda es obligatoria: el flag `Excluir` viaja al navegador como campo oculto y lo controla el
  cliente, asi que un doble click en Confirmar, un F5 o un reenvio del POST duplicaban el resumen
  entero. Los items salteados se contabilizan en
  `ResultadoImportacionResumen.MovimientosOmitidosPorDuplicado` (no son error, no abortan el lote).

#### Cuotas N/M con N > 1

Las cuotas cuyo numero de cuota es mayor a 1 **ya no se excluyen por defecto** del import. El
caso real es empezar a usar la app con una compra en cuotas ya en curso: la primera importacion de
esa cuota puede ser una 05/12, no una 01/12.

Consecuencia: al crear una `Cuota` nueva desde el confirm, `FechaInicio` se **retrocede** N-1
meses respecto de la fecha del movimiento:

```
FechaInicio = item.Fecha.AddMonths(-(item.NumeroCuota ?? 1) + 1)
```

Sin ese backdating, la fecha de fin calculada (`FechaInicio + CantidadCuotas - 1`) queda corrida
varios meses y la cuota se muestra como activa/vigente mas tiempo del que corresponde en
`DashboardController.ObtenerCuotasActivas` y `HomeController` (`CuotasVigentes`).

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
