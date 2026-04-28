# Arquitectura Técnica — Sistema de Gestión Ganadera

Versión: **v1**
Agente: `3 - arquitecto-mvc`
Entradas:
- `docs/ganaderia/definiciones/1-analista-funcional.md` v10
- `docs/ganaderia/definiciones/2-disenador-funcional.md` v1

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
  - **Rechazo explícito** de `HasSequence` (EF Core no lo soporta para MySQL/Pomelo).

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
| **Correlativo de Factura** | Tabla `ContadorFactura` con `UPDATE ... RETURNING` dentro de la transacción | EF Core + Pomelo no soportan `HasSequence` en MySQL; `FOR UPDATE` también válido pero requiere transaction explícita. |
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
- **ST2** EF Core 10 con provider Pomelo.EntityFrameworkCore.MySql alineado a .NET 10.
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

## 12. Historial de versiones

- **v1** — Primera consolidación arquitectónica sobre el blankproject real. Reutiliza `SoftDestroyable`, `ServiceResult`, `IRepository<T>`, `AppDbContext` con query filter global de soft delete, `NotificationService` y convenciones de enums con `HasConversion<int>`. Define estructura de carpetas, dos migraciones EF separadas, estrategia de correlativo con tabla contador + transacción, job diario vía `IHostedService`, almacenamiento local de comprobantes servido por controller autenticado, riesgos técnicos RT1–RT8 y pruebas arquitectónicas PA1–PA6. Deja 3 preguntas abiertas para el diseñador funcional.
