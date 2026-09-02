---
name: feedback-descuento-volumen-presupuesto
description: Segundo eje de descuento de expansion agresiva - por volumen del proyecto (tiers V0-V3), combina con el de reutilizacion via MAX no suma. Vigente desde 2026-08-19.
metadata:
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-20T15:24:54.839Z
---

Joaquin pidio (2026-08-19) agregar una regla de "a mayor volumen, menor costo total" al presupuesto. Se delego el research a `olvidata-ceo` antes de implementar (pedido explicito del usuario: "hacer un research de como aplicar esta regla").

**Regla implementada:** segundo eje de descuento sobre `Subtotal_lista`, independiente del ratio de reutilizacion R ya existente (`27-presupuesto-parametros.instructions.md`, seccion "Descuento de expansion agresiva"):

| Tier | Subtotal_lista | Descuento |
|---|---|---:|
| V0 | < USD 600 | 0% |
| V1 | USD 600-1200 | 5% |
| V2 | USD 1200-2000 | 10% |
| V3 | USD 2000+ | 15% |

**Combina via MAX, no suma:** `factor_tier = MAX(factor_tier_reutilizacion, factor_tier_volumen)`. Verificado contra el dataset real (vinosefue, Ganaderia, La Platense) que sumar solo aportaba +5 puntos marginales sobre proyectos ya en Tier 1 de reutilizacion (30%) — insuficiente para justificar la complejidad de explicar dos descuentos + un tope global. MAX cubre el hueco real: proyectos grandes con reuso BAJO (rubro nuevo, sin patron previo), que hoy cotizaban a precio de lista completo pese a ser el ticket mas valioso.

**Research de mercado (via olvidata-ceo):** estudios/consultoras chicas usan 10-15% de descuento por volumen (bloques de horas/retainers); 20-40% es escala enterprise (contratos USD 15K-100K+/mes), no aplica al perfil de Olvidata (proyectos USD 280-2.250).

**Mismo alcance y gatillo que el descuento por reutilizacion:** solo Build inicial cliente nuevo/rewrite (no Mantenimiento/Extras/Merge), condicionado al mismo tablero de ciclos economicos (checkpoint octubre 2027) — se pausan juntos si pasa a rojo.

**Impacto en el dataset historico:** proyectos con reuso alto (caso tipico de Olvidata) no cambian de precio — ya estaban en el tope de 30%. Solo mueve el precio en proyectos grandes y genuinamente nuevos.

**Donde vive:** `27-presupuesto-parametros.instructions.md` (formula completa), `presupuesto-mvc.agent.md` (politica de facturacion actualizada a MAX de los dos tiers), `docs/calibracion/dataset.yml` (tablas estructuradas de ambos ejes de descuento).

**Como aplicar:** todo presupuesto de Build inicial nuevo debe calcular AMBOS tiers (R y volumen) y tomar el mayor, nunca sumarlos. Relacionado: [[project-agentes-ia-mejoras-2026-08-15]].
