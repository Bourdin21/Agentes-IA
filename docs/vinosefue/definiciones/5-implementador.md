# Memoria - Implementador

## Proyecto: vinosefue
## Ultima actualizacion: 2026-05-22

> Documento de referencia rapida. La memoria detallada por feature con cambios por capa, migraciones y checklists vive en:
> `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md`

---

## Features completadas (cronologia inversa)

### 2026-07-03 (ajuste post-revision cliente, 3ra vuelta) — Simplificacion de Reportes/DeudaProveedor y Reportes/Riesgo
- Decision del cliente sobre el pendiente que QA marco (columna de pago al proveedor en $0 hardcodeado en ambos reportes): sacar esa dimension en vez de aproximarla, enlazando al ledger nuevo (`Proveedor/CuentaCorriente`) como fuente de verdad.
- **`Reportes/DeudaProveedor`**: pasa a ser listado puro de compras facturadas (Compra, Pedido(s), Cliente(s), Deuda Base, Fecha). Se sacaron `TotalPagadoProveedor`/`SaldoPendiente`/`EstadoPago` del DTO y el filtro `estadoPago` del controller/vista. Se agrego boton "Ver saldo real del proveedor" con link a `Proveedor/CuentaCorriente`.
- **`Reportes/Riesgo`**: se saco la clasificacion de 2 ejes con el proveedor (ya no calculable de forma confiable). **Redefinicion de "riesgo"** (sin inventar reglas nuevas no discutidas, siguiendo instruccion explicita del cliente de "dejarlo simple" ante la ambiguedad): pedido activo con saldo pendiente de cobro del cliente (`SaldoCliente > 0`). Se agrego el saldo GENERAL del proveedor como dato de contexto en la cabecera (tarjeta, no por fila), con link a `Proveedor/CuentaCorriente`. Se saco el filtro `tipoRiesgo` (sin opciones validas que ofrecer).
- Capas: Application (DTOs, interfaz), Infrastructure (`ReporteService`), Web (controller, viewmodels, 2 vistas reescritas + copy actualizado en `Reportes/Index.cshtml`). Sin cambios de Domain ni migraciones EF.
- Build OK. Smoke test runtime con datos reales: ambos reportes 200 OK, saldo del proveedor en la tarjeta de Riesgo coincide exactamente con `Proveedor/CuentaCorriente`.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Ajuste 2026-07-03 (mismo dia, 3ra vuelta)").

### 2026-07-03 (ajuste post-revision cliente) — Fix orfandad de items al cancelar/eliminar + recalculo de costo al editar cantidad
- El cliente reviso los riesgos residuales del feature de abajo y pidio corregir 2 antes de QA (no quedan como defecto catalogado).
- **Fix 1:** cancelar un Pedido o eliminar un item ahora chequea si el item esta vinculado a una Compra activa: si la Compra sigue en `Borrador`, se desvincula automaticamente y se recalcula el `TotalCostoSnapshot`; si ya esta `Generada` o posterior (facturada), se **bloquea** la cancelacion/eliminacion con mensaje claro ("Quitalo de la compra primero o contacta a administracion").
- **Fix 2:** el helper compartido `RecalcularSnapshotComprasVinculadasAsync` ahora solo actua si la Compra vinculada sigue en `Borrador` (antes recalculaba sin condicion); se agrego su uso en `ActualizarCantidadItemAsync`, `AgregarItemAsync` y `AgregarItemsBatchAsync` (ramas de merge de item existente).
- Unico archivo tocado: `PedidoService.cs` (sin cambios de Domain/Application/Web ni migraciones nuevas).
- Build OK. Probado en runtime contra datos de dev (con datos sinteticos temporales, revertidos al finalizar): bloqueo y desvinculacion verificados tanto para cancelar como para eliminar item, y recalculo de costo verificado para edicion de cantidad.
- 2 de los riesgos residuales del feature anterior quedan resueltos (ver detalle en memoria completa). El resto de riesgos residuales no cambia.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Ajuste 2026-07-03 (mismo dia, post-revision del cliente)").

