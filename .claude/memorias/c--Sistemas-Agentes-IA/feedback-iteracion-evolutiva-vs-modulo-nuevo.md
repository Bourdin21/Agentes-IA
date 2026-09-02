---
name: feedback-iteracion-evolutiva-vs-modulo-nuevo
description: "When estimating work on an already-delivered system that reuses an existing pattern, anchor on 'Modificacion sobre modulo existente' ranges, not 'modulo nuevo' ranges — confirmed by a 7.07x overestimate otherwise"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
---

Before classifying a presupuesto item as a "modulo nuevo" (ABM complejo, Modulo financiero, workflow con estados — the higher-hour ranges in `27-presupuesto-parametros.instructions.md`), check whether it's actually an **iteracion evolutiva sobre un sistema ya entregado que reutiliza un patron ya resuelto en el mismo repo** (same kind of entity/service/flow already implemented elsewhere in that codebase — e.g. a ledger pattern like `CuentaCorriente`/`MovimientoCC` already exists for one entity and gets replicated for another). If it does, anchor in the **"Modificacion sobre modulo existente"** section instead — it has much lower ranges (0.5-2h) than the "modulo nuevo" tables (4-11.5h).

**Why:** vinosefue sprint "Compras al proveedor: armado manual y cuenta corriente" (2026-07-03) closed at 4 real hours for 8 items that included a new provider ledger and a full FK-relationship refactor. Reconstructing the PERT retroactively using the standard "modulo nuevo" ranges (ABM complejo, Modulo financiero) produced 28.27h — a **7.07x overestimate, the new record in the studio's dataset** (surpassing Ganaderia's 5.05x and ShowroomGriffin's 4.0x). The root cause: the ledger reused the exact pattern already built for the Cliente's `CuentaCorriente`, and the payment/credit-note CRUD reused `AdjuntoService`/`MetodoPago` already built for another flow — none of that infrastructure had to be invented, which the "modulo nuevo" ranges don't account for.

**How to apply:** `27-presupuesto-parametros.instructions.md` now has 3 new granular ranges under "Modificacion sobre modulo existente" derived from this closure (refactor de vinculo/FK + migracion: ~1.5-2h; ledger reutilizando patron existente: ~1-1.5h; ABM manual reutilizando servicios existentes: ~0.5-1h), plus an explicit rule to check for pattern-reuse before reaching for the bigger "modulo nuevo" tables. When a client (or the studio itself) reports real hours only as a lump-sum total for a batch of items (no per-item breakdown), treat the per-item split as an unconfirmed proportional hypothesis — the total ratio is the solid data point, not the per-item numbers. Related: [[project-ganaderia-referencia-presupuesto]], [[project-agentes-ia]].
