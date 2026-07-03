# Memoria - Disenador funcional

## Proyecto: vinosefue
## Ultima actualizacion: 2026-07-03

## Definiciones vigentes

### Alcance funcional resumido

Diseño del lote "Compras al proveedor — desacople y cuenta corriente" (5 items), sobre base de [1-analista-funcional.md](1-analista-funcional.md) aprobado. Cubre: ocultar stock propio en detalle de compra, reordenar listado de compras, armado manual de compra por artículo (con desacople total de estados Compra↔Pedido), y un extracto de cuenta corriente único del proveedor con alta manual de Pagos y Notas de Crédito.

**Nota de diseño importante:** el proveedor es único en el sistema (`ProveedorController.GetProveedorAsync()` no recibe id — singleton). El extracto de cuenta corriente NO necesita selector de proveedor, a diferencia del de Clientes.

### Flujos de pantalla acordados

**1. `Compras/Detalle` (ajuste, no pantalla nueva)**
- La tabla "Items" deja de incluir filas con `EsStockPropio == true`. Filtro se aplica en el service/controller, no solo visualmente (para que quede consistente si en el futuro se exporta o factura).
- Se agrega sección **"Pedidos de origen"** (reemplaza a `PedidosVinculados` actual, que hoy asume 1 pedido completo = 1 fila): por cada Pedido distinto entre los items de la compra, una fila con Nº pedido (link a `Pedidos/Detalle`), Cliente, Estado actual del pedido (badge, solo informativo — sin acción de cambio de estado desde acá), cantidad de items de ese pedido incluidos en esta compra.
- Si la compra está en estado `Borrador` o `Generada` (estados tempranos, editables): botones "Agregar items" (abre selector, ver pantalla 3) y, por fila de item, "Quitar de esta compra" (libera el item al pool disponible). En estados posteriores (`EnPreparacion`, `Recibida`, `Cancelada`) esas acciones no se muestran.

**2. `Compras/Index` (ajuste, no pantalla nueva)**
- Reordenar columnas de la tabla: **Fecha** pasa a ser la primera columna (antes de Número). Orden restante: Fecha, Número, Pedido(s), Cliente(s), Estado, Total Costo, Nota, Pago Prov., Acciones.
- El orden de filas ya es descendente por `FechaGeneracion` — sin cambios de backend en este punto.
- Botón **"Nueva Compra"** en el header de la vista (reemplaza al disparo automático). Lleva a la pantalla 3.
- El contador/alerta actual "Pedidos sueltos" (`PedidosSueltosCount`, línea 61 de `ComprasController.Index`) se redefine como **"Items disponibles para comprar"**: cuenta `PedidoItem` con `ProductoProveedorId != null`, de pedidos en estado `Confirmado` o posterior (a excepción de `Cancelado`), que no estén vinculados a ninguna Compra activa (no `Cancelada`). Reemplaza el concepto de "pedido suelto" (que asumía vínculo a nivel Pedido) por "item disponible" (coherente con el vínculo a nivel item). `ReconsolidarPedidosSueltosAsync` deja de tener sentido tal como está — se elimina o se re-significa como acceso directo a la pantalla 3 con filtro pre-aplicado (a definir con Arquitectura, no bloquea diseño).

**3. `Compras/Crear` (pantalla nueva)**
- Wireframe textual:
  ```
  [Nueva Compra al Proveedor]
  --------------------------------------------------------
  Filtros: [Cliente ▾] [Pedido Nº ...] [Producto ...] [Buscar]
  --------------------------------------------------------
  ☐ | Pedido    | Cliente        | Producto        | Cant. | Costo unit. | Subtotal
  ☐ | #4521     | Juan Pérez     | Malbec Reserva  | 2     | $1.341,36   | $2.682,72
  ☐ | #4521     | Juan Pérez     | Malbec Roble    | 3     | $... 
  ☐ | #4530     | María Gómez    | Cabernet        | 1     | $...
  --------------------------------------------------------
  Seleccionados: 2 items · Total estimado: $ X.XXX,XX
  [Observaciones (opcional)]
  [Cancelar]                                    [Crear Compra]
  ```
