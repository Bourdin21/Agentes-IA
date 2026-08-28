# Memoria - Disenador funcional

## Proyecto: desborder-sin-gluten
## Ultima actualizacion: 2026-08-25

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Revisado `docs/patrones/catalogo.yml` y `docs/*/definiciones/` del historial. Multiples matches directos de dominio y de codigo YA ENTREGADO — este es el proyecto con MAYOR reutilizacion confirmada del historial hasta ahora:

- **PAT-006 (Integracion ARCA/AFIP WSFEv1)** — codigo real en produccion (`marihogar`, con CAE real confirmado 2026-08-21). Se porta/adapta `AfipService.cs`/`AfipTokenCache.cs` tal cual, siguiendo el circuito documentado en `34-integracion-afip-arca.instructions.md` (certificado .p12, Punto de Venta tipo Web Services, orden de campos XML). Reutilizacion real, no solo de diseño.
- **PAT-003 (MetodoPago — venta con IVA + pago dividido en multiples medios)** — codigo real en produccion (`ShowroomGriffin`, replicado en `vinosefue`/`ganaderia`). Reutilizable para la Propuesta A.
- **PAT-004 (RowVersion manual MySQL)**, **PAT-008 (DataTables + filtros)** — patrones normativos estandar del estudio, aplicables como siempre.
- **delicias-naturales** (Gestion Comercial, 19 modulos, cerrado 2025) es el precedente de dominio MAS cercano — un comercio de productos "naturales" (dietetica/health foods) con Productos, Stock, Ventas, Compras, Clientes/Proveedores, y (segun `34-integracion-afip-arca.instructions.md`) **ya tenia su propia integracion AFIP** (version .NET Framework, `FacturacionAfipService.cs`). No hay `docs/delicias-naturales/definiciones/` detallado (proyecto anterior a la metodologia actual) pero el `metadata.md` confirma el dominio y el stack legado — sirve como validacion de que el estudio ya resolvio exactamente este tipo de negocio antes, aunque el codigo de esa epoca (.NET Framework 4.7.2 + EF6) no es portable directo al baseline BlankProject (.NET 10) salvo el contrato XML de AFIP.
- **ShowroomGriffin** (9 modulos, retail con variantes) es la referencia de arquitectura para la Propuesta A, escalada HACIA ABAJO (DesBorder es una dietetica chica, sin variantes de color/talle, sin devoluciones complejas, sin aumento masivo de precios).

### Las dos propuestas no son alternativas independientes — B es la Etapa 1 literal de A
Decision de diseño central de este proyecto: Propuesta B (solo facturacion) no es un sistema aparte que se descarta si despues quieren crecer — es exactamente el subconjunto de modulos de Propuesta A que resuelve el dolor mas urgente (facturar electronicamente en vez de a mano), construido sobre la MISMA base (BlankProject + AfipService + Identity). Si DesBorder arranca con B y despues quiere sumar stock/ventas/caja (Propuesta A completa), es un **Merge sobre sistema propio ya entregado** (agregar modulos), no una migracion ni un rewrite — mismo catalogo de productos, mismo circuito AFIP, misma base de usuarios. Esto es el argumento central de "posibilidad de crecimiento al ser Olvidata una software factory": el estudio no vende un producto cerrado, sigue construyendo sobre lo mismo que ya se entrego.

### Historias de usuario — nucleo compartido (ambas propuestas)

**HU-01 — Emitir comprobante electronico**
Como usuario, quiero cargar un comprobante (cliente/consumidor final, uno o mas conceptos con su %IVA) y emitirlo con CAE real de AFIP, para dejar de facturar a mano.
- Criterio: si AFIP rechaza el comprobante (error de validacion), el sistema muestra el motivo real devuelto por AFIP, no un error generico. El comprobante emitido queda disponible para reimprimir en PDF con QR (obligatorio AFIP).

**HU-02 — Catalogo de productos/conceptos**
Como usuario, quiero tener cargados los productos/conceptos que vendo (nombre, precio, %IVA) para no tipearlos de cero en cada factura.
- Criterio: alta/baja/edicion simple. En Propuesta A, el mismo catalogo alimenta tambien el stock; en Propuesta B es solo para facturar rapido, sin cantidad en existencia.

**HU-03 — Historial de comprobantes**
Como usuario, quiero ver el listado de comprobantes ya emitidos (fecha, cliente, total, CAE) para consultarlos o reimprimirlos.
- Criterio: DataTable server-side con filtro por fecha y por numero de comprobante (PAT-008).

