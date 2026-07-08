# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-06-29 — analista-funcional
- Etapa: Discovery
- Cambio: Apertura del proyecto. Relevamiento inicial del proceso de ventas actual: Meta Ads → WhatsApp → local físico → factura + trazabilidad manual.
- Motivo: Cliente quiere reemplazar sistema actual y maximizar/agilizar ventas.
- Impacto en capas: Pendiente — depende de respuestas al cuestionario de discovery.
- Riesgos/supuestos: Posible integración con WhatsApp Business API (Meta); posible facturación electrónica AFIP. Ambos aumentan significativamente complejidad y costo. A validar con cliente.

### 2026-06-29 — analista-funcional
- Etapa: Análisis funcional cerrado
- Cambio: Cliente confirmó todas las opciones de mayor alcance (P1-B a P7-B). Sistema completo: CRM leads, catálogo, stock, presupuestador, ventas, entregas con cobro en domicilio, facturación AFIP, bot WhatsApp, dashboard, roles.
- Motivo: Cliente quiere solución integral desde v1.
- Impacto en capas: Presentación (10 módulos, responsive obligatorio), Negocio (4 máquinas de estados, reglas de stock, conversión presupuesto→venta), Datos (entidades: Lead, Producto, Stock, Presupuesto, Venta, PagoVenta, Entrega, Comprobante AFIP, Mensaje WhatsApp).
- Riesgos/supuestos: Integración AFIP y WhatsApp de muy alto impacto. Requieren gestión de cuenta Meta y certificado digital AFIP previo al arranque. Hosting debe ser VPS/cloud (no compartido).

### 2026-06-29 — analista-funcional (actualización de riesgos y stack)
- Etapa: Análisis funcional — actualización post-confirmación de infraestructura
- Cambio: Riesgo de hosting ELIMINADO. SMARTEASP confirmado compatible con webhook Meta (BotPublicitario corriendo) y AFIP WSFE (delicias-naturales corriendo). WhatsAppClient.cs de BotPublicitario es reutilizable. Stack definitivo cerrado.
- Motivo: Cliente informó que delicias-naturales usa AFIP WSFE en SMARTEASP y que BotPublicitario tiene webhook corriendo en el mismo servidor.
- Impacto en capas: Reduce riesgo de Infraestructura. Reduce tiempo de implementación M7 y M8 por reutilización.
- Riesgos/supuestos: Hosting OK. AFIP requiere nuevo certificado (.p12) del CUIT del cliente. WhatsApp requiere confirmar si ya tiene Business Manager activo.

### 2026-07-06 — analista-funcional
- Etapa: Discovery v2 + Análisis funcional v2
- Cambio: Relevamiento ampliado. Sistema actual del cliente: Contagram. Alcance: 18 módulos (vs 10 del análisis v1). Sistema de gestión comercial completo. Módulos nuevos: CC local, compras proveedores, CC proveedores, cheques 30/60/90 + job acreditación automática, caja mensual, gastos varios, proyección financiera, aumento masivo de precios. Módulos expandidos: catálogo (precio compra/venta/marca/modelo), stock (manual), ventas (impacto CC), ARCA (selección ítems parciales), dashboard (KPIs financieros).
- Motivo: El relevamiento v1 fue sobre el proceso de captación. El v2 relevó el sistema de gestión que Contagram cubre hoy, que es significativamente más amplio.
- Impacto en capas: Presentación (18 módulos, dashboard expandido), Negocio (6 máquinas de estado, job diario cheques, proyección financiera), Datos (~22 entidades, 1 IHostedService).
- Riesgos/supuestos: Job idempotente de cheques (patrón ganadería). Proyección financiera: fijar expectativas de precisión. Presupuesto v1 ($1,171) invalidado — rehacer completo.

### 2026-06-29 — presupuestador
- Etapa: Presupuesto
- Cambio: Presupuesto inicial ejecutado. 10 módulos, PERT completo con anclaje histórico. Total $1,378 (E1 $907 / E2 $471). Mantenimiento $400/año Plan PREMIUM.
- Motivo: Cliente confirmó alcance máximo (P1-P7 opción B). Se omitió diseño y arquitectura por alcance suficientemente definido en análisis funcional.
- Impacto en capas: Todos los módulos estimados por funcionalidad, no por capa.
- Riesgos/supuestos: AFIP documentado como excepción explícita. M4 y M1 sin referencia exacta — incertidumbre media declarada.

### 2026-06-29 — analista-funcional (eliminación riesgo Meta Business)
- Etapa: Análisis funcional
- Cambio: Confirmado que el cliente ya tiene Meta Business Manager activo. Riesgo de aprobación WhatsApp eliminado.
- Motivo: Cliente confirmó explícitamente.
- Impacto: Solo resta asociar número de teléfono dedicado al Business Manager existente para activar WhatsApp Business Cloud API. Sin trámites de verificación de empresa.

### 2026-07-06 — presupuestador (iteración 1)
- Etapa: Presupuesto v2
- Cambio: Presupuesto v2 ejecutado sobre análisis funcional v2 (18 módulos). Relevamiento de reutilización cross-proyecto previo. 13 E1 + 5 E2. Tasa M×$16.80. Total bruto $2,088. Neto $1,775. Tokens IA $190 (10%). **Reemplazado en la misma sesión por la iteración 2.**

### 2026-07-06 — presupuestador (iteración 2)
- Etapa: Presupuesto v2 — ajuste comercial
- Cambio: M9 Dashboard + M16 Aumento masivo + M17 Proyección movidos de E2 a E1. Sin Tokens IA. Tasa override M×$35 directo. E1 $3,500 / E2 $455. Total $3,955. Desc. 15%: −$593. Neto: $3,362. **Reemplazado por iteración 3 en la misma sesión.**

### 2026-07-06 — presupuestador (iteración 3)
- Etapa: Presupuesto v2 — recálculo por horas reales
- Cambio: Metodología 40h × $30/h = $1,200. E1 $1,060 / E2 $140. Neto $1,020. **Reemplazado por iteración 4.**

### 2026-07-06 — presupuestador (iteración 4)
- Etapa: Presupuesto v2 — ajuste de etapas
- Cambio: Traslado de $300 de E1 a E2. E1 $760 / E2 $440. Neto $1,020. **Reemplazado por iteración 5.**

### 2026-07-06 — presupuestador (iteración 5)
- Etapa: Presupuesto v2 — cierre comercial
- Cambio: Primer año PREMIUM incluido en $1,020. **Reemplazado por iteración 6.**

### 2026-07-06 — presupuestador (iteración 6 — vigente, listo para entrega)
- Etapa: Presupuesto v2 — precio final
- Cambio: Precio fijo E1 $700 / E2 $200 / Total $900. Sin descuento referido (eliminado). Primer año mantenimiento PREMIUM incluido en $900. Desde 2do año: $400/año.
- Motivo: Ajuste comercial final — precio directo sin descuento explícito.
- Riesgos/supuestos: M17 proyección financiera sin referencia de cierre real. M14 cheques — IHostedService en SMARTEASP confirmado por ganadería.
