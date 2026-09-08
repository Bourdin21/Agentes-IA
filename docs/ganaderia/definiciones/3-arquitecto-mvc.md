# Arquitectura Técnica — Sistema de Gestión Ganadera

Versión: **v3**
Agente: `3 - arquitecto-mvc`
Entradas:
- `docs/ganaderia/definiciones/1-analista-funcional.md` v12
- `docs/ganaderia/definiciones/2-disenador-funcional.md` v3
Repositorio de v2/v3: **`C:\Sistemas\ganaderia - emo`** (exclusivo; NO aplica a `ganaderia - fausto`). **Sistema en producción** — las migraciones deben preservar los datos ya cargados (`Egreso` en v2, `FacturaVenta.Motivo` en v3).

> Nota: §1–§12 documentan el diseño arquitectónico **original** (v1, previo a implementación) y quedan como referencia histórica; la implementación real ya diverge en nomenclatura (`Egreso` no `Gasto`, `FacturaVenta` no `Factura`, `JobEjecucion` no `Novedad` para idempotencia, `AcreditacionCuotasHostedService` no `AcreditacionDiariaHostedService`). El diseño técnico de v2 (§13) está grounded directamente en el código real de `ganaderia - emo`.

Proyecto: BlankProject (ASP.NET Core **MVC**, .NET 10, EF Core 10, MySQL 8, Identity, Serilog)
Solución base (existente):
- `BlankProject.Domain` — entidades + `SoftDestroyable`
- `BlankProject.Application` — DTOs (`ServiceResult`/`ServiceResult<T>`), interfaces (`IRepository<T>`, `INotificationService`, etc.)
- `BlankProject.Infrastructure` — `AppDbContext` (IdentityDbContext), repositorios, `NotificationService`, `EmailService`, migraciones
- `BlankProject.Web` — Controllers, Views, Helpers, Middleware

Alcance: definir componentes y responsabilidades por capa, identificar cambios concretos, evaluar migraciones EF, riesgos y estrategia de pruebas. **No** implementa código.

---

## 0. Salida mínima del agente

### 0.1 Alcance funcional resumido
Se instancia el diseño funcional v1 sobre las convenciones ya presentes en BlankProject. El módulo de gestión ganadera se suma como **vertical nueva** (namespace `Ganaderia`) en las cuatro capas, reutilizando:
- `SoftDestroyable` como base de todas las entidades nuevas.
- `ServiceResult` / `ServiceResult<T>` como contrato de salida de servicios.
- `IRepository<T>` genérico + repositorios específicos cuando haya consultas con joins pesados.
- `IdentityDbContext<ApplicationUser>` extendido con nuevos `DbSet<>`.
- Query filter global de soft delete ya configurado en `AppDbContext`.
- `INotificationService` existente como canal **in-app** para las novedades del job diario (§9 análisis).
- Roles Identity: `Productor` y `SuperUsuario` (a agregar en seed).

### 0.2 Impacto técnico por capa
- **Domain** (+14 entidades, +8 enums, +1 matriz estática).
- **Application** (+12 interfaces de servicios, +DTOs/VMs de lectura, +contratos de lectura).
- **Infrastructure** (+14 `DbSet<>` en `AppDbContext`, +configuraciones fluent, +2 migraciones EF, +10 implementaciones de servicio, +1 `IHostedService` para job diario, +servicio de almacenamiento de archivos local, +seed de roles y matriz).
- **Web** (+13 Controllers MVC, +~26 Views, +ViewComponent `NovedadesBadge`, +filtros de autorización por rol, +Helpers para cálculo de IVA y formato de correlativo, +rutas estáticas para servir comprobantes autenticados).

### 0.3 Riesgos y supuestos
Se mantienen R13, R16, R18, R20/R24, R22, R23, RD1–RD5. Nuevos riesgos técnicos:
- **RT1** Correlativo de Factura bajo concurrencia con InnoDB.
- **RT2** Migraciones extensas: separar en dos migraciones (catálogos + operativa) para reducir riesgo.
- **RT3** Query filter de soft delete puede ocultar Grupos inactivos en queries históricas (PA3); requiere `IgnoreQueryFilters()` explícito en consultas de Dashboard/Caja históricas.
- **RT4** Reutilizar `NotificationService` evita duplicar infra pero exige ampliar `Notification` si se requiere agrupamiento por día.
- **RT5** Servir comprobantes desde `App_Data` requiere endpoint autenticado (no `wwwroot`) para no exponerlos públicamente.

Supuestos técnicos: ST1 MySQL 8 soporta `SELECT ... FOR UPDATE`; ST2 EF Core 10 permite `HasSequence` sólo en SQL Server → usar tabla contador en MySQL; ST3 el `IHostedService` corre en la misma instancia (no multi-nodo en v1); ST4 `DateTime.UtcNow` para persistencia y conversión a `America/Argentina/Buenos_Aires` sólo en presentación; ST5 enums se persisten como `int` (consistente con `EstadoUsuario`).

### 0.4 Pruebas mínimas
- Heredadas: PF1–PF52, PV1–PV12, PD1–PD7.
- **Nuevas de arquitectura (PA)**:
  - PA1 Migración aplicada y revertible en entorno limpio.
  - PA2 Seed crea roles `Productor`/`SuperUsuario` y matriz de transiciones.
  - PA3 Query filter de soft delete: Grupo inactivo NO aparece en queries operativas pero SÍ en `IgnoreQueryFilters()`.
  - PA4 Concurrencia en emisión de Factura: 2 hilos obtienen correlativos distintos y consecutivos.
  - PA5 Job diario registrado como `IHostedService` y ejecutable bajo demanda en ambiente dev.
  - PA6 Endpoint de comprobantes rechaza usuarios no autenticados.

### 0.5 Checklist de salida para merge
Ver **§9**.

---

## 1. Estructura de carpetas propuesta

### 1.1 `BlankProject.Domain`
```
Entities/
  Ganaderia/
	Venta.cs
	DetalleVenta.cs
	Factura.cs
	Cuota.cs
	MovimientoCaja.cs
	Gasto.cs
	ComprobanteGasto.cs
	Rubro.cs
	Proveedor.cs
	Grupo.cs
	MovimientoStock.cs
	OrganismoIntermediario.cs
	Novedad.cs                  (si se decide tabla propia; alternativa: reutilizar Notification)
	ContadorFactura.cs          (tabla técnica para correlativo)
Enums/
  Ganaderia/
	MotivoVenta.cs
	FormaDePago.cs
	TasaImpuesto.cs
	EstadoCuota.cs
	EstadoMovimientoCaja.cs
	TipoMovimientoStock.cs
	CategoriaHacienda.cs
	AmbitoProveedor.cs
	OpcionRegularizacion.cs
Constants/
  Ganaderia/
	MatrizTransicionesCategoria.cs   (lista estática readonly)
	RolesGanaderia.cs                ("Productor", "SuperUsuario")
```

### 1.2 `BlankProject.Application`
```
Interfaces/
  Ganaderia/
	IVentaService.cs
	IFacturaService.cs
	ICuotaService.cs
	IGastoService.cs
	IMovimientoStockService.cs
	IStockQueryService.cs
	ICajaService.cs
	IDashboardService.cs
	IAcreditacionJobService.cs
	ICatalogoService.cs         (genérico)
	IUsuarioProductorService.cs
	IFileStorageService.cs      (almacenamiento local de comprobantes)
	INumeradorFacturaService.cs (correlativo)
DTOs/
  Ganaderia/
	Ventas/ (VentaListadoDto, VentaDetalleDto, LineaVentaDto, FiltroVentas)
	Facturas/ (FacturaDetalleDto, CuotaDto, FiltroFacturas)
	Stock/ (StockPorGrupoDto, StockPorCategoriaDto, MovimientoStockDto, FiltroMovimientosStock)
	Caja/ (MovimientoCajaDto, MovimientoCajaDetalleDto, FiltroCaja)
	Gastos/ (GastoListadoDto, GastoDetalleDto, FiltroGastos)
	Dashboard/ (DashboardResultadoDto)
	Novedades/ (NovedadDto, ResumenAcreditacionDto)
```

### 1.3 `BlankProject.Infrastructure`
```
Data/
  AppDbContext.cs                 (+14 DbSets)
  Configurations/Ganaderia/       (IEntityTypeConfiguration<T> por entidad)
  Migrations/                     (2 migraciones nuevas: Catalogos + Operativa)
  SeedData.cs                     (+ roles Productor/SuperUsuario)
Services/Ganaderia/
  VentaService.cs
  FacturaService.cs
  CuotaService.cs
  GastoService.cs
  MovimientoStockService.cs
  StockQueryService.cs
  CajaService.cs
  DashboardService.cs
  CatalogoService.cs              (genérico <TEntity, TDto, TViewModel>)
  UsuarioProductorService.cs
  NumeradorFacturaService.cs      (correlativo con UPDATE ... RETURNING)
  LocalFileStorageService.cs      (IFileStorageService)
  AcreditacionJobService.cs       (lógica del job)
HostedServices/
  AcreditacionDiariaHostedService.cs   (IHostedService que invoca el job 1x/día)
DependencyInjection.cs              (+registro de todos los nuevos servicios)
```

### 1.4 `BlankProject.Web`
```
Controllers/Ganaderia/
  VentasController.cs
  FacturasController.cs
  CuotasController.cs
  GastosController.cs
  StockController.cs
  MovimientosStockController.cs
  CajaController.cs
  DashboardController.cs
  GruposController.cs
  RubrosController.cs
  ProveedoresController.cs
  OrganismosController.cs
  UsuariosController.cs           (sólo SuperUsuario)
  NovedadesController.cs
  ComprobantesController.cs       (endpoint autenticado para descarga)
Models/ViewModels/Ganaderia/      (14 ViewModels del diseño §3)
ViewComponents/
  NovedadesBadgeViewComponent.cs
Views/
  Ventas/, Facturas/, Cuotas/, Gastos/, Stock/, MovimientosStock/, Caja/,
  Dashboard/, Grupos/, Rubros/, Proveedores/, Organismos/, Usuarios/, Novedades/
Helpers/Ganaderia/
  CalculoIvaHelper.cs
  FormatoCorrelativoHelper.cs
```

