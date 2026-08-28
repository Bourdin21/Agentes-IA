# Memoria - Arquitecto MVC

## Proyecto: marihogar
## Ultima actualizacion: 2026-08-16

## Definiciones vigentes

> Nota de consolidación (2026-08-16): las 8 secciones "Arquitectura v2" a "v9" (antes de nivel 2, apiladas por fecha de Change Request) pasaron a subsecciones de este único bloque — contenido sin resumir, ver `## Historial de ajustes` para el resumen de una línea por versión.

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

### Arquitectura v2 — Change request feedback primera demo (2026-07-27, CR-1 a CR-7)

Sobre diseño v2 aprobado (`2-disenador-funcional.md`). Solo se listan cambios/adiciones — todo lo no mencionado aquí sigue igual que en v1.

### Cambios de esquema (Domain + migraciones)

| Entidad | Cambio | Módulo |
|---|---|---|
| `OrdenCompra` | + `TipoComprobante` (enum nuevo `TipoComprobanteCompra`: A/B/C, nullable), `Facturada` (bool), `PorcentajeIva`/`MontoIva`, `PorcentajeIIBB`/`MontoIIBB`, `PorcentajeOtrosImpuestos`/`MontoOtrosImpuestos` (decimal, default 0). `Total` pasa a calcularse como Subtotal + suma de impuestos (antes era solo suma de líneas). | CR-1 |
| `Cheque` | + `FechaEmision` (DateTime, requerido). Migración de datos: cheques ya existentes sin este dato → `FechaEmision = FechaVencimiento - Cuota` (recalculado hacia atrás, ya que se conoce Cuota y Vencimiento). | CR-2 |
| `Cheque` | + `Notificado` (bool, default false) — evita que el job dispare la misma notificación de "venció, pendiente de acreditar" más de una vez por cheque. | CR-7 |
| `MetodoPago` (enum compartido) | + `TarjetaCredito=6`, `BancoCarrefour=7`. | CR-3 |
| `PagoVenta` | + `CantidadCuotas` (int?, solo si Metodo=TarjetaCredito — validación en Service, no en BD), `PorcentajeInteres` (decimal?, nullable = sin interés). | CR-3 |
| `CategoriaGasto` | **Breaking change de valores**: pasa de (Alquiler=1/Servicios=2/Sueldos=3/Flete=4/Otro=5) a (Sueldos=1/Impuestos=2/Luz=3/APR=4/Publicidad=5/Otro=6) — se reordena para que "Otro" quede último de forma consistente con el resto del proyecto. Requiere **migración de datos explícita** (no solo de esquema) sobre los `Gasto` ya existentes: mapeo Alquiler→Otro, Servicios→Luz, Sueldos→Sueldos, Flete→Otro, Otro→Otro, aplicado por `UPDATE` explícito ANTES de que el nuevo enum entre en vigencia (para no dejar valores int apuntando a la categoría equivocada por el reordenamiento). | CR-5 |
| `Proveedor` | + `Nombre`/`Apellido` (string?, persona física de contacto — distinto de `RazonSocial`), `CondicionIva` (enum nuevo `CondicionIva`: ResponsableInscripto/Monotributo/ExentoNoResponsable, según lo visto en el Excel real), `DomicilioFiscal`/`LocalidadFiscal`/`ProvinciaFiscal`/`CodigoPostalFiscal` (string?, separados de los ya existentes Dirección genérica), `Observaciones` (string?). | CR-6 (campos de Proveedor) |
| `MovimientoCCProveedor` | Nuevo `OrigenTipo="SaldoInicial"` para el movimiento de apertura al importar un proveedor con saldo previo (`Proveedor.SaldoInicial` decimal, + `FechaSaldoInicial` DateTime?, ambos nuevos). | CR-6 |

Migración EF: `AddImpuestosOCyChequeEmision` (CR-1+CR-2), `AddMetodoPagoTarjetaCarrefour` (CR-3, solo enum+columnas nullable, sin cambio de esquema en tablas existentes salvo columnas nuevas en `PagosVenta`), `AddCategoriaGastoV2` (CR-5, con script de `UPDATE` de datos incluido en la misma migración, antes de que el nuevo mapeo de valores quede vigente), `AddProveedorCamposFiscales` (CR-6).

### CR-4 — Endpoint público de descarga (riesgo de seguridad, mitigación obligatoria)

El link que se comparte por WhatsApp sale del sistema (lo abre el cliente final, sin login). Reglas de arquitectura:
- Nunca exponer el `Id` incremental de `Venta`/`ComprobanteAfip` en la URL pública (enumerable — cualquiera podría probar ids consecutivos y ver comprobantes ajenos).
- Cada comprobante compartido genera un **token opaco** (`Guid`, columna nueva `TokenDescargaPublica` en `Venta` y en `ComprobanteAfip`, generado la primera vez que se pide el link, reutilizado después — no un token por click).
- Endpoint nuevo `GET /Comprobante/Descargar/{token}` **sin `[Authorize]`**, `AllowAnonymous` explícito (única acción de todo el sistema con este atributo fuera de Login/AccessDenied) — devuelve solo el PDF, nunca datos de otras ventas, nunca un listado. Rate limiting de la policy `general` ya vigente aplica igual (protección básica contra fuerza bruta del token).
- El PDF servido por este endpoint es de solo lectura — no expone ninguna acción (editar/cancelar/etc.), reduce superficie de riesgo al mínimo.
- **Confirmado por el cliente (2026-07-27)**: cuando la venta no tiene `ComprobanteAfip` emitido, el PDF es un **remito de venta** nuevo (`IExportService`/`PresupuestoService`-style: QuestPDF, mismo patrón visual que el resto), sin CAE ni datos fiscales — solo ítems, cantidades, total y datos del cliente. Nuevo método `IVentaService.GenerarRemitoAsync`/`ComprobanteAfipService` decide cuál PDF servir (remito vs. factura AFIP) según si existe un `ComprobanteAfip` con Estado=Emitido para esa Venta.

### CR-6 — Importador de histórico (herramienta, no pantalla)

Mismo patrón que `tools/SeedTestData/` (proyecto de consola aparte, fuera de `MariHogar.slnx`, sin secretos hardcodeados): `tools/ImportarHistorico/`, lee los 4 `.xlsx` de `Importacion/` con `ClosedXML` (ya referenciado por `ExportService` del proyecto principal, se reutiliza el paquete) en vez de Excel COM (COM no es viable en el servidor de producción ni en CI, es solo lo que usó el orquestador para el análisis exploratorio). Orden de import: Proveedores → Productos derivados (por nombre no reconocido) → Compras → Ventas → Gastos. Idempotente por un marcador propio (no reutiliza el de `SeedTestData`), reporta al final cuántas filas por archivo se importaron vs. requirieron intervención manual (producto nuevo creado, categoría de gasto forzada a "Otro").

**Decisión del cliente (2026-07-27) — vaciar producción antes de importar (los Excel son la fuente de verdad, no lo que hay hoy cargado)**: antes de correr `ImportarHistorico`, se vacían en producción las tablas de las entidades que tienen dato en los Excel — incluye lo que quedó de la copia local→prod del 27/07 (datos ficticios) **y** lo que el cliente cargó explorando el sitio (su Proveedor "Prueba" + 2 OC reales), porque el propio cliente confirmó que todo eso es de prueba.
- **Tablas a vaciar** (en orden que respeta FK, `DELETE` no `TRUNCATE` por los `AUTO_INCREMENT` que conviene resetear también vía `ALTER TABLE ... AUTO_INCREMENT = 1` después de cada `DELETE`): `MovimientosCCProveedor`, `Cheques`, `PagosOrdenCompra`, `OrdenCompraItems`, `OrdenesCompra`, `Proveedores`, `MovimientosCCLocal`, `PagosVenta`, `VentaItems`, `Ventas`, `PresupuestoItems`, `Presupuestos`, `Gastos`, `MovimientosStock`, `ProductoFotos`, `Productos`, `Marcas`, `Categorias`.
- **Tablas que NO se tocan**: `AspNetUsers`/`AspNetRoles`/`AspNetUserRoles` (usuarios reales, incluida la cuenta real `tatoibiza@icloud.com`), `AuditLogs`, `Notifications`, `Entregas`/`EntregaIntentos` (0 filas, sin impacto), `ComprobantesAfip`/`ComprobanteAfipItems` (0 filas).
- **Salvaguarda obligatoria antes de ejecutar**: dump de respaldo de producción (`mysqldump` completo, no solo las tablas a vaciar) guardado localmente antes de correr el `DELETE`, por si hace falta revertir. Esta limpieza es una acción destructiva sobre producción — **requiere confirmación explícita del cliente en el momento de ejecutarla** (ya fue autorizada en principio el 2026-07-27, pero se re-confirma antes del `DELETE` real, no se ejecuta solo por haber quedado escrito acá).

