# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-04-22 17:58 - presupuestador
- Etapa: Presupuesto
- Cambio: se ejecuto la estimacion funcional del sistema ganaderia con WBS por modulos visibles, PERT por item, contingencia por tipo de modulo y autocorreccion contra historicos.
- Motivo: contar con una base presupuestaria trazable antes de implementacion.
- Impacto en capas: Presentacion, Negocio y Datos.
- Riesgos/supuestos: alcance estimado sobre analisis funcional v10, diseno funcional v1 y arquitectura tecnica v1; se contemplan 2 migraciones EF y reutilizacion de componentes ya resueltos de la solucion base.

### 2026-05-22 - deploy produccion
- Etapa: Cierre — deploy a produccion
- Cambio: sistema completo desplegado a produccion. Todas las etapas (0-6) implementadas. QA formal completado con defectos conocidos documentados.
- Motivo: primera version lista para uso productivo del cliente.
- Impacto en capas: todas.
- Riesgos/supuestos: 3 FAILs de QA conocidos no bloqueantes (§3.3, §5.7, §9). Defectos documentados en `6-qa.md`.

### 2026-05-07 - qa
- Etapa: 7 - QA integral
- Cambio: reporte QA generado sobre `1-analista-funcional.md` v10, `2-disenador-funcional.md` v1 y `5-implementador.md`. FAILs encontrados: §3.3 (cuotas enum libre en lugar de cerrado), §5.7 (unicidad Inicial por Grupo no validada), §9 (bandeja Novedades no implementada). Auto-fix aplicados: BUG-G-001 (bloqueo rechazo cuota Pendiente), BUG-G-003 (forma de pago real en regularizacion 3b).
- Motivo: validacion formal antes de deploy a produccion.
- Impacto en capas: Infrastructure (servicios corregidos).
- Riesgos/supuestos: 3 FAILs aceptados como deuda tecnica. Sistema considerado apto para produccion con esas limitaciones conocidas.

### 2026-05-07 - implementador
- Etapa: 5 - Egresos; 6 - Dashboard + usuarios + transversales
- Cambio: Etapa 5 — `EgresosController` + vistas CRUD + `IEgresoService`/`EgresoService` con comprobantes en `App_Data/`. Migraciones: `Egreso_FormaDePago`, `FacturaVenta_Comprobante`. Etapa 6 — `DashboardController` con KPIs anuales; `UsersController` (ABM usuarios); `NotificationsController`; `JobEjecucion` entidad + `AcreditacionCuotasHostedService` con tracking de ejecuciones. Migracion `JobEjecucion`. Renombrado `Factura` → `FacturaVenta` en toda la solucion (migracion + code).
- Motivo: completar modulos de egresos, dashboard y cierre de transversales del sistema.
- Impacto en capas: todas.
- Riesgos/supuestos: build OK. Sistema listo para QA integral.

### 2026-05-06 - implementador
- Etapa: 3 - Ventas + Facturas + Cuotas + Caja; 4 - Cuotas rechazo/regularizacion
- Cambio: `FacturasController` + `CuotasController` + `CajaController` con vistas completas. `IFacturaVentaService`/`FacturaVentaService`: creacion de facturas multi-item con IVA, numeracion correlativa `F-NNNNNN`, generacion automatica de cuotas (1/2/3 a 30/60/90 dias), comprobante PDF. `ICuotaService`/`CuotaService`: `AcreditarAsync`, `RechazarAsync`, `RegularizarAsync` (3a ErrorDeCarga + 3b CobroPosterior). `ICajaService`/`CajaService`: saldo = Σ movimientos Acreditados. Migraciones: `RenameFacturaToFacturaVenta`, `FacturaVenta_ItemKilosPrecioPorKilo_PlazoNullable`, `MovimientoCaja_DrillDownNav`.
- Motivo: implementar el nucleo de ingresos del sistema (ventas a compradores con facturacion y cuotas).
- Impacto en capas: todas.
- Riesgos/supuestos: `CajaController` marcado con `[Etapa2Only]` (diferido segun analisis funcional v10 §3.5).

### 2026-04-22 - implementador
- Etapa: 2 - Stock y movimientos + ABM catalogos UI
- Cambio: `StockController` con vistas Index, Detalle, CargaInicial, Movimientos; logica de stock calculado via `IStockService.GetStockAsync`. `GruposController`, `RubrosController`, `ProveedoresController` con CRUD completo. `MovimientoStock` tipos: Inicial, Nacimiento, Compra, Muerte, Venta, Compensacion. Migracion `Ganaderia_Etapa1_Catalogos_Operacion` aplicada.
- Motivo: dar acceso UI a los catalogos y permitir carga y consulta de stock ganadero.
- Impacto en capas: todas.
- Riesgos/supuestos: stock calculado dinamicamente (sin campo persitido), operaciones criticas en transaccion explicita.

### 2026-04-22 - implementador
- Etapa: 0 - Preparacion y fundaciones
- Cambio: creacion de estructura de carpetas Ganaderia en las 4 capas, alta de los 9 enums del dominio, constantes `RolesGanaderia` y `MatrizTransicionesCategoria`, y helpers Web `CalculoIvaHelper` y `FormatoCorrelativoHelper`.
- Motivo: dejar fundaciones tecnicas listas antes de modelar entidades y migraciones.
- Impacto en capas: Domain (enums + constantes), Web (helpers). Application e Infrastructure solo carpetas.
- Riesgos/supuestos: ninguno especifico de etapa. Solucion ya renombrada a `Ganaderia.*` y conexion `ganaderia_dev` configurada.