---

## 2. Impacto técnico por capa

### 2.1 Domain

**Entidades nuevas** (todas heredan de `SoftDestroyable`):

| Entidad | Campos clave | Notas |
|---|---|---|
| `Venta` | `Motivo`, `Fecha`, `FacturaId?` | 1↔1 con Factura |
| `DetalleVenta` | `VentaId`, `GrupoId`, `Cantidad` | |
| `Factura` | `VentaId`, `Numero` (string, unique), `OrganismoIntermediarioId`, `Categoria`, `KilosTotales`, `PrecioPorKg`, `Total`, `TasaImpuestoAplicada`, `TotalConImpuestos`, `Fecha`, `PlazoDias` | **`TasaImpuestoAplicada` y `Numero` son inmutables** |
| `Cuota` | `FacturaId`, `NumeroCuota`, `FechaVencimiento`, `Importe`, `Estado` | |
| `MovimientoCaja` | `Fecha`, `Tipo` (Ingreso/Egreso derivado), `Importe`, `Estado`, `CuotaId?`, `GastoId?`, `FormaDePago?` | FK "polimórfica" opcional |
| `Gasto` | `Fecha`, `Importe`, `RubroId`, `Concepto`, `Descripcion?`, `ProveedorId`, `FormaDePago`, `ComprobanteGastoId?` | |
| `ComprobanteGasto` | `GastoId`, `RutaRelativa`, `MimeType`, `TamañoBytes` | Archivo fuera de DB |
| `Rubro` | `Nombre`, `Activo` (en `SoftDestroyable` via `DeletedAt`) | |
| `Proveedor` | `RazonSocial`, `Cuit`, `Contacto`, `Ambito` | |
| `Grupo` | `Nombre`, `Categoria`, `StockMinimo` | Baja lógica requiere `stock == 0` (validación en Service) |
| `MovimientoStock` | `Tipo`, `GrupoOrigenId?`, `GrupoDestinoId?`, `Cantidad`, `Fecha`, `VentaId?`, `Observaciones?` | Vinculable a Venta |
| `OrganismoIntermediario` | `RazonSocial`, `Cuit`, `Contacto` | |
| `ContadorFactura` | `Id` (PK fija = 1), `UltimoNumero` | Tabla técnica de una sola fila para correlativo |
| `Novedad` | `UserId`, `Fecha`, `Titulo`, `Detalle`, `LinkOrigen`, `Leida` | **Alternativa**: reutilizar `Notification` existente (decisión §6) |

**Enums nuevos**: 9 (ver §10 análisis + `OpcionRegularizacion { ErrorDeCarga, CobroPosterior }`).

**Constante**: `MatrizTransicionesCategoria` como `IReadOnlyList<(CategoriaHacienda Origen, CategoriaHacienda Destino)>` con 3 pares iniciales.

### 2.2 Application

- **Interfaces** (12) según §4 del diseño funcional, todas con firmas `async`, devolviendo `ServiceResult`/`ServiceResult<T>` donde corresponda.
- **DTOs** separados de ViewModels: DTOs viajan entre Application ↔ Infrastructure ↔ Web (lectura); ViewModels viven sólo en Web (binding + validación).
- **Sin dependencia** a EF Core en esta capa (se respeta la convención actual del blankproject).
- Se reutiliza `ServiceResult` existente. No se crea un `Resultado` paralelo.

### 2.3 Infrastructure

**AppDbContext** — cambios:
- Agregar 14 `DbSet<>`.
- Registrar `IEntityTypeConfiguration<T>` para cada entidad (fluent API en archivos separados).
- El query filter global de soft delete **ya existe** y cubre las nuevas entidades por herencia de `SoftDestroyable`.

**Configuraciones fluent clave**:
- `Factura.Numero`: `HasMaxLength(10)`, `IsRequired()`, `HasIndex().IsUnique()`.
- `Factura.TasaImpuestoAplicada`, `TotalConImpuestos`: `HasPrecision(18,2)` donde aplique a decimals.
- Todos los enums: `HasConversion<int>()` (consistente con `EstadoUsuario`).
- `MovimientoStock.GrupoOrigenId` y `GrupoDestinoId`: FK con `OnDelete(Restrict)`.
- `MovimientoCaja.CuotaId` y `GastoId`: FK opcionales, `OnDelete(Restrict)`.
- `Cuota`: índice compuesto `(Estado, FechaVencimiento)` para el job.
- `MovimientoCaja`: índice `(Estado, Fecha)`.
- `Gasto.Concepto`: índice para autocomplete por prefijo.

**Migraciones EF propuestas** (2):
1. `20260XXX_Ganaderia_Catalogos` — Grupo, Rubro, Proveedor, OrganismoIntermediario, ContadorFactura, Novedad (si se crea), enums.
2. `20260XXX_Ganaderia_Operativa` — Venta, DetalleVenta, Factura, Cuota, Gasto, ComprobanteGasto, MovimientoStock, MovimientoCaja.

Se separan porque la primera no tiene dependencias cruzadas y permite iniciar carga de maestros; la segunda introduce todas las FK operativas.

**SeedData** — ampliación:
- Crear roles Identity `Productor` y `SuperUsuario` si no existen.
- Crear usuario SuperUsuario inicial (sólo en entorno Dev, con password rotativa).
- Insertar fila única en `ContadorFactura` con `Id=1, UltimoNumero=0`.

**Servicios clave**:

- **`NumeradorFacturaService`** (RT1/RD1):
  - Dentro de la misma transacción que `EmitirFactura`, ejecutar raw SQL:
	```sql
	UPDATE ContadorFactura SET UltimoNumero = UltimoNumero + 1 WHERE Id = 1;
	SELECT UltimoNumero FROM ContadorFactura WHERE Id = 1;
	```
	o en una sola sentencia `UPDATE ... RETURNING` (MySQL 8 soporta vía ejecución con `FromSqlRaw`/`ExecuteSqlRawAsync`). Alternativa equivalente: `SELECT ... FOR UPDATE` + `UPDATE`.
  - Formato: `F-{n:D6}` (helper `FormatoCorrelativoHelper`).
  - **Rechazo explícito** de `HasSequence` (EF Core no lo soporta para MySQL).

- **`LocalFileStorageService : IFileStorageService`**:
  - Raíz: `App_Data/comprobantes/{yyyy}/{MM}/`.
  - Guarda con nombre `{guid}{ext}` para evitar colisiones.
  - Valida extensión y tamaño nuevamente (defensa en profundidad sobre el validador del VM, RD4).
  - Expone `Task<Stream> AbrirAsync(string rutaRelativa)` y `Task EliminarAsync(string rutaRelativa)`.

- **`AcreditacionJobService`** + **`AcreditacionDiariaHostedService`**:
  - `IHostedService` con loop `Timer` diario a las 06:00 hora local (configurable en `appsettings.json`).
  - Invoca `IAcreditacionJobService.EjecutarDiariaAsync(DateTime.UtcNow)`.
  - **Idempotente (RD5/PF17)**: query `WHERE Estado == Pendiente AND FechaVencimiento <= hoy AND NOT EXISTS (MovimientoCaja Acreditado asociado)`.
  - Genera `Novedad` (o `Notification`) resumen para cada usuario Productor activo.
  - Expone también endpoint `POST /Jobs/Acreditar` **restringido a SuperUsuario** para disparo manual en dev (PA5).

### 2.4 Web

- **Controllers** delgados: validan `ModelState`, mapean VM↔DTO (`AutoMapper` si ya está en el proyecto; si no, mapeo manual), invocan Service, traducen `ServiceResult` a `ModelState`/`TempData`.
- **ViewComponent `NovedadesBadge`**: consulta `INovedadesService.ObtenerDelDiaAsync(User.Id, hoy)` y renderiza badge en el layout.
- **Filtros de autorización**:
  - A nivel Controller: `[Authorize(Roles = RolesGanaderia.Productor + "," + RolesGanaderia.SuperUsuario)]` en todos los operativos.
  - `UsuariosController`: `[Authorize(Roles = RolesGanaderia.SuperUsuario)]`.
- **`ComprobantesController`** (RT5): `GET /Comprobantes/{gastoId}` retorna `FileResult`, exige autenticación y valida que el Gasto pertenezca al scope del usuario. **Nunca** servir desde `wwwroot`.
- **Helpers**:
  - `CalculoIvaHelper.CalcularTotales(total, tasa)` → `(subtotal, iva, totalConImpuestos)`.
  - `FormatoCorrelativoHelper.FormatearNumeroFactura(int n)` → `"F-000123"`.
- **Validación cliente**: jQuery Validate + `data-val-*` generados por DataAnnotations. Upload de archivo usa validador custom para tamaño/extensión antes del POST (RD4, PD3).

---

## 3. Decisiones técnicas clave

| Decisión | Elección | Justificación |
|---|---|---|
| **Correlativo de Factura** | Tabla `ContadorFactura` con `UPDATE ... RETURNING` dentro de la transacción | EF Core + MySql.EntityFrameworkCore no soportan `HasSequence` en MySQL; `FOR UPDATE` también válido pero requiere transaction explícita. |
| **Novedades** | **Reutilizar `Notification` existente** con campo `Title="Acreditaciones del día"` agrupado; no crear `Novedad` duplicada | Reduce duplicación; `INotificationService` ya gestiona marcado de lectura. Decisión sujeta a confirmación con diseñador si se requiere modelo diferenciado. |
| **Persistencia de enums** | `HasConversion<int>()` | Consistente con `EstadoUsuario` existente; menor tamaño en MySQL. |
| **DTOs vs ViewModels** | DTOs en Application, VMs en Web | Evita que Application dependa de `DataAnnotations` de MVC. |
| **Repositorios** | `IRepository<T>` genérico por defecto; repositorio específico sólo en `IStockQueryService` por agregaciones y `INumeradorFacturaService` por SQL crudo | Respeta convención del blankproject. |
| **Transacciones** | `IDbContextTransaction` explícito en: `VentaService.Crear`, `FacturaService.Emitir`, `MovimientoStockService.Registrar`, `CuotaService.Regularizar3b` | Operaciones multi-entidad con invariantes fuertes. |
| **Job diario** | `IHostedService` con `PeriodicTimer` + validación de "última ejecución" persistida para idempotencia | Simple, single-node; si se escala a multi-nodo se reemplaza por Hangfire/Quartz. |
| **Almacenamiento de comprobantes** | `App_Data/comprobantes/{yyyy}/{MM}/{guid}.{ext}` + endpoint autenticado | Simple en v1; migrable a Azure Blob/S3 cambiando sólo la implementación de `IFileStorageService`. |
| **Soft delete en consultas históricas** | `IgnoreQueryFilters()` en Dashboard, Caja y detalles históricos (PA3) | El query filter global oculta inactivos; historia necesita verlos. |
| **Zonas horarias** | UTC en DB, conversión a `America/Argentina/Buenos_Aires` en presentación | Consistente con `CreatedAt` existente. |
| **AutoMapper** | Reutilizar si ya está presente; si no, mapeo manual por simplicidad inicial | A confirmar al revisar `.csproj` del Web (no inspeccionado aún). |

