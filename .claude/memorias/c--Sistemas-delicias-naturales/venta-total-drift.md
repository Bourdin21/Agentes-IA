---
name: venta-total-drift
description: Al menos 23 ventas en producción tienen Venta.Total desincronizado de la suma real de sus ProductosVenta.Subtotal
metadata: 
  node_type: memory
  type: project
  originSessionId: d598e711-73e1-4ffa-8130-c5cbb9032bfe
  modified: 2026-08-12T17:24:37.214Z
---

Detectado el 2026-08-12 investigando por qué el listado de Ventas mostraba "100% pagado" con saldo pendiente > 0 (ver también el fix de redondeo en `Venta.GetPorcentajePagado`, ese era el causante principal y ya está arreglado). De paso encontré un problema de datos separado y más profundo, sin arreglar todavía:

**Al menos 23 ventas activas en producción tienen `ventas.Total` (campo guardado) distinto de `SUM(productosventa.Subtotal)` de sus líneas activas**, por más de $0,50 de diferencia. Ejemplos reales: Venta #4065 (Total=849.811,39 vs líneas=829.120,00), #3962, #3849, #3828, #1874, #1754, #1715, #1601, #1539, #866, #647, #640, #474, #459, #299, #195, #192, #146, #139, #111, #102, #76, #48.

**Por qué importa:** `Venta.GetMontoRestante` usa el campo `Total` guardado, mientras que `Venta.GetTotal`/`GetPorcentajePagado` usan la suma de líneas (`ProductosVenta.Subtotal`). Si divergen, el "% pagado" y el "saldo pendiente" mostrados pueden contradecirse entre sí (uno dice pagado, el otro dice que falta, o al revés) — no es solo un problema de redondeo, en estos 23 casos la diferencia es real y de varios cientos/miles de pesos.

**Hipótesis de causa (sin confirmar):** probablemente ediciones de la venta (`VentasController.Edit`, agregar/quitar/modificar productos) que no volvieron a recalcular `Total` después de tocar `ProductosVenta`. No confirmé el mecanismo exacto — no llegué a revisar el código de `Edit` a fondo.

**Cómo aplicar:** si en el futuro aparece otro reporte de "el total no coincide" o "dice pagado pero falta plata" en Ventas, buscar primero si es este mismo drift (comparar `ventas.Total` vs `SUM(productosventa.Subtotal WHERE DeletedAt IS NULL)`) antes de asumir otra causa. Arreglar esto requiere decidir, venta por venta, cuál de los dos valores es el correcto (¿la edición fue legítima y el Total viejo quedó mal, o los productos se tocaron después de facturar/cobrar y el Total original es el que vale?) — no es un fix de una línea, necesita revisión caso por caso o al menos confirmar el mecanismo en `VentasController.Edit` antes de tocar datos.