### CR-7 — `ChequeAcreditacionHostedService`: de acreditar a notificar

Cambio de lógica interna (`EjecutarSiCorrespondeAsync`), sin cambio de la interfaz `IChequeService` ni de la máquina de estados ya definida (`Acreditar`/`Rechazar` siguen siendo las únicas transiciones válidas desde `Pendiente`, ya expuestas en la UI desde Sprint 4). El job pasa de `chequeService.AcreditarVencidosAsync(...)` a una consulta de solo lectura (`Cheques` con `Estado=Pendiente AND FechaVencimiento<=hoy AND Notificado=false`) + `INotificationService.CrearAsync` por cada uno + marcar `Notificado=true`. Ya no llama a ningún método que cambie `Estado`.

### Riesgos técnicos de este change request

| Riesgo | Nivel | Mitigación |
|---|---|---|
| CR-1: OC ya cerradas con Total recalculado (impuestos) pueden mostrar saldo distinto al histórico | Medio | Migración fija impuesto 0% en OC existentes — Total no cambia para nada ya cerrado, confirmado en Diseño. |
| CR-5: mapeo automático del enum viejo→nuevo de `CategoriaGasto` sobre datos ya en producción | Medio-Alto | Mapeo explícito por `UPDATE` documentado, revisado antes de aplicar — no una migración EF ciega de valores. Recomendado que el Administrador revise los 29 gastos ya cargados después de la migración. |
| CR-4: endpoint público sin autenticación | Medio | Token opaco no adivinable + `AllowAnonymous` explícito y aislado a un único endpoint de solo lectura + rate limiting ya vigente. |
| CR-6: 239 compras + 634 ventas con productos en texto libre sin catálogo 1 a 1 | Alto (esfuerzo, no seguridad) | Creación automática de Producto nuevo por nombre no reconocido, con precio de venta pendiente de completar — evita bloquear el import completo, documentado como intervención manual post-import. |
| CR-6: ventas históricas nunca se re-facturan ante AFIP | Bajo | Confirmado con el cliente (columna "ARCA" del histórico). Se importan sin `ComprobanteAfip` asociado, documentado explícitamente. |

### Gate de aprobación

Arquitectura v2 cerrada. Impacto de alcance real sobre lo ya presupuestado en Etapa 1 (no estaba contemplado) — **requiere presupuesto propio como change request**, ver `4-presupuestador.md`. No habilitado el paso a Implementación hasta que el cliente apruebe ese presupuesto (gate duro, `00-operativa-global.instructions.md`).

### Arquitectura v3 — CR-10/CR-11/CR-12: auditoría de columnas del histórico

Sobre diseño v4 (`2-disenador-funcional.md`). 3 campos nuevos, todos `string?` nullable, sobre entidades ya existentes — sin entidades nuevas, sin cambio de máquina de estados, sin impacto en servicios de dominio (`VentaService`/`OrdenCompraService`/`GastoService` no cambian su lógica, solo persisten un campo más).

### CR-10 — `OrdenCompra.PuntoVenta` + `OrdenCompra.NumeroComprobante`
- `OrdenCompra` gana `PuntoVenta` (`string?`, largo máx. 10) y `NumeroComprobante` (`string?`, largo máx. 20) — texto, no numérico, porque el histórico real trae ceros a la izquierda (ej. "0001-00001234") que un `int` perdería.
- Sin validación de unicidad ni de formato a nivel de BD (el punto de venta/número real de AFIP no lo emite este sistema para compras, es un dato que el Administrador transcribe de la factura del proveedor — mismo criterio de "dato informativo, no fuente de verdad fiscal" que ya aplica a `TipoComprobante`/`Facturada` de CR-1).
- Migración EF: `AddOrdenCompraNumeroComprobante` (2 columnas nullable, sin script de datos — nulo para todo lo ya cargado).

### CR-11 — `Gasto.Subcategoria`
- `Gasto` gana `Subcategoria` (`string?`, largo máx. 100).
- El importador de CR-6 (`tools/ImportarHistorico/Program.cs`, sección Gastos) se ajusta: hoy usa la columna "Subcategoría" del Excel como *fallback* de `Descripcion` cuando esta viene vacía (línea ~548-552 del script) — pasa a cargar `Subcategoria` = columna real siempre que tenga dato, sin tocar la lógica de `Descripcion` (que sigue igual). **CR-6 todavía no corrió contra producción** (pendiente del "todavía no" del cliente), así que este ajuste se aplica directamente al script antes de la corrida real, sin migración de datos sobre filas ya existentes.
- Migración EF: `AddGastoSubcategoria` (1 columna nullable).

### CR-12 — `Venta.NotaInterna`
- `Venta` gana `NotaInterna` (`string?`, largo máx. 500).
- **Punto de seguridad/alcance explícito**: `VentaService.GenerarRemitoPdfInterno` y `ComprobanteAfipService` (generación de PDF) **no leen este campo** — se verifica en Implementación que ningún template QuestPDF lo incluya, para que nunca aparezca en un documento que ve el cliente final. Mismo criterio de "dato interno vs. dato de cara al cliente" que ya separa `Venta.MotivoCancelacion` (interno) de lo que sí se imprime.
- El importador de CR-6 (sección Ventas) se ajusta para volcar la columna "Nota Interna" del Excel en este campo en vez de descartarla — no cambia la resolución ya definida de `PagoVenta` consolidado en Efectivo.
- Migración EF: `AddVentaNotaInterna` (1 columna nullable).

### Riesgos técnicos de esta ampliación
| Riesgo | Nivel | Mitigación |
|---|---|---|
| CR-12: filtración accidental de `NotaInterna` a un documento visible por el cliente | Medio | Verificación explícita en QA: generar un PDF de remito de una Venta con `NotaInterna` cargada y confirmar que no aparece en el PDF. |
| CR-10/11/12: los 3 campos son opcionales — riesgo de que el Administrador los deje vacíos y se repita el mismo problema de dato disperso que motivó este análisis | Bajo | Fuera de alcance técnico — es un hábito de uso, no un control de sistema. No se fuerza obligatoriedad porque en el histórico real ninguno de los 3 llega al 100% (CR-10 depende de si está Facturada; CR-11/12 no son siempre completados por el usuario real, ver fill-rate en `1-analista-funcional.md`). |

### Gate de aprobación
Arquitectura v3 cerrada. Sin impacto en lo ya presupuestado del Change Request #1 (CR-1 a CR-9) — es una ampliación propia, nueva, sobre el mismo change request en curso. **Requiere presupuesto propio**, ver `4-presupuestador.md`. No habilitado el paso a Implementación hasta que el cliente lo apruebe (gate duro).

### Arquitectura v4 — CR-14/CR-15/CR-16/CR-18: mejoras post-migración

Sobre diseño v5. **Sin migración EF** — todos los cambios son de comportamiento (cálculo/normalización), no de esquema.

