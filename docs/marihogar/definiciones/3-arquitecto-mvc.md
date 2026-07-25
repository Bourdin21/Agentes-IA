# Memoria - Arquitecto MVC

## Proyecto: marihogar
## Ultima actualizacion: 2026-07-24

## Definiciones vigentes

### Alcance funcional resumido

Sobre diseno aprobado (`2-disenador-funcional.md`) y analisis aprobado (`1-analista-funcional.md`): 18 modulos, Clean Architecture 4 capas (Domain/Application/Infrastructure/Web), ASP.NET Core MVC .NET 10 + EF Core 10 + MySQL, ya bootstrapeado desde BlankProject (repo `c:/Sistemas/marihogar`, solucion `MariHogar.*`). Base ya presente y **reutilizable sin cambios**: `ApplicationUser`, `AuditLog`, `Notification`, `SoftDestroyable`, `Repository<T>`, `AppDbContext` con auditoria automatica, `EmailService`, `ErrorNotifier`, `NotificationService`, `ExportService`, Users CRUD + roles Identity (M10 practicamente resuelto — solo falta seed de rol "Vendedor" ademas de "Administrador").

### Componentes por capa

#### Domain — entidades nuevas (heredan `SoftDestroyable` salvo lo indicado)

| Entidad | Modulo | Notas |
|---|---|---|
| `Categoria` | M2 | Nombre, activo. Usada tambien por M16 (criterio de aumento) y M8/E2 (categoria de calificacion del bot). |
| `Marca` | M2 | Nombre. |
| `Producto` | M2/M3 | Nombre, Descripcion, PrecioCompra, PrecioVenta, MarcaId, Modelo (texto), CategoriaId, StockMinimo, StockActual (campo desnormalizado, recalculado por `MovimientoStock`, nunca editado directo salvo ajuste). |
| `ProductoFoto` | M2 | ProductoId, Url/Path, Orden, EsPortada. Max 5 por producto (regla de negocio en Service, no constraint de BD). |
| `MovimientoStock` | M3 | ProductoId, TipoMovimiento (enum: Venta/Compra/Ajuste), Cantidad (+/-), OrigenId (VentaId/OrdenCompraId/null), Motivo (solo Ajuste), UsuarioId. **No hereda SoftDestroyable** (ledger inmutable, se revierte con contramovimiento). |
| `Lead` (E2) | M1 | Nombre, Telefono, ProductoConsultadoId, AnuncioOrigen (texto/id Meta), Estado (enum), VendedorAsignadoId. |
| `InteraccionLead` (E2) | M1 | LeadId, Tipo (MensajeBot/NotaVendedor), Texto, Fecha. No hereda SoftDestroyable (historial). |
| `Presupuesto` | M4 | LeadId (nullable), VendedorId, Estado (enum), FechaEnvio, VigenciaDias, Total (calculado, persistido para performance). |
| `PresupuestoItem` | M4 | PresupuestoId, ProductoId, Cantidad, PrecioUnitario. |
| `Venta` | M5 | PresupuestoOrigenId (nullable), VendedorId, Estado (enum), Total. |
| `VentaItem` | M5 | VentaId, ProductoId, Cantidad, PrecioUnitario, CantidadFacturada (para soportar facturacion parcial M7). |
| `PagoVenta` | M5 | VentaId, Metodo (enum: Efectivo/Transferencia/MercadoPago), Monto, Fecha. |
| `Entrega` | M6 | VentaId, Direccion, FechaProgramada, VendedorAsignadoId, Estado (enum), MotivoNoEntrega (nullable). |
| `ComprobanteAfip` | M7 | VentaId, TipoComprobante (A/B), CAE, VencimientoCAE, NumeroComprobante, Estado (Pendiente/Emitido/Error), DetalleError. |
| `ComprobanteAfipItem` | M7 | ComprobanteAfipId, VentaItemId, Cantidad. |
| `MovimientoCCLocal` | M11 | Fecha, Tipo (Ingreso/Egreso), Monto, OrigenTipo (Venta/PagoOC/Gasto), OrigenId, EsReversion (bool). No hereda SoftDestroyable (ledger). |
| `Proveedor` | M12 | RazonSocial, CUIT, Telefono, Email, Direccion. |
| `OrdenCompra` | M12 | ProveedorId, Estado (enum), Total. |
| `OrdenCompraItem` | M12 | OrdenCompraId, ProductoId, Cantidad, PrecioCompra. |
| `PagoOrdenCompra` | M12/M14 | OrdenCompraId, Metodo (enum: Efectivo/Transferencia/Cheque/Deposito), Monto, Fecha. |
| `Cheque` | M14 | PagoOrdenCompraId, Numero, Banco, FechaVencimiento, Cuota (30/60/90), Estado (enum), MotivoRechazo (nullable). |
| `MovimientoCCProveedor` | M13 | ProveedorId, Fecha, Tipo (Cargo/Pago), Monto, OrigenTipo (OrdenCompra/PagoOC), OrigenId, EsReversion (bool). No hereda SoftDestroyable (ledger). |
| `Gasto` | M18 | Categoria (enum: Alquiler/Servicios/Sueldos/Flete/Otro), Monto, FormaPago (enum), Fecha, Descripcion. |
| `CategoriaPreguntaBot` (E2) | M8 | CategoriaId (FK a `Categoria`), Preguntas (coleccion `PreguntaBot`). |
| `PreguntaBot` (E2) | M8 | CategoriaPreguntaBotId, Texto, Orden. |
| `MensajeWhatsApp` (E2) | M8 | LeadId, Direccion (Entrante/Saliente), Texto, Fecha, RawPayload (json, debug). No hereda SoftDestroyable (historial). |

