---
name: feedback
description: Corrections and preferences from Joaquín for working on BotPublicitario
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3852cee1-ac66-4cd4-bebe-7d515e611a03
originSessionId: 983b7554-673a-43f9-a21f-081f1cbf672d
---
## Never invent prices or business data
Do not fabricate product prices, service descriptions, or business-specific data. If prices/content are needed and not provided, ask the user.
**Why:** User caught invented ARS prices in catalog and asked "de donde sacaste esos precios?" — real prices were later provided.
**How to apply:** For any catalog, pricing, or business content, wait for user-provided data rather than estimating.

## .env must never be committed
**Why:** Explicitly documented in .gitignore and .env template comments. Contains live Meta API tokens.
**How to apply:** Before any `git add`, verify `.env` is excluded. Never suggest committing it.

## WhatsApp scripts: mencionar demo de 15 min, cierre pasivo
Los scripts deben mencionar que hay una demo de 15 minutos disponible, pero el cierre debe ser pasivo — el prospecto decide si responder, no se le pide fecha ni horario.
**Why:** El usuario quiere que el prospecto tome la iniciativa. Mencionamos la demo para que sepa qué hay, pero sin presionar ("¿Tenés 15 minutos esta semana?" está prohibido).
**How to apply:** Usar cierres del tipo: "Si te interesa ver cómo funciona, tengo una demo de 15 minutos lista. Respondé este mensaje si querés que te la muestre." / "Si te interesa, avisame por acá."