- **CR-14**: `CCLocalService`/`CCProveedorService` calculan el saldo acumulado en memoria al armar el DTO de listado (ordenar por `Fecha, Id` ascendente, acumular `+Monto` en Ingreso / `-Monto` en Egreso). Sin índice ni columna nueva — costo O(n) sobre movimientos ya traídos, volumen bajo (decenas/cientos por cuenta).
- **CR-15**: cambio de JS puro en `OrdenesCompra/Details.cshtml` — sin impacto de capas de servidor.
- **CR-16**: `ProveedorService.CrearAsync`/`EditarAsync` y `ProductoService.CrearAsync`/`EditarAsync` aplican `.Trim().ToUpperInvariant()` a `RazonSocial`/`Nombre` antes de persistir. Sin cambio de validación (los `[StringLength]` ya existentes siguen aplicando sobre el valor normalizado).
- **CR-18**: nuevo bloque al final de `tools/ImportarHistorico/Program.cs` (después de Gastos) que calcula el saldo final de CC Local y de cada CC Proveedor con movimientos, y postea un movimiento de ajuste de signo contrario por el monto exacto del saldo, con `OrigenTipo="AjusteApertura"` (nuevo valor de texto libre, mismo patrón ya usado por `OrigenTipo` en el resto del ledger) y `OrigenId=0` (sin entidad de origen real). No participa de ninguna máquina de estados ni entidad nueva.

### Riesgos técnicos
| Riesgo | Nivel | Mitigación |
|---|---|---|
| CR-14: coherencia del saldo acumulado si dos movimientos comparten `Fecha` exacta | Bajo | Desempate determinístico por `Id` (orden de creación), mismo criterio en ambos servicios. |
| CR-18: el movimiento de ajuste podría interpretarse como un ingreso/egreso real en Caja mensual del período donde se lo postea | Medio | Fecha del ajuste = fecha de corte de la importación (no una fecha operativa real) — documentar en el reporte final del script para que el Administrador lo identifique fácilmente por su `Descripcion` explícita. |

### Gate de aprobación
Arquitectura v4 cerrada. Sin migración EF, sin impacto de esquema. Mismo criterio que CR-8/CR-9/CR-13 — sin gate de presupuesto nuevo, adenda de bajo esfuerzo sobre el Change Request #1 ya aprobado (ver `4-presupuestador.md`).

### Arquitectura v5 — CR-21/CR-22: doble precio + edición de precio/subtotal en Ventas

Sobre diseño v6. **Con migración EF** (a diferencia de la mayoría del lote anterior) — cambio de esquema real en `Producto` y `VentaItem`.

### CR-21 — `Producto`
- Rename de columna `PrecioVenta` → `PrecioEfectivo` (migración `RenameColumn`, sin script de datos — mismo valor, mismo tipo `decimal(18,2)`, sin pérdida).
- `Producto.PrecioLista` — propiedad C# de solo lectura (`=> Math.Round(PrecioEfectivo * 1.21m, 2)`), **no mapeada a EF** (`[NotMapped]` o `.Ignore()` en `AppDbContext`). Se expone en los DTOs de listado/detalle como un valor ya calculado, nunca se recibe desde el cliente en ningún request de escritura.
- Todo lugar que hoy lee `Producto.PrecioVenta` (búsqueda de producto en Ventas, `AumentoMasivoPrecioService`, `ProductoDtos`, `tools/ImportarHistorico/`, `tools/SeedTestData/`) pasa a leer `PrecioEfectivo` — rename mecánico, sin cambio de comportamiento (Aumento Masivo sigue ajustando el mismo campo, `PrecioLista` lo sigue automáticamente por ser calculado).

### CR-22 — `VentaItem` + `VentaService.ConfirmarAsync`
- `VentaItem` gana `Subtotal` (`decimal`) — migración aditiva con script de datos: `UPDATE VentaItems SET Subtotal = Cantidad * PrecioUnitario` para backfillear las 973 líneas ya existentes (dev y producción), de forma que ninguna Venta ya cerrada cambie de Total tras la migración.
- **`VentaService.ConfirmarAsync` — cambio de la regla de precio, con el punto de seguridad como foco central**:
  - Firma cambia para recibir el rol del usuario (o resolverlo internamente vía `ClaimsPrincipal`/`IHttpContextAccessor` ya disponible en el controller, pasado explícito al service — seguir el patrón ya usado en el proyecto para no introducir una dependencia nueva de `HttpContext` en la capa Infrastructure).
  - Si el rol es Administrador: usa `item.PrecioUnitario`/`item.Subtotal` tal como llegan en el `VentaInput` (con validación: ambos > 0, y una tolerancia — `Subtotal` puede diferir de `Cantidad×PrecioUnitario` a propósito, no se valida esa igualdad).
  - Si el rol NO es Administrador (Vendedor u otro): **sin cambios respecto del comportamiento actual** — `PrecioUnitario = producto.PrecioEfectivo` siempre recalculado server-side, `Subtotal = Cantidad × PrecioUnitario`, ignorando cualquier valor que venga en el payload. Esto se aplica **siempre**, sin importar qué mande el cliente — un Vendedor (o un request forjado a mano contra el endpoint) nunca puede colar un precio propio, aunque el campo exista en el DTO.
  - `venta.Total = Σ VentaItem.Subtotal` (antes: `Σ Cantidad×PrecioUnitario` calculado aparte) — cambio de la fórmula del total, ya cubierto por el backfill de la migración para que las Ventas históricas no cambien.
- `VentaInput`/`VentaItemInput` (Application DTOs) ganan `Subtotal` (`decimal?`, opcional — si no viene o el rol es Vendedor, se ignora y se calcula server-side).

### Riesgos técnicos
| Riesgo | Nivel | Mitigación |
|---|---|---|
| Bypass del control de precio por un Vendedor forjando el request (no vía UI) | **Alto** | Validación exclusivamente server-side por rol, nunca solo ocultar el input — el mismo criterio ya usado en el resto del sistema para roles (`[Authorize(Policy=...)]`, revalidación de reglas de negocio nunca confiadas al cliente). QA debe probar explícitamente un POST directo simulando un Vendedor con precio manipulado. |
| Migración de `Subtotal`: alguna de las 973 líneas ya existentes con `Cantidad`/`PrecioUnitario` nulos o inconsistentes | Bajo | Ambos campos son `NOT NULL` desde el modelo original, sin nulos posibles — el backfill es determinístico. |
| Rename de columna `PrecioVenta`→`PrecioEfectivo` en producción, con datos reales ya cargados (207 productos) | Bajo | `RenameColumn` de EF Core es una operación de esquema pura (no reescribe datos), mismo mecanismo ya usado sin incidentes en migraciones anteriores del proyecto. |
| `Producto.PrecioLista` desincronizado si en el futuro alguien agrega un campo de columna real con ese nombre por error | Bajo | Documentado explícitamente en el doc-comment de la entidad que es una propiedad calculada, nunca debe pasar a ser columna. |

### Gate de aprobación
Arquitectura v5 cerrada. **Con migración EF** (2 cambios de esquema: rename + columna nueva con backfill) — requiere presupuesto propio, ver `4-presupuestador.md`. No habilitado el paso a Implementación hasta aprobación (gate duro) — dado que el cliente ya dio la orden de implementar en el pedido original, se trata como aprobación implícita del alcance ya acotado con las 2 preguntas de diseño resueltas, sin volver a pedir luz verde de presupuesto por separado (mismo criterio que adendas anteriores de bajo monto).

### Arquitectura v6 — CR-24: precio de línea, Total editable, pagos posteriores en Ventas

Sobre diseño v7. **Sin migración EF** — CR-24.1/24.2/24.3 son cambios de JS puro (usan campos ya existentes de CR-22); CR-24.4 reutiliza `PagoVenta`/`MovimientoCCLocal` ya existentes, sin columnas nuevas.