---

## 4. Cambios en entidades, servicios, controllers y vistas (delta vs blankproject actual)

### 4.1 Entidades
- **+14 nuevas** bajo `Domain/Entities/Ganaderia/` (§2.1).
- **Sin cambios** en `ApplicationUser`, `AuditLog`, `Notification` salvo verificar que el `Title/Message` sean suficientes para el resumen del job.
- Todas las nuevas entidades heredan `SoftDestroyable` → quedan auditadas y con soft delete automático por el pipeline existente.

### 4.2 Servicios
- **+12 interfaces** en `Application/Interfaces/Ganaderia/`.
- **+12 implementaciones** en `Infrastructure/Services/Ganaderia/`.
- **+1 hosted service** en `Infrastructure/HostedServices/`.
- Registrar todos en `BlankProject.Infrastructure/DependencyInjection.cs` (método existente `AddInfrastructure`).

### 4.3 Controllers
- **+14 Controllers** MVC en `Web/Controllers/Ganaderia/` (+`ComprobantesController`).
- **0 modificaciones** en Controllers existentes del blankproject base.

### 4.4 Vistas
- **+~26 Views** en `Web/Views/Ganaderia/...` (agrupadas por Controller).
- **+1 ViewComponent** `NovedadesBadge` en el layout compartido (`_Layout.cshtml`).
- **+partial views** reutilizables: `_LineaVenta.cshtml`, `_CuotaPreview.cshtml`, `_UploaderComprobante.cshtml`, `_FiltrosCaja.cshtml`.

---

## 5. Migraciones EF — estrategia

### 5.1 Migraciones propuestas

1. **`Ganaderia_Catalogos`** (bajo riesgo, sin FKs cruzadas operativas):
   - Tablas: `Grupos`, `Rubros`, `Proveedores`, `OrganismosIntermediarios`, `ContadorFactura`, `Novedades` (si se decide tabla propia).
   - Seed: fila única en `ContadorFactura(Id=1, UltimoNumero=0)`.
   - Seed: roles `Productor` y `SuperUsuario` en Identity.

2. **`Ganaderia_Operativa`** (alta complejidad):
   - Tablas: `Ventas`, `DetallesVenta`, `Facturas`, `Cuotas`, `Gastos`, `ComprobantesGasto`, `MovimientosStock`, `MovimientosCaja`.
   - Índices: `Factura.Numero` unique, `Cuota (Estado, FechaVencimiento)`, `MovimientoCaja (Estado, Fecha)`, `Gasto.Concepto`.

### 5.2 Estrategia de aplicación
- Generar en dev: `dotnet ef migrations add Ganaderia_Catalogos -p BlankProject.Infrastructure -s BlankProject.Web`.
- Aplicar en ambiente limpio y validar rollback (`dotnet ef database update <PrevMigration>`).
- **No** tocar migraciones existentes del blankproject base.

### 5.3 Rollback
- Cada migración debe generar `Down` válido (verificar en el `.cs` generado antes de commitear).
- Rollback en producción: `update` a la migración anterior; los datos de catálogo quedan huérfanos si se rollbackea catálogos con datos → documentar en release notes.

---

## 6. Impacto en permisos, estados y validaciones

### 6.1 Permisos
- **Roles nuevos**: `Productor`, `SuperUsuario` (seed).
- Límite de **5 Productores activos** validado en `UsuarioProductorService.CrearAsync` y `ActivarAsync`.
- `UsuariosController`: `[Authorize(Roles = "SuperUsuario")]`.
- Resto de controllers operativos: `[Authorize(Roles = "Productor,SuperUsuario")]`.
- `ComprobantesController`: `[Authorize]` + validación de ownership del Gasto.

### 6.2 Estados (invariantes)
| Entidad | Estados | Transiciones permitidas |
|---|---|---|
| Cuota | Pendiente, Acreditada, Rechazada | P→A (job), P→R (manual), A→R (manual), R→A (regularización 3a), R→R (3b: crea nuevo mov. pero cuota queda R) |
| MovimientoCaja | Pendiente, Acreditado | A→P (rechazo), P→A (regularización 3a) |
| Venta | — | Editable/anulable mientras no tenga Factura |
| Factura | — | Editable mientras todas las cuotas estén Pendientes |
| Grupo | Activo/Inactivo (via `DeletedAt`) | Baja lógica requiere stock==0 |

### 6.3 Validaciones transversales
- **DataAnnotations** en ViewModels (cliente + servidor).
- **Reglas de negocio** en Services (devuelven `ServiceResult.CreateError(...)` con mensaje en español).
- **Unicidad**: `Factura.Numero` por índice único + chequeo en Service.
- **Stock suficiente** atómico dentro de transacción en `VentaService` y `MovimientoStockService`.
- **Matriz de transiciones** consultada desde `MatrizTransicionesCategoria` (Domain).
- **Archivos**: extensión (PDF/JPG/PNG) + tamaño (≤5MB) validado en VM + Service.

---

## 7. Riesgos y supuestos (detallado)

### 7.1 Riesgos técnicos
| ID | Riesgo | Mitigación |
|---|---|---|
| RT1 | Correlativo de Factura duplicado por concurrencia | Transacción + `UPDATE ... RETURNING` atómico + índice único en `Factura.Numero` como red de seguridad |
| RT2 | Migración extensa falla en producción | Dividir en 2 migraciones; probar `update`/`update <prev>` en staging |
| RT3 | Query filter de soft delete oculta datos históricos | `IgnoreQueryFilters()` explícito en Dashboard/Caja/Detalle de venta antigua |
| RT4 | `Notification` existente insuficiente para agrupar novedades | Validar campos; si no alcanza, crear entidad `Novedad` (decisión diferible a implementación) |
| RT5 | Comprobantes accesibles públicamente | Servir sólo desde `ComprobantesController` autenticado; nunca publicar la carpeta `App_Data` |
| RT6 | Job corre en múltiples nodos en futuro | Documentar limitación single-node en v1; roadmap a Hangfire/Quartz si escala |
| RT7 | Regeneración de cuotas al editar Factura pierde relaciones con MovCaja | Validar precondición (todas Pendientes) antes de borrar; si alguna tiene MovCaja el Service rechaza (PF21) |
| RT8 | Timezone inconsistente entre job (UTC) y usuario (Argentina) | Config `JobOptions:HoraLocalEjecucion` y conversión explícita |

### 7.2 Supuestos
- **ST1** MySQL 8 con soporte `FOR UPDATE` y `UPDATE ... RETURNING` (MariaDB también).
- **ST2** EF Core 10 con provider **MySql.EntityFrameworkCore** (Oracle) 10.0.1 alineado a .NET 10 — verificado en `Ganaderia.Infrastructure.csproj` (2026-07-23). No se usa Pomelo (ver `Stack activo` en la operativa global del estudio).
- **ST3** Deploy single-node en v1 (un solo host).
- **ST4** UTC en DB, conversión en presentación.
- **ST5** Enums como `int` (consistente con blankproject actual).
- **ST6** `App_Data` disponible como carpeta persistente en el host (no ephemeral).
- **ST7** `NotificationService` y `EmailService` existentes no se modifican; si hace falta agrupar novedades, se extiende `Notification` con campo `Fecha` (evaluar en implementación).

---

## 8. Estrategia de pruebas

### 8.1 Unit (Application/Services)
- Mock `IRepository<T>` / `AppDbContext` (usar InMemory sólo para reglas simples; TestContainers MySQL para las que dependen de SQL crudo).
- Cubrir: cálculo de IVA, generación/regeneración de cuotas con redondeo, validación de matriz, idempotencia del job, reglas de rechazo/regularización, unicidad de `Inicial` por Grupo.
- Targets PF/PV/PD del análisis y diseño.

### 8.2 Integración (Infrastructure)
- **TestContainers MySQL** para:
  - PA1 Migraciones aplicadas.
  - PA4 Concurrencia en correlativo (2 hilos).
  - Query filter + `IgnoreQueryFilters` (PA3).
- Seed de datos mínimos: roles, 1 Productor, 1 SuperUsuario, 1 Grupo, 1 Rubro, 1 Proveedor, 1 Organismo.

### 8.3 E2E / UI (Web)
- Smoke test por pantalla: abrir, enviar formulario válido e inválido, verificar `ModelState`.
- PD1 (delegación en Controllers) verificable por revisión estática; opcional test que inyecta Service mock y verifica que el Controller no toca cálculos.
- PA5 Job disparable manualmente por endpoint protegido.
- PA6 `ComprobantesController` rechaza anónimo → 401/redirect a login.

### 8.4 Orden de ejecución recomendado
1. Domain (entidades + enums + constantes).
2. Configurations + migraciones + seed.
3. Services de catálogos (Grupo/Rubro/Proveedor/Organismo) + tests.
4. Services de stock + tests (incluye Inicial y matriz).
5. Services de venta/factura/cuotas + tests (correlativo, IVA, cuotas).
6. Services de gastos + storage de archivos.
7. Services de caja + job.
8. Dashboard.
9. Controllers + Views en el mismo orden.
10. E2E smoke.

---

## 9. Checklist de salida para merge

