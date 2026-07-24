# Memoria - Implementador

## Proyecto: ganaderia
## Ultima actualizacion: 2026-07-23

## Contexto inicial

- Solucion ya copiada del template y renombrada a `Ganaderia.{Domain, Application, Infrastructure, Web}` sobre .NET 10, EF Core 10 + Pomelo MySQL 8, Identity, Serilog, QuestPDF, Bootstrap 5.
- Base reutilizable verificada en codigo:
  - `Ganaderia.Domain.Entities.SoftDestroyable` (Id + auditoria + soft delete via `DeletedAt`).
  - `Ganaderia.Application.DTOs.ServiceResult` y `ServiceResult<T>` (CreateSuccess/CreateError).
  - `Ganaderia.Application.Interfaces.IRepository<T>`, `INotificationService`, `IEmailService`, `IExportService`, `IErrorNotifier`.
  - `Ganaderia.Infrastructure.Data.AppDbContext` (IdentityDbContext con query filter global de soft delete).
  - `Ganaderia.Infrastructure.DependencyInjection.AddInfrastructure(...)` ya registra DbContext, repos, SMTP, NotificationService, ExportService y healthchecks.
  - `Ganaderia.Web.Helpers.FormatoMoneda` (es-AR).
  - Migracion inicial existente: `20260302164700_InitialCreate`.
- Conexion dev: `Server=localhost;Port=3306;Database=ganaderia_dev;Uid=root;Pwd=root;`.

## Plan de etapas aprobado

0. Preparacion y fundaciones (enums + constantes + helpers + memoria) — **EN CURSO**
1. Catalogos base ganaderos + migracion `Ganaderia_Catalogos` + seed roles + ContadorFactura
2. Stock y movimientos + matriz + migracion `Ganaderia_Operativa_Stock`
3. Ventas + Facturas + Cuotas + correlativo + migracion `Ganaderia_Operativa_Ventas`
4. Cuotas: rechazo, regularizacion, caja y job diario
5. Egresos: gastos + comprobantes + autocomplete
6. Dashboard + usuarios productor + cierre de transversales
7. QA integral + checklist

## Convenciones acordadas

- Capa `Application` no depende de EF Core ni `DataAnnotations` de MVC.
- Enums persistidos como `int` con `HasConversion<int>()` (consistente con `EstadoUsuario`).
- DTOs en Application; ViewModels solo en Web.
- Controllers delgados; reglas de negocio en Services.
- Operaciones criticas en transaccion explicita (`IDbContextTransaction`).
- UTC en DB, conversion a `America/Argentina/Buenos_Aires` en presentacion.
- Soft delete via `SoftDestroyable.DeletedAt`; consultas historicas usan `IgnoreQueryFilters()` cuando corresponde (RT3 / PA3).
- Comprobantes fuera de `wwwroot`, raiz `App_Data/comprobantes/{yyyy}/{MM}/{guid}.{ext}`, descarga via endpoint autenticado (RT5).
- Roles Identity: `Productor`, `SuperUsuario` (constantes en `RolesGanaderia`).
- Matriz de transiciones inter-categoria: lista cerrada estatica en `MatrizTransicionesCategoria` (Ternera->Vaquillona, Vaquillona->Vaca, Ternero->Toro).
- Correlativo de Factura: tabla tecnica `ContadorFactura` (Id=1) con `UPDATE ... RETURNING` dentro de la misma transaccion + indice unique en `Factura.Numero` como red de seguridad.

## Etapa 0 - 2026-04-22 - en curso

### Alcance
- Crear estructura de carpetas Ganaderia en las 4 capas.
- Crear los 9 enums del dominio.
- Crear constantes `RolesGanaderia` y `MatrizTransicionesCategoria`.
- Crear helpers Web: `CalculoIvaHelper`, `FormatoCorrelativoHelper`.
- Sin migracion EF en esta etapa.

### Cambios por capa
- Domain: +9 enums (`MotivoVenta`, `FormaDePago`, `TasaImpuesto`, `EstadoCuota`, `EstadoMovimientoCaja`, `TipoMovimientoStock`, `CategoriaHacienda`, `AmbitoProveedor`, `OpcionRegularizacion`), +2 constantes (`RolesGanaderia`, `MatrizTransicionesCategoria`).
- Application: estructura de carpetas `Interfaces/Ganaderia/`, `DTOs/Ganaderia/...` (vacias por ahora).
- Infrastructure: estructura de carpetas `Data/Configurations/Ganaderia/`, `Services/Ganaderia/`, `HostedServices/` (vacias por ahora).
- Web: +2 helpers, estructura de carpetas para controllers, vistas, viewmodels y viewcomponents.

### Migraciones
- No.

### Riesgos/supuestos
- Ninguno especifico de etapa.

### Cierre
- Build: OK (`Ganaderia.Domain`, `Application`, `Infrastructure`, `Web`).
- Archivos creados:
  - Domain/Enums/Ganaderia: `MotivoVenta`, `FormaDePago`, `TasaImpuesto`, `EstadoCuota`, `EstadoMovimientoCaja`, `TipoMovimientoStock`, `CategoriaHacienda`, `AmbitoProveedor`, `OpcionRegularizacion` (todos con valores explicitos como int).
  - Domain/Constants/Ganaderia: `RolesGanaderia` (incluye constante `Operativos`), `MatrizTransicionesCategoria` (con helper `EsTransicionPermitida`).
  - Web/Helpers/Ganaderia: `CalculoIvaHelper` (factor por enum + redondeo a 2 decimales), `FormatoCorrelativoHelper` (`F-NNNNNN` + parser).
- Sin migracion EF.
- Sin cambios en codigo del template.
- Etapa 0 cerrada. Listo para Etapa 1 (catalogos + migracion `Ganaderia_Catalogos`).

## Etapa 1 - 2026-04-22 - cerrada

### Alcance
Sentar el modelo completo de dominio operativo (catalogos + facturacion + cuotas + caja + egresos + comprobantes + movimientos de stock), los servicios de negocio asociados, registrar todo en DI y generar la migracion EF correspondiente. UI/Controllers quedan para etapas siguientes.

### Cambios por capa
- Domain: +12 entidades en `Domain/Entities/Ganaderia/` (`Grupo`, `Rubro`, `Proveedor`, `OrganismoIntermediario`, `ContadorFactura`, `MovimientoStock`, `Factura`, `FacturaItem`, `FacturaCuota`, `MovimientoCaja`, `Egreso`, `ComprobanteEgreso`). Todas heredan de `SoftDestroyable` salvo `ContadorFactura`.
- Application:
  - +6 archivos de contratos en `Application/Interfaces/Ganaderia/` (`ICatalogoServices`, `IStockService`, `IFacturaService`, `ICuotaService`, `ICajaEgresoServices`, `IDashboardService`).
  - +2 helpers movidos desde Web a `Application/Helpers/Ganaderia/` (`CalculoIvaHelper`, `FormatoCorrelativoHelper`). Motivo: son regla de negocio reutilizable cross-capa.
- Infrastructure:
  - `Data/AppDbContext.cs`: +12 `DbSet<>` y `ConfigureGanaderia(...)` con tipos, indices, precision monetaria, query filters de soft delete y FK con `OnDelete(DeleteBehavior.Restrict|Cascade)`.
  - `Data/SeedData.cs`: roles `SuperUsuario` y `Productor` (alias historico `Administrador = Productor`) y semilla de `ContadorFactura` (Id=1, UltimoNumero=0).
  - `DependencyInjection.cs`: registro de los 13 servicios Ganaderia (catalogos, stock, factura+numerador, cuotas, caja, egresos, dashboard) + storage local de comprobantes + `AcreditacionCuotasHostedService`.
  - +10 implementaciones en `Infrastructure/Services/Ganaderia/`: `GrupoService`, `RubroService`, `ProveedorService`, `OrganismoIntermediarioService` (en `CatalogoServices.cs`), `StockService`, `NumeradorFacturaService`, `FacturaService`, `CuotaService`, `CajaService`, `EgresoService`, `LocalComprobanteStorageService`, `DashboardService`, `AcreditacionCuotasHostedService`. Helper interno `StockHelper.CalcularStockAsync/Signo` reusado por servicios.
- Web:
  - `Program.cs`: +policy `RequireProductor` (SuperUsuario|Productor); cambio de `AddExceptionHandler<GlobalExceptionHandler>` (singleton roto por consumir `IErrorNotifier` scoped) por `AddScoped<IExceptionHandler, GlobalExceptionHandler>`. Bug preexistente que impedia arrancar.
  - `Web/Helpers/Ganaderia/CalculoIvaHelper.cs` y `FormatoCorrelativoHelper.cs`: removidos (reubicados en Application).