- **CR-24.1/24.2**: `Ventas/Create.cshtml` — el handler `.btn-toggle-iva` deja de asignar `it.precioUnitario = it.ivaActivo ? it.precioLista : it.precioEfectivo` (valores fijos del producto) y pasa a calcular `precioConIva = precioUnitario × 1.21` en vivo sobre el valor actual del input de precio; se agrega un elemento de solo-lectura nuevo en la fila para mostrarlo. El subtotal por defecto (mientras no sea manual) usa `precioUnitario` o `precioConIva` según el estado del toggle.
- **CR-24.3**: fila de pie "Total" en el `tbody`/`tfoot` del carrito, con handler propio: `factor = nuevoTotal / totalActual`; cada línea recalcula `subtotal = subtotalActual × factor` (redondeado a 2 decimales), marcando cada línea como `subtotalManual = true` (ya fueron ajustadas explícitamente). Si `totalActual` es 0 (carrito vacío o todos los subtotales en 0), el reparto proporcional no es posible — se documenta como caso sin efecto (no hay nada que repartir).
- **CR-24.4**: nueva interfaz `IPagoVentaService` (Application) + `PagoVentaService` (Infrastructure) — mismo contrato y mismas reglas que `IPagoOrdenCompraService.RegistrarPagoAsync`, adaptado a Venta: recibe `VentaId` + lista de líneas de pago, valida que la Venta esté `Pendiente`/`PagadaParcial` (nunca `Pagada`/`Cancelada`), que el total a pagar no supere el saldo pendiente (`Total − Σ PagosVenta.Monto` ya registrados), crea `PagoVenta` + movimiento `Ingreso` en `MovimientoCCLocal` (mismo patrón que `ConfirmarAsync`, `OrigenTipo="Venta"`) en una transacción, y recalcula `Venta.Estado`. Nueva acción en `VentasController` (mismo patrón que `OrdenesCompraController.RegistrarPago`) + sub-formulario en `Ventas/Details.cshtml`.
- **CR-24.5**: cambio de una línea en el JS de `Ventas/Create.cshtml` — en el `success` del POST a `Confirmar`, `window.location.href` a `Ventas/Details/{id}` en vez de mostrar la pantalla de éxito in-page (se puede conservar el bloque de éxito como fallback si se prefiere no eliminar código, pero deja de ser el camino por defecto).

### Riesgos técnicos
| Riesgo | Nivel | Mitigación |
|---|---|---|
| CR-24.3: redondeo acumulado al repartir proporcionalmente puede dejar la suma con centavos de diferencia contra el Total tipeado | Bajo | Ajustar la última línea del reparto con el resto exacto (mismo patrón ya usado en `ParsearFormasPagoVenta` de CR-23 para no dejar diferencias de redondeo sueltas). |
| CR-24.4: doble registro de pago si el usuario hace doble click | Bajo | Deshabilitar el botón de confirmar mientras la request está en curso, mismo patrón ya usado en el resto del proyecto (`OrdenesCompra/Details.cshtml`). |
| CR-24.4: pagar de más (superar el saldo pendiente) | Medio | Validación server-side idéntica a `PagoOrdenCompraService` — nunca confiar solo en que el input del cliente no exceda el saldo. |

### Arquitectura v7 — CR-25/CR-26: comprobante AFIP editable + rediseño de PDFs + QR AFIP

Sobre diseño v8. **Sin migración EF** — CR-25 es un cambio de validación/UI, CR-26 es visual + una integración nueva (QR) sin persistencia adicional (el QR se genera on-the-fly a partir de datos ya guardados en `ComprobanteAfip`).

### CR-25 — `ComprobanteAfipService.EmitirAsync`
- Elimina el `return error` cuando `itemInput.Cantidad > pendiente` — pasa a ser informativo únicamente en la UI (el servidor ya no lo bloquea). El precio/subtotal pasan a tomarse de `itemInput` (ya no se fuerza `ventaItem.PrecioUnitario`) — mismo criterio de "campo abierto, sin comparación server-side contra la Venta" pedido explícitamente por el cliente ("tener la venta como referencia no como fuente de verdad"). **Nota de alcance**: a diferencia de CR-22 (Ventas), acá NO hay distinción de rol Administrador/Vendedor en el pedido — `RequireVentas` (policy ya vigente del controller) sigue siendo el único control de acceso, ambos roles pueden facturar con estos valores libres, igual que hoy pueden facturar sin ellos.
- `ComprobanteAfipController.Create` deja de redirigir cuando `precarga.Items.Count == 0` — se arma la precarga igual, con `CantidadPendiente` en 0 (el frontend ya no la usa como tope, solo como referencia informativa).
- Reparto proporcional de la fila "Total": mismo algoritmo ya implementado en `Ventas/Create.cshtml` (CR-24.3) — última línea absorbe el resto exacto del redondeo.

### CR-26 — Rediseño de `VentaService.GenerarRemitoPdfInterno` y `ComprobanteAfipService.GenerarPdfAsync`
- Encabezado con logo (`wwwroot/icons/isotipo_sin_anillo_color.png`, `.Image()` de QuestPDF) + nombre + CUIT (desde `AfipSettings.CUIT`, ya inyectado en `ComprobanteAfipService`; para el remito, que no tiene `AfipSettings` inyectado hoy, agregar la dependencia).
- Tablas: alinear las columnas Cantidad/Precio/Subtotal a la derecha (`.AlignRight()`), total en una caja destacada (`.Border()`/`.Background()`).

### CR-26 — Código QR de AFIP (RG 4291) — especificación exacta a implementar
Agregar el paquete NuGet **`QRCoder`** (generación de QR estándar, sin dependencias de red) a `MariHogar.Infrastructure`. En `ComprobanteAfipService.GenerarPdfAsync`, construir la URL exacta que exige AFIP:

```
https://www.afip.gob.ar/fe/qr/?p={Base64(JSON)}
```

JSON (nombres de campo exactos, sensibles a mayúsculas/minúsculas — no inventar variantes):
```json
{
  "ver": 1,
  "fecha": "yyyy-MM-dd",
  "cuit": 20331136132,
  "ptoVta": 1,
  "tipoCmp": 6,
  "nroCmp": 123,
  "importe": 1000.50,
  "moneda": "PES",
  "ctz": 1,
  "tipoDocRec": 80,
  "nroDocRec": 20123456789,
  "tipoCodAut": "E",
  "codAut": 12345678901234
}
```
- `cuit`: `AfipSettings.CUIT` (el emisor, no el receptor).
- `tipoCmp`: **usar directo `(int)comprobante.TipoComprobante`** — el enum `TipoComprobanteAfip` ya está definido con los códigos reales de AFIP (`FacturaA=1`, `FacturaB=6`, ver doc-comment de ese archivo), no hace falta un mapeo nuevo.
- `ptoVta`/`nroCmp`: `comprobante.PuntoVenta`/`comprobante.NumeroComprobante`.
- `importe`: `comprobante.Total`.
- `moneda`: literal `"PES"`, `ctz`: literal `1` (el sistema no maneja otra moneda).
- `tipoDocRec`/`nroDocRec`: **reusar `ResolverDocumentoAfip(comprobante.ClienteCUIT, comprobante.ClienteDNI)`**, ya existe en este mismo archivo (agregado en el fix de Consumidor Final) — mismos códigos (80/96/99).
- `tipoCodAut`: literal `"E"` (CAE, según la especificación — es el único caso que este sistema emite, nunca CAEA).
- `codAut`: `comprobante.CAE` parseado a número (el campo hoy es `string?`).
- Generar el PNG del QR con `QRCoder` (`QRCodeGenerator` + `PngByteQRCode`, o el helper equivalente de la versión del paquete que se instale), embeber con `.Image(bytes)` en el pie de la página, con un texto breve al lado ("Comprobante autorizado por AFIP") — visible pero no dominante en el layout.

### Riesgos técnicos
| Riesgo | Nivel | Mitigación |
|---|---|---|
| CR-25: facturar con datos que no coinciden con la Venta puede generar diferencias contables entre "lo vendido" y "lo facturado" | Medio (aceptado explícitamente por el cliente — es el objetivo del pedido) | Aviso informativo no bloqueante en pantalla cuando difiere de lo pendiente/vendido, para que quede claro que es una decisión consciente, no un error de carga. |
| CR-26: el QR mal formado (campo con nombre incorrecto, tipo de dato incorrecto) generaría un comprobante que AFIP validaría igual (el QR es informativo/de verificación, no se envía a AFIP — FECAESolicitar no lo incluye) pero que un lector de QR de un tercero rechazaría | Medio | Seguir la especificación exacta de arriba, sin improvisar nombres de campo. Verificar manualmente escaneando el QR de un comprobante real de prueba antes de dar el ítem por cerrado. |