- Solo lista items **disponibles** (definición igual a la de la pantalla 2). Un item ya asignado a una Compra activa no aparece.
- Al confirmar, crea `CompraProveedor` en estado `Borrador`, vincula los items seleccionados, calcula `TotalCostoSnapshot` = suma de subtotales, y redirige a `Compras/Detalle` de la nueva compra.
- Reutiliza patrón visual de tabla + filtros ya usado en `Compras/Index` y `Reportes/DeudaProveedor` (`table-responsive`, `card`, filtros en `row g-2 align-items-end`).

**4. `Proveedor/CuentaCorriente` (pantalla nueva, análoga a `Reportes/CuentaCorriente.cshtml` de Cliente)**
- Sin selector de proveedor (es único). Filtro solo por rango de fechas (Desde/Hasta), igual patrón que la vista de Cliente.
- Resumen superior: 3 tarjetas — Total Debe (FAC), Total Haber (NCR + Pagos), Saldo actual (mismo estilo `border-danger`/`border-success` condicional que ya usa `CuentaCorriente.cshtml` de Cliente).
- Tabla cronológica **ascendente** por fecha (a diferencia del listado de Compras, que es descendente — son pantallas distintas con propósitos distintos: acá el saldo acumulado necesita leerse de arriba hacia abajo, igual que el extracto real adjuntado por el cliente): columnas Fecha, Hora, Detalle, Debe, Haber, Saldo.
  - "Detalle" se arma como texto: `"FAC - {NumeroCompra}"`, `"NCR - {Referencia}"`, `"Efectivo - Recibo N° {Referencia}"`, `"Transferencia - Recibo N° {Referencia}"` — igual formato al extracto real del proveedor.
  - Las filas `FAC` llevan link a `Compras/Detalle` de la compra que las originó (trazabilidad). Las filas de Pago/NCR no llevan link obligatorio a una compra.
- Botones de acción: **"Registrar Pago"** y **"Registrar Nota de Crédito"** (modales, SweetAlert2 o partial view + modal Bootstrap, a definir por Arquitectura/Implementación según patrón ya usado en `Compras/Detalle` para `RegistrarPagoProveedor`).
  - Modal Pago: Fecha, Método (Efectivo/Transferencia — reutiliza `MetodoPago`), Importe, Referencia (n° de recibo, texto libre), Adjunto opcional.
  - Modal Nota de Crédito: Fecha, Importe, Referencia/Motivo (texto libre).
- Edición/anulación de un movimiento manual (Pago o NCR): mismo criterio que hoy tiene `PagoProveedor` (editable/eliminable solo si no está en un estado de cierre — a confirmar rango con Arquitectura), soft delete, recalculo de saldo.

### ViewModels definidos