Total: 24 entidades nuevas + 3 ya existentes reutilizadas (ApplicationUser, AuditLog, Notification) = consistente con la estimacion de "~22 entidades" del analisis (ajustado a 24 tras el detalle de items/pagos separados).

#### Domain — enums nuevos

`EstadoLead`, `TipoInteraccionLead`, `EstadoPresupuesto`, `EstadoVenta`, `MetodoPago` (compartido Venta/OC: Efectivo/Transferencia/MercadoPago/Cheque/Deposito — con validacion por Service de cuales aplican segun contexto), `EstadoEntrega`, `TipoComprobanteAfip`, `EstadoComprobanteAfip`, `TipoMovimientoStock`, `TipoMovimientoCC`, `EstadoOrdenCompra`, `EstadoCheque`, `CuotaCheque` (30/60/90), `CategoriaGasto`, `FormaPagoGasto`. Todos persistidos `HasConversion<int>()` (convencion ya establecida en `20-domain.instructions.md`).

#### Application — interfaces y DTOs nuevos

- Interfaces de Service por modulo (una por cada Service listado en Diseno > Contratos funcionales): `IProductoService`, `IStockService`, `IPresupuestoService`, `IVentaService`, `IEntregaService`, `IComprobanteAfipService`, `IAfipService` (contrato WSAA+WSFE, implementacion en Infrastructure), `IOrdenCompraService`, `IPagoOrdenCompraService`, `IChequeService`, `ICCLocalService`, `ICCProveedorService`, `ICajaService`, `IGastoService`, `IProyeccionFinancieraService`, `IAumentoMasivoPrecioService`, `IDashboardService`, `ILeadService` (E2), `IBotWhatsAppService` (E2), `IWhatsAppClient` (E2, contrato de bajo nivel — implementacion portada de BotPublicitario).
- DTOs de proyeccion (nunca exponer entidades a Web): `ProductoDto`, `VentaResumenDto`, `KpiDashboardDto`, `ProyeccionFinancieraDto`, `PrevisualizacionAumentoDto`, etc. — uno por consulta de listado/reporte, siguiendo patron ya usado por `ExportService`.
- Reutiliza `ServiceResult`/`ServiceResult<T>`, `DataTableRequest`/`DataTableResponse<T>` ya existentes en `MariHogar.Application`.

#### Infrastructure — servicios e integraciones nuevas

- Servicios de negocio: implementacion de todas las interfaces de arriba en `Infrastructure/Services/`, Scoped, registrados en `DependencyInjection.cs`.
- `AfipService` (M7): portado del patron WSAA+WSFE de `delicias-naturales` (`.p12`, token 24h cacheado). Requiere certificado digital del CUIT de marihogar (dependencia del cliente, ya documentada).
- `WhatsAppClient` + `MessagingService` (M8, E2): portados de `BotPublicitario/WhatsApp/` a .NET 10, adaptados a Clean Architecture (interfaz en Application, implementacion aqui). Incluye parseo del objeto `referral` del webhook de Meta para mapear anuncio -> producto.
- `ChequeAcreditacionHostedService` (M14): `IHostedService` (patron `AcreditacionCuotasHostedService` de ganaderia), corre 1 vez por dia, idempotente por `EstadoCheque != Acreditado`, dispara `INotificationService.CrearAsync` por cada cheque acreditado.
- Webhook receptor de WhatsApp (M8, E2): endpoint HTTP dedicado (`WhatsAppWebhookController` en Web, delega a `IBotWhatsAppService` en Infrastructure) con verificacion de firma HMAC del lado de Meta (mismo patron que BotPublicitario).

