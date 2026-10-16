<!-- Archivado de docs/crm-olvidata/trazabilidad.md el 2026-10-15 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-09 (1 bloques archivados)

- 2026-09-14 (10) — presupuestador: estimacion interna de "4 frentes — combo con gancho" (pendiente de aprobacion)

---

## 2026-09-14 (10) — presupuestador: estimacion interna de "4 frentes — combo con gancho" (pendiente de aprobacion)

- **Agente/etapa:** `agentes-ia-presupuestador`, modo Ask. Proyecto interno: estimacion de esfuerzo y costo equivalente, sin precio al cliente, sin Tokens IA/descuentos/mantenimiento. Detalle en `definiciones/4-presupuestador.md`.
- **Anclaje:** cierre real propio del sprint 2026-08-27 (22 h M → 2.5-3 h reales). Iteracion evolutiva sobre el mismo repo con rondas previas → pisos de "modificacion sobre modulo existente".
- **Numeros:** 7 etapas, **21.0 h M base / 22.0 h PERT / 25.62 h con contingencia variable** (E5 envio facturable al 25%, E1 y E7 al 8%, resto 15%) / 10.08 h facturables / ≈ USD 353 de costo interno equivalente (M × 16,80) + ≈ USD 46 de IA sombra (overhead Ask-mode subido a 6 h por las 2 rondas de rediseño). Sanity check total contra el sprint 08/27: 0.95. Real esperado 3-3.5 h, techo 4.5-5 h por la verificacion contra produccion de E2/E5.
- **Etapas de entrega:** Etapa 1 = E1+E2 (3.5 h, desplegable ya, mejora el inbound, sin migracion); Etapa 2 = E3+E4+E5+E7 (14 h, reactiva el outbound con el combo; para enviar requiere textos de marketing + aprobacion de Meta); Etapa 2b = E6 modulos por frente (3.5 h, diferible sin bloquear el outbound).
- **Gate:** Implementacion bloqueada hasta que Joaquin apruebe y elija alcance de arranque (Etapa 1 sola / Etapa 1+2 / con o sin E6).
- **PRESUPUESTO APROBADO (mismo dia):** Joaquin eligio alcance completo E1-E7 (incluye E6 modulos por frente, una sola migracion). Implementacion habilitada y lanzada con `agentes-ia-implementador` — migracion solo en `olvidatacrm_dev`, sin deploy a produccion, sin commits, sin tocar Meta ni reactivar outbound hasta QA + confirmacion del owner.
