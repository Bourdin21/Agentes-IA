---
name: feedback-tokens-ia-10-porciento
description: "Tokens IA charge is 25% of subtotal (unchanged), but since 2026-08-20 it's distributed INTO each module's price, never shown as its own client-facing line"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-20T17:29:29.607Z
---

**Superseded 2026-08-20 (exposure only, not the rate).** The Tokens IA *rate* is still 25% of Subtotal Etapa 1 + Subtotal Etapa 2 (unchanged since 2026-07-24). What changed is how it's *shown*: it no longer appears as its own "Tokens IA" line in the client document — it's now **distributed into every module's displayed price**, via a constant `x1.25` factor applied to each item/area's list price (constant because the charge is always exactly 25% of the list subtotal, so `Σ(item_lista × 1.25) = Subtotal_lista + Tokens_IA` — the total is unchanged, only the per-module breakdown absorbs it). History: fixed USD 100 (until 2026-06) → 10% (2026-07-03–07-24) → 25% visible line (2026-07-24–08-20) → **25% distributed into modules, invisible as a line item (current, since 2026-08-20)**.

**Why:** User (2026-08-20) asked explicitly to fold the charge into module prices ("tiene que estar impuesta ya en el precio del modulo") — reverses the *opposite* explicit instruction from 2026-07-03 (this same memory used to say "never prorated"). Rationale wasn't stated beyond the direct instruction — likely a presentation preference (client sees one clean number per module, not a visible AI-tax line). This is the second full reversal of this specific display rule; if it flips again, check with the user before assuming which direction is current.

**Interaction with the reuse/volume discount:** the discount (`27-presupuesto-parametros.instructions.md` § "Descuento de expansion agresiva") still shows as its own separate line ("Descuento por eficiencia de desarrollo") when it applies — only Tokens IA got folded in, not the discount. Order: compute module list prices → multiply each by 1.25 for the client-facing number → subtract the discount (if any) as its own line at the total level, same mechanism as before.

**Distinct from the internal-only "Costo interno de IA" concept** (see [[feedback-costo-ia-interno-presupuesto]]): this 25% is a client-facing pricing/margin charge, calculated on the module subtotal regardless of actual AI token consumption. The other memory is a *real* projected cost estimate (shadow-priced at API list rates) used internally to check whether this 25% margin covers actual AI cost.

**How to apply:** `.github/instructions/27-presupuesto-parametros.instructions.md` ("Cargo por uso de tokens IA" section) and `.github/agents/presupuesto-mvc.agent.md` (salida minima item 12) both updated. The internal `4-presupuestador.md` per project still shows the full breakdown (list price, Tokens IA amount, x1.25 distributed price) for the studio's own trazabilidad — only the client-facing `presupuesto-cliente.md` hides the Tokens IA concept entirely. Existing closed projects' documents were NOT retroactively updated — only applies going forward. Related: [[project-agentes-ia]], [[feedback-costo-ia-interno-presupuesto]].