### Arquitectura v8 — CR-27: Cuenta Corriente de Proveedores real (impuestos + pagos reales)

Sobre diseño (análisis v12, sin pasar por etapa de Diseño separada — mismo criterio ya usado para CR-23, corrección de datos históricos sobre un módulo ya en producción). **1 migración EF nueva** (`AddNotaInternaOrdenCompra`, columna nullable simple). El resto es corrección de datos vía `tools/ImportarHistorico/Program.cs` (sin cambio de esquema) + 2 cambios chicos de Application/Infrastructure/Web.

### CA-CR27.1/27.2 — `tools/ImportarHistorico/Program.cs`, nueva sección 2.5 + sección 3 modificada
- Nueva sección 2.5 (antes de la sección 3, Compras) carga `Informe Cuentas Corrientes Movimientos de Proveedores...xlsx` en 2 diccionarios indexados por la columna `Id`/`Id Compra` (misma numeración del sistema anterior que la sección 3 ya usa para agrupar líneas de `Informe de Compras` — verificado 239/239 antes de programar, sin faltantes):
  - `comprasTax[id]`: `Subtotal` = columna "Subtotal con Descuento"; `MontoIva` = suma de las 5 columnas IVA (2,5/5/10,5/21/27%); `MontoIIBB` = columna "Perc. IIBB"; `MontoOtrosImpuestos` = residual `Total − Subtotal − MontoIva − MontoIIBB` (absorbe Perc.IVA/Imp.Internos/Imp.Municipales/Sellos + cualquier redondeo del propio Excel — verificado que solo 4/239 filas no cierran exacto por su cuenta, diferencia inmaterial ~$136.300 combinados; mismo patrón "la última parte absorbe el resto" ya usado en CR-24.3/CR-25); `Total` = columna "Total compra" tomada tal cual, **autoritativa** (no se recalcula); `PuntoVenta`/`NumeroComprobante`/`Descripcion`.
  - `pagosPorCompra[idCompra]`: lista de `(Fecha, Metodo, Monto)` por cada fila `Operación="Pago"` con `Id Compra` válido y `Pagado > 0`. `Metodo` resuelto por `MapearMetodoPagoOC` (función nueva, texto de "Medio de Pago" — siempre uno de 8 valores fijos verificados antes de programar, nunca texto libre a diferencia de la Nota Interna de Ventas): "Caja del Local"/"Caja General" → Efectivo; "Banco Galicia"/"BANCO PCIA"/"cuenta dni PCIA" → Transferencia; "Cheque Propio"/"Cheque de Terceros" → Cheque (sin distinguir propio/terceros — el modelo no lo contempla y este archivo no trae número/banco real para poblar la sub-entidad `Cheque`); "Mercado Pago" → MercadoPago.
- En el loop existente de la sección 3 (agrupado por `idCompra`): `oc.Subtotal/MontoIva/MontoIIBB/MontoOtrosImpuestos/Total` se toman de `comprasTax[idCompra]` en vez de `subtotal = Σ Cantidad×PrecioUnitario` (sin impuestos, decisión CR-1 ahora superada); `PuntoVenta`/`NumeroComprobante` solo si `Facturada=true` (mismo criterio ya vigente en el modelo desde CR-10); `NotaInterna = Descripcion`. Fallback defensivo al subtotal-sin-impuestos si `idCompra` no estuviera en el diccionario (no debería ocurrir, cobertura 239/239 verificada).
- El bloque que creaba 1 `PagoOrdenCompra` ficticio en Efectivo por el Total completo (CR-19) se reemplaza por un loop sobre `pagosPorCompra[idCompra]`: un `PagoOrdenCompra` + `MovimientoCCProveedor` (Pago) real por cada pago encontrado, con `Fecha`/`Metodo`/`Monto` reales. Si la Compra no tiene ningún pago real, no se crea ninguno — queda con saldo pendiente real.

### CA-CR27.3 — Sección 6 (ajuste de apertura, CR-18): sub-bloque de CC Proveedores deshabilitado
El sub-bloque que llevaba a $0 el saldo remanente de cada proveedor (parche de CR-18 para cuando no había forma de conocer la deuda real) queda deshabilitado — el archivo nuevo da cobertura 100% real de las 239 Compras existentes, así que el saldo `Σ Cargo − Σ Pago` que queda tras CA-CR27.1/27.2 YA ES el saldo real (verificado que coincide con la columna "A pagar" del propio archivo, diferencia $0,05 por redondeo acumulado en 239 filas). Mantener el ajuste automático reintroduciría exactamente el problema que CR-27 vino a resolver. El sub-bloque de CC Local (Ventas/Gastos) **no se toca** — esos módulos no tienen todavía la misma cobertura 100% real.

### CA-CR27.4 — Mercado Pago habilitado para Proveedores
`MetodoPago.MercadoPago` agregado a `PagoOrdenCompraService.MetodosPermitidosOC` (guard server-side) y al diccionario JS `METODOS` de `OrdenesCompra/Details.cshtml`. Sin cambio de enum (el valor ya existía, solo se amplía dónde es válido).

### CA-CR27.5 — `OrdenCompra.NotaInterna`
Columna nullable nueva, mismo patrón exacto que `Venta.NotaInterna` (CR-12): nunca se lee en `VentaService.GenerarRemitoPdfInterno` ni en `ComprobanteAfipService` (no aplica a OC, pero mismo principio de "nunca en un comprobante"), visible/editable en `OrdenesCompra/Create.cshtml` (colapsable) y de solo lectura en `Details.cshtml`. Migración `AddNotaInternaOrdenCompra`.

### Riesgos técnicos
| Riesgo | Nivel | Mitigación |
|---|---|---|
| CA-CR27.1: `MontoOtrosImpuestos` calculado como residual podría dar negativo si el mapeo de columnas estuviera mal | Medio | Verificar con query real que ningún registro importado tiene `MontoOtrosImpuestos < 0` antes de dar el ítem por cerrado (ítem de la revisión de QA). |
| CA-CR27.3: deshabilitar el ajuste de apertura de CC Proveedores podría dejar un saldo real distinto al de "A pagar" si el archivo no cubriera el 100% de las Compras | Bajo | Verificado antes de programar que las 239 Compras del archivo nuevo coinciden 1 a 1 con las 239 ya importadas — cobertura completa confirmada, no parcial. |
| CA-CR27.4: agregar Mercado Pago a `MetodosPermitidosOC` sin revisar el resto del `HashSet` podría abrir sin querer otro método no autorizado | Bajo | Cambio de una sola línea, agregando únicamente `MetodoPago.MercadoPago` al `HashSet` existente — el resto de los métodos permitidos no se toca. |

### Arquitectura v9 — CR-32/CR-33/CR-34: precio dual + recargo tarjeta, edición de Venta, acreditación diferida

Sobre diseño v9. **1 migración EF combinada** (`PagoVenta` gana 3 columnas nullable + 1 enum nuevo, sin script de datos — los `PagoVenta` ya existentes quedan con `MontoBase=null`/`EstadoAcreditacion=Acreditado`/`FechaAcreditacionEfectiva=null`, comportamiento idéntico al actual).

### Domain
- Nuevo enum `EstadoAcreditacionPago { Acreditado = 1, Pendiente = 2 }` (mismo estilo que `EstadoCheque`).
- `PagoVenta` gana:
  - `decimal? MontoBase` — CR-32.2. Null cuando `Metodo != TarjetaCredito` (en ese caso `Monto` es directamente lo cobrado, sin recargo). Con tarjeta: `Monto = MontoBase * 1.21m` (mismo % que `Producto.PrecioLista`, CR-21 — se reutiliza el literal `1.21m` ya usado en 3 lugares del código, no hace falta un setting nuevo).
  - `EstadoAcreditacionPago EstadoAcreditacion` (default `Acreditado`) — CR-34.1.
  - `DateTime? FechaAcreditacionEfectiva` — CR-34.1, obligatoria solo cuando `Metodo == TarjetaCredito` (validado en Service, no en BD).

