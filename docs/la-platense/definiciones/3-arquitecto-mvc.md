# Memoria - Arquitecto MVC

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-08-17 (v7 — retirado ICatalogoMigracionService: la carga real del catalogo va por script directo, no por la app)

## Definiciones vigentes

### Componentes por capa

- **Presentación**: Controllers/Views para Usuarios, Catálogo, Stock, Ventas, Facturación AFIP, Proveedores/Compras, Importación de listas, Caja, Gastos, CtaCteNegocio, CtaCteEmpleado, Presupuestos, Entregas, AumentoMasivo, Dashboard. DataTables para todos los listados; SweetAlert2 para confirmaciones; daterangepicker para filtros de fecha (Caja, Ventas, Compras).
- **Negocio (Services)**: `VentaWorkflowService`, `UnidadMedidaConversionService`, `RecargoCuotasService`, `ListaPreciosProveedorImportService`, `CuentaCorrienteEmpleadoService`, `CajaService` (diaria+mensual), `AfipFacturacionService` (incluye emisión de NC/ND), `AnulacionVentaService`, `DevolucionMercaderiaService`, `EntregaMarkupService`, `AumentoMasivoService`, `DashboardService` (3 niveles: día / salud financiera / tendencias), `AjusteStockService` (corrección manual auditada + venta con stock negativo permitido), `CodigoBarrasLookupService` (resuelve producto por código escaneado en venta). *`EtiquetaService` se retira — la ticketeadora es manual, no hay generación/impresión de etiquetas de por medio. `CatalogoMigracionService` también se retira de este alcance — la migración se pospone, ver `4-presupuestador.md`.*
- **Datos**: `AppDbContext` + repositorios EF Core / MySQL, siguiendo el patrón estándar del blankproject base (10-blankproject-base, soft delete + auditoría en todas las entidades).

### Entidades y configuraciones EF

Entidades nuevas (resumen — el detalle exacto de columnas se cierra en Implementación):

- `Producto` (nombre, codigo, marca, modelo, categoriaId, precioCompra, precioVenta, precioConDescuento, porcentajeIVA, unidadVenta [enum: Unidad/Peso/Metro/Bulto], unidadCompra [enum, nullable], factorConversion [nullable], stock, stockMinimo, clasificacionABC [enum A/B/C, nullable — usado en la puesta a punto de stock inicial], stockVerificado [bool, default false hasta que se cuenta o se ajusta manualmente], codigoBarras [string, único — de fábrica reutilizado o propio asignado por el negocio]).
- `AjusteStock` (productoId, fecha, usuarioId, cantidadAnterior, cantidadNueva, motivo) — reutiliza el patrón de ajuste manual de `ShowroomGriffin` (`StockController`). Marca `Producto.stockVerificado = true` al aplicarse.
- `Marca`, `Modelo`, `Categoria` (catálogo simple, patrón ya resuelto).
- `Cliente` (nombre, CUIT/DNI, condicionIVA, telefono, saldoCuentaCorriente).
- `Venta` (fecha, clienteId [nullable = consumidor final], estado [Borrador/Facturada/Anulada], subtotal, totalIVA, total, tipoComprobanteAfip, cae, numeroComprobante). El repartidor tiene visibilidad total sobre `Entrega` (sin scoping por `repartidorId` — confirmado, ve todas).
- `NotaCreditoDebito` (ventaId, tipoComprobanteAfip [NC/ND], cae, numeroComprobante, motivo, fecha) — vinculada a la `Venta` original, dispara la transición `Facturada`→`Anulada`.
- `DevolucionMercaderia` (ventaId, notaCreditoId, fecha, motivo) con `ItemDevolucion` (productoId, cantidad) — reingresa stock al confirmarse. Sin flujo de "cambio/canje" (confirmado, siempre devolución simple).
- `ItemVenta` (ventaId, productoId, cantidad, unidadVenta, precioUnitario, porcentajeIVA, descuento, recargo, subtotal).
- `PagoVenta` (ventaId, medioPago [Efectivo/Debito/CreditoCuotas/CuentaCorriente], monto, cuotas [nullable], porcentajeRecargoAplicado [nullable]).
- `Proveedor` (nombre, CUIT, tcPropio, porcentajeDescuento, saldoCuentaCorriente).
- `Compra` (fecha, proveedorId, formaPago [Echeck/Transferencia], total).
- `ItemCompra` (compraId, productoId, cantidadUnidadCompra, cantidadUnidadVentaEquivalente, precioUnitario).
- `MovimientoCuentaCorrienteProveedor` (proveedorId, fecha, tipo, monto, saldo) — reutiliza patrón `MovimientoCCProveedor` de `vinosefue`.
- `CajaMovimiento` (fecha, tipo [Ingreso/Egreso], monto, origen, referenciaId).
- `CierreCajaDiario`, `CierreCajaMensual` (fecha/periodo, totalIngresos, totalEgresos, saldo).
- `Gasto` (fecha, concepto, monto, tipoImpacto [CajaChica/CajaMensual]).
- `EmpleadoCuentaCorriente` (usuarioId, fecha, tipo [Sueldo/Retiro/Gasto], monto, saldo) — visibilidad restringida al propio usuario + admin.
- `Presupuesto` (clienteId, fecha, items, total, pdfGenerado).
- `Entrega` (ventaId, tipo [Propia/Tercerizada], costoBase, porcentajeMarkup, costoFinal, estado, repartidorId [nullable]).
- `HistorialPrecio` (productoId, fecha, precioAnterior, precioNuevo, motivo) — soporta Aumento Masivo.