#### Web — controllers, views, sidebar

- ~16 controllers nuevos: `ProductosController`, `StockController`, `PresupuestosController`, `VentasController`, `EntregasController`, `ComprobantesAfipController`, `CCLocalController`, `ProveedoresController`, `OrdenesCompraController`, `CCProveedoresController`, `ChequesController`, `CajaController`, `GastosController`, `DashboardController` (reemplaza/extiende `HomeController` como landing autenticada), `AumentoMasivoPreciosController`, `LeadsController` (E2). Mas `WhatsAppWebhookController` (E2, sin UI, solo webhook) y `ConfiguracionBotController` (E2).
- Views siguiendo estructura ya presente (`Views/<Controller>/Index|Create|Edit|Details.cshtml`), DataTables server-side + filtros persistidos en sesion (patron definido en Diseno) en todos los listados.
- Sidebar (`Shared/_Layout.cshtml`) ampliado con secciones nuevas agrupadas por area (Ventas, Catalogo, Compras, Financiero, Configuracion), items condicionados por policy.
- Nuevas policies: `RequireAdministracion` ya existe (reutilizar para todo lo financiero/compras/config); agregar policy `RequireVentas` (Administrador + Vendedor) para modulos operativos compartidos.

### Modelo de permisos (roles/claims/policies)

- Roles Identity: `Administrador` (ya seedeado por template) + **`Vendedor` (nuevo, agregar a `SeedData.cs`)**.
- Policies nuevas/reutilizadas en `Program.cs`:
  - `RequireAdministracion` (ya existe, patron `RequireSuperUsuario`/`RequireAdministracion` del template): gatea Catalogo (alta/edicion/precios), Stock (ajuste manual), Compras, CC Proveedores, Cheques, Gastos, CC Local, Caja, Proyeccion, Aumento masivo, Usuarios, Configuracion bot.
  - `RequireVentas` (nueva, roles Administrador + Vendedor): gatea Leads, Presupuestos, Ventas, Entregas, Comprobantes AFIP.
- Ocultamiento de campos sensibles (precio de compra) para Vendedor: **no alcanza con CSS/ocultar en la vista** — el ViewModel/DTO que llega a la vista de Vendedor no debe incluir el campo (filtrado en el Service/mapping segun rol del usuario actual), evitando exposicion en el HTML renderizado o en llamadas AJAX.
- Dashboard: dos ViewModels distintos (`DashboardAdminViewModel`/`DashboardVendedorViewModel`, ya definidos en Diseno) resueltos por policy en el Controller, no por template condicional sobre el mismo modelo.

### Migraciones EF requeridas

**Si, multiples migraciones requeridas** (proyecto nuevo sobre base ya migrada `InitialCreate`). Estrategia: 1 migracion por grupo funcional cohesivo (no 1 por entidad, para mantener el historial legible), en el orden de dependencia:

1. `AddCatalogo` — Categoria, Marca, Producto, ProductoFoto, MovimientoStock, enum TipoMovimientoStock.
2. `AddRolVendedor` — seed del rol Vendedor (data migration, sin cambio de esquema).
3. `AddPresupuestosVentas` — Presupuesto, PresupuestoItem, Venta, VentaItem, PagoVenta + enums EstadoPresupuesto/EstadoVenta/MetodoPago.
4. `AddEntregas` — Entrega + enum EstadoEntrega.
5. `AddComprobantesAfip` — ComprobanteAfip, ComprobanteAfipItem + enums TipoComprobanteAfip/EstadoComprobanteAfip.
6. `AddCCLocal` — MovimientoCCLocal + enum TipoMovimientoCC (reutilizable tambien por CC Proveedor si se unifica el enum, a decidir en implementacion — sugerido mantener separado por claridad de dominio).
7. `AddCompras` — Proveedor, OrdenCompra, OrdenCompraItem, PagoOrdenCompra + enum EstadoOrdenCompra.
8. `AddCCProveedores` — MovimientoCCProveedor.
9. `AddCheques` — Cheque + enums EstadoCheque/CuotaCheque.
10. `AddGastos` — Gasto + enums CategoriaGasto/FormaPagoGasto.
11. `AddLeadsBot` (Etapa 2) — Lead, InteraccionLead, CategoriaPreguntaBot, PreguntaBot, MensajeWhatsApp + enums EstadoLead/TipoInteraccionLead.