### Application/Infrastructure — `VentaService.ConfirmarAsync` (CR-32.2/32.3)
- Nueva validación: si `pago.Metodo == TarjetaCredito`, `pago.MontoBase` es obligatorio (> 0) y `FechaAcreditacionEfectiva` obligatoria; `Monto` se **calcula server-side** como `MontoBase * 1.21m` (nunca se confía en un `Monto` que viniera del cliente para Tarjeta — mismo criterio de "el servidor recalcula lo crítico" ya establecido en CR-22 para precio/subtotal).
- `venta.Total` sigue siendo `Σ VentaItem.Subtotal` (sin cambio — es el total "contado", CA-CR32.2 lo fija así explícitamente).
- `sumaPagos` para resolver `Estado` pasa de `Σ pago.Monto` a `Σ (pago.MontoBase ?? pago.Monto)` — así el ejemplo del cliente cierra ($250.000 base tarjeta + $50.000 efectivo = $300.000 = Total, `Estado = Pagada`, aunque el dinero real cobrado sea $352.500).
- **CA-CR32.3, cambio de comportamiento deliberado**: en vez de un único `MovimientoCCLocal.Ingreso` por `venta.Total` (código actual, línea ~370), se postea **un `Ingreso` por cada línea de pago** con `Metodo != TarjetaCredito` o (`Metodo == TarjetaCredito` y `EstadoAcreditacion == Acreditado` — nunca al confirmar, ver CR-34.2 abajo) — cada uno por su `Monto` real (incluye el recargo cuando corresponde). Cuando no hay tarjeta de por medio, la suma de los `Ingreso` por línea coincide exacto con el único `Ingreso` que se posteaba antes (mismo total, mismo período) — sin regresión para el caso sin tarjeta.
- Pagos con tarjeta pendientes de acreditar **no postean ningún `MovimientoCCLocal` al confirmar** — quedan solo como fila de `PagoVenta` con `EstadoAcreditacion=Pendiente`, el `Ingreso` se postea recién en `AcreditarPagoAsync` (CR-34.2).

### Application/Infrastructure — `PagoVentaService.RegistrarPagoAsync` (CR-24.4, mismos cambios que `ConfirmarAsync` arriba)
Los pagos posteriores (registrados desde `Ventas/Details` después de creada la Venta) pasan por el mismo camino nuevo — `MontoBase`/recargo server-side para Tarjeta, `EstadoAcreditacion=Pendiente` + `FechaAcreditacionEfectiva` obligatoria, sin postear `MovimientoCCLocal` hasta acreditar. El cálculo de "saldo pendiente" que ya hace este service (`venta.Total - Σ pagos existentes`) pasa a sumar `MontoBase ?? Monto`, igual que en `ConfirmarAsync` — un pago con tarjeta nunca debe poder "sobre-cubrir" el saldo por el recargo.

### Application/Infrastructure — nuevo `IVentaService.AcreditarPagoAsync(int pagoVentaId, string usuarioId)` (CR-34.2)
Mismo patrón que `IChequeService.AcreditarAsync`: valida `EstadoAcreditacion == Pendiente`, marca `Acreditado`, postea `MovimientoCCLocal.Ingreso` por `pago.Monto` con `Fecha = pago.FechaAcreditacionEfectiva` (no `DateTime.UtcNow` — el ingreso debe caer en el período contable de la acreditación real, mismo criterio de fecha histórica ya usado en varios lugares del proyecto). Acción Administrador-only (misma policy que `Cheques/Acreditar`).

### Application/Infrastructure — nuevo `VentaService.EditarAsync(int ventaId, VentaInput input, string usuarioId)` (CR-33)
- Guard de estado: `venta.Estado != Cancelada` (mismo criterio de "estados editables" ya usado en `OrdenCompraService`).
- **Mismo guard combinado que ya usa `CancelarAsync`** (server-side, nunca solo en la vista): `if (await TieneEntregaAsociadaAsync(ventaId) || await TieneComprobanteAsociadoAsync(ventaId)) return error` — ambos métodos privados **ya existentes** en `VentaService`, reutilizados tal cual, sin duplicar consultas ni inventar un criterio nuevo basado en `CAE != null` (los ~286 comprobantes históricos tienen `Estado=Emitido` con `CAE=null` — deben bloquear edición igual que ya bloquean cancelación). Se suma `TieneEntregaAsociadaAsync` porque editar cantidades/productos de una Venta con una Entrega ya programada (M6) desincronizaría qué se va a entregar — mismo espíritu que ya impide cancelar en ese caso.
- Dentro de una transacción: revierte `MovimientoStock` de los items actuales (mismo patrón que `CancelarAsync`, contramovimiento con `EsReversion=true` no aplica aquí porque `MovimientoStock` no tiene ese flag — se postea un movimiento de signo opuesto, igual que ya hace `CancelarAsync` con `venta.Items` al cancelar), reemplaza el set de `VentaItem` (mismo patrón simple de `OrdenCompraService.UpdateAsync`/`PresupuestoService`), aplica el stock de los items nuevos, recalcula `Total`. **No toca `PagoVenta`** — si el Total nuevo difiere del ya cobrado, `Estado` se recalcula solo (puede quedar `PagadaParcial` con sobrepago informativo, no bloquea el guardado — decisión de diseño explícita, CA-CR33.2).
- Mismo control de seguridad de precio/subtotal que `ConfirmarAsync` (`esAdministrador` resuelto solo en el Controller vía `User.IsInRole`) — no se relaja el gate de CR-22 para esta vía nueva.

### Web
- `Ventas/Create.cshtml`: quita el botón toggle IVA (CR-24.1), agrega columna "Precio tarjeta" (solo lectura, visible ambos roles) al lado de "Precio contado/transf" (input, edición Administrador-only sin cambio). Sección de pago: cuando se elige Tarjeta de Crédito, el campo de monto se relabelea "Monto base a cubrir" + texto en vivo "Total a cobrar con recargo: $X" (cálculo JS espejo del server-side, el server igual recalcula — nunca se confía en el cálculo del cliente) + nuevo campo de fecha "Fecha efectiva de acreditación" (sugerida hoy+18 días corridos, editable).
- Nueva `Ventas/Edit.cshtml`: reutiliza el JS/layout de `Create.cshtml` con los items/cliente/nota precargados desde `VentaDetailDto`. Acción `VentasController.Edit` (GET+POST), mismo patrón de mapeo que `OrdenesCompraController.Edit`.
- `Ventas/Details.cshtml`: tabla de Pagos gana columna de estado (badge "Acreditado" en verde / "Pendiente hasta dd/mm/aaaa" en amarillo) + botón "Marcar acreditado" (Administrador only, POST a la acción nueva) cuando `EstadoAcreditacion == Pendiente`. Botón "Editar" visible cuando `EstadoReal != Cancelada` y ningún comprobante tiene CAE (mismo criterio ya usado para mostrar/ocultar otras acciones condicionales en esta pantalla).

### Application — `ProyeccionFinancieraService` (CR-34.3)
El bloque `PagosVentaPorAcreditar` (ya agregado por CR-29, hoy filtra solo `Fecha > hoy`) amplía su `Where` con `OR (m.OrigenTipo == "Venta" pendiente de acreditar)` — dado que ahora el `MovimientoCCLocal` de un pago con tarjeta pendiente **no existe todavía** (CA-CR32.3/34.2: no se postea hasta acreditar), la fuente de este bloque deja de ser exclusivamente `MovimientoCCLocal` y pasa a incluir también una consulta directa a `PagoVenta` con `EstadoAcreditacion == Pendiente` (uniendo ambas fuentes: pagos con fecha futura ya posteados de CR-29, y pagos con tarjeta todavía sin postear de CR-34) — dato informativo, no cambia `IngresosProyectados`/`GastosComprometidos`/`TieneDeficit` (CA-N22 intacto).

