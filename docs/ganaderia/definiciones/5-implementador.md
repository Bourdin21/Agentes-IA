# Memoria - Implementador

## Proyecto: ganaderia
## Ultima actualizacion: 2026-04-22

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