Indices recomendados: `Producto.CategoriaId`, `Producto.MarcaId`, `MovimientoStock.ProductoId`, `Venta.Estado`, `Presupuesto.Estado`, `Cheque.FechaVencimiento` (usado por el job diario — consulta filtra por rango de fecha, indice obligatorio para performance a mediano plazo), `Lead.Estado`, `MensajeWhatsApp.LeadId`.

### Estrategia de pruebas funcionales

- Cubrir cada maquina de estados con sus transiciones validas e invalidas (checklist `26-checklists.instructions.md`, seccion workflow) — QA recorre Lead, Presupuesto, Venta, Entrega, OC, Cheque.
- Cubrir cada formulario con matriz de casos (valido, requeridos vacios, formatos invalidos, limites de negocio) segun pedido explicito del cliente de "formularios 100% OK" — detalle en `1-analista-funcional.md`/Diseno y materializado como casos de prueba en etapa QA (`6-qa.md`).
- Casos de integracion con caso ok / error / timeout para AFIP y WhatsApp (checklist integracion externa).
- Caso critico de concurrencia/idempotencia: job de acreditacion de cheques corriendo dos veces el mismo dia no debe duplicar acreditaciones ni notificaciones.
- Caso critico transaccional: fallo simulado en el paso de movimiento de stock durante confirmacion de venta no debe dejar la venta confirmada sin su movimiento (todo o nada).
- Verificar filtros persistidos en sesion en al menos 3 listados representativos (Productos, Ventas, Cheques) como prueba de patron transversal, no solo declarativa.

### Riesgos tecnicos activos

| Riesgo | Nivel | Mitigacion |
|---|---|---|
| Certificado ARCA (.p12) del cliente no disponible al iniciar M7 | Medio | Bloqueo declarado — M7 puede implementarse con el servicio mockeado/homologacion mientras se gestiona el certificado real; no bloquea el resto del sistema. |
| Numero WhatsApp dedicado no disponible al iniciar M8 (Etapa 2) | Medio | Etapa 2 es posterior a Etapa 1 — tiempo suficiente para que el cliente lo gestione. |
| Job `ChequeAcreditacionHostedService` en SMARTEASP | Bajo | Confirmado compatible por precedente de ganaderia en el mismo hosting. |
| Enum `MetodoPago` compartido entre Venta y OC con opciones que no aplican a ambos contextos (ej. MercadoPago no aplica a pago a proveedor) | Bajo | Validacion de negocio en el Service (no en el enum) — lista de metodos permitidos por contexto se filtra en el ViewModel/Controller. |
| `Producto.StockActual` desnormalizado puede desincronizarse si se edita `MovimientoStock` fuera del flujo de Service | Medio | Regla de arquitectura: **ningun codigo escribe `MovimientoStock` directo via `DbContext`** — siempre via `IStockService`, unico punto de verdad que actualiza ambos en la misma transaccion. |
| Facturacion parcial acumulativa (M7) requiere trackear `CantidadFacturada` por `VentaItem` de forma consistente entre comprobantes | Medio | Validacion server-side obligatoria en `ComprobanteAfipService`: cantidad solicitada <= (Cantidad - CantidadFacturada) del item, dentro de la misma transaccion que crea el comprobante. |

### Gate de aprobacion para pasar a presupuesto

Arquitectura cerrada y consistente con el presupuesto ya vigente (`4-presupuestador.md`, iteracion 6: E1 $700 / E2 $200 / Total $900, 18 modulos). No se detectan cambios de alcance respecto del presupuesto vigente — el presupuesto **no requiere reestimacion**. Habilitado el paso a Implementacion.

## Historial de ajustes
- 2026-07-24: Arquitectura tecnica v1 cerrada. Mapa completo de 24 entidades nuevas + reutilizacion de base BlankProject ya bootstrapeada (ApplicationUser/AuditLog/Notification/Repository/AppDbContext). 11 migraciones EF agrupadas por modulo funcional. Modelo de permisos con 2 policies (RequireAdministracion existente + RequireVentas nueva). Riesgos tecnicos y estrategia de pruebas definidos. Validado contra presupuesto vigente sin desvio de alcance — gate habilitado para Implementacion.