- **`CompraProveedorItemDisponibleViewModel`**: `PedidoItemId`, `PedidoId`, `PedidoNumero`, `ClienteNombre`, `Sku`, `Nombre`, `Cantidad`, `PrecioUnitCosto`, `DescuentoPorcentajeCosto`, `SubtotalCosto`.
- **`CrearCompraProveedorViewModel`**: `ItemsDisponibles: List<CompraProveedorItemDisponibleViewModel>`, `ItemIdsSeleccionados: List<int>` (validación: mínimo 1), `Observaciones` (opcional, max 500), filtros de búsqueda (`ClienteId?`, `PedidoNumero?`, `Producto?`).
- **`CompraProveedorDetalleViewModel`** (ajuste sobre el actual): se quita el filtrado de `EsStockPropio` de `Items`; se agrega `PedidosOrigen: List<CompraPedidoOrigenViewModel>` (`PedidoId`, `PedidoNumero`, `ClienteNombre`, `EstadoOperativo`, `CantidadItemsEnEstaCompra`); se agrega `PuedeEditarItems: bool` (true si `Estado` en `Borrador`/`Generada`).
- **`MovimientoCCProveedorViewModel`**: `Fecha` (DateTime completo, para separar Fecha/Hora en la vista), `TipoOrigen` (enum: `Factura`, `NotaCredito`, `PagoEfectivo`, `PagoTransferencia`, `PagoOtro`), `Detalle` (string ya formateado), `Debe`, `Haber`, `SaldoAcumulado`, `CompraProveedorId?` (nullable, para el link cuando `TipoOrigen == Factura`).
- **`ReporteCuentaCorrienteProveedorViewModel`**: `FechaDesde?`, `FechaHasta?`, `TotalDebe`, `TotalHaber`, `Saldo`, `Items: List<MovimientoCCProveedorViewModel>`, `Page`, `TotalPages`, `TotalCount`.
- **`RegistrarPagoProveedorGeneralViewModel`**: `Fecha` (requerido, no futura), `Importe` (requerido, > 0), `MetodoPago` (Efectivo/Transferencia — reutiliza enum existente), `Referencia` (opcional, max 100), `Adjunto` (`IFormFile?`, mismas extensiones/tamaño permitidos que hoy: pdf/jpg/jpeg/png/webp, 10 MB).
- **`RegistrarNotaCreditoProveedorViewModel`**: `Fecha` (requerido, no futura), `Importe` (requerido, > 0), `Referencia` (opcional, max 200 — motivo/nº de nota).

### Validaciones de UI acordadas

- `CrearCompraProveedorViewModel.ItemIdsSeleccionados`: al menos 1 item seleccionado, todos deben seguir "disponibles" al momento de confirmar (revalidar server-side por concurrencia: si otro usuario ya lo tomó, mostrar error puntual con SweetAlert2 y refrescar la lista).
- Importe de Pago/NCR: > 0, hasta 2 decimales, sin tope superior salvo el que ya exista en el sistema para otros importes monetarios.
- Fecha de Pago/NCR: no puede ser futura (igual criterio que otras fechas de movimiento del sistema).
- Adjunto: mismas reglas ya vigentes (`ExtensionesPermitidas`, `MaxFileSize` de `ComprasController`).
- Al intentar "Quitar item" de una compra en estado no editable (`EnPreparacion`/`Recibida`/`Cancelada`), la acción no se muestra (regla de UI, no solo validación de servidor).

### Contratos funcionales para Services

- `ICompraProveedorService`:
  - `GetItemsDisponiblesAsync(filtros)` → reemplaza el rol de "pedidos sueltos"; devuelve `PedidoItem` de origen proveedor sin Compra activa vinculada.
  - `CrearCompraManualAsync(proveedorId, itemIds, observaciones, usuarioId)` → reemplaza a `GetOrCreateCompraBorradorInternalAsync` (que dejará de dispararse desde `PedidoService`).
  - `AgregarItemsAsync(compraId, itemIds)` / `QuitarItemAsync(compraId, itemId)` — solo en estados tempranos.
  - `CambiarEstadoAsync(...)` — se simplifica: deja de tocar `Pedido.EstadoOperativo` en cualquier transición.
- `IPedidoService.ConfirmarAsync`: deja de invocar la creación/vinculación automática de Compra (`PedidoService.cs:797-811`). El split automático por faltante de stock propio (reserva contra catálogo proveedor) se mantiene igual — el item resultante simplemente queda disponible en el pool para una futura compra manual.
- Nuevo `ICuentaCorrienteProveedorService` (o método agregado a `ICompraProveedorService`, a resolver en Arquitectura):
  - `GetExtractoAsync(desde?, hasta?, page, pageSize)` → arma la lista de movimientos + saldo acumulado.
  - `RegistrarFacturaAsync(compraId)` → invocado automáticamente cuando una Compra pasa a un estado "facturable" (a definir con Arquitectura: ¿al crearla, o al confirmarla/subir nota de pedido?).
  - `RegistrarPagoAsync(pagoViewModel)` / `RegistrarNotaCreditoAsync(ncrViewModel)` → alta manual, sin `CompraProveedorId` obligatorio.
  - `EditarMovimientoManualAsync` / `EliminarMovimientoManualAsync` (soft delete) — solo para movimientos de origen Pago/NCR, nunca para movimientos de origen Factura (esos solo se anulan cancelando la Compra que los generó).

