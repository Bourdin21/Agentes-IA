# Memoria - Analista funcional

## Proyecto: delicias-naturales
## Ultima actualizacion: sesion Dashboard Ampliado

## Contexto del sistema

**Stack:** ASP.NET MVC / .NET Framework 4.7.2 / EF 6 / MySQL  
**Entidades:** 26 | **Controladores:** 19 | **Migraciones EF:** 25+  
**Integraciones:** AFIP x5, SignalR, PDF  

### Modulos existentes confirmados
| Modulo | Controller | Estado |
|---|---|---|
| Dashboard | DashboardController | Existente — 2 reportes (Ventas, Productos) |
| Ventas | VentasController | Existente |
| Clientes | ClientesController | Existente |
| Productos | ProductosController | Existente |
| Pagos | PagosController | Existente |
| Compras | ComprasController | Existente |
| Proveedores | ProveedoresController | Existente |
| Cajas | CajasController | Existente |
| Pedidos | PedidosController | Existente |
| Facturas | FacturasController | Existente (AFIP) |
| Recetas | RecetasController | Existente |
| Solicitudes Ingreso Stock | SolicitudesIngresoStockController | Existente |

### Modelo de datos clave
- **Venta**: fecha, total, estado (Ingresada/Finalizada/Facturada), clienteId, pagos, productosVenta
- **ProductoVenta**: ventaId, productoId, cantidad, precioUnitario, descuento, recargo, subtotal, condIVA
- **Producto**: nombre, codigo, unidadMedida (Kg/Unidades/Gramos), precio, precioCompra, margen, stock, categoriaId
- **Pago**: fecha, monto, metodoPago (Efectivo/Credito/Debito/MercadoPago/Transferencia/SaldoFavor), ventaId
- **Cliente**: nombre, CUIT, condicionIVA, telefono, email, ventas[]
- **Compra**: fecha, estado (Pendiente/Recibida/Pagada), proveedorId, productosCompra, totalCompra
- **Caja**: tipo (Chica/Grande), estado (Abierta/Cerrada), montoInicial, montoFinal, movimientos[]
- **MovimientoCaja**: tipo (Egreso/Ingreso/Apertura/Cierre/Transferencia), origen (Venta/Compra/Gasto/Pedido)
- **Pedido**: fecha, estado (Pendiente/Aprobado/Rechazado/ListoParaRetirar), clienteId, ventaId, total

---

## Sesion: Dashboard Ampliado

### Pedido del cliente
> "Que el Dashboard tenga mas informacion. Filtro por producto (ej. almendras: kilos y plata, de-tal-fecha a tal-fecha). De clientes, no solo los mejores sino todos, cuanto compra cada uno, cuanto paga, cuanto debe."

### Decisiones confirmadas
| Pregunta | Decision |
|---|---|
| P1 — Metricas detalle producto | Hipotesis B: cantidad + monto + precio promedio + tabla clientes + grafico diario |
| P2 — Calculo deuda cliente | Hipotesis A: historico total. SaldoFavor reduce deuda. Si pagado > comprado → saldo a favor $X |
| P3 — Periodo vista clientes | Hipotesis A: siempre historico, sin filtro de fechas |
| P4 — Unidad cantidad producto | Hipotesis A: unidad de venta (bolsas, unidades, kg) |
| P5 — Bloques adicionales | Pedidos (Bloque F) + Rentabilidad (Bloque G) — ambos en alcance |

### Alcance funcional aprobado
| ID | Reporte | Ruta | Tipo |
|---|---|---|---|
| RF-D01 | Detalle por Producto especifico | Dashboard/Producto | Reporte nuevo |
| RF-D02 | Historial completo de Clientes con deuda | Dashboard/Clientes | Reporte nuevo |
| RF-D03 | Pedidos: estados y conversion | Dashboard/Pedidos | Reporte nuevo |
| RF-D04 | Rentabilidad: margen bruto real | Dashboard/Rentabilidad | Reporte nuevo |
| RF-D05 | Index Dashboard actualizado | Dashboard/Index | Mejora modulo existente |

### Deuda tecnica identificada
| ID | Descripcion | Tratamiento |
|---|---|---|
| DT-01 | ProductoSimpleViewModel.CantidadVendida es int; modelo tiene decimal. Trunca kg en informe existente. | Absorbida en RF-D01 sin costo adicional. Eleva M de 2.0h a 2.5h. |

### Reglas funcionales acordadas
- Deuda del cliente = SUM(Venta.Total) - SUM(Pago.Monto) sobre historial completo, nunca negativa
- Si totalPagado > totalComprado: Deuda = 0, SaldoAFavor = diferencia
- Pagos con MetodoPago = SaldoFavor se incluyen en totalPagado (reducen deuda)
- Reporte de Clientes no tiene filtro de fechas: datos siempre historicos
- Cantidad vendida se muestra en la unidad de venta del producto (kg, unidades, gramos)
- PrecioCompra en Rentabilidad es el precio actual, no el historico al momento de cada venta (limitacion del modelo — documentar en UI)

### Exclusiones confirmadas
- Exportacion a PDF o Excel de los reportes
- Acceso a reportes para roles distintos de Administrador
- Compras/Proveedores y Caja en Dashboard

## Historial de ajustes
- Sesion Dashboard Ampliado: analisis cerrado, 5 items aprobados. Presupuesto USD 100 acordado (lista USD 125, descuento fidelidad USD 25). Documento cliente en repo del proyecto.