- [ ] 14 entidades nuevas creadas bajo `Domain/Entities/Ganaderia`, todas heredan `SoftDestroyable`.
- [ ] 9 enums nuevos en `Domain/Enums/Ganaderia`.
- [ ] `MatrizTransicionesCategoria` como constante en Domain.
- [ ] 12 interfaces en `Application/Interfaces/Ganaderia` con `ServiceResult`/`ServiceResult<T>`.
- [ ] DTOs separados de ViewModels.
- [ ] `AppDbContext` ampliado con 14 DbSets + configuraciones fluent.
- [ ] 2 migraciones EF generadas (`Catalogos`, `Operativa`), `Down` verificado, aplicación y rollback probados en entorno limpio.
- [ ] Seed de roles `Productor`/`SuperUsuario` y fila inicial en `ContadorFactura`.
- [ ] `NumeradorFacturaService` con transacción + `UPDATE ... RETURNING` + índice único de respaldo.
- [ ] `LocalFileStorageService` implementando `IFileStorageService` con validación server-side de extensión y tamaño.
- [ ] `AcreditacionJobService` + `AcreditacionDiariaHostedService` registrados en DI, idempotentes.
- [ ] Decisión de reutilizar `Notification` vs crear `Novedad` confirmada (pendiente §6).
- [ ] `ComprobantesController` autenticado sirviendo archivos desde `App_Data`.
- [ ] Controllers delegan a Services (PD1 verificable).
- [ ] Transacciones explícitas en operaciones multi-entidad identificadas (§3).
- [ ] Layout con `NovedadesBadgeViewComponent`.
- [ ] Autorización por rol aplicada (`Productor,SuperUsuario` / `SuperUsuario`).
- [ ] Cobertura de PF1–PF52, PV1–PV12, PD1–PD7, PA1–PA6.
- [ ] `IgnoreQueryFilters()` aplicado en consultas históricas (Dashboard/Caja/Detalle venta).
- [ ] `DependencyInjection.AddInfrastructure` ampliado con todos los nuevos servicios.
- [ ] Roadmap a Hangfire/Quartz documentado si se escala a multi-nodo (RT6).
- [ ] Confirmación con diseñador sobre: Notification vs Novedad (RT4); anulación de Gasto con MovCaja (§11 diseño).

---

## 10. Preguntas abiertas devueltas al diseñador

1. **Novedades**: ¿reutilizamos `Notification` + `INotificationService` existentes (opción simple, reduce código) o creamos entidad dedicada `Novedad` con semántica "bandeja diaria" (más clara funcionalmente)? Recomendación técnica: **reutilizar** y ampliar `Notification` si es necesario.
2. **Anulación de Gasto** con MovimientoCaja ya acreditado: el diseño lo deja "a confirmar". Opciones:
   - a) No permitir anular; forzar a registrar un Gasto inverso manual.
   - b) Permitir anulación que revierta el MovCaja (genera un contra-movimiento o lo marca anulado).
   - Recomendación técnica: **opción (a)** por consistencia con el tratamiento de Cuota (también sin contramovimiento).
3. **AutoMapper**: ¿está en uso en el blankproject o usamos mapeo manual? Si no está, propongo mapeo manual en la primera iteración y evaluar AutoMapper después.

---

## 11. Handoff al desarrollador

Con este documento, el desarrollador puede arrancar por:

1. **Sprint 1**: Domain (entidades + enums + matriz) + Configurations + migración `Ganaderia_Catalogos` + SeedData (roles + contador).
2. **Sprint 2**: `CatalogoService` genérico + `UsuarioProductorService` + controllers/views de ABMs (Grupo, Rubro, Proveedor, Organismo, Usuario).
3. **Sprint 3**: `MovimientoStockService` + `StockQueryService` + controllers/views + tests (incluye `Inicial`, matriz, baja de grupo).
4. **Sprint 4**: `VentaService` + `FacturaService` + `CuotaService` + `NumeradorFacturaService` + controllers/views + migración `Ganaderia_Operativa`.
5. **Sprint 5**: `GastoService` + `LocalFileStorageService` + `ComprobantesController` + autocomplete.
6. **Sprint 6**: `CajaService` + `AcreditacionJobService` + `AcreditacionDiariaHostedService` + `NovedadesBadgeViewComponent`.
7. **Sprint 7**: `DashboardService` + vista + filtros.
8. **Sprint 8**: QA funcional contra PF/PV/PD/PA + ajustes.

---

## 13. Arquitectura v2 — Pagos múltiples de Egreso (`ganaderia - emo`)

Grounded directamente en el código real: `Egreso.cs`, `EgresoService.cs`, `MovimientoCaja.cs`, `FacturaVentaCuota.cs`/`CuotaService.cs` (patrón de referencia), `AppDbContext.cs`, `AcreditacionCuotasHostedService.cs`.

### 13.1 Domain — cambios

**`Egreso.cs`** — se quita el campo `FormaDePago`; se agrega navegación:
```csharp
public class Egreso : SoftDestroyable
{
    public DateOnly Fecha { get; set; }
    public int RubroId { get; set; }
    public Rubro? Rubro { get; set; }
    public int ProveedorId { get; set; }
    public Proveedor? Proveedor { get; set; }
    public string Detalle { get; set; } = string.Empty;
    public decimal Importe { get; set; }
    public ComprobanteEgreso? Comprobante { get; set; }

    public ICollection<EgresoPago> Pagos { get; set; } = new List<EgresoPago>();
}
```

**`EgresoPago.cs`** (nueva entidad, calcada de `FacturaVentaCuota` + campos propios de cheque):
```csharp
public class EgresoPago : SoftDestroyable
{
    public int EgresoId { get; set; }
    public Egreso? Egreso { get; set; }

    public FormaDePago FormaDePago { get; set; }
    public decimal Importe { get; set; }
    public DateOnly FechaEfectiva { get; set; }
    public DateOnly? FechaVencimiento { get; set; } // obligatoria solo si FormaDePago == Cheque
    public EstadoPagoEgreso Estado { get; set; } = EstadoPagoEgreso.Pendiente;

    public DateOnly? FechaRechazo { get; set; }
    public string? MotivoRechazo { get; set; }
    public OpcionRegularizacion? OpcionRegularizacion { get; set; }
    public DateOnly? FechaRegularizacion { get; set; }

    // Trazabilidad al movimiento de caja generado al acreditar (mismo patron que FacturaVentaCuota.MovimientoCajaIngresoId).
    public int? MovimientoCajaEgresoId { get; set; }
}
```

**`EstadoPagoEgreso.cs`** (enum nuevo):
```csharp
public enum EstadoPagoEgreso { Pendiente = 1, Acreditado = 2, Rechazado = 3 }
```

`OpcionRegularizacion` y `FormaDePago` se **reutilizan** tal cual existen hoy (ya usados por `FacturaVentaCuota`).

**`MovimientoCaja.cs`** — reemplaza la FK directa a `Egreso` por FK al pago:
```csharp
// antes: public int? EgresoId { get; set; }  public Egreso? Egreso { get; set; }
public int? EgresoPagoId { get; set; }
public EgresoPago? EgresoPago { get; set; }
```

### 13.2 Application — cambios

**`ICajaEgresoServices.cs`**:
```csharp
public record EgresoPagoInput(FormaDePago FormaDePago, decimal Importe, DateOnly FechaEfectiva, DateOnly? FechaVencimiento);

public record EgresoCreateInput(
    DateOnly Fecha, int RubroId, int ProveedorId, string Detalle, decimal Importe,
    List<EgresoPagoInput> Pagos);   // reemplaza el parametro FormaDePago suelto

public interface IEgresoService
{
    Task<List<Egreso>> ListAsync(DateOnly? desde = null, DateOnly? hasta = null);
    Task<Egreso?> GetAsync(int id);
    Task<ServiceResult<Egreso>> CreateAsync(EgresoCreateInput input, Stream? comprobante, string? nombreArchivo, string? contentType);
    Task<ServiceResult> AnularAsync(int egresoId);
    Task<List<string>> SugerenciasDetalleAsync(string? term, int top = 10);
}

public interface IEgresoPagoService   // nuevo, calcado de ICuotaService
{
    Task<ServiceResult> RechazarAsync(int egresoPagoId, DateOnly fechaRechazo, string motivo);
    Task<ServiceResult> RegularizarAsync(int egresoPagoId, OpcionRegularizacion opcion, DateOnly fechaRegularizacion, FormaDePago? formaPagoReal = null);
    Task<int> AcreditarChequesVencidosAsync(DateOnly hoy);   // invocado por el job diario
}
```

### 13.3 Infrastructure — cambios

**`EgresoService.CreateAsync`** — validaciones nuevas antes de abrir transacción:
- `input.Pagos.Count >= 1` (PV15).
- Cada `Importe > 0`.
- Cheque ⇒ `FechaVencimiento.HasValue && FechaVencimiento >= FechaEfectiva` (PV13/PV14).
- `Math.Round(input.Pagos.Sum(p => p.Importe), 2) == Math.Round(input.Importe, 2)` (PF56, RD6).

Dentro de la transacción: persiste `Egreso`, agrega un `EgresoPago` por cada línea; para `Efectivo`/`Transferencia` marca `Estado = Acreditado` y agrega su `MovimientoCaja` (igual que hoy, `Estado = Acreditado`, `EgresoPagoId` en vez de `EgresoId`); para `Cheque` deja `Estado = Pendiente` **sin** crear `MovimientoCaja` (PF53/PF54/PF55).

**`EgresoService.AnularAsync`** — extiende el soft-delete: además del `Egreso`, itera `_db.EgresoPagos.Where(p => p.EgresoId == egresoId)` y `_db.MovimientosCaja.Where(m => m.EgresoPago!.EgresoId == egresoId)`, marcando `DeletedAt` en todos (análisis v11 §4.6).