### Migraciones requeridas

- Migración inicial: todas las entidades listadas arriba (incluye `NotaCreditoDebito`, `DevolucionMercaderia`, y los campos nuevos de `Producto` para stock inicial y código de barras).
- **Migración de datos del catálogo existente del cliente — RETOMADA 2026-08-17, ya no pospuesta.** Joaquín consiguió acceso directo al backup real de SQL Server del sistema actual (17,35GB, ~121.691 artículos activos — corrige el volumen estimado de ~17.000). Ver detalle completo de Análisis/Diseño en `1-analista-funcional.md` y `2-disenador-funcional.md` flujo 10. Arquitectura de esta etapa (Etapa 3) en la sección siguiente.

### Etapa 3 — Arquitectura de la migración de catálogo (2026-08-17)

**Entidades nuevas:**
- `CodigoProveedorProducto` (productoId, proveedorId, codigoDelProveedor, activo) — reemplaza la idea original de "un código externo único en `Producto`": un mismo `Producto` puede tener N filas, una por cada proveedor que lo vende con su propio código. Confirmado por los datos reales: dos listas de proveedor de muestra no comparten ningún esquema de código entre sí, y el sistema actual del cliente ya resuelve esto igual (tabla `Codigo` con `ProveedorKey`+`Codigo`). Índice único compuesto `(ProveedorId, CodigoDelProveedor)`.
- Sin entidad nueva para el "reporte de excepciones" de la migración — se modela como una vista/consulta sobre el resultado del proceso de limpieza (paso 1 del flujo 10), no como una tabla persistente del sistema en producción.

**Extensión de entidades ya existentes (Entrega 1/2, no rompe lo ya implementado):**
- `Producto`: agrega `Bonificacion` (string, nullable, ej. `"33+5"` — bonificación compuesta, confirmada como gap real por Joaquín) y `ClasificacionABCSugerida` (enum A/B/C, nullable, calculado — separado de `ClasificacionABC` que ya existe y sigue siendo el campo editable manual de Entrega 1, ver R10 vigente).
- `Cliente`: agrega `Domicilio`, `Localidad`, `Email`, `Notas` (todos string nullable — gaps confirmados en Análisis frente al sistema real).

