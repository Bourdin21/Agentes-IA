# Memoria - Arquitecto MVC

## Proyecto: vinosefue
## Ultima actualizacion: 2026-07-03

## Definiciones vigentes

### Alcance funcional resumido

Arquitectura técnica del lote "Compras al proveedor — desacople y cuenta corriente" (5 items), sobre [1-analista-funcional.md](1-analista-funcional.md) y [2-disenador-funcional.md](2-disenador-funcional.md) aprobados. El cliente decide implementar directamente, sin etapa formal de Presupuesto.

**Decisión de arquitectura clave (simplificación, principio "no premature abstraction"):** el vínculo Compra↔Pedido pasa de nivel-Pedido (`Pedido.CompraProveedorId`) a nivel-Item (`PedidoItem.CompraProveedorId`). No hace falta una tabla de vínculo N:N nueva — un `PedidoItem` solo puede estar en una Compra activa a la vez, así que una FK nullable directa en `PedidoItem` alcanza (mismo patrón que ya usa `Pedido.CompraProveedorId` hoy, solo que un nivel más abajo). Esto además resuelve el Fix 1 (stock propio) como efecto colateral: como `CompraProveedorId` solo se setea en items con `ProductoProveedorId != null`, el detalle de compra ya no puede traer items propios — no hace falta filtro adicional en la vista.

**Segunda simplificación:** no se crea una entidad `CuentaCorrienteProveedor` "cabecera" (a diferencia de `CuentaCorriente` de Cliente). El proveedor es único en el sistema (`ProveedorController.GetProveedorAsync()` sin id) — una cabecera 1:1 sería una tabla de una sola fila para siempre. Se guarda `ProveedorId` directo en `MovimientoCCProveedor`.

### Componentes por capa

#### Domain

| Componente | Cambio |
|---|---|
| `PedidoItem.cs` | Agregar `public int? CompraProveedorId { get; set; }` + nav `public CompraProveedor? CompraProveedor { get; set; }`. Regla de negocio (service, no constraint DB nueva): solo items con `ProductoProveedorId != null` pueden tener `CompraProveedorId` seteado. |
| `Pedido.cs` | **Eliminar** `CompraProveedorId` (FK) y su navegación `CompraProveedor`. El pedido deja de tener cualquier referencia a la compra. |
| `CompraProveedor.cs` | Reemplazar `ICollection<Pedido> Pedidos` por `ICollection<PedidoItem> Items`. **Eliminar** `TotalPagadoProveedor`, `SaldoPendienteProveedor`, `EstadoPagoProveedor` (el saldo por compra deja de tener sentido: los pagos ya no se atan a una compra puntual, viven en el ledger general). Se mantienen `TotalCostoSnapshot`, `TotalCostoReal`, `DiferenciaCosto`, `DeudaBase` (siguen sirviendo para saber cuánto FAC postear al ledger). Se elimina `ICollection<PagoProveedor> PagosProveedor`. |
| `PagoProveedor.cs` | **Eliminar** la entidad (se migra su data a `MovimientoCCProveedor` y no convive con el modelo nuevo, por decisión del cliente). |
| `MovimientoCCProveedor.cs` (nueva) | `Id`, `ProveedorId`, `Fecha` (DateTime, incluye hora), `Tipo` (`TipoMovimientoCC` — reutilizado, Debito/Credito), `OrigenTipo` (`OrigenTipoMovimientoProveedor` — nuevo enum), `MetodoPago` (`MetodoPago?` — reutilizado, solo aplica si `OrigenTipo == Pago`), `Importe`, `Referencia` (string?, libre — nº recibo/motivo NCR), `CompraProveedorId` (int?, FK — solo seteado si `OrigenTipo == Factura`, para trazabilidad y reversión), `AdjuntoId` (int?, reutiliza `Adjunto`), `CreadoPorUsuarioId`. Hereda `SoftDestroyable` (permite editar/anular Pago y NCR vía soft delete; los movimientos `Factura` no se tocan directo, solo se revierten cancelando la compra origen). |
| `OrigenTipoMovimientoProveedor.cs` (nuevo enum) | `Factura = 1`, `NotaCredito = 2`, `Pago = 3`. |

#### Application

