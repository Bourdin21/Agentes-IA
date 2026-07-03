# Memoria - Analista funcional

## Proyecto: vinosefue
## Ultima actualizacion: 2026-07-03

## Definiciones vigentes

### Modulos/features analizados

**Lote "Compras al proveedor — desacople y cuenta corriente" (2026-07-03)**, 5 items:

1. FIX — Stock propio no debe figurar en el detalle de Compras al proveedor.
2. FIX — Listado de Compras: columna Fecha primero + orden descendente.
3. FEATURE — Desacoplar el estado de la Compra al proveedor del estado del Pedido; creación manual de la orden de compra seleccionando artículos de pedidos confirmados.
4. FEATURE — Simplificar el modelo de cuenta corriente del proveedor para que coincida con el extracto real del proveedor (Fecha/Hora/Detalle/Debe/Haber/Saldo).
5. FEATURE — Generar Pagos y Notas de Crédito del proveedor como movimientos de esa cuenta corriente.

### Estado actual del sistema (relevado en código, no documentado previamente)

- **`CompraProveedor`** (`VinoSeFue.Domain\Entities\CompraProveedor.cs`) no tiene items propios: agrupa `Pedidos` completos (`ICollection<Pedido> Pedidos`) y los items se derivan de `Pedido.Items`.
- **Generación hoy: automática.** Al confirmar un Pedido (`PedidoService.cs:797-811`) si tiene algún item de origen proveedor, se busca/crea una Compra en estado `Borrador` (única compra abierta a la vez, `CompraProveedorService.cs:599-603`) y se le vincula el pedido completo. Un admin luego "sube la nota de pedido" y la compra pasa a `EnPreparacion`.
- **Sincronización de estados hoy: automática y unidireccional** Compra → Pedidos (`CompraProveedorService.CambiarEstadoAsync`, líneas 420-493): Generada→Confirmado, EnPreparacion→EnPreparacion, Recibida→Entregado, Cancelada→desvincula y vuelve a Confirmado.
- **Stock propio**: los items `EsStockPropio` (`ProductoPropioId.HasValue`) ya están excluidos del costo/deuda de la compra (`TotalCostoSnapshot` los filtra, `PedidoService.cs:800-801` y `CompraProveedorService.cs:637-645`, comentario explícito "no se compran al proveedor"). **Pero sí aparecen listados** en el detalle de la compra porque `ComprasController.Detalle` (líneas 95-106) arma `Items` con `compra.Pedidos.SelectMany(p => p.Items)` sin filtrar por origen — ahí está el fix pedido.
- **Listado de Compras** (`ComprasController.Index` + `Views/Compras/Index.cshtml:88-96`): la consulta YA ordena `OrderByDescending(c => c.FechaGeneracion)` (`CompraProveedorService.cs:39`). Lo que falta es solo el orden visual de columnas: hoy "Fecha" es la 6ta columna (Número, Pedido(s), Cliente(s), Estado, Total Costo, Fecha, Nota, Pago Prov., Acciones).
- **Cuenta corriente hoy**: `CuentaCorriente`/`MovimientoCC` (con `TipoMovimientoCC` = solo `Debito`/`Credito`) es exclusiva de **Clientes**. No existe un ledger equivalente para Proveedor. La "deuda proveedor" se deriva por compra individual: `DeudaBase` (`TotalCostoReal ?? TotalCostoSnapshot`) menos `TotalPagadoProveedor` (denormalizado), expuesta en `Reportes/DeudaProveedor.cshtml`.
- **Pagos a proveedor hoy**: `PagoProveedor` (`Domain\Entities\PagoProveedor.cs`) existe pero está **atado 1:1 a una `CompraProveedorId` puntual** ("Pago al proveedor siempre asociado a una CompraProveedor", comentario en la entidad). No existe entidad ni acción de "Nota de Crédito de proveedor" en ningún punto del código.
- Esto NO coincide con el extracto real del proveedor (imagen adjunta del cliente): ahí los pagos (Efectivo/Transferencia) y NCR se aplican contra el **saldo corriente general** de la cuenta, no contra una factura/compra puntual — el pago de $2.000.000 del 8/5 no coincide con ningún FAC individual, reduce el saldo acumulado.

### Reglas funcionales acordadas (todas confirmadas por el cliente el 2026-07-03)

