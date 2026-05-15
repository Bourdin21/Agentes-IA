# Memoria - Implementador

## Proyecto: vinosefue
## Ultima actualizacion: 2026-05-15

> Documento de referencia rapida. La memoria detallada por feature con cambios por capa, migraciones y checklists vive en:
> `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md`

---

## Features completadas (cronologia inversa)

### 2026-05-15 — Reversion estados pedido (ajuste Web final)
- `ReversionDtos.cs` actualizado; `PedidosController` endpoints `RevertirCancelacion` y `RevertirFinalizacionConcesion`; `Detalle.cshtml` con card de reversion, modales de confirmacion (motivo 15-500 + RowVersion), tabla de historial.
- Politica `RequireRevertirPedido` (SuperUsuario + Administrador).
- Build: OK. Migracion `AddReversionPedidoYHistorial` pendiente en produccion.

### 2026-05-14 — Concesiones recibidas UI + ExportService + Dashboard + deploy produccion
- `StockController` + views Stock/Index, Detalle, ConcesionesImpagas.
- `ConcesionesRecibidasController` + views Index, Detalle, Crear.
- `ReporteService` + `IReporteService` + dashboard `Home/Index` actualizado con KPIs y reporte `DeudaProveedor` (badge Concesion).
- `ExportService` e `IExportService` implementados.
- Deploy a produccion `olvidatasoft-002-site6`: scripts SQL idempotentes aplicados el 2026-05-14 12:02.
- Manual de usuario actualizado.

### 2026-05-13 — Modulo Concesion recibida del proveedor (dominio + servicios)
- Entidades: `ConcesionRecibidaProveedor`, `ConcesionRecibidaProveedorItem`, `MovimientoConcesionRecibida`.
- Enums: `EstadoConcesionRecibida` (Abierta/Liquidada/CerradaManual), `TipoMovimientoConcesion`.
- `ConcesionRecibidaService`: `CrearAsync`, `ListarAsync`, `GetAsync`, `CerrarManualAsync`, `ImputarConsumoFifoAsync`, `DevolverConsumoLifoAsync`, `RecalcularEstadoAsync`.
- Gancho en `CompraProveedorService.RegistrarPagoProveedorAsync` -> `RecalcularEstadoAsync`.
- Ganchos FIFO/LIFO en `PedidoService` (confirmar/cancelar/borrar/ajustar/revertir finalizacion).
- Migracion: `20260513182527_AddConcesionesRecibidasProveedor`.
- Numero secuencial `CON-######` via `GenerarNumeroSecuencialAsync`.
- `regresiones-manuales.yml` actualizado con nuevos REG items.

### 2026-05-12 — Descuento % costo en Compras/Detalle
- `PedidoItem.DescuentoPorcentajeCosto` (nuevo campo, precision 5,2, default 0).
- Migracion: `20260512214004_AddDescuentoPorcentajeCostoPedidoItem`.
- `ComprasController.ActualizarCostosItem` (solo Admin); recalculo JS en cliente.

### 2026-05-09 — Descuento % en items de pedido
- Migracion: `20260509232720_AddDescuentoPorcentajePedidoItem`.
- Scripts produccion generados.

### 2026-04-27 — Reversion de estados de pedido (Fases 1 y 2)
- `HistorialEstadoPedido` entidad nueva. `Pedido` con `RowVersion` + campos auditoria.
- `RevertirFinalizacionConcesionAsync` y `RevertirCancelacionAsync` con compensacion contable no destructiva.
- Migracion: `20260427152550_AddReversionPedidoYHistorial`.

### 2026-04-25 — Reversion a Borrador + edicion post-confirmacion
- `VolverABorradorAsync` idempotente (guarda: compra no Recibida).
- Edicion de items en Confirmado/EnPreparacion propaga snapshot a compra.

### 2026-04-24 — Stock propio (5 etapas)
- `ProductoPropio` entidad; `PedidoItem` dual origen.
- `IStockPropioService` con reserva/devolucion FIFO, split a proveedor, concurrencia optimista.
- `StockController` + vistas + autocomplete en pedidos.
- Migracion: `20260424211341_AddProductosPropiosYStock`.

---

## Migraciones EF (cronologia)

| Migracion | Fecha | Local | Produccion |
|---|---|---|---|
| `AddProductosPropiosYStock` | 2026-04-24 | aplicada | pendiente |
| `AddReversionPedidoYHistorial` | 2026-04-27 | aplicada | pendiente |
| `AddDescuentoPorcentajePedidoItem` | 2026-05-09 | aplicada | **aplicada 2026-05-14** |
| `AddReversionRecepcionCompraProveedor` | 2026-05-13 | aplicada | **aplicada 2026-05-14** |
| `AddConcesionesRecibidasProveedor` | 2026-05-13 | aplicada | **aplicada 2026-05-14** |
| `AddDescuentoPorcentajeCostoPedidoItem` | 2026-05-12 | aplicada | **aplicada 2026-05-14** |

---

## Riesgos residuales
- `AddReversionPedidoYHistorial` y `AddProductosPropiosYStock` **pendientes en produccion** (no incluidas en el deploy del 2026-05-14).
- DEF-003 abierto: boton "Registrar pago" no bloqueado en compra espejo de concesion `CerradaManual`.
- Tests automatizados del feature de reversion y stock propio pendientes.

## Proximos pasos
- Aplicar migraciones `AddReversionPedidoYHistorial` y `AddProductosPropiosYStock` en produccion.
- Cerrar DEF-003 (bloqueo UI compra espejo concesion CerradaManual).
- QA manual del feature reversion y stock propio.