**HU-04 — Usuarios y roles**
Como administrador, quiero que cada persona tenga su propio usuario para saber quien emitio cada comprobante.
- Criterio: minimo un rol Administracion; si hay mas de 1 persona (ver supuesto de "1 o 2"), un segundo rol Vendedor con acceso a facturar pero no a configuracion.

### Historias de usuario adicionales — solo Propuesta A (integral)

**HU-05 — Control de stock**
Como administrador, quiero que la cantidad en stock de cada producto se descuente automaticamente al facturar una venta, para no llevar el conteo a mano.
- Criterio: alerta visual cuando un producto queda por debajo de un minimo configurado. Ajuste manual de stock disponible (con motivo, auditado).

**HU-06 — Compra a proveedor**
Como administrador, quiero registrar una compra simple (proveedor, productos, cantidades, costo) para reponer stock y actualizar el ultimo precio de costo.
- Criterio: al confirmar la compra, se suma la cantidad al stock del producto. Sin workflow de estados complejo (a diferencia de ShowroomGriffin) — DesBorder es un comercio chico, alta directa.

**HU-07 — Venta con cobro (PAT-003)**
Como vendedor, quiero registrar una venta con uno o mas productos y uno o mas medios de pago (efectivo, tarjeta, transferencia), que genera el comprobante AFIP automaticamente al confirmar.
- Criterio: la suma de los pagos debe ser exactamente igual al total de la venta (regla PAT-003, bloqueante). Al confirmar, descuenta stock (HU-05) y emite el comprobante (HU-01) en la misma operacion.

**HU-08 — Cierre de caja del dia**
Como administrador, quiero ver el resumen del dia (total facturado, desglosado por medio de pago) para hacer el cierre de caja sin sumar planillas a mano.
- Criterio: el resumen se arma leyendo las ventas/pagos del dia (no requiere un "cierre manual" para verse) y muestra el total por medio de pago (efectivo/tarjeta/transferencia).

**HU-09 — Dashboard simple**
Como administrador, quiero ver de un vistazo las ventas del dia y los productos con stock bajo al entrar al sistema.

*(Etapa 2, solo Propuesta A)* **HU-10 — Reportes basicos**
Como administrador, quiero ver ventas por periodo y productos mas vendidos para entender que se mueve mas.

### Flujos de pantalla acordados
**Propuesta B:** Login → Nueva factura (elegir/cargar cliente → agregar conceptos con %IVA → emitir) → Historial de comprobantes.
**Propuesta A:** Login → Dashboard → Nueva venta (buscar producto con stock → carrito → medios de pago → confirmar, dispara stock + AFIP en la misma operacion) → Cierre de caja del dia. Mas las pantallas de Productos/Stock/Compras/Usuarios como ABMs estandar.

### ViewModels definidos
- `ComprobanteFormViewModel` (ClienteNombre/DNI-CUIT, CondicionIVAReceptor, Items[] con Concepto/Cantidad/Precio/PorcentajeIVA).
- `ProductoViewModel` (Nombre, Precio, PorcentajeIVA, + Stock/StockMinimo solo en Propuesta A).
- `VentaFormViewModel` (Items[], Pagos[] — reuso directo de PAT-003).
- `CierreCajaViewModel` (Fecha, TotalPorMedioPago[], TotalGeneral) — solo Propuesta A.

### Validaciones de UI acordadas
- No permitir emitir un comprobante sin al menos un item con precio > 0.
- (Propuesta A) No permitir vender una cantidad mayor al stock disponible.
- (Propuesta A) Suma de pagos == total de la venta, bloqueante (regla PAT-003).

### Contratos funcionales para Services
- `IAfipService` — reuso directo del contrato de marihogar (`EmitirAsync`, `ConsultarPuntosVentaAsync` como herramienta de soporte).
- `IComprobanteService` — nuevo, orquesta armar el request AFIP a partir del formulario y persistir el comprobante con su CAE.
- `IVentaService` (solo Propuesta A) — al confirmar, descuenta stock, valida pagos (PAT-003) y llama a `IComprobanteService` en la misma transaccion.

## Historial de ajustes
- 2026-08-25: primera version. Diseño con la mayor reutilizacion de codigo real confirmada del historial (PAT-006 marihogar, PAT-003 ShowroomGriffin). B definida explicitamente como subconjunto/Etapa 1 de A, no como alternativa aislada.
