# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

> Nota: la documentacion detallada por feature vive en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\`. Este archivo registra el log cronologico de alto nivel.

### 2026-05-22 - implementador
- Etapa: Implementacion — Mejoras varias (pedidos y compras)
- Cambio: ajuste en `PedidoService`; `ComprasController` y `PedidosController` con nuevas acciones; vistas `Compras/Detalle.cshtml` y `Pedidos/Detalle.cshtml` expandidas (~75 lineas nuevas cada una). Adicion de `.github/copilot-instructions.md` al repositorio del sistema.
- Motivo: correcciones y mejoras post-entrega solicitadas por el cliente.
- Impacto en capas: Infrastructure (service), Presentacion (controllers + vistas).
- Riesgos/supuestos: sin migracion EF. Build OK.

### 2026-05-18 - implementador
- Etapa: Implementacion — Baja de pedidos (soft delete)
- Cambio: `IPedidoService` + `PedidoService` con `EliminarAsync`; `PedidosController` con accion Delete; vistas `Index.cshtml` y `Detalle.cshtml` actualizadas con boton de baja. Regla: solo pedidos en estado Borrador o Cancelado, sin pagos activos, sin compra avanzada, sin concesion activa.
- Motivo: cliente necesitaba poder eliminar pedidos erroneos en estados tempranos.
- Impacto en capas: Application (interface), Infrastructure (service), Presentacion (controller + vistas).
- Riesgos/supuestos: soft delete via `DeletedAt`. Sin migracion EF. Build OK.

### 2026-05-15 - implementador
- Etapa: Implementacion — Feature Reversion estados pedido (ajuste final)
- Cambio: `ReversionDtos.cs` actualizado; `PedidosController` y `PedidoService` ajustados; `Detalle.cshtml` actualizado con card de reversion y tabla de historial.
- Motivo: completar la integracion Web del feature de reversion (Fases 1 y 2) incluyendo politica `RequireRevertirPedido`.
- Impacto en capas: Application (DTOs), Infrastructure (service), Presentacion (controller + vista).
- Riesgos/supuestos: migracion `AddReversionPedidoYHistorial` pendiente de aplicar en produccion.

### 2026-05-14 - implementador + documentador
- Etapa: Implementacion — Concesiones recibidas UI + ExportService + Dashboard + deploy produccion
- Cambio: `StockController`, `ConcesionesRecibidasController` y vistas completadas. `ReporteService` + `IReporteService` + `DashboardViewModel` + vista `Home/Index` actualizados. `ExportService` e `IExportService` implementados. Scripts SQL idempotentes generados y aplicados en produccion (`olvidatasoft-002-site6`). Manual de usuario actualizado.
- Motivo: completar UI del modulo Concesiones Recibidas del Proveedor y hacer deploy del ciclo Mayo.
- Impacto en capas: todas.
- Riesgos/supuestos: migration `AddConcesionesRecibidasProveedor` aplicada en produccion.

### 2026-05-13 - implementador + qa
- Etapa: Implementacion + QA — Concesiones recibidas del proveedor (dominio + servicios + QA)
- Cambio: entidades `ConcesionRecibidaProveedor`, `ConcesionRecibidaProveedorItem`, `MovimientoConcesionRecibida`; enums `EstadoConcesionRecibida`, `TipoMovimientoConcesion`. `ConcesionRecibidaService` con FIFO/LIFO, maquina de estados completa, liquidacion automatica. Migracion `AddConcesionesRecibidasProveedor` generada. QA formal completado: 10/10 criterios de aceptacion PASS (1 parcial DEF-003). Catalogo de regresiones `regresiones-manuales.yml` actualizado. Reporte `DeudaProveedor` con badge Concesion.
- Motivo: nuevo modulo funcional solicitado por el cliente para gestionar mercaderia recibida en consignacion de proveedores.
- Impacto en capas: todas.
- Riesgos/supuestos: DEF-003 pendiente (boton pago bloqueado en compra espejo de concesion CerradaManual).

### 2026-05-12 - implementador
- Etapa: Implementacion — Descuento % en costo de items de compra
- Cambio: `PedidoItem.DescuentoPorcentajeCosto` nuevo campo. Migracion `AddDescuentoPorcentajeCostoPedidoItem`. `ComprasController.ActualizarCostosItem` con politica `RequireAdministracion`. Vista `Compras/Detalle` con inputs editables por fila y recalculo JS.
- Motivo: paridad de edicion de costos entre Pedidos y Compras/Detalle.
- Impacto en capas: Domain, Infrastructure (EF + service), Presentacion.
- Riesgos/supuestos: migracion aplicada local; pendiente produccion (incluida en deploy 2026-05-14).

### 2026-05-09 - implementador
- Etapa: Implementacion — Descuento % en items de pedido
- Cambio: migracion `AddDescuentoPorcentajePedidoItem` generada y aplicada. Script SQL `20260509_AddDescuentoPorcentajePedidoItem.sql` para produccion. Script de limpieza de datos de prueba `20260509_TruncatePedidosYCompras_PROD.sql` generado.
- Motivo: incorporar campo de descuento porcentual por item en pedidos.
- Impacto en capas: Domain, Infrastructure.
- Riesgos/supuestos: script de limpieza requiere aprobacion previa a ejecucion en produccion.

### 2026-04-27 - implementador
- Etapa: Implementacion — Reversion de estados de pedido Fase 1 + Fase 2
- Cambio: `HistorialEstadoPedido` entidad nueva. `Pedido` con campos de auditoria de reversion + `RowVersion`. `IPedidoService` ampliado con `RevertirFinalizacionConcesionAsync`, `RevertirCancelacionAsync`, `GetHistorialAsync`. Migracion `AddReversionPedidoYHistorial`. Politica `RequireRevertirPedido` en `Program.cs`. Endpoints y vista `Detalle.cshtml` con modales de confirmacion y tabla de historial. Compensaciones contables via `MovimientoCC` con prefijo [Reversion] (no destructivas). Re-reserva de stock propio al revertir.
- Motivo: cliente necesitaba revertir concesiones finalizadas y cancelaciones por error.
- Impacto en capas: todas.
- Riesgos/supuestos: build OK. Migracion aplicada local, pendiente produccion.

### 2026-04-25 - implementador
- Etapa: Implementacion — Reversion a Borrador + edicion post-confirmacion con propagacion a compra
- Cambio: `PedidoService.VolverABorradorAsync` idempotente. Edicion de items en estado Confirmado/EnPreparacion propaga `TotalCostoSnapshot` a la compra vinculada. Cancelacion desvincula items y si la compra queda vacia vuelve a Borrador.
- Motivo: pedido del cliente (Fase 2 de reversiones).
- Impacto en capas: Infrastructure (service), Presentacion (controller + vista).
- Riesgos/supuestos: concurrencia resuelta por revalidacion transaccional (sin `RowVersion` en `Pedido`).

### 2026-04-24 - implementador
- Etapa: Implementacion — Stock propio (5 etapas completadas)
- Cambio: `ProductoPropio` entidad nueva. `PedidoItem` con dual origen (provider/propio). `IStockPropioService` con reserva/devolucion/ajuste y concurrencia optimista. Integracion en `PedidoService.ConfirmarAsync` (reserva FIFO + split a proveedor). `StockController` + vistas CRUD. Autocomplete en pedidos acepta stock propio. Migracion `AddProductosPropiosYStock`.
- Motivo: cliente necesita manejar productos de inventario propio separados del catalogo de proveedores.
- Impacto en capas: todas.
- Riesgos/supuestos: `RowVersion` incrementado manualmente (MySQL no tiene rowversion nativo). Build OK.
