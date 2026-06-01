# QA — VinoSeFue — Memoria Acumulativa
ultima_actualizacion: 2026-05-30

## Sesiones

### Sesión 1 — 2026-05-29/30: Reconciliación deuda proveedor Area 520

**Punto cero:** 12/05/2026, saldo = $0 (confirmado por Rec.16431 que cierra el período anterior)

**Base de comparación:**
- Sistema (PROD): $4.151.951,50 de deuda total
- Ledger proveedor (al 29/05): $3.233.878
- DIFERENCIA: $918.073,50 (sistema sobreestima)

**CMP reconciliadas:**
- CMP-000003 (pre-12/5): pagada $3.499.456 efectivo. Saldo 0. Fuera de scope punto cero.
- CMP-000005: ? MATCH EXACTO. FAC R4-14535 - NCR R4-14536 = $3.085.008. Pago Rec.16729 = $1.655.879. Saldo $1.429.129 = proveedor.

**CMPs con discrepancia:**
- CMP-000004: Snap $1.473.290 / Real $1.520.120 / Proveedor FAC aprox $1.419.105 (R4-14539+14540+14617+14618) ? diff $101.015
- CMP-000006+007 (sin pedidos): sistema $793.964 vs FAC R4-14760+14761 ($385.644) ? diff $408.320
- CMP-000009 (Borrador): $399.720 sin correlato en ledger proveedor provisto (post-29/05 o pendiente facturación)

**Anomalías detectadas:**
- CMP-000006 y CMP-000007 no tienen pedidos vinculados (creadas manualmente)
- PED-000013: PrecioUnitCostoSnapshot × Cantidad ? SubtotalCosto en 2 items (posible aplicación de descuento)
- "corona 330 cc porron" (cerveza) incluida en CMP-000004 (proveedor vinos Area 520) ? $142.560 de proveedores mixtos

**Preguntas pendientes para el analista:**
1. ¿Cómo se crearon CMP-000006 y CMP-000007? ¿Son correctos los importes?
2. ¿"corona 330 cc porron" corresponde a Area 520 o a otro proveedor?
3. ¿CMP-000009 tiene FAC del proveedor posterior al 29/05?
4. ¿El pago CMP-000003 ($3.499.456) cubre deuda pre-27/03 no incluida en el extracto?
