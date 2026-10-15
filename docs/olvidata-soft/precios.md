# Precios de lista — Olvidata Soft

**Fuente única de precios** (Joaquín, 2026-10-15). Todo monto de lista de Olvidata vive acá y en ningún otro archivo: `olvidata-ceo` es el dueño (lo edita), `olvidata-sales`, `olvidata-marketing` y `olvidata-cm` apuntan acá. `scripts/doctor.py` marca error si un agente de negocio vuelve a tener un monto en USD.

Fuera de esta regla: costos de proveedores (`olvidata-infra`, pauta en `olvidata-cm`) y las fórmulas de estimación de módulos (`olvidata-presupuesto-bot`, que salen de la instrucción 27). Respaldos y research de mercado: `docs/referencia/`.

**Condiciones generales:** todos los precios son **+ IVA** (confirmado 2026-09-19). Se pagan en **pesos al tipo de cambio del día del pago** (Landing: dólar blue del día del pago). Anticipo del 50% no negociable antes de empezar.

---

## 1. Landing

| Producto | 1er año | Desde el 2º año | Vigente desde |
|---|---|---|---|
| Landing 2D | USD 375, todo incluido | USD 375/año | 2026-09-19 |
| Landing 2D autogestionable (panel de promos) | USD 500, todo incluido | USD 375/año | 2026-10-02 (renovación 375 desde 2026-10-15; MACERATA conserva 300) |
| Landing 2D autogestionable pasada a 3D | +USD 500 → USD 1.000 | +USD 100 → USD 475/año | 2026-10-15 |
| Landing 3D | USD 1.000, todo incluido | USD 400/año | 2026-10-15 |

Incluye dominio, hosting, SSL, soporte y mantenimiento. Respaldos: `docs/referencia/precios-landing-2d-autogestionable-2026-10.md`, `docs/referencia/precios-landing-3d-2026-10.md`.

## 2. Build (sistema de gestión a medida)

- **Desarrollo:** piso USD 800, rango típico USD 1.200–2.500 (desde 2026-09-19). Pago 50% anticipo / 50% entrega.
- **Plan anual de mantenimiento** (desde 2026-09-19; no retroactivo a clientes ya firmados):

| Plan | Tablas | USD/año | Usuarios |
|---|---|---|---|
| STARTER | 1–5 | 360 | 1 |
| PRO | 6–15 | 480 | hasta 2 |
| PREMIUM | 16–30 | 600 | hasta 3 (el más vendido) |
| SCALE | 31+ | 1.000 | ilimitados |

Incluye PWA móvil, hosting + SSL + dominio, actualizaciones de seguridad, performance y ronda de ajuste. Sin permanencia. **No publicar estos precios en el sitio** (decisión 2026-09-19). Cargado también en `27-presupuesto-parametros.instructions.md`.

- **Upsells** (ronda cada 6 meses a toda la base): módulo nuevo desde USD 250 (ampliación sobre sistemas entregados, confirmado 2026-10-15) · UI personalizada USD 100 · backup mensual USD 80/año.
- **Usuario adicional:** sin cargo fijo, no es upsell. Los usuarios nunca modifican el precio del plan; más de 10 se acuerda puntualmente.

## 3. AI Agents / Second Brain corporativo (portal Agentes Multi-rubro)

Modelo aprobado 2026-10-13, montos fijados 2026-10-15 (`docs/referencia/research-precios-ai-agents-second-brain-2026-10.md`). **Promo de entrada hasta 2026-12-31.**

**Setup — tres ejes, nunca por cantidad de agentes:**

| Concepto | Setup |
|---|---|
| Licencia de rubro + organización (alta, roles, cartera, piloto) | USD 1.500 (50/50) |
| Conector nuevo, por sistema externo distinto | Simple USD 500 · Media USD 900 · Compleja/sin API USD 1.500 |
| Agente 100% personalizado (no derivable del núcleo) | Básico USD 500 · Intermedio USD 1.000 · Avanzado USD 2.000 |
| Agente derivado por instructivo (self-service) | USD 0, ilimitados |
| Relevamiento externo (Bernarda), si hay ≥1 agente personalizado Intermedio/Avanzado | +USD 700 por cliente |

**Mensual:**

| Concepto | USD/mes | Crédito de IA incluido | Tope de corte |
|---|---|---|---|
| Organización S | 90 | 20 | 100 |
| Organización M | 150 | 50 | 250 |
| Organización L | 250 | 100 | 500 |
| Por conector activo | +25 | — | — |
| Por agente personalizado Básico / Intermedio / Avanzado | +40 / +80 / +150 | +5 / +10 / +20 | +20 / +40 / +80 |

- El tier de organización se asigna por **volumen de uso medido**, no por cantidad de agentes.
- **Excedente:** agotado el crédito del mes, el costo real se factura × 3 en el ciclo siguiente.
- **Núcleo vs. personalizado:** si la regla la fija el organismo o el sistema externo (ARCA, ARBA, Bejerman), va al núcleo, dentro de la licencia; si la fija la organización, es personalizado y se cobra.
- **Varios agentes personalizados para un mismo cliente:** 10% de descuento en cada agente nuevo (desde el segundo), sobre setup y recurrente. El primero va a lista.
- **Integraciones:** cada sistema externo distinto cuenta como una (2 cuentas del mismo banco = 1; banco + Mercado Pago = 2).
- **Cambio de tier de un agente:** paga la diferencia de setup y, desde la renovación siguiente, el mensual del tier nuevo.
- **Entrega de código (excepción comercial):** USD 6.000 por rubro, pago único, licencia de uso interno sin reventa + soporte opcional USD 1.200/año. Contrato revisado por abogado.