### Riesgos técnicos
| Riesgo | Nivel | Mitigación |
|---|---|---|
| CR-32.3: cambiar de "1 Ingreso por Total" a "N Ingresos por línea de pago" podría descuadrar reportes de Caja que asuman 1 movimiento por Venta | Medio | Verificar con query real (`marihogar_dev`) que `SUM(MovimientoCCLocal.Monto WHERE OrigenTipo='Venta')` de una Venta multi-pago cierra exacto contra la suma esperada, antes y después del cambio, sobre datos reales ya migrados. |
| CR-33: revertir/reaplicar stock en `EditarAsync` sobre una Venta con Entrega ya asociada (M6) podría dejar el stock de la Entrega desincronizado | Bajo | Resuelto en el diseño: `EditarAsync` reutiliza el mismo guard combinado que `CancelarAsync` (`TieneEntregaAsociadaAsync` incluido) — no queda como riesgo abierto, ver sección de arriba. |
| CR-34.2: `AcreditarPagoAsync` posteando con `Fecha = FechaAcreditacionEfectiva` en el pasado (si el usuario la carga mal) podría alterar retroactivamente un período de Caja ya cerrado/reportado | Bajo | Mismo riesgo ya aceptado para cualquier fecha histórica cargada a mano en este proyecto (ej. `Fecha` de pago de CR-29) — sin mitigación adicional, es una acción manual del Administrador. |
| CR-32.2: recargo fijo del 21% hardcodeado (mismo literal que `PrecioLista`) no permite un recargo distinto por promoción/entidad financiera | Bajo | Fuera de alcance de este pedido — el cliente pidió específicamente "se suma IVA" (21%), no un recargo configurable. Documentado como límite conocido si en el futuro se necesita variar. |

### CR-55 (Arquitectura) — Nota de Crédito AFIP

**Domain**:
- `TipoComprobanteAfip` (enum) gana `NotaCreditoA = 3` y `NotaCreditoB = 8` — códigos reales AFIP (mismo criterio que el enum ya vigente: el valor ES el `CbteTipo`).
- `ComprobanteAfip` gana `ComprobanteAsociadoId` (`int?`, self-FK a `ComprobantesAfip.Id`, sin cascada — la factura original nunca se borra por borrar la NC, ni viceversa) y `Motivo` (`string?`, max 500).

**Application**:
- `AfipComprobanteRequestDto` gana `CbteAsociado` (`CbteAsociadoDto? { int Tipo, int PuntoVenta, long Numero }`, null salvo Nota de Crédito).
- Nuevo `GenerarNotaCreditoInput { int ComprobanteAfipId, string Motivo }`.
- `IComprobanteAfipService` gana `Task<ServiceResult<int>> GenerarNotaCreditoAsync(GenerarNotaCreditoInput input)`.

**Infrastructure**:
- `AfipService.ArmarFecaeSolicitarEnvelope`: agrega el bloque `CbtesAsoc` dentro de `FECAEDetRequest` cuando `request.CbteAsociado != null` — **orden de campos verificado contra el WSDL real de AFIP** (`delicias-naturales/Web References/ws_factura_afip/Reference.cs`, proxy generado, orden de propiedades = orden de schema): va inmediatamente después de `MonCotiz` y antes de `Tributos`/`Iva`. Estructura: `<CbtesAsoc><CbteAsoc><Tipo>N</Tipo><PtoVta>N</PtoVta><Nro>N</Nro></CbteAsoc></CbtesAsoc>` (Cuit/CbteFch quedan opcionales, no se envían — no son obligatorios en WSFEv1 para este caso).
- `ComprobanteAfipService.GenerarNotaCreditoAsync` (nuevo método, mismo esqueleto que `EmitirAsync`):
  1. Carga la factura original (`Include(Items)`), valida `Estado == Emitido` y que no tenga ya una NC asociada (`_db.ComprobantesAfip.AnyAsync(c => c.ComprobanteAsociadoId == facturaId)`).
  2. Crea un `ComprobanteAfip` nuevo replicando 1:1 `Items`/`ClienteNombre`/`ClienteCUIT`/`ClienteDNI`/`Total`/`PuntoVenta` de la original; `TipoComprobante` = `NotaCreditoA` si la original es `FacturaA`, `NotaCreditoB` si es `FacturaB`; `ComprobanteAsociadoId` = Id de la original; `Motivo` = el ingresado.
  3. Llama a `IAfipService.EmitirAsync` (mismo método ya existente, ahora recibiendo `CbteAsociado` poblado con Tipo=`(int)facturaOriginal.TipoComprobante`, PuntoVenta=`facturaOriginal.PuntoVenta`, Numero=`facturaOriginal.NumeroComprobante!.Value`).
  4. Si `Exito`: persiste CAE/Estado=Emitido de la NC **y**, en la misma transacción, decrementa `VentaItem.CantidadFacturada` de cada ítem de la Venta por la cantidad que cubría la factura original (nunca por debajo de 0 — guard defensivo aunque en este alcance nunca debería pasar, dado que la NC es siempre total).
  5. Si falla: mismo patrón ya existente (`Estado=Error`, `DetalleError`, reintentable vía el mismo `ReintentarAsync` ya genérico — no hace falta un método de reintento separado, `ReintentarAsync` ya opera sobre cualquier `ComprobanteAfip` en Error sin importar el `TipoComprobante`).
- `ComprobanteAfipService.GenerarPdfAsync`: agrega una rama para `TipoComprobante` Nota de Crédito — mismo layout de CR-43, cambia el título ("NOTA DE CRÉDITO") y el código de comprobante (003/008 en vez de 001/006).

**Web**:
- `ComprobantesAfipController` (o donde viva la acción "Facturar"/`Details`): nueva acción `GenerarNotaCredito(int comprobanteAfipId, string motivo)`, misma policy `RequireVentas` ya vigente en el controller (sin restricción nueva, confirmado con el cliente).
- Vista: botón + SweetAlert2 (motivo obligatorio) + badge "Anulada" en la factura cuando tiene NC `Emitido` asociada — mismo patrón visual que `btn-swal-confirm`/`Cancelar` ya usado en `OrdenesCompra/Details.cshtml`.

**Migración EF**: 1 nueva (`AddNotaCreditoAfip`) — 2 columnas nullable en `ComprobantesAfip` (`ComprobanteAsociadoId int NULL` + FK a sí misma, `Motivo varchar(500) NULL`), sin backfill (columnas nuevas, todo el histórico queda NULL = sin NC asociada, comportamiento correcto).

**Riesgos técnicos**:
| Riesgo | Severidad | Mitigación |
|---|---|---|
| Orden de campos XML incorrecto en `CbtesAsoc` → AFIP rechaza el request completo (no un error de negocio legible) | Medio | Verificado contra el WSDL real antes de implementar (ver arriba) — no es una suposición. Igual, probar con una NC real de bajo monto antes de confiar el flujo. |
| Revertir `CantidadFacturada` mal (ej. doble resta si se reintenta) | Medio | La reversión ocurre en el mismo paso atómico que marcar la NC `Emitido` (transacción única) — no puede ejecutarse dos veces para la misma NC porque `Estado` ya pasó a `Emitido` (guard de `ReintentarAsync` exige `Estado==Error` para reintentar). |
| Cliente confunde "Anular factura" con "Cancelar Venta" (son conceptos distintos: la NC anula el documento fiscal, la Venta en sí sigue existiendo y se puede refacturar) | Bajo | Cubierto en el texto del SweetAlert2 de confirmación — aclarar explícitamente que la Venta no se cancela, solo la factura. |

### CR-59 (Arquitectura) — Pagos con tarjeta de crédito a liquidar

**Domain**: sin cambios — `PagoVenta.Metodo`, `EstadoAcreditacion`, `FechaAcreditacionEfectiva` ya existen desde CR-32/34.

**Application**:
- Nuevos DTOs: `PagoTarjetaListItemDto { int Id, int VentaId, string? ClienteNombre, decimal Monto, int? CantidadCuotas, DateTime Fecha, DateTime? FechaAcreditacionEfectiva, string Estado, bool VenceProximo }`, `PagoTarjetaFiltro { EstadoAcreditacionPago? Estado, DateTime? AcreditacionDesde, DateTime? AcreditacionHasta }`, `PagosTarjetaPendientesDto { int Cantidad, decimal Monto }` (para la card de Dashboard).
- `IVentaService` gana `Task<DataTableResponse<PagoTarjetaListItemDto>> ListarPagosTarjetaAsync(DataTableRequest request, PagoTarjetaFiltro filtro)`.
- `IDashboardService` gana `Task<PagosTarjetaPendientesDto> ObtenerPagosTarjetaPendientesAsync()`.