### 2026-07-03 — Compras al proveedor: desacople total de Pedido + ledger unico de cuenta corriente del proveedor
- Vinculo Compra-Item pasa de nivel-Pedido a nivel-Item (`PedidoItem.CompraProveedorId`, FK directa). Se elimina `Pedido.CompraProveedorId`.
- Nueva entidad `MovimientoCCProveedor` + enum `OrigenTipoMovimientoProveedor` (Factura/NotaCredito/Pago); se elimina `PagoProveedor` y campos `TotalPagadoProveedor`/`SaldoPendienteProveedor`/`EstadoPagoProveedor` de `CompraProveedor`.
- Nuevas pantallas: `Compras/Crear` (armado manual de compra por item), `Proveedor/CuentaCorriente` (extracto ascendente con saldo acumulado, alta de Pago/NCR).
- `CompraProveedorService.CambiarEstadoAsync` ya no sincroniza estados con Pedido; postea Factura automatica en Borrador->Generada y la revierte al Cancelar (nunca genera NCR automatica).
- **Desvio documentado:** se generaron 2 migraciones EF (no 4 como pedia la arquitectura) por limitacion de tooling EF Core al generar diffs parciales; se preservo la misma propiedad de seguridad (aditivo -> verificar con script de datos -> destructivo).
- **Caso borde no contemplado en arquitectura:** el modulo "Concesion recibida del proveedor" (compra espejo) dependia de pago/deuda por compra individual — se resolvio manteniendo esos metodos con la misma firma pero reimplementados contra el ledger nuevo filtrado por CompraProveedorId.
- Build OK, 0 errores. Migraciones aplicadas y verificadas en local (conteos/sumas del backfill cuadran). Smoke test runtime OK (login + rutas clave + datos reales). Pendiente: aplicar en produccion (requiere aprobacion cliente) y QA funcional completo del flujo de escritura.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Compras al proveedor — desacople total de Pedido y ledger unico de cuenta corriente").

### 2026-05-22 — Mejoras varias (pedidos y compras)
- Ajuste en `PedidoService`; `ComprasController` y `PedidosController` con nuevas acciones.
- Vistas `Compras/Detalle.cshtml` y `Pedidos/Detalle.cshtml` expandidas con nueva funcionalidad.
- Adicion de `.github/copilot-instructions.md` al repositorio del sistema.
- Build: OK. Sin migracion EF.

### 2026-05-18 — Baja de pedidos (soft delete)
- `IPedidoService` + `PedidoService` con metodo `EliminarAsync`.
- `PedidosController` con accion Delete; vistas `Index.cshtml` y `Detalle.cshtml` con boton de baja.
- Reglas de negocio: solo Borrador o Cancelado, sin pagos activos, sin compra avanzada, sin concesion activa.
- Build: OK. Sin migracion EF.

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
| `AddCompraProveedorIdToPedidoItemAndLedger` | 2026-07-03 | aplicada | pendiente |
| `RemoveCompraProveedorIdFromPedidoAndPagoProveedor` | 2026-07-03 | aplicada | pendiente |

---

## Riesgos residuales
- `AddReversionPedidoYHistorial` y `AddProductosPropiosYStock` **pendientes en produccion** (no incluidas en el deploy del 2026-05-14).
- Las 2 migraciones del 2026-07-03 (lote "Compras al proveedor") **pendientes en produccion**: requieren correr en orden migracion 1 -> script de datos backfill -> verificar conteos -> migracion 2 (destructiva). Ver detalle en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md`.
- DEF-003 abierto: boton "Registrar pago" no bloqueado en compra espejo de concesion `CerradaManual`.
- Reportes `Reportes/DeudaProveedor` y `Reportes/Riesgo` quedan con columnas de pago al proveedor degradadas a $0 desde el 2026-07-03 (pago ya no es atribuible por compra/pedido individual) — candidatos a retirar o rediseñar en favor de `Proveedor/CuentaCorriente`.
- Tests automatizados del feature de reversion y stock propio pendientes.

## Proximos pasos
- Aplicar migraciones `AddReversionPedidoYHistorial` y `AddProductosPropiosYStock` en produccion.
- Aplicar en produccion el lote "Compras al proveedor — desacople y CC" (2 migraciones + script de datos, con aprobacion previa del cliente y backup).
- Cerrar DEF-003 (bloqueo UI compra espejo concesion CerradaManual).
- QA manual del feature reversion, stock propio, y del lote "Compras al proveedor" (especialmente el flujo de escritura: Crear compra, Agregar/Quitar item, Pagos/NCR).
