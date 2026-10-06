---
name: la-platense-estado-entrega5
description: Estado de La Platense al 2026-10-06 — CR-01/CR-02 construidos sin deploy, AFIP sigue sin certificado, LP-037 abierto a proposito, produccion varias migraciones atras
metadata:
  type: project
---

Al **2026-10-06**, en la rama `entrega-1-migracion`: **CR-01** (venta sin factura) y **CR-02**
(facturación parcial con comprobantes 1:N) están construidos y medidos, en commits locales
**sin push y sin deploy**. Producción está **varias migraciones atrás**, por pedido explícito de
Joaquín.

**Why:** el acumulado local no se despliega hasta que Joaquín lo decida; cada ronda cierra con
commit local y lo declara. CR-02 se adelantó a la Entrega 5 por una razón con fecha de vencimiento:
mientras **no haya un CAE real emitido**, migrar de "un comprobante por venta" a 1:N es aditivo y
sin backfill; después del primero pasa a ser una reconstrucción de datos sobre documentos fiscales.

**How to apply:** al retomar este proyecto, antes de planificar nada:

- **AFIP sigue deshabilitado** — falta el certificado `.p12` y el CUIT real del cliente. Es el único
  gate de la Entrega 5 y puede llegar en cualquier momento. Los comprobantes nacen en `Pendiente` y
  eso es el estado **normal**, no una anomalía.
- **`LP-037` está ABIERTO y MEDIDO a propósito** en `tools/ArnesSeisSitiosRestantes`
  (**20 OK / 2 FALLADAS**). Esas 2 fallas son esperadas: el cierre de caja puede firmar totales en
  cero con escritores concurrentes, porque los gap locks de InnoDB conviven entre sí. **No arreglarlas
  ni silenciarlas, y no contarlas como regresión.** Necesita una decisión pendiente de Joaquín:
  lectura de bloqueo por rango vs. fila centinela por período.
- **`AnulacionVentaViewModel` e `IAnulacionVentaService` quedaron superados** por los comprobantes
  1:N: la nota de crédito se emite contra un **comprobante**, no contra la venta. Hay que ajustar ese
  contrato **antes** de construir el módulo 16.
- **Fuera de alcance y sin construir:** CR-03 (interés por tarjeta), CR-04 (plan de echeqs), CR-05
  (transferencia) y los impuestos de v2.
- Producción tiene **2.990 clientes** y **~112.000 productos** con actividad real: toda migración se
  piensa aditiva.

Las bases a no tocar nunca al verificar: `laplatense_dev`, los fixtures de QA (`laplatense_qa*`) y
producción (`site4now`). Los arneses abortan solos si la cadena las menciona.