**Servicios nuevos:**
- ~~`ICatalogoMigracionService`/`CatalogoMigracionService`~~ — **implementado y luego retirado (2026-08-17)**: Joaquín decidió que la carga del catálogo histórico (~121.691 productos) va por **script directo a la base**, no por un Service/Controller de la app con flujo preview→confirmar — al ser una carga de una sola vez, no justifica mantener esa superficie en el sistema. El script reutiliza las entidades (`Producto`/`CodigoProveedorProducto`/`Cliente`/`Proveedor`) y la lógica de deduplicación ya diseñada, pero corre fuera del ciclo de vida de `FerreteriaLaPlatense.Web` — los pasos 1 y 2 del flujo 10 quedan unificados en una sola herramienta batch.
- `IClasificacionAbcAutomaticaService` / `ClasificacionAbcAutomaticaService`: recalcula por lote `Producto.ClasificacionABCSugerida` sobre ventana móvil de `ItemVenta` (12 meses configurable) con corte Pareto 80/95 por cantidad vendida. Se registra Scoped, se invoca desde una acción manual de administración (no job automático en esta etapa — ver riesgo abajo). **Se mantiene** — es funcionalidad permanente del sistema, no exclusiva de la migración.
- **El proceso de limpieza/extracción (paso 1 del flujo 10) NO es un servicio de la aplicación web** — es un proceso batch de una sola corrida (script/herramienta de migración ejecutado por Olvidata contra una copia del backup del cliente), fuera del ciclo de vida normal de `FerreteriaLaPlatense.Web`. No requiere DI ni controller.

**Migración EF de esta etapa:**
- Una migración: `EntregaTres_MigracionCatalogo_CodigoProveedorProducto` (o el nombre que corresponda en Implementación) — agrega `CodigoProveedorProducto`, y las columnas nuevas de `Producto`/`Cliente`. No modifica ninguna migración ya aplicada de Entrega 1/2.
- La carga masiva de datos migrados (~121.691 productos + `CodigoProveedorProducto` + clientes) **no va en la migración EF** — es un seed/import de datos ejecutado una vez, separado del esquema.

### Capacidad de hosting — verificado 2026-08-17 (pregunta de Joaquín: la base de producción tiene un tope de 500MB)

Medición real (no estimada a ojo): se cargó una muestra real de 1.487 productos activos (de la base restaurada) en una tabla MySQL local con el esquema exacto de `Producto`, y se midió el tamaño real vía `information_schema.tables` (InnoDB, datos+índices): **297,8 bytes/fila**. Extrapolado a los 121.691 productos activos reales: **≈ 34,6 MB**. Sumando una estimación de `CodigoProveedorProducto` (asumiendo 0,5-1 código de proveedor por producto en promedio tras la deduplicación, ~180 bytes/fila): **≈ 11-22 MB adicionales**. Total estimado de la migración de catálogo: **≈ 46-67 MB**, contra un tope de **500 MB** — deja **más del 85% de margen libre**, no es un bloqueante para esta etapa.

**Riesgo real distinto, a monitorear (no resuelto por esta medición):** el tope de 500MB es del total de la base, no solo del catálogo — las tablas transaccionales que crecen con el uso diario (`Ventas`/`ItemVenta`/`PagoVenta`/`CajaMovimiento`/`Notifications`, etc., de Entregas 1 y 2) van a acumular filas de forma continua mes a mes, a diferencia de la carga del catálogo que es un evento único. No se midió proyección de crecimiento transaccional en esta ronda — recomendado revisar el uso real de espacio cada pocos meses una vez el sistema esté en producción operativa, no solo antes de la migración de catálogo.

### Riesgos técnicos de Etapa 3 (adicionales a los ya vigentes)

- **Volumen real 7x el estimado original** (121.691 activos vs ~17.000 supuestos): no cambia el diseño (`DataTables` server-side de Entrega 1 ya pagina en servidor, no carga todo en memoria), pero sí el tiempo de import batch inicial y el tamaño del reporte de excepciones — a validar tiempos reales en Implementación con un dataset de este volumen antes de comprometer una ventana de corte a producción.
- **`IClasificacionAbcAutomaticaService` sin trigger automático definido todavía**: el diseño lo deja como acción manual desde administración, no un job programado — si Joaquín pide que se recalcule solo (ej. mensual), es una extensión menor (`CronCreate`/hosted service), no un cambio de arquitectura, pero no está confirmado en esta ronda.
- **Deduplicación de nombre con respaldo `FechaModificacionPrecio`**: decide el 87% de los casos ambiguos (3.544 de 3.612 grupos, ver Análisis) — es una heurística, no una regla infalible; algunos casos van a requerir corrección manual posterior desde el catálogo ya migrado (edición normal de `Producto`, no requiere pantalla especial).
- **Origen de ventas para ABC confirmado como `VentaItem`/`Operacion`, no `tblVentas`/`tblDetalleVentas`** (`tblDetalleVentas.Codigo` no vincula a ningún producto en los datos reales) — si en el futuro el cliente migra su operatoria diaria hacia el otro circuito, `IClasificacionAbcAutomaticaService` deja de tener datos de origen; no aplica mientras el sistema nuevo sea el único en uso post-migración (los `ItemVenta` los genera el sistema nuevo, no dependen de los circuitos legacy una vez migrado).

