---
name: feedback-consulta-ceo-perfil-atipico
description: "No todo Build inicial de cliente nuevo debe recibir el descuento agresivo por defecto solo porque el ratio de reutilizacion califica numericamente — si el perfil del cliente muestra capacidad de pago establecida (B2B con trayectoria, ya paga por software equivalente), consultar a olvidata-ceo antes de aplicar el tier"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-30T14:07:10.252Z
---

Confirmado 2026-08-26 con el caso FABINCO (fabricante/distribuidor B2B de indumentaria laboral, 50 años de trayectoria) vs. Peras del Olmo (marca de diseño, venta directa al consumidor) — ambos leads tenian el MISMO ratio de reutilizacion calculado (R=81.8%, calificando objetivamente para Tier 1 / 30% de descuento por expansion agresiva), pero recibieron tratamiento de precio opuesto:

- **Peras del Olmo**: se aplico el Tier 1 (30%) por defecto, sin consulta — es el perfil tipico que la politica de descuento esta pensada para acelerar (cliente chico/mediano, retail directo al consumidor).
- **FABINCO**: se consulto explicitamente al agente `olvidata-ceo` antes de aplicar nada, y la recomendacion fue **NO aplicar ningun descuento** — cotizar a precio de lista completo. Motivo: empresa de 50 años, B2B, ya paga por un sistema equivalente hoy, tiene presupuesto de software real — no necesita precio subsidiado para cerrar, y regalarlo ahi es margen tirado sin necesidad.

**Regla derivada (ya incorporada como Paso 0.5 en `presupuesto-mvc.agent.md`):** antes de aplicar el tier de descuento calculado por defecto, revisar la clasificacion de perfil de cliente (B2B/B2C, escala, señales de capacidad de pago) hecha por el analista funcional. Si hay señales de perfil atipico (empresa establecida, ya paga por software, venta B2B con presupuesto propio de tecnologia), consultar explicitamente a `olvidata-ceo` antes de fijar el precio — no asumir que el calculo numerico de R/volumen es la ultima palabra. Si el perfil es el cliente chico/mediano tipico del pipeline (mayoria de los casos), aplicar el tier calculado sin necesidad de consulta.

**Como aplicar:** cuando el analista funcional detecte un lead con sitio web propio, años de trayectoria documentados, o venta B2B/por presupuesto (no venta de mostrador), marcarlo explicitamente como candidato a esta consulta antes de que el presupuestador fije el tier — no dejar que se aplique el default solo porque nadie lo señalo a tiempo.