## Máquina de estados

### `Pedido.EstadoOperativo` — cambio de diseño: sin disparadores desde Compra

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Confirmado | Cambio manual por usuario | EnPreparacion / Cancelado / etc. | — (sin cambios respecto a hoy) | — | — |
| (cualquiera) | Cambio de estado de una Compra vinculada | **sin efecto** | N/A | N/A | N/A (comportamiento eliminado, antes disparaba transición automática en `CambiarEstadoAsync` líneas 420-493) |

### `CompraProveedor.Estado` — transiciones ya no propagan a Pedido

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| (sin compra) | Usuario crea compra seleccionando ≥1 item disponible | Borrador | items pertenecen a pedidos Confirmado+ y no están en otra compra activa | Vincula items, calcula `TotalCostoSnapshot` | "El item ya fue incluido en otra compra" si perdió disponibilidad por concurrencia |
| Borrador | Usuario agrega/quita items | Borrador | compra no cancelada | Recalcula `TotalCostoSnapshot` | — |
| Borrador | Usuario confirma armado / sube nota de pedido | Generada o EnPreparacion (a definir con Arquitectura si se mantienen ambos pasos) | ≥1 item vinculado | Bloquea edición de items; genera movimiento Débito (FAC) en cuenta corriente proveedor | "La compra no tiene items" |
| Generada/EnPreparacion | Usuario marca Recibida | Recibida | — | Sin efecto sobre `Pedido` (antes: Entregado automático) | — |
| Recibida | Usuario revierte recepción | EnPreparacion | motivo 15-500 chars (igual que hoy) | Sin efecto sobre `Pedido` | — |
| Borrador/Generada/EnPreparacion | Usuario cancela | Cancelada | — | Libera los items (vuelven al pool disponible); NO reactiva ni cambia el Pedido; si ya generó FAC, se debe anular/compensar el movimiento en la cuenta corriente (a definir con Arquitectura: reversa o nota de crédito automática) | — |

### Movimientos de cuenta corriente proveedor (`MovimientoCCProveedor`, nuevo)

| Estado/Evento | Origen | Efecto en saldo | Guarda |
|---|---|---|---|
| Alta automática | Compra pasa a estado facturable | Debe += DeudaBase de la compra | 1 solo movimiento FAC por compra (no duplicar si cambia de estado varias veces) |
| Alta manual | Usuario registra Nota de Crédito | Haber += Importe | Importe > 0 |
| Alta manual | Usuario registra Pago (Efectivo/Transferencia) | Haber += Importe | Importe > 0 |
| Baja lógica | Usuario anula Pago/NCR propio | revierte el Haber correspondiente | Solo movimientos de origen Pago/NCR |

## Reglas de negocio y permisos por pantalla

- Todas las pantallas nuevas/ajustadas (`Compras/*`, `Proveedor/CuentaCorriente`) mantienen la policy actual `RequireAdministracion` (sin cambios de permisos).
- Un `PedidoItem` no puede estar vinculado a más de una Compra **activa** (no `Cancelada`) simultáneamente — validación server-side obligatoria en `CrearCompraManualAsync` y `AgregarItemsAsync`.
- El estado del Pedido nunca se modifica desde una acción de Compra, y viceversa — regla dura de este diseño.
- Un movimiento de tipo Factura en la cuenta corriente del proveedor no se edita ni elimina directamente: solo se ve afectado si se cancela la Compra que lo originó (comportamiento a especificar en Arquitectura).

