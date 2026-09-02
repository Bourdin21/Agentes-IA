---
name: meta-whatsapp-limites
description: WhatsApp Business Platform tiene 2 límites de envío independientes (cuenta vs. por-destinatario); el cuestionario del bot no consume ninguno
metadata: 
  node_type: memory
  type: project
  originSessionId: 6dad76aa-39ef-4734-885b-25074d2a71fb
  modified: 2026-07-28T21:00:05.717Z
---

Meta/WhatsApp Business Platform aplica **dos límites de envío completamente independientes**, no uno solo — confundirlos lleva a conclusiones erróneas sobre "cuánto margen hay":

1. **Límite de cuenta** (Messaging Limits/tier, lo que se ve en el panel de Meta: "Current 2000", umbral de 1.000 únicos/7 días para subir de tier) — cuántas conversaciones *nuevas* puede iniciar el número de negocio en 24hs. Sin relación con el error 131049.
2. **Límite por destinatario** (frecuencia de plantillas Marketing, dispara el error **131049** "healthy ecosystem engagement") — cada persona en WhatsApp tiene un tope propio de mensajes Marketing recibidos de **todas las empresas combinadas**, no solo la que consulta. Un contacto puede fallar por esto aunque la cuenta tenga margen de sobra en el punto 1. No es evitable del todo (estructural al outbound frío); el contacto que falla debe reintentarse recién días después, no el mismo día.
3. **Los mensajes de texto libre dentro de la ventana de 24hs post-respuesta del contacto (conversación "user-initiated") no consumen ninguno de los 2 límites** — solo las plantillas de business-initiated cuentan. Relevante para cualquier plan de volumen: el intercambio conversacional (preguntas de calificación, etc.) es efectivamente gratis en términos de estos límites; solo el envío inicial de la plantilla Marketing pesa contra ambos límites.

**Por qué:** investigado 2026-07-28 en [[olvidatasoft-crm]] a raíz de que el cliente vio margen de sobra en el panel de Meta pero seguía viendo el error 131049 en los logs — fuente: documentación pública de WhatsApp Business Platform, no un endpoint propio de Graph API. Ver `docs/crm-olvidata/logica-negocio-bot.md` y `docs/crm-olvidata/trazabilidad.md` (entrada 2026-07-28) para el detalle completo con las cifras reales observadas.

**Cómo aplicar:** al diseñar cualquier plan de volumen de campañas outbound (para este proyecto o para cualquier otro proyecto del estudio que use WhatsApp Business API), dimensionar contra el límite de cuenta (tier) para el volumen de *inicio* de conversaciones, no preocuparse por el cuestionario/conversación posterior, y aceptar que el 131049 es una tasa de fricción normal (no un bug) que baja con mejor segmentación pero no llega a cero.
