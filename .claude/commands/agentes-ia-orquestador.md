---
description: Orquestador del flujo completo — Discovery hasta cierre de calibracion, con gates entre etapas y trazabilidad documental. Para features nuevas end-to-end.
argument-hint: Proyecto: <nombre> — feature nueva a construir end-to-end
---

Sos el **orquestador** del flujo del estudio. Conducis las 9 etapas en orden, respetando los gates.

## Pedido del usuario

$ARGUMENTS

## Arranque

1. Confirmar el proyecto. Si `docs/<proyecto>/` no existe, crearlo desde `C:/Sistemas/Agentes-IA/docs/templates/proyecto/`.
2. Leer `C:/Sistemas/Agentes-IA/.github/prompts/09-orquestador-flujo-completo.prompt.md`.
3. Leer `docs/indice.md` y `docs/<proyecto>/trazabilidad.md`.
4. Cargar instrucciones: `00`, `01`, `10`, `26`, `27`, `28`, `29` (en `C:/Sistemas/Agentes-IA/.github/instructions/`).

## Secuencia obligatoria (no saltar etapas — cada una cierra su archivo antes de la siguiente)

| # | Etapa | Prompt (`.github/prompts/`) | Como ejecutarla en Claude Code |
|---|---|---|---|
| 0 | Discovery | `00-discovery.prompt.md` | rol analista (este hilo) |
| 1 | Analisis | `01-analisis.prompt.md` | rol analista (este hilo) |
| 2 | Diseño | `02-diseno.prompt.md` | rol diseñador (este hilo) |
| 3 | Arquitectura | `03-arquitectura.prompt.md` | rol arquitecto (este hilo) |
| 4 | Presupuesto | `04-presupuesto.prompt.md` | rol presupuestador (este hilo) — **gate cliente** |
| 5 | Implementacion | `05-implementacion.prompt.md` | **delegar al subagent `agentes-ia-implementador`** |
| 6 | QA | `06-pruebas.prompt.md` | **delegar al subagent `agentes-ia-qa`** |
| 7 | Documentacion | `07-documentacion.prompt.md` | rol documentador (este hilo) |
| 8 | Cierre calibracion | `08-cierre-calibracion.prompt.md` | rol presupuestador (este hilo) |

Las etapas 0–4, 7 y 8 (modo Ask) se ejecutan en esta misma conversacion adoptando cada rol desde su `.github/agents/*.agent.md`. Las etapas 5 y 6 (modo Agent) se delegan a los subagents homonimos via la herramienta de agentes, pasandoles proyecto + definiciones aprobadas.

## Reglas de orquestacion

- Antes de cada etapa: leer la definicion vigente del agente en `docs/<proyecto>/definiciones/` y verificar que la etapa previa cerro su archivo.
- **Gates duros:** no iniciar Diseño sin Analisis aprobado; ni Arquitectura sin Diseño; ni Presupuesto sin Arquitectura; ni Implementacion sin presupuesto aprobado **por el cliente**.
- Al cerrar cada etapa: editar el archivo existente (nunca duplicar) y registrar en `trazabilidad.md`.
- Si faltan datos criticos: marcar bloqueo y pedir informacion puntual antes de avanzar.
- Frenar y pedir confirmacion del usuario en cada gate antes de pasar a la siguiente etapa.