### Decisiones de negocio aplicadas
- `MotivoVenta` no incluye `Compensacion` (se descarto frente al primer borrador): toda Factura genera egreso de stock; las compensaciones inter/intra grupo viven solo en `MovimientoStock`.
- `FormaDePago` no representa Contado vs Cuotas. Se agrego `CantidadCuotas` al `FacturaCreateInput` (1 = contado mismo dia; 3 = a 30/60/90 dias). El ajuste de centavos cae en la ultima cuota.
- `EstadoMovimientoCaja` solo tiene `Pendiente|Acreditado`. La "anulacion" de caja es soft-delete (`DeletedAt`) sobre el movimiento, manteniendo trazabilidad y excluyendolo del saldo.
- Regularizacion de cuotas (analisis funcional v10 §3.7):
  - `ErrorDeCarga`: el rechazo fue error -> cuota vuelve a `Acreditada`, se restaura el movimiento original con `Estado = Acreditado` y se quita `DeletedAt`. No se crea movimiento nuevo.
  - `CobroPosterior`: cuota se mantiene `Rechazada`; el movimiento original se restaura como `Pendiente` y se crea un movimiento nuevo `Acreditado` con la fecha real de cobro.
- Numerador de factura: `ContadorFactura` (Id=1) con incremento dentro de la misma transaccion EF que la insercion de la `Factura`; indice `UNIQUE` en `Factura.Numero` como red de seguridad ante condicion de carrera.
- Anulacion de Factura: bloqueada si tiene cuotas `Acreditadas` (debe usarse Rechazo/Regularizacion). Reversa stock con movimientos `Compra` y soft-deletea cabecera + items + cuotas.

### Migraciones EF
- Nueva: `Data/Migrations/<timestamp>_Ganaderia_Etapa1_Catalogos_Operacion.cs` (proyecto `Ganaderia.Infrastructure`, contexto `AppDbContext`). Pendiente aplicar (`dotnet ef database update`) en la primera UI funcional de catalogos para validar contra MySQL real.
- Impacto: +12 tablas (Grupos, Rubros, Proveedores, OrganismosIntermediarios, ContadoresFactura, MovimientosStock, Facturas, FacturaItems, FacturaCuotas, MovimientosCaja, Egresos, ComprobantesEgreso). Todas con FK restrictivas y query filters globales de soft delete (excepto `ContadoresFactura`).

### Build y pruebas
- Build: OK (`dotnet build` despues de la migracion).
- Pruebas minimas ejecutadas: solo build + scaffolding de migracion. Pruebas funcionales se cubren en QA al cierre de cada vertical.

### Riesgos y supuestos
- La migracion no fue aplicada todavia contra `ganaderia_dev`; hacerlo despues de tener al menos una vista de catalogo (Etapa 1.5/2) para validar end-to-end.
- Conversion `enum -> int` esta confiada al convention global de Pomelo; verificar tipos generados al revisar el archivo de migracion.
- `ContadorFactura.Id` se fija en 1 con `ValueGeneratedNever` y se siembra en `SeedData`. No se diseno cluster: en un escenario multi-instancia agregaremos `RowVersion` o `SELECT ... FOR UPDATE`.
- `LocalComprobanteStorageService` resuelve path con `AppContext.BaseDirectory\_storage\comprobantes` por defecto; en prod debe configurarse `Ganaderia:ComprobantesPath` fuera del directorio de deploy.
- `AcreditacionCuotasHostedService` corre cada hora y dispara una vez por dia; suficiente para v1 mono-instancia (analisis v10 §7).

### Pruebas minimas requeridas para QA (a futuro vertical)
- Crear/editar/eliminar de cada catalogo (Grupo, Rubro, Proveedor, OrganismoIntermediario), con bloqueo de baja por dependencias.
- Stock: ingresos, muerte y compensacion entre grupos validando `MatrizTransicionesCategoria` y stock no negativo.
- Emision de factura contado y a 3 cuotas: chequear correlativo, totales con IVA snapshot, generacion de cuotas y egreso de stock.
- Acreditacion manual y por job, rechazo y ambas variantes de regularizacion: verificar saldo de caja confirmado.
- Egreso con/sin comprobante: verificar movimiento de caja y baja con reverso de caja.

### Checklist de salida para merge
- [x] Build OK
- [x] Sin uso de EF/MVC en Application
- [x] Servicios registrados en DI
- [x] Migracion EF generada
- [x] Migracion aplicada a `ganaderia_dev`
- [x] Vistas/Controllers de catalogos (Etapa 2)
- [ ] Pruebas funcionales por modulo (QA Etapa 7)

## Etapas 2 a 6 - 2026-04-22 - cerradas (UI Web)

### Alcance funcional resumido
Materializar la capa Web de la vertical Ganaderia: ABM de catalogos, operaciones de stock, emision/anulacion de facturas, gestion manual de cuotas, caja, egresos con comprobante y dashboard operativo. Reusa layout, identidad, auditoria, soft delete y manejo global de errores del template.

### Plan de ejecucion tecnica por etapas
- Etapa 2 (Catalogos + Stock UI): GruposController, RubrosController, ProveedoresController, OrganismosController, StockController + vistas Razor + ViewModels + selects con `SelectListItem`.
- Etapa 3 (Ventas): FacturasController + Create/Details/Index + `FacturaCreateVm` con items dinamicos.
- Etapa 4 (Cuotas + Caja): CuotasController (Index/Acreditar/Rechazar/Regularizar) + CajaController (Index con saldo y movimientos).
- Etapa 5 (Egresos + Comprobantes): EgresosController (Index/Create/Anular/Comprobante) con `IFormFile` y endpoint autenticado de descarga.
- Etapa 6 (Dashboard + navegacion): DashboardController + integracion del menu Ganaderia en `_Layout.cshtml` y namespaces nuevos en `_ViewImports.cshtml`.

### Cambios por capa
- Web/Models/Ganaderia: +5 archivos de ViewModels (`CatalogoViewModels`, `StockViewModels`, `FacturaViewModels`, `CuotaViewModels`, `EgresoViewModels`) con DataAnnotations.
- Web/Controllers: +10 controllers (`GruposController`, `RubrosController`, `ProveedoresController`, `OrganismosController`, `StockController`, `FacturasController`, `CuotasController`, `CajaController`, `EgresosController`, `DashboardController`). Todos `[Authorize(Policy = "RequireProductor")]`, delgados, delegan reglas a Application.
- Web/Views: +30 vistas Razor (Index/Create/Edit/Details segun corresponde) bajo `Views/{Grupos,Rubros,Proveedores,Organismos,Stock,Facturas,Cuotas,Caja,Egresos,Dashboard}`.
- Web/Views/Shared/_Layout.cshtml: nuevo bloque de navegacion con secciones Principal (Inicio, Dashboard), Operacion (Stock, Facturas, Cuotas, Egresos, Caja) y Catalogos (Grupos, Rubros, Proveedores, Organismos). Se removio el item de plantilla "Sample Ping".
- Web/Views/_ViewImports.cshtml: +`Ganaderia.Web.Models.Ganaderia`, +`Ganaderia.Domain.Entities.Ganaderia`, +`Ganaderia.Domain.Enums.Ganaderia`.
- Web/Helpers/FormatoMoneda.cs: +alias `Formatear(decimal)` que delega en `FormatMoneda(valor, "$")`. Motivo: las nuevas vistas Ganaderia consumen `FormatoMoneda.Formatear(...)` para importes.

### Decisiones aplicadas en UI
- Controllers MVC delgados: validan `ModelState`, delegan a servicios y traducen `ServiceResult` a `TempData["SuccessMessage"]`/`["ErrorMessage"]` que el layout renderiza con SweetAlert2.
- Selects de grupos/proveedores/organismos/rubros se cargan con `SelectListItem` desde los servicios de catalogos para evitar acoplar vistas a entidades.
- Compradores en facturas filtran proveedores por `AmbitoProveedor.Ingresos|Ambos`. Proveedores de egreso filtran por `Egresos|Ambos`.
- Anulacion de Factura y Egreso se exponen como `POST` con anti-forgery, devolviendo a Index con mensajes.
- Descarga de comprobante via `EgresosController.Comprobante(id)`: stream con `ContentType` real, fuera de `wwwroot`.
- Rechazo y regularizacion de cuotas reciben el motivo y la `OpcionRegularizacion` desde vistas dedicadas (`Cuotas/Rechazar`, `Cuotas/Regularizar`).

### Migraciones EF
- Sin nuevas migraciones en estas etapas (todo el modelo de datos ya quedo cubierto por la migracion `Ganaderia_Etapa1_Catalogos_Operacion`).

### Build y pruebas
- `run_build`: Build successful tras crear ViewModels, Controllers, Views y actualizar layout/imports.
- Pruebas minimas: solo compilacion. La validacion funcional end-to-end queda para Etapa 7 (QA integral).

### Riesgos y supuestos
- Las vistas creadas son funcionales pero minimas; pulido visual fino con design system queda como deuda para QA.
- Items dinamicos en alta de Factura usan postback simple por ahora; si se requiere agregar/quitar filas en cliente conviene introducir un partial + JS dedicado en QA.
- El job `AcreditacionCuotasHostedService` queda registrado y corriendo en host; ante despliegue multi-instancia debera evaluarse leader election.
- `LocalComprobanteStorageService` requiere configurar `Ganaderia:ComprobantesPath` en produccion fuera del deploy.