| Componente | Cambio |
|---|---|
| `ICompraProveedorService` | **Nuevos:** `GetItemsDisponiblesAsync(filtros)`, `GetItemsDisponiblesCountAsync()` (reemplaza `GetPedidosSueltosCountAsync`), `CrearCompraManualAsync(itemIds, observaciones, usuarioId)`, `AgregarItemsAsync(compraId, itemIds)`, `QuitarItemAsync(compraId, itemId)`, `RegistrarPagoProveedorAsync(importe, metodoPago, fecha, referencia, adjunto?, usuarioId)` (general, sin `compraId`), `RegistrarNotaCreditoProveedorAsync(importe, fecha, referencia, usuarioId)`, `EditarMovimientoManualAsync(movimientoId, ...)`, `EliminarMovimientoManualAsync(movimientoId, usuarioId)`. **Eliminados:** `GetOrCreateCompraBorradorAsync`, `VincularPedidoACompraBorradorAsync`, `GetPedidosSueltosCountAsync`, `ReconsolidarPedidosSueltosAsync`, `RegistrarPagoProveedorAsync(compraId,...)`, `EditarPagoProveedorAsync`, `EliminarPagoProveedorAsync`, `GetPagosProveedorAsync`, `GetTotalPagadoProveedorAsync`. **Modificado:** `CambiarEstadoAsync` pierde el bloque de sincronización hacia `Pedido` (líneas 442-476 actuales); gana el posteo automático de Factura al pasar `Borrador → Generada` y su reversión al pasar a `Cancelada` (solo si ya había Factura posteada). |
| `IReporteService` | **Nuevo:** `GetCuentaCorrienteProveedorAsync(desde?, hasta?, page, pageSize)` → reutiliza el mismo patrón que `GetCuentaCorriente` de Cliente (armar `MovimientoCCProveedorViewModel` con saldo acumulado). |
| `IPedidoService` | `ConfirmarAsync` pierde el bloque de vinculación automática a Compra (líneas 797-811 actuales). El resto (reserva de stock propio + split automático por faltante) **no cambia** — el item resultante del split simplemente queda disponible (`CompraProveedorId == null`) para una futura compra manual. |
| DTOs nuevos | `CompraProveedorItemDisponibleDto`, `CrearCompraManualRequest`, `MovimientoCCProveedorDto`, `RegistrarPagoProveedorRequest`, `RegistrarNotaCreditoProveedorRequest` — siguiendo convención `ServiceResult`/`ServiceResult<T>` ya usada en el proyecto. |

#### Infrastructure

| Componente | Cambio |
|---|---|
| `CompraProveedorService.cs` | Implementa los métodos nuevos/eliminados de arriba. `BuildComprasQuery` deja de hacer `.Include(c => c.Pedidos)` y pasa a `.Include(c => c.Items).ThenInclude(i => i.Pedido).ThenInclude(p => p.Cliente)`. `GetByIdAsync` idem. Posteo de Factura: dentro de la misma transacción de `CambiarEstadoAsync` cuando `nuevoEstado == Generada`, crear `MovimientoCCProveedor { Tipo = Debito, OrigenTipo = Factura, Importe = compra.DeudaBase, CompraProveedorId = compra.Id, Fecha = DateTime.UtcNow, Referencia = compra.Numero }`. Reversión: si `nuevoEstado == Cancelada` y existe un movimiento Factura activo con ese `CompraProveedorId`, soft-delete de ese movimiento (recalculando el saldo se resuelve solo, porque el saldo se calcula sumando movimientos no eliminados). |
| `AppDbContext.cs` | Nuevo `DbSet<MovimientoCCProveedor> MovimientosCCProveedor`. Quitar `DbSet<PagoProveedor> PagosProveedor`. Configuración EF (Fluent API o `IEntityTypeConfiguration`) para `PedidoItem.CompraProveedorId` (FK opcional a `CompraProveedor`, `OnDelete: Restrict`) y para `MovimientoCCProveedor` (FKs a `Proveedor`, `CompraProveedor` opcional, `Adjunto` opcional). |
| `ReporteService.cs` | Nuevo método `GetCuentaCorrienteProveedorAsync`, calcado del ya existente para Cliente (agrupar movimientos no eliminados por rango de fecha, orden **ascendente** por `Fecha`, `Saldo` acumulado fila a fila). |
| `PedidoService.cs` | Quitar bloque de auto-vinculación a Compra (líneas 797-811). Quitar el método/uso de `SumarCostoProveedorDeComprasAsync` si queda sin otros usos. |

#### Web

