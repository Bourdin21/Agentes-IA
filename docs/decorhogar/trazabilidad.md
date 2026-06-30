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
