---
name: afip-generar-hardening
description: "Incidente de factura duplicada en AFIP (comprobantes #4139/#4140) y el hardening aplicado a FacturasController.Generar"
metadata: 
  node_type: memory
  type: project
  originSessionId: d598e711-73e1-4ffa-8130-c5cbb9032bfe
  modified: 2026-08-04T21:51:11.335Z
---

El 2026-08-04 AFIP autorizó dos comprobantes (Factura A #4139 y #4140, Punto de Venta 5) para la misma venta del mismo cliente (Cliente Id 434, Venta #8867, $472.360,15 cada uno) — un duplicado real, con dos CAE válidos. Se confirmó consultando AFIP directamente vía `FECompConsultar` (ver [[verificar-vistas-razor]] para el approach general de diagnóstico en producción).

**Causa raíz:** `FacturasController.Generar` llamaba a AFIP (acción externa, irreversible) *dentro* de una transacción SQL local. La primera vez, AFIP autorizó el CAE (#4139) pero el guardado local posterior falló (la transacción hizo rollback) — el usuario vio un error genérico "Error al generar la factura" sin saber que AFIP ya había emitido el comprobante, así que reintentó, y esa segunda vez sí se guardó localmente pero como un comprobante nuevo (#4140), duplicando la operación ante AFIP.

**Fix aplicado (2026-08-03, ya en producción):**
- La llamada a AFIP quedó completamente fuera de cualquier transacción SQL.
- Chequeo de idempotencia: si la factura ya no está en estado Ingresado, no se vuelve a llamar a AFIP.
- El CAE se persiste con reintentos (`PersistirCaeConReintentos`, 3 intentos con un `ApplicationDbContext` nuevo por intento).
- Si el guardado falla igual tras los reintentos: log Fatal + mail urgente a Olvidata (reutilizando `NotificacionesHelper.EnviarCorreoError`) + mensaje al usuario que muestra el CAE/número de comprobante explícitamente y le dice que NO reintente.
- Actualizar `Venta.Estado = Facturada` quedó como best-effort, separado del guardado crítico del CAE.

**Pendiente/fuera de alcance:** el comprobante #4139 duplicado en AFIP sigue sin anular — hace falta que el usuario emita una Nota de Crédito A por $472.360,15 contra ese comprobante (o el #4140) para que el IVA/ingresos reportados a AFIP queden correctos. No lo hice yo porque emitir una Nota de Crédito es una acción real e irreversible ante AFIP.

**Cómo aplicar:** si aparece otra sospecha de comprobante duplicado o "perdido" en AFIP, el mismo método de diagnóstico (consultar `FECompConsultar` directo contra AFIP con un harness standalone, no hace falta tocar el código de la app) sirve para confirmar sin ambigüedad qué autorizó AFIP realmente, en vez de asumir a partir de la base local.
