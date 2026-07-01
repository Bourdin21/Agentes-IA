---
name: agentes-ia-orquestador
description: Orquestador del flujo completo del estudio — Discovery hasta cierre de calibración con gates entre etapas y trazabilidad documental. Usar para features nuevas end-to-end.
disable-model-invocation: true
---

# Orquestador — flujo completo

Modo Cursor: alternar **Ask** (etapas 1–4, 7–8) y **Agent** (5–6).

## Arranque

1. Confirmar proyecto (crear desde `docs/templates/proyecto/` si no existe).
2. Leer `C:/Sistemas/Agentes-IA/.github/prompts/09-orquestador-flujo-completo.prompt.md`.
3. Leer `docs/indice.md` y `docs/<proyecto>/trazabilidad.md`.
4. Cargar instrucciones: `00`, `01`, `10`, `26`, `27`, `28`, `29`.

## Secuencia (no saltar etapas)

| # | Prompt | Skill sugerido |
|---|---|---|
| 0 | `00-discovery.prompt.md` | analista-funcional |
| 1 | `01-analisis.prompt.md` | analista-funcional |
| 2 | `02-diseno.prompt.md` | disenador-funcional |
| 3 | `03-arquitectura.prompt.md` | arquitecto-mvc |
| 4 | `04-presupuesto.prompt.md` | presupuestador |
| 5 | `05-implementacion.prompt.md` | implementador |
| 6 | `06-pruebas.prompt.md` | qa |
| 7 | `07-documentacion.prompt.md` | documentador |
| 8 | `08-cierre-calibracion.prompt.md` | presupuestador |

Ruta prompts: `C:/Sistemas/Agentes-IA/.github/prompts/`

## Reglas

- Antes de cada etapa: leer definición vigente del agente en `docs/<proyecto>/definiciones/`.
- Al cerrar: editar el archivo existente (no crear duplicados) y registrar en `trazabilidad.md`.
- Si faltan datos críticos: marcar bloqueo y pedir información puntual.