- **Item 1:** en `Compras/Detalle`, la lista de items debe excluir los items de stock propio (`EsStockPropio == true` / `ProductoProveedorId == null`). El cálculo de costo/deuda no cambia (ya los excluye).
- **Item 2:** reordenar columnas del listado de Compras para que "Fecha" sea la primera columna visible. El orden descendente por fecha ya existe en el backend — no requiere cambio de lógica, solo de vista.
- **Item 3 — granularidad de selección:** confirmado **por artículo individual**. El usuario arma una Compra eligiendo líneas puntuales de pedidos confirmados (no el pedido completo); items de un mismo pedido pueden repartirse en compras distintas (ej. Vino A del pedido #4521 va a la Compra de esta semana, Vino B del mismo pedido queda pendiente para una compra futura). Implica una entidad de vínculo nueva `CompraProveedorItem` (o similar) que relacione `CompraProveedorId` ↔ `PedidoItemId`, reemplazando el vínculo actual a nivel de `Pedido` completo (`CompraProveedor.Pedidos`).
- **Item 3 — desacople de estados:** confirmado **totalmente independiente**. Se elimina toda sincronización automática Compra→Pedido (`CompraProveedorService.CambiarEstadoAsync`, hoy líneas 420-493). El estado del Pedido lo gestiona el usuario manualmente en la pantalla de Pedidos. La Compra solo referencia informativamente qué pedidos/items la originaron, visible en `Compras/Detalle`.
- **Item 4/5 — modelo de cuenta corriente:** confirmado **ledger único del proveedor**, análogo al patrón ya probado para Clientes (`CuentaCorriente` + `MovimientoCC`). Cada Compra facturada/confirmada genera un Débito (FAC) automático; el usuario puede cargar manualmente Notas de Crédito (Haber) y Pagos —efectivo/transferencia— (Haber), todos contra el saldo corriente GENERAL del proveedor, sin atarse 1 a 1 a una compra puntual. Reemplaza el modelo actual de `PagoProveedor` atado a `CompraProveedorId`.

### Impacto en flujo de creación de Compra (ya no automático)

- Se elimina la creación/vinculación automática de Compra al confirmar un Pedido (`PedidoService.cs:797-811`, `GetOrCreateCompraBorradorInternalAsync`).
- Los pedidos confirmados con items de proveedor quedan en un "pool" disponible para compra (no vinculados a ninguna Compra hasta que el usuario arme una manualmente).
- El split automático por faltante de stock propio (`PedidoService.cs:693-699`, cuando no alcanza el stock propio y se cubre con catálogo de proveedor) se mantiene: ese item generado sigue entrando al pool disponible para compra, igual que cualquier item de origen proveedor.
- `ReconsolidarPedidosSueltosAsync` y el flujo de "Nota de pedido" pierden sentido tal como están (ligados al modelo de 1 compra Borrador acumulando pedidos completos) — a redefinir en Diseño/Arquitectura.

### Criterios de aceptación vigentes

**CU-1 — Ocultar stock propio en detalle de compra**
- Dado un Pedido con items de origen proveedor y de stock propio vinculado a una Compra, cuando el usuario abre `Compras/Detalle`, entonces la tabla de items solo muestra los de origen proveedor (stock propio no aparece ni como línea informativa).
- El total de la compra no cambia (ya excluía stock propio).

**CU-2 — Orden del listado de compras**
- Dado el listado de Compras, cuando el usuario lo abre sin filtros, entonces la primera columna visible es "Fecha" y las filas están ordenadas de más reciente a más antigua (ya así en backend).

**CU-3 — Armado manual de Compra por artículo**
- Dado un conjunto de pedidos en estado Confirmado con items de origen proveedor, cuando el usuario crea una nueva Compra y selecciona items puntuales (de uno o varios pedidos), entonces se crea una `CompraProveedor` en estado inicial con esos items vinculados y su costo total calculado sobre los items seleccionados.
- Un item ya incluido en una Compra no puede volver a seleccionarse para otra Compra (evitar duplicar deuda).
- El estado del Pedido de origen NO cambia automáticamente al crear, avanzar o cancelar la Compra.
- En `Compras/Detalle` se listan los pedidos de cliente de origen de los items seleccionados (número, cliente, estado actual del pedido) a modo informativo/trazabilidad.

**CU-4 — Extracto de cuenta corriente del proveedor**
- Dado un proveedor con compras facturadas, pagos y notas de crédito, cuando el usuario abre la cuenta corriente de ese proveedor, entonces ve un listado cronológico con columnas Fecha, Hora, Detalle, Debe, Haber, Saldo, con saldo corriente acumulado (igual estructura que el extracto real adjuntado por el cliente).
- Cada Compra confirmada/facturada genera automáticamente un movimiento de Débito (FAC) por su costo total.

**CU-5 — Alta manual de Pago y Nota de Crédito de proveedor**
- Dado un proveedor con saldo pendiente, cuando el usuario registra un Pago (efectivo o transferencia) o una Nota de Crédito, entonces se genera un movimiento de Haber en la cuenta corriente general del proveedor (sin necesidad de indicar una Compra puntual) y el saldo se actualiza.
- Los pagos/NCR admiten referencia libre (n° de recibo/transferencia) para trazabilidad, tal como en el extracto real.

### Supuestos y dependencias

- Se asume que "stock propio ya pagado" significa que nunca debe generar deuda ni aparecer como línea de compra al proveedor — coherente con el comportamiento ya implementado para el costo; falta extenderlo a la vista.
- El nuevo modelo de cuenta corriente de proveedor es conceptualmente análogo al ya existente para Clientes (`CuentaCorriente` + `MovimientoCC`), lo que reduce riesgo técnico (patrón ya probado en el sistema) pero implica una entidad y tablas nuevas, no una extensión de `PagoProveedor`.
- Los pedidos de cliente seguirán existiendo como entidad independiente; el requerimiento pide poder **verlos** desde el detalle de la compra, no fusionar sus estados.
- Los 3 puntos de diseño abiertos fueron confirmados por el cliente el 2026-07-03 (ver "Reglas funcionales acordadas"); el análisis queda cerrado sin bloqueos para pasar a Diseño funcional (etapa 2).

### Riesgos

- **Riesgo alto:** reemplazar el vínculo `CompraProveedor.Pedidos` (a nivel Pedido) por un vínculo a nivel `PedidoItem` es un cambio de modelo de datos de raíz. Afecta: `ComprasController`, `CompraProveedorService` (BuildComprasQuery, CambiarEstadoAsync, GetResumenDeudaGlobalAsync), reportes de deuda proveedor, y probablemente requiere migrar datos existentes (compras ya creadas con el modelo viejo).
- **Riesgo medio:** al eliminar la sincronización automática de estados, cualquier reporte/vista que hoy asuma que "Pedido Entregado ⇒ Compra Recibida" (o viceversa) puede quedar desactualizado; hay que revisar `ReconsolidarPedidosSueltosAsync`, badges de estado en vistas de Pedidos, y el flujo de "Nota de pedido" que hoy dispara la transición Borrador→EnPreparacion.
- **Riesgo medio:** migrar `PagoProveedor` (atado a Compra) a un ledger general de proveedor puede dejar huérfanos los pagos ya cargados en producción; requiere decidir en Arquitectura si se migran o conviven ambos modelos por un tiempo.
- **Riesgo bajo:** los fixes 1 y 2 no tienen riesgo relevante (cambios acotados a vista/filtro).

### Permisos, estados y validaciones identificadas

- Las acciones de `ComprasController` hoy requieren policy `RequireAdministracion` (`ComprasController.cs:11`) — se asume que la creación manual de Compra y el alta de Pagos/NCR de proveedor mantienen la misma policy salvo indicación contraria.
- Estados de `CompraProveedor` hoy: Borrador, Generada, EnPreparacion, Recibida, Cancelada (`EstadoCompraProveedor`) — a redefinir en Diseño si el modelo manual por ítem sigue necesitando estado "Borrador" (probablemente sí, para armar la compra antes de confirmarla).
- Validación crítica nueva: un `PedidoItem` no puede pertenecer a más de una Compra activa simultáneamente (evitar duplicar deuda/compra del mismo artículo).
- Validación crítica nueva: un movimiento de Débito (FAC) del ledger de proveedor debe quedar trazable a la Compra que lo originó (para poder auditar, aunque el pago no se ate 1 a 1).

### Banderas tempranas

- **Requiere migración EF:** Sí. Nueva entidad de vínculo item↔compra, nueva entidad de ledger de proveedor (`CuentaCorrienteProveedor`/`MovimientoCCProveedor` o equivalente), y cambios en `CompraProveedor`/`PagoProveedor`.
- **Integración externa:** No.
- **Máquina de estados:** Sí — se simplifica la de `CompraProveedor` (deja de estar acoplada a la de `Pedido`), y el `Pedido` pasa a tener transiciones 100% manuales sin disparadores desde Compra.

### Exclusiones confirmadas

- No se migran datos históricos de `PagoProveedor` a un nuevo ledger automáticamente salvo que el cliente lo pida explícitamente (a definir en Diseño/Arquitectura una vez resuelto el modelo).
- No se toca el modelo de `CuentaCorriente` de Clientes (queda igual).
- No se define en esta etapa la UI final (eso es Diseño funcional, etapa 2).

## Historial de ajustes
- 2026-07-03: Discovery + Análisis funcional inicial del lote "Compras al proveedor — desacople y cuenta corriente" (5 items). Fixes 1 y 2 sin bloqueos desde el inicio.
- 2026-07-03: Cliente resolvió las 3 preguntas abiertas de arquitectura funcional: (1) selección por artículo individual, no por pedido completo; (2) desacople total de estados Compra↔Pedido, sin ningún disparador automático remanente; (3) ledger único de cuenta corriente del proveedor (no pago atado a compra puntual). Análisis cerrado, pasa a Diseño funcional (etapa 2).