### Pruebas minimas requeridas para QA
- ABM de cada catalogo (Grupo, Rubro, Proveedor, Organismo) con bloqueo de baja por dependencia.
- Movimientos de stock: ingreso inicial, nacimiento, muerte, compensacion (matriz) y validacion de stock no negativo.
- Emision de factura contado y a N cuotas: correlativo, IVA snapshot, generacion de cuotas, egreso de stock; anulacion bloqueada con cuotas acreditadas.
- Cuotas: acreditacion manual, rechazo, ambas regularizaciones (`ErrorDeCarga`, `CobroPosterior`) con efecto correcto en caja.
- Egresos: alta con/sin comprobante, descarga autenticada, anulacion que revierte caja.
- Dashboard: KPIs (saldo caja, ingresos/egresos del mes, cuotas pendientes, grupos bajo minimo) y stock resumen.

### Checklist de salida para merge
- [x] Build OK
- [x] Controllers Web `[Authorize]` con policy `RequireProductor`
- [x] Reglas de negocio en Services (Application/Infrastructure), no en Controllers
- [x] Sidebar y `_ViewImports` integrados
- [x] Sin EF/MVC en Application
- [ ] Pruebas funcionales por modulo (QA Etapa 7)
- [ ] Pulido visual con design system (Etapa 7)


## Etapa 7 - 2026-04-22 - cerrada (QA + pulido)

### Alcance
Pulido transversal de UI y entrega del plan integral de QA para validacion funcional end-to-end.

### Cambios por capa
- Web/Views: empty states en grillas principales (Stock/Index, Facturas/Index, Cuotas/Index, Egresos/Index); fechas formateadas dd/MM/yyyy; numero de factura en negrita; badges de color para EstadoCuota (Acreditada=success, Rechazada=danger, otros=secondary).
- docs/qa/plan-qa-etapa7.md: plan de QA con casos por modulo + transversales + performance basico + datos seed + sign-off.

### Migraciones EF
- Sin nuevas migraciones.

### Build y pruebas
- Build: OK tras pulidos visuales.
- Pruebas: ejecutar manualmente segun docs/qa/plan-qa-etapa7.md.

### Riesgos y supuestos
- Plan de QA asume datos seed minimos cargados.
- Performance se valida manualmente.
- Pruebas automatizadas (xUnit) quedan como deuda tecnica futura.

### Checklist de salida para merge
- [x] Build OK final
- [x] Pulido visual aplicado
- [x] Plan de QA documentado en docs/qa/plan-qa-etapa7.md
- [ ] QA manual ejecutado y firmado
- [ ] Despliegue a UAT

## Etapa 8 - 2026-05-07 - cerrada (Refactor dominio + mejoras operativas)

### Alcance
Refactor del modelo de dominio post-QA: consolidacion de `OrganismoIntermediario` en `Proveedor`, renombrado fisico `Factura -> FacturaVenta`, implementacion de modulos faltantes (Stock, Egresos con FormaDePago, Notificaciones, Feature Flags) y deploy a produccion.

### Cambios por capa

**Domain:**
- `FacturaVenta.cs` nueva entidad (renombra `Factura`); `FacturaVentaItem.cs`; `FacturaVentaCuota.cs`; `ContadorFacturaVenta.cs`.
- `ComprobanteFacturaVenta.cs` entidad nueva para adjunto de factura.
- `JobEjecucion.cs` entidad nueva para trazabilidad del job de acreditacion.
- `MovimientoStock.cs`: `FacturaId` renombrado a `FacturaVentaId`.
- `TasaImpuesto` enum ajustado.

**Application:**
- `IFacturaVentaService.cs` y `INumeradorFacturaVentaService.cs`: contratos actualizados post-rename.
- `ICatalogoServices.cs`: removido `IOrganismoIntermediarioService` (absorbido en `IProveedorService`).
- `ICuotaService.cs` ajustado al nuevo nombre de entidad.
- `IStockService.cs` ajustado.

**Infrastructure:**
- `AppDbContext.cs`: 5 `DbSet` actualizados + `DbSet<JobEjecucion>` nuevo.
- `FacturaVentaService.cs`: servicio reescrito para el nuevo modelo. `ProveedorId` reemplaza a `OrganismoIntermediarioId`.
- `NumeradorFacturaVentaService.cs`: actualizado.
- `CuotaService.cs`, `DashboardService.cs`, `CatalogoServices.cs`, `SeedData.cs`, `DependencyInjection.cs`: actualizados.
- `AcreditacionCuotasHostedService.cs`: ahora persiste `JobEjecucion` por cada corrida.
- 5 migraciones EF nuevas (ver abajo).

**Web:**
- `FacturasController.cs`: reescrito para `FacturaVenta` con `ProveedorId` en lugar de `OrganismoIntermediarioId`. Vistas `Index`, `Create`, `Details` actualizadas.
- `FacturaViewModels.cs`, `CatalogoViewModels.cs`: actualizados.
- `StockController.cs` + `StockViewModels.cs` + vistas `Stock/Index`, `Stock/Compra`, `Stock/Historial`, `Stock/Movimientos`.
- `EgresosController.cs` + `EgresoViewModels.cs`: `FormaDePago` ahora incluido en el alta de egreso.
- `CajaController.cs`: drill-down de navegacion.
- `NotificationsController.cs` + vistas `Notifications/Index`, `Notifications/Details` + `wwwroot/js/notifications.js`.
- `Cuotas/Index.cshtml`: actualizada.
- `_Layout.cshtml`: menu actualizado (remover Organismos, agregar Stock con historial).
- `AccountController.cs`: ajustes menores.
- `Program.cs`: `FeatureFlags.cs` nuevo para control de modulos en preview.
- `Filters/Etapa2OnlyAttribute.cs`: filtro de acceso por feature flag.
- `appsettings.json` / `appsettings.Production.json`: flags de etapa configurados.
- `web.config`: actualizado para produccion.
- `Ganaderia.Web.csproj`: dependencias actualizadas.

### Migraciones EF (5 nuevas, todas aplicadas en `ganaderia_dev`)

| Migracion | Descripcion |
|---|---|
| `20260507144532_RenameFacturaToFacturaVenta` | Rename fisico `Facturas->FacturasVenta`, items, cuotas, contador y FK en stock |
| `20260507152516_FacturaVenta_ItemKilosPrecioPorKilo_PlazoNullable` | Campos `Kilos`, `PrecioPorKilo` en item; `Plazo` nullable en cuota |
| `20260507154402_Egreso_FormaDePago` | Campo `FormaDePago` (int) en tabla `Egresos` |
| `20260507155158_MovimientoCaja_DrillDownNav` | FK de navegacion drill-down en `MovimientosCaja` |
| `20260507163603_JobEjecucion` | Tabla `JobEjecuciones` para trazabilidad del job diario |
| `20260507173610_FacturaVenta_Comprobante` | Tabla `ComprobantesFacturaVenta` para adjuntos de factura |

### Decisiones tecnicas aplicadas
- `OrganismoIntermediario` eliminado: los organismos migraron como `Proveedor` con `Ambito = Ingresos`. El controller `OrganismosController` y sus vistas fueron removidos.
- `Factura` -> `FacturaVenta` end-to-end (entidad, tabla, indices, FK, servicios, controllers, vistas, menu). Migration Option B: no destructiva, preserva datos.
- Feature Flags via `FeatureFlags.cs` + `Etapa2OnlyAttribute` para controlar visibilidad de modulos en etapa de UAT.
- Job de acreditacion de cuotas ahora persiste `JobEjecucion` con timestamp, resultado y errores para auditoria operativa.

### Build y evidencia
- Build: OK tras todas las migraciones y refactors.
- Migraciones aplicadas a `ganaderia_dev`.

### Riesgos y supuestos
- Pendiente aplicar migraciones en produccion (UAT no iniciado formalmente).
- `appsettings.Production.json` configurado con flags de etapa para deploy controlado.

---

## Iteracion v11 — Pagos multiples de Egreso (2026-07-02)

Repositorio exclusivo: `C:\Sistemas\ganaderia - emo` (NO se toco `C:\Sistemas\ganaderia - fausto`). Sistema **en produccion desde mayo 2026**; cambio evolutivo, no proyecto nuevo. Fuentes: `1-analista-funcional.md` v11 §4, `2-disenador-funcional.md` v2 §2.6-2.9/§3.5-3.5.2/§4.4-4.9, `3-arquitecto-mvc.md` §13 (prioridad sobre §1-12), `4-presupuestador.md` "Iteracion v11" (USD 415.0, aprobado).

### 0. Escaneo de reutilizacion (paso obligatorio previo)
Se escaneo `C:/Sistemas/Agentes-IA/docs/*/definiciones/5-implementador.md` (ShowroomGriffin, century-21, delicias-naturales, meta-ads, etc.) buscando el patron "pagos multiples con estado y ciclo de vida (Pendiente/Acreditado/Rechazado) + job diario idempotente + rechazo/regularizacion 3a/3b". **Sin match cross-proyecto.** El unico precedente es intra-proyecto: `CuotaService`/`FacturaVentaCuota`, ya implementado y probado en este mismo repositorio (etapa anterior, mayo 2026). Se copio ese patron 1:1 en `EgresoPagoService` en vez de disenar desde cero, tal como indicaba la arquitectura (RT10).