**`EgresoPagoService.cs`** (nueva, implementación calcada 1:1 del patrón de `CuotaService.cs`):
- `RechazarAsync`: sólo desde `Pendiente`/`Acreditado`, sólo `FormaDePago == Cheque` (PV16); si tenía `MovimientoCajaEgresoId`, ese movimiento → `Pendiente` (`IgnoreQueryFilters()` + `DeletedAt = null`, mismo patrón que `CuotaService.RechazarAsync`).
- `RegularizarAsync`: sólo desde `Rechazado`; 3a (`ErrorDeCarga`) restaura el movimiento original a `Acreditado`; 3b (`CobroPosterior`) crea un `MovimientoCaja` nuevo `Acreditado` con fecha/forma reales, movimiento original queda `Pendiente`.
- `AcreditarChequesVencidosAsync(hoy)`: `WHERE FormaDePago == Cheque AND Estado == Pendiente AND FechaVencimiento <= hoy`, crea `MovimientoCaja` (`EsIngreso = false`, `Estado = Acreditado`, `Fecha = FechaVencimiento`, `EgresoPagoId`), setea `EgresoPago.Estado = Acreditado`, `MovimientoCajaEgresoId`. Misma idempotencia que `CuotaService.AcreditarCuotasVencidasAsync` (query re-ejecutable sin duplicar: sólo toma pagos aún `Pendiente`).

**`AcreditacionCuotasHostedService.cs`** — se extiende `EjecutarSiCorrespondeAsync` (no se crea un segundo `IHostedService`): después de `cuotaSvc.AcreditarCuotasVencidasAsync(hoyArt)`, agrega:
```csharp
var egresoPagoSvc = scope.ServiceProvider.GetRequiredService<IEgresoPagoService>();
var chequesProcesados = await egresoPagoSvc.AcreditarChequesVencidosAsync(hoyArt);
```
`JobEjecucion` gana columna `ChequesEgresoProcesados` (int) para el mismo registro diario; `registro.Detalle` incluye ambos totales; `NotificarAdministradoresAsync` recibe el total combinado para la notificación in-app consolidada (mismo mensaje, no dos notificaciones separadas).

**`AppDbContext.cs`** — fluent config nueva:
```csharp
modelBuilder.Entity<EgresoPago>(e =>
{
    e.Property(p => p.FormaDePago).HasConversion<int>();
    e.Property(p => p.Estado).HasConversion<int>();
    e.Property(p => p.OpcionRegularizacion).HasConversion<int>();
    e.Property(p => p.Importe).HasPrecision(18, 2);
    e.Property(p => p.MotivoRechazo).HasMaxLength(500);
    e.HasOne(p => p.Egreso).WithMany(g => g.Pagos).HasForeignKey(p => p.EgresoId).OnDelete(DeleteBehavior.Restrict);
    e.HasIndex(p => new { p.Estado, p.FormaDePago, p.FechaVencimiento }); // para el job (igual patron que FacturaVentaCuota)
});
```
En `ConfigureGanaderia`, el bloque `MovimientoCaja` reemplaza `e.HasOne(p => p.Egreso)...HasForeignKey(p => p.EgresoId)` por `e.HasOne(p => p.EgresoPago).WithMany().HasForeignKey(p => p.EgresoPagoId).OnDelete(DeleteBehavior.Restrict).IsRequired(false)`. El bloque `Egreso` pierde `e.Property(p => p.FormaDePago).HasConversion<int>()`.

### 13.4 Migración EF — **con datos existentes (riesgo crítico)**

`ganaderia - emo` está **en producción** con `Egreso` ya cargados (1 `FormaDePago` + 1 `MovimientoCaja` vía `EgresoId` cada uno). La migración debe preservar esa historia. Se propone **una migración con `Up()` en 3 fases** (schema → backfill de datos → drop de columnas viejas):

1. **Fase A (schema aditivo)**: crear tabla `EgresoPagos` (sin FK todavía desde `MovimientoCaja`); agregar columna nullable `MovimientosCaja.EgresoPagoId`; agregar `JobEjecuciones.ChequesEgresoProcesados` (nullable/default 0).
2. **Fase B (backfill, SQL dentro de la misma migración vía `migrationBuilder.Sql(...)`)**:
   ```sql
   INSERT INTO EgresoPagos (EgresoId, FormaDePago, Importe, FechaEfectiva, FechaVencimiento, Estado,
                             MovimientoCajaEgresoId, CreatedAt, CreatedByUserId)
   SELECT Id, FormaDePago, Importe, Fecha, NULL, 2 /*Acreditado*/,
          (SELECT Id FROM MovimientosCaja mc WHERE mc.EgresoId = Egresos.Id LIMIT 1),
          CreatedAt, CreatedByUserId
   FROM Egresos;

   UPDATE MovimientosCaja mc
   JOIN EgresoPagos ep ON ep.MovimientoCajaEgresoId = mc.Id
   SET mc.EgresoPagoId = ep.Id;
   ```
   Los `Egreso` con `DeletedAt` no nulo (anulados) también migran su pago (queda igualmente de baja lógica, mismo `DeletedAt`); si el `Egreso` anulado no tenía `MovimientoCaja` vigente, `MovimientoCajaEgresoId` queda `NULL`.
3. **Fase C (schema destructivo)**: `DROP COLUMN Egresos.FormaDePago`; `DROP COLUMN MovimientosCaja.EgresoId` (+ su FK); agregar FK real `MovimientosCaja.EgresoPagoId → EgresoPagos.Id`.

**RT9 (nuevo, crítico)** — la Fase C es irreversible sin backup: si el backfill de Fase B falla silenciosamente (0 filas por mismatch de tipos/FK), se pierde la trazabilidad de pagos históricos al dropear las columnas. **Mitigación obligatoria**: correr la migración completa primero contra una copia de la base de producción (o snapshot), validar `COUNT(EgresoPagos) == COUNT(Egresos)` y `COUNT(MovimientosCaja WHERE EgresoPagoId IS NOT NULL) == COUNT(MovimientosCaja WHERE EgresoId IS NOT NULL era antes)` **antes** de aplicar en producción. Tomar backup de `Egresos` y `MovimientosCaja` inmediatamente antes del deploy.

### 13.5 Riesgos técnicos v2

| ID | Riesgo | Mitigación |
|---|---|---|
| RT9 | Pérdida de trazabilidad histórica de pagos al migrar datos de producción (§13.4) | Backfill validado contra copia de producción + backup previo al deploy; smoke test post-migración que compara conteos |
| RT10 | `EgresoPagoService` diverge del comportamiento ya probado de `CuotaService` si se reimplementa desde cero | Copiar el patrón línea por línea (transacción, `IgnoreQueryFilters()`, mutación sin contramovimiento) en vez de rediseñar |
| RT11 | Job diario extendido: si `AcreditarChequesVencidosAsync` lanza excepción, no debe impedir que `AcreditarCuotasVencidasAsync` ya corrido quede confirmado (evitar rollback cruzado entre ambas colecciones) | Cada `AcreditarXVencidosAsync` abre su propia transacción por ítem (ya es el patrón actual de `CuotaService`); no envolver ambas llamadas en una transacción común |
| RT12 | Grilla dinámica de pagos en `Egresos/Create` sin JS robusto puede romper el binding de `List<EgresoPagoViewModel>` en POST | Usar índices secuenciales `Pagos[0].Importe`, `Pagos[1].Importe`... regenerados al agregar/quitar filas (patrón estándar MVC), cubrir con smoke test manual antes de QA |

### 13.6 Checklist adicional v2

- [ ] `EgresoPago` creada, hereda `SoftDestroyable`, configurada en `AppDbContext` con índice `(Estado, FormaDePago, FechaVencimiento)`.
- [ ] `MovimientoCaja.EgresoId` reemplazado por `EgresoPagoId` (FK + navegación).
- [ ] Migración con backfill de datos ejecutada y validada contra copia de producción (RT9) **antes** de aplicar en el ambiente real.
- [ ] `IEgresoPagoService`/`EgresoPagoService` implementados calcando el patrón de `ICuotaService`/`CuotaService`.
- [ ] `EgresoService.CreateAsync` valida suma exacta de pagos + reglas de cheque (servidor, autoridad).
- [ ] `EgresoService.AnularAsync` propaga baja lógica a `EgresoPago` y `MovimientoCaja` asociados.
- [ ] `AcreditacionCuotasHostedService` extendido para procesar `EgresoPago` sin crear un segundo `IHostedService`.
- [ ] `EgresosController.Create` con grilla dinámica de pagos (binding `List<EgresoPagoViewModel>`); `EgresoPagosController` con `Rechazar`/`Regularizar`.
- [ ] Backup de `Egresos`/`MovimientosCaja` tomado inmediatamente antes del deploy a producción.

---

## 15. Arquitectura v3 — Autocomplete Select2 (Concepto de Egreso, Motivo de Factura de venta)

Grounded en código real: `EgresosController.SugerenciasDetalle` (ya existente, patrón a replicar), `IFacturaVentaService`/`FacturaVentaService`/`FacturasController`, `FacturaVentaCreateVm`, `FacturaVenta.cs`, `AppDbContext.ConfigureGanaderia` (bloque `FacturaVenta`).

### 15.1 Domain
`FacturaVenta.cs`:
```csharp
// antes: public MotivoVenta Motivo { get; set; }
public string Motivo { get; set; } = string.Empty;
```
Se **elimina** `Enums/Ganaderia/MotivoVenta.cs` (sin más referencias tras el cambio; verificado que no participa en ninguna lógica de negocio, sólo en persistencia y visualización — análisis v12 S37).

### 15.2 Application
`IFacturaVentaService.cs`:
- `FacturaVentaCreateInput.Motivo` cambia de `MotivoVenta` a `string`.
- Nuevo método: `Task<List<string>> SugerenciasMotivoAsync(string? term, int top = 10);` — misma firma que `IEgresoService.SugerenciasDetalleAsync`.

### 15.3 Infrastructure
**`FacturaVentaService.SugerenciasMotivoAsync`** — calcado 1:1 de `EgresoService.SugerenciasDetalleAsync` (mismo patrón: `Where(!string.IsNullOrEmpty)`, filtro `EF.Functions.Like` si hay término, `GroupBy` + `OrderByDescending(Max(Id))` + `Take(top)`), pero sobre `_db.FacturasVenta` y la propiedad `Motivo`.

**`AppDbContext.cs`** — en el bloque `modelBuilder.Entity<FacturaVenta>(e => { ... })`:
```csharp
// antes: e.Property(p => p.Motivo).HasConversion<int>();
e.Property(p => p.Motivo).HasMaxLength(200).IsRequired();
```