### Riesgos tecnicos activos

- **Venta con stock negativo permitido**: la validación de stock en `VentaWorkflowService` debe permitir confirmar una venta aunque el producto quede en negativo (solo aviso, no bloqueo) mientras `Producto.stockVerificado = false` — evitar que una regla de "no vender sin stock" (frecuente en ABMs de stock genéricos) bloquee el mostrador durante la transición de datos.
- **Conversión de unidades compra↔venta**: no hay entidad/patrón exacto reutilizable en el historial — es desarrollo nuevo (aislado en `UnidadMedidaConversionService` para minimizar impacto en el resto del sistema).
- **Workflow Venta Borrador→Facturada con edición previa**: mayor superficie de riesgo que el patrón estándar de venta+AFIP ya resuelto (que factura directo, sin estado intermedio editable).
- **Importación de listas de proveedor**: el mapeo de columnas puede no ser 100% genérico entre proveedores — riesgo de tener que ajustar el parser por proveedor real.
- ~~Etiquetado con ticketeadora~~ → **Ya no es un riesgo: la ticketeadora es manual, no se integra con el sistema.**

### Mapa de reutilización cross-proyecto

| Componente / patrón | Proyecto origen | Qué se reutiliza |
|---|---|---|
| Estructura base de Producto/Catálogo/Stock | `marihogar` | Catálogo (M2), Stock (M3) — ABM y alertas de stock mínimo ya resueltos |
| `Producto.unidadMedida` (enum Kg/Unidades/Gramos) | `delicias-naturales` | Base conceptual para `UnidadVenta` — se extiende con `UnidadCompra`+`FactorConversion` (pieza nueva) |
| Ventas + cuenta corriente de clientes (fiado) | `marihogar` | Base de `Venta`/CC cliente — se extiende con workflow Borrador→Facturada (pieza nueva) |
| Facturación AFIP (WSAA/WSFE, .p12) | `marihogar`, `delicias-naturales` | Patrón completo ya resuelto, mismo `AfipFacturacionService` |
| Proveedores + compras + actualización de stock | `marihogar` | Base de `Compra`/`Proveedor` — se extiende con TC propio + % descuento + importación (piezas nuevas) |
| `MovimientoCCProveedor` (ledger) | `vinosefue` | Reutilizado directo para cuenta corriente de proveedores |
| Caja / `CajaService` / `EgresoService` | `ganaderia` | Base de ingresos/egresos — se extiende con cierre diario y mensual como dos niveles separados |
| Gastos varios | `marihogar` | Base directa, se agrega clasificación caja chica/mensual |
| Presupuestos y cotizaciones en PDF | `marihogar` | Reutilizado directo |
| Entregas (seguimiento, estados) | `marihogar` | Base de `Entrega` — se extiende con markup configurable y distinción propia/tercerizada |
| Aumento masivo de precios (categoría/marca) | `marihogar`, `ShowroomGriffin` | Reutilizado directo, se agrega filtro por proveedor |
| Parser de importación Excel propietario | `contadores-bma-conversor` | Referencia para la migración de catálogo cuando se cotice esa fase futura (pospuesta, no forma parte de este alcance) |
| `Marca`/`Modelo` como catálogos separados | `ShowroomGriffin` | Reutilizado directo |
| Devolución de mercadería (stock, motivo, vínculo a venta) | `ShowroomGriffin` | Reutilizado directo — base de `DevolucionMercaderia` |
| Emisión de NC/ND AFIP | `marihogar`/`delicias-naturales` (extensión) | El circuito WSAA/WSFE ya resuelto se extiende para emitir NC vinculada a la factura original — no es una integración nueva desde cero |
| Búsqueda de producto en la pantalla de venta | Módulo Ventas (mismo proyecto) | El escaneo de código de barras extiende el buscador de producto ya existente en el flujo de venta, no crea uno nuevo |
| `CodigoProveedorProducto` (mapeo de código por proveedor) | Sistema actual del cliente (tabla `Codigo`) + patrón de catálogo simple ya usado en Entrega 1 (`ShowroomGriffin`) | No es reuse cross-proyecto en el sentido estricto — es la confirmación de que el propio sistema legacy del cliente ya modela el mismo problema con la misma forma; se reutiliza el patrón EF de catálogo simple ya usado para Marca/Modelo/Categoria |
| Importación de dataset limpio (Etapa 3, paso 2 del flujo 10) | `IListaPreciosProveedorImportService` (mismo proyecto, Entrega 2) | Mismo contrato preview→confirmar, aplicado a Producto/Cliente en vez de precios de proveedor — no es un patrón nuevo |

