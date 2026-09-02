---
name: cuenta-corriente-gaps-agosto
description: "Auditoría de bugs/gaps en cuenta corriente, ventas y pagos con saldo a favor (21/08/2026) y los fixes aplicados"
metadata: 
  node_type: memory
  type: project
  originSessionId: d598e711-73e1-4ffa-8130-c5cbb9032bfe
  modified: 2026-08-21T18:18:50.811Z
---

Auditoría pedida por el usuario el 2026-08-21 sobre el subsistema de cuenta corriente/pagos (ver también [[venta-total-drift]] y [[afip-generar-hardening]], hallazgos relacionados de la misma familia: "la Venta no tiene una única fuente de verdad confiable para su estado financiero").

**Hallazgos y qué se hizo con cada uno:**

1. **Race condition en `PagosController.RegistrarPago`** (🔴 causa raíz real, con casos confirmados en producción) — el cálculo de `GetMontoRestante`/excedente no tenía ningún lock, a diferencia de `VentaSequenceHelper.Lock` que sí protege la asignación de números de venta por el mismo motivo. Dos pagos casi simultáneos para la misma venta podían leer el mismo saldo restante "viejo" y ninguno generaba el movimiento de crédito por sobrepago aunque juntos superaran el total. Casos reales confirmados: Venta #9089 (Cliente 378, $6.400 sin reflejar) y Venta #8696 (Cliente 714, $9.400 sin reflejar), ambos posteriores al deploy del ledger de cuenta corriente (no es deuda histórica sin migrar). **Fix:** se agregó `_registrarPagoLock` (mismo patrón que `VentaSequenceHelper`) envolviendo todo el ciclo leer→decidir→guardar. **Datos:** se insertaron manualmente los 2 movimientos de Crédito faltantes.
2. **`VentasController.DeleteConfirmed` no revertía `MovimientoCuentaCorriente`** al borrar una venta completa (sí lo hacía `PagosController.EliminarPago` al borrar un pago individual). Sin casos materializados en datos todavía (el ledger tiene pocas semanas de vida), pero confirmado como gap real en el código. **Fix:** se agregó la misma lógica de reversión antes de borrar los pagos de la venta.
3. **`RegistrarPago` no validaba `venta.Estado` server-side** — la UI oculta el botón "Agregar Pago" salvo en Finalizada/Facturada, pero el controller lo aceptaba igual si alguien lo invocaba directo. **Fix:** guard agregado (bloquea pagos sobre ventas Ingresada).
4. **Las Notas de Crédito no interactúan con la cuenta corriente** — si una NC reduce lo que un cliente debía por una venta ya pagada, no se genera ningún ajuste automático (puede dejar un sobrepago fantasma). Se decidió NO automatizarlo (adivinar el monto correcto es riesgoso) — **fix:** aviso visual en `Views/Ventas/Details.cshtml` cuando una venta tiene una NC aprobada y pagos registrados, para revisión manual.
5. **Clientes activos duplicados por CUIT (7 pares)** — el usuario aclaró que es **intencional**: un mismo CUIT puede facturar para dos locales distintos del mismo dueño. **No tocar, no es un bug.**
6. **Resto de $2.090,30 en Venta #8716 (Cliente 759)**, de una corrección manual anterior incompleta (se borró un Pago SaldoFavor sin generar el reemplazo) — quedó **sin resolver**, no estaba en el alcance que confirmó el usuario. Si vuelve a aparecer, retomarlo.

**Estado al cerrar (2026-08-21):** los 2 fixes de datos ya están aplicados directo en producción (los movimientos de crédito insertados). Los 4 fixes de código están escritos y compilan limpio, pendientes del deploy programado para las 18hs de ese mismo día — verificar en la próxima sesión si ese deploy salió bien antes de asumir que estos fixes ya están viviendo en producción.

**Cómo aplicar:** si en el futuro aparece otro "sobrepago sin movimiento de cuenta corriente", primero descartar si es de ANTES del 2026-08-05 (deuda histórica sin migrar, esperable) — si es de después, es candidato a la misma race condition que esto debería haber arreglado; revisar si el fix del lock realmente se deployó.
