---
name: implementador-refactor-facturaventa
description: Historical record of the OrganismoIntermediario→Proveedor and Factura→FacturaVenta rename refactor (closed 2026-05-07)
metadata: 
  node_type: memory
  type: project
  originSessionId: 11114fe4-9ddd-4d2a-b493-b6fa9769b26d
  modified: 2026-07-22T17:02:52.459Z
---

Etapa cerrada 2026-05-07 en branch `main`: `OrganismoIntermediario` se absorbió en `Proveedor` (nuevo campo `Ambito`: Egresos/Ingresos/Ambos), y la entidad `Factura` (con sus items, cuotas, contador correlativo) se renombró end-to-end a `FacturaVenta`. `MovimientoStock.FacturaId` → `FacturaVentaId`.

Migración `20260507144532_RenameFacturaToFacturaVenta`: no destructiva (RENAME TABLE + populate + drop de `OrganismosIntermediarios`), pero `Down()` lanza `NotSupportedException` — es irreversible sin backup porque la consolidación pierde la diferenciación organismo/comprador.

**Why:** decisión arquitectónica "Option B" para simplificar el modelo (una FV referencia un único `ProveedorId` en vez de split organismo/comprador).

**How to apply:** si se toca código de Facturas/Proveedores, no buscar referencias a `Factura` u `OrganismoIntermediario` — ya no existen en código activo. El detalle completo y checklist de la etapa está en `docs/ganaderia/definiciones/5-implementador.md`, que se actualiza al inicio/cierre de cada etapa de implementación — leerlo para ver el historial de etapas más reciente antes de asumir el estado del modelo.

Ver también [[project-overview]] y [[docs-locations]].