**Migración EF** (una sola, sin las 3 fases de v2 porque no hay reestructuración relacional, sólo cambio de tipo de columna + backfill de valores):
```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    // Fase A: columna nueva nullable
    migrationBuilder.AddColumn<string>(name: "MotivoTexto", table: "FacturasVenta", type: "varchar(200)", maxLength: 200, nullable: true);

    // Fase B: backfill — mapea los 3 valores historicos del enum (1/2/3) a su texto equivalente.
    migrationBuilder.Sql(@"
        UPDATE FacturasVenta SET MotivoTexto = CASE Motivo
            WHEN 1 THEN 'Faena'
            WHEN 2 THEN 'Vacía'
            WHEN 3 THEN 'Enfermedad'
            ELSE 'Faena' /* red de seguridad; no deberia ocurrir, Motivo es NOT NULL con esos 3 valores */
        END;
    ");

    // Fase C: dropear columna vieja, renombrar la nueva, marcar NOT NULL.
    migrationBuilder.DropColumn(name: "Motivo", table: "FacturasVenta");
    migrationBuilder.RenameColumn(name: "MotivoTexto", table: "FacturasVenta", newName: "Motivo");
    migrationBuilder.AlterColumn<string>(name: "Motivo", table: "FacturasVenta", type: "varchar(200)", maxLength: 200, nullable: false);
}
```
`Down()`: recrea la columna `int` e intenta mapear de vuelta por texto exacto (`'Faena'→1`, `'Vacía'→2`, `'Enfermedad'→3`, cualquier otro valor libre cargado después de v3 no tiene representación en el enum viejo y se mapea a `1` con nota en release notes — mismo criterio que el `Down()` de la migración v2, rollback de datos operativos nuevos no es lossless).

**RT13 (nuevo, v3)** — riesgo bajo (a diferencia de RT9): esta migración no reestructura relaciones ni puede perder trazabilidad histórica (los 3 valores mapean 1:1, sin ambigüedad). Igual se recomienda correrla primero contra una copia de desarrollo/staging antes de producción, como buena práctica general, pero no requiere el nivel de validación obligatoria de RT9.

### 15.4 Web
- `FacturaVentaCreateVm.Motivo`: `MotivoVenta` → `string`, `[Required, StringLength(200)]`.
- `FacturasController`: agregar acción `SugerenciasMotivo(string? term, int top = 10)` — calcada de `EgresosController.SugerenciasDetalle`.
- `Facturas/Create.cshtml`: reemplazar `<select asp-for="Motivo" asp-items="Html.GetEnumSelectList<MotivoVenta>()">` por `<input asp-for="Motivo" type="hidden" class="js-select2-motivo" />` (o `<select>` vacío) + inicialización Select2 (diseño §8.1).
- `Egresos/Create.cshtml`: reemplazar el `<input list="DetalleSugerencias"> + <datalist>` y su JS de `fetch` manual (agregado en el bugfix post-v11) por el mismo patrón Select2, apuntando a `Egresos/SugerenciasDetalle` (endpoint sin cambios).
- Script Select2 reutilizable: se propone un único archivo `wwwroot/js/ov-autocomplete-select2.js` con una función `initAutocompleteSelect2(selector, url)` invocada desde ambas vistas, para no duplicar el snippet del diseño §8.1 en 2 archivos `.cshtml`.

### 15.5 Checklist adicional v3
- [ ] `MotivoVenta` enum eliminado del Domain, sin referencias colgantes.
- [ ] `FacturaVenta.Motivo` es `string(200)` NOT NULL en DB, con backfill validado (los 3 valores históricos migran correctamente).
- [ ] `IFacturaVentaService.SugerenciasMotivoAsync` implementado, calcado de `SugerenciasDetalleAsync`.
- [ ] `FacturasController.SugerenciasMotivo` acción nueva, misma forma de contrato JSON que `Egresos/SugerenciasDetalle`.
- [ ] Select2 inicializado en `Egresos/Create` y `Facturas/Create` vía función JS reutilizable (`ov-autocomplete-select2.js`), sin código muerto del `<datalist>`/fetch manual anterior.
- [ ] Build 0 errores; smoke test de navegador real (Playwright o similar) del autocomplete en ambas pantallas antes de cerrar QA — lección explícita del bugfix post-v11 (`6-qa.md` §12.4).

---

## 17. Arquitectura v4 — Descuento comercial pre-impuestos + serie de IVA en el Tablero Anual

Sobre el diseño funcional **v4** (§8.3 de `2-disenador-funcional.md`) y el análisis **v13**. Grounded en el código real de `ganaderia - emo` al 2026-09-06 (post v16), no en el plan original.

### Escaneo de reutilización cross-proyecto (tarea 0)

| Componente buscado | Dónde | Decisión |
|---|---|---|
| Modelo de impuestos **por comprobante** (`Subtotal` / `MontoIva` / `MontoIIBB` / `Total`) | `marihogar` (`3-arquitecto-mvc.md` §332, `5-implementador.md` §657 CR-1) | **Mismo modelo, mismo criterio** (`Total` autoritativo, no se recalcula al leer). **Corrección de atribución (v4.1):** el préstamo va al revés de lo que decía la primera redacción de esta tabla — marihogar §657 dice explícitamente que su bloque de impuestos es *"patrón copiado del bloque de impuestos de `FacturaVenta.cs` de `ganaderia - emo`"*. El criterio se confirma, pero **ganaderia es el proyecto de origen**, no el receptor. Corolario: marihogar tiene hoy el mismo modelo de 4 campos por comprobante y es **candidato natural a recibir este mismo descuento** si el cliente lo pide. |
| Descuento como columna | `la-platense/3-arquitecto-mvc.md` (`ItemVenta.descuento/recargo`, `Proveedor.porcentajeDescuento`) | **No aplica**: es descuento por línea y por proveedor. Acá es global por comprobante (P3:A). |
| Migración de datos financieros en producción | `vinosefue/3-arquitecto-mvc.md` §74 (script SQL idempotente + backup obligatorio) | **Riesgo mucho menor acá**: no se muta ningún dato existente, sólo se agregan dos columnas `NOT NULL DEFAULT 0`. No requiere el protocolo de backfill de v2 (RT9). |
| Gráfico de posición de IVA | — | **No existe en ningún proyecto del historial.** Componente nuevo, pero construido como clon del `chartMensual` propio. |

**Conclusión:** no se importa código externo. El criterio de "total autoritativo" ya es de este proyecto (marihogar lo tomó de acá), y se apoya todo en la infraestructura ya probada de este mismo repositorio.

### 17.1 Domain

`FacturaVenta` y `Egreso` suman **dos columnas cada uno**, con la convención de precisión ya vigente en `AppDbContext` (porcentajes `HasPrecision(9,4)`, montos `HasPrecision(18,2)` — **corrige el `18,4` que había estimado el diseño**, que no era la convención del proyecto):

```csharp
/// <summary>Descuento comercial opcional. % e importe editables (la autoridad es el importe).</summary>
public decimal PorcentajeDescuento { get; set; }   // HasPrecision(9, 4)
public decimal MontoDescuento { get; set; }        // HasPrecision(18, 2)

/// <summary>Base imponible real: Subtotal - MontoDescuento. No se persiste.</summary>
public decimal NetoGravado => Subtotal - MontoDescuento;
```

`NetoGravado` es propiedad calculada y **debe ignorarse explícitamente** en la configuración (`e.Ignore(p => p.NetoGravado)` en ambos `modelBuilder.Entity<>`), o EF Core intenta mapearla como columna. Se agrega igual (en vez de repetir la resta en cada vista/PDF) porque es la fórmula que RD12 quiere en un solo lugar.

Semántica que se preserva sin cambios:
- `FacturaVenta.Total` sigue siendo **el total persistido y autoritativo**, ahora `NetoGravado + MontoIva + MontoIIBB + MontoOtrasPercepciones`.
- `Egreso.Importe` sigue siendo **el TOTAL** (nombre histórico, ver v15), ahora `NetoGravado + MontoIva`.
- Anulación = soft delete (`SoftDestroyable` + filtro global): las series de IVA no necesitan filtrar anulados a mano, el query filter ya los excluye. **No usar `IgnoreQueryFilters()` en las consultas nuevas** — es el modo exacto de romper PF75.

### 17.2 Application

- `FacturaVentaCreateInput` y `EgresoCreateInput` (records posicionales) += `PorcentajeDescuento`, `MontoDescuento`. Al ser posicionales, el compilador marca todos los call sites: son **los controllers únicamente** (alta y edición), lo cual es la garantía barata de que no queda ninguno sin actualizar.
- `TableroAnualMesDto` += `IvaVentas`, `IvaCompras`, y `SaldoIva => IvaVentas - IvaCompras` (mismo patrón que el `Neto` que ya tiene).
- `TableroAnualKpisDto` += `SaldoIvaPeriodo`.
- **Ninguna interfaz cambia de firma.**

### 17.3 Infrastructure

**`FacturaVentaService`** — dos puntos de cambio, ya localizados en el código actual:

- Líneas 61 y 150 (`CreateAsync` y `EditAsync`) calculan hoy `total = Math.Round(subtotal + MontoIva + MontoIIBB + MontoOtrasPercepciones, 2)`. Pasan a `total = Math.Round(subtotal - input.MontoDescuento + ..., 2)`. **El total ya se calcula en servidor** (el cliente nunca lo postea), así que el descuento entra por la puerta correcta sin cambiar el contrato de confianza.
- El validador de tuplas `(nombre, pct, monto)` (~línea 382) suma la entrada `("Descuento", input.PorcentajeDescuento, input.MontoDescuento)` y agrega la única regla propia: `MontoDescuento < subtotal` (PV20) y `PorcentajeDescuento < 100` (PV19).
- `ValidarIngresos` (~línea 404) **no cambia**: sigue comparando contra `total`, que ahora ya viene descontado. La tolerancia de $0,01 por ingreso se mantiene.

**`EgresoService`** — `importe = Math.Round(subtotal - montoDescuento + montoIva, 2)`; la validación de pagos sigue contra `importe` con **tolerancia cero** (divergencia deliberada respecto de facturas, ya documentada en v15).

**`DashboardService.GetTableroAnualAsync`** — dos consultas nuevas, independientes de `MovimientosCaja` (PD16):

