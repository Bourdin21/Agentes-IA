---
name: analisis-mejoras-entrega2
description: "Post-client-meeting improvements delivery (2026-07-23) — Cuotas→Ingresos rename, Dashboard/Tablero Anual split, editable taxes/installments in Facturas, form-data-loss bug fix"
metadata: 
  node_type: memory
  type: project
  originSessionId: 11114fe4-9ddd-4d2a-b493-b6fa9769b26d
  modified: 2026-07-23T14:25:54.360Z
---

Entrega grande implementada 2026-07-23 en branch `main`, a partir de una reunión con el cliente. Análisis funcional completo en `docs/ganaderia/definiciones/6-analisis-mejoras-entrega2.md`, registro de implementación en `docs/ganaderia/definiciones/5-implementador.md` (última etapa).

**Alcance implementado (todo con build verde y migraciones aplicadas contra `ganaderia_dev` real):**
1. Fix bug de formularios: `asp-items` sin `asp-for` en 2 grillas dinámicas (`Egresos/_FilaPago.cshtml`, `Facturas/Create.cshtml`) — causa raíz acotada, no era un problema transversal como parecía a priori.
2. Egresos y Facturas: fila de totales en el listado según filtros aplicados (mecanismo `data-dt-sum-cols`/`data-dt-sum-target` agregado a `datatables-defaults.js`, reutilizable).
3. Rename físico end-to-end `Cuotas`→`Ingresos` (entidad `FacturaVentaCuota`→`FacturaVentaIngreso`, enum `EstadoCuota`→`EstadoIngreso`, controller/vistas/menú, migración `RenameCuotaToIngreso`).
4. Dashboard dividido: `/Dashboard` (stock puro) vs `/Dashboard/TableroAnual` (dinero puro), cada uno con sus propios filtros de período.
5. Facturas: IVA/IIBB/Otras Percepciones ahora son 3 pares %+importe editables (reemplaza enum `TasaImpuesto`, eliminado); Ingresos (cuotas de cobro) totalmente personalizables por el usuario en vez de auto-generados por plazo fijo. Migración `FacturaVenta_ImpuestosEditables`.

**Why:** el cliente pidió esto tras revisar el sistema en producción — quería separar control de stock vs dinero, más flexibilidad contable en facturas (impuestos argentinos reales: IVA + IIBB + percepciones), y notó que "Cuotas" se prestaba a confusión con pagos de gastos.

**Corrección importante durante el trabajo:** el análisis inicial proponía además eliminar el campo `Estado` de `MovimientoCaja` por considerarlo dead code (basado en grepear solo los sitios de creación). Se descartó al revisar `CuotaService`/`EgresoPagoService` completos: el campo sí se muta (Acreditado→Pendiente) al rechazar un ingreso/pago ya acreditado. **Lección:** al analizar si un campo es "siempre el mismo valor", no alcanza con grepear las creaciones — hay que revisar también las mutaciones en flujos de rechazo/regularización.

**How to apply:** si se toca código de Facturas/Cuotas/Dashboard, no asumir la estructura descripta en el análisis original de la reunión sin este documento — varios campos y DTOs cambiaron de nombre. Pendiente: smoke test manual end-to-end y extender `docs/qa/plan-qa-etapa7.md` con casos de esta entrega (ver checklist de salida en `5-implementador.md`).

Ver también [[project-overview]] y [[docs-locations]].