### 1. Alcance funcional resumido
El modulo Egreso (compra a proveedor) pasa de "1 forma de pago con acreditacion inmediata" a **pagos multiples** (nueva entidad `EgresoPago`, 1 Egreso -> N Pagos). Habilita cheques diferidos con fecha de vencimiento propia + pago compensatorio, con ciclo de vida Pendiente->Acreditado via el job diario ya existente (`AcreditacionCuotasHostedService`, extendido, no duplicado), y rechazo/regularizacion (Opcion 3a/3b) simetricos a los ya implementados para Cuotas de venta. Sin edicion de Egresos existentes (fuera de alcance, S34).

### 2. Plan de ejecucion tecnica por etapas (seguido)
1. Domain: `EgresoPago`, `EstadoPagoEgreso`, cambios en `Egreso`/`MovimientoCaja`/`JobEjecucion`.
2. Application: `EgresoPagoInput`, `EgresoCreateInput` (con `List<EgresoPagoInput> Pagos`), `IEgresoPagoService`.
3. Infrastructure: `EgresoService.CreateAsync/AnularAsync` reescritos, `EgresoPagoService` nuevo (calcado de `CuotaService`), `AppDbContext` (DbSet + fluent config), `AcreditacionCuotasHostedService` extendido, `DependencyInjection` actualizado. Ajuste no previsto: `CajaService.ListAsync` tambien usaba `MovimientoCaja.Egreso` para drill-down y requirio actualizarse a `EgresoPago.Egreso`.
4. Migracion EF en 3 fases (schema aditivo -> backfill SQL -> drop destructivo), reescrita a mano sobre el esqueleto de `dotnet ef migrations add` (ver §4).
5. Web: `EgresoViewModels.cs` (grilla `Pagos`), `EgresosController.Create` adaptado, `EgresoPagosController` nuevo (Rechazar/Regularizar), vistas `Egresos/Create.cshtml` (grilla dinamica JS con reindexado `Pagos[i]`), `Egresos/_FilaPago.cshtml` (partial), `Egresos/Details.cshtml` (tabla de pagos + acciones), `Egresos/Index.cshtml` (columna "Pagos" en vez de "Forma pago"), `EgresoPagos/Rechazar.cshtml`, `EgresoPagos/Regularizar.cshtml` (calcadas de `Cuotas/Rechazar.cshtml`/`Cuotas/Regularizar.cshtml`). Ajuste no previsto: `Caja/Index.cshtml` tambien referenciaba `MovimientoCaja.EgresoId` para el link de drill-down y se adapto a `m.EgresoPago.EgresoId`.

### 3. Cambios por capa (archivos)

**Domain**
- `Ganaderia.Domain/Entities/Ganaderia/EgresoPago.cs` (nuevo) — entidad `SoftDestroyable` con `EgresoId`, `FormaDePago`, `Importe`, `FechaEfectiva`, `FechaVencimiento?`, `Estado`, `FechaRechazo?`, `MotivoRechazo?`, `OpcionRegularizacion?`, `FechaRegularizacion?`, `MovimientoCajaEgresoId?`.
- `Ganaderia.Domain/Enums/Ganaderia/EstadoPagoEgreso.cs` (nuevo) — `Pendiente=1, Acreditado=2, Rechazado=3`.
- `Ganaderia.Domain/Entities/Ganaderia/Egreso.cs` — se quito `FormaDePago`; se agrego `ICollection<EgresoPago> Pagos`.
- `Ganaderia.Domain/Entities/Ganaderia/MovimientoCaja.cs` — `EgresoId`/`Egreso` reemplazados por `EgresoPagoId`/`EgresoPago`.
- `Ganaderia.Domain/Entities/Ganaderia/JobEjecucion.cs` — nueva columna `ChequesEgresoProcesados` (int).

**Application**
- `Ganaderia.Application/Interfaces/Ganaderia/ICajaEgresoServices.cs` — nuevo record `EgresoPagoInput`; `EgresoCreateInput` cambia `FormaDePago` por `List<EgresoPagoInput> Pagos`; nueva interfaz `IEgresoPagoService` (`RechazarAsync`, `RegularizarAsync`, `AcreditarChequesVencidosAsync`).

**Infrastructure**
- `Ganaderia.Infrastructure/Services/Ganaderia/EgresoService.cs` — `CreateAsync` reescrito: valida `Pagos.Count>=1` (PV15), cada `Importe>0`, Cheque requiere `FechaVencimiento>=FechaEfectiva` (PV13/PV14), suma de pagos == importe total con redondeo 2 decimales sin tolerancia (PF56/RD6/S31); crea N `EgresoPago` en transaccion, Efectivo/Transferencia con `MovimientoCaja` inmediato Acreditado, Cheque en Pendiente sin movimiento. `AnularAsync` reescrito: propaga soft-delete a todos los `EgresoPago` del Egreso y a todos los `MovimientoCaja` asociados a esos pagos.
- `Ganaderia.Infrastructure/Services/Ganaderia/EgresoPagoService.cs` (nuevo) — `RechazarAsync`, `RegularizarAsync` (3a/3b), `AcreditarChequesVencidosAsync` calcados linea por linea del patron de `CuotaService.cs` (misma transaccion por item, `IgnoreQueryFilters()`, mutacion de estado sin contramovimiento en rechazo).
- `Ganaderia.Infrastructure/Services/Ganaderia/CajaService.cs` — `ListAsync`: `Include(m => m.Egreso)` reemplazado por `Include(m => m.EgresoPago).ThenInclude(p => p.Egreso)` (ajuste no previsto explicitamente en la arquitectura, detectado al compilar).
- `Ganaderia.Infrastructure/Services/Ganaderia/AcreditacionCuotasHostedService.cs` — `EjecutarSiCorrespondeAsync` extendido: tras `ICuotaService.AcreditarCuotasVencidasAsync`, invoca `IEgresoPagoService.AcreditarChequesVencidosAsync` (transaccion independiente por coleccion, RT11); `registro.ChequesEgresoProcesados` persistido; notificacion in-app consolidada con ambos totales (una sola notificacion, no dos).
- `Ganaderia.Infrastructure/Data/AppDbContext.cs` — `DbSet<EgresoPago> EgresoPagos`; fluent config nueva de `EgresoPago` (conversiones int, precision 18,2, indice `(Estado, FormaDePago, FechaVencimiento)`, FK a `Egreso`); `MovimientoCaja` reconfigurado con FK a `EgresoPago` en vez de `Egreso`; `Egreso` pierde la conversion de `FormaDePago`.
- `Ganaderia.Infrastructure/DependencyInjection.cs` — registrado `IEgresoPagoService -> EgresoPagoService` (Scoped).

**Web**
- `Ganaderia.Web/Models/Ganaderia/EgresoViewModels.cs` — `EgresoCreateVm.FormaDePago` reemplazado por `List<EgresoPagoViewModel> Pagos` (min. 1 fila por defecto); nuevo `EgresoPagoViewModel`; nuevos `RechazoEgresoPagoVm`, `RegularizacionEgresoPagoVm`.
- `Ganaderia.Web/Controllers/EgresosController.cs` — `Create(POST)`: valida `Pagos.Count>0` en cliente, mapea `List<EgresoPagoViewModel>` a `List<EgresoPagoInput>`.
- `Ganaderia.Web/Controllers/EgresoPagosController.cs` (nuevo) — `Rechazar`/`Regularizar` (GET+POST), calcado de `CuotasController`.
- `Ganaderia.Web/Views/Egresos/Create.cshtml` — grilla dinamica de pagos (agregar/quitar filas por JS, reindexado `Pagos[i].Campo`, toggle de `FechaVencimiento` habilitado solo si Cheque, validacion en vivo de suma == importe total).
- `Ganaderia.Web/Views/Egresos/_FilaPago.cshtml` (nuevo, partial) — fila de la grilla, reutilizada tanto en el render inicial como en el template JS de "agregar pago".
- `Ganaderia.Web/Views/Egresos/Details.cshtml` — tabla de pagos con estado (badge) y acciones Rechazar/Regularizar condicionadas a `FormaDePago==Cheque` y `Estado`.
- `Ganaderia.Web/Views/Egresos/Index.cshtml` — columna "Forma pago" reemplazada por "Pagos" (muestra la unica forma si hay 1 pago, o "N pagos" con tooltip si hay varios).
- `Ganaderia.Web/Views/EgresoPagos/Rechazar.cshtml`, `Regularizar.cshtml` (nuevas) — calcadas de `Cuotas/Rechazar.cshtml`/`Cuotas/Regularizar.cshtml`.
- `Ganaderia.Web/Views/Caja/Index.cshtml` — drill-down de Egreso adaptado a `m.EgresoPago.EgresoId` (ajuste no previsto).

### 4. Migracion EF — `20260702181125_EgresoPago_PagosMultiples`

**Critico**: el `Up()` auto-generado por `dotnet ef migrations add` dropeaba `Egresos.FormaDePago` y **renombraba** `MovimientosCaja.EgresoId` a `EgresoPagoId` sin backfill — hubiera corrompido la FK (los valores existentes de `EgresoId` habrian quedado apuntando a `EgresoPagoId` inexistentes, ya que la tabla `EgresoPagos` se crea vacia) y perdido la trazabilidad de `Egreso.FormaDePago`. Se reescribio manualmente el archivo `.cs` de la migracion (`Up()`/`Down()`) siguiendo el plan de 3 fases de `3-arquitecto-mvc.md` §13.4:

- **Fase A (schema aditivo)**: `CREATE TABLE EgresoPagos`; `ADD COLUMN MovimientosCaja.EgresoPagoId` (nullable, coexiste temporalmente con `EgresoId`); `ADD COLUMN JobEjecuciones.ChequesEgresoProcesados` (default 0).
- **Fase B (backfill, `migrationBuilder.Sql(...)`)**: `INSERT INTO EgresoPagos` — 1 fila por cada `Egreso` existente (`Estado=2/Acreditado`, `FormaDePago`/`Importe`/`Fecha` copiados, `MovimientoCajaEgresoId` resuelto via subquery al `MovimientoCaja` existente); luego `UPDATE MovimientosCaja ... SET EgresoPagoId = ep.Id` via join contra `EgresoPagos.MovimientoCajaEgresoId`. Egresos anulados (`DeletedAt` no nulo) migran su pago con el mismo `DeletedAt`. Se dejaron **comentadas en el propio archivo** las 3 queries de validacion (conteo `Egresos` vs `EgresoPagos`, conteo `MovimientosCaja` con `EgresoId`/`EgresoPagoId` no nulo, pagos sin `MovimientoCajaEgresoId`) para correr manualmente contra una copia de produccion antes del deploy real (RT9).
- **Fase C (schema destructivo)**: recien aqui `DROP FK`, `DROP COLUMN MovimientosCaja.EgresoId`, `DROP COLUMN Egresos.FormaDePago`, `ADD FK MovimientosCaja.EgresoPagoId -> EgresoPagos.Id`.
- **`Down()`**: reconstruye el esquema v10 (recrea `Egresos.FormaDePago` a partir del primer `EgresoPago` de cada Egreso — mejor esfuerzo; recrea `MovimientosCaja.EgresoId` desde `EgresoPago.EgresoId`). Documentado en el propio archivo: si se cargaron Egresos con **mas de 1 pago** o cheques Pendientes despues de aplicar esta migracion, el rollback pierde esa informacion (no representable en el modelo v10) — mismo criterio que RT2 del plan v1, no es lossless.

**Validacion del backfill (a ejecutar en el despliegue, NO en este entorno)**:
```sql
-- 1) Egresos y EgresoPagos deben coincidir 1:1
SELECT (SELECT COUNT(*) FROM Egresos) AS TotalEgresos,
       (SELECT COUNT(*) FROM EgresoPagos) AS TotalEgresoPagos;

-- 2) MovimientosCaja con vinculo a Egreso (antes) vs a EgresoPago (despues) deben coincidir
--    (correr el primer SELECT ANTES de aplicar la migracion, el segundo DESPUES)
SELECT COUNT(*) FROM MovimientosCaja WHERE EgresoId IS NOT NULL;      -- pre-migracion
SELECT COUNT(*) FROM MovimientosCaja WHERE EgresoPagoId IS NOT NULL; -- post-migracion

-- 3) Todo EgresoPago vigente (no anulado) deberia tener su MovimientoCaja vinculado
SELECT * FROM EgresoPagos WHERE MovimientoCajaEgresoId IS NULL AND DeletedAt IS NULL; -- debe dar 0 filas
```
Se valido la migracion generando el script SQL completo (`dotnet ef migrations script ... -o migracion_egresopago.sql`, scratchpad de la sesion) y confirmando el orden de sentencias: `CREATE TABLE` -> `INSERT`/`UPDATE` backfill -> `DROP COLUMN`/`ADD CONSTRAINT`. **No se aplico contra ninguna base** (ni dev ni produccion): eso queda a cargo del despliegue, con backup previo de `Egresos` y `MovimientosCaja`, tal como exige RT9.

### 5. Evidencia de build
- `dotnet build Ganaderia.slnx -c Debug` → **Compilacion correcta. 0 Errores** (9 advertencias, todas preexistentes: `NU1902` MailKit/MimeKit y `CS0114` en `HomeController`, no relacionadas con este cambio).
- `dotnet build Ganaderia.slnx -c Release` → **Compilacion correcta. 0 Errores**.
- `dotnet ef migrations add EgresoPago_PagosMultiples ...` → generado y build post-edicion manual OK.
- `dotnet ef migrations script <anterior> <nueva> -o ...` → generado sin errores; orden de fases verificado manualmente en el SQL resultante.
- No se aplico la migracion contra ninguna base de datos (dev ni produccion) en esta sesion.

### 6. Riesgos y supuestos
- **RT9** (critico, heredado de arquitectura): backfill debe validarse contra copia de produccion + backup previo antes de aplicar el deploy real. Script de validacion dejado documentado en la propia migracion.
- **RT10**: se siguio el patron de `CuotaService` linea por linea para minimizar divergencia de comportamiento.
- **RT11**: `AcreditarCuotasVencidasAsync` y `AcreditarChequesVencidosAsync` corren con transacciones independientes por item (no una transaccion comun), para que una falla en una coleccion no revierta la otra.
- **RT12**: grilla dinamica de pagos con reindexado JS de `Pagos[i]`; cubierta con estructura estandar de binding MVC, falta smoke test manual en navegador (no ejecutado en esta sesion, requiere entorno corriendo).
- Supuesto nuevo no cubierto explicitamente por el diseño: `CajaService` y `Caja/Index.cshtml` tambien consumian la FK vieja `MovimientoCaja.Egreso`/`EgresoId` para drill-down de consulta — no estaba listado en el alcance pero es necesario para que el build compile y el modulo Caja siga funcionando; se adapto sin cambiar el comportamiento visible (mismo link "Ver egreso", ahora resuelto via `EgresoPago.EgresoId`).

### 7. Decisiones de diseño no 100% especificadas (para que QA las tenga en cuenta)
- El diseñador funcional §4 usa firmas genericas `Resultado<T>` (plan v1 pre-implementacion); se siguio la arquitectura §13 (`ServiceResult`, records `EgresoCreateInput`/`EgresoPagoInput`) por tener prioridad explicita y estar grounded en el codigo real.
- El mensaje de `Concepto` del `MovimientoCaja` generado por acreditacion de cheque vencido usa el texto fijo "(Cheque vencido)"; no estaba especificado el formato exacto en el diseño, se siguio el estilo de `CuotaService` (`Concepto` descriptivo con rubro/proveedor).
- En `EgresoPagoService.RegularizarAsync` opcion 3b, el nuevo `MovimientoCaja` usa `EsIngreso=false` (es un egreso) — analogo a `CuotaService` que usa `EsIngreso=true` para cuotas (ingreso); no explicitado en el diseño pero es la unica opcion consistente con el signo del saldo de caja.
- La columna "Pagos" del listado `Egresos/Index` (1 forma de pago vs "N pagos") es una decision de UI no especificada en el diseño (que solo detallaba `Egresos/Create` y `Egresos/Details`); se opto por mantener la tabla legible sin agregar columnas nuevas al DataTable existente.
- No se implemento un endpoint `GET` en `EgresoPagosController` para mostrar el detalle del pago antes de rechazar/regularizar (igual que `CuotasController`, que solo recibe el `id` por la URL); el usuario ve el contexto completo en `Egresos/Details` antes de hacer clic en la accion.

### 8. Pruebas minimas requeridas para QA
Aplican tal cual del analisis funcional v11 §16: **PF53-PF61** (alta con 1 pago Efectivo, cheque diferido que cubre el total, 2 cheques + compensatorio, suma que no cuadra bloqueada, job acredita cheque vencido + notifica, job idempotente, rechazo de cheque Acreditado, regularizacion 3a, regularizacion 3b) y **PV13-PV16** (cheque sin fecha de vencimiento bloqueado, fecha de vencimiento anterior a fecha efectiva bloqueado, Egreso sin pagos bloqueado, no regularizar/rechazar pago que no sea Cheque o ya Rechazado).

Desvios/notas para QA:
- PF56 (suma no coincide) y PV13/PV14 se validan tanto en cliente (JS, en vivo) como en servidor (`EgresoService.CreateAsync`, autoritativo) — probar tambien con JS deshabilitado o POST directo para confirmar que el servidor bloquea igual.
- No hay prueba automatizada de integracion para el backfill de la migracion (RT9): la validacion contra datos reales de produccion queda fuera del alcance de esta sesion, a cargo del equipo de despliegue con las queries documentadas en la migracion (§4 arriba).
- Falta smoke test manual en navegador de la grilla dinamica (agregar/quitar filas, reindexado, toggle de fecha de vencimiento) — no ejecutado en esta sesion por no haber corrido la app.
- Regresion a validar: `Caja/Index` (listado y drill-down a Egreso) y `Facturas/Details` (que su propio `FormaDePago` de `FacturaVenta`, entidad no tocada, siga funcionando sin cambios).

