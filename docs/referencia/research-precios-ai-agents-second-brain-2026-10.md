# Research de precios — AI Agents / "second brain" corporativo

Fecha: 2026-10-15. Pedido por Joaquín para cerrar el punto pendiente del rediseño de pricing AI Agents multirubro (2026-10-13, montos "bajo revisión": *"me parece caro"*). **Propuesta, no vigente hasta que Joaquín la confirme.** Complementa `docs/olvidata-agentes-multirubro/research-precios-ai-agents-2026-09.md` y el research del 2026-10-13 resumido en `olvidata-ceo`.

[P] = precio de lista del proveedor · [R] = rango reportado en blog/agregador (casi todos venden lo mismo: sesgo al alza).

## 1. SaaS por usuario (lo que el cliente compara primero)

| Producto | USD/usuario/mes | Nota | Fuente |
|---|---|---|---|
| Notion AI (plan Business) | 15–20 [R] | IA incluida en el plan desde 2025 | eesel.ai, dupple.com |
| ChatGPT Business | 20–25 [R] | 2 a 200 usuarios | costbench.com |
| Claude Team (Standard) | 25 [R] | Premium 125 | costbench.com |
| Microsoft 365 Copilot Business | 21 (promo 18 hasta 31/12/2026) [R] | add-on, + licencia M365 aparte | eesel.ai/blog/copilot-pricing |
| Guru | 15–25 [R] | mínimo 10 usuarios | eesel.ai, dupple.com |
| Glean | 40–50 [R] | mínimo ~100 usuarios, piso ~USD 60.000/año; mediana Vendr ~97.500/año | coworker.ai |

Para una pyme de 15 usuarios: **USD 300–450/mes** en un asistente genérico, sin setup, que **no** conoce la operatoria ni las reglas del rubro y no ejecuta tareas sobre sus datos.

## 2. Implementadores de agentes IA (Argentina)

| Alcance | Setup | Mensual | Fuente |
|---|---|---|---|
| Agente básico / chatbot simple | USD 500–1.500 [R] | API 20–100 + hosting ~20 | freelancer.ar, diegoceredi.com |
| Agente personalizado | USD 1.500–7.000+ [R] | — | freelancer.ar |
| Pyme mediana (habitual) | USD 3.500–5.000 [R] | — | cosys.com.ar |
| Agente integrado (CRM/ERP/API) | USD 5.000–15.000+ [R] | cientos a 1.500+ | cosys.com.ar (2026-09-18) |

## 3. Base de conocimiento con RAG a medida (global)

| Alcance | Setup | Mensual | Fuente |
|---|---|---|---|
| Agente RAG productivo, pyme | USD 15.000–75.000 [R] | 200–500 (un flujo) | cleveroad.com, ayautomate.com |
| RAG estándar | USD 20.000–60.000 [R] | — | salttechno.ai |
| Enterprise | USD 70.000–300.000 [R] | 500–20.000+ | tekrevol.com, softteco.com |

Plazos de referencia de un producto "Second Brain" comercial (Brasil): piloto ~2 semanas, despliegue completo 6–12 semanas (2ndbrain.com.br, sin precio público).

## 4. Olvidata contra el mercado

Vigente bajo revisión (rediseño 2026-10-13): licencia de rubro USD 1.500 · conectores 500/900/1.500 + 25/mes · agente personalizado +500/1.000/2.000 + 40/80/150/mes · agente derivado por instructivo USD 0 · mensual Org S/M/L 90/150/250 (propuesto, no fijado).

| Caso | Olvidata | Mercado |
|---|---|---|
| Pyme 15 usuarios, solo núcleo del rubro | 1.500 + 90–150/mes (USD 6–10/usuario) | SaaS genérico 300–450/mes sin setup · implementador AR 1.500–5.000 |
| Tipo BMA (4 ejes, sin conector) | 4.000–4.700 + 290/mes | implementador AR 5.000–15.000 · RAG a medida 15.000+ |

**Lectura:** el precio **no es caro** contra ninguno de los tres comparables. El mensual por organización queda **por debajo del precio por usuario de un ChatGPT/Claude/Copilot genérico** para cualquier equipo de más de 5–6 personas, y el setup en la franja baja de los implementadores argentinos.

## Salvedades

1. Casi todas las cifras salen de blogs de vendedores o agregadores; Glean no publica precios.
2. Los SaaS por usuario son el ancla que el cliente tiene en la cabeza: conviene que la propuesta los nombre como comparación (más barato por persona y además conoce el rubro).
3. Precios en USD sin impuestos.