| Componente | Cambio |
|---|---|
| `ComprasController.cs` | **Nuevas acciones:** `Crear` (GET: lista items disponibles con filtros; POST: crea la compra), `AgregarItems` (POST, solo si `Estado` en Borrador/Generada), `QuitarItem` (POST, idem). **Eliminar:** `Reconsolidar` (pierde sentido con el flujo manual). **Ajustar:** `Detalle` (arma `Items` desde `compra.Items` en vez de `compra.Pedidos.SelectMany`; agrega sección `PedidosOrigen` agrupando por `Item.Pedido`); `Index` (agrega botón "Nueva Compra"; el contador ya no es "Pedidos sueltos" sino "Items disponibles"). **Ajustar:** `RegistrarPagoProveedor`/`EditarPagoProveedor`/`EliminarPagoProveedor` se **mueven** a `ProveedorController` (dejan de requerir `compraId`). |
| `ProveedorController.cs` | **Nuevas acciones:** `CuentaCorriente` (GET, con `desde`/`hasta`/`page`), `RegistrarPago` (POST), `RegistrarNotaCredito` (POST), `EditarMovimiento`/`EliminarMovimiento` (POST, solo para movimientos `OrigenTipo != Factura`). Mantiene policy `RequireAdministracion` ya vigente. |
| Vistas | Nuevas: `Compras/Crear.cshtml`, `Proveedor/CuentaCorriente.cshtml` (calcada de `Reportes/CuentaCorriente.cshtml`, sin selector de proveedor). Ajustadas: `Compras/Detalle.cshtml` (sección "Pedidos de origen", botones agregar/quitar item en estados tempranos, quita la card de "Pagos" que ahora vive en la pantalla de cuenta corriente), `Compras/Index.cshtml` (columna Fecha primero, botón Nueva Compra, contador renombrado). `Reportes/DeudaProveedor.cshtml` queda obsoleta (reemplazada funcionalmente por `Proveedor/CuentaCorriente` — se recomienda eliminarla o redirigir, a confirmar con Documentación/cliente ya que hoy es un reporte separado). |

### Entidades y configuraciones EF

- `PedidoItem`: + `CompraProveedorId` (int?, FK a `CompraProveedor`, index no único — un compra tiene muchos items).
- `Pedido`: − `CompraProveedorId` (columna y FK eliminadas).
- `CompraProveedor`: − `TotalPagadoProveedor` (columna eliminada).
- `MovimientoCCProveedor` (tabla nueva): columnas descriptas arriba + columnas de auditoría estándar de `SoftDestroyable`.
- `PagoProveedor` (tabla eliminada tras migrar su data).

### Migraciones requeridas

**Sí, requiere migración EF.** Se recomienda dividir en 3 migraciones + 1 script de datos, en este orden:

1. **`AddCompraProveedorIdToPedidoItem`**: agrega `PedidoItems.CompraProveedorId` (nullable, FK).
   - *Script de datos (dentro o inmediatamente después de la migración):* para cada `Pedido` con `CompraProveedorId` no nulo, `UPDATE PedidoItems SET CompraProveedorId = <valor del pedido> WHERE PedidoId = <id> AND ProductoProveedorId IS NOT NULL`. Debe correr antes de eliminar la columna vieja.
2. **`RemoveCompraProveedorIdFromPedido`**: elimina `Pedidos.CompraProveedorId` (columna y FK) — solo después de confirmar que el script de datos de la migración 1 corrió en producción.
3. **`AddMovimientoCCProveedor`**: crea tabla `MovimientosCCProveedor` con sus FKs (`Proveedor`, `CompraProveedor` opcional, `Adjunto` opcional).
   - *Script de datos:* (a) por cada `CompraProveedor` con `Estado` en `Generada`/`EnPreparacion`/`Recibida` (es decir, ya "facturada" bajo el modelo viejo), insertar 1 `MovimientoCCProveedor` (`Tipo=Debito`, `OrigenTipo=Factura`, `Importe=DeudaBase`, `Fecha=FechaGeneracion`, `Referencia=Numero`, `CompraProveedorId=Id`). (b) por cada `PagoProveedor` no eliminado, insertar 1 `MovimientoCCProveedor` (`Tipo=Credito`, `OrigenTipo=Pago`, `MetodoPago`, `Importe`, `Fecha`, `Referencia`, `CompraProveedorId`, `AdjuntoId`, `CreadoPorUsuarioId`).
4. **`RemovePagoProveedorYTotalPagado`**: elimina tabla `PagosProveedor` y columna `CompraProveedor.TotalPagadoProveedor` — solo después de validar que el script de la migración 3(b) migró el 100% de los pagos (contar filas antes/después como chequeo).

Todas las migraciones de datos en producción deben ir como script SQL idempotente (mismo patrón que `20260509_AddDescuentoPorcentajePedidoItem.sql` u otros ya usados en este proyecto), con backup previo obligatorio por tratarse de datos financieros.

### Riesgos técnicos activos