### 9. Checklist de salida para merge
- [x] `EgresoPago` creada, hereda `SoftDestroyable`, configurada en `AppDbContext` con indice `(Estado, FormaDePago, FechaVencimiento)`.
- [x] `MovimientoCaja.EgresoId` reemplazado por `EgresoPagoId` (FK + navegacion).
- [x] Migracion con backfill de datos escrita en 3 fases y validada via script SQL generado (orden de sentencias correcto).
- [ ] Migracion con backfill **ejecutada y validada contra copia real de produccion** — pendiente, responsabilidad del despliegue (RT9).
- [x] `IEgresoPagoService`/`EgresoPagoService` implementados calcando el patron de `ICuotaService`/`CuotaService`.
- [x] `EgresoService.CreateAsync` valida suma exacta de pagos + reglas de cheque (servidor, autoridad).
- [x] `EgresoService.AnularAsync` propaga baja logica a `EgresoPago` y `MovimientoCaja` asociados.
- [x] `AcreditacionCuotasHostedService` extendido para procesar `EgresoPago` sin crear un segundo `IHostedService`.
- [x] `EgresosController.Create` con grilla dinamica de pagos (binding `List<EgresoPagoViewModel>`); `EgresoPagosController` con `Rechazar`/`Regularizar`.
- [ ] Backup de `Egresos`/`MovimientosCaja` tomado inmediatamente antes del deploy a produccion — pendiente, responsabilidad del despliegue.
- [x] `dotnet build` OK en Debug y Release, 0 errores.
- [ ] Pruebas funcionales PF53-PF61/PV13-PV16 ejecutadas por QA — pendiente, fuera del alcance de esta sesion de implementacion.
- [x] `ganaderia - fausto` no tocado (confirmado: no es un repo git accesible en este entorno; ningun archivo fuera de `ganaderia - emo` fue leido ni escrito).
- Tests funcionales end-to-end pendientes (QA Etapa 7 plan, ejecutar con datos reales).

---

## Iteracion v12 — Autocomplete Select2 (Concepto de Egreso, Motivo de Factura de venta)

Repo: **`C:\Sistemas\ganaderia - emo`** unicamente (`ganaderia - fausto` no tocado). Grounded en analisis funcional v12 §3.1/§4.1/§10, diseño funcional v3 §8.1/§8.2, arquitectura v3 §15.

### 0. Escaneo de reutilizacion
Se escanearon todos los `docs/*/definiciones/5-implementador.md` del estudio buscando "Select2"/"autocomplete". Unico match relevante: `docs/vinosefue/definiciones/5-implementador.md`, que usa un autocomplete simple (no Select2 AJAX con `tags:true`), no aplicable como fuente de copia directa. El patron de referencia real ya vive dentro del propio proyecto `ganaderia - emo` (v11: `EgresosController.SugerenciasDetalle` + `EgresoService.SugerenciasDetalleAsync`), que es precisamente lo que arquitectura v3 indica calcar para `Motivo`. **Decision: implementar in-place calcando el patron existente del propio proyecto; no se copio codigo de otro proyecto del estudio.**

### 1. Alcance funcional resumido
Dos cambios de UX/datos con Select2 (ya cargado globalmente en `_Layout.cshtml`, sin agregar dependencias nuevas):
1. `Egresos/Create` — Concepto pasa de `<input list> + <datalist>` con `fetch` manual a Select2 AJAX (`tags:true`) contra el endpoint ya existente `Egresos/SugerenciasDetalle` (backend sin cambios).
2. `Facturas/Create` — Motivo deja de ser un enum cerrado (`MotivoVenta`: Faena/Vacía/Enfermedad) y pasa a texto libre con Select2 AJAX contra un endpoint nuevo `Facturas/SugerenciasMotivo`, mismo patron.

### 2. Plan de ejecucion tecnica por etapas
1. Script JS reutilizable `ov-autocomplete-select2.js` (`initAutocompleteSelect2(selector, url)`).
2. `Egresos/Create.cshtml`: `<input list>+<datalist>` → `<select>` + Select2; retiro del JS viejo de `fetch`.
3. Domain: `FacturaVenta.Motivo` de `MotivoVenta` (enum) a `string`; eliminacion de `Enums/Ganaderia/MotivoVenta.cs`.
4. Application: `IFacturaVentaService` — `FacturaVentaCreateInput.Motivo` a `string`; nuevo `SugerenciasMotivoAsync`.
5. Infrastructure: `FacturaVentaService.SugerenciasMotivoAsync` calcado de `EgresoService.SugerenciasDetalleAsync`; `Motivo.Trim()` en alta/edicion; validacion Required/StringLength(200) repetida en `ValidarInput` (defensa de servicio).
6. Infrastructure: `AppDbContext` — config fluent de `Motivo` de `HasConversion<int>()` a `HasMaxLength(200).IsRequired()`.
7. Migracion EF `FacturaVenta_MotivoTexto` (3 fases, ver §4).
8. Web: `FacturasController.SugerenciasMotivo` (calcada de `EgresosController.SugerenciasDetalle`); `FacturaVentaCreateVm.Motivo` a `string` con `[Required, StringLength(200)]`.
9. `Facturas/Create.cshtml`: `<select asp-items="Html.GetEnumSelectList<MotivoVenta>()">` → `<select>` + Select2 AJAX (misma vista sirve `Create` y `Edit`, ambos flujos cubiertos).
10. Verificacion de referencias colgantes a `MotivoVenta` en toda la solucion (grep antes y despues del borrado).
11. Build.

### 3. Cambios por capa (archivos tocados y motivo)

**Presentacion (Web)**
- `Ganaderia.Web/wwwroot/js/ov-autocomplete-select2.js` (nuevo): funcion unica `initAutocompleteSelect2(selector, url)` reutilizada por ambas vistas — evita duplicar el snippet de diseño §8.1 en 2 archivos `.cshtml` (RD9).
- `Ganaderia.Web/Views/Egresos/Create.cshtml`: input `Detalle` reemplazado por `<select>` + Select2; retirado el bloque JS de `fetch`/`<datalist>` (bugfix post-v11, ahora codigo muerto). Grilla de pagos multiples (`btnAgregarPago`, `filaPagoTemplate`, reindexado) **no tocada**.
- `Ganaderia.Web/Views/Facturas/Create.cshtml`: `<select asp-items="Html.GetEnumSelectList<MotivoVenta>()">` reemplazado por `<select>` + Select2 AJAX contra `Facturas/SugerenciasMotivo`. Resto de la vista (items, calculo de IVA/cuotas en vivo) no tocado.
- `Ganaderia.Web/Controllers/FacturasController.cs`: accion nueva `SugerenciasMotivo(string? term, int top = 10)`, calcada de `EgresosController.SugerenciasDetalle` — sin logica de negocio, delega en `IFacturaVentaService.SugerenciasMotivoAsync`.
- `Ganaderia.Web/Models/Ganaderia/FacturaViewModels.cs`: `FacturaVentaCreateVm.Motivo` de `MotivoVenta` a `string` con `[Required, StringLength(200)]`.

**Negocio (Application + Infrastructure)**
- `Ganaderia.Application/Interfaces/Ganaderia/IFacturaVentaService.cs`: `FacturaVentaCreateInput.Motivo` a `string`; nuevo `Task<List<string>> SugerenciasMotivoAsync(string? term, int top = 10)`.
- `Ganaderia.Infrastructure/Services/Ganaderia/FacturaVentaService.cs`: nuevo metodo `SugerenciasMotivoAsync` (mismo patron `GroupBy`+`OrderByDescending(Max(Id))`+`Take` que `EgresoService.SugerenciasDetalleAsync`, sobre `_db.FacturasVenta.Motivo`); `ValidarInput` ahora valida `Motivo` (obligatorio, max 200) sin enum de por medio; `Motivo.Trim()` aplicado en `CreateAsync`/`EditAsync` (mismo criterio que `Egreso.Detalle.Trim()`).

**Datos (EF Core + MySQL)**
- `Ganaderia.Domain/Entities/Ganaderia/FacturaVenta.cs`: `Motivo` de `MotivoVenta` a `string` (`= string.Empty`).
- `Ganaderia.Domain/Enums/Ganaderia/MotivoVenta.cs`: **eliminado** (verificado sin referencias colgantes tras el cambio, `grep -rn "MotivoVenta"` solo devuelve un comentario explicativo en `FacturaVenta.cs`).
- `Ganaderia.Infrastructure/Data/AppDbContext.cs`: config fluent de `FacturaVenta.Motivo` de `HasConversion<int>()` a `HasMaxLength(200).IsRequired()`.
- Migracion `20260702210025_FacturaVenta_MotivoTexto.cs` (+ `.Designer.cs`, snapshot actualizado) — ver §4.

### 4. Migracion EF aplicada
**`FacturaVenta_MotivoTexto`** (una sola migracion, 3 fases, sin el nivel de validacion obligatoria de la migracion v11/RT9 porque el mapeo es 1:1 sin ambiguedad — RT13 arquitectura §15.3):
- Fase A: `AddColumn<string>("MotivoTexto", "FacturasVenta", varchar(200), nullable)`.
- Fase B: backfill via `migrationBuilder.Sql` — `CASE Motivo WHEN 1 THEN 'Faena' WHEN 2 THEN 'Vacía' WHEN 3 THEN 'Enfermedad' ELSE 'Faena' END`.
- Fase C: `DropColumn("Motivo")` → `RenameColumn("MotivoTexto","Motivo")` → `AlterColumn` a `NOT NULL`.
- `Down()`: recrea columna `int`, mapea texto exacto de vuelta a 1/2/3, con fallback a `1` para valores libres cargados despues de v12 (no lossless, mismo criterio documentado que el `Down()` de la migracion v11).