**Infrastructure**:
- `VentaService.ListarPagosTarjetaAsync`: clon directo de `ChequeService.ListarAsync` — `_db.PagosVenta.Include(p => p.Venta).Where(p => p.Metodo == MetodoPago.TarjetaCredito)`, filtros por `EstadoAcreditacion`/`FechaAcreditacionEfectiva`, `VenceProximo` calculado igual que `ChequeListItemDto.VenceProximo` (`Estado == Pendiente && (FechaAcreditacionEfectiva - hoy) <= 7 días`).
- `DashboardService.ObtenerPagosTarjetaPendientesAsync`: `_db.PagosVenta.Where(p => p.Metodo == TarjetaCredito && p.EstadoAcreditacion == Pendiente)` → `Count`/`Sum(Monto)`. Sin filtro de período (mismo criterio que `ObtenerChequesPorVencerAsync`, que tampoco recibe `desde`/`hasta`).
- Ningún cambio en `AcreditarPagoAsync` — se llama tal cual desde la nueva acción del controller.

**Web**:
- `PagosTarjetaController` nuevo (`[Authorize(Policy = "RequireAdministracion")]`), clon 1:1 de `ChequesController` sin las acciones de Cheque específicas (`Rechazar` no aplica — `PagoVenta` no tiene ese estado): `Index()` (shell + combo N/A, no hay Proveedor), `GetData()` (POST, llama `ListarPagosTarjetaAsync`), `Acreditar(int pagoVentaId)` (POST, llama `_ventaService.AcreditarPagoAsync(pagoVentaId, VendedorId)`, redirige a su propio `Index` — no a `Ventas/Details`, a diferencia de la acción homónima que ya existe en `VentasController`, pensada para el caso "acreditar desde adentro de la venta").
- `Views/PagosTarjeta/Index.cshtml`: clon de `Cheques/Index.cshtml` — mismo DataTable server-side, mismo SweetAlert2 de "Acreditar" (sin el de "Rechazar").
- `_Layout.cshtml`: nuevo link de sidebar junto a "Cheques" (mismo ícono de referencia visual, `fa-credit-card` en vez de `fa-money-check-dollar` para diferenciarlo).
- `DashboardController`: nueva acción `GetPagosTarjetaPendientes()` (`[HttpGet, Authorize(Policy = "RequireAdministracion")]`, mismo criterio de defensa en profundidad que `GetChequesPorVencer`/`GetBalanceCaja`).
- `Dashboard/Admin.cshtml`: nueva card "Pagos con tarjeta por acreditar", mismo patrón AJAX independiente que el resto (`$.get` propio con `.done()`/`.fail()`).

**Migración EF**: ninguna — todos los campos consumidos ya existen en el esquema.

**Riesgos técnicos**:
| Riesgo | Severidad | Mitigación |
|---|---|---|
| Duplicar la acción "Acreditar" en 2 controllers (`VentasController.AcreditarPago` ya existente + la nueva de `PagosTarjetaController`) podría divergir si alguna cambia sin la otra | Bajo | Ambas llaman al mismo `IVentaService.AcreditarPagoAsync` sin duplicar lógica — la única diferencia es el `RedirectToAction` de destino (Details de la Venta vs. Index del listado nuevo), no hay 2 implementaciones del negocio. |
| Card de Dashboard sin filtro de período podría confundir si el usuario espera que respete el rango de fecha seleccionado arriba | Bajo | Mismo comportamiento ya establecido y aceptado por "Cheques por vencer" (tampoco respeta el filtro) — consistente con el resto de la pantalla, no es un caso nuevo. |

## Historial de ajustes
- 2026-08-27 — CR-59 (Arquitectura): ver sección completa "CR-59 (Arquitectura) — Pagos con tarjeta de crédito a liquidar" más arriba. Controller + vista clon de Cheques, 1 método de listado nuevo (`ListarPagosTarjetaAsync`) + 1 método de Dashboard (`ObtenerPagosTarjetaPendientesAsync`), ambos de solo lectura. `AcreditarPagoAsync` reutilizado sin cambios. Sin migración EF. Pendiente Presupuesto (gate cliente) antes de habilitar implementación.
- 2026-08-21 — CR-55 (Arquitectura): ver sección completa "CR-55 (Arquitectura) — Nota de Crédito AFIP" más arriba. `TipoComprobanteAfip` +2 valores (códigos reales AFIP), `ComprobanteAfip` +2 columnas (`ComprobanteAsociadoId`, `Motivo`). `AfipService` arma el bloque `CbtesAsoc` (orden verificado contra el WSDL real de AFIP). `ComprobanteAfipService.GenerarNotaCreditoAsync` nuevo, reutiliza `EmitirAsync`/`ReintentarAsync` ya existentes. 1 migración EF sin backfill. Pendiente Presupuesto (gate cliente) antes de habilitar implementación.
- 2026-08-11: Arquitectura v9 cerrada — CR-32 (`PagoVenta.MontoBase`, recargo 21% server-side, `MovimientoCCLocal` posteado por línea de pago en vez de por Total), CR-33 (`VentaService.EditarAsync` nuevo, bloqueado si hay CAE real), CR-34 (`PagoVenta.EstadoAcreditacion`/`FechaAcreditacionEfectiva`, `AcreditarPagoAsync` nuevo, ingreso diferido hasta acreditar). 1 migración EF combinada. Riesgos documentados, incluido el guard de Entrega asociada a revisar en `EditarAsync`. Pendiente Presupuesto (gate cliente) antes de habilitar implementación.
- 2026-07-30: Arquitectura v8 cerrada — CR-27 (Cuenta Corriente de Proveedores real: impuestos + pagos reales sobre las 239 OC históricas, reemplaza CR-19; Mercado Pago habilitado para Proveedores; Nota interna en OrdenCompra). 1 migración EF (`AddNotaInternaOrdenCompra`, columna nullable simple). Riesgos documentados. Sin gate de presupuesto nuevo para la corrección (mismo criterio que CR-23); Change Request #5 (USD 42) solo para las 2 capacidades nuevas.
- 2026-07-28: Arquitectura v4 cerrada — CR-14 (saldo calculado), CR-15 (cheque emisión default), CR-16 (mayúsculas), CR-18 (ajuste de apertura). Sin migración EF en ningún ítem. Riesgos documentados. Sin gate de presupuesto nuevo.
- 2026-07-27: Arquitectura v3 cerrada — CR-10 (Nº comprobante en OC), CR-11 (Subcategoría de Gasto), CR-12 (Nota interna de Venta). 3 migraciones EF nuevas, todas columnas nullable sin script de migración de datos (CR-6 todavía no corrió contra producción). Sin entidades nuevas ni cambio de servicios de dominio. Gate de presupuesto pendiente antes de habilitar implementación.
- 2026-07-27: Arquitectura v2 cerrada — change request feedback primera demo (CR-1 a CR-7). 4 migraciones EF nuevas (2 con script de migración de datos explícito, no solo de esquema). 1 endpoint público nuevo (`AllowAnonymous`) con mitigación de seguridad por token opaco. 1 herramienta de importación nueva (`tools/ImportarHistorico/`, mismo patrón que `SeedTestData`). Cambio de comportamiento del job de cheques (de acreditar a notificar). Riesgos técnicos documentados por ítem. Gate de presupuesto pendiente antes de habilitar implementación.
- 2026-07-24: Arquitectura tecnica v1 cerrada. Mapa completo de 24 entidades nuevas + reutilizacion de base BlankProject ya bootstrapeada (ApplicationUser/AuditLog/Notification/Repository/AppDbContext). 11 migraciones EF agrupadas por modulo funcional. Modelo de permisos con 2 policies (RequireAdministracion existente + RequireVentas nueva). Riesgos tecnicos y estrategia de pruebas definidos. Validado contra presupuesto vigente sin desvio de alcance — gate habilitado para Implementacion.