**Piezas sin precedente exacto (desarrollo nuevo, no reuse):** conversión de unidades compra↔venta con factor configurable, workflow Venta Borrador→Facturada editable, cuenta corriente de empleados con autoservicio (autorización a nivel de registro), cuenta corriente consolidada del negocio, dashboard de 3 niveles ("foto completa del negocio"), la resolución código de barras→producto en venta, **el proceso de limpieza/deduplicación batch de Etapa 3** (reglas de negocio específicas de este dataset, sin precedente en el historial del estudio) y **la clasificación ABC automática por ventas** (`IClasificacionAbcAutomaticaService`, sin precedente exacto — el análisis Pareto sobre `ItemVenta` es una pieza de cálculo nueva).

### Código de barras múltiple por producto (2026-08-21)

- Nueva entidad `CodigoBarrasProducto` (Domain, `SoftDestroyable`): `ProductoId` (FK), `Codigo` (string, único global — no compuesto con `ProductoId`, un código de barras real pertenece a un único producto), `Activo`. Mismo shape que `CodigoProveedorProducto` (patrón ya resuelto en Etapa 3) — reuse directo, no un tipo de entidad nuevo.
- `Producto.CodigoBarras` **no cambia** — sigue siendo el código propio de la impresora interna del cliente, 1 por producto.
- `ICodigoBarrasLookupService.BuscarPorCodigoAsync` se extiende: `WHERE Producto.CodigoBarras = @codigo OR EXISTS (SELECT 1 FROM CodigoBarrasProducto WHERE Codigo = @codigo AND ProductoId = Producto.Id)`.
- Migración EF: tabla nueva, aditiva, sin tocar `Productos`.
- Backfill de datos: extensión del script `tools/MigracionCatalogo/Program.cs` (mismo patrón que el modo `--solo-codigo-barras` ya construido) — para los artículos con más de un código `Tipo='B'`, inserta todos los códigos reales en `CodigoBarrasProducto` en vez de descartarlos como ambiguos.
- Fuera de alcance (declarado, no un gap accidental): ABM en pantalla para agregar/quitar códigos alternos manualmente — igual que `CodigoProveedorProducto`, se carga solo por script/migración por ahora.