**Nota de proceso:** se genero primero el scaffold con `dotnet ef migrations add FacturaVenta_MotivoTexto` (con `AppDbContext` ya editado) para obtener el `Designer.cs`/snapshot correctos del modelo destino automaticamente; el `Up()`/`Down()` auto-generado hacia un `AlterColumn` directo `int→varchar` (cast numerico, ej. `1→"1"`, perdida de dato semantico) y se **reemplazo a mano** por las 3 fases con backfill textual antes de dar la migracion por cerrada. El snapshot y el `.Designer.cs` finales SI reflejan el modelo destino correcto (`Motivo` string(200) NOT NULL), confirmado por inspeccion.

**Impacto:** sistema en produccion con `FacturasVenta.Motivo` ya cargado como `int` (1/2/3). Se recomienda correr primero contra copia de desarrollo/staging antes de produccion (buena practica general), no requiere el nivel de validacion obligatoria de RT9 (v11) por tratarse de un mapeo cerrado sin ambiguedad.

### 5. Evidencia de build
- `dotnet build` (`Ganaderia.slnx`, Debug) → **Compilacion correcta. 0 Errores** (9 advertencias, todas preexistentes: `NU1902` MailKit/MimeKit y `CS0114` en `HomeController`, no relacionadas con este cambio).
- `dotnet ef migrations add FacturaVenta_MotivoTexto ...` → generado correctamente (advertencia esperada "may result in loss of data" del scaffold automatico, corregida a mano reescribiendo `Up()`/`Down()`).
- `dotnet ef migrations list` → confirma `20260702210025_FacturaVenta_MotivoTexto` como ultima migracion de la cadena, inmediatamente despues de `20260702181125_EgresoPago_PagosMultiples` (v11).
- No se aplico la migracion contra ninguna base de datos (dev ni produccion) en esta sesion (sin conexion disponible en este entorno).

### 6. Riesgos y supuestos
- **RT13** (arquitectura §15.3): riesgo bajo, mapeo 1:1 sin ambiguedad; igual se recomienda correr primero contra staging antes de produccion.
- **RD9**: cubierto — no quedo codigo muerto del `<datalist>`/fetch viejo (verificado con `grep -rn "datalist"` sobre `Ganaderia.Web/Views`, sin resultados).
- **RD10** (heredado del diseño, no accionable en esta iteracion): `Motivo` como texto libre pierde la garantia de lista cerrada para agrupar/reportar; no hay uso actual de ese tipo en Dashboard ni reglas de negocio (confirmado, analisis v12 S37/R28).
- Supuesto propio: el mensaje de error de servidor para `Motivo` vacio/largo ("Motivo obligatorio." / "Motivo no puede superar 200 caracteres.") no estaba especificado textualmente en el diseño; se redacto siguiendo el estilo de los mensajes existentes en `FacturaVentaService.ValidarInput`.

### 7. Decisiones de diseño no 100% especificadas
- El endpoint `SugerenciasMotivo` se agrego directamente en `FacturasController` (no una interfaz `IFacturaVentaSugerenciasService` separada) — diseño v3 §8.2 dejaba ambas opciones abiertas ("...o interfaz nueva... si el diseño arquitectonico prefiere separarlo"); arquitectura v3 §15.2 no separa el metodo, asi que se siguio la arquitectura (metodo dentro de `IFacturaVentaService`, misma decision que prevalecio en el documento con prioridad explicita).
- El `<select>` de Select2 se inicializa con una unica `<option>` preseleccionada (valor actual del modelo) tanto en `Egresos/Create` como en `Facturas/Create` (relevante para `Facturas/Edit`, que reusa la vista `Create`) — necesario para que Select2 muestre el valor existente al editar sin depender de una llamada AJAX previa; no explicitado en el diseño pero es el patron estandar de Select2 con `ajax` + valor inicial.
- Se aplico `.Trim()` a `Motivo` en el Service (alta y edicion), simetrico a `Egreso.Detalle.Trim()` — no explicitado puntualmente para Motivo en diseño/arquitectura v3, pero es coherente con el "mismo patron" pedido explicitamente para normalizacion (trim + case-insensitive, S36).

### 8. Pruebas minimas requeridas para QA
**PF62–PF66** (analisis v12 §16): Select2 con coincidencias muestra desplegable y carga valor al seleccionar (Egresos); Select2 admite valor nuevo sin coincidencias (Egresos); Motivo sugiere valores previos (Facturas); Motivo acepta valor nuevo no limitado a los 3 historicos (Facturas); facturas historicas muestran su Motivo original tras la migracion sin perdida de dato.
**PV17–PV18**: Motivo vacio bloqueado (Required); Motivo > 200 caracteres bloqueado (StringLength).

Notas para QA:
- PF66 (preservacion de datos historicos post-migracion) requiere aplicar la migracion contra una copia de la base de produccion real y verificar los 3 valores mapeados (`1→Faena`, `2→Vacía`, `3→Enfermedad`) — no ejecutable en este entorno sin conexion a MySQL.
- Falta smoke test manual en navegador real de ambos Select2 (Playwright o similar) — arquitectura §15.5 lo marca como paso explicito antes de cerrar QA, dada la experiencia del bugfix post-v11 con el `<datalist>` (`6-qa.md` §12.4). No ejecutado en esta sesion por no correr la app.
- Verificar tambien `Facturas/Edit` (reusa la vista `Create`): el Select2 de Motivo debe mostrar el valor existente preseleccionado al entrar a editar una factura.

### 9. Checklist de salida para merge (v12)
- [x] `MotivoVenta` enum eliminado del Domain, sin referencias colgantes (`grep -rn "MotivoVenta"` limpio salvo comentario explicativo).
- [x] `FacturaVenta.Motivo` es `string(200)` NOT NULL en la configuracion EF (snapshot y Designer.cs confirmados), con backfill definido en la migracion (no ejecutado contra datos reales en esta sesion).
- [x] `IFacturaVentaService.SugerenciasMotivoAsync` implementado, calcado de `SugerenciasDetalleAsync`.
- [x] `FacturasController.SugerenciasMotivo` accion nueva, mismo contrato JSON que `Egresos/SugerenciasDetalle`.
- [x] Select2 inicializado en `Egresos/Create` y `Facturas/Create` via `ov-autocomplete-select2.js`, sin codigo muerto del `<datalist>`/fetch anterior.
- [x] `dotnet build` OK, 0 errores.
- [ ] Migracion **ejecutada y validada contra copia de staging/produccion** — pendiente, responsabilidad del despliegue.
- [ ] Smoke test de navegador real del autocomplete en ambas pantallas — pendiente, fuera del alcance de esta sesion (no se corrio la app).
- [ ] Pruebas funcionales PF62–PF66 + PV17–PV18 ejecutadas por QA — pendiente.
- [x] `ganaderia - fausto` no tocado (ningun archivo fuera de `ganaderia - emo` fue leido ni escrito en esta sesion).

---

## Iteracion v13 — Entrega de mejoras post-reunion con cliente (2026-07-23)

Repositorio exclusivo: `C:\Sistemas\ganaderia - emo`. Analisis funcional previo en el repo del proyecto: `C:\Sistemas\ganaderia - emo\docs\ganaderia\definiciones\6-analisis-mejoras-entrega2.md` (fecha de analisis 2026-07-22, mergeado aca el 2026-07-23 durante el barrido de memorias cross-proyecto — ver `trazabilidad.md`).

### Alcance funcional entregado

