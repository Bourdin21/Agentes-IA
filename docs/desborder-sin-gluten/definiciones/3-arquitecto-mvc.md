# Memoria - Arquitecto MVC

## Proyecto: desborder-sin-gluten
## Ultima actualizacion: 2026-08-25

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Confirmado en `2-disenador-funcional.md`: mayor reutilizacion de codigo real del historial. Resumen para arquitectura:

- `AfipService`/`AfipTokenCache` (PAT-006) — portado de `marihogar` (.NET 10), adaptado a las credenciales/CUIT/Punto de Venta de DesBorder. Seguir `34-integracion-afip-arca.instructions.md` al pie de la letra (certificado con `X509KeyStorageFlags.MachineKeySet`, Punto de Venta tipo "Web Services", orden de campos XML verificado contra WSDL real).
- `VentaPago`/logica de pago dividido (PAT-003) — portado de `ShowroomGriffin`, solo para Propuesta A.
- `RowVersion` manual MySQL (PAT-004), DataTables+filtros (PAT-008) — estandar del baseline.

### Componentes por capa — nucleo compartido (B y A)
- **Domain**: `Comprobante` (Id, TipoComprobante enum con codigos AFIP reales, PuntoVenta, NumeroComprobante, ClienteNombre, ClienteDocTipo/DocNro, CondicionIVAReceptorId, Fecha, ImpNeto, ImpIVA, ImpTotal, CAE, CAEFchVto, Estado), `ComprobanteItem` (ComprobanteId, Concepto, Cantidad, PrecioUnitario, PorcentajeIVA, ImporteIVA), `Producto` (Nombre, Precio, PorcentajeIVA + campos de stock solo si Propuesta A).
- **Application**: `IAfipService`, `IComprobanteService`, DTOs de listado/detalle.
- **Infrastructure**: `AfipService` (portado), `ComprobanteService` (arma el request AFIP desde el ViewModel, persiste con CAE real), `AppDbContext`.
- **Web**: `ComprobantesController` (Nuevo/Historial), Identity scaffolding.

### Componentes adicionales — solo Propuesta A
- **Domain**: `Stock` (1:1 con Producto o campo directo — dado el tamaño chico del catalogo esperado, se resuelve como campo `CantidadStock`/`StockMinimo` directo en `Producto`, sin entidad separada — mas simple que el `Stock` polimorfico de ShowroomGriffin, no se justifica esa complejidad para una dietetica chica), `MovimientoStock` (auditoria de ajustes/ventas/compras), `Proveedor`, `Compra`/`CompraItem`, `Venta`/`VentaItem`/`VentaPago` (PAT-003).
- **Application/Infrastructure**: `IVentaService` (transaccion: descuenta stock + valida PAT-003 + llama `IComprobanteService`), `ICompraService` (suma stock + actualiza ultimo costo), `ICierreCajaService` (agrega `VentaPago` del dia por medio de pago, sin tabla propia — es una consulta, no un "cierre" persistido, salvo que el cliente pida bloquear el dia despues de cerrado — no incluido en este alcance).

### Entidades y configuraciones EF
- `Comprobante`: Id, TipoComprobante (enum, valor = codigo AFIP real), PuntoVenta, NumeroComprobante, ClienteNombre, ClienteDocTipo, ClienteDocNro, CondicionIVAReceptorId, Fecha, ImpNeto, ImpIVA, ImpTotal, CAE, CAEFchVto, Estado (Pendiente/Emitido/Error), CreatedAt.
- `ComprobanteItem`: Id, ComprobanteId (FK), Concepto, Cantidad, PrecioUnitario, PorcentajeIVA, ImporteIVA.
- `Producto`: Id, Nombre, Precio, PorcentajeIVA, (Propuesta A: CantidadStock, StockMinimo, UltimoCosto), CreatedAt.
- (Propuesta A) `Proveedor`, `Compra`/`CompraItem`, `Venta`/`VentaItem`/`VentaPago`, `MovimientoStock`.
- Roles Identity: `Administracion`, `Vendedor` (solo si se confirma 2 personas — con 1 persona, un unico rol alcanza) + `SuperUsuario` interno.

### Migraciones requeridas
- Propuesta B: migracion inicial con 2 tablas de negocio (`Comprobante`, `ComprobanteItem`) + Identity.
- Propuesta A: migracion inicial con 8 tablas de negocio (`Comprobante`, `ComprobanteItem`, `Producto`, `Proveedor`, `Compra`, `CompraItem`, `Venta`, `VentaItem`/`VentaPago`, `MovimientoStock` — se cuenta `VentaItem`+`VentaPago` como 2 tablas separadas segun PAT-003) + Identity.
- Index unico en `Comprobante.PuntoVenta + TipoComprobante + NumeroComprobante` (evita duplicar numeracion).

### Riesgos tecnicos activos
- **Condicion fiscal de DesBorder no confirmada** (Monotributo vs Responsable Inscripto) — define si emite Factura C (Monotributo) o A/B (RI), y si aplica `CondicionIVAReceptorId` de forma distinta. Bloqueante para configurar `AfipSettings` real — se resuelve en la demo/onboarding, no antes.
- **Certificado .p12 y Punto de Venta tipo Web Services**: dependencia dura del cliente (tramite en el portal AFIP/ARCA con su Clave Fiscal) — no lo puede resolver el estudio por ellos. Ver "Lo que necesitamos de tu parte" en el documento cliente.
- **Migrar de B a A mas adelante**: crear las tablas nuevas (Producto gana columnas de stock, se agregan Proveedor/Compra/Venta/MovimientoStock) es una migracion aditiva sobre la tabla `Producto`/`Comprobante` ya existente — no rompe comprobantes ya emitidos. Confirmar este punto explicitamente si el cliente pregunta "si empiezo con B, pierdo algo al pasar a A" — la respuesta es no.
- **Volumen de facturacion real desconocido** (no se sabe cuantas facturas/dia emite DesBorder) — si el volumen es alto, revisar cache de token WSAA (ya cacheado 24h en el patron reutilizado, deberia alcanzar sin ajuste).

## Historial de ajustes
- 2026-08-25: primera version. Arquitectura de Propuesta B como nucleo minimo compartido, Propuesta A como extension aditiva sobre el mismo `Producto`/`Comprobante` — confirmado que no hay migracion destructiva al crecer de B a A.
