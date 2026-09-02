---
name: project-overview
description: "What the Ganaderia system is, its architecture, and current status (in production)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 11114fe4-9ddd-4d2a-b493-b6fa9769b26d
  modified: 2026-07-23T14:25:35.611Z
---

Sistema de Gestión Ganadera para un cliente de **Olvidata Soft**, hecho a medida sobre la plantilla `BlankProject` (ASP.NET Core MVC, .NET 10, MySQL, EF Core Code First, Identity, Serilog).

**Arquitectura en capas:** `Ganaderia.Domain` (entidades/enums, sin dependencias) → `Ganaderia.Application` (interfaces/DTOs) → `Ganaderia.Infrastructure` (implementaciones, EF, servicios) → `Ganaderia.Web` (controllers/views/MVC). Convenciones de nomenclatura y estructura general heredadas de la plantilla están documentadas en el `README.md` del repo.

**Módulos funcionales del dominio ganadero:**
- Catálogos: Grupos (lotes/rodeos con categoría y stock mínimo), Rubros (categorías de gasto), Proveedores (unifica compradores de hacienda y proveedores de gastos, con `Ambito`: Egresos/Ingresos/Ambos).
- Stock de hacienda: movimientos (Stock inicial, Compra, Nacimiento, Muerte, Compensación de categoría según matriz de transiciones permitidas: Ternera→Vaquillona, Vaquillona→Vaca, Ternero→Toro).
- Facturas de venta (FV, antes "Factura"): numeración correlativa F-000001, ítems con Kilos totales + Precio por kilo. Desde la entrega [[analisis-mejoras-entrega2]] (2026-07-23): IVA / Ingresos Brutos / Otras Percepciones son 3 pares %+importe totalmente editables (ya no hay enum cerrado de IVA), y los Ingresos (cuotas de cobro) son totalmente personalizables por el usuario (fecha e importe libres, cantidad libre) en vez de generarse automáticamente por plazo fijo. Descuenta stock automáticamente; anulación/edición bloqueada si hay ingresos acreditados/rechazados.
- Ingresos (antes llamado "Cuotas", renombrado en la misma entrega para no confundir con pagos de egresos): Pendiente/Acreditado/Rechazado, acreditación automática diaria por hosted service (`AcreditacionIngresosHostedService`), regularización (Error de carga / Cobro posterior).
- Caja: saldo = acreditados ingresos - acreditados egresos, movimientos pendientes no afectan saldo (el campo `Estado` de `MovimientoCaja` sí es necesario — se muta a Pendiente cuando se rechaza un ingreso/pago ya acreditado, no es dead code).
- Egresos: con comprobantes adjuntos (PDF/JPG/PNG) guardados fuera de `wwwroot`, forma de pago múltiple vía `EgresoPagos` (agregado en migración `20260702181125_EgresoPago_PagosMultiples`).
- Dashboard (`/Dashboard`, control de stock puro) y Tablero Anual (`/Dashboard/TableroAnual`, control de dinero puro) son pantallas separadas desde 2026-07-23 — antes mezclaban ambas cosas. Dashboard: actividad de hacienda por grupo con filtro mes/año, kg vendidos y precio promedio por kg. Tablero Anual: saldo, ingresos/egresos por período (año o mes puntual), ingresos/pagos de egreso pendientes.

**Roles:** Productor (operativo completo), SuperUsuario (total + administración/auditoría).

**Estado:** el proyecto ya está en producción (commits "se paso a prod", "final del proyecto"). Dos refactors arquitectónicos importantes:
- [[implementador-refactor-facturaventa]]: `OrganismoIntermediario` se absorbió en `Proveedor`, y `Factura` se renombró a `FacturaVenta` (migración `20260507144532_RenameFacturaToFacturaVenta`, no destructiva, `Down()` no soportado). Cerrado 2026-05-07.
- [[analisis-mejoras-entrega2]]: entrega grande post-reunión con cliente — rename `Cuotas`→`Ingresos`, split Dashboard/Tablero Anual, impuestos e ingresos totalmente editables en Facturas, fix de bug de formularios, totales en listados. Cerrado 2026-07-23.

Documentación funcional/manual de usuario en [[docs-locations]].
