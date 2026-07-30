# Memoria - Arquitecto MVC

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-07-30

## Definiciones vigentes

### Componentes por capa

- **Presentación**: Controllers/Views para Usuarios, Catálogo, Stock, Ventas, Facturación AFIP, Proveedores/Compras, Importación de listas, Caja, Gastos, CtaCteNegocio, CtaCteEmpleado, Presupuestos, Entregas, AumentoMasivo, Dashboard. DataTables para todos los listados; SweetAlert2 para confirmaciones; daterangepicker para filtros de fecha (Caja, Ventas, Compras).
- **Negocio (Services)**: `VentaWorkflowService`, `UnidadMedidaConversionService`, `RecargoCuotasService`, `ListaPreciosProveedorImportService`, `CuentaCorrienteEmpleadoService`, `CajaService` (diaria+mensual), `AfipFacturacionService` (incluye emisión de NC/ND), `AnulacionVentaService`, `DevolucionMercaderiaService`, `EntregaMarkupService`, `AumentoMasivoService`, `DashboardService` (3 niveles: día / salud financiera / tendencias), `AjusteStockService` (corrección manual auditada + venta con stock negativo permitido), `EtiquetaService` (generación de etiquetas imprimibles con código de barras), `CodigoBarrasLookupService` (resuelve producto por código escaneado en venta). *`CatalogoMigracionService` se retira de este alcance — la migración se pospone, ver `4-presupuestador.md`.*
- **Datos**: `AppDbContext` + repositorios EF Core / MySQL, siguiendo el patrón estándar del blankproject base (10-blankproject-base, soft delete + auditoría en todas las entidades).

### Entidades y configuraciones EF

Entidades nuevas (resumen — el detalle exacto de columnas se cierra en Implementación):

- `Producto` (nombre, codigo, marca, modelo, categoriaId, precioCompra, precioVenta, precioConDescuento, porcentajeIVA, unidadVenta [enum: Unidad/Peso/Metro/Bulto], unidadCompra [enum, nullable], factorConversion [nullable], stock, stockMinimo, clasificacionABC [enum A/B/C, nullable — usado en la puesta a punto de stock inicial], stockVerificado [bool, default false hasta que se cuenta o se ajusta manualmente]).
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

- Migración inicial: todas las entidades listadas arriba (incluye `NotaCreditoDebito` y `DevolucionMercaderia`).
- Migración de datos (Etapa 3, no EF-schema sino de contenido): importación del catálogo de productos existente del cliente (~17.000 filas) — formato de origen aún no confirmado, ver `1-analista-funcional.md` §Supuestos y dependencias. Se ejecuta por lotes, con reporte de éxitos/errores/duplicados (no una única transacción sobre 17.000 filas).

### Riesgos tecnicos activos

- **Venta con stock negativo permitido**: la validación de stock en `VentaWorkflowService` debe permitir confirmar una venta aunque el producto quede en negativo (solo aviso, no bloqueo) mientras `Producto.stockVerificado = false` — evitar que una regla de "no vender sin stock" (frecuente en ABMs de stock genéricos) bloquee el mostrador durante la transición de datos.
- **Conversión de unidades compra↔venta**: no hay entidad/patrón exacto reutilizable en el historial — es desarrollo nuevo (aislado en `UnidadMedidaConversionService` para minimizar impacto en el resto del sistema).
- **Workflow Venta Borrador→Facturada con edición previa**: mayor superficie de riesgo que el patrón estándar de venta+AFIP ya resuelto (que factura directo, sin estado intermedio editable).
- **Importación de listas de proveedor**: el mapeo de columnas puede no ser 100% genérico entre proveedores — riesgo de tener que ajustar el parser por proveedor real.

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
| Parser de importación Excel propietario | `contadores-bma-conversor` | Patrón de parser reutilizado para migración de catálogo (Etapa 3) e importación de listas de proveedor |
| `Marca`/`Modelo` como catálogos separados | `ShowroomGriffin` | Reutilizado directo |
| Devolución de mercadería (stock, motivo, vínculo a venta) | `ShowroomGriffin` | Reutilizado directo — base de `DevolucionMercaderia` |
| Emisión de NC/ND AFIP | `marihogar`/`delicias-naturales` (extensión) | El circuito WSAA/WSFE ya resuelto se extiende para emitir NC vinculada a la factura original — no es una integración nueva desde cero |

**Piezas sin precedente exacto (desarrollo nuevo, no reuse):** conversión de unidades compra↔venta con factor configurable, workflow Venta Borrador→Facturada editable, cuenta corriente de empleados con autoservicio (autorización a nivel de registro), cuenta corriente consolidada del negocio, dashboard de 3 niveles ("foto completa del negocio"), y la migración de catálogo en volumen (17.000 filas, formato aún no confirmado — mayor incertidumbre real que reuse).

## Historial de ajustes
- 2026-07-30: Arquitectura v1 — mapa de reutilización cross-proyecto definido (marihogar como base estructural principal; delicias-naturales, vinosefue, ganaderia, ShowroomGriffin y contadores-bma-conversor como donantes puntuales). Identificadas 4 piezas sin precedente exacto que se presupuestan como desarrollo nuevo.
- 2026-07-30 (v2): agregadas entidades `NotaCreditoDebito` y `DevolucionMercaderia` (venta facturada anulable por NC, confirmado por el cliente). Reutilización directa del patrón de devoluciones de `ShowroomGriffin`. Migración de catálogo confirmada en ~17.000 filas — promovida a Etapa 3 independiente, ejecutada por lotes con reporte de errores. Dashboard redefinido como pieza de mayor prioridad de diseño (3 niveles), no un KPI-set genérico.
- 2026-07-30 (v3): agregada entidad `AjusteStock` (reutiliza patrón `StockController` de `ShowroomGriffin`) y campos `Producto.clasificacionABC`/`stockVerificado`, para soportar el plan de puesta a punto de stock inicial (el cliente no tiene stock confiable hoy). Riesgo técnico nuevo declarado: la validación de venta debe permitir stock negativo para productos no verificados, sin bloquear el mostrador.
