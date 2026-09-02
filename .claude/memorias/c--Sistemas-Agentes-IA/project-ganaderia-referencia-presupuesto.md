---
name: project-ganaderia-referencia-presupuesto
description: "Ganaderia is the fixed commercial reference project for future budget calibration — real hours, real price, and the maintenance/discount breakdown"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
---

The `ganaderia` project (repo `ganaderia - emo`) is explicitly designated as a **reference project for future budgets** in `.github/instructions/27-presupuesto-parametros.instructions.md` and `docs/ganaderia/definiciones/4-presupuestador.md`.

Closed numbers (2026-07-03):
- Scope: 8 functional modules (catalogos, usuarios, stock, ingresos con facturacion/cuotas, rechazos/regularizacion/job diario, egresos, caja, dashboard), 2 EF migrations, ABM+workflow+financial-logic mix.
- Real dev effort: **20 hours** (vs. 101.0h PERT-with-contingency estimated — 5.05x overestimate, the highest ratio in the studio's dataset).
- Real commercial price: **USD 950 total**, not the USD 1,212 figure recorded earlier that session (that was only the internal PERT×$12/h estimate, never actually billed). The USD 950 includes a 15% referral discount (same discount type used on contadores-bma-conversor) and bundles the first year of the annual maintenance plan (USD 300) into that price. Backing out maintenance: development-only ≈ USD 650 ≈ **USD 32.5/h effective** — close to the studio's USD 35/h target rate. Ongoing annual plan from year 2: USD 300/year.

**Why:** User corrected the real-hours figure twice in the same session (first 18h, then 20h) and then supplied the actual commercial closing terms, explicitly asking to lock ganaderia in as the reference for estimating future projects of similar scope by functionality-delivered-vs-actual-cost, not by the original PERT estimate.

**How to apply:** When the presupuestador agent estimates a new project with a comparable scope (8-11 modules, ABM+workflow+financial mix), anchor M using this project's **20 real hours / USD 650 dev cost** relationship instead of its 101.0h PERT figure. When quoting a discounted/referral deal, this project confirms the pattern of bundling first-year maintenance into the initial price is workable and has precedent (contadores-bma-conversor also used the 15% referral discount). Related: [[project-agentes-ia]].