- **Alto:** las migraciones 2 y 4 son destructivas (dropean columnas/tabla). Deben ejecutarse solo después de verificar en un ambiente de staging que el 100% de los datos históricos se migraron correctamente (conteo de filas, suma de importes cuadrando contra el reporte `DeudaProveedor` actual antes de tocar nada).
- **Medio:** la fecha del movimiento Factura backfilleado usa `CompraProveedor.FechaGeneracion` como aproximación (el modelo viejo no registraba un momento de "facturación" distinto). El saldo total va a cuadrar, pero el orden cronológico exacto de FACs viejas frente a NCR/Pagos del mismo día podría no coincidir 100% con el extracto real para movimientos históricos.
- **Medio:** al postear la Factura en la transición `Borrador → Generada`, si un usuario cancela una compra en `Generada`/`EnPreparacion` después de que otros movimientos (NCR/Pagos) ya se cargaron contra el saldo general, la reversión de esa Factura puede dejar el saldo en negativo transitoriamente — es un comportamiento esperado y correcto (refleja que hay pagos/NCR sin una factura que los respalde), pero conviene mostrarlo con claridad en la UI (saldo puede ser negativo = "a favor").
- **Bajo:** remover `Reportes/DeudaProveedor.cshtml` (o dejarlo obsoleto) puede confundir a usuarios que ya lo usan como bookmark — coordinarlo con Documentación.
- **Bajo:** los Fixes 1 y 2 no tienen riesgo técnico relevante; el Fix 1 queda resuelto de forma implícita por el cambio de modelo (ver "Decisión de arquitectura clave" arriba).
- **Medio (detectado 2026-07-08):** el provider `MySql.EntityFrameworkCore` 10.0.1 (Oracle oficial, no Pomelo) sobre EF Core 10.0.2 **no traduce `List<string>.Contains(...)` a SQL correctamente** — tira `InvalidOperationException: Expression '@xxx' in the SQL tree does not have a type mapping assigned`, sin importar si la lista está vacía o tiene datos. Confirmado en `ComprasController.Detalle` (`_context.Users.Where(u => userIds.Contains(u.Id))`, `userIds` es `List<string>`). Workaround aplicado ahí: traer la tabla completa (chica) con `.ToListAsync()` y filtrar en memoria (LINQ-to-Objects) en vez de traducir el `.Contains()` a SQL. `List<int>.Contains(...)` NO está afectado (verificado en otros services del proyecto). **Pendiente:** no se auditó exhaustivamente el resto del código en busca de otros `.Contains()` sobre `List<string>`/`List<Guid>` que puedan compartir este bug — candidatos a revisar si aparecen crashes similares: cualquier filtro por lista de IDs de usuario (`ApplicationUser.Id` es `string`) en otros controllers/services.

### Modelo de permisos

Sin cambios. Todas las acciones nuevas (`ComprasController.Crear/AgregarItems/QuitarItem`, `ProveedorController.CuentaCorriente/RegistrarPago/RegistrarNotaCredito/EditarMovimiento/EliminarMovimiento`) quedan bajo la policy ya vigente `RequireAdministracion` en ambos controllers — no se introduce ningún rol/claim nuevo.

### Estrategia de pruebas funcionales

- Regresión sobre `PedidoService.ConfirmarAsync`: confirmar que el split automático de stock propio sigue funcionando igual, y que ya NO se crea/vincula ninguna Compra.
- Flujo completo nuevo: crear pedido confirmado → `Compras/Crear` → seleccionar items puntuales → verificar que compra queda en Borrador con el costo correcto → pasar a Generada → verificar que se postea 1 movimiento Factura en la cuenta corriente del proveedor con el importe correcto → cancelar → verificar que el movimiento se revierte y los items vuelven a estar disponibles.
- Verificar que un item ya en una compra activa no aparece en `Compras/Crear` ni puede agregarse a otra compra (prueba de concurrencia: dos usuarios intentando tomar el mismo item).
- Verificar independencia total de estados: cambiar estado de Pedido no mueve la Compra y viceversa, en todas las combinaciones relevantes.
- Verificar extracto de cuenta corriente del proveedor: orden ascendente, saldo acumulado correcto, registrar Pago y NCR manuales y confirmar impacto inmediato en saldo.
- Verificar migración de datos en un dump de staging: conteo de `PagoProveedor` migrados = conteo de movimientos `Pago` creados; suma de `DeudaBase` de compras facturadas = suma de movimientos `Factura`; saldo global antes/después de migrar coincide con `GetResumenDeudaGlobalAsync` actual (o su reemplazo).

## Historial de ajustes
- 2026-07-03: Arquitectura inicial del lote "Compras al proveedor — desacople y cuenta corriente". Decisiones propias del arquitecto (no bloqueantes, documentadas como tal): vínculo Compra↔Item vía FK directa en `PedidoItem` (no tabla N:N nueva); sin entidad `CuentaCorrienteProveedor` cabecera (proveedor único); posteo de Factura en la transición Borrador→Generada; se elimina el saldo/estado de pago a nivel de Compra individual (ahora vive solo en el ledger general). Cliente decide saltar Presupuesto e ir directo a Implementación.