```csharp
var ivaVentas = await _db.FacturasVenta
    .Where(f => f.Fecha >= inicioAnio && f.Fecha <= finAnio)
    .Select(f => new { f.Fecha, f.MontoIva }).ToListAsync();
var ivaCompras = await _db.Egresos
    .Where(e => e.Fecha >= inicioAnio && e.Fecha <= finAnio)
    .Select(e => new { e.Fecha, e.MontoIva }).ToListAsync();
```

Se agrupan en memoria por `Fecha.Month` dentro del `Enumerable.Range(1,12)` que ya arma `meses` — mismo patrón que `movsAnio`, y evita `GROUP BY MONTH()` traducido por el proveedor Oracle de MySQL. Volumen esperado: cientos de filas por año, no justifica optimizar. El KPI `SaldoIvaPeriodo` se calcula sobre el período filtrado (año, o mes si está seleccionado), consistente con `TotalIngresos`/`TotalEgresos`.

### 17.4 Web

- `FacturaVentaCreateVm` y `EgresoCreateVm` += los dos campos con `[Range]`; `FacturaVentaCreateVm` += `bool EsEdicion` (RD13 — `Facturas` no tiene `Edit.cshtml`, la edición reusa `Create.cshtml`).
- `Facturas/Create.cshtml`: card renombrada, fila de descuento, línea "Neto gravado", `impGrupos` con `'desc'` al frente, `base()` reescrita, botón "Sin descuento", bloque de reajuste condicionado a `EsEdicion`. **LP-003**: los `value=` de los dos campos nuevos van por el `Func<decimal,string> num` invariante que ya existe en la vista.
- `Egresos/Create.cshtml`: misma card reducida; el hidden `#ImporteTotal` (sin `name`, no postea) refleja el nuevo total.
- `Facturas/Details.cshtml` y `Egresos/Details.cshtml`: muestran la fila de descuento **sólo si `MontoDescuento > 0`**, y leen `Total`/`Importe` persistidos (RD12). **Corrección (v4.1):** la primera redacción listaba también "el PDF del comprobante" entre los consumidores a adaptar — **ese PDF no existe**: el comprobante es un archivo que el usuario *sube* (`ComprobanteFacturaVenta`/`ComprobanteEgreso`), y `ExportService` es genérico del template. Los únicos consumidores reales son ambos `Index` (sumatorias) y ambos `Details`, que ya leían los totales persistidos.
- `Dashboard/TableroAnual.cshtml`: card `chartIva` clonada de `chartMensual`, KPI de saldo, tabla de desglose y el rótulo de base contable.

### 17.5 Migración EF

**Una sola migración**, `Comprobantes_DescuentoComercial`, escrita a mano (EF scaffolding en este proyecto ya generó operaciones destructivas tres veces — ver v13/v14/v15):

```sql
ALTER TABLE FacturasVenta
  ADD COLUMN PorcentajeDescuento decimal(9,4)  NOT NULL DEFAULT 0,
  ADD COLUMN MontoDescuento      decimal(18,2) NOT NULL DEFAULT 0;
ALTER TABLE Egresos
  ADD COLUMN PorcentajeDescuento decimal(9,4)  NOT NULL DEFAULT 0,
  ADD COLUMN MontoDescuento      decimal(18,2) NOT NULL DEFAULT 0;
```

Sin backfill: `DEFAULT 0` deja el histórico con la semántica correcta (sin descuento) y `Total`/`Importe` siguen cuadrando exactamente contra sus componentes (PF70, RD15). `Down` = `DropColumn` ×4, sin pérdida de datos previos a v4. **No requiere** el protocolo de 3 fases de RT9 ni el script idempotente de vinosefue: no toca una sola fila existente.

### 17.6 Riesgos técnicos v4

- **RT17** `NetoGravado` es propiedad calculada: si falta el `Ignore` en `AppDbContext`, EF Core la toma como columna y la migración scaffoldeada intenta crearla. Verificar el snapshot generado antes de aplicar.
- **RT18** El descuento cambia la base de tres impuestos a la vez. Todo consumidor que recomponga totales fuera del servicio (`Details`, sumatorias de listados, tablero) debe leer `Total`/`Importe` persistidos. Criterio propio del proyecto, heredado después por `marihogar`.
- **RT19** `MontoDescuento` es la autoridad y `PorcentajeDescuento` es derivado: si la UI manda un % que no cuadra con el importe (POST fuera del formulario), el servidor usa el **importe** y no intenta reconciliar. Documentarlo en el resumen XML de la entidad para que no se "arregle" después.
- **RT20** La serie de IVA no debe usar `IgnoreQueryFilters()`: el filtro global de soft delete es lo que implementa "excluye anulados" (PF75). Es un error de una sola palabra con consecuencia silenciosa.
- **RT21** Los records de input son posicionales: agregar parámetros al medio rompe cualquier construcción por posición. Agregar los dos campos **inmediatamente después de `Subtotal`/antes de los impuestos** y verificar que compile en los cuatro call sites (alta y edición × factura y egreso).

### 17.7 Estrategia de pruebas

- **Unit / servicio**: PF67–PF71 (aritmética de descuento en venta y egreso), PV19–PV23 (validaciones en servidor, incluido POST directo que saltea la UI).
- **Integración / datos**: tras la migración, verificar `SELECT COUNT(*) FROM FacturasVenta WHERE ROUND(Subtotal - MontoDescuento + MontoIva + MontoIIBB + MontoOtrasPercepciones, 2) <> ROUND(Total, 2)` = 0, y su equivalente en `Egresos` — mismo chequeo de invariante que ya se corre desde v15.
- **UI**: PF72 (aviso + reajuste), PF73–PF76 (series del gráfico, devengado, anulados, saldo), PF77 (desglose en detalles), PD13–PD17.

### 17.8 Checklist adicional v4

- [ ] `Ignore(NetoGravado)` presente en ambas entidades y verificado contra el snapshot de la migración (RT17).
- [ ] Migración escrita a mano y revisada: 4 `AddColumn` con `defaultValue: 0m`, ningún `RenameColumn`, ningún `DropTable`.
- [ ] Invariante `Subtotal - Descuento + impuestos = Total` en 0 desvíos, en dev y en producción post-deploy.
- [ ] Series de IVA sin `IgnoreQueryFilters()` (RT20).
- [ ] Rótulo de base devengado y "no es un Libro IVA" visible en la card, no en tooltip.
- [ ] Botón de reajuste ausente en el alta (RD13/PD15).
- [ ] `value=` de descuento con `CultureInfo.InvariantCulture` (LP-003).

---

## 18. Arquitectura v5 — Deducciones de liquidación + compra de hacienda con costo

Sobre el diseño **v5** (§8.4) y el análisis **v14**. Grounded en el código real post-v17.1.

### Escaneo de reutilización

`MovimientoStock.FacturaVentaId` ya resuelve el vínculo movimiento↔comprobante en este mismo proyecto: `EgresoId` se agrega con idéntico criterio (FK nullable, sin navegación inversa obligatoria). El catálogo `ConceptoDeduccion` se calca de `Rubro` (`SoftDestroyable` + ABM simple). No hay componente equivalente en otros proyectos del historial: `marihogar` y `la-platense` cargan sus impuestos a mano, ninguno precarga desde catálogo.

### 18.1 Domain

**Nueva entidad `ConceptoDeduccion : SoftDestroyable`**

```csharp
public string Nombre { get; set; } = string.Empty;   // 100, único entre activos
public bool EsImporteFijo { get; set; }              // false = porcentual
public decimal Porcentaje { get; set; }              // HasPrecision(9, 4)
public decimal ImporteFijo { get; set; }             // HasPrecision(18, 2)
public bool AplicaPorDefecto { get; set; }
public int Orden { get; set; }
```

**Nueva entidad `FacturaVentaDeduccion : SoftDestroyable`**

```csharp
public int FacturaVentaId { get; set; }
public int? ConceptoDeduccionId { get; set; }   // referencia blanda; puede quedar huérfana
public string Nombre { get; set; } = string.Empty;  // SNAPSHOT (RD17)
public bool EsImporteFijo { get; set; }
public decimal Porcentaje { get; set; }         // HasPrecision(9, 4)
public decimal Monto { get; set; }              // HasPrecision(18, 2)
```

**`FacturaVenta`**: se **eliminan** `PorcentajeIIBB`, `MontoIIBB`, `PorcentajeOtrasPercepciones`, `MontoOtrasPercepciones`. Se agregan `TotalDeducciones` (18,2; desnormalizado para listados y detalle sin cargar la colección) y `List<FacturaVentaDeduccion> Deducciones`. `Total` pasa a `NetoGravado + MontoIva − TotalDeducciones`.

**`MovimientoStock`**: `+ int? EgresoId` (FK nullable a `Egreso`, `OnDelete: Restrict`), simétrico a `FacturaVentaId`.

### 18.2 Application

- `FacturaVentaCreateInput`: se quitan los cuatro campos de IIBB/percepciones; se agrega `List<DeduccionInput> Deducciones` (`ConceptoDeduccionId?`, `Nombre`, `EsImporteFijo`, `Porcentaje`, `Monto`).
- Nuevo `IConceptoDeduccionService` (ABM + `ListarParaPrecargaAsync()` que devuelve los `AplicaPorDefecto` ordenados).
- `IStockService.RegistrarCompraAsync` gana un parámetro opcional `CostoCompraInput? costo` (rubro, proveedor, subtotal, descuento, IVA, pagos).
- `TableroAnualKpisDto` += `ReinvertidoEnHacienda`.

### 18.3 Infrastructure

**`FacturaVentaService`** — el cálculo del total (líneas ~61 y ~158, las mismas dos de v13) pasa a:

```csharp
var neto  = Math.Round(subtotal - input.MontoDescuento, 2);
var dedu  = Math.Round(input.Deducciones.Sum(d => d.Monto), 2);
var total = Math.Round(neto + input.MontoIva - dedu, 2);
```

**Base de cálculo de las deducciones (v14.1):** el importe de cada deducción porcentual se calcula sobre el **`Subtotal`** (importe bruto), no sobre el neto gravado — el IVA es el único sobre el neto. Igual que con el IVA, **el servidor no recalcula esos importes**: el cliente los manda y el servidor valida rangos y suma (mismo contrato de confianza desde v13). El cambio de base vive por lo tanto en `Facturas/Create.cshtml` (`recalcDeducciones(subtotal)`), no en el servicio.