## 4. Chatbots (ventas y consultas automáticas)

Corregido 2026-09-17, tier Grandes empresas 2026-09-19. **Promo de entrada hasta 2026-12-31.**

| Tier | Setup | USD/año |
|---|---|---|
| Starter (hasta 200 conv/mes) | 700–900 | 480 |
| Pro (hasta 600 conv/mes) | 900–1.200 | 700 |
| Scale (alto volumen) | 1.200–1.800 | 1.100 |
| Grandes empresas | 2.500–4.000 | 3.000 |

- **Piso duro:** no vender un Starter por debajo de USD 480/año.
- **Conversación** = una ventana de 24 h de Meta con ese contacto. Si el cliente supera el tope de su tier **2 meses seguidos**, pasa al siguiente desde la renovación (paga la diferencia de setup). (2026-10-15)
- **Tech Provider:** el cliente paga la mensajería de Meta directo y trae su propia key de Claude. Decirlo siempre en la propuesta.
- El recurrente cubre infra, kill switch de gasto, monitoreo, 1 ronda de ajuste de prompt por mes y el crédito de IA a costo real.

## 5. Reglas transversales

- **Combo Landing 3D + AI Agents + Chatbots:** suma de las listas de los tres frentes con **10% de descuento sobre el setup**; el recurrente va a lista (2026-10-15).
- **Pilotos (hasta 2027):** 30% de descuento sobre el setup, recurrente a lista, **máximo 3 por frente**, a cambio de caso + logo + testimonio (2026-10-15).
- **Lista 2027** (cierres desde 2027-01-01, AI Agents y Chatbots): **promo × 1,20** (decisión 2026-09-19). Aplicado a la lista vigente:
  - AI Agents: licencia USD 1.800 · conectores 600/1.080/1.800 + 30/mes · agentes personalizados 600/1.200/2.400 + 48/96/180/mes · Organización S/M/L 108/180/300/mes.
  - Chatbots: setup 840–1.080 / 1.080–1.440 / 1.440–2.160 / 3.000–4.800 · 576 / 840 / 1.320 / 3.600 por año.
- **Renovación de la promo:** el cliente que cierra antes del 2026-12-31 mantiene el precio promo en las renovaciones mientras siga activo (recomendación de `olvidata-ceo`, mismo criterio que la suba de planes de 2026-07-24).
- **Cómo se comunica un precio** (una sola vez, como dato con fecha, sin presión): ver `docs/olvidata-soft/comunicacion.md`.

---

## Historial (superado — no cotizar con esto)

Cada entrada dice qué la reemplazó. Se conserva para entender propuestas viejas.

- **Landing 3D USD 600/año sin setup** (2026-09-14) → setup 2.000–3.000 + 600–900/año propuesto 2026-09-19, nunca vigente → **USD 1.000 + 400/año** (2026-10-15).
- **Landing 2D autogestionable: upgrade a 3D +USD 100** → precio del deal MACERATA, no de lista (2026-10-02); lista +500/+100 desde 2026-10-15.
- **Planes Build 300/400/500/850** (2026-07-24) → 360/480/600/1.000 (2026-09-19), no retroactivo.
- **Build desarrollo USD 400–1.000** → piso 800, típico 1.200–2.500 (2026-09-19).
- **AI Agents por tier** (2026-09-19): Básico setup 1.500–2.500 + 2.400/año · Intermedio 3.000–5.000 + 4.800/año · Avanzado 6.000–9.000 + 8.400/año (antes, 2026-09-14: 300–400/600–800/1.200–1.500 + 400/650/1.000) → plan base Rubro estándar USD 1.500 + 90/mes + agentes a medida 500/1.000/2.000 + 40/80/150/mes (2026-09-21) → rediseño por tres ejes (2026-10-13, fijado 2026-10-15). La tabla "Lista 2027" de AI Agents por tier (1.800–3.000 + 2.880, etc.) quedó superada con su base.
- **Lista post-promo recomendada por `olvidata-ceo`** (suba 25–30%) → superada por la decisión ×1,20 (2026-09-19).
- **Chatbots** (2026-09-14): setup 400–700 igual para los tres tiers + 350/550/900 por año, debajo del piso de rentabilidad → tabla actual (2026-09-17).
- **Upsells:** módulo nuevo USD 200 → 250; usuario adicional USD 125/año → sin cargo; performance y ronda de ajuste dejaron de ser upsells (2026-09-14).
- **Propuesta BMA USD 11.000 + 13.200/año** (2026-09-21) → recalculada sobre los 4 ejes reales: setup USD 4.000 (+700 Bernarda si aplica) + USD 290/mes; la brecha con lo pactado informalmente (2.500 / 170) queda como descuento piloto (2026-10-13). Detalle en `docs/contadores-bma-agentes-ia/trazabilidad.md`.
