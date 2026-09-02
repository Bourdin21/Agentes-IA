---
name: pedidos-total-sin-iva
description: "Bug de \"Total Estimado\" en Pedidos sin IVA sumado (Cantidad*PrecioUnitario en vez de Subtotal) y los 4 lugares donde se repetía"
metadata: 
  node_type: memory
  type: project
  originSessionId: d598e711-73e1-4ffa-8130-c5cbb9032bfe
  modified: 2026-08-05T22:05:09.548Z
---

**Patrón de bug real, encontrado el 2026-08-06 en producción:** en varias vistas/emails se recalculaba el total de un pedido con `Cantidad * PrecioUnitario * (1 - Descuento/100)`, que **no aplica el factor de IVA**. El campo `PedidoDetalle.Subtotal` (y `ProductoVenta.Subtotal`) ya viene calculado CON IVA desde `PedidosController` (create) — cualquier vista que recalcule en vez de usar `.Subtotal` directamente va a mostrar un total más bajo que el real para productos gravados (10,5%/21%).

**Caso real:** Pedido #181, cliente Julieta Amelio — "Total Estimado" en el listado mostraba $50.497,69 (sin el 21% IVA de un Chocolate Arcor gravado) mientras que el total real (`Pedidos/Details`, columnas Efectivo+Transferencia, y la Venta generada) era $54.420,00. La diferencia exacta era el IVA del único ítem gravado.

**4 lugares con el mismo bug, todos corregidos (reemplazando el cálculo por `.Sum(d => d.Subtotal)` o `item.Subtotal`):**
- `Views/Pedidos/Index.cshtml` (columna "Total Estimado", listado admin/vendedor)
- `Views/Pedidos/MisPedidos.cshtml` (mismo, pero visible para el Cliente)
- `Views/Pedidos/_VentaCompletaPartial.cshtml` (subtotal por línea al abrir "Ver venta completa" desde Pedidos/Details)
- `Helper/NotificacionesHelper.cs` → `EnviarCorreoCambioEstadoPedido`/`GenerarMailCambioEstado` (el mail que recibe el cliente al aprobar/rechazar su pedido — mostraba mal el total y cada subtotal)

**Cómo aplicar:** el invariante correcto en todo el código de Pedidos/Ventas es: **nunca recalcular `Cantidad * PrecioUnitario * (1-desc%)` para mostrar un total al usuario — siempre usar el campo `.Subtotal` ya persistido**, que es la única fuente que aplica el factor de IVA (`IvaForzado`/`CondIVA`) correctamente. Si aparece una discrepancia similar en el futuro (total mostrado ≠ total real), buscar primero este mismo antipatrón (`grep -r "Cantidad \*.*PrecioUnitario"`) antes de asumir otra causa.

**Validación anti-tampering ya existente (confirmado, no hace falta agregar):** un Cliente no puede sacarle IVA a un producto gravado — el frontend (`pedido-create.js`) oculta el selector de IVA para productos `ConIva`/`DiezYMedio` y manda un campo fijo, y el backend (`PedidosController`, creación del pedido) valida explícitamente `if (productoGravado && item.AplicarIva == false) return error` más un chequeo anti-downgrade de `IvaForzado`. Esto ya estaba bien antes de esta sesión.