Validaciones nuevas: cada `%` en [0,100), cada `Monto` ≥ 0 (PV24/PV25), `total > 0` (PV26). Se **borra** la validación de IIBB/percepciones. `EditAsync` reemplaza las deducciones con `RemoveRange` + alta (no hay ledger acá: son líneas del comprobante, no movimientos posteados, así que MH-020 no aplica).

**`StockService.RegistrarCompraAsync`** — con costo, **una sola transacción explícita**: crear el `Egreso` + sus `EgresoPago` + movimientos de caja, `SaveChangesAsync` para obtener el Id, y recién entonces `StockHelper.PostearMovimiento(...)` con `EgresoId` seteado. **No** llamar a `EgresoService.CreateAsync` desde adentro: abre su propia transacción y rompe la atomicidad (RT22). La lógica de alta de egreso se extrae a un método compartido que ambos servicios invocan dentro de la transacción del llamador.

**`StockService.AnularCompraAsync`** — revierte las dos puntas: contramovimiento de caja por lo acreditado (MH-020), baja de los pagos pendientes, soft delete del egreso y contramovimiento de stock. R34.

**`DashboardService`** — `ReinvertidoEnHacienda` = suma de `Egreso.Importe` de los egresos referenciados por movimientos de stock tipo `Compra` no anulados, en el período filtrado.

### 18.4 Web

`ConceptosDeduccionController` (ABM, calcado de `RubrosController`) + entrada en el menú de Catálogos. `Facturas/Create.cshtml`: la card cambia según §8.4.2 y el driver `impGrupos` pierde `iibb`/`percep` y gana el manejo de la grilla. `Stock/Compra.cshtml`: bloque de costo con el **JS compartido** (RD18/PD19). `Facturas/Details.cshtml` y el listado: desglose de deducciones leyendo el snapshot.

### 18.5 Migración EF

**Una sola migración `Facturas_Deducciones_Y_CompraConCosto`, escrita a mano:**

1. `CreateTable ConceptosDeduccion` + `CreateTable FacturaVentaDeducciones` (FK a `FacturasVenta`, cascade; FK a `ConceptosDeduccion`, restrict).
2. `AddColumn FacturasVenta.TotalDeducciones decimal(18,2) NOT NULL DEFAULT 0`.
3. `AddColumn MovimientosStock.EgresoId int NULL` + FK restrict.
4. `DropColumn` de los cuatro campos de IIBB/percepciones de `FacturasVenta`.
5. `INSERT` de los cuatro conceptos semilla (§8.4.1).

**El paso 4 es destructivo y sólo es seguro porque producción tiene 0 facturas de venta** — verificado el 2026-09-08 por consulta directa (`SELECT COUNT(*) FROM FacturasVenta` → 0). **Re-verificar inmediatamente antes de aplicar la migración**: si el cliente cargó facturas en el medio, hay que frenar y convertir esos valores en filas de deducción antes de borrar las columnas.

### Riesgos técnicos v5

- **RT22** Atomicidad de la compra con costo: `EgresoService.CreateAsync` abre su propia transacción. Componer dos servicios transaccionales anida transacciones y rompe PF86. La lógica compartida tiene que poder correr **dentro** de la transacción del llamador.
- **RT23** El `DropColumn` del paso 4 destruye datos si producción dejó de estar en cero. Verificación obligatoria antes de aplicar.
- **RT24** `FacturaVentaDeduccion.ConceptoDeduccionId` es una referencia blanda: el concepto puede borrarse (soft delete) después. El detalle **debe** leer `Nombre`/`Porcentaje` de la propia fila, nunca hacer join al catálogo (RD17/R33).
- **RT25** `MovimientoStock.EgresoId` con `OnDelete: Restrict`: un egreso vinculado a una compra no puede borrarse duro. Es intencional; la baja es soft delete, como todo el resto.
- **RT26** El desglose de deducciones se muestra en el detalle: si alguien recompone el total desde ahí en vez de leer `Total` persistido, va a ignorar los redondeos por línea (RT18 otra vez).

### Checklist de salida v5

- [ ] `SELECT COUNT(*) FROM FacturasVenta` en producción = 0, **verificado el día del deploy**, antes de aplicar la migración (RT23).
- [ ] Migración a mano revisada: sin `RenameColumn`, con los `DropColumn` explícitos y las semillas incluidas.
- [ ] JS de costo/pagos en un único archivo, consumido por `Egresos/Create` y `Stock/Compra` (RD18/PD19).
- [ ] Invariante `Neto − Deducciones + IVA = Total` en 0 desvíos.
- [ ] Compra con costo: stock y egreso creados o ninguno de los dos (PF86), con la transacción verificada forzando un fallo.
- [ ] Anulación de compra de hacienda revierte las dos puntas con contramovimiento (PF88, MH-020).
- [ ] `value=` de los campos nuevos con `CultureInfo.InvariantCulture` y marcadores `__Invariant` en las filas de la grilla (LP-003 / GAN-005).

---

## 16. Historial de versiones

- **v1** — Primera consolidación arquitectónica sobre el blankproject real. Reutiliza `SoftDestroyable`, `ServiceResult`, `IRepository<T>`, `AppDbContext` con query filter global de soft delete, `NotificationService` y convenciones de enums con `HasConversion<int>`. Define estructura de carpetas, dos migraciones EF separadas, estrategia de correlativo con tabla contador + transacción, job diario vía `IHostedService`, almacenamiento local de comprobantes servido por controller autenticado, riesgos técnicos RT1–RT8 y pruebas arquitectónicas PA1–PA6. Deja 3 preguntas abiertas para el diseñador funcional.
- **v2** — Diseño técnico de pagos múltiples de Egreso (§13), grounded en el código real de `ganaderia - emo` (no en el plan v1 pre-implementación). Nueva entidad `EgresoPago` + enum `EstadoPagoEgreso`; `MovimientoCaja.EgresoId` reemplazado por `EgresoPagoId`; nuevo servicio `IEgresoPagoService` calcado de `ICuotaService`; extensión de `AcreditacionCuotasHostedService` (no se crea un segundo job). Punto crítico: migración EF con **backfill de datos de producción** en 3 fases (RT9), con validación obligatoria contra copia de producción antes del deploy real. Riesgos RT9–RT12.
- **v3** — Diseño técnico de autocomplete Select2 (§15): `FacturaVenta.Motivo` pasa de enum (`MotivoVenta`, eliminado) a texto libre, con migración de backfill de menor riesgo que v2 (RT13, mapeo 1:1 sin ambigüedad). Nuevo `IFacturaVentaService.SugerenciasMotivoAsync` simétrico a `IEgresoService.SugerenciasDetalleAsync`. Se retira el `<datalist>` nativo de Egresos y se unifica el widget de autocomplete en un único script JS reutilizable (`ov-autocomplete-select2.js`) para ambas pantallas.
- **v4** — Diseño técnico del descuento comercial pre-impuestos y de la serie de IVA del Tablero Anual (§17), sobre el código real post-v16. Dos columnas por comprobante (`PorcentajeDescuento` 9,4 + `MontoDescuento` 18,2 — se corrige el 18,4 que había estimado el diseño, que no era la convención del proyecto) más `NetoGravado` calculado con `Ignore` explícito. `Total`/`Importe` siguen calculándose **en servidor** (dos líneas por servicio), así que el descuento no cambia el contrato de confianza con el cliente. Serie de IVA por consulta directa a `FacturasVenta`/`Egresos` agrupada en memoria (devengado, sin tocar `MovimientosCaja`), apoyándose en el filtro global de soft delete para excluir anulados. Una única migración `Comprobantes_DescuentoComercial` con `DEFAULT 0` y **sin backfill** — no muta ninguna fila existente, por lo que no requiere el protocolo de 3 fases de RT9. Riesgos RT17–RT21. Escaneo cross-proyecto: criterio de "total autoritativo" tomado de `marihogar`; descuento por línea de `la-platense` descartado; protocolo de migración de `vinosefue` evaluado y no necesario.
- **v4.1** — Dos correcciones de la v4 detectadas por el implementador al contrastar §17 contra el código y los docs reales: (1) el escaneo de reutilización atribuía a `marihogar` el origen del criterio "total autoritativo", cuando `marihogar/5-implementador.md` §657 dice que ese bloque de impuestos fue copiado **de `ganaderia`** — la dirección del préstamo estaba invertida, y corregirla importa porque define a qué proyecto se mira como referencia la próxima vez (corolario: marihogar es candidato natural a recibir este mismo descuento); (2) §17.4 listaba "el PDF del comprobante" entre los consumidores a adaptar, y **ese PDF no existe** en este proyecto (el comprobante es un archivo que el usuario sube). Ningún cambio de decisión técnica.
- **v5** — Diseño técnico de las deducciones de liquidación y de la compra de hacienda con costo (§18). Dos entidades nuevas (`ConceptoDeduccion` catálogo, `FacturaVentaDeduccion` líneas con **snapshot** de nombre y porcentaje), eliminación de los cuatro campos de IIBB/percepciones de `FacturaVenta` —destructivo, seguro sólo porque producción tiene 0 facturas, a re-verificar el día del deploy (RT23)—, `MovimientoStock.EgresoId` simétrico al `FacturaVentaId` existente, y una única migración a mano con semillas. El punto técnico delicado es RT22: la compra con costo tiene que crear egreso y movimiento de stock en **una sola** transacción, así que la lógica de alta de egreso se extrae a un método que corre dentro de la transacción del llamador en vez de llamar a `EgresoService.CreateAsync`. Riesgos RT22–RT26.
- **v5.1** — Base de cálculo de las deducciones corregida a **`Subtotal`** (era el neto gravado), por decisión del usuario tras cuantificar el desvío contra la liquidación real ($117.177,80 en un comprobante de 136 millones). El IVA sigue siendo el único concepto que se calcula sobre el neto gravado. Como el servidor no recalcula los importes de deducción (los recibe del cliente y valida, mismo contrato que el IVA desde v13), el cambio quedó confinado al JS de `Facturas/Create.cshtml` más la documentación de la entidad. R32 cerrado.