## Historial de ajustes
- 2026-08-21: agregada `CodigoBarrasProducto` (1 a N, reuse directo del patrón `CodigoProveedorProducto`) para soportar productos con múltiples códigos de barras reales de fábrica. `Producto.CodigoBarras` sin cambios (sigue siendo el código propio, 1 por producto). Ver `1-analista-funcional.md` §10 y `4-presupuestador.md` para el presupuesto.
- 2026-07-30: Arquitectura v1 — mapa de reutilización cross-proyecto definido (marihogar como base estructural principal; delicias-naturales, vinosefue, ganaderia, ShowroomGriffin y contadores-bma-conversor como donantes puntuales). Identificadas 4 piezas sin precedente exacto que se presupuestan como desarrollo nuevo.
- 2026-07-30 (v2): agregadas entidades `NotaCreditoDebito` y `DevolucionMercaderia` (venta facturada anulable por NC, confirmado por el cliente). Reutilización directa del patrón de devoluciones de `ShowroomGriffin`. Migración de catálogo confirmada en ~17.000 filas — promovida a Etapa 3 independiente, ejecutada por lotes con reporte de errores. Dashboard redefinido como pieza de mayor prioridad de diseño (3 niveles), no un KPI-set genérico.
- 2026-07-30 (v3): agregada entidad `AjusteStock` (reutiliza patrón `StockController` de `ShowroomGriffin`) y campos `Producto.clasificacionABC`/`stockVerificado`, para soportar el plan de puesta a punto de stock inicial (el cliente no tiene stock confiable hoy). Riesgo técnico nuevo declarado: la validación de venta debe permitir stock negativo para productos no verificados, sin bloquear el mostrador.
- 2026-07-30 (v4): dos cambios. (a) Agregado `Producto.codigoBarras` + `EtiquetaService` + `CodigoBarrasLookupService` (código de fábrica o propio, etiquetado con ticketeadora, escaneo en venta) — riesgo declarado: se asume impresora estándar de Windows, a confirmar marca/modelo. (b) **Retirada la migración de catálogo de este alcance** (`CatalogoMigracionService` se saca) — se pospone a una fase posterior, condicionada a si Joaquín consigue acceso directo a la base de datos actual del cliente (segundo relevamiento) en vez de depender de un archivo Excel de formato desconocido.
- 2026-07-30 (v5): Joaquín confirmó que la ticketeadora es manual — no se integra con el sistema. Se retira `EtiquetaService` por completo (no hay generación/impresión de etiquetas). Queda solo `CodigoBarrasLookupService` + el campo `Producto.codigoBarras`. Riesgo de protocolo propietario (ZPL/EPL) ya no aplica.
- 2026-08-17 (v6): **Migración de catálogo retomada** — Joaquín consiguió acceso real al backup de SQL Server del sistema actual (121.691 artículos activos, corrige el volumen estimado de ~17.000). Agregada entidad `CodigoProveedorProducto` (reemplaza la idea de código externo único en `Producto`, confirmado por los datos reales que cada proveedor tiene su propio esquema sin relación entre sí). Extendidos `Producto` (`Bonificacion`, `ClasificacionABCSugerida`) y `Cliente` (`Domicilio`/`Localidad`/`Email`/`Notas`) con gaps confirmados frente al sistema real. Agregados `ICatalogoMigracionService` (import idempotente, mismo contrato que `IListaPreciosProveedorImportService`) y `IClasificacionAbcAutomaticaService` (ABC automática por Pareto sobre `ItemVenta`, ventana de 12 meses, sugerencia editable que nunca pisa el campo manual). El proceso de limpieza/deduplicación (paso 1 del flujo 10) es batch, fuera del ciclo de vida de la app web — no requiere servicio ni controller.
- 2026-08-17 (v7): implementada y QA-pasada la mitad "app" de Etapa 3 (`CodigoProveedorProducto`, `Proveedor` mínimo, extensión de `Producto`/`Cliente`, `ICatalogoMigracionService`, `IClasificacionAbcAutomaticaService` — commit `71daf36` en `migracion-catalogo`). Inmediatamente después, **Joaquín corrigió el enfoque de carga**: la migración del catálogo histórico va por script directo a la base, no por `ICatalogoMigracionService`/`MigracionCatalogoController` (esa carga es de una sola vez, no justifica mantener un flujo web de subida+preview+confirmar). **Se retiró `ICatalogoMigracionService`/`CatalogoMigracionService`/`MigracionCatalogoController` y sus vistas**, ya implementados — build limpio verificado tras la baja. Se conservan `Proveedor`, `CodigoProveedorProducto`, la extensión de `Producto`/`Cliente`, y `IClasificacionAbcAutomaticaService` (funcionalidad permanente, no exclusiva de la migración) — toda esa lógica la va a reutilizar el script de migración real. Aclaración de alcance explícita de Joaquín: esto es distinto de la futura importación de listas de precios de proveedor (flujo 3, recurrente, seguirá siendo por archivo vía pantalla cuando se implemente).