## Impacto funcional por capa

- **Presentación**: `ComprasController` (nuevas acciones `Crear`, `AgregarItems`, `QuitarItem`; ajuste de `Detalle` e `Index`), nuevo `ProveedorController.CuentaCorriente` (+ acciones de alta/edición/baja de Pago y NCR), nuevas vistas `Compras/Crear.cshtml`, `Proveedor/CuentaCorriente.cshtml`, ajustes en `Compras/Detalle.cshtml` e `Index.cshtml`.
- **Negocio**: `PedidoService.ConfirmarAsync` pierde la creación/vinculación automática de Compra. `CompraProveedorService` gana métodos de armado manual y pierde la sincronización de estados hacia Pedido. Nuevo servicio (o extensión) para el ledger de proveedor.
- **Datos**: nueva entidad de vínculo item↔compra (reemplaza `CompraProveedor.Pedidos`), nueva entidad `MovimientoCCProveedor` (+ posible `CuentaCorrienteProveedor` si se replica 1:1 el patrón de Cliente), cambios en `CompraProveedor` (probablemente se elimina la colección `Pedidos` directa) y evaluación de qué hacer con `PagoProveedor` existente (migrar a `MovimientoCCProveedor` o convivir).

## Riesgos de implementación

- Migrar compras ya creadas en producción del modelo "Compra↔Pedido completo" al modelo "Compra↔PedidoItem" requiere un script de datos (no solo migración de esquema) — a dimensionar en Arquitectura.
- Quitar la sincronización automática de estados puede sorprender a usuarios acostumbrados al flujo actual (ej. hoy "Recibida" marca el pedido "Entregado" solo); se recomienda comunicarlo en la documentación de cliente (etapa 7).

### Puntos resueltos por el cliente (2026-07-03)

- **Cancelación de Compra ya facturada:** el movimiento Factura **se revierte** (no queda un residuo ni se genera NCR automática). Las Notas de Crédito son **siempre de alta manual** por el usuario — nunca automáticas — para que el ledger coincida 100% con la cuenta corriente real del distribuidor/proveedor.
- **Pagos históricos de `PagoProveedor`:** se **migran** al ledger nuevo `MovimientoCCProveedor` (no conviven dos modelos). Requiere script de migración de datos en la etapa de Arquitectura/Implementación.
- **Presupuesto:** el cliente decide implementar directamente, sin pasar por la etapa formal de Presupuesto. Se salta ese gate por instrucción expresa del cliente/owner.

## Historias de usuario completas

**HU-1** — Como administrador, quiero que el detalle de una compra al proveedor no muestre los items de stock propio, para no confundirlos con lo que realmente le debo pagar al proveedor.
- CA: dado un pedido con items propios y de proveedor vinculado a una compra, cuando abro el detalle, los items propios no aparecen en la tabla ni afectan el total.

**HU-2** — Como administrador, quiero ver la fecha como primer dato de cada compra en el listado, ordenado de la más reciente a la más antigua, para ubicar rápido las compras recientes.
- CA: la primera columna del listado es "Fecha"; la primera fila es la compra con `FechaGeneracion` más reciente.

**HU-3** — Como administrador, quiero crear una orden de compra eligiendo puntualmente qué artículos de qué pedidos confirmados incluir, para agrupar solo lo que efectivamente le voy a comprar al proveedor en ese momento.
- CA: en `Compras/Crear` veo únicamente items disponibles (proveedor, sin compra activa); al seleccionar y confirmar, se crea la compra con esos items y el total calculado.
- CA (borde): si un item deja de estar disponible entre que lo veo y confirmo (otro usuario lo tomó), el sistema me avisa puntualmente cuál item y no crea la compra con ese item.