1. **Fix bug transversal de formularios**: `asp-items` sin `asp-for` en grillas dinamicas indexadas (`Views/Egresos/_FilaPago.cshtml` combo `FormaDePago`, `Views/Facturas/Create.cshtml` combo `Items[i].GrupoId`) causaba que el combo visual se reseteara a la primera opcion tras un POST invalido, aunque el dato server-side estuviera intacto (los controllers ya recargaban `SelectList` y hacian `return View(vm)` correctamente — el bug era puramente de Razor no marcando `selected` en grillas indexadas sin `asp-for`). Confirmado por grep que estos eran los **unicos 2 casos** en toda la app; el resto de combos usa `asp-for` y no tiene el bug. Caso aparte no arreglable: `<input type="file">` del comprobante nunca puede repoblarse tras un POST fallido (limitacion de navegador, no bug de codigo).
2. **Fila de totales en listados** (`Egresos/Index` y `Facturas/Index`): suma de `Importe`/`Total` sobre el filtro aplicado, calculada server-side. Mecanismo nuevo y reutilizable `data-dt-sum-cols` agregado a `datatables-defaults.js`.
3. **Rename end-to-end `FacturaVentaCuota`/`Cuotas` → `FacturaVentaIngreso`/`Ingresos`**: entidad, enum `EstadoCuota`→`EstadoIngreso` (de paso alinea genero gramatical: Acreditada/Rechazada → Acreditado/Rechazado, igual que `EstadoPagoEgreso`), FK `MovimientoCaja.FacturaCuotaId`→`FacturaIngresoId`, tabla `FacturaVentaCuotas`→`FacturaVentaIngresos` (`RENAME TABLE`, metadata-only en MySQL/InnoDB), `ICuotaService`/`CuotaService`→`IIngresoService`/`IngresoService`, `CuotasController`→`IngresosController` (ruta `/Cuotas`→`/Ingresos`), vistas `Views/Cuotas/*`→`Views/Ingresos/*`, link de menu. Migracion **`RenameCuotaToIngreso`** (Option B, no destructiva, mismo patron que `RenameFacturaToFacturaVenta` del refactor de Etapa 8). Motivo: el cliente senalo que "Cuotas" (cobro de Factura de venta) se confunde con las cuotas/pagos de un Egreso — la estructura de fondo ya era simetrica con `EgresoPago` (el propio codigo ya documentaba `EgresoPagosController.cs:10` como *"Simetrico a CuotasController"*), solo hacia falta renombrar, no rediseñar. Redaccion acordada: "Ingresos" es el nombre del modulo/entidad/menu (donde ocurre la confusion real); "cuota" se mantiene como palabra descriptiva dentro del detalle de una factura puntual ("Cuota 1 de 3"), donde el contexto ya es inequivoco.
4. **Dashboard dividido en dos pantallas**:
   - `/Dashboard` (control de **stock puro**, sin plata): nuevo filtro Mes+Año (default mes/año actual). Tabla "Actividad de hacienda por grupo" del periodo filtrado: Nacimientos, Muertes, Compras, Vendidas (cabezas), **Kg vendidos** y **precio promedio ponderado por kg** (`Σ(KilosTotales·PrecioPorKilo) / Σ(KilosTotales)` del periodo — no promedio simple, para que una venta grande pese mas que una chica), Stock al cierre del periodo. Se mantiene la tabla de stock vivo actual (foto del presente, no depende del filtro). Se quitan las 4 cards de plata (pasan al Tablero Anual).
   - `/Dashboard/TableroAnual` (control de **dinero puro**, sin cabezas): filtro Año (ya existia) + nuevo filtro Mes con opcion "Todos". KPIs de plata: Saldo de caja (antes oculto tras `Features:Etapa2`, ahora **siempre visible** en este tablero), Ingresos, Egresos, Resultado neto. Cambio de KPI: "Cuotas acreditadas"/"Pagos egreso acreditados" reemplazados por **Ingresos pendientes** (cantidad+monto) y **Pagos de egreso pendientes** (cantidad+monto — nuevo, mismo calculo que ingresos pendientes pero sobre `EgresoPagos.Estado=Pendiente`). Se quita la tabla/grafico de actividad de hacienda (pasa al Dashboard).
   - Sin migracion EF para este punto: todo el dato fuente (`MovimientoStock`, `FacturaVentaItem`, `MovimientoCaja`, `EgresoPago`) ya existia.
   - Sugerencias para dashboards futuros (no implementadas, quedan para priorizar con el cliente): flujo de caja proyectado 30/60/90 dias, cheques a vencer/depositar, evolucion del precio promedio por kg, peso promedio por cabeza vendida, egresos por rubro, composicion de stock por categoria.
5. **Facturas de venta — impuestos y cuotas 100% editables**:
   - `TasaIva` (enum cerrado 0/10,5/21/27% sobre `Subtotal` completo, no editable) reemplazado por 3 pares %+importe **independientes y editables** (IVA, Ingresos Brutos, Otras Percepciones), sincronizados en tiempo real client-side ("ultimo tocado manda"). Bases de calculo: IVA sobre `Subtotal` (sin cambios); IIBB y Otras Percepciones sobre `Subtotal + MontoIva` cada una (no se calculan una sobre la otra, evita circularidad). `Total = Subtotal + MontoIva + MontoIIBB + MontoOtrasPercepciones`. El enum `TasaImpuesto` se mantiene solo como preset de UI (botones de acceso rapido 0/10,5/21/27 que auto-completan el campo decimal), no como tipo de columna.
   - Ingresos (ex-Cuotas) pasan de generacion 100% automatica por `Plazo` (reparto uniforme, vencimientos multiplos de 30 dias) a **grilla editable**: fecha e importe libres por linea, cantidad libre. El campo `Plazo` pasa a ser un helper de UI ("generar sugerido" que prellena con la logica vieja como punto de partida editable), deja de ser fuente de verdad. Validacion server-side: al menos 1 ingreso, todos los importes > 0, todas las fechas cargadas, `Σ Importe == Total` con tolerancia de redondeo de **$0,01 por ingreso** (ajustable si resulta muy estricta/laxa en la practica). `EditAsync` deja de regenerar automaticamente: recibe la lista editada igual que `CreateAsync`.
   - Migracion **`FacturaVenta_ImpuestosEditables`** (no destructiva): puebla `MontoIva`/`PorcentajeIva` desde las columnas viejas `Iva`/`TasaIva` antes de borrarlas. La migracion scaffoldeada por defecto de EF hacia un `RenameColumn` **incorrecto** que hubiera asignado los montos de IVA historicos a la columna de Otras Percepciones — se reescribio a mano para evitar la perdida/corrupcion de datos historicos.
6. **Correccion sobre el analisis original**: el punto "Caja: campo `Estado` redundante" (propuesto inicialmente) se **descarto** tras revisar `CuotaService`/`EgresoPagoService` con mas profundidad — `MovimientoCaja.Estado` si varia (rechazar muta el movimiento a `Pendiente` sin borrarlo, para preservar trazabilidad; regularizar "Error de carga" lo vuelve a `Acreditado`; regularizar "Cobro posterior" deja el original `Pendiente` y crea uno nuevo `Acreditado`). No era dead code — el analisis inicial solo habia grepeado los sitios de creacion (`new MovimientoCaja{...}`), no las mutaciones sobre movimientos existentes. Leccion de proceso: verificar mutaciones ademas de creaciones antes de descartar un campo como redundante.

### Evidencia de build y migraciones

- ✅ `dotnet build` sin errores en cada etapa intermedia y al cierre.
- ✅ `dotnet ef database update` — ambas migraciones (`RenameCuotaToIngreso`, `FacturaVenta_ImpuestosEditables`) aplicadas contra `ganaderia_dev` real, con verificacion de "no pending model changes" tras cada una (migracion vacia de prueba generada y removida).
- ⏳ Smoke test manual end-to-end (factura con impuestos/ingresos personalizados, dashboard con filtros, tablero anual) — pendiente en QA.
- ⏳ `docs/qa/plan-qa-etapa7.md` (local al repo del proyecto) — pendiente de extender con casos de esta entrega.

### ⚠️ Riesgo operativo abierto — migraciones aplicadas en produccion SIN backup previo

**Las 4 migraciones pendientes (`FacturaVenta_MotivoTexto`, `AgregarReferenciaEgresoPago`, `RenameCuotaToIngreso`, `FacturaVenta_ImpuestosEditables`) ya fueron aplicadas contra la base de datos de PRODUCCION el 2026-07-23** (script acumulado `migration-prod-20260723-1200.sql`, aplicado via `dotnet ef database update` directo), **sin backup previo** — `mysqldump`/`mysql` CLI no estaban disponibles en el entorno de esa sesion. El cliente acepto explicitamente el riesgo. **El deploy del codigo nuevo (Web Deploy) todavia esta pendiente**: la base de prod ya tiene el esquema nuevo pero la app publicada todavia corre el codigo viejo — inconsistencia activa hasta completar el deploy. Accion de seguimiento: (1) programar backup manual de la base de prod cuanto antes aunque las migraciones ya se hayan aplicado (mitiga riesgo hacia adelante), (2) completar el deploy del codigo lo antes posible para cerrar la ventana de inconsistencia esquema/codigo, (3) evaluar instalar `mysql-client`/`mysqldump` en el entorno de despliegue para que este riesgo no se repita en la proxima entrega.

### Riesgos y supuestos

- Tolerancia de redondeo `Σ ingresos == Total`: $0,01 por ingreso — ajustable.
- Flag `Features:Etapa2` (hoy `true` en produccion) no se toco; sigue ocultando Caja/Tablero Anual si se desactivara. Pregunta abierta con el cliente: ¿eliminar el flag ya que se considera funcionalidad estable, o mantenerlo?
- Herramientas adicionales de dashboard (flujo de caja proyectado, cheques a vencer, etc.) quedaron sin implementar — sugerencias opcionales, no pedido explicito.

### Checklist de salida (estado al cierre de esta iteracion)

- [x] Build verde en cada paso.
- [x] Sin referencias residuales a `Cuota`/`FacturaVentaCuota`/`EstadoCuota`/`TasaImpuesto`/`CalculoIvaHelper` en codigo activo (verificado por grep; solo quedan en migraciones historicas).
- [x] Migraciones con `Up()`/`Down()` simetricos y no destructivos, validadas contra base real (dev).
- [x] Manual de usuario del proyecto (`ganaderia - emo/docs/ganaderia/manual-usuario.md`) actualizado: seccion Ingresos, Facturas de venta (impuestos e ingresos editables).
- [x] Migraciones aplicadas en produccion (ver riesgo operativo arriba — sin backup previo).
- [ ] Deploy del codigo nuevo a produccion (Web Deploy) — **pendiente, prioridad alta** (base ya migrada, app todavia vieja).
- [ ] Smoke test manual end-to-end en QA/prod.
- [ ] Extender el plan de QA local del proyecto con casos de esta entrega (impuestos editables, ingresos personalizados, filtros de dashboard).