**HU-4** — Como administrador, quiero ver en el detalle de la compra qué pedidos de cliente originaron cada item, para poder rastrear el destino de la mercadería.
- CA: en `Compras/Detalle` veo una sección con cada pedido de origen (número, cliente, estado actual), sin poder cambiar el estado del pedido desde ahí.

**HU-5** — Como administrador, quiero que cambiar el estado de una compra (o de un pedido) no afecte automáticamente al otro, para gestionar cada uno según mi propio proceso operativo.
- CA: al cambiar el estado de una Compra (cualquier transición), el/los Pedido(s) de origen no cambian de estado. Y viceversa.

**HU-6** — Como administrador, quiero ver un extracto de cuenta corriente del proveedor (fecha, hora, detalle, debe, haber, saldo) igual al que me manda el proveedor, para conciliar fácil mi sistema con su cuenta real.
- CA: la pantalla muestra movimientos ordenados por fecha ascendente con saldo acumulado, formato de "Detalle" equivalente al del extracto real (FAC/NCR/Efectivo/Transferencia + referencia).

**HU-7** — Como administrador, quiero registrar un pago (efectivo o transferencia) al proveedor sin tener que asociarlo a una compra puntual, para reflejar pagos que cubren el saldo acumulado tal como los hago en la realidad.
- CA: al registrar un pago solo indico fecha, método, importe y referencia; el pago impacta el saldo general, no el de una compra específica.

**HU-8** — Como administrador, quiero registrar una nota de crédito del proveedor, para reflejar descuentos o devoluciones que me reconoce contra mi cuenta corriente.
- CA: al registrar una NCR (fecha, importe, referencia), se genera un movimiento Haber en el extracto y el saldo general baja en esa medida.

**HU-9** — Como administrador, quiero poder editar o anular un pago/NCR cargado por error, para mantener la cuenta corriente conciliada.
- CA: puedo editar/anular un movimiento manual mientras la compra/periodo no esté cerrado (criterio a confirmar con Arquitectura); el saldo se recalcula al instante.

## Plan funcional por etapas (para Arquitectura)

1. **Etapa A — Fixes de bajo riesgo**: ocultar stock propio en `Compras/Detalle`; reordenar columna Fecha en `Compras/Index`. Sin cambios de modelo de datos.
2. **Etapa B — Armado manual de Compra por item**: nueva entidad de vínculo item↔compra; nuevos endpoints/servicio de creación manual; pantalla `Compras/Crear`; ajuste de `Compras/Detalle` (sección Pedidos de origen + edición de items en estados tempranos); eliminar disparo automático desde `PedidoService.ConfirmarAsync`.
3. **Etapa C — Desacople de estados**: simplificar `CompraProveedorService.CambiarEstadoAsync` quitando toda propagación hacia `Pedido`.
4. **Etapa D — Ledger de cuenta corriente del proveedor**: nueva(s) entidad(es) `MovimientoCCProveedor` (y `CuentaCorrienteProveedor` si aplica el mismo patrón 1:1 de Cliente); generación automática de movimiento Factura al facturar una Compra; pantalla `Proveedor/CuentaCorriente`.
5. **Etapa E — Pagos y Notas de Crédito generales**: altas/edición/baja manual de Pago y NCR contra el ledger; decisión y ejecución de qué pasa con `PagoProveedor` histórico (migración o convivencia).

## Historial de ajustes
- 2026-07-03: Diseño funcional inicial del lote "Compras al proveedor — desacople y cuenta corriente", sobre análisis aprobado el mismo día. Se identifican 2 riesgos nuevos no cubiertos en el análisis: reversión del movimiento Factura al cancelar una Compra, y destino de los pagos históricos de `PagoProveedor`.
- 2026-07-03: Cliente resuelve ambos puntos (reversión de Factura al cancelar + NCR siempre manual; migración de `PagoProveedor` histórico al ledger nuevo) y decide saltar la etapa de Presupuesto para implementar directamente. Diseño cerrado, pasa a Arquitectura.
